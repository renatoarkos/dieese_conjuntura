-- Migração 0002 — camada CURATED mínima: catálogo de indicadores + série temporal (ADR 0005)
--
-- Primeira transformação RAW→CURATED do projeto. Não guarda o dado bruto (isso
-- continua em raw_ingestoes/Storage) — guarda só o ponto final já pronto para
-- um cartão/gráfico consultar, alimentado por pipelines/curated/.

create table if not exists indicadores (
    id text primary key,                 -- slug estável, ex. 'pib_brasil'
    nome text not null,
    dimensao text not null check (dimensao in (
        'macroeconomia', 'monetario_credito', 'inflacao', 'mercado_trabalho', 'caged'
    )),
    unidade text not null,
    periodicidade text not null,
    fonte text not null,
    classificacao text not null check (classificacao in ('A', 'B', 'C', 'D', 'E')),
    metodologia_md text,
    -- Convenção de leitura (não um fato objetivo): se uma alta do valor costuma
    -- ser lida como melhora, piora, ou não tem leitura unívoca — usado só para
    -- colorir a seta de variação do cartão (CLAUDE.md: distinguir dado de
    -- interpretação — isto é interpretação, documentada como tal).
    direcao_positiva text not null default 'neutra' check (direcao_positiva in ('alta', 'baixa', 'neutra')),
    ordem_exibicao integer not null default 0
);

create table if not exists indicadores_serie (
    id bigint generated always as identity primary key,
    indicador_id text not null references indicadores (id) on delete cascade,
    data_referencia date not null,
    valor numeric not null,
    metadata jsonb,
    atualizado_em timestamptz not null default now(),
    unique (indicador_id, data_referencia)
);

create index if not exists idx_indicadores_serie_indicador
    on indicadores_serie (indicador_id, data_referencia desc);

alter table indicadores enable row level security;
alter table indicadores_serie enable row level security;

-- Leitura pública: são dados de fontes já públicas (IBGE/BCB/SICONFI/MDIC/FMI/BNDES),
-- nada sigiloso — decisão registrada no ADR 0005. O que fica atrás do login é a
-- navegação completa da interface (frontend/painel.html), não o dado em si. Escrita
-- continua restrita ao service_role (usado só pelos scripts de pipelines/curated/).
create policy "indicadores: leitura publica"
    on indicadores for select
    to anon, authenticated
    using (true);

create policy "indicadores_serie: leitura publica"
    on indicadores_serie for select
    to anon, authenticated
    using (true);

