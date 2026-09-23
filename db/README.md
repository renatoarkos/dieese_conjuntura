# db/

Schema versionado do banco de dados definitivo (Supabase/Postgres) — decisão registrada em
`docs/08-decisoes-adr/0004-supabase-raw-storage.md`.

**Escopo atual: apenas RAW.** Nenhuma tabela de STAGING/CURATED/ANALYTICS existe ainda —
fica para um ADR futuro.

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

## Supabase Storage

Bucket `raw`, organizado por fonte: `raw/<fonte>/<nome-do-arquivo>` — mesmo padrão de
`data/raw/<fonte>/` usado localmente pelos scripts de `pipelines/ingestao/`. O bucket em si
ainda não foi criado nem versionado aqui (criação de bucket também é feita pelo dashboard,
não por migração SQL) — ver ADR 0004 para o que falta.
