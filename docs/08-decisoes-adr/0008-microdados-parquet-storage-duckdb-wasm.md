# ADR 0008 — Microdado de RAIS/CAGED fora do Postgres: Parquet + Supabase Storage + DuckDB-WASM

## Status

Aceito — 2026-10-15. **Revisa parcialmente o ADR 0006** (`docs/08-decisoes-adr/0006-microdados-rais-caged.md`),
que não é apagado nem reescrito — continua valendo como registro do que foi decidido e tentado
primeiro. Este ADR explica por que essa decisão precisou mudar e registra a nova decisão,
seguindo a regra do `CLAUDE.md`: "não substitua uma decisão arquitetural consolidada sem:
1. consultar o ADR anterior; 2. explicar por que precisa mudar; 3. registrar nova decisão."

## Contexto

O ADR 0006 decidiu guardar o microdado completo de RAIS e Novo CAGED (dezenas de milhões de
registros) em duas tabelas Postgres (`rais_vinculos`, `caged_movimentacoes`) no mesmo projeto
Supabase usado para o resto da plataforma, com funções RPC (`rais_por_uf`, `rais_por_cbo` etc.,
`db/migrations/0007_microdados_rais_caged.sql`) para cruzamento agregado no servidor.

**O que aconteceu na prática, após este ADR:** a carga real começou pela RAIS. A região Norte
(5,2 milhões de registros) carregou com sucesso em `rais_vinculos`. Ao iniciar a carga da
região seguinte, o banco estourou o limite de armazenamento do plano gratuito do Supabase —
**0,5 GB de Database Size**, cota muito menor do que o volume que a RAIS completa exigiria
(a RAIS 2024 inteira tem mais de 58 milhões de vínculos, só uma fração carregada no incidente).
O banco travou (crash por disco cheio), ficou com status "Unhealthy" por um período
significativo, e a API pública do site (que depende do mesmo projeto Supabase para servir os
indicadores de `indicadores`/`indicadores_serie`) ficou fora do ar.

## Por que a decisão do ADR 0006 está sendo revista

O ADR 0006 tratou "banco Supabase principal" como o destino do microdado sem confrontar a cota
real do plano gratuito contra o volume real da fonte — a suposição implícita era que o volume
caberia. O incidente mostrou que não cabe: **Database Size (0,5 GB) é uma cota muito mais
apertada do que Storage** no mesmo plano gratuito, e dezenas de milhões de registros de
microdado individual (RAIS e CAGED juntos) não cabem nela. Além disso, colocar o microdado na
mesma instância de banco que serve a API pública de indicadores criou uma dependência de
disponibilidade indesejada: um problema de volume no microdado derrubou também o que já estava
em produção. A decisão precisa mudar porque a premissa de capacidade que a sustentava não se
confirmou — não porque o objetivo original (cruzamento livre do microdado) deixou de ser
válido.

## Decisão

1. **O microdado completo sai do Postgres do Supabase.** Nenhuma tabela em grão de registro
   (`rais_vinculos`, `caged_movimentacoes`) continua recebendo carga. A camada
   `indicadores`/`indicadores_serie` (dado agregado, público) não é afetada — continua no
   Postgres normalmente.
2. **Os mesmos pipelines de transformação passam a gerar arquivos Parquet**, em vez de inserir
   linha a linha num banco Postgres: `pipelines/curated/carregar_rais_microdados.py` e
   `carregar_caged_microdados.py` precisam ser reescritos para esse novo formato de saída
   (reescrita ainda não feita — fica para quem implementar, fora do escopo deste ADR).
3. **Os arquivos Parquet ficam hospedados no Supabase Storage** (não no banco) — Storage tem
   cota separada e bem mais generosa que Database Size no mesmo plano, e é o recurso correto
   para arquivo binário grande, em vez de linha de banco relacional.
4. **Consulta direto do navegador via DuckDB-WASM** (SQL client-side de verdade, rodando no
   navegador do usuário) contra os arquivos Parquet via HTTP — sem servidor próprio novo,
   mantendo a arquitetura "site estático + Supabase" já decidida no ADR 0005
   (`docs/08-decisoes-adr/0005-dieese-360-frontend-e-camada-curated.md`), sem introduzir
   backend customizado.
