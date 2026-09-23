# ADR 0004 — Supabase como armazenamento definitivo, escopo mínimo (RAW + Storage)

## Status

Aceito — 2026-09-23. **Implementação parcial**: migração `0001_criar_raw_ingestoes.sql` aplicada com sucesso no SQL Editor do Supabase pelo responsável do projeto (confirmado via API: `raw_ingestoes` existe e responde HTTP 200); bucket `raw` criado via Storage API (privado, sem acesso público). **Ainda pendente**: integração dos 26 scripts de coleta — nenhum script hoje envia arquivo ao Storage nem grava linha em `raw_ingestoes`, eles continuam gravando apenas em `data/raw/` local.

## Contexto

`ADR 0003` resolveu o agendamento dos motores (GitHub Actions), mas deixou explicitamente em aberto o armazenamento definitivo — os `data/raw/` gerados a cada execução ficam hoje em artifacts temporários do GitHub Actions (90 dias), insuficiente para série histórica.

O responsável pelo projeto criou um projeto Supabase e passou as credenciais (2026-09-23). Conectividade confirmada via REST (`/rest/v1/`): chaves `service_role`/`secret` respondem HTTP 200. Credenciais salvas em `.env` local, fora do Git.

Diante da pergunta sobre escopo (só RAW? STAGING/CURATED também? Storage para arquivos brutos?), o responsável escolheu explicitamente a opção mínima: **RAW + Storage**, deixando STAGING/CURATED para uma decisão de arquitetura futura — consistente com o padrão já estabelecido nos ADRs 0001-0003 (piloto mínimo e reversível, não a arquitetura definitiva de uma vez).

## Decisão

- **Escopo**: apenas a camada RAW (`CLAUDE.md`: "dados recebidos diretamente das fontes... não editar manualmente"). STAGING/CURATED/ANALYTICS ficam fora deste ADR.
- **Arquivos brutos → Supabase Storage**: cada execução de motor passa a poder enviar o arquivo bruto coletado (PDF, CSV, JSON, XLS, 7z...) para um bucket `raw`, organizado por fonte: `raw/<fonte>/<nome-do-arquivo>` — mesmo padrão de nomenclatura já usado em `data/raw/<fonte>/`. Isso substitui a dependência dos artifacts de 90 dias do GitHub Actions como armazenamento de longo prazo (os artifacts continuam existindo como cópia de curto prazo/debug, não como fonte de verdade).
- **Metadados de cada coleta → tabela Postgres `raw_ingestoes`**: uma tabela única e genérica (não uma tabela por fonte), registrando fonte, indicador, script executado, timestamp, caminho no Storage, tamanho, hash SHA-256, status (sucesso/erro) e um campo `metadata jsonb` livre para detalhes específicos da fonte (ex. código de série SGS, tabela SIDRA). Escolha de uma tabela genérica em vez de uma por fonte: menor superfície de schema para manter enquanto o piloto ainda está evoluindo (26 fontes e crescendo) — se algum caso de uso concreto exigir schema específico por fonte, isso é decisão de STAGING, não de RAW.
- **Segurança**: `raw_ingestoes` criada com Row Level Security habilitada e **nenhuma policy para `anon`/`authenticated`** — acesso apenas via `service_role` (que ignora RLS), usado só em processos de backend/ingestão. Nenhum dado sensível é esperado nesta tabela (são metadados de coleta, não dados de indicadores), mas o padrão de "negar por padrão" é mantido de qualquer forma.
- **Migração versionada**: schema escrito como SQL versionado em `db/migrations/0001_criar_raw_ingestoes.sql`, não aplicado automaticamente por nenhum script deste piloto — requer execução manual no SQL Editor do Supabase (ver `db/README.md`). As chaves de API (`anon`/`service_role`/`publishable`/`secret`) não permitem DDL via REST; sem uma string de conexão Postgres direta (não fornecida), a aplicação da migração é um passo manual do responsável do projeto.

## O que este ADR NÃO decide

- **STAGING/CURATED/ANALYTICS no Supabase** — fica para um ADR futuro, quando a arquitetura de transformação de dados for definida.
- **Migração automática do schema** — nenhum script deste piloto aplica `db/migrations/*.sql` automaticamente; é passo manual nesta fase.
- **Upload automático dos 26 scripts existentes para o Storage** — os scripts de coleta continuam, por enquanto, apenas gravando em `data/raw/` local. Conectar cada script ao Storage/`raw_ingestoes` é trabalho de implementação futuro, não incluído neste ADR.
- **Backend/API de aplicação** — Supabase como banco não implica automaticamente Supabase como backend da aplicação final; essa decisão segue em aberto.

## Consequências

- Uma vez aplicada a migração e implementado o envio ao Storage nos scripts, o projeto passa a ter série histórica permanente do RAW, em vez de depender de artifacts de 90 dias.
- A tabela `raw_ingestoes` funciona como log de auditoria mínimo (quando cada fonte foi coletada pela última vez, com sucesso ou erro) — útil mesmo antes de qualquer camada STAGING existir.
- Fica pendente decidir, num ADR futuro, o desenho de STAGING/CURATED — este ADR resolve apenas onde o dado bruto mora, não como ele vira indicador pronto.
