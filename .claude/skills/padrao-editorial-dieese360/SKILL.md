---
name: padrao-editorial-dieese360
description: Padrão de escrita e de diagramação visual do DIEESE 360 — quando escrever qualquer texto visível no site (ou no chat com o responsável do projeto) e quando criar ou ajustar qualquer gráfico, cartão, quadro, legenda ou cor. Carregar antes de publicar texto novo ou elemento visual novo na plataforma.
---

# Padrão editorial do DIEESE 360

Este skill reúne, num só lugar, o que o projeto já decidiu sobre como o DIEESE 360 escreve e como ele se parece — para não precisar redescobrir isso a cada sessão, e para toda escrita/diagramação nova sair consistente com o que já existe. Ele não substitui as fontes abaixo; resume o que já está decidido nelas em forma de checklist de uso rápido. Em caso de conflito, as fontes originais prevalecem.

**Fontes (nesta ordem de autoridade):**
1. `CLAUDE.md` (raiz do repositório) — princípios permanentes do projeto.
2. `Prompt_mestre_escrita_academica_humana.md` (raiz) — guia completo de escrita.
3. `agents/editor-academico.md`, `agents/designer-marca.md`, `agents/engenheiro-frontend.md`, `agents/bi-dataviz.md` — papéis especializados que operacionalizam isso.
4. `research/notas/INVENTARIO_BENCHMARK_MERCADOS_FINANCEIROS.md` — benchmark de 12 sites de dado financeiro, com recomendação de design própria para este projeto (seção 6).
5. `frontend/css/styles.css` — tokens reais (cor, tipografia, espaçamento) já em produção.

## 1. Escrita (texto do site e texto do chat)

Vale para qualquer texto visível na interface (título, legenda, cartão, FAQ, aviso, metodologia) **e** para as respostas do Claude no chat com o responsável do projeto — não só para o conteúdo publicado.

- Seguir `Prompt_mestre_escrita_academica_humana.md` nas seções 8 e 11: nada de travessão como vício visual, nada de contraste artificial ("não é X, é Y"), nada de abertura genérica, nada de fórmula de ênfase vazia ("vale ressaltar", "é fundamental"), nada de conclusão-padrão ("em suma", "diante do exposto"), nada de tríade automática.
- Frases diretas e concretas. Calibrar certeza à evidência disponível (seção 9 do prompt mestre): não hedgear o que é fato, não afirmar categoricamente o que é hipótese.
- Nunca inventar fato institucional, fonte, data de divulgação, API ou metodologia — isso vale tanto para texto quanto para qualquer outro artefato (`CLAUDE.md`, seção PRINCÍPIOS).
- Todo indicador precisa deixar claro **em relação a quê** uma variação é medida (mesmo período do ano anterior? período imediatamente anterior? acumulado em 12 meses?) — não basta "% (variação)" sem qualificar. Verificar contra o script de transformação real (`pipelines/curated/transformar_*.py`) antes de escrever a descrição, nunca supor pelo nome do indicador.
- Antes de publicar texto de metodologia/unidade, perguntar: uma pessoa sem contexto prévio entende contra o que esse número está sendo comparado, só de ler isso? Se não, reescrever.

## 2. Diagramação (gráfico, quadro, legenda, cor)

### 2.1 Nada de tamanho ou espaçamento avulso

`frontend/css/styles.css` tem, no `:root`, quatro tokens de escala de apoio: `--fs-fine` (11px, anotação mínima), `--fs-label` (12px, rótulo em caixa alta), `--fs-caption` (13px, frase de apoio curta), `--fs-body-sm` (14px, parágrafo dentro de quadro). Qualquer badge, legenda ou nota nova usa um destes — nunca um valor de fonte próprio. Antes de escrever um `font-size`/`padding`/`margin` novo, verificar se já existe um token ou um componente equivalente para aquele papel visual e reaproveitar.

Quebra de texto também é diagramação: todo bloco de texto mais longo precisa de `max-width` em `ch` (medida de leitura, não a largura toda do contêiner) e, quando o espaço é apertado, de uma estratégia de corte deliberada (`line-clamp` em N linhas completas, nunca truncar bruscamente no meio de uma linha só).

### 2.2 Evitar o estereótipo de "site feito por IA"

