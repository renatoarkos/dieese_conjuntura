# Inventário de Benchmark — Visualização de Dados de Mercado Financeiro

## 1. Objetivo

Levantar como os principais sites de dados de mercado (ações, índices, criptoativos) do mundo e do Brasil apresentam visualmente a informação — tipo de gráfico, estrutura de página, métricas exibidas, convenção de cor, navegação — para embasar o design de uma futura página de mercados financeiros ampliada na plataforma DIEESE 360. Este documento é só o inventário (etapa de pesquisa); a decisão de o que implementar, e como, é um passo seguinte, ainda não tomado aqui.

Pedido original do responsável do projeto (2026-10-22/23): estudar a diagramação de sites de bolsa/cripto, reunir o que há de melhor, e construir "a melhor página de acompanhamento de ações que vai existir no Brasil" — trazendo o máximo de indicadores extraíveis do Yahoo Finance e de outras fontes livres.

## 2. Metodologia

Pesquisa conduzida por três investigações paralelas (agentes de pesquisa), em 23/10/2026, usando WebSearch e WebFetch — **sem navegador real conectado** (a extensão Claude in Chrome não estava disponível nesta sessão), o que impediu renderizar visualmente páginas fortemente dependentes de JavaScript/canvas e páginas protegidas contra acesso automatizado (bloqueios 403/429/500, CAPTCHA). Isso é uma limitação real e deliberadamente sinalizada: **nenhuma captura de tela foi feita**; a cor exata de pixel, por exemplo, só pôde ser confirmada com precisão para o TradingView (via documentação oficial de biblioteca open-source).

Para cada afirmação não-trivial abaixo, o relatório distingue:
- **[confirmado]** — obtido por acesso direto ao HTML/texto real da página, ou por fonte primária oficial (blog da própria empresa, documentação, FAQ).
- **[fonte terceira]** — descrito por review, comparação, fórum ou documentação de terceiros, não verificado diretamente nesta sessão.
- **[não confirmado]** — conhecimento geral não verificado nesta sessão; tratado como hipótese, não fato.

Sites cobertos: Yahoo Finance, Google Finance, TradingView, Bloomberg Markets, MarketWatch, Investing.com, Finviz (tabela e mapa de calor), CoinMarketCap, CoinGecko, InfoMoney, StatusInvest, B3.

**Antes de qualquer decisão de design definitiva baseada neste documento, recomenda-se validação visual humana direta** (abrir as páginas, ou reconectar a extensão de navegador) especialmente para: Google Finance, Bloomberg Markets, MarketWatch, StatusInvest, B3 e o mapa de calor do Finviz — os seis pontos onde a pesquisa automatizada teve acesso parcial ou nulo.

## 3. Por site

### 3.1 Yahoo Finance

- **Gráfico**: resumo padrão usa área/baseline (linha com preenchimento); candlestick fica reservado a um "Advanced Chart" separado [confirmado].
- **Estrutura**: dashboard denso por blocos empilhados — tiles de índices no topo, abas por classe de ativo (World Indices, Futures, Bonds, Currencies, Sectors, Stocks, Crypto, ETFs...), tabelas regionais, ETFs em grade de mini-rankings, notícia intercalada [confirmado].
- **Métricas**: preço, variação (R$/%), volume, market cap, P/E, 52-week range (texto e provavelmente como faixa visual), beta, EPS, dividend yield, preço-alvo de analistas em range slider [confirmado, página de AAPL].
- **Cor**: verde/vermelho padrão do setor, tom exato não confirmado.
- **Destaque único**: retorno % já calculado em cada botão de seletor de período (1D/5D/1M/6M/YTD/1Y/5Y) — não precisa abrir o gráfico para saber quanto um ativo subiu no período.
- **Pontos fracos**: gráfico simples e avançado em páginas separadas (navegação fragmentada); densidade alta de notícia/anúncio.

### 3.2 Google Finance

