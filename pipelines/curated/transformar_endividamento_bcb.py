"""Transformação CURATED do endividamento familiar — parte BCB (ADR 0005) — a partir
do RAW gravado por
`pipelines/ingestao/bloco_2_monetario_credito/coleta_endividamento_bcb.py`
(BCB/SGS, família RNDBF, 5 séries).

===============================================================================
POR QUE 5 INDICADORES SEPARADOS, NÃO UM SÓ "ENDIVIDAMENTO"
===============================================================================
**QF10 resolvida em 2026-10-14** por leitura direta da aba `T15` da planilha
interna mais recente do DIEESE (leitura somente-leitura de
`materiais/originais/dieese/`): a aba expõe uma linha "SGS" com os 4 códigos
exatos que compõem a "Tabela 27" — 29037 e 29038 (Endividamento, Total e sem
financiamento imobiliário) e 29034 e 29035 (Comprometimento de renda
dessazonalizado, Total e sem financiamento imobiliário). O 5º código, 29265
(comprometimento de renda SEM ajuste sazonal), não faz parte da Tabela 27 —
é publicado como indicador complementar legítimo, claramente distinto, não
como candidato ambíguo. Os 5 continuam como indicadores próprios (em vez de
um "endividamento" único) porque medem coisas diferentes (saldo de dívida x
comprometimento de renda; com x sem financiamento imobiliário).
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from curated_supabase import baixar_objeto_storage, buscar_ultimo_raw, registrar_serie

SCRIPT_ORIGEM = "pipelines/ingestao/bloco_2_monetario_credito/coleta_endividamento_bcb.py"

CODIGO_PARA_INDICADOR = {
    "29034": "comprometimento_renda_com_ajuste",
    "29035": "comprometimento_renda_sem_imovel",
    "29265": "comprometimento_renda_sem_ajuste",
    "29037": "endividamento_familias_acumulado_12m",
    "29038": "endividamento_familias_sem_imovel",
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
