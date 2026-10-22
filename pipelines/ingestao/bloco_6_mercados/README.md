# Bloco 6 — Mercados financeiros

Este bloco reúne a coleta bruta (camada RAW) de cotações de mercado: 4 índices de bolsa
(Ibovespa, S&P 500, Nasdaq Composite, Dow Jones), 2 criptoativos (Bitcoin, Ethereum) e 3
ações da B3 entre as mais negociadas (Petrobras PETR4, Vale VALE3, Itaú Unibanco ITUB4).

**Diferente dos demais blocos, este dado não é produzido nem validado pelo DIEESE** — é
referência de mercado (ver `docs/08-decisoes-adr/0010-dimensao-mercados-yahoo-finance.md`
para o contexto completo da decisão e a separação deliberada do restante da plataforma).

Fonte: endpoint público de gráfico da Yahoo Finance
(`query1.finance.yahoo.com/v8/finance/chart/<ticker>`), sem chave de API, acessado via
`urllib` puro — mesma regra de nenhuma dependência externa (ADR 0001) do resto do
projeto. Não usa o pacote `yfinance`.

## Como rodar

```bash
python3 pipelines/ingestao/bloco_6_mercados/coleta_mercados_yahoo.py
```

Coleta os 9 tickers numa única execução (mesmo padrão de scripts que trazem várias séries
relacionadas da mesma fonte, ex. `coleta_commodities_bcb.py`). Um ticker fora do ar não
derruba os demais — o erro é avisado em stderr e a coleta segue para o próximo.

## Limitação conhecida

Fechamento diário, não cotação em tempo real — a arquitetura do projeto (site estático +
Supabase, sem backend/streaming) não comporta isso. Ver ADR 0010, item "O que esta decisão
NÃO resolve".
