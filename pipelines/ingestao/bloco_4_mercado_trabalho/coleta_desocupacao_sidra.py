"""Coleta bruta da taxa de desocupação (PNAD Contínua trimestral) via API pública
do SIDRA/IBGE.

Piloto técnico controlado — ver docs/08-decisoes-adr/0002-expansao-piloto-por-blocos.md
Fonte confirmada em: docs/04-fontes/ibge-sidra.md (Tabela SIDRA 4093) — Discovery de
Fontes, Lote Piloto 01.

===============================================================================
COMO FUNCIONA A API DO SIDRA (vale para todos os scripts "..._sidra.py")
===============================================================================
O SIDRA é o sistema de tabelas do IBGE. Toda consulta pela API segue o mesmo
formato de URL, com "segmentos" separados por barra — cada um filtra uma
dimensão da tabela:

    https://apisidra.ibge.gov.br/values/t/{tabela}/n1/{territorio}/v/{variavel}/p/{periodo}/c2/{classificacao}

  - `t/4093`      → número da tabela no SIDRA (cada tabela do IBGE tem um ID
                    fixo; 4093 é "Taxa de desocupação", um dos resultados da
                    PNAD Contínua trimestral). Para achar o número de outra
                    tabela, procure no site sidra.ibge.gov.br e copie da URL
                    da tabela.
  - `n1/all`      → nível territorial (n1 = Brasil) e "all" = todos os
                    territórios desse nível (aqui só existe 1: o próprio
                    Brasil). Esta mesma tabela também está disponível por
                    Grande Região e UF, usando n2/n3 em vez de n1.
  - `v/all`       → quais variáveis da tabela trazer ("all" = todas).
  - `p/all`       → quais períodos trazer ("all" = a série completa).
  - `c2/all`      → um filtro de classificação específico desta tabela (aqui:
                    `c2` é a classificação "Sexo", com as categorias Total,
                    Homens e Mulheres — "all" traz as três). Cada tabela do
                    SIDRA tem suas próprias classificações — o número do
                    código muda de tabela para tabela.

A resposta é sempre uma lista de objetos JSON, onde o PRIMEIRO item é o
cabeçalho (nomes das colunas) e os demais são os valores — por isso este
script não faz nenhuma limpeza: grava a lista inteira exatamente como veio.

===============================================================================
O QUE ESTE SCRIPT FAZ, PASSO A PASSO
===============================================================================
1. Monta a URL da consulta (constante `URL`, ver acima).
2. Busca os dados na API (`_buscar_dados`).
3. Salva a resposta, sem alterar nada, em `data/raw/ibge_sidra/` com um nome
   de arquivo que inclui a tabela e o instante da coleta (`_salvar_raw`).
4. Registra a coleta no Supabase — arquivo no Storage + linha em
   `raw_ingestoes` (`registrar_coleta`, importado de `pipelines/supabase_raw.py`).

O QUE A TABELA 4093 MEDE: a proporção de pessoas de 14 anos ou mais que estão
desocupadas (procurando trabalho ativamente e disponíveis para começar a
trabalhar) em relação à força de trabalho total, na semana de referência da
pesquisa. É o indicador oficial de "taxa de desemprego" divulgado pelo IBGE a
cada trimestre, calculado a partir da PNAD Contínua (Pesquisa Nacional por
Amostra de Domicílios Contínua).

Este script NÃO transforma o dado — grava a resposta bruta da API exatamente
como recebida, respeitando o princípio de que a camada RAW nunca deve ser
editada manualmente ou pré-processada (ver CLAUDE.md, seção DADOS). Calcular
variações, comparar trimestres ou qualquer outra conta é trabalho da camada
STAGING, feito depois, a partir do arquivo que este script grava — nunca aqui.
"""

import json
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from supabase_raw import registrar_coleta

# Tabela 4093 do SIDRA: "Taxa de desocupação" — PNAD Contínua trimestral.
URL = "https://apisidra.ibge.gov.br/values/t/4093/n1/all/v/all/p/all/c2/all"

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
    dados publicados (ver nota sobre reponderação 2025 em
    docs/04-fontes/ibge-sidra.md), e queremos poder comparar o que a API
    respondia em momentos diferentes — por isso nunca sobrescrevemos a
    coleta anterior.
    """
    DESTINO.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    arquivo = DESTINO / f"desocupacao_sidra_4093_{timestamp}.json"
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
