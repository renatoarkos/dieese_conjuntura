"""Transformação CURATED da produção industrial — PIM-PF (ADR 0005) — a partir do RAW
gravado por `pipelines/ingestao/bloco_1_macroeconomia/coleta_pim_industria_sidra.py`
(SIDRA tabela 8888). Mesma situação da PMS: o script de ingestão já pede só a
variável 11604 ("Variação acumulada em 12 meses") — sem recorte a escolher
aqui. Período (`D3C`, "AAAAMM") é mensal direto.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from curated_supabase import baixar_objeto_storage, buscar_ultimo_raw, registrar_serie

SCRIPT_ORIGEM = "pipelines/ingestao/bloco_1_macroeconomia/coleta_pim_industria_sidra.py"
INDICADOR_ID = "pim_producao_industrial"


def _baixar_raw() -> list:
    registros = buscar_ultimo_raw(SCRIPT_ORIGEM)
    if not registros:
        raise RuntimeError(f"Nenhum RAW com status=sucesso encontrado para {SCRIPT_ORIGEM}")
    conteudo = baixar_objeto_storage(registros[0]["storage_path"])
    return json.loads(conteudo.decode("utf-8"))


def _data_do_mes(codigo_periodo: str) -> str:
    return f"{codigo_periodo[:4]}-{codigo_periodo[4:6]}-01"


def _montar_pontos(dados: list) -> list[dict]:
    pontos = []
    for linha in dados[1:]:
        valor_bruto = linha.get("V")
        if valor_bruto in (None, "...", "-", "X"):
            continue
        pontos.append(
            {
                "data_referencia": _data_do_mes(linha["D3C"]),
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