- **Gráfico**: linha/área; a cor do próprio traçado (não só o número) muda com o sinal da variação no período [fonte terceira — não confirmado por observação direta; WebFetch bloqueado em todas as tentativas, inclusive pelas duas pesquisas independentes].
- **Estrutura**: blocos por categoria (Futuros, EUA, Europa, Ásia, Moedas, Cripto), notícias do dia, calendário de earnings, ranking "Most followed on Google" [fonte terceira].
- **Métricas**: preço, variação, faixa do dia, 52-week range, market cap, volume, P/E, dividend yield [fonte terceira, via schema de API que espelha os campos reais da página].
- **Destaque único**: desde 2006, marcadores de eventos corporativos (dividendos, splits, notícias) sobrepostos diretamente na linha do gráfico [fonte terceira]; em nov/2025 a Google anunciou uma camada de IA para gráficos comparativos gerados por linguagem natural [confirmado via blog oficial do Google].
- **Consenso entre as duas pesquisas independentes**: é o mais minimalista/arejado da lista — menos módulos simultâneos que o Yahoo, foco em achar informação rápido.
- **Ressalva**: seção mais frágil do levantamento — nenhuma das duas pesquisas conseguiu acesso direto.

### 3.3 TradingView

- **Gráfico**: candlestick é o padrão de destaque, mas a lista de tipos suportados é a mais extensa da categoria — 21 tipos, incluindo Renko, Kagi, Point&Figure, Heikin Ashi, volume footprint [confirmado, documentação oficial de suporte].
- **Cor das velas** [confirmado oficialmente, biblioteca open-source `lightweight-charts` que reflete o padrão visual do produto]: alta = **#26a69a** (verde-petróleo/teal), baixa = **#ef5350** (vermelho-coral) — um par dessaturado, mais "profissional" que verde/vermelho puro. Pavio em cinza neutro (#737375). **Esta é a única convenção de cor confirmada com precisão de hex em todo o levantamento.**
- **Estrutura**: barra de ferramentas de desenho (110+ ferramentas em 8 categorias), painéis sincronizáveis (preço + osciladores), watchlist e feed social de "ideias" da comunidade ao lado do gráfico [confirmado].
- **Mapa de calor próprio**: tiles agrupados por setor, tamanho por market cap/volume/turnover (com opção "mono size" para neutralizar viés de megacaps), paleta alternativa para daltonismo disponível [confirmado].
- **Destaque único**: Bar Replay (retroceder e reproduzir a formação histórica das velas, com 9 velocidades, sincronizável entre múltiplos gráficos); Pine Script (indicador customizado pela comunidade, 100.000+ scripts).
- **Pontos fracos**: opacidade sobre o que é dado real vs. atrasado (depende de acordo por bolsa, não é informado com clareza).

### 3.4 Bloomberg Markets

- **Acesso**: bloqueado (HTTP 403) em todas as tentativas das três pesquisas — nenhuma confirmação direta nesta seção inteira.
- **Estrutura** [fonte terceira, com conflitos entre fontes]: página de mercados mistura ticker de índices/câmbio/commodities com manchetes jornalísticas — não é um painel de dados puro. Ticker ao vivo no topo, densidade adaptativa por breakpoint. Paywall dinâmico desde 2018, ajustado algoritmicamente [confirmado o mecanismo, limite exato não].
- **Cor**: verde/vermelho confirmado como padrão (inclusive com modo de alto contraste documentado para acessibilidade); fundo branco predominante no site público, mas duas extrações reversas de terceiros divergem sobre os hex exatos — não usar como referência de pixel.
- **Contexto do Terminal** (produto profissional, não o site): densidade é valor de marca deliberado — a própria equipe de UX da Bloomberg documentou publicamente que a estratégia é "esconder complexidade", não simplificar, porque o usuário profissional valoriza dominar uma interface complexa.
- **Destaque único**: tabela país-a-país para índices regionais; integração editorial forte entre dado e texto jornalístico da mesma redação.

