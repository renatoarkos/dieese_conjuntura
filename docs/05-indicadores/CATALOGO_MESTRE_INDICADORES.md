# Catálogo Mestre de Indicadores

## Natureza deste documento

Catálogo Mestre de Indicadores da plataforma DIEESE Conjuntura, conforme definido em `docs/00-visao-geral/VISAO_DO_PRODUTO.md`, Seção 7 — a camada semântica central que conecta fontes, dados, indicadores e interpretações. Este documento é **distinto** de `docs/05-indicadores/INVENTARIO_INDICADORES_P1.md`, que é um levantamento preliminar restrito à leitura de três materiais internos do DIEESE (P1), sem pesquisa de fonte externa. As entradas aqui já passaram por confirmação direta na fonte oficial (Discovery de Fontes — Lote Piloto 01, ver `research/notas/DISCOVERY_FONTES_LOTE_PILOTO_01.md`).

Este documento está em construção progressiva — iniciou com 6 indicadores (Lote Piloto 01) e já cobre 33 (após Lotes 02-06 e investigação de lacunas conhecidas, 2026-09-22), crescendo conforme novos lotes de Discovery de Fontes forem executados.

Campos seguem `VISAO_DO_PRODUTO.md`, Seção 7: identificação, conceito, fonte, metodologia, periodicidade, unidade, abrangência, dimensões, histórico, transformações, atualização, relações com outros indicadores, relações teóricas, limitações, status de automação. Campos que dependem de outros papéis especializados (relações teóricas — Especialista em Metodologia Econômica; relevância conjuntural — Economista de Conjuntura) ainda não foram preenchidos neste lote e estão marcados como **[A PREENCHER]**.

---

## 1. PIB Brasil — variação do índice de volume trimestral

- **Identificação**: PIB Brasil, variação trimestral do índice de volume (Contas Nacionais Trimestrais).
- **Conceito**: variação real (volume, sem efeito-preço) do Produto Interno Bruto trimestral, em quatro recortes de comparação (trimestre/mesmo trimestre ano anterior; acumulado 4 trimestres; acumulado no ano; trimestre/trimestre anterior com ajuste sazonal).
- **Fonte**: IBGE, Sistema de Contas Nacionais Trimestrais. SIDRA Tabela 5932. Ficha completa em `docs/04-fontes/ibge-sidra.md`.
- **Metodologia**: Sistema de Contas Nacionais — Referência 2010 (SNA 2008); ajuste sazonal via X-13 ARIMA-SEATS.
- **Periodicidade**: Trimestral (divulgação ~60 dias após o fim do trimestre — não confirmado por fonte oficial lida integralmente).
- **Unidade**: % (variação).
- **Abrangência**: Brasil (nível nacional apenas — sem desagregação estadual nesta tabela).
- **Dimensões**: nenhuma além da série temporal (recorte territorial único: Brasil).
- **Histórico**: série encadeada desde 1996 (base 1995=100).
- **Transformações**: série encadeada com ajuste sazonal já aplicado pelo IBGE (X-13 ARIMA-SEATS).
- **Atualização**: automatizável via API SIDRA — ver classificação abaixo.
- **Relações com outros indicadores**: [A PREENCHER — Economista de Conjuntura / Especialista em Metodologia Econômica]. Candidatas identificadas no Discovery P1: PIB x Selic (Lei de Okun, Regra de Taylor — ver `research/notas/FLUXO_ATUAL_CONJUNTURA.md`, Seção 4.2).
- **Relações teóricas**: [A PREENCHER — Especialista em Metodologia Econômica].
- **Limitações**: defasagem de ~60 dias entre trimestre de referência e divulgação; dados preliminares sujeitos a revisão; série dessazonalizada recalculada a cada nova observação (valores de trimestres passados podem mudar).
- **Status de automação**: **A — API direta**, confirmada por teste real (`apisidra.ibge.gov.br`, 2026-09-22).

---

## 2. IPCA e subgrupos

- **Identificação**: IPCA — Índice Nacional de Preços ao Consumidor Amplo, índice geral e grupos/subgrupos/itens/subitens.
- **Conceito**: variação de preços ao consumidor para famílias com renda de 1 a 40 salários mínimos, áreas urbanas, 16 regiões de abrangência do SNIPC.
- **Fonte**: IBGE, Sistema Nacional de Índices de Preços ao Consumidor (SNIPC). SIDRA Tabela 7060 (índice geral e grupos oficiais). Ficha completa em `docs/04-fontes/ibge-sidra.md`.
- **Metodologia**: Nota Metodológica 01/2018 (SNIPC); Métodos de Cálculo do SNIPC, 6ª edição.
- **Periodicidade**: Mensal.
- **Unidade**: % (variação mensal, acumulada no ano, acumulada em 12 meses).
- **Abrangência**: Brasil + 16 áreas de abrangência do SNIPC.
- **Dimensões**: grupo/subgrupo/item/subitem de despesa; território (Brasil + 16 áreas).
- **Histórico**: IPCA como indicador existe desde dez/1979, mas a Tabela 7060 especificamente cobre apenas a partir de jan/2020 (períodos anteriores em tabelas históricas distintas: 1419, 2938, 58).
- **Transformações**: nenhuma além das já calculadas pelo IBGE (variação mensal/acumulada).
- **Atualização**: automatizável via API SIDRA — ver classificação abaixo.
- **Relações com outros indicadores**: [A PREENCHER]. Candidatas do Discovery P1: Curva de Phillips (com Taxa de desocupação, indicador 5 deste catálogo); Regra de Taylor (com Selic); pass-through cambial (com Taxa de câmbio).
- **Relações teóricas**: [A PREENCHER — Especialista em Metodologia Econômica].
- **Limitações**: cobre apenas famílias urbanas de 1-40 salários mínimos; defasagem crescente entre padrão de consumo da POF-base e padrão real corrente entre reponderações.
- **ALERTA — divergência a validar**: o material interno do DIEESE cita "pesos-base jan/2012" para esta tabela, mas a Tabela 7060 confirmadamente usa pesos da POF 2017-2018 (vigentes desde jan/2020) — a tabela de pesos jan/2012 é a 1419 (histórica). Além disso, os agregados especiais "Serviços" e "Monitorados", citados no material do DIEESE, **não foram localizados** na classificação da Tabela 7060. Ver detalhamento em `docs/04-fontes/ibge-sidra.md`.
- **Status de automação**: **A — API direta** para índice geral e grupos oficiais (confirmada por teste real). **D — investigação adicional** para os agregados "Serviços"/"Monitorados".

