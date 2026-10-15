# Incidente 2026-10-15 — Disco cheio no Supabase e exposição de credencial em chat

## Status

Registrado — 2026-10-15. Não é um ADR de decisão arquitetural; é um registro de incidente
(causa raiz + auditoria de segurança associada), no mesmo diretório dos ADRs por ser
documentação permanente sobre uma credencial e um comportamento de infraestrutura que
afetam decisões futuras.

## O que aconteceu

Durante a carga em massa do microdado completo da RAIS (`pipelines/curated/carregar_rais_microdados.py`,
ver ADR 0006), uma instância do Claude Code nesta sessão precisou de acesso direto ao
Postgres do Supabase (`DATABASE_URL`) para inserir os registros de `rais_vinculos`. O
responsável do projeto colou a senha de conexão do banco diretamente na conversa do chat
(não um canal/cofre de segredos) para que ela pudesse ser salva em `.env` na raiz do
projeto. Pouco depois, a carga da região Norte da RAIS (~5,2 milhões de registros) excedeu
a cota de armazenamento do plano gratuito do Supabase e o banco travou.

## Causa raiz

- **Plano gratuito do Supabase = 0,5 GB de banco de dados.** Esse limite é do projeto
  inteiro (todas as tabelas), não por tabela.
- **A RAIS 2024 tem ~58 milhões de vínculos no Brasil inteiro** (ADR 0006); mesmo só a
  região Norte, com ~5,2 milhões de registros em `rais_vinculos` (19 colunas, a maioria
  numérica/texto curto), foi suficiente para estourar os 0,5 GB — microdado em grão de
  registro individual é incompatível, em volume, com o teto de armazenamento do plano
  gratuito.
- Carga direta via Postgres (`psycopg2`/`COPY`, ADR 0006 item 5) foi a escolha certa para
  throughput de inserção, mas não muda o fato de que o destino final (Postgres gerenciado
  do plano gratuito) tem teto de disco baixo demais para microdado completo multi-UF.
- Investigar e corrigir o travamento do banco em si **não é escopo desta tarefa** (aspecto
  de infraestrutura/disponibilidade, não de segurança) — mencionado aqui só como causa raiz
  do incidente, registrado para rastreabilidade.
- Consequência de arquitetura (relatada pelo responsável do projeto como decisão já
  tomada, não auditada independentemente nesta tarefa): o caso de uso que motivou obter o
  `DATABASE_URL` — carga de microdado direto no Postgres do Supabase — foi abandonado em
  favor de mover o microdado para **Parquet + DuckDB-WASM** fora do Supabase. Essa mudança
  de arquitetura, quando formalizada, deve gerar seu próprio ADR numerado (não é objeto
  deste registro de incidente).

## Auditoria de segurança realizada

Escopo: aspecto de credencial do incidente (exposição da senha do Postgres em chat),
conforme solicitado — não a causa do travamento do banco.

### 1. Histórico do Git para `.env`

```
git log --all --full-history -- .env
```

Nenhum resultado — `.env` **nunca foi commitado**, em nenhum commit, em nenhuma branch, em
todo o histórico do repositório. `.env` está listado em `.gitignore` (linhas 13-15: `.env`,
`.env.*`, com exceção explícita `!.env.example`). `git check-ignore -v .env` confirma que o
arquivo real na working tree está corretamente ignorado.

**Achado: nenhum.** Não há exposição via repositório Git — a exposição ocorreu só no canal
de chat, nunca chegou ao controle de versão.

### 2. `db/migrations/0007_microdados_rais_caged.sql` e `0008_indicadores_serie_recentes.sql`

- Todas as 9 funções RPC novas (`rais_por_uf`, `rais_por_cbo`, `rais_por_cnae`,
  `rais_por_sexo_faixa_etaria`, `caged_por_uf`, `caged_por_cbo`, `caged_por_cnae`,
  `caged_por_sexo` em 0007; `indicadores_serie_recentes` em 0008) são
  `language sql stable security invoker` — **nenhuma é `security definer`**. Correto: rodam
  com o privilégio de quem chama (RLS do chamador se aplica), não com o privilégio de quem
  criou a função.