### 3.5 MarketWatch

- **Acesso**: parcialmente bloqueado (CAPTCHA/429 na maioria das tentativas); uma pesquisa conseguiu texto real de duas páginas, a outra foi totalmente bloqueada.
- **Estrutura** [confirmado onde indicado]: editorial-primeiro, não dashboard-primeiro — ticker compacto de 6 cotações no topo, cards de notícia com ticker embutido, tabelas de 5-6 colunas sem sparkline nem coluna de volume na visão de mercados [confirmado, acesso direto].
- **Página de ativo**: status de sessão explícito no texto (Premarket, "Delayed quote", timestamp), faixas (range bars) com marcador de posição para Day's Range e 52-Week Range, lista "Key Data" em marcadores (não grade), gauge de analistas com escala própria de 5 pontos (Sell-Under-Hold-Over-Buy) [confirmado, acesso direto a AAPL].
- **Destaque único**: Virtual Stock Exchange — simulador de bolsa em tempo real com ligas competitivas, sem equivalente nos outros 11 sites; exposição explícita do atraso/sessão do dado, sem esconder em tooltip.
- **Pontos fracos**: densidade editorial alta (muito card de notícia pequeno empilhado), paywall cruzado com Barron's/WSJ.

### 3.6 Investing.com

- **Gráfico**: "Streaming Chart" alternável entre área e candlestick, 6 escalas de tempo [confirmado, blog oficial].
- **Estrutura** [confirmado, acesso direto a múltiplas páginas]: tabela de índices com 46 linhas, abas Price/Performance/Technical/Charts; controle explícito de densidade pelo usuário — **Compact/Normal/Extended**, pouco comum entre os sites pesquisados; "Market Movers" com abas Most Active/Gainers/Losers.
- **Página de ativo**: badge "Trading near 52-week High", gauge de sentimento técnico de 5 estágios (Strong Sell–Strong Buy) repetido em três contextos, separação visual entre "Analysts Sentiment" (profissional) e "Members' Sentiments" (opinião de usuários), template único de página de ativo reaproveitado entre ações/índices/cripto/câmbio (só o bloco de métricas muda) [confirmado].
- **Calendário econômico**: confirmado como o recurso mais forte do site — ~66 eventos globais no dia consultado, campos Horário/País/Evento/Importância/Atual/Consenso/Anterior, filtros cruzados por país/categoria/importância [confirmado, acesso direto].
- **Destaque único**: calendário atual-vs-consenso-vs-anterior com filtro por importância, sem equivalente de escopo global aberto nos outros 11 sites; perfis de coluna comutáveis no screener.
- **Pontos fracos**: densidade muito alta, paywall granular linha-a-linha (ícones de cadeado), nags de upgrade constantes; o próprio site declara em texto que os dados "podem não ser em tempo real nem precisos" [confirmado, texto literal da página].

### 3.7 Finviz — tabela (Screener)

- **Estrutura** [confirmado, acesso direto]: **14 "visões" de coluna comutáveis** (Overview, Valuation, Financial, Ownership, Performance, Technical, Custom, Charts, Tickers, Basic, TA, News, Snapshot, Maps, Stats) aplicadas sobre o mesmo filtro, sem refazer a consulta — o padrão mais sofisticado de equilíbrio densidade/legibilidade encontrado no levantamento inteiro. 60+ critérios de filtro; 20 linhas/página no gratuito; delay de 1 minuto [confirmado, texto do rodapé].
- **Cor**: só a coluna de variação % é colorida; resto da tabela monocromático.
- **Pontos fracos**: paginação curta no gratuito, filtros em faixas predefinidas (sem valor numérico livre) no plano grátis.

### 3.8 Finviz — Mapa de calor (Map/Matrix)

Seção com maior detalhe por ser o padrão mais citado no pedido original ("bolha mostrando variação diária").

