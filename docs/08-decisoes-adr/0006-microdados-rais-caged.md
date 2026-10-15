# ADR 0006 — Microdado completo de RAIS e Novo CAGED, cruzamento via RPC

## Status

Aceito e em implementação — 2026-10-14. **Parcialmente substituído em 2026-10-15 pelo
ADR 0008** (`docs/08-decisoes-adr/0008-microdados-parquet-storage-duckdb-wasm.md`): a carga em
Postgres estourou a cota de Database Size do plano gratuito do Supabase durante a execução real
(ver ADR 0008 para o incidente e a nova decisão — microdado passa para Parquet em Supabase
Storage, consultado via DuckDB-WASM no navegador). Este registro permanece como histórico da
decisão original e não deve ser apagado.

## Contexto

Até esta decisão, RAIS e Novo CAGED existiam na plataforma só como indicadores agregados
(2 pontos cada em `indicadores_serie`: estoque de vínculos ativos e rendimento médio de
dezembro para a RAIS; salário médio real de admissão e desligamento para o CAGED — ver
`pipelines/curated/transformar_rais_dieese.py` e `transformar_salario_caged.py`). A tabela
`indicadores_serie` tem `unique(indicador_id, data_referencia)` — uma linha por período,
estruturalmente incapaz de guardar um registro por vínculo/movimentação.

O responsável do projeto pediu, em sequência (2026-10-14): que a RAIS ficasse completa na
plataforma "com todos os microdados" para cruzamento livre; que RAIS e Novo CAGED tivessem
cada uma uma página de exploração "idêntica às plataformas online que temos no site do
MTE" (o painel do PDET). Confirmou explicitamente, quando perguntado:

- **Armazenamento**: banco Supabase principal (não um arquivo analítico separado).
- **Acesso**: só usuário autenticado (nenhuma leitura pública do microdado).
- **Deflator**: IPCA como padrão — por ser o índice mais usado em portais de dados
  públicos (IPEADATA, BCB, IBGE), não por ser confirmado como o deflator que o próprio
  DIEESE usa para rendimentos. Essa confirmação (QF04) segue em aberto, e-mail enviado à
  equipe do DIEESE sem resposta até esta data. Trocar o deflator no futuro exige só
  reprocessar a carga, não mudar o schema.
- **Carga em massa**: via conexão direta ao Postgres (`DATABASE_URL`), não pela API REST —
  só a RAIS 2024 tem ~58 milhões de vínculos, volume incompatível com inserção em lotes
  via HTTP em tempo hábil.

Os nomes de coluna usados neste ADR e no schema foram confirmados por leitura real do
cabeçalho dos arquivos brutos (`data/raw/mte_rais/RAIS_VINC_PUB_NORTE_2024.7z`,
`data/raw/mte_caged/CAGEDMOV202607.7z`), não inferidos: RAIS tem 62 colunas (vírgula,
`latin-1`), Novo CAGED tem 28 colunas (`;`, `utf-8`).

## Decisão

1. **Duas tabelas novas em grão de registro** (`db/migrations/0007_microdados_rais_caged.sql`):
   `rais_vinculos` e `caged_movimentacoes`, cada linha é um vínculo/movimentação individual.
   Só as colunas com valor analítico para cruzamento entraram no schema (não as 62/28
   colunas originais) — ficam de fora colunas de nicho (bairros de SP/Fortaleza/RJ,
   distritos de SP, região administrativa do DF, ano de chegada ao Brasil, causas de
   afastamento) que não servem a nenhum filtro da página de exploração.
2. **RLS restrita a `authenticated`**, nenhuma política para `anon` — diferente do padrão
   de leitura pública usado em `indicadores`/`indicadores_serie` (que são dado já público
   nas fontes originais). O microdado individual, mesmo anonimizado pela fonte, fica
   atrás de login.
3. **Deflator**: número-índice do IPCA derivado por encadeamento multiplicativo a partir da
   série de variação mensal já publicada (`pipelines/curated/derivar_ipca_numero_indice.py`,
   novo indicador `ipca_numero_indice`), base 100 em jan/2020. Cada registro de
   RAIS/CAGED guarda valor nominal e valor real (deflacionado para o mês mais recente
   disponível do índice).
4. **Cruzamento via função RPC do Postgres**, não cruzamento livre no cliente: o
   navegador nunca baixa as linhas cruas (inviável com dezenas de milhões de registros).
   Nesta primeira etapa, funções fixas para os cortes mais pedidos (por UF, por grande
   grupo CBO, por divisão CNAE, por sexo×faixa etária/categoria), cada uma aceitando um
   filtro opcional de UF para alguma combinação. CBO é agrupado pelo "grande grupo"
   (1º dígito do código, hierarquia oficial) e CNAE pela "divisão" (2 primeiros dígitos
   da classe), não pelo código completo — evita resultado com milhares de categorias
   ilegíveis num gráfico.
5. **Carga via `psycopg2` + `COPY`/`execute_values`** (`pipelines/curated/carregar_rais_microdados.py`,
   `carregar_caged_microdados.py`), streaming arquivo por arquivo (nunca a base inteira
   descompactada em disco ao mesmo tempo) — mesmo padrão de streaming já usado nas
   transformações agregadas existentes.

## O que este ADR NÃO resolve

- Cruzamento livre entre qualquer par de dimensões (ex. CBO × escolaridade × UF ao mesmo
  tempo) — v1 cobre os cortes fixos listados acima; um cruzamento totalmente dinâmico
  exigiria uma função RPC parametrizada por lista arbitrária de colunas, fora de escopo
  nesta etapa.
- Histórico multi-ano completo — carrega-se inicialmente só a RAIS 2024 (já baixada) e o
  CAGED já baixado localmente (desde jan/2020, parcial); anos/meses adicionais entram
  depois, pelo mesmo pipeline.
- A confirmação do deflator real usado pelo DIEESE (QF04) — o IPCA aqui é uma escolha
  pragmática e documentada como provisória, não uma validação metodológica.
- Rótulos legíveis de código (ex. nome do município, nome da ocupação CBO, nome da CNAE) —
  as funções RPC devolvem códigos numéricos; tradução código→rótulo fica para a camada de
  frontend ou para uma tabela de referência futura.

## Consequências

- O projeto passa a ter, pela primeira vez, uma tabela em grão de registro individual —
  desvio deliberado do padrão `indicadores_serie` (uma linha por período), documentado
  aqui para não ser confundido com uma inconsistência de schema.
- Dependência nova: `psycopg2` (só para os dois scripts de carga em massa; o resto do
  projeto continua usando a API REST do Supabase, sem conexão direta ao Postgres).
- Credencial nova em `.env`: `DATABASE_URL` — mais sensível que a chave de serviço já
  usada (acesso direto ao banco, não mediado por RLS de aplicação, embora RLS continue
  valendo para qualquer acesso via API REST/cliente autenticado).
- Se/quando QF04 for respondida com um deflator diferente do IPCA, a correção é só
  reprocessar a carga (`carregar_rais_microdados.py`/`carregar_caged_microdados.py`) com
  uma nova série de número-índice — não exige mudança de schema nem das funções RPC.