- `rais_vinculos` e `caged_movimentacoes` têm RLS habilitada, com política de `select`
  restrita a `to authenticated` (`using (true)`) — **sem política para `anon`**, consistente
  com a decisão registrada no ADR 0006 ("nenhuma leitura pública do microdado", confirmada
  explicitamente com o responsável do projeto).
- `grant execute` de 0007 é só `to authenticated` — coerente com a RLS das tabelas de
  origem: não adianta nem faz sentido liberar a função para `anon` se a tabela por trás
  está fechada para esse papel.
- `grant execute` de 0008 (`indicadores_serie_recentes`) é `to anon, authenticated` — audita
  contra a RLS de `indicadores_serie`, que (migração 0002) já tem política
  `"indicadores_serie: leitura publica"` com `to anon, authenticated`. Consistente: essa
  tabela guarda dado agregado e já público nas fontes originais (ADR 0005), então liberar a
  função de leitura recente para `anon` não amplia o que já era público.

**Achado: nenhum problema.** As duas migrações preservam exatamente a regra de negócio já
decidida (microdado individual = só autenticado; indicador agregado = público), sem
`security definer` e sem grant além da RLS subjacente.

### 3. Busca por `DATABASE_URL` em `frontend/`

```
grep -r "DATABASE_URL" frontend/
```

Nenhum resultado. A busca em todo o repositório mostra `DATABASE_URL` só em:
`pipelines/curated/carregar_rais_microdados.py`, `pipelines/curated/carregar_caged_microdados.py`,
e documentação (`0006-microdados-rais-caged.md`,
`CHECKLIST_SESSAO_ANTIGRAVITY_2026-10-14.md`). Nenhuma referência em
`.github/workflows/` — a credencial não está (ainda) em GitHub Secrets, só local em `.env`.

**Achado: nenhum.** A credencial de acesso direto ao Postgres nunca aparece em código
client-side, só nos dois scripts de pipeline server-side que de fato a usam.

### 4. Revisão do próprio `.env`

O arquivo `.env` já traz comentário explícito junto a `DATABASE_URL` classificando-a como
"ainda mais sensível que as chaves [SUPABASE_SECRET_KEY/SERVICE_ROLE_KEY] acima: acesso
direto ao banco, não mediado por RLS de aplicação" — boa prática já presente antes desta
auditoria, mantida sem alteração.

## Avaliação de risco e recomendação sobre a senha

**Vetor de exposição real:** a senha foi digitada em texto puro numa conversa de chat
(não um cofre de segredos, não um canal com política de retenção/acesso equivalente a um
secret manager). Isso é uma exposição, mesmo não sendo um vazamento via repositório:
transcrições de chat podem ficar retidas em histórico/memória da ferramenta, podem ser
lidas por qualquer pessoa com acesso a essa conversa, e não há como "revogar" o que já foi
exibido em texto puro do mesmo jeito que se revoga um commit (que pelo menos pode ser
removido do histórico).

**Fatores que pesam a favor de trocar a senha agora:**

1. Exposição em canal não seguro é, por definição, uma credencial comprometida — a prática
   padrão de segurança é tratá-la como tal independentemente do canal ter sido "só" um chat
   e não um vazamento público.
2. O uso que justificou obter essa credencial (carga direta de microdado no Postgres) foi
   abandonado — não há mais um job ativo e recorrente dependendo exatamente desse valor, o
   que **reduz o custo da troca a praticamente zero**: não é preciso coordenar com nenhum
   pipeline agendado (`.github/workflows/`) nem com `frontend/`, já que nenhum dos dois
   referencia `DATABASE_URL` (achados 3 acima). Só os dois scripts de carga em
   `pipelines/curated/` e o `.env` local precisariam do valor novo, e ambos já estão em
   transição para fora do Postgres direto (Parquet + DuckDB-WASM).
3. O banco já está num estado instável (travado por estouro de cota) — trocar a senha agora,
   enquanto o uso de acesso direto está sendo descontinuado, é o momento de menor atrito
   para fazer essa rotação, comparado a fazê-la depois, com outro uso já dependente dela.

