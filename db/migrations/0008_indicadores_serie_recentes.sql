-- Migração 0008 — corrige corte silencioso de 1.000 linhas (achado em
-- auditoria externa, 2026-10-15, item C08) na consulta em lote de séries
-- usada pela home (ticker, resumo do dia, carrossel por dimensão).
--
-- `indicadores_serie` tem 9.838 pontos no total (todos os indicadores,
-- todo o histórico). frontend/js/dados.js#carregarSeriesPorIndicadores
-- buscava "todos os pontos dos indicadores pedidos, ordenados por data
-- desc" e cortava para os últimos N por indicador NO CLIENTE — mas o
-- PostgREST já devolve só as 1.000 linhas mais recentes de TODA a
-- consulta antes disso, não 1.000 por indicador. Indicadores de
-- periodicidade mais espaçada (anual, quadrimestral — CAGED, RAIS,
-- ICT-DIEESE, greves, taxa de sindicalização) corriam risco real de ficar
-- de fora porque o ponto mais recente deles é mais antigo que o corte
-- global de 1.000 linhas.
--
-- Esta função devolve exatamente os N pontos mais recentes DE CADA
-- indicador pedido, via window function no banco — nunca depende de corte
-- de linhas do lado do cliente.

create or replace function indicadores_serie_recentes(p_indicador_ids text[], p_limite int default 24)
returns table (indicador_id text, data_referencia date, valor numeric, metadata jsonb)
language sql stable security invoker as $$
    select indicador_id, data_referencia, valor, metadata
    from (
        select s.indicador_id, s.data_referencia, s.valor, s.metadata,
               row_number() over (partition by s.indicador_id order by s.data_referencia desc) as posicao
        from indicadores_serie s
        where s.indicador_id = any(p_indicador_ids)
    ) numerado
    where posicao <= p_limite
    order by indicador_id, data_referencia asc;
$$;

grant execute on function indicadores_serie_recentes to anon, authenticated;
