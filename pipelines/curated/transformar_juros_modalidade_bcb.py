"""Transformação CURATED das taxas médias de juros por modalidade (ADR 0005) — a
partir do RAW gravado por
`pipelines/ingestao/bloco_2_monetario_credito/coleta_juros_modalidade_bcb.py`
(BCB/SGS, 4 séries independentes — recursos livres, PF/PJ).
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from curated_supabase import baixar_objeto_storage, buscar_ultimo_raw, registrar_serie

SCRIPT_ORIGEM = "pipelines/ingestao/bloco_2_monetario_credito/coleta_juros_modalidade_bcb.py"

CODIGO_PARA_INDICADOR = {
    "20728": "juros_pj_veiculos",
    "22019": "juros_pj_cartao_rotativo",
    "20741": "juros_pf_cheque_especial",
    "20742": "juros_pf_credito_pessoal",
}


def _baixar_raw(codigo: str) -> list:
    registros = buscar_ultimo_raw(SCRIPT_ORIGEM, limite=16)
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
