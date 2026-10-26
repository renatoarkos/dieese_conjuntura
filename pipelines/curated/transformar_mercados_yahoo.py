"""Transformação CURATED da dimensão "mercados" (ADR 0010) — a partir do RAW
gravado por `pipelines/ingestao/bloco_6_mercados/coleta_mercados_yahoo.py`
(Yahoo Finance, 9 tickers: 4 índices, 2 criptoativos, 3 ações da B3).

Mesma situação de `transformar_commodities_bcb.py`: os 9 tickers são gravados
sob o mesmo `script`, então é preciso distinguir pelo nome do arquivo
(`_<nome_curto>_`) em vez de só pegar "o RAW mais recente".

===============================================================================
COMO OS PONTOS (DATA, VALOR) SÃO ESCOLHIDOS DENTRO DO RAW
===============================================================================
O RAW de cada ticker traz ~1 ano de candles diários (`range=1y`, ver
docstring do script de coleta). Este script grava TODOS os candles com
`close` não nulo (alguns dias vêm com `close: null` quando não houve pregão,
ex. feriado) — não só o mais recente. Isso preenche o histórico desde a
primeira execução (sparkline com dado real, variação calculável no mesmo
mecanismo já usado em todo o resto da plataforma — ponto mais recente vs.
ponto anterior), em vez de esperar dias de coleta acumularem ponto a ponto.
`registrar_serie` já faz upsert por `(indicador_id, data_referencia)`, então
rodar este script todo dia não duplica os dias já gravados, só adiciona o
mais recente.

A data de cada ponto é a data (UTC) do timestamp Unix do candle, não a data
da coleta — podem divergir em 1 dia perto da virada UTC/horário de mercado.
Simplificação deliberada e documentada: não é feita conversão para o fuso
horário de cada bolsa (B3/NYSE/Nasdaq fecham todos ainda dentro do mesmo dia
UTC na prática, mas isso não foi verificado caso a caso).

===============================================================================
CAMPOS EXTRAS NO `metadata` DO PONTO MAIS RECENTE (2026-10-23)
===============================================================================
O mesmo RAW já traz, em `chart.result[0].meta`, campos que antes não eram
aproveitados: volume do dia, máxima/mínima do dia, faixa de 52 semanas e
fechamento anterior. Testado e confirmado nesta sessão para ação B3 e
criptoativo — os mesmos campos populam para os dois tipos de ativo (exceto
`marketCap`, ausente no endpoint gratuito para qualquer tipo de ativo). Só o
PONTO MAIS RECENTE de cada execução grava esses campos em `metadata` — são
uma "foto do dia" (refletem o estado no momento da coleta), não uma série
histórica desses campos; os pontos mais antigos do histórico de 1 ano
continuam só com `data_referencia`/`valor`.
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from curated_supabase import baixar_objeto_storage, buscar_ultimo_raw, registrar_serie

SCRIPT_ORIGEM = "pipelines/ingestao/bloco_6_mercados/coleta_mercados_yahoo.py"

# nome_curto (usado no nome do arquivo RAW) -> id do indicador no catálogo CURATED
NOME_PARA_INDICADOR = {
    "ibovespa": "ibovespa",
    "sp500": "sp500",
    "nasdaq": "nasdaq",
    "dow_jones": "dow_jones",
    "bitcoin": "bitcoin",
    "ethereum": "ethereum",
    "petr4": "petr4",
    "vale3": "vale3",
    "itub4": "itub4",
}


# ------------------------------------------------------------------------
# PASSO 1 — baixar o RAW mais recente de um ticker específico
# ------------------------------------------------------------------------
def _baixar_raw(nome_curto: str) -> dict:
    registros = buscar_ultimo_raw(SCRIPT_ORIGEM, limite=len(NOME_PARA_INDICADOR) * 4)
    alvo = next(
        (r for r in registros if f"_{nome_curto}_" in (r.get("storage_path") or "")),
        None,
    )
    if alvo is None:
        raise RuntimeError(f"Nenhum RAW do ticker '{nome_curto}' encontrado para {SCRIPT_ORIGEM}")
    conteudo = baixar_objeto_storage(alvo["storage_path"])
    return json.loads(conteudo.decode("utf-8"))


# ------------------------------------------------------------------------
# PASSO 2 — extrair todos os candles válidos (close não nulo) + metadata
# extra (volume, faixa do dia, faixa de 52 semanas, fechamento anterior) no
# ponto mais recente, lida de chart.result[0].meta.
# ------------------------------------------------------------------------
_CAMPOS_META = {
    "regularMarketVolume": "volume",
    "regularMarketDayHigh": "maxima_dia",
    "regularMarketDayLow": "minima_dia",
    "fiftyTwoWeekHigh": "maxima_52_semanas",
    "fiftyTwoWeekLow": "minima_52_semanas",
    "chartPreviousClose": "fechamento_anterior",
}


def _metadata_extra(meta: dict) -> dict:
    extra = {}
    for campo_origem, campo_destino in _CAMPOS_META.items():
        valor = meta.get(campo_origem)
        if valor is not None:
            extra[campo_destino] = valor
    return extra


def _pontos_validos(dados: dict) -> list[dict]:
    resultado = (dados.get("chart") or {}).get("result") or []
    if not resultado:
        return []
    r = resultado[0]
    timestamps = r.get("timestamp") or []
    closes = ((r.get("indicators") or {}).get("quote") or [{}])[0].get("close") or []
    pontos = []
    for ts, close in zip(timestamps, closes):
        if close is not None:
            data = datetime.fromtimestamp(ts, tz=timezone.utc).date().isoformat()
            pontos.append({"data_referencia": data, "valor": round(float(close), 4)})
    extra = _metadata_extra(r.get("meta") or {})
    if pontos and extra:
        pontos[-1]["metadata"] = extra
    return pontos


def transformar() -> dict[str, int]:
    resultado = {}
    for nome_curto, indicador_id in NOME_PARA_INDICADOR.items():
        dados = _baixar_raw(nome_curto)
        pontos = _pontos_validos(dados)
        if not pontos:
            print(f"Aviso: nenhum candle válido para '{nome_curto}' no RAW mais recente — pulando.", file=sys.stderr)
            resultado[indicador_id] = 0
            continue
        registrar_serie(indicador_id, pontos)
        resultado[indicador_id] = len(pontos)
    return resultado


if __name__ == "__main__":
    resultado = transformar()
    for indicador_id, n in resultado.items():
        print(f"Transformação concluída: {n} ponto(s) gravado(s) em indicadores_serie ({indicador_id}).")