---

## 3. Taxa de câmbio (venda, média de período)

- **Identificação**: Taxa de câmbio — Livre — Dólar americano (venda) — Média de período.
- **Conceito**: valor médio (não o fechamento pontual) da cotação de venda do dólar americano no câmbio livre ao longo de um período.
- **Fonte**: Banco Central do Brasil (BCB), via SGS. **Não é SIDRA** — ver alerta abaixo. Ficha completa em `docs/04-fontes/bcb.md`.
- **Metodologia**: Sistema PTAX (Circular BCB 3.506/2010; Resolução BCB 45/2020).
- **Periodicidade**: mensal (série candidata SGS 3698) / anual (série candidata SGS 3694); série diária subjacente (SGS 1) atualizada diariamente.
- **Unidade**: R$/US$.
- **Abrangência**: Brasil (câmbio nacional).
- **Dimensões**: nenhuma — série temporal simples (compra/venda e fim-de-período/média-de-período são séries SGS distintas).
- **Histórico**: desde 1943 (série anual, SGS 3694) / desde 1953 (série mensal, SGS 3698, hipótese).
- **Transformações**: cálculo de média de período sobre as cotações diárias, já realizado pelo BCB.
- **Atualização**: automatizável via API BCB/SGS — ver classificação abaixo.
- **Relações com outros indicadores**: [A PREENCHER]. Candidata do Discovery P1: pass-through cambial (com IPCA).
- **Relações teóricas**: [A PREENCHER — Especialista em Metodologia Econômica].
- **Limitações**: rótulo textual oficial exato das séries 3694/3698 não confirmado diretamente (apenas por hipótese numérica/cruzamento); limite de 10 anos por consulta na API SGS.
- **ALERTA — divergência a validar**: o material interno do DIEESE cita "SIDRA/BCB Tabela 3694" como fonte. Confirmado que a **Tabela SIDRA 3694 não existe mais como tabela de câmbio** — é hoje uma tabela da pesquisa escolar PeNSE, sem qualquer relação com câmbio. A fonte real e única é BCB/SGS diretamente; o número "3694" citado pelo DIEESE provavelmente se refere ao código de série do SGS, não a uma tabela SIDRA. Ver detalhamento em `docs/04-fontes/bcb.md`.
- **Status de automação**: **A — API direta**, confirmada por teste real (`api.bcb.gov.br`, 2026-09-22). Ressalva: confirmar rótulo textual exato da série antes de uso em produção.

---

## 4. Taxa Selic

- **Identificação**: Taxa de juros — Selic. **Fonte confirmada como composta**: SGS 4189 (nov/2015-jul/2024) + SGS 432 (ago/2024 em diante).
- **Conceito**: taxa básica de juros da economia brasileira. Nov/2015-jul/2024: Selic acumulada no mês, anualizada base 252 (taxa efetiva). Ago/2024 em diante: Meta Selic definida pelo Copom (valor de fim de mês).
- **Fonte**: Banco Central do Brasil (BCB), via SGS. **Não é SIDRA** (achado do Lote Piloto 01). Ficha completa em `docs/04-fontes/bcb.md`.
- **Metodologia**: até jul/2024, taxa efetiva calculada pelo Departamento de Operações do Mercado Aberto (SGS 4189); a partir de ago/2024, meta definida pelo Copom a cada reunião (SGS 432). **Confirmado por comparação direta com os 122 valores mensais da aba T14 do material do DIEESE** (2026-09-22) — 100% de correspondência em 121 dos 122 meses testados (jan/2025 é exceção isolada, diferença de 0,01 p.p. de SGS 4189, provável arredondamento).
- **Periodicidade**: mensal, conforme uso do DIEESE (SGS 4189 é nativamente mensal; SGS 432 é diária, mas o DIEESE usa o valor de fim de mês).
- **Unidade**: % a.a.
- **Abrangência**: Brasil.
- **Dimensões**: nenhuma — série temporal simples.
- **Histórico**: SGS 432 desde 05/03/1999; SGS 11 desde 04/06/1986; SGS 4189/4390 desde agosto/1986.
- **Transformações**: nenhuma além das já calculadas pelo BCB.
- **Atualização**: automatizável via API BCB/SGS — ver classificação abaixo.
- **Relações com outros indicadores**: [A PREENCHER]. Candidatas do Discovery P1: Efeito Fisher/juros real (com IPCA — cálculo já presente no material do DIEESE); Regra de Taylor (com IPCA); PIB x Selic (justaposição já presente no material, sem teste estatístico).
- **Relações teóricas**: [A PREENCHER — Especialista em Metodologia Econômica].
- **Limitações**: a série é uma composição de duas fontes SGS diferentes ao longo do tempo — uma ingestão automatizada precisa replicar a regra de troca (4189 até jul/2024, 432 a partir de ago/2024), não assumir série única constante; limite de 10 anos por consulta na API.
- **Divergência resolvida**: o material interno do DIEESE cita "SIDRA e BCB" como fonte. Confirmado que o **SIDRA não hospeda nenhuma tabela de Selic** — fonte real é exclusivamente BCB/SGS. A identidade exata da série **foi resolvida por comparação direta** com os 122 valores mensais da aba T14 (ver acima) — não é mais uma pendência aberta.
- **Nova pergunta (QF03b, não bloqueante)**: por que a planilha do DIEESE mudou de SGS 4189 para SGS 432 em ago/2024? Não determinável apenas pelos dados — requer validação humana, mas não impede a automação (ambas as séries são classificação A).
- **Status de automação**: **A — API direta**, fonte exata confirmada para ambos os trechos da série.