**Fatores que pesariam contra (nenhum encontrado como impeditivo):** não há commit exposto
para reescrever, não há CI dependente, não há consumidor client-side. Não existe um motivo
de custo/coordenação para adiar.

**Recomendação: sim, trocar a senha do Postgres agora.** É de baixo custo (nenhum
consumidor em produção depende da string atual fora dos dois scripts que estão sendo
descontinuados), e é a prática correta diante de qualquer credencial que foi exibida em
texto puro fora de um cofre de segredos — independentemente de o canal ter sido "só" uma
conversa e não um vazamento de repositório. Esta é uma recomendação, não uma ação
executada: conforme os limites deste papel (rotação de chave exige autorização explícita do
responsável do projeto, e não deve ser feita por este agente sem essa autorização, e o
procedimento pede explicitamente para não tentar conexão com o banco/API do Supabase nesta
tarefa), a troca em si fica para o responsável do projeto executar no painel do Supabase e
atualizar o `.env` local (sem versionar o novo valor).

## Nota — ADR 0008 já registrado em paralelo (achado desta auditoria, não produzido por ela)

No momento de redigir este registro, encontrei na working tree (ainda não commitado)
`docs/08-decisoes-adr/0008-microdados-parquet-storage-duckdb-wasm.md` e uma atualização de
status no ADR 0006, aparentemente produzidos por outro agente/instância nesta mesma sessão,
formalizando exatamente a mudança de arquitetura mencionada no contexto desta tarefa
(microdado sai do Postgres, vai para Parquet em Supabase Storage, consultado via
DuckDB-WASM no navegador). Não escrevi nem editei esses dois arquivos — são mencionados
aqui só porque confirmam, de forma independente, o abandono do uso que motivou a
`DATABASE_URL` (reforça a recomendação de troca de senha acima) e porque o próprio ADR 0008
deixa uma pendência de segurança em aberto que é diretamente do escopo deste papel:

> "Política de acesso do bucket do Storage: o ADR 0006 exigia acesso só autenticado ao
> microdado (...). Mover para Storage + DuckDB-WASM no navegador levanta a pergunta de como
> preservar essa restrição (URL assinada, política de bucket restrita a usuário logado,
> proxy de autenticação) — não decidido aqui, precisa ser resolvido antes da implementação."

**Sinalização do Engenheiro de Segurança:** esse ponto é crítico e deve ser bloqueante antes
de qualquer publicação de bucket. DuckDB-WASM roda no navegador e precisa buscar o arquivo
Parquet via HTTP — se o bucket for tornado público (caminho mais simples de implementar) sem
uma camada de autorização equivalente à RLS hoje aplicada em `rais_vinculos`/
`caged_movimentacoes` (restrita a `authenticated`, confirmada no ADR 0006), o microdado
individual passaria de "só autenticado" para "qualquer pessoa com a URL" — uma regressão de
controle de acesso, não uma decisão de negócio tomada. Recomendo que a implementação do ADR
0008 não prossiga sem essa política de acesso resolvida e revisada por este papel antes do
bucket ser criado/publicado.

## Dúvidas remanescentes

- Se/quando a migração para Parquet + DuckDB-WASM for formalizada, deve gerar um ADR
  numerado próprio descrevendo a nova arquitetura de armazenamento do microdado e
  provavelmente aposentando `DATABASE_URL` por completo (não só trocando o valor) — fora do
  escopo desta auditoria.
- Não foi auditado (fora de escopo explícito desta tarefa) o travamento do banco em si nem
  um plano de redimensionamento/upgrade do Supabase.

## Próximo passo recomendado

1. Responsável do projeto troca a senha do Postgres no painel do Supabase e atualiza
   `DATABASE_URL` no `.env` local (não versionar).
2. Quando a migração para Parquet + DuckDB-WASM for concretizada, registrar ADR numerado
   próprio e, nesse momento, avaliar remover `DATABASE_URL` do `.env` por completo caso
   nenhum script continue precisando de acesso direto ao Postgres.
