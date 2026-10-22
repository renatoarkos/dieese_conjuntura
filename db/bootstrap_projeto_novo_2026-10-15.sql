-- Script de bootstrap do projeto Supabase NOVO (gdggtyioygsmehnvzxvc), gerado em
-- 2026-10-15 após o projeto anterior (mygmpquzzxbbcekertrd) travar por estouro de
-- disco (ver docs/08-decisoes-adr/INCIDENTE_2026-10-15_disco_cheio_supabase.md).
--
-- É a concatenação, na ordem certa, das migrações 0001, 0002, 0003, 0004, 0005,
-- 0006, 0008 e 0009 de db/migrations/ — a 0007 (microdado RAIS/CAGED) foi
-- deliberadamente OMITIDA por estar obsoleta desde o ADR 0008.
--
-- Este arquivo NÃO é uma migração numerada nova — é um script de recuperação de
-- uso único. As migrações continuam sendo a fonte de verdade do schema; se algo
-- aqui divergir delas no futuro, as migrações numeradas prevalecem.
--
-- Como aplicar: abrir https://supabase.com/dashboard/project/gdggtyioygsmehnvzxvc/sql/new,
-- colar este arquivo inteiro e rodar.

-- ============================================================
-- Migração 0001 — tabela de log de coletas RAW (ADR 0004)
-- ============================================================
create table if not exists raw_ingestoes (
    id bigint generated always as identity primary key,
    fonte text not null,
    indicador text,
    script text not null,
    coletado_em timestamptz not null default now(),
    storage_path text,
    tamanho_bytes bigint,
    sha256 text,
    status text not null check (status in ('sucesso', 'erro')),
    mensagem_erro text,
    metadata jsonb
);

create index if not exists idx_raw_ingestoes_fonte
    on raw_ingestoes (fonte, coletado_em desc);

alter table raw_ingestoes enable row level security;

