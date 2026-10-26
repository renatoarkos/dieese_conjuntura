-- Migração 0011 — catálogo amplo de ações da B3 (mapa de calor), ADR 0010 Fase 2
--
-- Deliberadamente SEPARADO de `indicadores`/`indicadores_serie`: essa dupla é
-- para indicadores curados, com metodologia rica, um por linha. Não cabe nela
-- um catálogo de ~300-700 ações da B3 atualizado em bloco todo dia — seria
-- forçar um formato pensado para outra coisa. Mesmo espírito já estabelecido
-- pelo ADR 0010: dado de mercado, não produção/validação do DIEESE.
--
-- Fonte: brapi.dev, endpoint /api/v2/tickers (plano gratuito), via
-- pipelines/ingestao/bloco_6_mercados/coleta_b3_brapi.py +
-- pipelines/curated/transformar_b3_brapi.py.

create table if not exists mercado_b3_ativos (
    ticker text primary key,
    nome text not null,
    setor text,
    subsetor text,
    tipo text not null,
    atualizado_em timestamptz not null default now()
);

create index if not exists idx_mercado_b3_ativos_setor
    on mercado_b3_ativos (setor);

create table if not exists mercado_b3_serie (
    id bigint generated always as identity primary key,
    ticker text not null references mercado_b3_ativos (ticker) on delete cascade,
    data_referencia date not null,
    preco numeric not null,
    variacao_pct numeric,
    volume bigint,
    market_cap numeric,
    unique (ticker, data_referencia)
);

create index if not exists idx_mercado_b3_serie_ticker
    on mercado_b3_serie (ticker, data_referencia desc);

alter table mercado_b3_ativos enable row level security;
alter table mercado_b3_serie enable row level security;

-- Leitura pública: mesmo padrão de indicadores/indicadores_serie — vai para a
-- página pública (mercados.html). Escrita só service_role (pipeline).
create policy "mercado_b3_ativos: leitura publica"
    on mercado_b3_ativos for select
    to anon, authenticated
    using (true);

create policy "mercado_b3_serie: leitura publica"
    on mercado_b3_serie for select
    to anon, authenticated
    using (true);
