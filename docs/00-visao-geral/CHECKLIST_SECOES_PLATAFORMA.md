# Checklist de Seções da Plataforma DIEESE 360

## Natureza deste documento

Checklist de implementação derivado de `VISAO_DO_PRODUTO.md` (a visão original do produto, escrita no início do Discovery) e dos pedidos feitos ao longo da construção do frontend (ADR 0005 e conversas subsequentes). Serve para acompanhar, seção por seção, o que já existe na plataforma e o que falta construir — a pedido explícito do responsável do projeto (2026-10-14): "Preciso que realmente a gente construa uma estrutura e arquitetura para aparecer tudo o que precisamos e já pensamos para essa plataforma."

Cada item cita de qual seção de `VISAO_DO_PRODUTO.md` ele vem, quando aplicável, para rastreabilidade — nada aqui é inventado, é a visão original sendo convertida em itens concretos de interface.

## Como ler o status

- ✅ **Construído** — já existe e está publicado.
- 🟡 **Parcial** — existe uma versão inicial, mas não cobre tudo que a visão original pede.
- ⬜ **Não iniciado** — ainda não existe nenhuma versão.

---

## A. Página pública (`index.html`) — institucional

| Status | Seção | Origem | Observação |
|---|---|---|---|
| ✅ | Hero (nome, slogan, call-to-action) | — | |
| ✅ | Ticker de indicadores de atualização frequente | — | Reformulado em 2026-10-14 (cartões com selo de variação). |
| ✅ | "O que é o DIEESE 360" | — | Texto institucional sobre a plataforma em si. |
| ✅ | Dimensões (grade com as 5 áreas temáticas) | — | |
| ✅ | Amostra de indicadores (cartão giratório) | — | Revertido em 2026-10-14 para virar no lugar, não navegar. |
| ✅ | **Quem somos** | pedido 2026-10-14 | Implementado em 2026-10-14 com texto baseado na página institucional oficial `dieese.org.br/materialinstitucional/quemSomos.html` (fundação 1955, ~700 associados, 17 escritórios, 2 observatórios do trabalho) — fonte citada no próprio texto da seção. |
| ✅ | **O que é o Boletim de Conjuntura** | pedido 2026-10-14 | Implementado em 2026-10-14 com base na série pública `dieese.org.br/boletimdeconjuntura` (desde nov/2014, edição mais recente identificada nº 54/mai-2026). **Periodicidade não é mensal fixa** — sinalizado explicitamente no texto, não inventado. **Pendência**: não confirmado se este produto público é o mesmo que a "Apresentação de Conjuntura" interna (`ATR_Conjuntura_*.pptx`) usada como material de origem do catálogo — nomes/formatos distintos, tratados como possivelmente diferentes. |
| ⬜ | Calendário de divulgações oficiais | VISÃO §11 (DIVULGAÇÕES) | Acompanhar o calendário de divulgação de cada fonte (BCB, IBGE etc.) e indicar a próxima publicação esperada por indicador. Precisa de fonte oficial de calendário por instituição — não inventar datas. |

## B. Catálogo e exploração de dados

| Status | Seção | Origem | Observação |
|---|---|---|---|
| 🟡 | Catálogo Mestre de Indicadores | VISÃO §7 | Cada indicador já tem ficha completa (fonte, metodologia, periodicidade etc.) na própria página do indicador — falta uma **visão de catálogo consolidada**, pesquisável/filtrável, listando todos de uma vez (hoje só existe espalhado pela barra lateral). |
| 🟡 | Exploração multidimensional (filtro de período, vista gráfico/tabela/infográfico/mapa) | VISÃO §9 | Já existe **por indicador individual** (`indicador.html`). Falta o modo "explorador" de verdade: combinar/comparar múltiplos indicadores na mesma tela, tabela dinâmica cruzando dimensões. |
| ⬜ | Explorador de Dados (combinar séries, segmentações, tabelas dinâmicas) | VISÃO §9 | Feature grande — montar comparações livres entre indicadores de dimensões diferentes, não pré-definidas. |
| ⬜ | Dashboards editoriais | VISÃO §10 | Visões pré-montadas pela equipe técnica, com narrativa e indicadores selecionados para comunicar uma leitura específica — diferente do Explorador (livre) e dos cartões por dimensão (genéricos). |

## C. Análise e interpretação

| Status | Seção | Origem | Observação |
|---|---|---|---|
| ⬜ | Biblioteca de Relações Econômicas | VISÃO §8 | Investigação empírica de ~26 relações da literatura (Curva de Phillips, Lei de Okun, efeito Fisher, Kaldor-Verdoorn, Minsky etc. — lista completa em `VISAO_DO_PRODUTO.md`), ortodoxas e heterodoxas, **sem** declarar veredito sobre a teoria em si — só se há evidência compatível, para o período/dados analisados. Esforço grande, exige definição metodológica por relação. |
| ⬜ | Interpretação assistida | VISÃO §12 | Responder automaticamente "o que mudou", "quanto mudou", "como se compara historicamente", "houve mudança de tendência" — baseado em evidência calculada, nunca substituindo o analista. |

## D. Indicadores — cobertura de dados (não é "seção de página", mas é checklist igual)

| Status | Item | Observação |
|---|---|---|
| ✅ | 53 séries publicadas, 5 dimensões | Macroeconomia, Monetário/Crédito, Inflação, Mercado de Trabalho, CAGED — ver `ESTADO_DO_PROJETO.md`. |
| 🟡 | RAIS (expansão além do catálogo original) | Metodologia validada (região Norte, 2026-10-14) — processamento do Brasil completo em andamento. |
| ⬜ | QF04 (rendimento médio real — recorte exato) | E-mail enviado à equipe do DIEESE, aguardando resposta. |
| ⬜ | QF08 (PIB per capita — fonte BCB exata) | E-mail enviado à equipe do DIEESE, aguardando resposta. |
| ⬜ | Outras fontes de expansão (B3, CVM, Receita Federal, Banco Mundial, OCDE, FRED etc.) | Autorizado livremente pelo responsável (2026-10-14) — pesquisa exploratória já feita para parte delas em `docs/04-fontes/outras-instituicoes*.md`. |

---

## Como este checklist deve ser usado

Implementação item a item, não tudo de uma vez — cada linha vira sua própria seção/página quando for construída, e este documento é atualizado (status ✅) na mesma hora. Prioridade imediata combinada em 2026-10-14: **Quem somos** e **O que é o Boletim de Conjuntura** (seção A), por serem as mais simples de implementar (conteúdo institucional, sem decisão de arquitetura nova) e terem sido pedidas explicitamente.
