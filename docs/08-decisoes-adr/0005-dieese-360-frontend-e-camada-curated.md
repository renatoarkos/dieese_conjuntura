# ADR 0005 — DIEESE 360: frontend, camada CURATED mínima e autenticação

## Status

Aceito e em implementação — 2026-10-09. Plano detalhado em conversa com o responsável do
projeto (nome e visibilidade de dados confirmados explicitamente). Primeiro ADR deste
projeto a cobrir a camada de aplicação (os ADRs 0001-0004 cobriram só pipeline,
agendamento e armazenamento RAW).

## Contexto

O projeto tem 35 motores de coleta (`pipelines/ingestao/`) rodando em produção, mas nunca
teve interface — os dados existem só como RAW (CSV/JSON/PDF/microdados no Supabase
Storage), sem nenhuma camada pronta para um gráfico ou cartão consultar diretamente. O
responsável pelo projeto pediu a construção do frontend: uma plataforma de uso interno
para os técnicos elaborarem os boletins de conjuntura e darem subsídio em tempo real para
todo o DIEESE, organizada por dimensões de dados (os mesmos 5 blocos temáticos já usados
em `pipelines/ingestao/`), com página inicial pública e área interna por login.

## Decisão

### 1. Nome e identidade
A plataforma se chama **DIEESE 360**, slogan "A conjuntura brasileira vista de todos os
ângulos: dados, indicadores e análise em tempo real." — decidido com o responsável do
projeto.

### 2. Stack do frontend
HTML/CSS/JS puro (sem framework, sem bundler) + cliente `supabase-js` vendorizado +
deploy Vercel — **o mesmo padrão já usado e validado no projeto irmão
`painel_saude_mental/painel-web`**, que também é uma ferramenta interna do DIEESE. Reúso
direto de componentes já testados desse projeto:
- Tokens de marca (`--azul:#030086`, `--vermelho:#EC0000`, `--fonte-titulo:"Poppins"`,
  `--fonte-texto:"Open Sans"`, raio `10px`, sombra suave).
- Padrão de autenticação (`js/app.js`/`js/login.js`): Supabase Auth, `exigirSessao()`
  checando uma tabela `perfis` com `ativo boolean`, sessão encerrada por inatividade.
- Padrão de animação de entrada (`js/animacao-dash.js`): cartões surgindo em sequência,
  números contando do zero ao valor final, linhas SVG se desenhando — respeita
  `prefers-reduced-motion`.
- A ideia de cartão giratório (`js/cartao-giratorio.js`) é adaptada para uma versão mais
  simples *in-place* (sem o "voo ao centro" do modal), já que o caso de uso aqui é "virar
  o cartão para ver a explicação", não abrir um detalhe modal.

Não escolher um framework (React/Next/Vue) agora é consistente com o ADR 0001
(stack mínima) e evita introduzir uma segunda stack de frontend no ecossistema do DIEESE
sem necessidade demonstrada.

### 3. Camada CURATED mínima (pré-requisito para números reais)
Duas tabelas novas no mesmo projeto Supabase já em uso (`db/migrations/0002_criar_camada_curated.sql`):
- `indicadores` — catálogo: um indicador por linha (nome, dimensão, unidade,
  periodicidade, fonte, classificação A-E, metodologia resumida, ordem de exibição).
- `indicadores_serie` — série temporal: um ponto (indicador, data, valor) por linha, com
  `metadata jsonb` livre para detalhe específico (ex. quebra por UF).

Alimentadas por `pipelines/curated/` — scripts de transformação que leem o RAW mais
recente de cada indicador (via `raw_ingestoes`, localizado pelo campo `script`, que é
único por indicador) e gravam pontos em `indicadores_serie`. Primeira rodada cobre os
indicadores do `bloco_1_macroeconomia` com fonte estruturada (JSON/CSV) — 10 dos 12
scripts desse bloco. Os outros 2 ficam documentados como pendência, não como dado
inventado (ver "O que este ADR NÃO resolve").

### 4. Autenticação e visibilidade dos dados
Supabase Auth, contas individuais cadastradas por um administrador (mesmo padrão do
`painel_saude_mental`) — sem cadastro aberto. Decisão explícita do responsável do
projeto sobre visibilidade: **os números em si são públicos** (`indicadores` e
`indicadores_serie` com RLS de leitura liberada para `anon`) — são dados de fontes já
públicas (IBGE, BCB, SICONFI, MDIC, FMI, BNDES), não há nada sigiloso neles. O que fica
atrás do login é a **navegação completa da interface** por dimensão (a ferramenta de
trabalho interna), não o dado bruto. A home pública mostra só uma amostra curada.

## O que este ADR NÃO resolve

- **As outras 4 dimensões com dado real** (Monetário/Crédito, Inflação, Mercado de
  Trabalho, CAGED) — a interface já fica pronta para recebê-las; falta repetir o padrão
  de `pipelines/curated/` para cada bloco.
- **2 dos 12 indicadores do bloco_1_macroeconomia**: UCI/CNI (o RAW é um arquivo `.xlsx`
  binário — precisa de um parser dedicado, construído depois de inspecionar a estrutura
  real da planilha, não adivinhado) e PIB Mundial/FMI (a resposta SDMX 3.0 capturada no
  RAW mais recente, inspecionada diretamente nesta rodada, não contém observações
  numéricas utilizáveis — só metadados de estrutura; a URL de coleta provavelmente
  precisa de ajuste, ex. `dimensionAtObservation=AllDimensions`, antes de um transform
  poder ser escrito corretamente). Nenhum dos dois ganhou um valor inventado para
  preencher a lacuna.
- **Geração das imagens de marca** — `frontend/img-prompts.json` fica pronto (mesmo
  formato do `painel-web`), gerar/curar as imagens é um passo separado.
- **Deploy em produção** — construído e testado localmente; publicar no Vercel é ação
  externa visível, fica para autorização explícita separada (mesmo padrão já seguido
  com o `painel-web`).

## Consequências

- Primeira vez que o projeto tem uma transformação RAW→CURATED de verdade — o desenho
  de `indicadores`/`indicadores_serie` é deliberadamente simples (2 tabelas) para não
  antecipar decisões de ANALYTICS que ainda não foram tomadas; outras dimensões podem
  exigir ajuste de schema (ex. séries com quebra regional, como o Limite Fiscal por UF,
  guardadas por ora como `metadata.por_uf` dentro de um único indicador agregado).
- A migração 0002, como a 0001, precisa ser aplicada manualmente no SQL Editor do
  Supabase (mesma limitação registrada no ADR 0004 — as chaves de API não permitem DDL).
