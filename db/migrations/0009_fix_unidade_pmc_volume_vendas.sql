-- Migração 0009 — corrige rótulo de unidade de 'pmc_volume_vendas' (achado QA C06).
--
-- A migração 0002 cadastrou este indicador com unidade = '% (variação acum. 12m)',
-- mas `pipelines/curated/transformar_pmc_comercio_sidra.py` sempre usou (e
-- `metodologia_md`, atualizado na migração 0004, sempre descreveu)
-- D2C=11709 = "Variação mês/mesmo mês do ano anterior" — uma comparação
-- interanual mês a mês, NÃO uma variação acumulada em 12 meses (que seria
-- outro D2C da mesma tabela 8881, nunca usado por este pipeline). O rótulo
-- de unidade contradizia a série de fato publicada — confirmado lendo o
-- código do pipeline, não só o metadado. Corrige só o texto da unidade;
-- nenhum dado em indicadores_serie é alterado.

update indicadores
set unidade = '% (var. mês/mesmo mês ano anterior)'
where id = 'pmc_volume_vendas';
