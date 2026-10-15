-- Migração 0007 — microdado completo de RAIS (vínculos) e Novo CAGED
-- (movimentações), em grão de registro individual, para a página de
-- exploração estilo PDET/MTE pedida pelo responsável do projeto
-- (2026-10-14): "Os dados da RAIS eu preciso que fiquem completos na
-- plataforma com todos os microdados para eu gerar cruzar da forma que eu
-- bem entender" / "RAIS e o CAGED devem levar para uma nova página com um
-- painel online igual ao do MTE".
--
-- Diferente de indicadores/indicadores_serie (uma linha por período, dado já
-- agregado e público), estas duas tabelas guardam um registro por
-- vínculo/movimentação — por isso o acesso é só para usuário autenticado
-- (confirmado com o responsável do projeto), nunca público. Carregadas por
-- pipelines/curated/carregar_rais_microdados.py e carregar_caged_microdados.py
-- via conexão direta ao Postgres (não pela API REST — volume grande demais:
-- só a RAIS 2024 tem ~58 milhões de vínculos).
--
-- Só as colunas com valor analítico para cruzamento entraram aqui — a fonte
-- bruta tem mais colunas (confirmadas por leitura real do cabeçalho dos
-- arquivos, 2026-10-14): RAIS tem 62, CAGED tem 28. Colunas de nicho (bairros
-- de SP/Fortaleza/RJ, distritos de SP, região administrativa do DF, ano de
-- chegada ao Brasil, causas de afastamento) ficam de fora porque não servem
-- a nenhum filtro da página de exploração.

create table if not exists rais_vinculos (
    id bigint generated always as identity primary key,
    ano smallint not null,
    uf_trab text,
    municipio_trab_codigo text,
    cbo_2002_codigo text,
    cbo_2002_grande_grupo text,          -- 1º dígito do código CBO (hierarquia oficial), usado pra agrupar sem explodir em milhares de categorias
    cnae20_classe_codigo text,
    cnae20_divisao text,                  -- 2 primeiros dígitos do código CNAE 2.0 (divisão), mesma lógica do CBO
    sexo_codigo smallint,
    raca_cor_codigo smallint,
    faixa_etaria_codigo smallint,
    idade smallint,
    escolaridade_codigo smallint,
    faixa_rem_dez_sm_codigo smallint,
    vl_rem_dezembro_nom numeric,
    vl_rem_dezembro_real numeric,         -- deflacionado pelo IPCA (número-índice, ver indicadores_serie.ipca_numero_indice) — provisório até confirmação do deflator do DIEESE (QF04)
    vinculo_ativo_3112 boolean,
    tipo_vinculo_codigo smallint,
    natureza_juridica_codigo text,
    tamanho_estabelecimento_codigo smallint
);

create index if not exists idx_rais_vinculos_ano on rais_vinculos (ano);
create index if not exists idx_rais_vinculos_uf on rais_vinculos (uf_trab);
create index if not exists idx_rais_vinculos_cbo_gg on rais_vinculos (cbo_2002_grande_grupo);
create index if not exists idx_rais_vinculos_cnae_div on rais_vinculos (cnae20_divisao);
create index if not exists idx_rais_vinculos_sexo on rais_vinculos (sexo_codigo);
create index if not exists idx_rais_vinculos_ativo on rais_vinculos (vinculo_ativo_3112);

alter table rais_vinculos enable row level security;

create policy "rais_vinculos: leitura autenticada"
    on rais_vinculos for select
    to authenticated
    using (true);

create table if not exists caged_movimentacoes (
    id bigint generated always as identity primary key,
    competencia_mov text not null,        -- AAAAMM
    regiao text,
    uf text,
    municipio_codigo text,
    cnae20_secao text,
    cnae20_subclasse text,
    saldo_movimentacao smallint,          -- 1 = admissão, -1 = desligamento
    tipo_movimentacao_codigo text,
    cbo2002_codigo text,
    cbo2002_grande_grupo text,
    categoria_codigo smallint,
    grau_instrucao_codigo smallint,
    idade smallint,
    raca_cor_codigo smallint,
    sexo_codigo smallint,
    salario_mensal numeric,
    salario_mensal_real numeric,          -- deflacionado pelo IPCA, mesma ressalva de rais_vinculos.vl_rem_dezembro_real
    trabalho_intermitente boolean,
    trabalho_parcial boolean
);

create index if not exists idx_caged_mov_competencia on caged_movimentacoes (competencia_mov);
create index if not exists idx_caged_mov_uf on caged_movimentacoes (uf);
create index if not exists idx_caged_mov_cbo_gg on caged_movimentacoes (cbo2002_grande_grupo);
create index if not exists idx_caged_mov_cnae_secao on caged_movimentacoes (cnae20_secao);
create index if not exists idx_caged_mov_sexo on caged_movimentacoes (sexo_codigo);

alter table caged_movimentacoes enable row level security;

create policy "caged_movimentacoes: leitura autenticada"
    on caged_movimentacoes for select
    to authenticated
    using (true);