-- ============================================================
-- Migração 0002 — camada CURATED mínima: catálogo + série temporal + perfis
-- ============================================================
create table if not exists indicadores (
    id text primary key,
    nome text not null,
    dimensao text not null check (dimensao in (
        'macroeconomia', 'monetario_credito', 'inflacao', 'mercado_trabalho', 'caged'
    )),
    unidade text not null,
    periodicidade text not null,
    fonte text not null,
    classificacao text not null check (classificacao in ('A', 'B', 'C', 'D', 'E')),
    metodologia_md text,
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

create policy "indicadores: leitura publica"
    on indicadores for select
    to anon, authenticated
    using (true);

create policy "indicadores_serie: leitura publica"
    on indicadores_serie for select
    to anon, authenticated
    using (true);

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

create table if not exists perfis (
    id uuid primary key references auth.users (id) on delete cascade,
    nome text not null,
    email text not null,
    ativo boolean not null default true,
    criado_em timestamptz not null default now()
);

alter table perfis enable row level security;

create policy "perfis: leitura do proprio perfil"
    on perfis for select
    to authenticated
    using (id = auth.uid());

-- ============================================================
-- Migração 0003 — catálogo blocos 2/3/4 (Monetário, Inflação, Mercado de Trabalho)
-- ============================================================
insert into indicadores (id, nome, dimensao, unidade, periodicidade, fonte, classificacao, metodologia_md, direcao_positiva, ordem_exibicao)
values
    ('selic', 'Taxa Selic', 'monetario_credito', '% a.a.', 'mensal/diário', 'BCB/SGS (séries 4189 até jul/2024, 432 a partir de ago/2024)', 'A',
     'Taxa básica de juros da economia, definida pelo Copom. Até julho de 2024 a série mostra a Selic acumulada no mês; a partir de agosto de 2024, a meta definida em cada reunião do Copom (publicada diariamente).', 'neutra', 10),
    ('juros_pj_veiculos', 'Juros — PJ, aquisição de veículos', 'monetario_credito', '% a.a.', 'mensal', 'BCB/SGS (série 20728)', 'A',
     'Taxa média de juros cobrada de pessoas jurídicas em financiamentos de veículos, recursos livres, no mês.', 'baixa', 20),
    ('juros_pj_cartao_rotativo', 'Juros — PJ, cartão de crédito rotativo', 'monetario_credito', '% a.a.', 'mensal', 'BCB/SGS (série 22019)', 'A',
     'Taxa média de juros do cartão de crédito rotativo para pessoas jurídicas, recursos livres, no mês.', 'baixa', 21),
    ('juros_pf_cheque_especial', 'Juros — PF, cheque especial', 'monetario_credito', '% a.a.', 'mensal', 'BCB/SGS (série 20741)', 'A',
     'Taxa média de juros do cheque especial para pessoas físicas, recursos livres, no mês.', 'baixa', 22),
    ('juros_pf_credito_pessoal', 'Juros — PF, crédito pessoal não consignado', 'monetario_credito', '% a.a.', 'mensal', 'BCB/SGS (série 20742)', 'A',
     'Taxa média de juros do crédito pessoal não consignado para pessoas físicas, recursos livres, no mês.', 'baixa', 23),
    ('comprometimento_renda_com_ajuste', 'Comprometimento de renda das famílias (com ajuste sazonal)', 'monetario_credito', '%', 'mensal', 'BCB/SGS (série 29034)', 'A',
     'Proporção da renda das famílias comprometida com o pagamento de dívidas no mês, com ajuste sazonal. Candidata à Tabela 27 citada pelo DIEESE — qual das 3 séries RNDBF corresponde exatamente não está confirmado (QF10).', 'baixa', 30),
    ('comprometimento_renda_sem_ajuste', 'Comprometimento de renda das famílias (sem ajuste sazonal)', 'monetario_credito', '%', 'mensal', 'BCB/SGS (série 29265)', 'A',
     'Mesma métrica da série com ajuste sazonal, sem a correção sazonal — valor bruto do mês. Candidata à Tabela 27 do DIEESE (QF10, não confirmado).', 'baixa', 31),
    ('endividamento_familias_acumulado_12m', 'Endividamento das famílias (acumulado 12 meses)', 'monetario_credito', '%', 'mensal', 'BCB/SGS (série 29037)', 'A',
     'Relação entre o saldo da dívida das famílias com o SFN e a renda acumulada nos últimos 12 meses. Candidata à Tabela 27 do DIEESE (QF10, não confirmado).', 'baixa', 32),
    ('saldo_credito_sfn_total', 'Saldo de crédito do SFN — total', 'monetario_credito', 'R$', 'mensal', 'BCB/SGS (série 20539)', 'A',
     'Saldo total da carteira de crédito do Sistema Financeiro Nacional no mês — pessoas físicas e jurídicas, recursos livres e direcionados somados.', 'neutra', 40),
    ('saldo_credito_sfn_pf', 'Saldo de crédito do SFN — pessoas físicas', 'monetario_credito', 'R$', 'mensal', 'BCB/SGS (série 20541)', 'A',
     'Saldo da carteira de crédito do SFN tomado por pessoas físicas no mês, todos os tipos de recurso.', 'neutra', 41),
    ('saldo_credito_sfn_pj', 'Saldo de crédito do SFN — pessoas jurídicas', 'monetario_credito', 'R$', 'mensal', 'BCB/SGS (série 20540)', 'A',
     'Saldo da carteira de crédito do SFN tomado por pessoas jurídicas no mês, todos os tipos de recurso.', 'neutra', 42),
    ('saldo_credito_sfn_recursos_livres', 'Saldo de crédito do SFN — recursos livres', 'monetario_credito', 'R$', 'mensal', 'BCB/SGS (série 20542)', 'A',
     'Saldo da carteira de crédito do SFN com recursos livres (taxas e condições definidas pelo próprio banco) no mês, PF e PJ somados.', 'neutra', 43),
    ('saldo_credito_sfn_recursos_direcionados', 'Saldo de crédito do SFN — recursos direcionados', 'monetario_credito', 'R$', 'mensal', 'BCB/SGS (série 20593)', 'A',
     'Saldo da carteira de crédito do SFN com recursos direcionados (habitação, rural etc., regras específicas) no mês, PF e PJ somados.', 'neutra', 44),
    ('saldo_credito_sfn_livres_pf', 'Saldo de crédito do SFN — recursos livres, pessoas físicas', 'monetario_credito', 'R$', 'mensal', 'BCB/SGS (série 20570)', 'A',
     'Saldo da carteira de crédito do SFN com recursos livres tomado especificamente por pessoas físicas no mês.', 'neutra', 45),
    ('ipca', 'IPCA — índice geral', 'inflacao', '% (variação mensal)', 'mensal', 'IBGE/SIDRA (tabela 7060)', 'A',
     'Variação de preços do mês em relação ao mês anterior, para famílias com renda de 1 a 40 salários mínimos — o índice oficial de inflação do Brasil, usado para a meta de inflação do Banco Central.', 'baixa', 50),
    ('inpc', 'INPC — índice geral', 'inflacao', '% (variação mensal)', 'mensal', 'IBGE/SIDRA (tabela 7063)', 'A',
     'Variação de preços do mês em relação ao mês anterior, para famílias assalariadas de renda mais baixa (1 a 5 salários mínimos) — usado, por exemplo, para reajuste de benefícios previdenciários.', 'baixa', 51),
    ('igpm', 'IGP-M', 'inflacao', '% (variação mensal)', 'mensal', 'FGV/IBRE, via réplica oficial no BCB/SGS (série 189)', 'A',
     'Variação do mês do Índice Geral de Preços — Mercado, calculado pela FGV, muito usado em reajustes de aluguel e contratos.', 'baixa', 52),
    ('combustivel_gasolina', 'Preço da gasolina', 'inflacao', 'R$/litro', 'semanal', 'ANP (microdados por posto revendedor)', 'B',
     'Preço médio nacional de venda da gasolina comum (não a aditivada), média simples entre todos os postos que reportaram preço no dia.', 'baixa', 60),
    ('combustivel_diesel', 'Preço do diesel', 'inflacao', 'R$/litro', 'semanal', 'ANP (microdados por posto revendedor)', 'B',
     'Preço médio nacional de venda do diesel S10 (o tipo hoje predominante no mercado brasileiro), média simples entre todos os postos que reportaram preço no dia.', 'baixa', 61),
    ('combustivel_glp', 'Preço do GLP (gás de cozinha)', 'inflacao', 'R$/botijão', 'semanal', 'ANP (microdados por posto revendedor)', 'B',
     'Preço médio nacional de venda do GLP, média simples entre todos os postos que reportaram preço no dia.', 'baixa', 62),
    ('taxa_desocupacao', 'Taxa de desocupação', 'mercado_trabalho', '%', 'trimestral', 'IBGE/SIDRA (tabela 4093, PNAD Contínua)', 'A',
     'Proporção de pessoas de 14 anos ou mais que estavam desocupadas (procurando trabalho ativamente) em relação à força de trabalho total, na semana de referência do trimestre — o indicador oficial de taxa de desemprego do Brasil.', 'baixa', 70),
    ('populacao_ocupada', 'População ocupada', 'mercado_trabalho', 'mil pessoas', 'trimestral', 'IBGE/SIDRA (tabela 4097, PNAD Contínua)', 'A',
     'Total de pessoas de 14 anos ou mais que estavam ocupadas na semana de referência do trimestre, somando todas as posições na ocupação (com carteira, sem carteira, conta própria, empregador etc.).', 'alta', 71),
    ('taxa_participacao', 'Taxa de participação na força de trabalho', 'mercado_trabalho', '%', 'trimestral', 'IBGE/SIDRA (tabela 6461, PNAD Contínua)', 'A',
     'Proporção de pessoas de 14 anos ou mais que estavam na força de trabalho (ocupadas ou procurando emprego) em relação ao total da população nessa faixa etária, na semana de referência do trimestre.', 'neutra', 72),
    ('rendimento_medio_real', 'Rendimento médio real habitual', 'mercado_trabalho', 'R$', 'trimestral', 'IBGE/SIDRA (tabela 5440, PNAD Contínua)', 'A',
     'Valor médio mensal do rendimento habitualmente recebido no trabalho principal, já em termos reais (deflacionado pelo IBGE), das pessoas ocupadas no trimestre. Pendência conhecida: o DIEESE pode aplicar um deflacionamento adicional próprio sobre este valor — não resolvido aqui (ver QF04).', 'alta', 73),
    ('taxa_sindicalizacao', 'Taxa de sindicalização', 'mercado_trabalho', '%', 'anual', 'IBGE/SIDRA (tabela 8676, PNAD Contínua — módulo anual, com hiato em 2020/2021)', 'A',
     'Proporção de pessoas ocupadas de 14 anos ou mais que são sindicalizadas, no ano. Série anual e descontínua (o suplemento não foi levantado em 2020 e 2021) — não é uma série trimestral comum.', 'alta', 74),
    ('desemprego_ilostat', 'Taxa de desemprego — comparação internacional', 'mercado_trabalho', '%', 'anual', 'ILOSTAT/OIT (estimativa harmonizada internacionalmente)', 'A',
     'Estimativa da OIT para a taxa de desemprego do Brasil, ajustada para ser comparável com outros países — não é a mesma série que a Taxa de desocupação do IBGE (que não tem esse ajuste); use esta apenas para comparação internacional.', 'baixa', 75)
on conflict (id) do nothing;

-- ============================================================
-- Migração 0004 — QF07/QF09/QF10 + enriquecimento de metodologia
-- ============================================================
insert into indicadores (id, nome, dimensao, unidade, periodicidade, fonte, classificacao, metodologia_md, direcao_positiva, ordem_exibicao)
values
    ('nfsp_setor_publico_consolidado', 'NFSP — Necessidade de Financiamento do Setor Público', 'monetario_credito', '% do PIB', 'mensal', 'BCB/SGS (série 5760)', 'A', 'NFSP sem desvalorização cambial, fluxo acumulado em 12 meses, juros nominais, setor público consolidado (Governo Federal, Banco Central, estados, municípios e empresas estatais), em % do PIB. Mede o quanto o setor público precisou se financiar para cobrir juros nominais da dívida, acumulado nos últimos 12 meses. QF07 resolvida em 2026-10-14: o código citado originalmente pelo material do DIEESE (5474) não é catalogado oficialmente pelo BCB; confirmado por leitura direta da planilha interna mais recente do DIEESE que a série correta é a SGS 5760 (o próprio DIEESE já migrou para ela), validado por comparação de 14 valores mensais reais.', 'baixa', 46),
    ('comprometimento_renda_sem_imovel', 'Comprometimento de renda das famílias (sem financiamento imobiliário)', 'monetario_credito', '%', 'mensal', 'BCB/SGS (série 29035)', 'A', 'Proporção da renda das famílias comprometida com dívidas no mês, dessazonalizado, excluindo financiamento imobiliário. Confirmado como parte da "Tabela 27" do DIEESE (QF10, resolvida 2026-10-14).', 'baixa', 33),
    ('endividamento_familias_sem_imovel', 'Endividamento das famílias (sem financiamento imobiliário)', 'monetario_credito', '%', 'mensal', 'BCB/SGS (série 29038)', 'A', 'Relação entre o saldo da dívida das famílias com o SFN, excluindo financiamento imobiliário, e a renda acumulada nos últimos 12 meses. Confirmado como parte da "Tabela 27" do DIEESE (QF10, resolvida 2026-10-14).', 'baixa', 34),
    ('salario_medio_real_admissao_caged', 'Salário médio real de admissão', 'caged', 'R$', 'mensal', 'Novo CAGED, MTE (microdados via FTP/PDET)', 'C', 'Salário médio real dos trabalhadores admitidos formalmente no mês. Calculado a partir dos microdados brutos do Novo CAGED (um registro por admissão/desligamento formal), não de uma tabela pronta. Exclui vínculos de modalidade intermitente e com salário fora da faixa de 0,3 a 150 salários mínimos vigentes no mês. Valores deflacionados pelo INPC (número-índice, IBGE/SIDRA 1736) a preços do mês mais recente disponível na série — mesma convenção da planilha interna do DIEESE ("sem ajustes": não corrige declarações recebidas fora do prazo, por isso os meses mais recentes podem ser revisados para cima em coletas futuras). Metodologia validada por simulação direta contra o microdado real de abr/2026: diferença de R$ 0,01 frente ao valor publicado pelo DIEESE. Cada ponto também carrega o recorte por sexo em metadata.por_sexo (mesmo padrão do recorte por UF do Limite Fiscal).', 'alta', 1),
    ('salario_medio_real_desligamento_caged', 'Salário médio real de desligamento', 'caged', 'R$', 'mensal', 'Novo CAGED, MTE (microdados via FTP/PDET)', 'C', 'Salário médio real dos trabalhadores desligados formalmente no mês. Calculado a partir dos microdados brutos do Novo CAGED (um registro por admissão/desligamento formal), não de uma tabela pronta. Exclui vínculos de modalidade intermitente e com salário fora da faixa de 0,3 a 150 salários mínimos vigentes no mês. Valores deflacionados pelo INPC (número-índice, IBGE/SIDRA 1736) a preços do mês mais recente disponível na série — mesma convenção da planilha interna do DIEESE ("sem ajustes": não corrige declarações recebidas fora do prazo, por isso os meses mais recentes podem ser revisados para cima em coletas futuras). Metodologia validada por simulação direta contra o microdado real de abr/2026: diferença de R$ 0,01 frente ao valor publicado pelo DIEESE. Cada ponto também carrega o recorte por sexo em metadata.por_sexo (mesmo padrão do recorte por UF do Limite Fiscal).', 'neutra', 2);

update indicadores set metodologia_md = 'Proporção da renda das famílias comprometida com o pagamento de dívidas no mês, dessazonalizado. Confirmado como parte da "Tabela 27" do DIEESE (QF10, resolvida 2026-10-14 por leitura direta da planilha interna do DIEESE — ver ADR 0005).' where id = 'comprometimento_renda_com_ajuste';
update indicadores set metodologia_md = 'Mesma métrica da série dessazonalizada, sem a correção sazonal — valor bruto do mês. Não faz parte da "Tabela 27" do DIEESE (QF10 resolvida 2026-10-14) — publicado como indicador complementar.' where id = 'comprometimento_renda_sem_ajuste';
update indicadores set metodologia_md = 'Relação entre o saldo da dívida das famílias com o SFN e a renda acumulada nos últimos 12 meses. Confirmado como parte da "Tabela 27" do DIEESE (QF10, resolvida 2026-10-14 por leitura direta da planilha interna do DIEESE — ver ADR 0005).' where id = 'endividamento_familias_acumulado_12m';
update indicadores set metodologia_md = 'Soma, em dólares (valor FOB — sem frete nem seguro), de tudo que o Brasil vendeu para o exterior no mês. Fonte: MDIC, Comex Stat (dados oficiais de comércio exterior, por NCM/país/UF — aqui publicado o agregado nacional). Periodicidade mensal, com defasagem de divulgação de poucos dias após o fechamento do mês. Sujeito a pequenas revisões entre divulgações, como todo dado de comércio exterior.' where id = 'balanca_exportacoes';
update indicadores set metodologia_md = 'Soma, em dólares (valor FOB — sem frete nem seguro), de tudo que o Brasil comprou do exterior no mês. Fonte: MDIC, Comex Stat. Periodicidade mensal, com defasagem de poucos dias após o fechamento do mês. Comparado a exportações (FOB), não inclui frete e seguro — por isso balança comercial (FOB-FOB) é diferente do saldo em transações correntes, que usa outra convenção (FOB-CIF).' where id = 'balanca_importacoes';
update indicadores set metodologia_md = 'Exportações menos importações do mês, ambas em valor FOB (sem frete/seguro). Positivo = superávit comercial; negativo = déficit comercial. Fonte: MDIC, Comex Stat. Mensal, com defasagem de poucos dias. Não confundir com o saldo em transações correntes do balanço de pagamentos, que usa convenção CIF nas importações.' where id = 'balanca_saldo';
update indicadores set metodologia_md = 'Índice que acompanha, em reais, o preço médio de uma cesta de commodities relevantes para a economia brasileira (produção, exportação e pressão sobre a inflação de insumos). Fonte: Banco Central do Brasil, Departamento Econômico (BCB/Depec), via SGS, série 27574. Base 100 = média de 2006. Mensal. Quanto maior, mais caras estão essas commodities no mês — é a soma ponderada dos 3 subíndices publicados ao lado (agropecuária, metal, energia).' where id = 'commodities_geral';
update indicadores set metodologia_md = 'Mesmo Índice de Commodities Brasil (IC-Br) do indicador geral, restrito à cesta de commodities agropecuárias (grãos, carnes, café etc.). Fonte: BCB/Depec, SGS, série 27575. Base 100 = média de 2006. Mensal.' where id = 'commodities_agropecuaria';
update indicadores set metodologia_md = 'Mesmo Índice de Commodities Brasil (IC-Br) do indicador geral, restrito à cesta de commodities metálicas (minério de ferro, cobre etc.). Fonte: BCB/Depec, SGS, série 27576. Base 100 = média de 2006. Mensal.' where id = 'commodities_metal';
update indicadores set metodologia_md = 'Mesmo Índice de Commodities Brasil (IC-Br) do indicador geral, restrito à cesta de commodities de energia (petróleo, gás etc.). Fonte: BCB/Depec, SGS, série 27577. Base 100 = média de 2006. Mensal.' where id = 'commodities_energia';
update indicadores set metodologia_md = 'Formação Bruta de Capital Fixo (FBCF) em relação ao PIB — quanto da riqueza produzida no trimestre foi reinvestido em máquinas, equipamentos e construção, em vez de consumido. Fonte: IBGE, Contas Nacionais Trimestrais, SIDRA Tabela 6727. Trimestral, série com ajuste sazonal. Sujeito a revisão entre divulgações — o mesmo trimestre pode mudar de valor em coletas futuras conforme o IBGE atualiza as Contas Nacionais; sempre prevalece a coleta mais recente.' where id = 'taxa_investimento';
update indicadores set metodologia_md = 'Variação da produção da indústria na soma dos últimos 12 meses, comparada aos 12 meses imediatamente anteriores — uma média móvel longa, que suaviza oscilações de curto prazo e reage mais devagar que uma comparação mês a mês. Fonte: IBGE, Pesquisa Industrial Mensal — Produção Física (PIM-PF), SIDRA Tabela 8888, variável 11604, categoria 129314 (Indústria geral). Mensal.' where id = 'pim_producao_industrial';
update indicadores set metodologia_md = 'Variação do volume do setor de serviços na soma dos últimos 12 meses, comparada aos 12 meses imediatamente anteriores — mesma lógica de média móvel longa do PIM-PF, por isso reage mais devagar que indicadores mês a mês. Fonte: IBGE, Pesquisa Mensal de Serviços (PMS), SIDRA Tabela 5906, variável 11626, categoria 56726 (Serviços totais). Mensal.' where id = 'pms_volume_servicos';
update indicadores set metodologia_md = 'Variação do volume de vendas do comércio varejista ampliado no mês, comparada ao mesmo mês do ano anterior — mede se as pessoas compraram mais ou menos, já descontado o efeito de preço (só quantidade). Fonte: IBGE, Pesquisa Mensal de Comércio (PMC), SIDRA Tabela 8881, variável 11709, categoria 56736 (índice de volume de vendas — não a receita nominal, que é outra categoria da mesma tabela). Mensal.' where id = 'pmc_volume_vendas';
update indicadores set metodologia_md = 'Quantos reais são necessários para comprar 1 dólar americano, na cotação de venda. O valor publicado é a média de todas as cotações do mês (não o fechamento de um dia específico). Fonte: Banco Central do Brasil, Sistema PTAX, via SGS (série candidata 3698/3694 — o material original do DIEESE cita "SIDRA/BCB Tabela 3694", mas a Tabela SIDRA 3694 não existe mais como câmbio; a fonte real é só BCB/SGS). Mensal.' where id = 'cambio_dolar';
update indicadores set metodologia_md = 'Total de crédito que o BNDES efetivamente liberou para financiamentos no mês — não é o que foi aprovado, é o que já foi pago às empresas. Fonte: BNDES, Portal de Dados Abertos (CKAN). Calculado a partir de microdado por operação individual (não uma tabela pronta de "desembolso total") — o dataset completo tem 3,76 milhões de registros desde 1995. Costuma ser divulgado com defasagem de ~6 meses em relação ao mês corrente.' where id = 'bndes_desembolsos';
update indicadores set metodologia_md = 'Variação do mês do Índice Geral de Preços — Mercado (IGP-M), calculado pela FGV/IBRE a partir de três componentes (IPA, IPC, INCC), muito usado em reajustes de aluguel e contratos. O portal da FGV não tem acesso público direto (exige assinatura) — coletado por rota alternativa: BCB/SGS, série 189, que replica oficialmente o valor do IGP-M. Mensal.' where id = 'igpm';
update indicadores set metodologia_md = 'Proporção de pessoas ocupadas de 14 anos ou mais que são sindicalizadas. Fonte: IBGE, PNAD Contínua anual (módulo "Características Adicionais do Mercado de Trabalho"), SIDRA Tabela 8676, variável 12535, categoria 47946 (Total). Série anual e descontínua — o módulo não foi levantado em 2020 e 2021 (hiato visível na série), não é uma série trimestral comum como os demais indicadores de mercado de trabalho.' where id = 'taxa_sindicalizacao';
update indicadores set metodologia_md = 'Variação de preços do mês em relação ao mês anterior, para famílias assalariadas de renda mais baixa (1 a 5 salários mínimos) — público-alvo diferente do IPCA. Usado, por exemplo, para reajuste de benefícios previdenciários. Fonte: IBGE, SNIPC, SIDRA Tabela 7063, variável 44 ("INPC — Variação mensal"). Mensal.' where id = 'inpc';
update indicadores set metodologia_md = 'Variação de preços do mês em relação ao mês anterior, para famílias com renda de 1 a 40 salários mínimos — o índice oficial de inflação do Brasil, usado para a meta de inflação do Banco Central. Fonte: IBGE, SNIPC, SIDRA Tabela 7060, variável 63 ("IPCA — Variação mensal"). Mensal. Pesos vigentes desde jan/2020, baseados na POF 2017-2018 (o material interno do DIEESE cita pesos jan/2012, que é uma tabela histórica distinta, 1419 — divergência de documentação, não de dado).' where id = 'ipca';
update indicadores set metodologia_md = 'Preço médio nacional de venda da gasolina comum (não a aditivada), média simples entre todos os postos que reportaram preço no período. Fonte: ANP, levantamento semanal "últimas 4 semanas", microdados por posto revendedor. Semanal, publicado como R$/litro.' where id = 'combustivel_gasolina';
update indicadores set metodologia_md = 'Preço médio nacional de venda do diesel S10 (o tipo hoje predominante no mercado brasileiro), média simples entre todos os postos que reportaram preço no período. Fonte: ANP, levantamento semanal "últimas 4 semanas", microdados por posto revendedor. Semanal, publicado como R$/litro.' where id = 'combustivel_diesel';
update indicadores set metodologia_md = 'Preço médio nacional de venda do GLP (gás de cozinha, botijão de 13kg), média simples entre todos os postos que reportaram preço no período. Fonte: ANP, levantamento semanal "últimas 4 semanas", microdados por posto revendedor. Semanal, publicado como R$/botijão.' where id = 'combustivel_glp';
update indicadores set metodologia_md = 'Proporção de pessoas de 14 anos ou mais que estavam desocupadas (procurando trabalho ativamente e disponíveis) em relação à força de trabalho total, na semana de referência do trimestre — o indicador oficial de taxa de desemprego do Brasil. Fonte: IBGE, PNAD Contínua trimestral, SIDRA Tabela 4093, variável 4099, categoria 6794 (Total — Brasil, sem recorte por sexo). Trimestral (trimestres móveis). Sujeita a erro amostral e a uma transição de desenho amostral do Censo 2010 para o Censo 2022, prevista para se completar em 2026 — risco de pequena descontinuidade técnica na série nesse período.' where id = 'taxa_desocupacao';
update indicadores set metodologia_md = 'Total de pessoas de 14 anos ou mais que estavam ocupadas na semana de referência do trimestre, somando todas as posições na ocupação (com carteira, sem carteira, conta própria, empregador etc.). Fonte: IBGE, PNAD Contínua trimestral, SIDRA Tabela 4097, variável 4090, categoria 96165 (Total). Trimestral, em mil pessoas.' where id = 'populacao_ocupada';
update indicadores set metodologia_md = 'Proporção de pessoas de 14 anos ou mais que estavam na força de trabalho (ocupadas ou procurando emprego ativamente) em relação ao total da população nessa faixa etária, na semana de referência do trimestre. Fonte: IBGE, PNAD Contínua trimestral, SIDRA Tabela 6461, variável 4096. Trimestral.' where id = 'taxa_participacao';
update indicadores set metodologia_md = 'Estimativa da Organização Internacional do Trabalho (OIT/ILO) para a taxa de desemprego do Brasil, harmonizada metodologicamente para ser comparável com a de outros países ("ILO Modelled Estimates") — não é a mesma série que a Taxa de desocupação do IBGE (que não passa por esse ajuste de comparabilidade internacional); use esta apenas para comparar o Brasil com outros países, não como substituto da série oficial brasileira. Fonte: ILOSTAT (OIT/ILO), API SDMX. Anual.' where id = 'desemprego_ilostat';
update indicadores set metodologia_md = 'Taxa média de juros do cheque especial para pessoas físicas, recursos livres (taxas e condições definidas pelo próprio banco, sem regra específica de governo). Fonte: Banco Central do Brasil, via SGS, série 20741 — código já citado célula a célula no material interno do DIEESE, confirmado por teste real da API. Mensal, % a.a.' where id = 'juros_pf_cheque_especial';
update indicadores set metodologia_md = 'Taxa média de juros do cartão de crédito rotativo para pessoas jurídicas, recursos livres. Fonte: Banco Central do Brasil, via SGS, série 22019 — código já citado célula a célula no material interno do DIEESE, confirmado por teste real da API. Mensal, % a.a.' where id = 'juros_pj_cartao_rotativo';
update indicadores set metodologia_md = 'Taxa média de juros cobrada de pessoas jurídicas em financiamentos de veículos, recursos livres. Fonte: Banco Central do Brasil, via SGS, série 20728 — código já citado célula a célula no material interno do DIEESE, confirmado por teste real da API. Mensal, % a.a.' where id = 'juros_pj_veiculos';
update indicadores set metodologia_md = 'Taxa média de juros do crédito pessoal não consignado para pessoas físicas, recursos livres (a modalidade mais cara de crédito pessoal, por não ter desconto em folha como garantia). Fonte: Banco Central do Brasil, via SGS, série 20742 — código já citado célula a célula no material interno do DIEESE, confirmado por teste real da API. Mensal, % a.a.' where id = 'juros_pf_credito_pessoal';
update indicadores set metodologia_md = 'Saldo total da carteira de crédito do Sistema Financeiro Nacional no mês — pessoas físicas e jurídicas, recursos livres e direcionados somados. Fonte: Banco Central do Brasil, via SGS, série 20539. Mensal, R$ milhões.' where id = 'saldo_credito_sfn_total';
update indicadores set metodologia_md = 'Saldo da carteira de crédito do SFN tomado por pessoas físicas no mês, todos os tipos de recurso (livres + direcionados) somados. Fonte: Banco Central do Brasil, via SGS, série 20541. Mensal, R$ milhões.' where id = 'saldo_credito_sfn_pf';
update indicadores set metodologia_md = 'Saldo da carteira de crédito do SFN tomado por pessoas jurídicas no mês, todos os tipos de recurso (livres + direcionados) somados. Fonte: Banco Central do Brasil, via SGS, série 20540. Mensal, R$ milhões.' where id = 'saldo_credito_sfn_pj';
update indicadores set metodologia_md = 'Saldo da carteira de crédito do SFN com recursos livres (taxas e condições definidas pelo próprio banco, sem regra específica de governo) no mês, pessoas físicas e jurídicas somadas. Fonte: Banco Central do Brasil, via SGS, série 20542. Mensal, R$ milhões.' where id = 'saldo_credito_sfn_recursos_livres';
update indicadores set metodologia_md = 'Saldo da carteira de crédito do SFN com recursos direcionados (habitação, rural etc., com regras específicas de taxa/prazo definidas por programas de governo) no mês, pessoas físicas e jurídicas somadas. Fonte: Banco Central do Brasil, via SGS, série 20593. Mensal, R$ milhões.' where id = 'saldo_credito_sfn_recursos_direcionados';
update indicadores set metodologia_md = 'Saldo da carteira de crédito do SFN com recursos livres tomado especificamente por pessoas físicas no mês. Fonte: Banco Central do Brasil, via SGS, série 20570. Mensal, R$ milhões.' where id = 'saldo_credito_sfn_livres_pf';
update indicadores set metodologia_md = 'Taxa básica de juros da economia brasileira, definida pelo Copom. A série é uma composição de duas fontes BCB/SGS ao longo do tempo, confirmada por comparação direta com 122 valores mensais da planilha interna do DIEESE: até julho de 2024, SGS 4189 (Selic acumulada no mês, taxa efetiva anualizada, base 252); a partir de agosto de 2024, SGS 432 (a meta Selic definida em cada reunião do Copom, valor de fim de mês). Mensal, % a.a.' where id = 'selic';

-- ============================================================
-- Migração 0005 — indicadores extraídos de PDF (ICT, Greves, Reajustes, Pisos)
-- ============================================================
insert into indicadores (id, nome, dimensao, unidade, periodicidade, fonte, classificacao, metodologia_md, direcao_positiva, ordem_exibicao)
values
    ('ict_dieese', 'Índice da Condição do Trabalho (ICT-DIEESE)', 'mercado_trabalho', 'índice (0-1)', 'trimestral', 'DIEESE, boletim público "Análise ICT-DIEESE" (dieese.org.br/analiseict)', 'B', 'Índice sintético (0 a 1, quanto mais próximo de 1 melhor) sobre condições de inserção no mercado de trabalho, elaboração própria do DIEESE a partir de microdados da PNAD Contínua (IBGE), combinando três dimensões: inserção ocupacional (formalização, previdência, tempo de permanência), desocupação (desocupação e desalento) e rendimento (valor por hora, concentração). Extraído automaticamente do texto do boletim trimestral público do DIEESE (PDF com camada de texto real, não é imagem escaneada) — não é a tabela bruta da PNAD.', 'alta', 76),
    ('greves_total_ano', 'Total de greves no ano', 'mercado_trabalho', 'nº de greves', 'anual', 'DIEESE, Sistema de Acompanhamento de Greves (SAG-DIEESE), boletim público "Balanço das Greves"', 'B', 'Número total de greves registradas no ano pelo SAG-DIEESE (Sistema de Acompanhamento de Greves), que reúne mobilizações de trabalhadores desde 1978 a partir de notícias em jornais e imprensa sindical. Boletim anual, publica o ano fechado anterior. Extraído do texto do boletim público "Balanço das Greves".', 'neutra', 77),
    ('greves_horas_paradas_ano', 'Horas paradas em greves no ano', 'mercado_trabalho', 'mil horas', 'anual', 'DIEESE, Sistema de Acompanhamento de Greves (SAG-DIEESE), boletim público "Balanço das Greves"', 'B', 'Total de horas paradas em greves no ano, somando todas as mobilizações registradas pelo SAG-DIEESE. Mesmo boletim e mesma fonte do indicador "Total de greves no ano".', 'neutra', 78),
    ('reajustes_acima_inpc_pct', 'Reajustes salariais acima do INPC', 'mercado_trabalho', '%', 'mensal', 'DIEESE, boletim público "De Olho nas Negociações" (dados do Mediador/MTE)', 'B', 'Percentual dos acordos e convenções coletivas de trabalho, inseridos no sistema Mediador (Ministério do Trabalho e Emprego), cujo reajuste salarial negociado na data-base mais recente ficou acima da variação do INPC no período. Quanto maior, mais negociações garantiram ganho real. Extraído do texto do boletim mensal público do DIEESE.', 'alta', 79),
    ('reajustes_abaixo_inpc_pct', 'Reajustes salariais abaixo do INPC', 'mercado_trabalho', '%', 'mensal', 'DIEESE, boletim público "De Olho nas Negociações" (dados do Mediador/MTE)', 'B', 'Percentual dos acordos e convenções coletivas de trabalho, inseridos no sistema Mediador (MTE), cujo reajuste salarial negociado na data-base mais recente ficou abaixo da variação do INPC no período — ou seja, representou perda real de poder de compra. Mesmo boletim do indicador "Reajustes salariais acima do INPC".', 'baixa', 80),
    ('piso_salarial_medio', 'Piso salarial médio negociado', 'mercado_trabalho', 'R$', 'mensal', 'DIEESE, boletim público "De Olho nas Negociações" (dados do Mediador/MTE)', 'B', 'Média simples dos pisos salariais negociados por categoria profissional, acumulado nas últimas 12 datas-bases (não o acumulado do ano corrente, que reinicia em janeiro). Metodologia do DIEESE considera um único valor por instrumento coletivo (o de menor valor quando há mais de um piso) e exclui estagiários e aprendizes. Extraído do texto do boletim mensal público.', 'alta', 81),
    ('piso_salarial_mediano', 'Piso salarial mediano negociado', 'mercado_trabalho', 'R$', 'mensal', 'DIEESE, boletim público "De Olho nas Negociações" (dados do Mediador/MTE)', 'B', 'Valor abaixo do qual se situam 50% dos pisos salariais negociados por categoria profissional, acumulado nas últimas 12 datas-bases. Mesma metodologia e mesmo boletim do "Piso salarial médio negociado" — a mediana é menos sensível a categorias com pisos muito altos ou muito baixos que a média.', 'alta', 82);

-- ============================================================
-- Migração 0006 — painéis customizados
-- ============================================================
create table if not exists paineis_customizados (
    id bigint generated always as identity primary key,
    usuario_id uuid not null references auth.users (id) on delete cascade,
    nome text not null default 'Meu painel',
    layout jsonb not null default '[]'::jsonb,
    criado_em timestamptz not null default now(),
    atualizado_em timestamptz not null default now()
);

create index if not exists idx_paineis_customizados_usuario
    on paineis_customizados (usuario_id);

alter table paineis_customizados enable row level security;

create policy "paineis_customizados: dono le"
    on paineis_customizados for select
    to authenticated
    using (usuario_id = auth.uid());

create policy "paineis_customizados: dono insere"
    on paineis_customizados for insert
    to authenticated
    with check (usuario_id = auth.uid());

create policy "paineis_customizados: dono atualiza"
    on paineis_customizados for update
    to authenticated
    using (usuario_id = auth.uid())
    with check (usuario_id = auth.uid());

create policy "paineis_customizados: dono apaga"
    on paineis_customizados for delete
    to authenticated
    using (usuario_id = auth.uid());

-- ============================================================
-- Migração 0008 — função de série recente (corrige corte de 1.000 linhas)
-- ============================================================
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

-- ============================================================
-- Migração 0009 — corrige rótulo de unidade do PMC
-- ============================================================
update indicadores
set unidade = '% (var. mês/mesmo mês ano anterior)'
where id = 'pmc_volume_vendas';