---

## 5. Taxa de desocupação

- **Identificação**: Taxa de desocupação, Brasil e Unidades da Federação.
- **Conceito**: proporção de pessoas de 14+ anos desocupadas (procurando trabalho ativamente e disponíveis) em relação à força de trabalho total, na semana de referência.
- **Fonte**: IBGE, Pesquisa Nacional por Amostra de Domicílios Contínua trimestral (PNAD Contínua). SIDRA Tabela 4093. Ficha completa em `docs/04-fontes/ibge-sidra.md`.
- **Metodologia**: notas técnicas da PNAD Contínua (múltiplas versões).
- **Periodicidade**: trimestral (trimestres móveis consolidados).
- **Unidade**: %.
- **Abrangência**: Brasil, Grande Região, UF e recortes administrativos adicionais.
- **Dimensões (nesta tabela)**: sexo (Total/Homens/Mulheres). Cortes por faixa etária e instrução estão em outras tabelas do mesmo assunto (ex. 4095, 6397), não na 4093.
- **Histórico**: 201201-202602 (14+ anos).
- **Transformações**: nenhuma além das já calculadas pelo IBGE.
- **Atualização**: automatizável via API SIDRA e API de Agregados — ver classificação abaixo.
- **Relações com outros indicadores**: [A PREENCHER]. Candidatas do Discovery P1: Curva de Phillips / Phillips com expectativas (com IPCA); Lei de Okun (com PIB, indicador 1 deste catálogo).
- **Relações teóricas**: [A PREENCHER — Especialista em Metodologia Econômica].
- **Limitações**: erro amostral (CVs reportados na própria tabela); desenho amostral em transição do Censo 2010 para o Censo 2022, com integralização prevista para 2026 — risco de descontinuidade técnica na série durante a transição.
- **Status de automação**: **A — API direta**, com evidência prática de chamadas reais bem-sucedidas em ambas as APIs (SIDRA e Agregados) em 2026-09-22.

---

## 6. Rendimento médio real habitual do trabalho principal

- **Identificação**: Rendimento médio mensal real, trabalho principal, por posição na ocupação e categoria do emprego.
- **Conceito**: valor médio mensal do rendimento do trabalho habitualmente recebido no trabalho principal, pessoas 14+ ocupadas, em termos reais.
- **Fonte**: IBGE, PNAD Contínua trimestral (dado bruto já deflacionado pelo IBGE). SIDRA Tabela 5440. Ficha completa em `docs/04-fontes/ibge-sidra.md`. **Componente adicional**: deflacionamento próprio do DIEESE via Nota Técnica interna (maio/2015, atualizada out/2018) — documento não disponível publicamente nem nos materiais já lidos.
- **Metodologia**: metodologia de deflacionamento do próprio IBGE (índices regionais ponderados a partir do IPCA das regiões que compõem cada Grande Região); nota técnica adicional do DIEESE não confirmada em detalhe.
- **Periodicidade**: trimestral.
- **Unidade**: R$.
- **Abrangência**: Brasil, Grande Região, UF.
- **Dimensões (nesta tabela)**: posição na ocupação / categoria do emprego (11 categorias). Cortes por sexo, instrução ou grupamento de atividade estão em outras tabelas (5436, 5438, 5442), não na 5440.
- **Histórico**: 201201-202602.
- **Transformações**: deflacionamento já aplicado pelo IBGE na própria tabela; possível deflacionamento adicional do DIEESE — ver alerta abaixo.
- **Atualização**: componente IBGE automatizável (ver classificação); componente DIEESE depende de processo interno não mapeado.
- **Relações com outros indicadores**: [A PREENCHER]. Candidata do Discovery P1: produtividade e salários (produtividade ausente dos materiais P1, relação não testável apenas com este lote).
- **Relações teóricas**: [A PREENCHER — Especialista em Metodologia Econômica].
- **Limitações**: herdadas do desenho amostral da PNAD Contínua; rendimento "habitual" é autodeclarado; **erro histórico documentado pelo próprio IBGE** — entre jan/2012 e jan/2015, pesos regionais do deflator usaram indevidamente o INPC em vez do IPCA (posteriormente corrigido).
- **ALERTA — risco metodológico a validar**: a Tabela 5440 do IBGE já entrega o valor em termos REAIS (deflacionado pela metodologia do próprio IBGE). O material do DIEESE indica um deflacionamento adicional próprio (Nota Técnica DIEESE). **Não é possível determinar, com os materiais e fontes disponíveis nesta pesquisa, se isso configura dupla deflação (o DIEESE aplicaria seu deflator sobre um valor já real) ou se o DIEESE parte de uma série nominal distinta (ainda não identificada)**. Requer validação humana e/ou acesso à Nota Técnica DIEESE antes de qualquer uso analítico ou de automação deste indicador.
- **Status de automação**: **A — dado bruto do IBGE**, confirmado por teste real da chamada de valores (233 registros, 1º tri/2012–2º tri/2026) e piloto executado (`pipelines/ingestao/bloco_4_mercado_trabalho/coleta_rendimento_medio_real_sidra.py`, 2026-09-23). **E — deflacionamento adicional do DIEESE** (manual/específico, depende de documento interno não disponível) — continua sem solução, não é resolvido por este motor.

