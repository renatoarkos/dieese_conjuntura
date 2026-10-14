# ADR 0005 — DIEESE 360: frontend, camada CURATED mínima e autenticação

## Status

Aceito e em implementação — 2026-10-09, expandido em 2026-10-14. Plano detalhado em
conversa com o responsável do projeto (nome e visibilidade de dados confirmados
explicitamente). Primeiro ADR deste projeto a cobrir a camada de aplicação (os ADRs
0001-0004 cobriram só pipeline, agendamento e armazenamento RAW).

**Atualização 2026-10-14**: a camada CURATED foi estendida das 15 séries originais
(só `bloco_1_macroeconomia`) para **41 séries, cobrindo também `bloco_2_monetario_credito`,
`bloco_3_inflacao` e `bloco_4_mercado_trabalho`** — 14 novos scripts em
`pipelines/curated/`, migração `db/migrations/0003_catalogo_bloco_2_3_4.sql` (26 novas
linhas de catálogo via `INSERT` direto pela API REST, não SQL Editor — DDL continua
exigindo SQL Editor, mas DML passou a ser feito por API para evitar o mojibake de
acentuação já registrado no ADR 0004) e os 3 workflows de agendamento atualizados com os
passos de transformação correspondentes. As imagens de marca de `frontend/img-prompts.json`
também foram geradas e integradas (hero da home, ícone por dimensão, imagem lateral do
login). Verificado com Playwright contra o banco real: as 41 séries carregam e renderizam
corretamente, agrupadas por dimensão, na página interna (`painel.html`).

**Atualização 2026-10-14 (tarde)**: QF07, QF09 e QF10 resolvidas por comparação direta
com a planilha interna mais recente do DIEESE (ver `migrations/0004_...sql`) — a camada
CURATED chega a **46 séries**, agora cobrindo os 5 blocos (CAGED publicado pela primeira
vez: salário médio real de admissão/desligamento, com recorte por sexo em
`metadata.por_sexo`, calculado a partir do microdado bruto via `py7zr`, única dependência
de terceiros do projeto). A exportação em Excel (`indicador.html`) foi reescrita com
título, cores de marca e bloco de metodologia — troca de biblioteca de `xlsx.mini.min.js`
(não escreve estilo) para `xlsx-js-style`. 35 notas metodológicas do catálogo foram
enriquecidas com fonte/tabela/código exatos. QF04 e QF08 permanecem abertas — achados
novos registrados em `ESTADO_DO_PROJETO.md`.

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
único por indicador) e gravam pontos em `indicadores_serie`. Primeira rodada (2026-10-09)
cobriu os indicadores do `bloco_1_macroeconomia` com fonte estruturada (JSON/CSV) — 10 dos
12 scripts desse bloco. Segunda rodada (2026-10-14) estendeu a mesma `curated_supabase.py`
e o mesmo padrão de script aos blocos 2, 3 e 4 — 14 scripts novos, 41 séries publicadas no
total. Os indicadores de fonte só-PDF (ICT, Greves, Reajustes, Pisos salariais) e os que
ainda exigem parser dedicado (UCI/CNI, PIB Mundial/FMI, PEIC) continuam pendência
documentada, não dado inventado (ver "O que este ADR NÃO resolve").

### 4. Autenticação e visibilidade dos dados
Supabase Auth, contas individuais cadastradas por um administrador (mesmo padrão do
`painel_saude_mental`) — sem cadastro aberto. Decisão explícita do responsável do
projeto sobre visibilidade: **os números em si são públicos** (`indicadores` e
`indicadores_serie` com RLS de leitura liberada para `anon`) — são dados de fontes já
públicas (IBGE, BCB, SICONFI, MDIC, FMI, BNDES), não há nada sigiloso neles. O que fica
atrás do login é a **navegação completa da interface** por dimensão (a ferramenta de
trabalho interna), não o dado bruto. A home pública mostra só uma amostra curada.

## O que este ADR NÃO resolve

- **CAGED (bloco 5) — só 2 dos indicadores do bloco têm dado real** (salário médio de
  admissão/desligamento, com recorte por sexo). O saldo de admissões/desligamentos por
  grupamento de atividade (indicador 14 do Catálogo Mestre) continua sem transformação —
  a ingestão RAW já roda; falta só o script de agregação, mesmo padrão já validado em
  `transformar_salario_caged.py`.
- **Recortes de microdado além de sexo** — o responsável do projeto pediu também
  território, escolaridade e faixa de renda; adiados deliberadamente para não triplicar
  o tempo de reprocessamento dos 79 meses de CAGED numa só rodada — ver
  `ESTADO_DO_PROJETO.md`, entrada de 2026-10-14 (tarde).
- **Indicadores de fonte só-PDF** (ICT, Greves ×3, Reajustes, Pisos salariais) — exigem
  extração texto→número de boletins PDF do próprio DIEESE, engenharia ainda não
  construída neste projeto (diferente do parsing de JSON/CSV feito até aqui).
- **UCI/CNI e PEIC** — RAW é `.xlsx` binário, precisa de parser dedicado construído a
  partir da estrutura real da planilha, não adivinhado.
- **PIB Mundial/FMI** — a resposta SDMX 3.0 capturada no RAW, inspecionada diretamente,
  não contém observações numéricas utilizáveis, só metadados de estrutura; a URL de
  coleta provavelmente precisa de ajuste (ex. `dimensionAtObservation=AllDimensions`)
  antes de um transform poder ser escrito corretamente.
- **PIB per capita (QF08)** — a fonte real é "BCB-Depec" (confirmado pelo rótulo da
  própria planilha do DIEESE), não SIDRA; endpoint/fórmula exata do BCB não localizada
  nesta rodada — ver achado detalhado em `ESTADO_DO_PROJETO.md`.
- **Rendimento médio real (QF04)** — achado novo: a aba real do DIEESE é um recorte por
  Grande Região × categoria específica, não o total Brasil hoje publicado; precisa de
  confirmação do DIEESE antes de mudar o recorte do indicador.
- **Focus/Expectativas** — falta decidir a convenção de mês de referência antes de
  gravar a série.
- Nenhum desses itens ganhou valor inventado para preencher a lacuna.
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
