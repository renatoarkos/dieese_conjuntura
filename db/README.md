# db/

Schema versionado do banco de dados definitivo (Supabase/Postgres) — decisão registrada em
`docs/08-decisoes-adr/0004-supabase-raw-storage.md`.

**Escopo atual: RAW + uma camada CURATED mínima.** `raw_ingestoes` (RAW) e
`indicadores`/`indicadores_serie`/`perfis` (CURATED mínima, ver ADR 0005) existem.
STAGING completo/ANALYTICS seguem em aberto.

## Como aplicar uma migração

As chaves de API do Supabase (`anon`/`service_role`/`publishable`/`secret`) não permitem
executar DDL (`CREATE TABLE` etc.) via REST — é preciso rodar o SQL diretamente:

1. Abrir o projeto no [dashboard do Supabase](https://supabase.com/dashboard).
2. Ir em **SQL Editor**.
3. Colar o conteúdo do arquivo de migração (em ordem numérica, começando por
   `migrations/0001_criar_raw_ingestoes.sql`) e executar.

Nenhum script deste repositório aplica migrações automaticamente nesta fase.

## Migrações

| # | Arquivo | O que faz |
|---|---|---|
| 0001 | `migrations/0001_criar_raw_ingestoes.sql` | Cria `raw_ingestoes` — log de metadados de cada execução dos motores de coleta (fonte, script, timestamp, caminho no Storage, status). RLS habilitada, sem policy pública. |
| 0002 | `migrations/0002_criar_camada_curated.sql` | Cria `indicadores` (catálogo) e `indicadores_serie` (série temporal) — alimentadas por `pipelines/curated/`, leitura pública (RLS). Cria também `perfis` (contas do painel interno DIEESE 360, cadastradas por um administrador). Ver ADR 0005. |
| 0003 | `migrations/0003_catalogo_bloco_2_3_4.sql` | Só `insert` — 26 indicadores novos dos blocos Monetário/Crédito, Inflação e Mercado de Trabalho. Como é DML (não DDL), já foi aplicada via API REST (`service_role`) em 2026-10-14, sem precisar do SQL Editor — o arquivo existe para manter o catálogo reproduzível do zero. |
| 0004 | `migrations/0004_resolucao_qf07_qf09_qf10_e_metodologias.sql` | Só `insert`/`update` — resolve QF07 (NFSP, série 5760), QF10 (2 séries que faltavam da Tabela 27) e QF09 (salário médio CAGED, 2 indicadores novos na dimensão `caged`, primeiros dessa dimensão); enriquece a metodologia de 35 indicadores já existentes com fonte/tabela/código exatos. Aplicada via API REST (`service_role`) em 2026-10-14, mesmo motivo do 0003. |

## Supabase Storage

Bucket `raw`, organizado por fonte: `raw/<fonte>/<nome-do-arquivo>` — mesmo padrão de
`data/raw/<fonte>/` usado localmente pelos scripts de `pipelines/ingestao/`. O bucket em si
ainda não foi criado nem versionado aqui (criação de bucket também é feita pelo dashboard,
não por migração SQL) — ver ADR 0004 para o que falta.
