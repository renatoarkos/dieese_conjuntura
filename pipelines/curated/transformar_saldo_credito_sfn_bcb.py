"""Transformação CURATED do saldo de crédito do SFN (ADR 0005) — a partir do RAW
gravado por
`pipelines/ingestao/bloco_2_monetario_credito/coleta_saldo_credito_sfn_bcb.py`
(BCB/SGS, 6 séries — total e recortes por tomador/tipo de recurso).
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from curated_supabase import baixar_objeto_storage, buscar_ultimo_raw, registrar_serie

SCRIPT_ORIGEM = "pipelines/ingestao/bloco_2_monetario_credito/coleta_saldo_credito_sfn_bcb.py"

CODIGO_PARA_INDICADOR = {
    "20539": "saldo_credito_sfn_total",
    "20541": "saldo_credito_sfn_pf",
    "20540": "saldo_credito_sfn_pj",
    "20542": "saldo_credito_sfn_recursos_livres",
    "20593": "saldo_credito_sfn_recursos_direcionados",
    "20570": "saldo_credito_sfn_livres_pf",
}


def _baixar_raw(codigo: str) -> list:
    registros = buscar_ultimo_raw(SCRIPT_ORIGEM, limite=20)
    alvo = next((r for r in registros if f"_{codigo}_" in (r.get("storage_path") or "")), None)
    if alvo is None:
        raise RuntimeError(f"Nenhum RAW da série SGS {codigo} encontrado para {SCRIPT_ORIGEM}")
    return json.loads(baixar_objeto_storage(alvo["storage_path"]).decode("utf-8"))


def _data_iso(data_bcb: str) -> str:
    dia, mes, ano = data_bcb.split("/")
    return f"{ano}-{mes}-{dia}"


def transformar() -> dict[str, int]:
    resultado = {}
    for codigo, indicador_id in CODIGO_PARA_INDICADOR.items():
        dados = _baixar_raw(codigo)
        pontos = [{"data_referencia": _data_iso(p["data"]), "valor": float(p["valor"])} for p in dados]
        registrar_serie(indicador_id, pontos)
        resultado[indicador_id] = len(pontos)
    return resultado


if __name__ == "__main__":
    for indicador_id, n in transformar().items():
        print(f"Transformação concluída: {n} pontos gravados em indicadores_serie ({indicador_id}).")
