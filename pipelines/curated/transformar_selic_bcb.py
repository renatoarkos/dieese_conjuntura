"""Transformação CURATED da Taxa Selic (ADR 0005) — a partir do RAW gravado por
`pipelines/ingestao/bloco_2_monetario_credito/coleta_selic_bcb.py` (BCB/SGS, 2 séries).

===============================================================================
POR QUE EMENDA DUAS SÉRIES (NÃO É UMA ESCOLHA ARBITRÁRIA)
===============================================================================
A série de Selic usada pelo DIEESE já foi confirmada, nesta mesma sessão de
projeto, como uma composição de duas séries SGS diferentes ao longo do tempo
(comparação ponto a ponto com 122 valores mensais do material original do
DIEESE, 100% de correspondência em ambos os trechos — ver
docs/04-fontes/bcb.md e docs/00-visao-geral/ESTADO_DO_PROJETO.md, achado de
2026-09-22):
  - SGS 4189 ("Selic acumulada no mês, anualizada") até jul/2024.
  - SGS 432 ("Meta Selic definida pelo Copom") a partir de ago/2024.
Este script aplica exatamente essa regra de corte já validada — não é uma
decisão nova tomada aqui.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from curated_supabase import baixar_objeto_storage, buscar_ultimo_raw, registrar_serie

SCRIPT_ORIGEM = "pipelines/ingestao/bloco_2_monetario_credito/coleta_selic_bcb.py"
INDICADOR_ID = "selic"
DATA_CORTE = "2024-08-01"  # SGS 4189 até jul/2024 (exclusive a partir daqui), SGS 432 dai em diante


def _baixar_raw(codigo: str) -> list:
    registros = buscar_ultimo_raw(SCRIPT_ORIGEM, limite=10)
    alvo = next((r for r in registros if f"_{codigo}_" in (r.get("storage_path") or "")), None)
    if alvo is None:
        raise RuntimeError(f"Nenhum RAW da série SGS {codigo} encontrado para {SCRIPT_ORIGEM}")
    return json.loads(baixar_objeto_storage(alvo["storage_path"]).decode("utf-8"))


def _data_iso(data_bcb: str) -> str:
    dia, mes, ano = data_bcb.split("/")
    return f"{ano}-{mes}-{dia}"


def transformar() -> int:
    serie_4189 = _baixar_raw("4189")
    serie_432 = _baixar_raw("432")

    pontos = [
        {"data_referencia": _data_iso(p["data"]), "valor": float(p["valor"]), "metadata": {"serie_sgs": "4189"}}
        for p in serie_4189
        if _data_iso(p["data"]) < DATA_CORTE
    ] + [
        {"data_referencia": _data_iso(p["data"]), "valor": float(p["valor"]), "metadata": {"serie_sgs": "432"}}
        for p in serie_432
        if _data_iso(p["data"]) >= DATA_CORTE
    ]
    pontos.sort(key=lambda p: p["data_referencia"])
    registrar_serie(INDICADOR_ID, pontos)
    return len(pontos)


if __name__ == "__main__":
    n = transformar()
    print(f"Transformação concluída: {n} pontos gravados em indicadores_serie ({INDICADOR_ID}).")
