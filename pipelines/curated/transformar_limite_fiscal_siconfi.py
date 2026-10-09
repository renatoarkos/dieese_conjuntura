"""Transformação CURATED do limite fiscal de pessoal por Estado (ADR 0005) — a partir do
RAW gravado por
`pipelines/ingestao/bloco_1_macroeconomia/coleta_limite_fiscal_siconfi.py` (SICONFI, RGF),
que grava um arquivo por UF (27 arquivos por rodada de coleta).

===============================================================================
QUAL LINHA DO RGF VIRA O VALOR DO INDICADOR
===============================================================================
Cada arquivo RAW tem ~300 linhas (uma por conta contábil × coluna do
demonstrativo). A métrica comparável ao limite da LRF é
`cod_conta=DespesaComPessoalTotal`, `coluna="% sobre a RCL Ajustada"`, dentro
de `anexo="RGF-Anexo 01"` — confirmado inspecionando um arquivo real (São
Paulo): 42,55% em 2026Q1, contra os limites legais de 49% (máximo),
46,55% (prudencial) e 44,1% (alerta), que são os mesmos para todas as UFs
(fixados por lei sobre a RCL de cada uma, não um valor em si).

===============================================================================
POR QUE "MÉDIA DAS 27 UFS" EM VEZ DE 27 INDICADORES SEPARADOS
===============================================================================
Simplificação deliberada desta primeira rodada CURATED (ver ADR 0005): em vez
de criar 27 linhas no catálogo `indicadores` (uma por UF), este script grava
UM indicador nacional (`limite_fiscal_pessoal`) cujo valor é a média simples
das 27 UFs, preservando o detalhe por UF em `metadata.por_uf` — nenhum dado é
perdido, só não tem card próprio por estado ainda. Expandir para 27
indicadores (ou um recurso de "ver por UF" no frontend lendo esse metadata) é
extensão natural, não um redesenho.
"""

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from curated_supabase import baixar_objeto_storage, buscar_ultimo_raw, registrar_serie

SCRIPT_ORIGEM = "pipelines/ingestao/bloco_1_macroeconomia/coleta_limite_fiscal_siconfi.py"
INDICADOR_ID = "limite_fiscal_pessoal"

PADRAO_ARQUIVO = re.compile(r"limite_fiscal_([A-Z]{2})_(\d{4})Q(\d)_")


# ------------------------------------------------------------------------
# PASSO 1 — baixar o arquivo mais recente de cada uma das 27 UFs
# ------------------------------------------------------------------------
def _baixar_ultima_rodada() -> dict[str, dict]:
    """Devolve {uf: dados_json} com o arquivo mais recente de cada UF. Pede
    bastante margem (limite=120) porque cada rodada de coleta grava 27
    arquivos de uma vez — isso cobre várias rodadas passadas, o suficiente
    para garantir que as 27 UFs apareçam mesmo que alguma tenha falhado numa
    rodada recente e só tenha sucesso numa anterior.
    """
    registros = buscar_ultimo_raw(SCRIPT_ORIGEM, limite=120)
    por_uf: dict[str, dict] = {}
    for registro in registros:
        m = PADRAO_ARQUIVO.search(registro.get("storage_path") or "")
        if not m:
            continue
        uf = m.group(1)
        if uf in por_uf:
            continue  # já temos uma versão mais recente desta UF (lista vem em ordem desc)
        conteudo = baixar_objeto_storage(registro["storage_path"])
        por_uf[uf] = json.loads(conteudo.decode("utf-8"))
    return por_uf


# ------------------------------------------------------------------------
# PASSO 2 — extrair "% sobre a RCL Ajustada" de DespesaComPessoalTotal
# ------------------------------------------------------------------------
def _percentual_despesa_pessoal(dados_uf: dict) -> float | None:
    for item in dados_uf.get("items", []):
        if (
            item.get("anexo") == "RGF-Anexo 01"
            and item.get("cod_conta") == "DespesaComPessoalTotal"
            and item.get("coluna") == "% sobre a RCL Ajustada"
        ):
            return float(item["valor"])
    return None


# ------------------------------------------------------------------------
# PASSO 3 — montar o ponto único (média + detalhe por UF), para a data de
# referência mais recente encontrada entre as UFs
# ------------------------------------------------------------------------
def _data_referencia(dados_uf: dict) -> str:
    item = dados_uf["items"][0]
    ano, periodo = item["exercicio"], item["periodo"]
    mes = (periodo - 1) * 4 + 1  # RGF é quadrimestral: períodos 1/2/3 -> jan/mai/set
    return f"{ano:04d}-{mes:02d}-01"


def transformar() -> int:
    por_uf = _baixar_ultima_rodada()
    percentuais: dict[str, float] = {}
    data_referencia = None
    for uf, dados_uf in por_uf.items():
        percentual = _percentual_despesa_pessoal(dados_uf)
        if percentual is None:
            continue
        percentuais[uf] = percentual
        if data_referencia is None:
            data_referencia = _data_referencia(dados_uf)

    if not percentuais:
        return 0

    media = round(sum(percentuais.values()) / len(percentuais), 2)
    ponto = {
        "data_referencia": data_referencia,
        "valor": media,
        "metadata": {
            "por_uf": percentuais,
            "limite_maximo_pct": 49.0,
            "limite_prudencial_pct": 46.55,
            "limite_alerta_pct": 44.1,
        },
    }
    registrar_serie(INDICADOR_ID, [ponto])
    return 1


if __name__ == "__main__":
    n = transformar()
    print(f"Transformação concluída: {n} ponto(s) gravado(s) em indicadores_serie ({INDICADOR_ID}).")