---

## 7. Volume de vendas — comércio (PMC)

- **Identificação**: Índice e variação da receita nominal e do volume de vendas no comércio varejista ampliado.
- **Conceito**: evolução do volume de vendas no comércio varejista ampliado (2022=100).
- **Fonte**: IBGE, Pesquisa Mensal de Comércio (PMC). SIDRA Tabela 8881. Ficha completa em `docs/04-fontes/ibge-sidra.md`.
- **ALERTA — cobertura parcial**: o material do DIEESE descreve este indicador como "comércio/serviços/indústria (PMC/PMS/PIM)" sob um único rótulo, mas **apenas a parcela comércio (PMC) foi confirmada**. As tabelas de PMS (serviços) e PIM (indústria) não foram identificadas nesta rodada — permanecem classificação D.
- **Periodicidade**: mensal. **Unidade**: número-índice / % (variação). **Abrangência**: Brasil.
- **Dimensões**: Tipos de índice (receita nominal; volume de vendas).
- **Histórico**: desde março/2003.
- **Status de automação**: **A** (comércio, piloto executado); **D** (serviços/indústria, não identificadas).

## 8. PIB per capita

- **Identificação**: Produto Interno Bruto per capita.
- **Conceito**: PIB dividido pela população residente, a valores correntes.
- **Fonte**: IBGE, Contas Nacionais. **ALERTA — tabela citada pelo DIEESE não existe**: a Tabela SIDRA 21777 citada no material retorna erro (HTTP 400/500) — não está mais no catálogo do SIDRA. Candidato de substituição identificado (hipótese, não confirmação): **Tabela 6784**. Ver detalhamento e QF08 em `docs/04-fontes/ibge-sidra.md`.
- **Periodicidade**: anual. **Unidade**: R$ correntes. **Abrangência**: Brasil.
- **Histórico**: 1996-2023 (tabela 6784, defasagem normal de Contas Nacionais anuais).
- **Status de automação**: **D** para a tabela original (21777, não existe); **A (hipótese)** para 6784 — não incluído no piloto técnico por falta de confirmação.

## 9. População e posição na ocupação

- **Identificação**: Pessoas ocupadas por posição na ocupação e categoria do emprego.
- **Conceito**: distribuição da população ocupada entre empregado com/sem carteira (setor privado e doméstico), setor público, empregador, conta própria, trabalhador familiar auxiliar.
- **Fonte**: IBGE, PNAD Contínua trimestral. SIDRA Tabela 4097. Ficha completa em `docs/04-fontes/ibge-sidra.md`.
- **Periodicidade**: trimestral. **Unidade**: mil pessoas / %. **Abrangência**: Brasil.
- **Histórico**: 1º trimestre/2012 até o mais recente.
- **Status de automação**: **A**, confirmada por teste real, piloto executado.

## 10. Taxa de participação na força de trabalho

- **Identificação**: Taxa de participação na força de trabalho.
- **Conceito**: proporção de pessoas 14+ que estão na força de trabalho (ocupadas + desocupadas em busca ativa) sobre o total da população em idade ativa.
- **Fonte**: IBGE, PNAD Contínua trimestral. SIDRA Tabela 6461. Ficha completa em `docs/04-fontes/ibge-sidra.md`.
- **Periodicidade**: trimestral. **Unidade**: %. **Abrangência**: Brasil.
- **Histórico**: 1º trimestre/2012 até o mais recente — mais longo que o recorte usado pelo DIEESE ("1T/2016 a 3T/2025").
- **Status de automação**: **A**, confirmada por teste real, piloto executado.

## 11. Taxas médias de juros por modalidade (PF/PJ, recursos livres)

- **Identificação**: Taxas médias de juros por modalidade de crédito — cheque especial, crédito pessoal não consignado (PF), aquisição de veículos, cartão de crédito rotativo (PJ).
- **Conceito**: custo médio do crédito em diferentes modalidades, recursos livres.
- **Fonte**: Banco Central do Brasil, via SGS. Códigos 20728, 22019, 20741, 20742 — já citados célula a célula no material do DIEESE, confirmados por teste real. Ficha completa em `docs/04-fontes/bcb.md`.
- **Periodicidade**: mensal. **Unidade**: % a.a. **Abrangência**: Brasil.
- **Histórico**: desde 03/2011 (3 séries) ou 07/1994 (cheque especial).
- **Status de automação**: **A**, confirmada por teste real, piloto executado — indicador de maior confiança de todo o checklist (única fonte com código de série já citado no material original).

## 12. NFSP — Necessidade de Financiamento do Setor Público

- **Identificação**: NFSP sem desvalorização cambial, fluxo acumulado em 12 meses, juros nominais, % do PIB.
- **Conceito**: montante que o setor público precisa captar para cobrir juros nominais da dívida, acumulado em 12 meses.
- **Fonte**: Banco Central do Brasil, via SGS. **ALERTA — ambiguidade de escopo não resolvida**: o código citado pelo material do DIEESE (5474) responde à API mas não está no catálogo oficial do BCB. Dois candidatos catalogados medem coisas diferentes: SGS 5760 ("Setor público consolidado") e SGS 5750 ("Governo Federal e Banco Central", exclui estados/municípios/estatais). Ver QF07 e detalhamento em `docs/04-fontes/bcb.md`.
- **Periodicidade**: mensal. **Unidade**: % do PIB. **Abrangência**: Brasil.
- **Status de automação**: **D** para 5474 (não catalogado); **A (hipótese)** para 5760/5750 — não incluído no piloto técnico até decisão da equipe do DIEESE sobre o escopo correto.