-- Catálogo dos 10 indicadores do bloco_1_macroeconomia já cobertos por
-- pipelines/curated/ nesta rodada (ver docs/08-decisoes-adr/0005-...).
-- UCI/CNI e PIB Mundial/FMI ficam de fora deliberadamente (ver o mesmo ADR) —
-- não inserir linha de catálogo para um indicador sem série real.
-- Os textos de `metodologia_md` abaixo descrevem sempre o período e a base de
-- comparação de forma explícita (ex. "no trimestre, comparado ao mesmo
-- trimestre do ano anterior") — pedido explícito do responsável do projeto
-- depois de ver a primeira versão (2026-10-10): o cartão não pode deixar
-- dúvida sobre a que período/base cada variação se refere.
insert into indicadores (id, nome, dimensao, unidade, periodicidade, fonte, classificacao, metodologia_md, direcao_positiva, ordem_exibicao)
values
    ('pib_brasil', 'PIB Brasil', 'macroeconomia', '% (variação)', 'trimestral', 'IBGE/SIDRA (tabela 5932)', 'A',
     'Mede o crescimento (ou queda) da economia brasileira. Compara o volume de bens e serviços produzidos no trimestre com o mesmo trimestre do ano anterior — por isso já descarta o efeito sazonal típico de cada época do ano (ex.: Natal, safra). Série com ajuste sazonal do IBGE.', 'alta', 10),
    ('cambio_dolar', 'Taxa de câmbio (dólar, venda)', 'macroeconomia', 'R$', 'mensal', 'BCB/SGS (série 3698)', 'A',
     'Quantos reais são necessários para comprar 1 dólar americano, na cotação de venda. Valor é a média de todas as cotações do mês — não é a cotação de um dia específico.', 'neutra', 20),
    ('balanca_exportacoes', 'Exportações (FOB)', 'macroeconomia', 'US$ FOB', 'mensal', 'MDIC/Comex Stat', 'B',
     'Soma, em dólares (valor FOB — sem contar frete e seguro), de tudo que o Brasil vendeu para o exterior no mês.', 'alta', 30),
    ('balanca_importacoes', 'Importações (FOB)', 'macroeconomia', 'US$ FOB', 'mensal', 'MDIC/Comex Stat', 'B',
     'Soma, em dólares (valor FOB), de tudo que o Brasil comprou do exterior no mês.', 'neutra', 31),
    ('balanca_saldo', 'Saldo da balança comercial', 'macroeconomia', 'US$ FOB', 'mensal', 'MDIC/Comex Stat', 'B',
     'Exportações menos importações do mês, em dólares (FOB). Positivo = superávit comercial; negativo = déficit comercial.', 'alta', 32),
    ('commodities_geral', 'Índice de Commodities Brasil — geral', 'macroeconomia', 'número-índice (2006=100)', 'mensal', 'BCB/Depec (SGS 27574)', 'A',
     'Índice que acompanha, em reais, o preço médio de uma cesta de commodities relevantes para a economia brasileira. Quanto maior, mais caras estão essas commodities no mês. Base 100 = média de 2006.', 'neutra', 40),
    ('commodities_agropecuaria', 'IC-Br — Agropecuária', 'macroeconomia', 'número-índice (2006=100)', 'mensal', 'BCB/Depec (SGS 27575)', 'A',
     'Mesmo índice do IC-Br geral, só com a cesta de commodities agropecuárias (grãos, carnes, café etc.). Base 100 = média de 2006.', 'neutra', 41),
    ('commodities_metal', 'IC-Br — Metal', 'macroeconomia', 'número-índice (2006=100)', 'mensal', 'BCB/Depec (SGS 27576)', 'A',
     'Mesmo índice do IC-Br geral, só com a cesta de commodities metálicas (minério de ferro, cobre etc.). Base 100 = média de 2006.', 'neutra', 42),
    ('commodities_energia', 'IC-Br — Energia', 'macroeconomia', 'número-índice (2006=100)', 'mensal', 'BCB/Depec (SGS 27577)', 'A',
     'Mesmo índice do IC-Br geral, só com a cesta de commodities de energia (petróleo, gás etc.). Base 100 = média de 2006.', 'neutra', 43),
    ('limite_fiscal_pessoal', 'Limite fiscal de pessoal (média das 27 UFs)', 'macroeconomia', '% da RCL ajustada', 'quadrimestral', 'SICONFI/Tesouro Nacional', 'A',
     'Quanto cada Estado gasta com a folha de pagamento do funcionalismo, em proporção à sua Receita Corrente Líquida. A Lei de Responsabilidade Fiscal limita o Poder Executivo estadual a 49% (prudencial: 46,55%; alerta: 44,1%). O número do cartão é a média simples das 27 UFs no quadrimestre mais recente — veja o mapa abaixo para o valor de cada estado.', 'baixa', 50),
    ('taxa_investimento', 'Taxa de investimento (FBCF/PIB)', 'macroeconomia', '%', 'trimestral', 'IBGE/SIDRA (tabela 6727)', 'A',
     'Quanto da riqueza produzida no país (PIB) do trimestre foi reinvestido em máquinas, equipamentos e construção, em vez de consumido.', 'alta', 60),
    ('bndes_desembolsos', 'Desembolsos do BNDES', 'macroeconomia', 'R$', 'mensal', 'BNDES/Dados Abertos', 'C',
     'Total de crédito que o BNDES efetivamente liberou para financiamentos no mês — não é o que foi aprovado, é o que já foi pago às empresas. Costuma ser divulgado com ~6 meses de defasagem.', 'alta', 70),
    ('pmc_volume_vendas', 'Volume de vendas — comércio (PMC)', 'macroeconomia', '% (variação acum. 12m)', 'mensal', 'IBGE/SIDRA (tabela 8881)', 'A',
     'Variação do volume de vendas do comércio varejista no mês, comparado ao mesmo mês do ano anterior — mede se as pessoas compraram mais ou menos (já descontado o efeito de preço, só quantidade).', 'alta', 80),
    ('pms_volume_servicos', 'Volume de serviços (PMS)', 'macroeconomia', '% (variação acum. 12m)', 'mensal', 'IBGE/SIDRA (tabela 5906)', 'A',
     'Variação do volume do setor de serviços na soma dos últimos 12 meses, comparada aos 12 meses imediatamente anteriores — uma média móvel longa, por isso reage mais devagar que indicadores mês a mês.', 'alta', 81),
    ('pim_producao_industrial', 'Produção industrial (PIM-PF)', 'macroeconomia', '% (variação acum. 12m)', 'mensal', 'IBGE/SIDRA (tabela 8888)', 'A',
     'Variação da produção da indústria na soma dos últimos 12 meses, comparada aos 12 meses imediatamente anteriores — mesma lógica de média móvel longa da PMS.', 'alta', 82)
on conflict (id) do nothing;

-- Perfis de usuário do painel interno (DIEESE 360) — mesmo padrão do
-- painel_saude_mental: 1 linha por pessoa com acesso, cadastrada por um
-- administrador (sem cadastro aberto). "ativo = false" revoga o acesso sem
-- apagar o histórico da conta.
create table if not exists perfis (
    id uuid primary key references auth.users (id) on delete cascade,
    nome text not null,
    email text not null,
    ativo boolean not null default true,
    criado_em timestamptz not null default now()
);

alter table perfis enable row level security;

-- Cada pessoa só lê o próprio perfil — suficiente para o exigirSessao() do
-- frontend conferir se a própria conta está ativa.
create policy "perfis: leitura do proprio perfil"
    on perfis for select
    to authenticated
    using (id = auth.uid());
