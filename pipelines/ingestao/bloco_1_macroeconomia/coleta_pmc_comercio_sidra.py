"""Coleta bruta do índice/variação da receita nominal e do volume de vendas no comércio
varejista ampliado (PMC — Pesquisa Mensal de Comércio) via API pública do SIDRA/IBGE.

Piloto técnico controlado — ver docs/08-decisoes-adr/0002-expansao-piloto-por-blocos.md
Fonte confirmada em: docs/04-fontes/ibge-sidra.md (Tabela SIDRA 8881)

===============================================================================
COMO FUNCIONA A API DO SIDRA (vale para todos os scripts "..._sidra.py")
===============================================================================
O SIDRA é o sistema de tabelas do IBGE. Toda consulta pela API segue o mesmo
formato de URL, com "segmentos" separados por barra — cada um filtra uma
dimensão da tabela:

    https://apisidra.ibge.gov.br/values/t/{tabela}/n1/{territorio}/v/{variavel}/p/{periodo}/c11046/{classificacao}

  - `t/8881`      → número da tabela no SIDRA (8881 é "Índice de volume de
                    vendas e receita nominal de vendas no comércio varejista
                    ampliado", Pesquisa Mensal de Comércio). Para achar o
                    número de outra tabela, procure em sidra.ibge.gov.br e
                    copie da URL da tabela.
  - `n1/all`      → nível territorial (n1 = Brasil) e "all" = todos os
                    territórios desse nível (aqui só existe 1: o próprio
                    Brasil).
  - `v/all`       → quais variáveis da tabela trazer ("all" = todas).
  - `p/all`       → quais períodos trazer ("all" = a série completa).
  - `c11046/all`  → classificação "Tipos de índice", desta tabela (as duas
                    categorias existentes: receita nominal e volume de
                    vendas) — "all" traz as duas de uma vez. Cada tabela do
                    SIDRA tem suas próprias classificações; o número do
                    código (aqui 11046) muda de tabela para tabela.

A resposta é sempre uma lista de objetos JSON, onde o PRIMEIRO item é o
cabeçalho (nomes das colunas) e os demais são os valores — por isso este
script não faz nenhuma limpeza: grava a lista inteira exatamente como veio.

===============================================================================
ATENÇÃO — escopo real desta tabela
===============================================================================
O material do DIEESE descreve este indicador com o rótulo único
"comércio/serviços/indústria (PMC/PMS/PIM)", mas a Tabela 8881 cobre APENAS a
Pesquisa Mensal de Comércio (PMC). PMS (serviços) e PIM (indústria) são
pesquisas distintas do IBGE, cada uma com sua própria tabela no SIDRA — ver
`coleta_pms_servicos_sidra.py` (tabela 5906) e `coleta_pim_industria_sidra.py`
(tabela 8888). Este script coleta somente a parcela comércio.

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
editada manualmente ou pré-processada (ver CLAUDE.md, seção DADOS). Calcular
variações, comparar com PMS/PIM ou qualquer outra conta é trabalho da camada
STAGING, feito depois, a partir do arquivo que este script grava — nunca aqui.
"""

import json
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from supabase_raw import registrar_coleta

# Tabela 8881 do SIDRA: "Índice de volume de vendas e receita nominal de
# vendas no comércio varejista ampliado" — Pesquisa Mensal de Comércio (PMC).
URL = "https://apisidra.ibge.gov.br/values/t/8881/n1/all/v/all/p/all/c11046/all"

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
    arquivo = DESTINO / f"pmc_comercio_sidra_8881_{timestamp}.json"
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