- **Tipo de visualização**: **treemap** (mapa de retângulos aninhados), não bolhas circulares. Técnica popularizada financeiramente pelo Finviz desde 2007.
- **Tamanho do bloco**: capitalização de mercado [confirmado, blog oficial].
- **Cor do bloco**: variação % do período, verde=alta/vermelho=queda, com intensidade crescendo com a magnitude até saturar [confirmado por convergência de múltiplas fontes terceiras; escala exata de corte não encontrada em fonte oficial].
- **Hierarquia**: setor → indústria → empresa individual, com rótulo de texto fixo por grupo de setor.
- **Texto no bloco**: ticker em destaque; variação % abaixo quando há espaço; blocos microcap podem mostrar só o ticker.
- **Interatividade**: tooltip ao passar o mouse (nome, preço, variação, histórico), zoom/pan [fonte terceira].
- **Variedade de mapas** (achado mais relevante desta seção, confirmado via blog oficial): o Finviz não tem um heatmap só — tem vários, todos no mesmo layout de treemap, variando o que a cor representa: por setor, por índice específico (Dow 30, Nasdaq 100, Russell 2000), **por faixa de capitalização**, **por drawdown/ganho de 52 semanas**, **por atividade de insider** (aqui a cor muda de convenção: azul=compra/vermelho=venda, intensidade proporcional ao volume de 6 meses), por tema estrutural (ex. Inteligência Artificial), além de Mundo, ETFs, Futuros e Cripto.
- **Acessibilidade**: paletas Dark/Light/**Colorblind** selecionáveis no recurso de embed [confirmado, blog oficial].
- **Evolução do produto — "Finviz Matrix"** (2024-2025): resposta direta do próprio Finviz à limitação clássica do treemap ponderado por cap (poucas megacaps podem fazer o mapa parecer "tudo verde" mesmo com a maioria das ações individuais em queda) — grade alternativa onde linha=indústria e coluna=faixa de capitalização, com tooltip "Why Is It Moving" [confirmado, blog oficial].
- **Fundo**: escuro, reforça contraste das cores.
- **Ressalva honesta**: escala exata de cor, mecanismo de drill-down e densidade de texto por bloco na versão ao vivo não foram confirmados visualmente (JS/canvas, sem navegador disponível). A descrição acima é a mais bem fundamentada do documento (múltiplas fontes primárias do próprio Finviz), mas ainda não é observação direta da tela.

### 3.9 CoinMarketCap

- **Estrutura** [confirmado, acesso direto]: tabela de ranking (#, Nome, Preço, variação 1h/24h/7d, Market Cap, Volume 24h, Circulating Supply, Sentiment, sparkline de 7 dias), barra de indicadores globais no topo (Market Cap total, índice CMC20 próprio, Fear & Greed Index, liquidações 24h), abas (Top, Trending, Gainers, New...), 101 linhas por página com paginação (8.000+ ativos).
- **Destaque único**: dashboards nativos de "clima de mercado" (CMC20, Fear & Greed, Altcoin Season Index, Bitcoin Dominance, mapa de liquidações, ETF Flows) acessíveis direto da home.
- **Achado de qualidade**: seção educativa "About Bitcoin" com dado desatualizado (ATH de 2021, exchange descontinuada) coexistindo com dado em tempo real no cabeçalho da mesma página — problema real de manutenção de conteúdo, encontrado por acesso direto.
- **Pontos fracos**: menu com 10+ categorias de primeiro nível (desorientador); vínculo histórico com a Binance citado por terceiros como motivo de desconfiança sobre neutralidade do ranking [alegação recorrente, não verificação própria].

### 3.10 CoinGecko

- **Estrutura** [confirmado, acesso direto]: tabela com 4 janelas de variação simultâneas (1h/24h/7d/30d), colunas FDV e razão Market Cap/FDV, customização de colunas/linhas pelo usuário, "Quick Filters" interpretativos (On the Move, Blue Chips, Growing Projects), filtros numéricos por faixa.
- **Página de ativo**: gráfico TradingView embutido, comparação com outras moedas no mesmo gráfico, métricas de derivativos (open interest, funding rate), dados de receita de protocolo (Token Terminal).
- **Destaque único — Trust Score**: nota de 1 a 10 por exchange/par de negociação, considerando liquidez, regulação, segurança, histórico de incidentes e prova de reservas [confirmado, metodologia oficial publicada] — único item de toda a lista de 12 sites que ataca diretamente o problema de volume manipulável, dando ao usuário um filtro de confiabilidade embutido na própria interface.
- **Achado de qualidade**: dominância do BTC exibida com valores diferentes (57,5% vs. 57,9%) em dois widgets da mesma página — inconsistência interna real, encontrada por acesso direto.
- **Pontos fracos**: densidade extrema de filtros/colunas; navegação por tema confusa (centenas de categorias).

### 3.11 InfoMoney

- **Estrutura** [confirmado, acesso direto à ficha de PETR4]: bloco estático de cotação (abertura, fechamento anterior, mínima/máxima, negócios, variação dia/mês/ano/12 meses), abas Gráfico/Notícias/Histórico/Indicadores/Dividendos/Desdobramento/Sobre/Subscrições/Relacionados — mas Indicadores/Dividendos/Histórico carregam via JS e ficaram vazios no fetch. Seção "Últimas Notícias sobre [ticker]" dentro da própria ficha.
- **Caráter**: portal de notícias com widget de cotação embutido, não dashboard-primeiro — densidade alta de chamada comercial (cursos, planilhas, simuladores) misturada à navegação da cotação [confirmado, texto direto da página].
- **Destaque único**: amarração entre cotação e notícia específica daquele ticker na mesma tela, sustentada pelo maior volume de produção jornalística financeira diária em português da lista.
- **Ponto fraco**: conteúdo analiticamente mais relevante (indicadores, dividendos) depende de JS pra aparecer, enquanto o promocional é sempre estático/visível.

### 3.12 StatusInvest

- **Acesso**: bloqueado por HTTP 403 a nível de domínio, reproduzido de forma independente por duas pesquisas diferentes. Parcialmente contornado por uma terceira pesquisa via trechos reais indexados (fichas de BDRs e da própria PETR4) encontrados por busca.
- **Estrutura** [confirmado por trechos reais indexados, não por fetch direto completo]: ficha organizada em blocos por dimensão analítica — **Valuation** (P/L, P/VP, DY, EV/EBITDA, EV/EBIT, P/EBIT, PSR, P/Ativo, VPA, LPA), **Endividamento** (inclui liquidez corrente), **Eficiência**, **Rentabilidade** (ROE, ROA), **Crescimento**. Indicador não aplicável aparece como traço, não zero. Atraso de cotação de 15 minutos.
- **Cobertura**: plano gratuito amplo — ações, FIIs, BDRs, ETFs e glossário sem paywall [fonte terceira, múltiplas fontes convergentes].
- **Destaque único**: é o único site da lista que dá de graça uma ficha fundamentalista completa e categorizada por dimensão analítica para ações, FIIs, BDRs e ETFs brasileiros — cobertura de FII que nenhum concorrente internacional da lista replica. A categorização por dimensão (valuation/endividamento/eficiência/rentabilidade/crescimento), em vez de lista plana, é a ideia de design mais transponível para um observatório socioeconômico organizado por dimensão.
- **Não confirmado**: existência de "score" proprietário, tipo de gráfico, paleta de cor, densidade visual real da tela — nenhuma fonte descreveu isso com precisão suficiente; não foi inventado.

### 3.13 B3 (Ibovespa)

- **Acesso**: página de estatísticas do índice deu HTTP 500 (reproduzido de forma independente por duas pesquisas); página de composição carregou mas sem dado (JS); página de metodologia carregou com conteúdo estático real.
- **Metodologia** [confirmado, fetch direto à página de metodologia]: índice criado em 1968, cobre ~80% dos negócios/volume financeiro do mercado; inclusão por Índice de Negociabilidade (presença em ativos somando 85% do IN, buffer de 90%, presença em 95% dos pregões, volume mínimo 0,1%); ponderação por valor de mercado do free float com cap de 20% por empresa e 2x o IN; rebalanceamento quadrimestral (jan/mai/set).
- **Achado de qualidade**: a composição divulgada publicamente já estava expirada na data da pesquisa, e o próprio material da B3 se contradiz sobre o número de ativos na carteira (79 vs. 76) — inconsistência editorial real, encontrada por acesso direto.
- **Destaque único**: é a única fonte primária e oficial entre os 12 sites — todos os outros republicam dado que, para ativos brasileiros, se origina na B3. A B3 publica critérios completos e versionados de inclusão/exclusão/ponderação/rebalanceamento ao lado do índice — exatamente o padrão de metadados que o CLAUDE.md deste projeto já exige para todo indicador.
- **Não confirmado**: tipo de gráfico, cor, densidade da tela viva do índice (a única tela viva tentada deu 500).

## 4. Padrões recorrentes entre os 12 sites

- **Candlestick vs. linha/área**: candlestick domina em contexto de análise técnica dedicada (TradingView, Advanced Chart do Yahoo, opcional no Investing.com/Google Finance); linha/área domina no resumo rápido de um ativo. Nenhum site usa candlestick como padrão numa visão geral de múltiplos ativos — ali prevalece tabela numérica, eventualmente com sparkline.
- **Tabela densa com colunas comutáveis** (Finviz com 14 visões, Investing.com com 9 perfis de coluna no screener) é o padrão mais sofisticado para equilibrar densidade e legibilidade.
- **Faixa (range bar) com marcador de posição** para variação do dia e de 52 semanas aparece de forma consistente em Yahoo, MarketWatch e Investing.com, como alternativa visual ao texto puro "mín–máx".
- **Gauge/velocímetro de sentimento** é assinatura do Investing.com, sem equivalente direto nos outros 11.
- **Paleta teal/coral dessaturada** do TradingView é a única convenção de cor confirmada com precisão de hex em todo o levantamento.
- **Acessibilidade de cor** tratada explicitamente só por Bloomberg (alto contraste) e TradingView (paleta colorblind no heatmap) — nenhum outro site sinaliza isso.
- **Mapa de calor/treemap** aparece em pelo menos 3 sites (Finviz, TradingView, e um link de "Crypto Heatmap" no rodapé do Yahoo) — é um padrão estabelecido, não uma excentricidade do Finviz.
- **Fusão editorial dado+notícia** é mais forte em MarketWatch, Bloomberg e InfoMoney; mais fraca em Google Finance e TradingView (dado primeiro, notícia secundária).
- **Selo de confiabilidade/metodologia** só existe de fato no CoinGecko (Trust Score por exchange) — nenhum outro site comunica visualmente a diferença entre dado primário oficial e dado agregado/estimado de terceiro.

## 5. Fontes de dados técnicas pesquisadas (o que dá para extrair de fato)

Pesquisa técnica complementar, feita diretamente contra as APIs (não contra as páginas visuais).

### 5.1 Endpoint público da Yahoo Finance (já em uso no projeto, `pipelines/ingestao/bloco_6_mercados/`)

O endpoint `query1.finance.yahoo.com/v8/finance/chart/<ticker>` (sem chave, sem login, usado hoje pela plataforma) devolve, no objeto `meta`, muito mais campos do que a implementação atual aproveita:

```
regularMarketPrice, regularMarketChangePercent, regularMarketVolume,
regularMarketDayHigh, regularMarketDayLow, chartPreviousClose,
fiftyTwoWeekHigh, fiftyTwoWeekLow, longName, shortName,
exchangeName, fullExchangeName, currency, timezone
```

Testado e confirmado nesta sessão para ação B3 (PETR4.SA) e criptoativo (BTC-USD) — os mesmos campos (volume, faixa do dia, 52 semanas, variação %) populam para os dois tipos de ativo. `marketCap` não aparece para criptoativos neste endpoint (esperado).

O endpoint `v7/finance/quote` (mais rico — teria P/E, dividend yield etc.) **exige autenticação** (cookie + token "crumb") e retornou HTTP 401 sem ela — é o mecanismo que o pacote `yfinance` resolve internamente. Não testado como viável sem essa camada de autenticação adicional.

### 5.2 brapi.dev — API brasileira dedicada à B3

Testada diretamente nesta sessão: `brapi.dev/api/quote/list` devolve um catálogo amplo de ações/fundos/BDRs da B3 com setor, subsetor, capitalização, variação e volume; `brapi.dev/api/quote/{ticker}?fundamental=true` devolve indicadores fundamentalistas (P/L, LPA, capitalização, faixa de 52 semanas, faixa do dia).

- **Limites confirmados** [WebSearch, FAQ oficial]: plano gratuito = 15.000 requisições/mês, 1 ticker por chamada, histórico de até 3 meses, delay de ~30 minutos para ações. Exige conta e chave de API (os termos pedem para não expor a chave no frontend — mesma regra já seguida neste projeto para toda chave secreta).
- Não avaliado nesta pesquisa: estabilidade/confiabilidade da fonte de dado por trás da brapi (de onde ela próprio extrai os dados), nem comparação completa de cobertura contra a Yahoo Finance para ativos específicos.

## 6. Recomendação de design — "o que a melhor página de mercado do Brasil deveria ter"

Esta síntese (produzida por uma das três pesquisas, com explicitamente a perspectiva de usuário avançado de dados financeiros) é o resultado mais importante deste documento para a próxima etapa do projeto. Parte de uma premissa central: **o público do DIEESE 360 é o pesquisador econômico e sindical, não o trader** — isso muda a prioridade de design em relação a qualquer um dos 12 sites pesquisados, que foram construídos para outro usuário.

1. **Tipos de gráfico, por contexto.** Visão geral de mercado: linha/área simples, sem candlestick — candlestick comunica informação de execução intradiária (abertura/máxima/mínima/fechamento) que é ruído para quem acompanha conjuntura, não faz day trade. Página de ativo individual: manter linha/área, mas fazer a cor do próprio traçado mudar com o sinal do período (ideia do Google Finance) — leitura de direção imediata. Candlestick e indicadores técnicos (linguagem do TradingView) não têm lugar nesta plataforma.

2. **Retorno por janela de tempo, exposto, não escondido.** A ideia do Yahoo Finance — retorno % de cada período (1M, YTD, 1A, 5A) já calculado no próprio seletor — é diretamente relevante para pesquisa de conjuntura, onde comparar janelas (desde início de governo, desde um choque, no ano) é tarefa constante.

3. **Mapa de calor/treemap: sim, mas com uma condição.** Vale adotar o padrão Finviz de um único layout de treemap (por setor da economia, por exemplo) com um seletor que troca só a métrica de cor — não construir um treemap por métrica. É indispensável acompanhar o treemap de um indicador simples de amplitude ("X de Y ativos em alta/queda" — ver "Finviz Matrix", criado justamente para resolver esse problema de leitura enganosa), para não deixar o leitor concluir representatividade só pela cor dominante.

4. **Métricas essenciais vs. supérfluas.** Essencial: valor atual, variação no dia, variação acumulada (mês/ano/12 meses), e para qualquer índice brasileiro mostrado, sua composição e metodologia citando a fonte oficial (padrão B3). Supérfluo para este público: P/L, EV/EBITDA, FDV, funding rate, book de ofertas, Treasury Holdings — métricas de avaliação de ativo individual para decisão de compra/venda (domínio do StatusInvest/CoinMarketCap/CoinGecko) são ruído fora do escopo de um observatório socioeconômico.

5. **Convenção de cor.** Manter verde/vermelho — é universal, desviar custaria clareza sem ganho. Adicionar, inspirado no Trust Score do CoinGecko, um selo de confiabilidade/metodologia por indicador (atualidade, metodologia documentada, data da última revisão) — operacionaliza o princípio já existente no CLAUDE.md do projeto ("todo indicador deve possuir metadados") num elemento visual simples. Reservar uma cor de destaque (não verde/vermelho) só para "dado oficial primário confirmado" vs. "dado agregado/estimado de terceiro" — nenhum dos 12 sites comunica essa diferença visualmente, e é central ao princípio de priorizar fontes primárias.

6. **Navegação/filtros.** A ideia mais forte: abas de "visão analítica" do Finviz (Overview/Valuation/Performance/Technical) sobre o mesmo recorte filtrado, adaptada para alternar entre "visão cambial", "visão de preços", "visão de atividade", "visão de emprego" sem perder o filtro selecionado. Combinada com o calendário econômico do Investing.com (atual vs. consenso vs. anterior, filtrado por importância) — adaptado para divulgações brasileiras (IPCA, PNAD, Caged, PIB, Copom), sempre restrito a fontes oficiais, nunca inventando data de divulgação.

7. **Notícia/contexto ancorado ao dado, mas rotulado.** A fusão editorial do MarketWatch/InfoMoney (notícia ancorada no número, não num card separado) é a ideia mais alinhada ao princípio do projeto de diferenciar dado, evidência, hipótese e interpretação — desde que o bloco de contexto fique claramente rotulado como interpretação, nunca misturado ao dado bruto sem essa marca.

8. **Densidade de informação.** Nenhum dos 12 sites tem a densidade ideal para este público — os agregadores internacionais pecam para mais (ruído, anúncio, métrica supérflua), o Google Finance peca para menos (sem metodologia, sem contexto). O ponto ideal está mais perto do StatusInvest (informação categorizada por dimensão analítica, densa mas organizada, sem anúncio agressivo) do que de qualquer agregador internacional — adaptado para dimensões econômicas em vez de fundamentalistas de empresa.

**Síntese em uma frase**: a melhor página de mercado para pesquisa de conjuntura não deveria copiar a interface de nenhum site de trading da lista — deveria combinar a clareza de leitura temporal do Yahoo/Google Finance, a organização por dimensão analítica do StatusInvest, o rigor documental da B3, o calendário de expectativa-vs-realizado do Investing.com e o selo de confiabilidade do CoinGecko, descartando quase tudo que serve ao trader (candlestick, book de ofertas, múltiplos de avaliação, indicadores técnicos).

## 7. Dúvidas remanescentes

1. Aparência visual real (cor, layout exato, tipo de gráfico) de Google Finance, Bloomberg Markets, MarketWatch, StatusInvest e B3 (página viva) — nenhuma foi observada diretamente; tudo vem de fonte secundária ou está marcado como não verificado.
2. Escala de cor exata e mecanismo de drill-down do mapa de calor clássico do Finviz.
3. Existência de um "score" proprietário no StatusInvest.
4. Estabilidade e origem real do dado servido pela brapi.dev (não avaliada nesta pesquisa).
5. Viabilidade de autenticação (cookie+crumb) para o endpoint mais rico da Yahoo Finance (`v7/finance/quote`), caso se queira P/E e dividend yield direto da Yahoo sem depender da brapi.dev.

## 8. Próximo passo recomendado

Este documento é só o inventário. A próxima etapa (ainda não iniciada) é especificar e planejar — não implementar diretamente — um projeto de ampliação da página de mercados financeiros da plataforma, usando a seção 6 como ponto de partida para decisão de design, e a seção 5 para decisão de fonte de dado. Validação visual humana das lacunas da seção 7 antes de fechar o design é recomendada, mas não bloqueante.
