"""Coleta bruta de cotações de mercado (índices de bolsa, criptoativos e
ações da B3) via o endpoint público de cotações da Yahoo Finance.

Piloto técnico controlado, mesmo espírito dos demais blocos — ver
docs/08-decisoes-adr/0010-dimensao-mercados-yahoo-finance.md.

===============================================================================
O QUE ESTE INDICADOR MEDE, E POR QUE ESTA FONTE
===============================================================================
Pedido do responsável do projeto (2026-10-15): uma dimensão própria para
ações da B3, outras bolsas mundiais e criptoativos, separada do restante da
plataforma (que é só indicador socioeconômico). Pesquisado se havia uma fonte
gratuita e sem chave de API: o endpoint de gráfico da Yahoo Finance
(`query1.finance.yahoo.com/v8/finance/chart/<ticker>`) responde publicamente,
sem autenticação, tanto para índices (prefixo "^") quanto para ações
individuais (sufixo ".SA" para a B3) e criptoativos (sufixo "-USD").
Testado diretamente nesta sessão para os 9 tickers abaixo antes de este
script existir — todos retornaram preço real e histórico recente.

Não é usado o pacote `yfinance` (wrapper Python popular para esta mesma API):
o acesso direto ao endpoint via `urllib` mantém a mesma regra já aplicada a
todo o resto do piloto (ADR 0001 — nenhuma dependência além da biblioteca
padrão do Python), sem exigir `pip install` novo nos workflows do GitHub
Actions.

===============================================================================
COMO FUNCIONA O ENDPOINT
===============================================================================
GET /v8/finance/chart/<ticker>?interval=1d&range=1y
Devolve `chart.result[0]` com:
  - `meta`: símbolo, moeda, nome, preço mais recente.
  - `timestamp`: lista de timestamps Unix (um por candle diário).
  - `indicators.quote[0].close`: lista de preços de fechamento, mesma ordem
    dos timestamps (pode conter `null` em dias sem pregão, ex. feriado).
`range=1y` (não `1d`) é usado de propósito: cada coleta já traz ~1 ano de
histórico, o que preenche o sparkline, permite calcular variação (ponto
mais recente vs. ponto anterior, mesmo mecanismo já usado em todo o resto da
plataforma) e, desde 2026-10-23, o retorno em janelas mais longas (1 mês, no
ano, 12 meses — ver `transformar_mercados_yahoo.py` e `frontend/js/mercados.js`)
desde a primeira execução, sem esperar dias de coleta
acumularem histórico.

===============================================================================
O QUE ESTE SCRIPT FAZ, PASSO A PASSO
===============================================================================
1. Para cada ticker em TICKERS, busca o gráfico dos últimos 5 dias
   (`_buscar_dados`).
2. Salva a resposta bruta de cada ticker num arquivo separado em
   `data/raw/yahoo_finance/` (`_salvar_raw`).
3. Registra cada arquivo no Supabase.

Este script NÃO transforma o dado (não escolhe "o fechamento de hoje" nem
calcula variação) — isso é trabalho de `transformar_mercados_yahoo.py`.
"""

import json
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from supabase_raw import registrar_coleta

# ticker Yahoo Finance -> nome curto usado só no nome do arquivo RAW
# (o id do indicador real está no catálogo `indicadores`, mapeado em
# transformar_mercados_yahoo.py — TICKER_PARA_INDICADOR).
TICKERS = {
    "%5EBVSP": "ibovespa",
    "%5EGSPC": "sp500",
    "%5EIXIC": "nasdaq",
    "%5EDJI": "dow_jones",
    "BTC-USD": "bitcoin",
    "ETH-USD": "ethereum",
    "PETR4.SA": "petr4",
    "VALE3.SA": "vale3",
    "ITUB4.SA": "itub4",
}

DESTINO = Path(__file__).resolve().parents[3] / "data" / "raw" / "yahoo_finance"

_CABECALHOS = {"User-Agent": "Mozilla/5.0 (compatible; DIEESE360-bot/1.0)"}


# ------------------------------------------------------------------------
# PASSO 1 — buscar o gráfico de um ticker
# ------------------------------------------------------------------------
def _buscar_dados(ticker_codificado: str) -> dict:
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker_codificado}?interval=1d&range=1y"
    req = urllib.request.Request(url, headers=_CABECALHOS)
    with urllib.request.urlopen(req, timeout=30) as resposta:
        return json.loads(resposta.read().decode("utf-8"))


# ------------------------------------------------------------------------
# PASSO 2 — salvar a resposta bruta de um ticker em disco
# ------------------------------------------------------------------------
def _salvar_raw(nome_curto: str, dados: dict, timestamp: str) -> Path:
    arquivo = DESTINO / f"mercados_{nome_curto}_{timestamp}.json"
    arquivo.write_text(json.dumps(dados, ensure_ascii=False, indent=2), encoding="utf-8")
    return arquivo


# ------------------------------------------------------------------------
# Orquestração: repete os passos acima para cada ticker de TICKERS.
# Um ticker fora do ar (feriado de bolsa, instabilidade da fonte) não deve
# travar os demais — captura o erro, avisa em stderr, segue para o próximo.
# ------------------------------------------------------------------------
def coletar() -> list[Path]:
    DESTINO.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

    arquivos = []
    for ticker_codificado, nome_curto in TICKERS.items():
        try:
            dados = _buscar_dados(ticker_codificado)
            arquivos.append(_salvar_raw(nome_curto, dados, timestamp))
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError) as erro:
            print(f"Falha ao coletar {nome_curto} ({ticker_codificado}): {erro}", file=sys.stderr)
    return arquivos


if __name__ == "__main__":
    for caminho in coletar():
        print(f"Coleta concluída: {caminho}")
        registrar_coleta(fonte=DESTINO.name, arquivo=caminho, script=__file__)
