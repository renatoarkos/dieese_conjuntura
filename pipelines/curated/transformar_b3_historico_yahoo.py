"""Transformação CURATED do histórico diário de TODAS as ações da B3 (ADR
0010 Fase 2 ampliada, 2026-10-26) — a partir do RAW gravado por
`pipelines/ingestao/bloco_6_mercados/coleta_b3_historico_yahoo.py` (Yahoo
Finance, um arquivo por ticker).

===============================================================================
COMO OS PONTOS SÃO ESCOLHIDOS, E COMO A VARIAÇÃO % É CALCULADA
===============================================================================
Mesmo princípio de `transformar_mercados_yahoo.py`: cada RAW traz ~1 ano de
candles diários (`range=1y`); todos os candles com `close` não nulo são
gravados, não só o mais recente — preenche o histórico desde a primeira
execução. A diferença aqui é que o endpoint de candle NÃO devolve variação %
por dia (só o preço de fechamento e o volume) — por isso este script calcula
a variação % dia a dia a partir dos fechamentos consecutivos, com a mesma
fórmula já usada no resto da plataforma (ponto atual vs. ponto anterior).

===============================================================================
POR QUE `market_cap` NUNCA APARECE NO PAYLOAD DESTE SCRIPT (não é enviado
como null — a chave simplesmente não existe no dicionário do ponto)
===============================================================================
O endpoint de candle da Yahoo não dá capitalização de mercado por dia (só a
brapi.dev dá isso, e só para "hoje" — ver `transformar_b3_brapi.py`). O
ponto de HOJE de cada ticker já pode ter `market_cap` gravado pelo
`transformar_b3_brapi.py`. Se este script reenviasse esse mesmo ponto com
`market_cap: null` explícito, o upsert (merge-duplicates) apagaria o valor
já gravado. Por isso a chave é omitida do dicionário em vez de enviada como
null — o PostgREST só inclui no `ON CONFLICT DO UPDATE SET` as colunas que
aparecem no corpo da requisição; uma coluna ausente não é tocada numa linha
já existente (e vira NULL por padrão numa linha nova, que é o comportamento
certo quando não temos o dado).

===============================================================================
RESPEITO À FONTE / VOLUME DE DADOS
===============================================================================
~300 tickers x até ~250 pontos cada ≈ 75 mil linhas no backfill completo —
trivial para o Postgres, mas gravado em lotes por ticker (ver
`curated_supabase.registrar_serie_b3`) para não mandar tudo num POST só. Uma
falha isolada num ticker (RAW ausente, resposta malformada) não deve travar
os demais — avisa em stderr e segue.
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from curated_supabase import baixar_objeto_storage, buscar_ultimo_raw, registrar_serie_b3

SCRIPT_ORIGEM = "pipelines/ingestao/bloco_6_mercados/coleta_b3_historico_yahoo.py"

# Folga generosa sobre o tamanho esperado do catálogo (~300 ações): cobre
# uma execução completa do dia mesmo com reexecuções/retentativas no meio.
_LIMITE_RAW = 1500


# ------------------------------------------------------------------------
# PASSO 1 — achar o RAW mais recente de cada ticker. Todos os tickers usam
# o mesmo `script` (mesma situação de transformar_mercados_yahoo.py), então
# é preciso separar pelo nome do arquivo (b3hist_<TICKER>_<timestamp>.json).
# ------------------------------------------------------------------------
def _listar_raw_mais_recente_por_ticker() -> dict[str, dict]:
    registros = buscar_ultimo_raw(SCRIPT_ORIGEM, limite=_LIMITE_RAW)
    por_ticker: dict[str, dict] = {}
    for registro in registros:
        nome_arquivo = (registro.get("storage_path") or "").rsplit("/", 1)[-1]
        if not nome_arquivo.startswith("b3hist_"):
            continue
        meio = nome_arquivo[len("b3hist_"):]
        ticker = meio.rsplit("_", 1)[0]
        if ticker and ticker not in por_ticker:  # já vem ordenado mais recente primeiro
            por_ticker[ticker] = registro
    return por_ticker


# ------------------------------------------------------------------------
# PASSO 2 — extrair candles válidos (close não nulo) e calcular variação %
# dia a dia a partir dos fechamentos consecutivos.
# ------------------------------------------------------------------------
def _pontos_de_um_ticker(ticker: str, dados: dict) -> list[dict]:
    resultado = (dados.get("chart") or {}).get("result") or []
    if not resultado:
        return []
    r = resultado[0]
    timestamps = r.get("timestamp") or []
    quote = ((r.get("indicators") or {}).get("quote") or [{}])[0]
    closes = quote.get("close") or []
    volumes = quote.get("volume") or []

    candles = []
    for i, ts in enumerate(timestamps):
        close = closes[i] if i < len(closes) else None
        if close is None:
            continue
        data = datetime.fromtimestamp(ts, tz=timezone.utc).date().isoformat()
        volume = volumes[i] if i < len(volumes) else None
        candles.append({"data": data, "preco": round(float(close), 4), "volume": volume})

    pontos = []
    anterior = None
    for c in candles:
        ponto = {
            "ticker": ticker,
            "data_referencia": c["data"],
            "preco": c["preco"],
            "variacao_pct": (
                round(((c["preco"] - anterior["preco"]) / anterior["preco"]) * 100, 4)
                if anterior and anterior["preco"]
                else None
            ),
        }
        if c["volume"] is not None:
            ponto["volume"] = c["volume"]
        pontos.append(ponto)
        anterior = c
    return pontos


def transformar() -> dict:
    por_ticker = _listar_raw_mais_recente_por_ticker()
    tickers_ok = 0
    tickers_falha = 0
    total_pontos = 0
    for ticker, registro in por_ticker.items():
        try:
            conteudo = baixar_objeto_storage(registro["storage_path"])
            dados = json.loads(conteudo.decode("utf-8"))
            pontos = _pontos_de_um_ticker(ticker, dados)
            if not pontos:
                print(f"Aviso: nenhum candle válido para {ticker} — pulando.", file=sys.stderr)
                tickers_falha += 1
                continue
            registrar_serie_b3(pontos)
            total_pontos += len(pontos)
            tickers_ok += 1
        except (KeyError, ValueError, json.JSONDecodeError, RuntimeError) as erro:
            print(f"Falha ao transformar histórico de {ticker}: {erro}", file=sys.stderr)
            tickers_falha += 1
    return {"tickers_ok": tickers_ok, "tickers_falha": tickers_falha, "pontos": total_pontos}


if __name__ == "__main__":
    resultado = transformar()
    print(
        f"Transformação concluída: {resultado['tickers_ok']} ação(ões), "
        f"{resultado['pontos']} ponto(s) gravado(s) em mercado_b3_serie "
        f"({resultado['tickers_falha']} falha(s))."
    )
