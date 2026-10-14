"""Transformação CURATED do endividamento familiar — parte BCB (ADR 0005) — a partir
do RAW gravado por
`pipelines/ingestao/bloco_2_monetario_credito/coleta_endividamento_bcb.py`
(BCB/SGS, família RNDBF, 3 séries candidatas).

===============================================================================
POR QUE 3 INDICADORES SEPARADOS, NÃO UM SÓ "ENDIVIDAMENTO"
===============================================================================
Qual destas 3 séries corresponde exatamente à "Tabela 27" citada pelo
material do DIEESE não está confirmado (QF10, pendência não bloqueante — ver
docs/00-visao-geral/ESTADO_DO_PROJETO.md). Publicar uma só, escolhida a dedo,
seria inventar uma correspondência que não foi validada. Por isso as 3 viram
indicadores próprios, cada um rotulado pelo que de fato mede — quando QF10
for respondida, basta decidir qual (ou quais) manter em destaque, sem
precisar refazer a coleta nem a transformação.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from curated_supabase import baixar_objeto_storage, buscar_ultimo_raw, registrar_serie

SCRIPT_ORIGEM = "pipelines/ingestao/bloco_2_monetario_credito/coleta_endividamento_bcb.py"

CODIGO_PARA_INDICADOR = {
    "29034": "comprometimento_renda_com_ajuste",
    "29265": "comprometimento_renda_sem_ajuste",
    "29037": "endividamento_familias_acumulado_12m",
}


def _baixar_raw(codigo: str) -> list:
    registros = buscar_ultimo_raw(SCRIPT_ORIGEM, limite=12)
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
