# ADR 0001 — Stack mínima para piloto técnico de ingestão

## Status

Aceito — escopo restrito a PIB Brasil (SIDRA 5932) e IPCA (SIDRA 7060, índice geral) — 2026-09-22.

## Contexto

- Fase do projeto: DISCOVERY. Nenhuma stack tecnológica definitiva foi aprovada (`docs/00-visao-geral/VISAO_DO_PRODUTO.md`, Seção 15).
- Discovery de Fontes — Lote Piloto 01 (`research/notas/DISCOVERY_FONTES_LOTE_PILOTO_01.md`) confirmou, com teste real de API, a fonte de 6 indicadores. Dois deles — **PIB Brasil** (SIDRA 5932) e **IPCA** (SIDRA 7060, índice geral e grupos oficiais) — estão sem nenhuma pendência de validação, ao contrário de Selic (série exata pendente, QF03), Câmbio (rótulo textual a confirmar) e Rendimento médio real (risco de dupla deflação, QF04).
- `docs/02-arquitetura/ROADMAP_DATALAKE_FASES.md` prevê uma Fase 4 — Piloto técnico controlado — que exige, no mínimo, escolher alguma tecnologia para executar código real de ingestão.
- O responsável pelo projeto autorizou explicitamente, em 2026-09-22, avançar com "ADR leve + piloto técnico mínimo", escopado aos 2 indicadores já prontos.

## Problema

Como ingerir dados reais de PIB e IPCA da API do IBGE/SIDRA para a camada RAW, de forma mínima e reversível, sem comprometer a arquitetura definitiva da plataforma (ainda não decidida)?

## Alternativas consideradas

1. Não escrever nenhum código ainda, permanecer apenas em especificação — descartada nesta rodada por decisão explícita do responsável pelo projeto.
2. Produzir um ADR completo avaliando toda a stack de ingestão antes de qualquer piloto — descartada por decisão explícita do responsável (preferiu o piloto mínimo primeiro).
3. **Piloto mínimo em Python, sem framework, sem orquestrador, sem banco de dados, gravando a resposta bruta da API em arquivo local** — escolhida.
4. Usar algum framework de orquestração (Airflow, Dagster, Prefect) já neste piloto — descartada por ser desproporcional ao escopo de 2 indicadores e por comprometer prematuramente uma decisão de orquestração que pertence à arquitetura definitiva.

## Decisão

Para este piloto, exclusivamente para os indicadores PIB Brasil (SIDRA 5932) e IPCA (SIDRA 7060, índice geral e grupos oficiais):

- **Linguagem**: Python 3, biblioteca padrão (`urllib`), sem dependência externa nova.
- **Execução**: script standalone por indicador, executado manualmente (sem agendamento automático nesta fase).
- **Destino dos dados**: `data/raw/`, já previsto e ignorado pelo Git em `.gitignore` (camada RAW não é versionada, padrão já estabelecido no projeto antes deste ADR).
- **Formato**: a resposta da API é gravada **sem transformação** (JSON bruto, como a fonte devolve), com nome de arquivo incluindo fonte, tabela e timestamp UTC da coleta — para preservar rastreabilidade (fonte → dado → data de coleta).
- **Sem banco de dados, sem orquestrador, sem framework de ingestão** nesta fase.

## Justificativa

- Mínimo necessário para validar, na prática, que os endpoints já confirmados na pesquisa de fonte (Lote Piloto 01) realmente produzem um dado utilizável ponta a ponta.
- Totalmente reversível: apagar `data/raw/` e os dois scripts não deixa rastro na arquitetura da plataforma.
- Não compromete nenhuma das decisões abertas em `VISAO_DO_PRODUTO.md`, Seção 15 (banco de dados, orquestrador, backend, frontend, cloud).
- Escopo deliberadamente pequeno (2 indicadores, sem pendência metodológica) — evita repetir, em escala, o erro de "escolher tecnologia antes de compreender os requisitos".

## Consequências

- Este piloto **não é** a arquitetura de ingestão definitiva da plataforma — será revisto ou substituído quando uma ADR de arquitetura definitiva for produzida (fase ARQUITETURA do projeto).
- Estabelece um padrão provisório de nomenclatura de arquivo RAW que pode ou não ser mantido.
- Qualquer expansão além destes 2 indicadores (Fase 5 do Roadmap) requer nova decisão explícita — este ADR não autoriza automaticamente a expansão a outros indicadores.
- Os demais 4 indicadores do Lote Piloto 01 (Câmbio, Selic, Desocupação, Rendimento médio real) permanecem fora do escopo deste piloto até suas pendências serem resolvidas ou até nova decisão de incluí-los.
- Os dados gravados em `data/raw/` não são versionados (já coberto por `.gitignore` preexistente) — a rastreabilidade da coleta fica no próprio nome do arquivo e no log de execução, não no histórico Git.
