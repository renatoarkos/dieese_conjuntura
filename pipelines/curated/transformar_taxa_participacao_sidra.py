"""Transformação CURATED da taxa de participação na força de trabalho (ADR 0005) — a
partir do RAW gravado por
`pipelines/ingestao/bloco_4_mercado_trabalho/coleta_taxa_participacao_sidra.py`
(SIDRA tabela 6461).

Diferente do que a docstring do script de ingestão sugere ("sem classificação
adicional"), o RAW real mistura 6 variáveis D2C (nível, coeficiente de
variação, variações percentuais e um campo de texto "Situação da Variação" —
que nem é numérico, vem como "Z"). Headline = D2C='4096' ("Taxa de
participação na força de trabalho..."), confirmado inspecionando o RAW real.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from curated_supabase import baixar_objeto_storage, buscar_ultimo_raw, registrar_serie

SCRIPT_ORIGEM = "pipelines/ingestao/bloco_4_mercado_trabalho/coleta_taxa_participacao_sidra.py"
INDICADOR_ID = "taxa_participacao"
D2C_ESCOLHIDO = "4096"


def _baixar_raw() -> list:
    registros = buscar_ultimo_raw(SCRIPT_ORIGEM)
    if not registros:
        raise RuntimeError(f"Nenhum RAW com status=sucesso encontrado para {SCRIPT_ORIGEM}")
    return json.loads(baixar_objeto_storage(registros[0]["storage_path"]).decode("utf-8"))


def _data_do_trimestre(codigo_periodo: str) -> str:
    ano, trimestre = int(codigo_periodo[:4]), int(codigo_periodo[4:6])
    return f"{ano:04d}-{(trimestre - 1) * 3 + 1:02d}-01"


def _montar_pontos(dados: list) -> list[dict]:
    pontos = []
    for linha in dados[1:]:
        if linha.get("D2C") != D2C_ESCOLHIDO:
            continue
        valor_bruto = linha.get("V")
        if valor_bruto in (None, "...", "-", "X", "Z"):
            continue
        pontos.append({"data_referencia": _data_do_trimestre(linha["D3C"]), "valor": float(valor_bruto)})
    return pontos


def transformar() -> int:
    pontos = _montar_pontos(_baixar_raw())
    registrar_serie(INDICADOR_ID, pontos)
    return len(pontos)


if __name__ == "__main__":
    n = transformar()
    print(f"Transformação concluída: {n} pontos gravados em indicadores_serie ({INDICADOR_ID}).")
