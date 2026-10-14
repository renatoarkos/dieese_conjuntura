"""Transformação CURATED do INPC (ADR 0005) — a partir do RAW gravado por
`pipelines/ingestao/bloco_3_inflacao/coleta_inpc_sidra.py` (SIDRA tabela 7063).

Mesma estrutura de 4 variáveis da tabela irmã do IPCA (7060), mas com códigos
`D2C` PRÓPRIOS (cada tabela do SIDRA numera suas variáveis de forma
independente — confirmado inspecionando os dois RAW reais antes de escrever
este script, para não presumir que o código do IPCA valeria aqui).
Headline = D2C='44' ("INPC - Variação mensal").
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from curated_supabase import baixar_objeto_storage, buscar_ultimo_raw, registrar_serie

SCRIPT_ORIGEM = "pipelines/ingestao/bloco_3_inflacao/coleta_inpc_sidra.py"
INDICADOR_ID = "inpc"
D2C_ESCOLHIDO = "44"  # INPC - Variação mensal


def _baixar_raw() -> list:
    registros = buscar_ultimo_raw(SCRIPT_ORIGEM)
    if not registros:
        raise RuntimeError(f"Nenhum RAW com status=sucesso encontrado para {SCRIPT_ORIGEM}")
    return json.loads(baixar_objeto_storage(registros[0]["storage_path"]).decode("utf-8"))


def _data_do_mes(codigo_periodo: str) -> str:
    return f"{codigo_periodo[:4]}-{codigo_periodo[4:6]}-01"


def _montar_pontos(dados: list) -> list[dict]:
    pontos = []
    for linha in dados[1:]:
        if linha.get("D2C") != D2C_ESCOLHIDO:
            continue
        valor_bruto = linha.get("V")
        if valor_bruto in (None, "...", "-", "X"):
            continue
        pontos.append({"data_referencia": _data_do_mes(linha["D3C"]), "valor": float(valor_bruto)})
    return pontos


def transformar() -> int:
    pontos = _montar_pontos(_baixar_raw())
    registrar_serie(INDICADOR_ID, pontos)
    return len(pontos)


if __name__ == "__main__":
    n = transformar()
    print(f"Transformação concluída: {n} pontos gravados em indicadores_serie ({INDICADOR_ID}).")
