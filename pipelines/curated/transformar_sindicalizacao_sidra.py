"""Transformação CURATED da taxa de sindicalização (ADR 0005) — a partir do RAW
gravado por
`pipelines/ingestao/bloco_4_mercado_trabalho/coleta_sindicalizacao_sidra.py`
(SIDRA tabela 8676).

Headline = D2C='12535' ("Taxa de sindicalização...") + D4C='47946' ("Total",
não um grupamento de atividade específico). Diferente dos demais indicadores
deste bloco, a série é ANUAL (não trimestral) — `D3C` vem como "AAAA" puro,
convertido para 1º de janeiro daquele ano. A série tem um hiato real em
2020/2021 (suplemento não levantado nesses anos, ver docstring do script de
ingestão) — isso aparece aqui como ausência de pontos, não como zero.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from curated_supabase import baixar_objeto_storage, buscar_ultimo_raw, registrar_serie

SCRIPT_ORIGEM = "pipelines/ingestao/bloco_4_mercado_trabalho/coleta_sindicalizacao_sidra.py"
INDICADOR_ID = "taxa_sindicalizacao"
D2C_ESCOLHIDO = "12535"
D4C_ESCOLHIDO = "47946"  # Total


def _baixar_raw() -> list:
    registros = buscar_ultimo_raw(SCRIPT_ORIGEM)
    if not registros:
        raise RuntimeError(f"Nenhum RAW com status=sucesso encontrado para {SCRIPT_ORIGEM}")
    return json.loads(baixar_objeto_storage(registros[0]["storage_path"]).decode("utf-8"))


def _montar_pontos(dados: list) -> list[dict]:
    pontos = []
    for linha in dados[1:]:
        if linha.get("D2C") != D2C_ESCOLHIDO or linha.get("D4C") != D4C_ESCOLHIDO:
            continue
        valor_bruto = linha.get("V")
        if valor_bruto in (None, "...", "-", "X"):
            continue
        ano = int(linha["D3C"])
        pontos.append({"data_referencia": f"{ano:04d}-01-01", "valor": float(valor_bruto)})
    return pontos


def transformar() -> int:
    pontos = _montar_pontos(_baixar_raw())
    registrar_serie(INDICADOR_ID, pontos)
    return len(pontos)


if __name__ == "__main__":
    n = transformar()
    print(f"Transformação concluída: {n} pontos gravados em indicadores_serie ({INDICADOR_ID}).")