-- ---------------------------------------------------------------------
-- Funções de cruzamento (RPC): o navegador nunca baixa as linhas cruas,
-- só o resultado já agregado no banco — essencial com dezenas de milhões
-- de registros. Primeira etapa: cortes fixos (por UF, por grande grupo
-- CBO, por divisão CNAE, por sexo×faixa etária), cada um aceitando um
-- filtro opcional de UF para permitir alguma combinação (ex. "CBO dentro
-- de SP"). Cruzamento totalmente livre entre qualquer par de colunas fica
-- para uma evolução futura (registrado no ADR 0006).
-- ---------------------------------------------------------------------

create or replace function rais_por_uf(p_ano smallint default null)
returns table (uf text, vinculos bigint, remuneracao_media_nominal numeric, remuneracao_media_real numeric)
language sql stable security invoker as $$
    select uf_trab, count(*), round(avg(vl_rem_dezembro_nom), 2), round(avg(vl_rem_dezembro_real), 2)
    from rais_vinculos
    where vinculo_ativo_3112 and (p_ano is null or ano = p_ano)
    group by uf_trab
    order by vinculos desc;
$$;

create or replace function rais_por_cbo(p_ano smallint default null, p_uf text default null)
returns table (cbo_grande_grupo text, vinculos bigint, remuneracao_media_nominal numeric, remuneracao_media_real numeric)
language sql stable security invoker as $$
    select cbo_2002_grande_grupo, count(*), round(avg(vl_rem_dezembro_nom), 2), round(avg(vl_rem_dezembro_real), 2)
    from rais_vinculos
    where vinculo_ativo_3112 and (p_ano is null or ano = p_ano) and (p_uf is null or uf_trab = p_uf)
    group by cbo_2002_grande_grupo
    order by vinculos desc;
$$;

create or replace function rais_por_cnae(p_ano smallint default null, p_uf text default null)
returns table (cnae_divisao text, vinculos bigint, remuneracao_media_nominal numeric, remuneracao_media_real numeric)
language sql stable security invoker as $$
    select cnae20_divisao, count(*), round(avg(vl_rem_dezembro_nom), 2), round(avg(vl_rem_dezembro_real), 2)
    from rais_vinculos
    where vinculo_ativo_3112 and (p_ano is null or ano = p_ano) and (p_uf is null or uf_trab = p_uf)
    group by cnae20_divisao
    order by vinculos desc;
$$;

create or replace function rais_por_sexo_faixa_etaria(p_ano smallint default null, p_uf text default null)
returns table (sexo_codigo smallint, faixa_etaria_codigo smallint, vinculos bigint, remuneracao_media_real numeric)
language sql stable security invoker as $$
    select sexo_codigo, faixa_etaria_codigo, count(*), round(avg(vl_rem_dezembro_real), 2)
    from rais_vinculos
    where vinculo_ativo_3112 and (p_ano is null or ano = p_ano) and (p_uf is null or uf_trab = p_uf)
    group by sexo_codigo, faixa_etaria_codigo
    order by sexo_codigo, faixa_etaria_codigo;
$$;

create or replace function caged_por_uf(p_competencia text default null)
returns table (uf text, admissoes bigint, desligamentos bigint, saldo bigint, salario_medio_admissao_real numeric)
language sql stable security invoker as $$
    select uf,
           count(*) filter (where saldo_movimentacao = 1),
           count(*) filter (where saldo_movimentacao = -1),
           sum(saldo_movimentacao),
           round(avg(salario_mensal_real) filter (where saldo_movimentacao = 1), 2)
    from caged_movimentacoes
    where (p_competencia is null or competencia_mov = p_competencia)
    group by uf
    order by admissoes desc;
$$;

create or replace function caged_por_cbo(p_competencia text default null, p_uf text default null)
returns table (cbo_grande_grupo text, admissoes bigint, desligamentos bigint, saldo bigint, salario_medio_admissao_real numeric)
language sql stable security invoker as $$
    select cbo2002_grande_grupo,
           count(*) filter (where saldo_movimentacao = 1),
           count(*) filter (where saldo_movimentacao = -1),
           sum(saldo_movimentacao),
           round(avg(salario_mensal_real) filter (where saldo_movimentacao = 1), 2)
    from caged_movimentacoes
    where (p_competencia is null or competencia_mov = p_competencia) and (p_uf is null or uf = p_uf)
    group by cbo2002_grande_grupo
    order by admissoes desc;
$$;

create or replace function caged_por_cnae(p_competencia text default null, p_uf text default null)
returns table (cnae_secao text, admissoes bigint, desligamentos bigint, saldo bigint, salario_medio_admissao_real numeric)
language sql stable security invoker as $$
    select cnae20_secao,
           count(*) filter (where saldo_movimentacao = 1),
           count(*) filter (where saldo_movimentacao = -1),
           sum(saldo_movimentacao),
           round(avg(salario_mensal_real) filter (where saldo_movimentacao = 1), 2)
    from caged_movimentacoes
    where (p_competencia is null or competencia_mov = p_competencia) and (p_uf is null or uf = p_uf)
    group by cnae20_secao
    order by admissoes desc;
$$;

create or replace function caged_por_sexo(p_competencia text default null, p_uf text default null)
returns table (sexo_codigo smallint, admissoes bigint, desligamentos bigint, saldo bigint, salario_medio_admissao_real numeric)
language sql stable security invoker as $$
    select sexo_codigo,
           count(*) filter (where saldo_movimentacao = 1),
           count(*) filter (where saldo_movimentacao = -1),
           sum(saldo_movimentacao),
           round(avg(salario_mensal_real) filter (where saldo_movimentacao = 1), 2)
    from caged_movimentacoes
    where (p_competencia is null or competencia_mov = p_competencia) and (p_uf is null or uf = p_uf)
    group by sexo_codigo
    order by admissoes desc;
$$;

-- RLS das tabelas de origem já restringe a autenticado; grant explícito
-- para o papel usado pelo cliente logado poder chamar via RPC.
grant execute on function rais_por_uf, rais_por_cbo, rais_por_cnae, rais_por_sexo_faixa_etaria,
    caged_por_uf, caged_por_cbo, caged_por_cnae, caged_por_sexo
    to authenticated;
