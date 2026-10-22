-- Migração 0010 — nova dimensão "mercados" (bolsas de valores e criptoativos)
--
-- Pedido do responsável do projeto (2026-10-15): "a parte de ações da bovespa
-- e outras bolsas mundiais, inclusive de criptoativos" deve virar uma
-- dimensão própria, com carrossel e quadro de dados próprio — separada do
-- ticker/"resumo do dia" principal, que continua só com indicadores
-- socioeconômicos (decisão já registrada antes nesta sessão: o carrossel
-- principal "não é uma lista de ativos financeiros").
--
-- Fonte: endpoint público de cotações da Yahoo Finance
-- (query1.finance.yahoo.com/v8/finance/chart/<ticker>), sem chave de API,
-- acessado via urllib puro — mesmo padrão "stdlib apenas" do resto do
-- projeto (ADR 0001), sem introduzir a dependência pip `yfinance`.
-- Classificação B: fonte agregadora de mercado, não estatística oficial
-- primária (mesmo critério já usado para MDIC/Comex Stat e ANP).

-- A constraint de dimensao foi criada inline na migração 0002 (nome
-- autogerado pelo Postgres). Em vez de assumir o nome exato, localiza e
-- derruba a constraint de CHECK existente na coluna antes de recriar — mais
-- robusto que hardcodar "indicadores_dimensao_check".
do $$
declare
    nome_constraint text;
begin
    select con.conname into nome_constraint
    from pg_constraint con
    join pg_class rel on rel.oid = con.conrelid
    where rel.relname = 'indicadores'
      and con.contype = 'c'
      and pg_get_constraintdef(con.oid) like '%dimensao%';

    if nome_constraint is not null then
        execute format('alter table indicadores drop constraint %I', nome_constraint);
    end if;
end $$;

alter table indicadores add constraint indicadores_dimensao_check
    check (dimensao in (
        'macroeconomia', 'monetario_credito', 'inflacao', 'mercado_trabalho', 'caged', 'mercados'
    ));

-- Catálogo inicial: 4 índices de referência, 2 criptoativos e 3 ações da B3
-- entre as mais negociadas/representativas (não é lista exaustiva de ativos —
-- mesmo princípio de "cortes mais representativos" já usado em outras
-- dimensões, evita parecer recomendação de investimento).
insert into indicadores (id, nome, dimensao, unidade, periodicidade, fonte, classificacao, metodologia_md, direcao_positiva, ordem_exibicao)
values
    ('ibovespa', 'Ibovespa', 'mercados', 'pontos', 'diário (fechamento)', 'Yahoo Finance (ticker ^BVSP)', 'B',
     'Valor de fechamento do Índice Bovespa (^BVSP), o principal indicador de desempenho médio das ações negociadas na B3. Ponto coletado é o fechamento do pregão mais recente disponível, não uma cotação intradiária em tempo real.', 'alta', 10),
    ('sp500', 'S&P 500', 'mercados', 'pontos', 'diário (fechamento)', 'Yahoo Finance (ticker ^GSPC)', 'B',
     'Valor de fechamento do índice S&P 500, que reúne as 500 maiores empresas listadas em bolsas dos Estados Unidos por valor de mercado. Fechamento do pregão mais recente, não cotação em tempo real.', 'alta', 11),
    ('nasdaq', 'Nasdaq Composite', 'mercados', 'pontos', 'diário (fechamento)', 'Yahoo Finance (ticker ^IXIC)', 'B',
     'Valor de fechamento do índice Nasdaq Composite, que acompanha todas as ações ordinárias listadas na bolsa Nasdaq, com peso relevante de empresas de tecnologia. Fechamento do pregão mais recente.', 'alta', 12),
    ('dow_jones', 'Dow Jones', 'mercados', 'pontos', 'diário (fechamento)', 'Yahoo Finance (ticker ^DJI)', 'B',
     'Valor de fechamento do índice Dow Jones Industrial Average, média ponderada por preço de 30 grandes empresas industriais dos Estados Unidos. Fechamento do pregão mais recente.', 'alta', 13),
    ('bitcoin', 'Bitcoin', 'mercados', 'US$', 'diário', 'Yahoo Finance (ticker BTC-USD)', 'B',
     'Cotação do Bitcoin em dólares americanos, referência de preço agregada pela Yahoo Finance a partir de exchanges de criptoativos. Criptoativos negociam 24 horas por dia, 7 dias por semana, sem pregão fixo. O ponto coletado é o preço no momento da coleta diária deste indicador, não necessariamente um "fechamento" no sentido de bolsa tradicional.', 'alta', 20),
    ('ethereum', 'Ethereum', 'mercados', 'US$', 'diário', 'Yahoo Finance (ticker ETH-USD)', 'B',
     'Cotação do Ethereum em dólares americanos, mesma fonte e mesma ressalva de coleta contínua (24/7) do indicador Bitcoin.', 'alta', 21),
    ('petr4', 'Petrobras (PETR4)', 'mercados', 'R$', 'diário (fechamento)', 'Yahoo Finance (ticker PETR4.SA)', 'B',
     'Preço de fechamento da ação preferencial da Petrobras (PETR4) na B3. Fechamento do pregão mais recente, não cotação em tempo real. Citado aqui como referência de mercado, não como recomendação de investimento.', 'alta', 30),
    ('vale3', 'Vale (VALE3)', 'mercados', 'R$', 'diário (fechamento)', 'Yahoo Finance (ticker VALE3.SA)', 'B',
     'Preço de fechamento da ação ordinária da Vale (VALE3) na B3. Fechamento do pregão mais recente. Citado aqui como referência de mercado, não como recomendação de investimento.', 'alta', 31),
    ('itub4', 'Itaú Unibanco (ITUB4)', 'mercados', 'R$', 'diário (fechamento)', 'Yahoo Finance (ticker ITUB4.SA)', 'B',
     'Preço de fechamento da ação preferencial do Itaú Unibanco (ITUB4) na B3. Fechamento do pregão mais recente. Citado aqui como referência de mercado, não como recomendação de investimento.', 'alta', 32)
on conflict (id) do nothing;