## 13. Evolução do salário médio de admissão e desligamento

- **Identificação**: Evolução do salário médio real de admissão e desligamento por mês.
- **Conceito**: valor médio salarial de trabalhadores admitidos e desligados formalmente no mercado de trabalho, por mês.
- **Fonte**: Novo CAGED, Ministério do Trabalho e Emprego (MTE), via PDET. Ficha completa em `docs/04-fontes/mte-caged.md`. **Sem API pública** — workbook mensal ("3. Tabelas") distribuído via pasta Google Drive sem URL fixa testável; caminho automatizável estável é o FTP de microdados brutos, que exige processamento próprio.
- **Periodicidade**: mensal. **Unidade**: R$. **Abrangência**: Brasil.
- **Histórico**: desde jan/2020 (metodologia Novo CAGED atual).
- **Status de automação**: **B (com ressalva) / C** — não incluído no piloto técnico. Ver QF09.

## 14. Saldo de admissões/desligamentos por grupamento de atividade e nível geográfico

- **Identificação**: Admissões, desligamentos e saldo por grupamento de atividade econômica e nível geográfico.
- **Conceito**: variação líquida de vínculos formais de emprego, por setor e território.
- **Fonte**: Novo CAGED, MTE/PDET. Mesma fonte e mesma limitação de acesso do indicador 13. Ficha completa em `docs/04-fontes/mte-caged.md`.
- **Periodicidade**: mensal. **Unidade**: nº de vínculos. **Abrangência**: Brasil, por setor e nível geográfico.
- **Histórico**: desde jan/2020.
- **Status de automação**: **B (com ressalva) / C** — não incluído no piloto técnico. Ver QF09.

## 15. PIB Mundial e estimativas

- **Identificação**: PIB Mundial e de países selecionados, variação real anual.
- **Conceito**: crescimento/contração do produto interno bruto real, mundial e por país/bloco, incluindo projeções.
- **Fonte**: Fundo Monetário Internacional (FMI), World Economic Outlook (WEO). API SDMX 3.0, dataflow WEO, indicador NGDP_RPCH. Ficha completa em `docs/04-fontes/fmi-cni.md`.
- **Periodicidade**: semestral (abril e outubro). **Unidade**: % variação. **Abrangência**: mundo, blocos, países.
- **Histórico**: 1980 até o presente, mais ~5 anos de projeção.
- **Limitação**: códigos de país do dataflow não são ISO3 simples — piloto coleta com curinga (todos os países/agregados); filtro por país específico é refinamento futuro.
- **Status de automação**: **A**, confirmada por teste real, piloto executado.

## 16. UCI — Utilização da Capacidade Instalada (Indústria de Transformação)

- **Identificação**: Utilização da Capacidade Instalada, indústria de transformação.
- **Conceito**: percentual da capacidade produtiva industrial efetivamente utilizada.
- **Fonte**: CNI — Indicadores Industriais. Ficha completa em `docs/04-fontes/fmi-cni.md`.
- **ALERTA — correção de atribuição**: o material do DIEESE cita "CNI - ICEI", mas a UCI não pertence ao ICEI (índice de confiança/expectativa) — pertence a outro levantamento da CNI, os "Indicadores Industriais". Recomenda-se corrigir a citação no material interno.
- **Periodicidade**: mensal. **Unidade**: %. **Abrangência**: Brasil.
- **Status de automação**: **B** — download estruturado (Excel), com descoberta de link via raspagem direcionada (URL muda a cada mês), confirmado e testado, piloto executado.

## 17. Balança comercial brasileira

- **Identificação**: Exportações, importações e saldo da balança comercial brasileira.
- **Conceito**: fluxo de comércio exterior, por NCM, mensal/acumulado.
- **Fonte**: MDIC, Comex Stat (SECEX é a secretaria dentro do MDIC, não uma instituição distinta). Ficha completa em `docs/04-fontes/mdic-tesouro.md`.
- **Periodicidade**: mensal. **Unidade**: US$ FOB. **Abrangência**: Brasil, por NCM/país/UF.
- **Histórico**: 1997-2026 (detalhado), 1989-1996 (agregado).
- **Status de automação**: **B confirmado** (CSV oficial por ano, URL estável e previsível) / **A hipótese** (API REST existe, endpoint agregado precisa teste com POST, não realizado nesta rodada). Piloto executado — download de CSV parcialmente concluído nesta rodada por instabilidade de rede do ambiente de desenvolvimento (não da fonte — HTTP 200 confirmado, mecanismo de retomada implementado).

## 18. Limite fiscal (prudencial e máximo) por Estado

- **Identificação**: Despesa total com pessoal (% da RCL) e limites da Lei de Responsabilidade Fiscal, por Unidade da Federação.
- **Conceito**: proximidade dos estados aos limites legais de gasto com pessoal.
- **Fonte**: SICONFI, Secretaria do Tesouro Nacional. Ficha completa em `docs/04-fontes/mdic-tesouro.md`.
- **Periodicidade**: quadrimestral (Relatório de Gestão Fiscal). **Unidade**: % da RCL. **Abrangência**: 27 UFs.
- **Observação**: o material do DIEESE registra consulta manual (02/06/2025) — a API já existe e automatiza o mesmo dado.
- **Status de automação**: **A**, confirmada por teste real com dados de São Paulo, piloto executado para as 27 UFs.

## 19. Endividamento familiar — parte PEIC/FecomercioSP

