"""Transformação CURATED do Índice de Commodities Brasil — IC-Br (ADR 0005) — a partir
do RAW gravado por `pipelines/ingestao/bloco_1_macroeconomia/coleta_commodities_bcb.py`
(BCB/SGS, 4 séries: geral + 3 subíndices).

Mesma situação de `transformar_cambio_bcb.py`: as 4 séries são gravadas sob o
mesmo `script`, então é preciso distinguir pelo nome do arquivo (`_<codigo>_`)
em vez de só pegar "o RAW mais recente". Aqui, diferente do câmbio, as 4
séries viram 4 indicadores diferentes (não é uma escolha entre elas).
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from curated_supabase import baixar_objeto_storage, buscar_ultimo_raw, registrar_serie

SCRIPT_ORIGEM = "pipelines/ingestao/bloco_1_macroeconomia/coleta_commodities_bcb.py"

# código SGS -> id do indicador no catálogo CURATED
CODIGO_PARA_INDICADOR = {
    "27574": "commodities_geral",
    "27575": "commodities_agropecuaria",
    "27576": "commodities_metal",
    "27577": "commodities_energia",
}


# ------------------------------------------------------------------------
# PASSO 1 — baixar o RAW mais recente de um código SGS específico
# ------------------------------------------------------------------------
def _baixar_raw(codigo: str) -> list:
    registros = buscar_ultimo_raw(SCRIPT_ORIGEM, limite=16)
    alvo = next(
        (r for r in registros if f"_{codigo}_" in (r.get("storage_path") or "")),
        None,
    )
    if alvo is None:
        raise RuntimeError(f"Nenhum RAW da série SGS {codigo} encontrado para {SCRIPT_ORIGEM}")
    conteudo = baixar_objeto_storage(alvo["storage_path"])
    return json.loads(conteudo.decode("utf-8"))


# ------------------------------------------------------------------------
# PASSO 2 — converter "DD/MM/AAAA" em "AAAA-MM-DD" e montar os pontos
# ------------------------------------------------------------------------
def _data_iso(data_bcb: str) -> str:
    dia, mes, ano = data_bcb.split("/")
    return f"{ano}-{mes}-{dia}"


def _montar_pontos(dados: list) -> list[dict]:
    return [
        {"data_referencia": _data_iso(linha["data"]), "valor": float(linha["valor"])}
        for linha in dados
    ]


def transformar() -> dict[str, int]:
    resultado = {}
    for codigo, indicador_id in CODIGO_PARA_INDICADOR.items():
        dados = _baixar_raw(codigo)
        pontos = _montar_pontos(dados)
        registrar_serie(indicador_id, pontos)
        resultado[indicador_id] = len(pontos)
    return resultado


if __name__ == "__main__":
    resultado = transformar()
    for indicador_id, n in resultado.items():
        print(f"Transformação concluída: {n} pontos gravados em indicadores_serie ({indicador_id}).")
