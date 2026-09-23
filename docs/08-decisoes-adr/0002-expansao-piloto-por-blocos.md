# ADR 0002 — Expansão do piloto técnico por blocos

## Status

Aceito — 2026-09-22.

## Contexto

O ADR 0001 (`docs/08-decisoes-adr/0001-stack-minima-piloto-ingestao.md`) restringiu o piloto técnico a 2 indicadores (PIB Brasil, IPCA) e registrou explicitamente que "qualquer expansão além destes 2 indicadores requer nova decisão explícita — este ADR não autoriza automaticamente a expansão."

Nesta sessão (2026-09-22), o responsável pelo projeto solicitou explicitamente: "Vamos começar o processo de automatização de extração dos dados por blocos. Sempre dê prioridade a procurar e ver se existem apis." Isso constitui a decisão explícita exigida pelo ADR 0001 para autorizar expansão.

Em paralelo, dois novos lotes de Discovery de Fontes (Lote 02 — IBGE/SIDRA; Lote 03 — BCB) confirmaram, com chamada real de API, mais 6 indicadores adicionais aos 6 já confirmados no Lote Piloto 01.

## Decisão

Expandir o piloto técnico à **mesma stack mínima já decidida no ADR 0001** (Python 3 puro, sem framework/orquestrador/banco, RAW sem transformação, execução manual), organizando os scripts em **blocos temáticos** (`pipelines/ingestao/bloco_*/`), replicando a estrutura de blocos já usada em `docs/04-fontes/CHECKLIST_FONTES_DATALAKE.md`.

**Escopo desta expansão** — apenas indicadores com fonte **inequivocamente confirmada** (sem ambiguidade de série/tabela pendente de decisão humana):

| Bloco | Indicador | Fonte confirmada |
|---|---|---|
| 1 — Macroeconomia | PIB Brasil (já piloto) | SIDRA 5932 |
| 1 — Macroeconomia | Taxa de câmbio | BCB/SGS 3694 (anual) + 3698 (mensal) |
| 1 — Macroeconomia | Volume de vendas — comércio (PMC) | SIDRA 8881 — **apenas a parcela comércio**, não serviços/indústria (ver limitação abaixo) |
| 2 — Monetário e Crédito | Taxa Selic | BCB/SGS 4189 (histórico) + 432 (Meta Selic) — coletados como duas séries RAW separadas, sem mesclar |
| 2 — Monetário e Crédito | Taxas de juros por modalidade | BCB/SGS 20728, 22019, 20741, 20742 |
| 3 — Inflação | IPCA índice geral (já piloto) | SIDRA 7060 |
| 4 — Mercado de Trabalho | Taxa de desocupação | SIDRA 4093 |
| 4 — Mercado de Trabalho | População e posição na ocupação | SIDRA 4097 |
| 4 — Mercado de Trabalho | Taxa de participação na força de trabalho | SIDRA 6461 |

**Explicitamente FORA do escopo desta expansão** (ambiguidade real, não resolvida apenas com pesquisa de fonte):

- **NFSP**: o código citado pelo material do DIEESE (SGS 5474) responde à API mas não está no catálogo oficial de metadados do BCB. O candidato com nome oficial batendo exatamente (SGS 5760, "setor público consolidado") tem escopo potencialmente diferente de um candidato alternativo (SGS 5750, "Governo Federal e Banco Central"). Mudar de 5474 para 5760/5750 muda o significado do indicador — decisão que cabe à equipe do DIEESE, não a este projeto. Ver pergunta QF07 em `research/notas/DISCOVERY_FONTES_LOTE_PILOTO_01.md`.
- **PIB per capita**: a tabela citada pelo DIEESE (SIDRA 21777) não existe mais. Candidato de substituição (SIDRA 6784) cobre o tema mas não é confirmado como a intenção original do DIEESE. Ver QF08.
- **Volume de vendas — serviços (PMS) e indústria (PIM)**: apenas a parcela comércio (PMC, tabela 8881) foi confirmada nesta rodada. As tabelas de PMS e PIM não foram identificadas — o indicador do material do DIEESE agrega as três pesquisas sob um único rótulo, mas só uma foi confirmada.
- **Rendimento médio real (deflacionamento DIEESE)**: já registrado como fora de escopo desde o ADR 0001 (depende de Nota Técnica DIEESE — QF04).

## Justificativa

- Mantém a mesma stack mínima e reversível do ADR 0001 — não é uma nova decisão de tecnologia, é a aplicação do mesmo padrão já aceito a mais indicadores.
- Organização por blocos (solicitada explicitamente pelo usuário) espelha a estrutura já usada no checklist de fontes, facilitando rastreabilidade entre "o que foi pesquisado" e "o que foi automatizado".
- Exclui deliberadamente qualquer indicador com ambiguidade de fonte não resolvida — automatizar a coleta de uma fonte incerta violaria o princípio de `CLAUDE.md` de não inventar fonte/dado.

## Consequências

- `pipelines/ingestao/` passa a ser organizado em subpastas por bloco (`bloco_1_macroeconomia/`, `bloco_2_monetario_credito/`, `bloco_3_inflacao/`, `bloco_4_mercado_trabalho/`). Os 2 scripts do piloto original (PIB, IPCA) são movidos para os blocos correspondentes, sem alteração de conteúdo.
- A série Selic é coletada como **duas séries RAW separadas** (SGS 4189 completa e SGS 432 completa) — a lógica de qual trecho usar em qual período (nov/2015-jul/2024 → 4189; ago/2024+ → 432) é uma decisão de transformação que pertence à camada STAGING, não à RAW, e não está implementada neste piloto.
- Novas perguntas de validação humana registradas: QF07 (NFSP) e QF08 (PIB per capita) — não bloqueiam o restante do piloto.
- Este ADR não cobre automaticamente os Lotes 04 (CAGED/MTE) e 05 (institucionais diversas) do checklist, nem os indicadores com lacuna conhecida (Greves, Cesta Básica, ICT, Combustíveis) — cada expansão futura segue precisando de fonte confirmada primeiro.