- **Identificação**: Percentual de famílias endividadas — Pesquisa de Endividamento e Inadimplência do Consumidor (PEIC).
- **Conceito**: proporção de famílias com dívidas em aberto, pesquisa de opinião mensal.
- **Fonte**: FecomercioSP. Ficha completa em `docs/04-fontes/fecomercio-peic.md`. (A outra parte deste indicador, BCB Tabela 27, ainda não foi pesquisada.)
- **Periodicidade**: mensal. **Unidade**: %. **Abrangência**: Brasil (pesquisa nacional da FecomercioSP).
- **Histórico**: desde fev/2004.
- **Status de automação**: **B** — download estruturado via API de mídia do WordPress (estável), confirmado e testado, piloto executado.

## 20. Expectativas de mercado (Focus) — insumo para estimativas de INPC/IPCA

- **Identificação**: Expectativas de mercado para IPCA e INPC, Boletim Focus.
- **Conceito**: pesquisa diária do BCB junto a instituições financeiras sobre expectativas de inflação futura — insumo bruto que o DIEESE usa em suas próprias estimativas (nowcasting).
- **Fonte**: Banco Central do Brasil, Sistema de Expectativas de Mercado (portal Olinda, OData) — sistema diferente do SGS. Ficha completa em `docs/04-fontes/bcb.md`.
- **Periodicidade**: diária (dias úteis). **Unidade**: % (média, mediana, desvio-padrão das expectativas). **Abrangência**: Brasil.
- **Histórico**: extenso (testado desde 2018 sem esforço adicional).
- **Status de automação**: **A**, confirmada por teste real para IPCA e INPC, piloto executado.

## 21. Volume de vendas — serviços (PMS) e indústria (PIM)

- **Identificação**: Índice/variação de volume de serviços (PMS) e produção física industrial (PIM-PF).
- **Conceito**: completam, junto com o comércio (PMC, indicador 7), o trio de pesquisas mensais de atividade que o material do DIEESE agrega sob o rótulo único "PMC/PMS/PIM".
- **Fonte**: IBGE. SIDRA 5906 (PMS) e SIDRA 8888 (PIM-PF). Ficha completa em `docs/04-fontes/ibge-sidra.md`.
- **Periodicidade**: mensal. **Unidade**: número-índice / % (variação acumulada em 12 meses). **Abrangência**: Brasil.
- **Histórico**: PMS desde jan/2011; PIM-PF desde jan/2002.
- **Status de automação**: **A** para ambos, confirmada por teste real, piloto executado.

## 22. INPC (parte IBGE da síntese de inflação)

- **Identificação**: Índice Nacional de Preços ao Consumidor (INPC), índice geral.
- **Conceito**: variação de preços ao consumidor para famílias com renda de 1 a 5 salários mínimos (público-alvo diferente do IPCA).
- **Fonte**: IBGE. SIDRA Tabela 7063. Ficha completa em `docs/04-fontes/ibge-sidra.md`. Parte de uma síntese multi-fonte do material do DIEESE (indicador 23 e 24, abaixo, são as demais partes).
- **Periodicidade**: mensal. **Unidade**: % (variação mensal/acumulada). **Abrangência**: Brasil.
- **Histórico**: a partir de jan/2020 (mesma reestruturação já vista no IPCA/7060).
- **Status de automação**: **A**, confirmada por teste real, piloto executado.

## 23. IGP-M (parte FGV da síntese de inflação, via rota alternativa BCB)

- **Identificação**: Índice Geral de Preços — Mercado (IGP-M), FGV/IBRE.
- **Conceito**: índice de preços amplo (produtor + consumidor + construção civil), usado como referência em contratos (aluguel, etc.).
- **Fonte**: FGV/IBRE — **sem acesso público direto confirmado** (portal exige contrato/assinatura). Coletado via **rota alternativa**: BCB/SGS código 189, que replica oficialmente o IGP-M. Ficha completa em `docs/04-fontes/fgv-indatend.md`.
- **Periodicidade**: mensal. **Unidade**: %. **Abrangência**: Brasil.
- **Limitação**: cobre apenas o IGP-M — outros índices FGV eventualmente citados pelo material (IPC-Fi, IPC-S) não têm rota alternativa confirmada.
- **Status de automação**: **A** (via BCB), piloto executado. Portal FGV direto: **D**.

## 24. INDATEND (parte manual da síntese de inflação)

- **Identificação**: fonte "INDATEND", citada no material do DIEESE como recebida por e-mail.
- **Conceito**: **Identificado (2026-09-23, evidência primária direta)** — não é instituição externa. É o nome de uma planilha Excel interna do próprio DIEESE (3 cópias mensais encontradas em `materiais/originais/`, título real nos metadados: "IBGE - Índices de Preços ao Consumidor"), que consolida manualmente ~11 séries já conhecidas (ICV-DIEESE, INPC, IPCA, IPC-FIPE, IPC-FGV, IGP-M, IGP-DI, IPA-DI, câmbio, salário mínimo, poupança, TR, BTN+TR).
- **Fonte**: processo de trabalho interno do DIEESE (planilha + envio por e-mail), não uma fonte externa a pesquisar. Ficha completa e evidência em `docs/04-fontes/fgv-indatend.md`.
- **Status de automação**: **E — manual, confirmado por evidência primária**. Não é lacuna de pesquisa — o dado bruto por trás do rótulo já está identificado; só mudaria se o DIEESE automatizasse o próprio processo interno.

## 25. Endividamento familiar — parte BCB ("Tabela 27") e Saldo de crédito SFN

