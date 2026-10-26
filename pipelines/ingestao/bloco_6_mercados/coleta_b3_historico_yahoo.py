"""Coleta bruta de histórico diário (candles) de TODAS as ações da B3 já
catalogadas em `mercado_b3_ativos`, via o mesmo endpoint de gráfico da Yahoo
Finance já usado pelo resto da dimensão "mercados" — ver
`coleta_mercados_yahoo.py` para o raciocínio completo sobre a fonte.

===============================================================================
POR QUE UM SCRIPT NOVO (não só ampliar a lista fixa de coleta_mercados_yahoo.py)
===============================================================================
`coleta_mercados_yahoo.py` tem uma lista fixa de 9 tickers (índices, cripto,
3 ações). Pedido do responsável do projeto (2026-10-26), a partir de um print
mostrando só 3 ações cadastradas: "eu preciso de todas [as ações]... vá
populando o banco de dados com a série histórica."

Testado nesta sessão (`curl`, sem autenticação): o mesmo endpoint
(`v8/finance/chart/<ticker>.SA?range=1y&interval=1d`) funciona para
QUALQUER ação da B3, não só essas 3 — 10 tickers aleatórios testados (BBAS3,
MGLU3, WEGE3, ABEV3, B3SA3, RENT3, SUZB3 entre outros), todos HTTP 200 com
até 248 pontos de histórico diário.

A lista de tickers aqui NÃO é fixa: vem de `mercado_b3_ativos` (já populada
por `transformar_b3_brapi.py`, a partir da brapi.dev — 291 empresas reais,
já deduplicadas por lá). A brapi.dev continua sendo a fonte de "quais
empresas existem e qual o setor/capitalização de cada uma" (plano gratuito
não dá histórico diário); a Yahoo Finance entra só para completar o que a
brapi não dá de graça: histórico diário real, repetível todo dia.

===============================================================================
RESPEITO À FONTE
===============================================================================
~300 chamadas individuais (uma por ticker) em vez de uma chamada só —
intervalo de `_INTERVALO_ENTRE_CHAMADAS` entre elas (mesmo valor já usado
entre páginas em `coleta_b3_brapi.py`), para não martelar um endpoint
público sem autenticação. Uma falha isolada (ticker deslistado,
instabilidade pontual) não trava os demais — só avisa em stderr e segue.

===============================================================================
O QUE ESTE SCRIPT FAZ, PASSO A PASSO
===============================================================================
1. Lê a lista de tickers de `mercado_b3_ativos` (tabela já populada, ver
   migração 0011) via REST do Supabase.
2. Para cada ticker, busca `v8/finance/chart/<ticker>.SA?range=1y&interval=1d`.
3. Salva a resposta bruta de cada ticker em `data/raw/yahoo_finance/`, com
   prefixo "b3hist_" (para diferenciar das coletas de índices/cripto/ações
   piloto feitas por `coleta_mercados_yahoo.py`).
4. Registra cada arquivo no Supabase.

Este script NÃO calcula variação nem escolhe o ponto mais recente — isso é
trabalho de `transformar_b3_historico_yahoo.py` (camada CURATED).
"""

import json
import os
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from supabase_raw import registrar_coleta

RAIZ = Path(__file__).resolve().parents[3]
DESTINO = RAIZ / "data" / "raw" / "yahoo_finance"

_CABECALHOS = {"User-Agent": "Mozilla/5.0 (compatible; DIEESE360-bot/1.0)"}
_INTERVALO_ENTRE_CHAMADAS = 0.35


def _carregar_env() -> dict:
    env: dict[str, str] = {}
    caminho_env = RAIZ / ".env"
    if caminho_env.exists():
        for linha in caminho_env.read_text(encoding="utf-8").splitlines():
            linha = linha.strip()
            if not linha or linha.startswith("#") or "=" not in linha:
                continue
            chave, _, valor = linha.partition("=")
            env[chave.strip()] = valor.strip()
    return env


# ------------------------------------------------------------------------
# PASSO 1 — lista de tickers já catalogados (mercado_b3_ativos)
# ------------------------------------------------------------------------
def _listar_tickers() -> list[str]:
    env = _carregar_env()
    url = env.get("SUPABASE_URL") or os.environ.get("SUPABASE_URL")
    chave = env.get("SUPABASE_SERVICE_ROLE_KEY") or os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
    if not url or not chave:
        raise RuntimeError("SUPABASE_URL/SUPABASE_SERVICE_ROLE_KEY não configurados em .env")
    req = urllib.request.Request(
        f"{url}/rest/v1/mercado_b3_ativos?select=ticker&order=ticker.asc",
        headers={"apikey": chave, "Authorization": f"Bearer {chave}"},
    )
    with urllib.request.urlopen(req, timeout=60) as resposta:
        linhas = json.loads(resposta.read().decode("utf-8"))
    return [linha["ticker"] for linha in linhas]


# ------------------------------------------------------------------------
# PASSO 2 — buscar o histórico de 1 ano de um ticker
# ------------------------------------------------------------------------
def _buscar_dados(ticker: str) -> dict:
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}.SA?interval=1d&range=1y"
    req = urllib.request.Request(url, headers=_CABECALHOS)
    with urllib.request.urlopen(req, timeout=30) as resposta:
        return json.loads(resposta.read().decode("utf-8"))


# ------------------------------------------------------------------------
# Orquestração — lista de tickers pode vir truncada via argumento de linha
# de comando (usado só para teste local em lote pequeno antes de rodar com
# todas; o workflow do GitHub Actions roda sem argumento, lista inteira).
# ------------------------------------------------------------------------
def coletar(limite: int | None = None) -> list[Path]:
    DESTINO.mkdir(parents=True, exist_ok=True)
    tickers = _listar_tickers()
    if limite:
        tickers = tickers[:limite]
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

    arquivos = []
    for indice, ticker in enumerate(tickers):
        try:
            dados = _buscar_dados(ticker)
            arquivo = DESTINO / f"b3hist_{ticker}_{timestamp}.json"
            arquivo.write_text(json.dumps(dados, ensure_ascii=False), encoding="utf-8")
            arquivos.append(arquivo)
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError) as erro:
            print(f"Falha ao coletar histórico de {ticker}: {erro}", file=sys.stderr)
        if indice < len(tickers) - 1:
            time.sleep(_INTERVALO_ENTRE_CHAMADAS)
    return arquivos


if __name__ == "__main__":
    _limite = int(sys.argv[1]) if len(sys.argv) > 1 else None
    arquivos = coletar(_limite)
    print(f"Coleta concluída: {len(arquivos)} ticker(s) salvos em {DESTINO}")
    for caminho in arquivos:
        registrar_coleta(fonte=DESTINO.name, arquivo=caminho, script=__file__)
