-- Migração 0003 — catálogo CURATED dos blocos 2 (Monetário/Crédito), 3 (Inflação)
-- e 4 (Mercado de Trabalho, parte) — ver docs/08-decisoes-adr/0005-...
--
-- Só adiciona linhas em `indicadores` (schema já existe desde a migração 0002) —
-- alimentadas por 14 scripts novos em pipelines/curated/. Nota de aplicação:
-- estas 26 linhas já foram inseridas via API REST (service_role) em 2026-10-14,
-- sem precisar do SQL Editor (é um INSERT, não um DDL) — este arquivo existe
-- para manter o catálogo reproduzível a partir do zero, documentado na ordem
-- certa junto com as demais migrações.
--
-- Textos de `metodologia_md` seguem o mesmo padrão de período/comparação
-- explícitos da migração 0002 (pedido do responsável do projeto, 2026-10-10).

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
