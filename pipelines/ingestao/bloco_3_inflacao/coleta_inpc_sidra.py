"""Coleta bruta do INPC (Índice Nacional de Preços ao Consumidor) — índice geral,
com variação mensal, acumulada no ano, acumulada em 12 meses e peso mensal — via API
pública do SIDRA/IBGE.

Piloto técnico controlado — ver docs/08-decisoes-adr/0002-expansao-piloto-por-blocos.md
Fonte confirmada em: docs/04-fontes/ibge-sidra.md (Tabela SIDRA 7063) — Lote 06b.

===============================================================================
COMO FUNCIONA A API DO SIDRA (vale para todos os scripts "..._sidra.py")
===============================================================================
O SIDRA é o sistema de tabelas do IBGE. Toda consulta pela API segue o mesmo
formato de URL, com "segmentos" separados por barra — cada um filtra uma
dimensão da tabela:

    https://apisidra.ibge.gov.br/values/t/{tabela}/n1/{territorio}/v/{variavel}/p/{periodo}/c315/{categoria}

  - `t/7063`      → número da tabela no SIDRA (cada tabela do IBGE tem um ID
                    fixo; 7063 é "INPC — Variação mensal, acumulada no ano,
                    acumulada em 12 meses e peso mensal", vigente a partir de
                    jan/2020, mesmo padrão de reestruturação já visto na
                    tabela do IPCA). Para achar o número de outra tabela,
                    procure no site sidra.ibge.gov.br e copie da URL da tabela.
  - `n1/all`      → nível territorial (n1 = Brasil) e "all" = todos os
                    territórios desse nível.
  - `v/all`       → quais variáveis da tabela trazer ("all" = todas: variação
                    mensal, acumulada no ano, acumulada em 12 meses e peso).
  - `p/all`       → quais períodos trazer ("all" = a série completa).
  - `c315/7169`   → classificação "Geral, grupo, subgrupo, item e subitem" da
                    tabela do INPC; a categoria `7169` é o código do ÍNDICE
                    GERAL (o número do país como um todo, sem abrir por grupo
                    de despesa) — mesmo padrão de código de categoria usado
                    na tabela irmã do IPCA (7060), mas cada tabela do SIDRA
                    tem suas próprias classificações.

A resposta é sempre uma lista de objetos JSON, onde o PRIMEIRO item é o
cabeçalho (nomes das colunas) e os demais são os valores — por isso este
script não faz nenhuma limpeza: grava a lista inteira exatamente como veio.

===============================================================================
POR QUE UM SCRIPT SEPARADO DO IPCA — INPC não é "o mesmo índice com outro nome"
===============================================================================
IPCA e INPC são dois índices de preços distintos, calculados pelo mesmo
sistema do IBGE (SNIPC) a partir da mesma coleta de preços, mas com
PÚBLICOS-ALVO diferentes: o IPCA cobre famílias com renda de 1 a 40 salários
mínimos, e o INPC cobre famílias de renda mais baixa (1 a 5 salários mínimos,
assalariadas). Como a composição de gastos muda com a renda, as cestas de
ponderação — e portanto os números resultantes — também são diferentes. Por
isso o INPC tem sua própria tabela no SIDRA (7063) e seu próprio script aqui,
em vez de ser tratado como um subproduto do script do IPCA.

Este script é parte da síntese "INPC, ICV e outros indicadores de inflação"
do material do DIEESE — cobre apenas a sub-fonte INPC/IBGE. As demais
sub-fontes citadas (Portal FGV, INDATEND) são tratadas separadamente: o
IGP-M/FGV está em `coleta_igpm_bcb.py` (via rota alternativa do BCB); o
INDATEND não tem coleta automatizável (fonte estritamente manual).

===============================================================================
O QUE ESTE SCRIPT FAZ, PASSO A PASSO
===============================================================================
1. Monta a URL da consulta (constante `URL`, ver acima).
2. Busca os dados na API (`_buscar_dados`).
3. Salva a resposta, sem alterar nada, em `data/raw/ibge_sidra/` com um nome
   de arquivo que inclui a tabela e o instante da coleta (`_salvar_raw`).
4. Registra a coleta no Supabase — arquivo no Storage + linha em
   `raw_ingestoes` (`registrar_coleta`, importado de `pipelines/supabase_raw.py`).

Este script NÃO transforma o dado — grava a resposta bruta da API exatamente
como recebida, respeitando o princípio de que a camada RAW nunca deve ser
editada manualmente ou pré-processada (ver CLAUDE.md, seção DADOS). Comparar
IPCA com INPC, calcular diferenças ou qualquer outra conta é trabalho da
camada STAGING, feito depois — nunca aqui.
"""

import json
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from supabase_raw import registrar_coleta

# Tabela 7063 do SIDRA: "INPC — variação mensal, acumulada no ano, acumulada em 12
# meses e peso mensal". Classificação c315/7169 = índice geral (sem abrir por grupo).
URL = "https://apisidra.ibge.gov.br/values/t/7063/n1/all/v/all/p/all/c315/7169"

DESTINO = Path(__file__).resolve().parents[3] / "data" / "raw" / "ibge_sidra"


# ------------------------------------------------------------------------
# PASSO 1 — buscar os dados na API
# ------------------------------------------------------------------------
def _buscar_dados() -> list:
    """Faz a requisição HTTP e devolve o JSON já decodificado (uma lista de
    dicionários — o primeiro é o cabeçalho, os demais são os valores).

    `timeout=60` existe porque a API do SIDRA pode demorar alguns segundos
    quando a tabela pedida tem muitos dados ("v/all p/all" traz a série
    inteira) — sem timeout, um problema de rede deixaria o script parado
    indefinidamente em vez de falhar de forma visível.
    """
    with urllib.request.urlopen(URL, timeout=60) as resposta:
        return json.loads(resposta.read().decode("utf-8"))


# ------------------------------------------------------------------------
# PASSO 2 — salvar a resposta bruta em disco
# ------------------------------------------------------------------------
def _salvar_raw(dados: list) -> Path:
    """Grava `dados` como JSON, formatado (indent=2) só para ficar legível
    para humanos que forem inspecionar o arquivo — isso não é uma
    transformação do dado, é só formatação de texto.

    O nome do arquivo leva um timestamp UTC (`_%Y%m%dT%H%M%SZ`) porque cada
    execução deste script é uma nova "fotografia" da série: o IBGE revisa
    dados publicados, e queremos poder comparar o que a API respondia em
    momentos diferentes — por isso nunca sobrescrevemos a coleta anterior.
    """
    DESTINO.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    arquivo = DESTINO / f"inpc_sidra_7063_{timestamp}.json"
    arquivo.write_text(json.dumps(dados, ensure_ascii=False, indent=2), encoding="utf-8")
    return arquivo


# ------------------------------------------------------------------------
# Orquestração: chama os passos acima, nesta ordem
# ------------------------------------------------------------------------
def coletar() -> Path:
    dados = _buscar_dados()
    return _salvar_raw(dados)


if __name__ == "__main__":
    caminho = coletar()
    print(f"Coleta concluída: {caminho}")
    registrar_coleta(fonte=DESTINO.name, arquivo=caminho, script=__file__)
