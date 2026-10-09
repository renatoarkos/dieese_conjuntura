"""Transformação CURATED do PIB Brasil (ADR 0005) — a partir do RAW gravado por
`pipelines/ingestao/bloco_1_macroeconomia/coleta_pib_sidra.py` (SIDRA tabela 5932).

===============================================================================
QUAL RECORTE DO PIB VIRA O "INDICADOR" DO PAINEL
===============================================================================
A tabela 5932 traz 4 recortes de comparação diferentes (ver
docs/05-indicadores/CATALOGO_MESTRE_INDICADORES.md, indicador 1) misturados no
mesmo arquivo RAW, diferenciados pelo campo `D2C`. Este script usa só
`D2C=6561` ("Taxa trimestral em relação ao mesmo período do ano anterior") —
é o recorte mais citado como "o PIB cresceu X%" no noticiário econômico
brasileiro, por isso o escolhido como valor único do cartão. Os outros 3
recortes continuam preservados no arquivo RAW, disponíveis para quem quiser
estendê-los depois.

O período (`D3C`, formato "AAAAQQ", ex. "202602" = 2º trimestre de 2026) vira
`data_referencia` = primeiro dia do primeiro mês do trimestre (ex. "2026-04-01").
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from curated_supabase import baixar_objeto_storage, buscar_ultimo_raw, registrar_serie

import json

SCRIPT_ORIGEM = "pipelines/ingestao/bloco_1_macroeconomia/coleta_pib_sidra.py"
INDICADOR_ID = "pib_brasil"
D2C_ESCOLHIDO = "6561"  # taxa trimestral vs. mesmo período do ano anterior


# ------------------------------------------------------------------------
# PASSO 1 — baixar o RAW mais recente
# ------------------------------------------------------------------------
def _baixar_raw() -> list:
    registros = buscar_ultimo_raw(SCRIPT_ORIGEM)
    if not registros:
        raise RuntimeError(f"Nenhum RAW com status=sucesso encontrado para {SCRIPT_ORIGEM}")
    conteudo = baixar_objeto_storage(registros[0]["storage_path"])
    return json.loads(conteudo.decode("utf-8"))


# ------------------------------------------------------------------------
# PASSO 2 — converter o período SIDRA ("AAAAQQ") em data (1º dia do trimestre)
# ------------------------------------------------------------------------
def _data_do_trimestre(codigo_periodo: str) -> str:
    ano, trimestre = int(codigo_periodo[:4]), int(codigo_periodo[4:6])
    mes = (trimestre - 1) * 3 + 1
    return f"{ano:04d}-{mes:02d}-01"


# ------------------------------------------------------------------------
# PASSO 3 — filtrar o recorte escolhido e montar os pontos
# ------------------------------------------------------------------------
def _montar_pontos(dados: list) -> list[dict]:
    pontos = []
    for linha in dados[1:]:  # linha 0 é o cabeçalho do SIDRA
        if linha.get("D2C") != D2C_ESCOLHIDO:
            continue
        valor_bruto = linha.get("V")
        if valor_bruto in (None, "...", "-", "X"):
            continue
        pontos.append(
            {
                "data_referencia": _data_do_trimestre(linha["D3C"]),
                "valor": float(valor_bruto),
                "metadata": {"d3n": linha.get("D3N")},
            }
        )
    return pontos


def transformar() -> int:
    dados = _baixar_raw()
    pontos = _montar_pontos(dados)
    registrar_serie(INDICADOR_ID, pontos)
    return len(pontos)


if __name__ == "__main__":
    n = transformar()
    print(f"Transformação concluída: {n} pontos gravados em indicadores_serie ({INDICADOR_ID}).")