5. **Layout de colunas**: ponto de partida é o já definido na migração 0007 (as colunas de
   `rais_vinculos`/`caged_movimentacoes`, já reduzidas das 62/28 colunas originais da fonte
   para as de valor analítico confirmado) — não um layout novo inventado agora. Ajustes finos
   ficam para a implementação.
6. **Tabelas/funções RPC da migração 0007 ficam OBSOLETAS.** `rais_vinculos`,
   `caged_movimentacoes` e as 7 funções RPC (`rais_por_uf`, `rais_por_cbo`, `rais_por_cnae`,
   `rais_por_sexo_faixa_etaria`, `caged_por_uf`, `caged_por_cbo`, `caged_por_cnae`,
   `caged_por_sexo`) não devem receber nova carga nem ser usadas por código novo. A migração
   0007 **não é apagada do histórico** — fica registrada como superada por este ADR. As
   tabelas/funções devem ser **removidas do banco numa limpeza futura** (migração de
   remoção, ainda não escrita) para liberar a cota de Database Size já escassa — o pouco que
   a região Norte carregou (5,2 milhões de registros) ainda ocupa espaço até essa limpeza
   acontecer.
7. **Frontend precisa ser reescrito**: `frontend/rais.html`/`caged.html` e
   `frontend/js/rais.js`/`caged.js`/`microdados.js` (hoje chamam `supabase.rpc(...)` contra as
   funções da migração 0007) vão precisar carregar DuckDB-WASM via CDN (ex. jsdelivr, **versão
   fixa, nunca "latest"**) e rodar SQL direto contra o Parquet via HTTP, em vez de chamar RPC.
   Reescrita ainda não feita — fora do escopo deste ADR.

## O que este ADR NÃO resolve (pendente de planejamento, não decidido aqui)

- **Política de acesso do bucket do Storage**: o ADR 0006 exigia acesso só autenticado ao
  microdado (nenhuma leitura pública, confirmado com o responsável). Mover para Storage +
  DuckDB-WASM no navegador levanta a pergunta de como preservar essa restrição (URL assinada,
  política de bucket restrita a usuário logado, proxy de autenticação) — **não decidido aqui**,
  precisa ser resolvido antes da implementação.
- **Particionamento exato dos arquivos Parquet** (por UF, por ano, por competência, arquivo
  único vs. múltiplos) — não decidido, fica para especificação técnica na implementação.
- **Biblioteca Python exata para escrever Parquet** nos pipelines (ex. `pyarrow`, `duckdb`,
  `pandas`+`pyarrow`) — dependência nova ainda não escolhida nem justificada; quem implementar
  deve avaliar e registrar a escolha (ADR leve ou nota de decisão, conforme o papel de
  Arquiteto de Software exige para dependência nova).
- **Cronograma da limpeza das tabelas/funções obsoletas** da migração 0007 — não definido
  aqui, só sinalizado como necessário.
- Nenhum detalhe de layout de coluna além do já existente na migração 0007 foi inventado.

## Consequências

- Pipelines de carga (`carregar_rais_microdados.py`, `carregar_caged_microdados.py`) e as
  páginas/scripts de frontend de RAIS/CAGED precisam de reescrita — trabalho de implementação
  real, não feito neste ADR.
- A migração 0007 permanece no histórico do repositório, mas suas tabelas/funções passam a
  status obsoleto; isso deve ficar visível para qualquer pessoa/IA que leia `db/migrations/`
  depois, para não reusá-las por engano.
- Dependência nova de biblioteca Parquet no pipeline Python (não escolhida ainda) e de
  DuckDB-WASM no frontend (via CDN, versão fixa).
- Reversibilidade: alta — Parquet em Storage é mais fácil de regenerar/mover do que linhas já
  inseridas em Postgres; a decisão de ADR 0006 sobre acesso restrito a autenticado precisa ser
  reafirmada ou ajustada explicitamente na implementação, não assumida como resolvida.
- Dúvida remanescente mais importante: como replicar "acesso só autenticado" com
  Parquet-em-Storage consultado direto do navegador — questão de segurança que deve ser
  resolvida antes de publicar qualquer bucket.

## Próximo passo recomendado

Especificar (fora deste ADR, antes de implementar): política de acesso do bucket,
particionamento do Parquet e escolha de biblioteca de escrita — depois reescrever os dois
pipelines de carga e os dois pares de página/script de frontend.