- **Identificação**: (a) Endividamento e comprometimento de renda das famílias com o SFN (família de séries RNDBF); (b) Saldo da carteira de crédito do SFN, por tomador e tipo de recurso.
- **Conceito**: (a) mede o quanto a renda das famílias está comprometida com dívidas; (b) mede o volume total de crédito em aberto no sistema financeiro.
- **Fonte**: Banco Central do Brasil, via SGS. Ficha completa em `docs/04-fontes/bcb.md`.
- **ALERTA**: para (a), o rótulo "Tabela 27" do material do DIEESE não tem correspondência literal confirmada no BCB — 3 séries candidatas (29034, 29265, 29037) foram confirmadas tecnicamente, mas qual delas (ou combinação) o DIEESE usa não está 100% certo. Para (b), 6 séries confirmadas; 3 recortes adicionais não testados.
- **Periodicidade**: mensal. **Unidade**: % (endividamento) / R$ milhões (saldo de crédito).
- **Status de automação**: **A** para as 9 séries confirmadas (3 de endividamento + 6 de saldo de crédito), piloto executado.

## 26. Cesta básica x salário mínimo

- **Identificação**: valor da cesta básica de alimentos, percentual do salário mínimo líquido comprometido, tempo de trabalho necessário.
- **Conceito**: poder de compra do salário mínimo frente ao custo da alimentação básica, por capital.
- **Fonte**: DIEESE, em parceria com a Conab — Pesquisa Nacional da Cesta Básica de Alimentos, boletim mensal público. Ficha completa em `docs/04-fontes/dieese-publicacoes.md`. **Este indicador estava registrado como lacuna** (arquivo interno não obtido) — a pesquisa encontrou que o próprio DIEESE publica publicamente, todo mês, exatamente este dado.
- **Periodicidade**: mensal. **Unidade**: R$ (valor da cesta) / % (do SM) / horas:minutos (tempo de trabalho). **Abrangência**: 27 capitais (desde ago/2025; antes, 17).
- **Histórico**: boletins públicos desde pelo menos 2005.
- **Limitação**: dado granular por produto/cidade não é mais público desde abr/2018 (exige assinatura) — não afeta este indicador, que usa apenas o agregado já público.
- **Status de automação**: **B**, confirmada e testada, piloto executado.

## 27. Preços de combustíveis (gasolina, diesel, GLP)

- **Identificação**: preço médio de revenda de gasolina, diesel e GLP (gás de cozinha).
- **Conceito**: variação de preços de energia doméstica/transporte.
- **Fonte**: ANP — série "últimas 4 semanas" (gasolina/etanol, diesel/GNV, GLP), microdados por posto revendedor. Ficha completa em `docs/04-fontes/anp-ipeadata.md`. IPEADATA tem API real, mas granularidade anual — incompatível, descartada.
- **Periodicidade**: semanal. **Unidade**: R$/litro. **Abrangência**: Brasil, por posto/município/UF.
- **Achado**: o bloqueio HTTP 403 inicial na página da ANP não era bloqueio institucional — era detecção de bot por cabeçalhos HTTP incompletos. Resolvido, e os 222 links reais de download foram extraídos da página.
- **Status de automação**: **B**, confirmada e testada, piloto executado.

## 28. ICT — Índice da Condição do Trabalho

- **Identificação**: Índice da Condição do Trabalho, elaboração própria DIEESE.
- **Conceito**: índice sintético (0 a 1, quanto maior melhor) sobre condições de inserção no mercado de trabalho, a partir da PNAD Contínua (dimensões: inserção ocupacional, desocupação, rendimento).
- **Fonte**: DIEESE, boletim trimestral público (`dieese.org.br/analiseict/`). Ficha completa em `docs/04-fontes/dieese-publicacoes.md`. **Atualizado 2026-09-23**: reclassificação corrigida via teste técnico (`pdftotext`) e validação cruzada contra a apresentação interna do DIEESE — valor do 3º tri/2025 bate exatamente (0,6848 na fonte interna vs. 0,68 no boletim público).
- **Periodicidade**: trimestral.
- **Status de automação**: **B — download estruturado, confirmado e testado, piloto executado** (`pipelines/ingestao/bloco_4_mercado_trabalho/coleta_ict_dieese.py`).

## 29-31. Greves (número, categorias, reivindicações)

- **Identificação**: número de greves, principais categorias grevistas, principais reivindicações.
- **Conceito**: intensidade e natureza do conflito capital-trabalho no Brasil.
- **Fonte**: Sistema de Acompanhamento de Greves (SAG), sistema interno do DIEESE; publicado publicamente no "Balanço das Greves" (série de Estudos e Pesquisas). Ficha completa em `docs/04-fontes/dieese-publicacoes.md`. **Atualizado 2026-09-23**: reclassificação corrigida via teste técnico e validação cruzada — total de greves de 2024 (880) e as 5 principais reivindicações (com percentuais idênticos até a casa decimal) batem exatamente entre a apresentação interna do DIEESE e o boletim público EP 111.
- **Periodicidade**: semestral/anual.
- **Status de automação**: **B — download estruturado, confirmado e testado, piloto executado** (`pipelines/ingestao/bloco_4_mercado_trabalho/coleta_greves_dieese.py`).
- **ALERTA — cuidado com dado não confirmado (mantido)**: um suposto "EP 114" com número de greves de 2025 mencionado em rodada anterior segue não confirmado (404) — não foi reintroduzido. A edição mais recente real confirmada é a EP 113 ("Balanço das Greves de 2025", ano completo).
- **Status de automação**: **E — manual**. PDF-imagem, exigiria OCR.

## 32. Taxa de sindicalização

