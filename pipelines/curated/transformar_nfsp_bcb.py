"""Transformação CURATED da NFSP (ADR 0005) — a partir do RAW gravado por
`pipelines/ingestao/bloco_2_monetario_credito/coleta_nfsp_bcb.py` (BCB/SGS
5760, "NFSP sem desvalorização cambial (% PIB) — fluxo acumulado em 12 meses
— juros nominais — Total — Setor público consolidado"). Série única — QF07
resolvida (ver docstring do script de coleta).
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from curated_supabase import baixar_objeto_storage, buscar_ultimo_raw, registrar_serie

SCRIPT_ORIGEM = "pipelines/ingestao/bloco_2_monetario_credito/coleta_nfsp_bcb.py"
INDICADOR_ID = "nfsp_setor_publico_consolidado"


def _baixar_raw() -> list:
    registros = buscar_ultimo_raw(SCRIPT_ORIGEM)
    if not registros:
        raise RuntimeError(f"Nenhum RAW com status=sucesso encontrado para {SCRIPT_ORIGEM}")
    return json.loads(baixar_objeto_storage(registros[0]["storage_path"]).decode("utf-8"))


def _data_iso(data_bcb: str) -> str:
    dia, mes, ano = data_bcb.split("/")
    return f"{ano}-{mes}-{dia}"


def transformar() -> int:
    dados = _baixar_raw()
    pontos = [{"data_referencia": _data_iso(p["data"]), "valor": float(p["valor"])} for p in dados]
    registrar_serie(INDICADOR_ID, pontos)
    return len(pontos)


if __name__ == "__main__":
    n = transformar()
    print(f"Transformação concluída: {n} pontos gravados em indicadores_serie ({INDICADOR_ID}).")