Princípio fixado pelo responsável do projeto, aplicado tanto a design (`agents/designer-marca.md`) quanto a texto (seção 1 acima). Sinais a evitar: herói centralizado com badge-pílula, par de botões muito arredondados, cartões com sombra pesada em grade perfeitamente simétrica, ilustração 3D genérica de estoque, gradiente roxo-azul decorativo, paleta "creme quente + serifada + terracota" ou "quase preto + um pop de verde-ácido" sem motivo. Inspirar-se em portais de dado real: FRED, Our World in Data, GOV.UK/ONS, Eurostat, Trading Economics — layout denso e editorial, não landing page comercial.

### 2.3 Benchmark de visualização de dado de mercado

`research/notas/INVENTARIO_BENCHMARK_MERCADOS_FINANCEIROS.md` levantou 12 sites (Yahoo Finance, TradingView, Investing.com, Finviz, CoinMarketCap, StatusInvest, B3 etc.) e já traduziu isso em recomendação própria para este projeto (seção 6 do documento). Decisões já tomadas a partir dali, reaproveitar em vez de redecidir:

- **Linha/área, não candlestick.** Candlestick comunica execução intradiária — ruído para quem acompanha conjuntura, não faz day trade. Visão geral: linha/área simples. Página de ativo: mesma linha/área, cor do traçado pode mudar com o sinal do período.
- **Retorno por janela de tempo sempre exposto**, não escondido atrás de um clique (ideia do seletor 1M/YTD/1A/5A do Yahoo Finance) — já implementado em `frontend/js/mercados.js` (`montarRetornos`), reaproveitar o padrão para qualquer página nova que mostre série temporal.
- **Mapa de calor (treemap) sempre acompanhado de um indicador de amplitude** ("X de Y ativos em alta") — um treemap ponderado por tamanho pode parecer "tudo verde" por causa de poucas empresas grandes, mesmo com a maioria em queda. Ver `montarAmplitude` em `frontend/js/mercados.js`.
- **Faixa (range bar) com marcador de posição** para variação do dia/período, em vez de só texto "mín–máx" — padrão Yahoo/MarketWatch/Investing.com, já implementado (`montarFaixa`).
- **Verde/alta, vermelho/queda é universal — manter.** Não inventar paleta alternativa para isso. Cor de marca (`--azul`, `--ouro`) fica para identidade, nunca para codificar sinal positivo/negativo.
- **Selo de fonte sempre que o dado não for produzido/validado pelo DIEESE** (ex. cotação de mercado agregada) — rotular explicitamente, nunca deixar parecer indicador curado como os demais.
- **Essencial vs. supérfluo**: para o público deste projeto (pesquisador econômico/sindical, não trader), mostrar valor atual, variação do dia, variação acumulada por janela, e metodologia/fonte oficial. P/L, EV/EBITDA, book de ofertas, indicador técnico — fora de escopo, são ruído para este público.

### 2.4 Regras gerais de dataviz (ver `agents/bi-dataviz.md`)

- Escala de eixo nunca distorce a leitura (eixo Y truncado para exagerar uma variação pequena) sem anotação explícita.
- Unidade sempre visível perto do número — nunca um valor solto sem saber se é %, R$, índice.
- Gráfico nunca sugere causalidade a partir de correlação visual entre duas séries.
- Marcador de contexto (ex. transição de mandato presidencial em `D.GOVERNOS`, `frontend/js/dados.js`) é neutro: sem cor, nota ou ordenação que implique "melhor/pior" — só referência temporal.

## 3. Checklist antes de publicar

1. O texto evita os padrões da seção 1? (travessão, abertura genérica, fórmula de ênfase vazia)
2. Toda variação/percentual diz, explicitamente, em relação a quê é medida?
3. Todo `font-size`/espaçamento novo usa um token existente, não um valor avulso?
4. O layout evita os sinais de "site de IA" da seção 2.2?
5. Se é visualização de mercado/série temporal, segue as decisões já tomadas na seção 2.3 (linha não candlestick, retorno por janela exposto, treemap com amplitude, faixa com marcador)?
6. Unidade e fonte estão visíveis? Metodologia explica a base de comparação?
7. Alguma mudança de interface foi verificada visualmente (navegador real, ou — na ausência de navegador na sessão — publicada como Artifact de comparação para o responsável do projeto conferir) antes de declarar concluída?

## 4. O que este skill não resolve sozinho

Esta é uma reunião do que já foi decidido, não uma autorização para decidir sozinho o que ainda está em aberto. Paleta além de azul/vermelho/dourado, nova família tipográfica, ou um padrão de visualização sem precedente nos benchmarks já estudados continuam exigindo validação humana (ver "Quando solicitar validação humana" em `agents/designer-marca.md` e `agents/engenheiro-frontend.md`).