- **Identificação**: taxa de sindicalização das pessoas 14+ ocupadas, por grupamento de atividade.
- **Conceito**: proporção de trabalhadores ocupados filiados a sindicato.
- **Fonte**: IBGE, PNAD Contínua anual (módulo "Características Adicionais do Mercado de Trabalho"). SIDRA Tabela 8676. Ficha completa em `docs/04-fontes/ibge-sidra.md`. **Este era o único indicador do catálogo original sem nenhuma fonte identificada** — resolvido com cross-check exato: o valor de 2024 (8,9%) retornado pela API bate exatamente com o título do slide do material do DIEESE.
- **Periodicidade**: anual, mas não contínua (sem levantamento em 2020/2021).
- **Unidade**: %. **Abrangência**: Brasil e Grandes Regiões (sem UF/município).
- **Histórico**: 2012-2019, hiato, 2022-2024.
- **Status de automação**: **A**, confirmada por teste real com valor cruzado, piloto executado.

## 33. Distribuição de reajustes salariais em negociação coletiva

- **Identificação**: distribuição de reajustes salariais negociados, comparados ao INPC.
- **Conceito**: quantas negociações coletivas ficaram acima/abaixo da inflação.
- **Fonte**: DIEESE, boletim mensal público "De Olho nas Negociações" (mesmo padrão do ICT e do Balanço das Greves). Ficha completa em `docs/04-fontes/dieese-publicacoes.md`. **Atualizado 2ª rodada (2026-09-23)**: edição 67 (abr/2026) lida diretamente — série mensal abr/25-mar/26, % acima/abaixo do INPC, variação real média, por setor e região; nota metodológica explícita do DIEESE citando o Mediador/MTE como fonte primária. Mediador/MTE reconfirmado sem API nem exportação em massa (consulta manual, unitária); dados.gov.br (CKAN) exige token institucional.
- **Periodicidade**: mensal. **Histórico**: desde pelo menos 2021.
- **Status de automação**: **B — download estruturado, confirmado e testado, piloto executado** (`pipelines/ingestao/bloco_4_mercado_trabalho/coleta_negociacao_coletiva_dieese.py`). Teste técnico com `pdftotext -layout -enc UTF-8` confirmou camada de texto real e limpa no PDF; script executado com sucesso, encontrando a edição 72 (set/2026, dados até ago/2026). Extração dos números do texto (STAGING) ainda não implementada.
- **Pista não confirmada**: números de terceiros sobre volume de instrumentos coletivos (~90,5 mil 2023-2025) não confirmados em fonte primária — não usar.

## 34. Valor médio dos pisos salariais por categoria

- **Identificação**: valor médio/mediano dos pisos salariais negociados, por categoria profissional.
- **Conceito**: referência de piso salarial mínimo por categoria, fruto de negociação coletiva.
- **Fonte**: DIEESE, mesmo boletim "De Olho nas Negociações" do indicador 33. **Atualizado 2ª rodada (2026-09-23)**: slide "Pisos salariais" da edição 67 lido diretamente — piso médio R$ 1.846 / mediano R$ 1.719 (1º trimestre de 2026), por setor econômico e região; metodologia exclui pisos de estagiário/aprendiz e considera um valor por instrumento. SACC (sistema histórico DIEESE-MTE) segue sem série corrente (só 2004-2008), não é mais necessário como fonte. Ficha completa em `docs/04-fontes/dieese-publicacoes.md`.
- **ALERTA**: um valor diferente (R$ 1.867 médio, R$ 1.736 mediano, boletim nº 68) citado em rodada anterior via terceiros **segue não confirmado na fonte primária** — não usar. Os valores R$ 1.846/R$ 1.719 acima, por outro lado, foram lidos diretamente do PDF e podem ser tratados como confirmados para aquela edição/trimestre.
- **Status de automação**: **B — download estruturado, confirmado e testado, piloto executado** (mesmo script e mesma execução do indicador 33 — mesmo boletim).

## Registro de pendências transversais (todos os lotes)

- Duas divergências entre o material interno do DIEESE e a fonte oficial confirmada permanecem abertas (IPCA/pesos-base, câmbio/SIDRA inexistente) — requerem validação com a equipe do DIEESE.
- A divergência "Selic/SIDRA inexistente" foi **resolvida** em 2026-09-22 por comparação direta de dados (ver indicador 4) — fonte exata identificada como composição SGS 4189 (até jul/2024) + SGS 432 (a partir de ago/2024). Resta apenas a pergunta não bloqueante sobre a motivação da troca (QF03b).
- Um risco metodológico não resolvido (rendimento médio real / possível dupla deflação) — requer validação humana e/ou acesso a documento interno do DIEESE (QF04).
- **Novo (Lote 02)**: tabela SIDRA de PIB per capita citada pelo material (21777) não existe mais — candidato de substituição (6784) não confirmado (QF08).
- **Novo (Lote 02)**: indicador "PMC/PMS/PIM" do material cobre, na verdade, apenas comércio (PMC) na tabela citada — serviços e indústria não identificados.
- **Novo (Lote 03)**: código NFSP citado pelo material (5474) não está catalogado oficialmente pelo BCB — dois candidatos com escopos diferentes (5760, 5750) não confirmados (QF07).
- **Novo (checagem de completude do corpus histórico, 2026-09-22)**: indicadores IBC-Br, PIB de São Paulo, impacto de juros sobre a dívida pública e taxa composta de subutilização da força de trabalho aparecem em apresentações de conjuntura de anos anteriores (2020-2022) mas não no material de dez/2025 já catalogado — possivelmente descontinuados por decisão editorial do DIEESE, não pesquisados nesta rodada. Ver `research/notas/DISCOVERY_FONTES_LOTE_PILOTO_01.md`, Seção 9.
- Campos "Relações com outros indicadores" e "Relações teóricas" ainda não foram trabalhados por nenhum especialista neste lote — ficam registrados como pendência explícita, não como ausência de relevância.
