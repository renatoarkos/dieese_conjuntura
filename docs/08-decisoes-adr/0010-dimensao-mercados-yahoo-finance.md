# ADR 0010 — Dimensão "Mercados financeiros" via endpoint público da Yahoo Finance

## Status

Aceito e implementado — 2026-10-15.

## Contexto

Em 2026-10-14, ainda nesta sessão, o responsável do projeto pediu uma seção de ações da
B3 e de outras bolsas mundiais, incluindo criptoativos, com dimensão, carrossel e quadro
de dados próprios, pedindo explicitamente para investigar se a Yahoo Finance ou outra
biblioteca trazia esses dados. O pedido foi registrado e deliberadamente adiado (fora da
missão tradicional de indicadores socioeconômicos do DIEESE). Em 2026-10-15, depois de
reconstruir a plataforma num projeto Supabase novo (ver
`docs/08-decisoes-adr/INCIDENTE_2026-10-15_disco_cheio_supabase.md`), o responsável do
projeto pediu para retomar esse pedido.

Esta decisão é deliberadamente separada do padrão de "indicador socioeconômico" do
restante do projeto. Registrado antes nesta mesma sessão (pedido do responsável do
projeto sobre o carrossel/ticker da home): o conjunto principal de indicadores "não é uma
lista de ativos financeiros". Esta dimensão nova não revoga essa decisão — ela cria um
espaço separado, com identidade visual e texto explicitamente diferenciados (ver
`frontend/js/inicio.js`, texto da dimensão "mercados"), para o pedido novo, sem misturar
cotação de mercado com os indicadores produzidos/validados pelo DIEESE.

## Pesquisa de fonte

Testado diretamente nesta sessão, antes de escrever qualquer código: o endpoint de
gráfico da Yahoo Finance (`query1.finance.yahoo.com/v8/finance/chart/<ticker>`) responde
publicamente, sem chave de API nem autenticação, tanto para índices (prefixo `^`, ex.
`^BVSP`) quanto para ações individuais (sufixo `.SA` para a B3, ex. `PETR4.SA`) e
criptoativos (sufixo `-USD`, ex. `BTC-USD`). Validado com 8 tickers reais antes de
escrever os scripts: Ibovespa, S&P 500, Nasdaq, Dow Jones, Bitcoin, Ethereum, PETR4,
VALE3 — todos devolveram preço e histórico recentes.

**Decisão: acessar o endpoint direto via `urllib` (biblioteca padrão), sem o pacote pip
`yfinance`** (wrapper popular para essa mesma API). Motivo: mantém a regra já estabelecida
desde o ADR 0001 ("nenhuma dependência além da biblioteca padrão do Python") — todos os
outros 35+ scripts de coleta deste projeto seguem essa regra, e os workflows do GitHub
Actions não têm nenhum passo de `pip install`. Introduzir `yfinance` quebraria essa
consistência e exigiria editar os 3 workflows para instalar a dependência antes de
cada execução. O endpoint cru já é suficiente e já foi validado.

## Decisão

1. **Nova dimensão `mercados`** adicionada à constraint de `dimensao` da tabela
   `indicadores` (migração `0010_dimensao_mercados.sql`), ao lado das 5 já existentes.
2. **Catálogo inicial de 9 indicadores**, não uma lista exaustiva de ativos (mesmo
   princípio de "cortes mais representativos" já usado em outras dimensões, ex. Limite
   Fiscal por UF): 4 índices de referência (Ibovespa, S&P 500, Nasdaq Composite, Dow
   Jones), 2 criptoativos (Bitcoin, Ethereum) e 3 ações da B3 entre as mais negociadas
   (Petrobras PETR4, Vale VALE3, Itaú Unibanco ITUB4). Classificação B (fonte agregadora
   de mercado, não estatística oficial primária — mesmo critério já usado para MDIC/Comex
   Stat e ANP).
3. **Novo bloco de pipeline** `pipelines/ingestao/bloco_6_mercados/coleta_mercados_yahoo.py`
   (coleta os 9 tickers, grava RAW em `data/raw/yahoo_finance/`) e
   `pipelines/curated/transformar_mercados_yahoo.py` (extrai o último candle diário válido
   de cada ticker, ignorando dias sem pregão, e publica em `indicadores_serie`). Mesmo
   padrão arquitetural de todo o resto do projeto: RAW → Storage/`raw_ingestoes` →
   CURATED.
4. **Periodicidade diária, fechamento, não tempo real**: a arquitetura do projeto (site
   estático + Supabase, sem backend próprio nem streaming) não comporta cotação
   intradiária ao vivo. Cada execução grava o último fechamento disponível (ou o último
   preço disponível para criptoativos, que negociam 24/7 sem fechamento no sentido
   tradicional — ressalva registrada no próprio `metodologia_md` do catálogo).
5. **Frontend**: nova seção de carrossel na home (`#dimensao-mercados`, mesmo componente
   de carrossel contínuo já usado nas outras 5 dimensões), com texto introdutório
   deixando explícito que não é produção do DIEESE e não é recomendação de investimento.
   Identidade visual deliberadamente mais neutra (tom `--azul-300`, sem cor própria da
   marca) que as outras 5 seções, reforçando essa diferença de natureza do dado.
6. **Agendamento**: adicionado como novo passo em `motores-diarios.yml` (mercados mudam
   todo dia útil, mesma cadência da Selic/Focus já cobertas por esse workflow) — não é um
   workflow novo, é um passo a mais no já existente.

## O que esta decisão NÃO resolve

- **Ícone próprio da dimensão** (`assets/dimensoes/icone-mercados.png`) ainda não existe
  — as outras 5 dimensões têm ícone gerado por IA seguindo o guia de estilo em
  `frontend/img-prompts.json`; esta ainda não. O carrossel funciona sem ele (degrada
  graciosamente, sem ícone), mas falta esse arquivo.
- **Cotação intradiária/tempo real** — fora de escopo da arquitetura atual (ver item 4
  acima). Se isso vier a ser pedido no futuro, é uma decisão de arquitetura nova (provável
  mudança de "site estático" para algo com backend/streaming), não uma extensão simples
  deste pipeline.
- **Lista de ativos**: se o responsável do projeto quiser adicionar/remover tickers, isso
  é só catálogo (`insert`/`delete` em `indicadores`) mais o dicionário `TICKERS` do script
  de coleta — não exige mudança de schema.

## Consequências

- Primeira dimensão da plataforma cujo dado não é produzido nem validado pelo DIEESE —
  por isso a separação visual e textual deliberada (item 5 acima), para não confundir o
  leitor sobre a natureza da informação.
- Nenhuma dependência pip nova; nenhuma mudança nos workflows além de passos adicionais
  dentro do já existente `motores-diarios.yml`.
- Reversibilidade alta: remover a dimensão é dropar as 9 linhas do catálogo e os 2
  scripts, sem efeito sobre nenhuma outra dimensão.
