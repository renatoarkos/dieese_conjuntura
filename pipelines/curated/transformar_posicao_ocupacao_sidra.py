"""Transformação CURATED da população ocupada (ADR 0005) — a partir do RAW gravado
por `pipelines/ingestao/bloco_4_mercado_trabalho/coleta_posicao_ocupacao_sidra.py`
(SIDRA tabela 4097).

Headline = D2C='4090' ("Pessoas de 14 anos ou mais de idade ocupadas na
semana de referência") + D4C='96165' ("Total", a soma de todas as posições
na ocupação — empregado com/sem carteira, conta própria etc., não uma
categoria específica). Unidade: mil pessoas.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from curated_supabase import baixar_objeto_storage, buscar_ultimo_raw, registrar_serie

SCRIPT_ORIGEM = "pipelines/ingestao/bloco_4_mercado_trabalho/coleta_posicao_ocupacao_sidra.py"
INDICADOR_ID = "populacao_ocupada"
D2C_ESCOLHIDO = "4090"
D4C_ESCOLHIDO = "96165"  # Total


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
        if linha.get("D2C") != D2C_ESCOLHIDO or linha.get("D4C") != D4C_ESCOLHIDO:
            continue
        valor_bruto = linha.get("V")
        if valor_bruto in (None, "...", "-", "X"):
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
