"""Transformação CURATED do rendimento médio real (ADR 0005) — a partir do RAW
gravado por
`pipelines/ingestao/bloco_4_mercado_trabalho/coleta_rendimento_medio_real_sidra.py`
(SIDRA tabela 5440).

A tabela mistura 4 variáveis D2 — 2 valores em reais (rendimento "habitual"
vs. "efetivamente recebido" no trabalho principal) e seus 2 coeficientes de
variação. **Bug real encontrado ao testar**: a primeira versão deste script
filtrava só por D4C (a única categoria presente, "Total"), sem checar D2 —
na prática pegava o PRIMEIRO registro de cada ponto, que calhava de ser um
coeficiente de variação (~0,8-1,0), não o valor em reais (~3.000+). Corrigido
filtrando também D2C='5932' — "rendimento habitual", o recorte exato citado
no nome do indicador no catálogo ("Rendimento médio real HABITUAL do
trabalho principal"), não o "efetivamente recebido" (D2C=5934, um conceito
diferente). D4C='96165' ("Total") segue sem ambiguidade, confirmado no RAW.

PENDÊNCIA CONHECIDA, NÃO RESOLVIDA AQUI: o material do DIEESE indica um
deflacionamento adicional próprio por cima deste valor (que já vem real do
IBGE) — ver docstring do script de ingestão e QF04. Este indicador publica o
dado bruto do IBGE; a dupla deflação (se existir) é uma decisão metodológica
que depende de documento interno do DIEESE, fora do alcance deste projeto.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from curated_supabase import baixar_objeto_storage, buscar_ultimo_raw, registrar_serie

SCRIPT_ORIGEM = "pipelines/ingestao/bloco_4_mercado_trabalho/coleta_rendimento_medio_real_sidra.py"
INDICADOR_ID = "rendimento_medio_real"
D2C_ESCOLHIDO = "5932"  # rendimento habitualmente recebido (não "efetivamente recebido" = 5934)
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
