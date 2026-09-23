# Fonte: IBGE / SIDRA

## Identificação da instituição

- **Instituição produtora**: Instituto Brasileiro de Geografia e Estatística (IBGE).
- **Sistema de disseminação**: SIDRA — Sistema IBGE de Recuperação Automática (sidra.ibge.gov.br), e API de Agregados (servicodados.ibge.gov.br/api/v3).
- **Natureza**: fonte primária e oficial. Para os quatro indicadores investigados neste lote, o IBGE é o produtor direto do dado (pesquisa amostral ou registro processado internamente) — não há agregação de dado de terceiros nestes casos.
- **Data de consulta de todo este documento**: 2026-09-22.

## Observação operacional geral (vale para todas as tabelas abaixo)

Tentativas de acesso direto (fetch automatizado) às páginas HTML institucionais em `ibge.gov.br` e `sidra.ibge.gov.br` retornaram **HTTP 403** (bloqueio a user-agents automatizados) em toda a pesquisa deste lote. Em contraste, as **APIs de dados** — `apisidra.ibge.gov.br` e `servicodados.ibge.gov.br/api/v3` — responderam normalmente e foram testadas com sucesso, retornando dados reais e coerentes. Isso é relevante para uma futura avaliação de engenharia de dados: o acesso programático deve mirar as APIs de dados, não o scraping de páginas HTML, que é bloqueado.

Padrão de API SIDRA confirmado e testado:
```
https://apisidra.ibge.gov.br/values/t/{tabela}/n1/{território}/v/{variável}/p/{período}/c{classificação}/{categorias}
```
Documentação: `https://apisidra.ibge.gov.br/home/ajuda` (acessível diretamente).

Padrão de API de Agregados confirmado e testado:
```
https://servicodados.ibge.gov.br/api/v3/agregados/{tabela}/metadados
```
Documentação: `https://servicodados.ibge.gov.br/api/docs/agregados?versao=3` (acessível diretamente).

Existe também API de calendário de divulgações: `https://servicodados.ibge.gov.br/api/docs/calendario?versao=3` (documentada, não testada nesta rodada).

---

## Tabela 5932 — PIB Brasil, variação do índice de volume trimestral

| Campo | Valor |
|---|---|
| O que mede | Variação real (volume, sem efeito-preço) do PIB trimestral do Brasil — trimestre/mesmo trimestre do ano anterior, acumulado em 4 trimestres, acumulado no ano, trimestre/trimestre anterior com ajuste sazonal. |
| Pesquisa de origem | Sistema de Contas Nacionais Trimestrais (Coordenação de Contas Nacionais — CONAC/IBGE). |
| Status da tabela | **CONFIRMADO ATIVA** — testada via API em 2026-09-22, retornou dado real do 2º trimestre de 2026 (taxa trimestral a.a. 2,0%; acumulada 4 trimestres 1,9%; acumulada no ano 1,9%; trimestre/trimestre anterior 0,5%). Nenhuma divergência de numeração frente ao citado pelo material do DIEESE. |
| Documentação metodológica | Sistema de Contas Nacionais — Referência 2010, 3ª edição: `https://biblioteca.ibge.gov.br/visualizacao/livros/liv96834.pdf`. Nota técnica de ajuste sazonal (X-13 ARIMA-SEATS): `https://ftp.ibge.gov.br/Contas_Nacionais/Contas_Nacionais_Trimestrais/Ajuste_Sazonal/X13_NasContasTrimestrais.pdf`. |
| Método de acesso | API SIDRA confirmada (exemplo testado: `https://apisidra.ibge.gov.br/values/t/5932/n1/all/v/all/p/last%201/c11255/90707`). Download estruturado via interface web — hipótese de alta confiança (padrão do SIDRA), não confirmado por navegação direta (bloqueio 403). |
| Periodicidade | Trimestral; divulgação ~60 dias após o fim do trimestre (não confirmado por documento oficial lido integralmente). |
| Histórico | Série encadeada desde 1996 (base 1995=100). |
| Dimensões | Apenas nível Brasil (N1) — não há desagregação estadual nesta tabela (PIB estadual é anual, outra pesquisa). |
| Revisões conhecidas | Mudança de ano de referência para 2010 ("Referência 2010", 2015), seguindo SNA 2008 — nova classificação de produtos/atividades, integração CNAE 2.0, adoção do X-13 ARIMA-SEATS. |
| Calendário | Existe calendário oficial (`ibge.gov.br/calendario/conjunturais.html`, `ibge.gov.br/calendario/mensal.html`) — confirmado via busca indexada, não lido diretamente (403). |
| Limitações | Defasagem de ~60 dias; dados preliminares sujeitos a revisão; série dessazonalizada recalculada a cada nova observação. |
| **Classificação de automação** | **A — API direta**, confirmada por teste real bem-sucedido. |

---

## Tabela 7060 — IPCA e subgrupos

| Campo | Valor |
|---|---|
| O que mede | Variação de preços ao consumidor (mensal, acumulada no ano, acumulada em 12 meses, peso mensal) para famílias com renda de 1 a 40 salários mínimos, áreas urbanas, 16 regiões de abrangência do SNIPC. |
| Pesquisa de origem | Sistema Nacional de Índices de Preços ao Consumidor (SNIPC/IBGE). |
| Status da tabela | **CONFIRMADO ATIVA**, mas com **divergência relevante em relação ao material do DIEESE** — ver seção "Achado a validar" abaixo. |
| Documentação metodológica | Nota Metodológica 01/2018 (SNIPC): `https://ftp.ibge.gov.br/Precos_Indices_de_Precos_ao_Consumidor/Sistema_de_Indices_de_Precos_ao_Consumidor/Notas_Metodologicas/Nota_metodologica_012018.pdf`. Métodos de Cálculo do SNIPC, 6ª ed.: `https://ftp.ibge.gov.br/Precos_Indices_de_Precos_ao_Consumidor/Sistema_de_Indices_de_Precos_ao_Consumidor/Metodos_de_calculo/Metodos_de_Calculo_6ed.pdf`. |
| Método de acesso | API SIDRA confirmada (exemplo testado: `https://apisidra.ibge.gov.br/values/t/7060/n1/all/v/all/p/last%201/c315/7169`). |
| Periodicidade | Mensal. |
| Histórico | O IPCA como indicador existe desde dez/1979, mas a **Tabela 7060 especificamente só cobre a partir de janeiro/2020** — períodos anteriores estão em tabelas históricas distintas (1419: jan/2012-dez/2019; 2938: 2006-2011; 58: 1991-1999). |
| Dimensões | Brasil + 16 áreas de abrangência do SNIPC (regiões metropolitanas + DF + algumas capitais), por grupo/subgrupo/item/subitem de despesa. |
| Revisões conhecidas | Reponderação com base na POF 2017-2018, vigente desde jan/2020 — substituiu a POF 2008-2009 (vigente jan/2012-dez/2019). Cada reponderação gera uma **nova tabela SIDRA** (não uma atualização retroativa da tabela anterior) — é assim que a mudança metodológica é sinalizada. |
| Calendário | Mesmo calendário institucional do IBGE (ver Tabela 5932). |
| Limitações | Cobre apenas famílias urbanas de 1-40 salários mínimos (não toda a população, não áreas rurais); defasagem crescente entre padrão de consumo medido pela POF e padrão real corrente entre uma reponderação e outra. |
| **Classificação de automação** | **A — API direta**, confirmada por teste real bem-sucedido, para o índice geral e grupos/subgrupos/itens/subitens oficiais. **D — investigação adicional** especificamente para os agregados "Serviços" e "Monitorados" citados pelo material do DIEESE (ver achado abaixo). |

### Achados a validar (divergências material DIEESE × fonte oficial confirmada)

1. **Base de pesos incorreta no material do DIEESE**: o material interno registra "pesos-base jan/2012" para a Tabela 7060. A pesquisa confirmou que a Tabela 7060 usa pesos da **POF 2017-2018** (vigentes desde jan/2020) — a tabela com pesos-base jan/2012 é a **Tabela 1419**, hoje histórica e sem novas atualizações. É possível que o material do DIEESE tenha misturado a citação de URL (7060) com uma nota herdada de uma versão anterior da planilha (quando talvez a fonte fosse de fato a 1419). **Recomenda-se validação com a equipe do DIEESE.**
2. **"Serviços" e "Monitorados" não localizados na Tabela 7060**: a classificação completa (C315) da tabela foi consultada via API e contém apenas os 9 grupos oficiais do IPCA (Alimentação e bebidas, Habitação, Artigos de residência, Vestuário, Transportes, Saúde e cuidados pessoais, Despesas pessoais, Educação, Comunicação) e seus subgrupos/itens/subitens — não os agregados especiais "Serviços" e "Monitorados" citados no material do DIEESE (slide 19/T19). Esses agregados existem como conceito no IBGE, mas a tabela SIDRA exata onde são publicados **não foi localizada** nesta rodada — registrado como pendência, não como confirmação de inexistência.

---

## Tabela 4093 — Taxa de desocupação

| Campo | Valor |
|---|---|
| O que mede | Proporção de pessoas de 14+ anos desocupadas (procurando trabalho ativamente e disponíveis) em relação à força de trabalho total, na semana de referência. |
| Pesquisa de origem | Pesquisa Nacional por Amostra de Domicílios Contínua trimestral (PNAD Contínua). |
| Status da tabela | **CONFIRMADO ATIVA** — metadados lidos diretamente via `servicodados.ibge.gov.br/api/v3/agregados/4093/metadados`; valores reais obtidos via API SIDRA (2º tri/2026: Brasil total 5,4%; homens 4,6%; mulheres 6,4%). Série 201201-202602. Nenhuma renumeração frente ao citado pelo DIEESE. |
| Documentação metodológica | Notas técnicas da PNAD Contínua (múltiplas versões, ex. `biblioteca.ibge.gov.br/visualizacao/livros/liv101651_notas_tecnicas.pdf`); arquivo `notas_metodologicas.pdf` confirmado existente em `ftp.ibge.gov.br/Trabalho_e_Rendimento/.../Notas_metodologicas/` (download real bem-sucedido, extração de texto não realizada). |
| Método de acesso | API SIDRA e API de Agregados **ambas testadas e funcionais** (exemplo real: `https://apisidra.ibge.gov.br/values/t/4093/n1/1/v/4099/p/last/c2/all`). Microdados públicos confirmados diretamente em `https://ftp.ibge.gov.br/Trabalho_e_Rendimento/Pesquisa_Nacional_por_Amostra_de_Domicilios_continua/Trimestral/Microdados/` (diretório acessado, pastas por ano 2012-2026). |
| Periodicidade | Trimestral (trimestres móveis consolidados). |
| Histórico | 201201 a 202602 (14+ anos). |
| Dimensões (nesta tabela) | Sexo (Total/Homens/Mulheres). Território: Brasil, Grande Região, UF, recortes adicionais N6/N7/N14. Cortes por faixa etária e instrução estão em outras tabelas do mesmo assunto (ex. 4095, 6397), não na 4093. |
| Revisões conhecidas | Reponderação de 2025 (Nota técnica 02/2025) incorporando Projeções de População 2024 baseadas no Censo 2022, vigente desde 31/07/2025 em todos os trimestres móveis. Amostra Mestra em transição gradual do desenho Censo 2010 → Censo 2022, integralização prevista para 2026. |
| Calendário | Calendário oficial confirmado existir (`ibge.gov.br/calendario-de-divulgacoes-novoportal.html`), conteúdo detalhado não lido diretamente (403). |
| Limitações | Erro amostral (CVs reportados na própria tabela); desenho amostral em transição até 2026, risco de descontinuidade técnica na série durante a transição. |
| **Classificação de automação** | **A — API direta**, com evidência prática (chamada real bem-sucedida em ambas as APIs). O agente que pesquisou classificou de forma conservadora como B por não ter testado o pipeline completo de parsing/paginação de ponta a ponta — a viabilidade técnica de A está confirmada; a engenharia de um pipeline de produção é etapa futura, não deste Discovery. |

---

## Tabela 5440 — Rendimento médio real habitual do trabalho principal

| Campo | Valor |
|---|---|
| O que mede | Valor médio mensal do rendimento do trabalho habitualmente recebido no trabalho principal, pessoas 14+ ocupadas, **em termos reais** (já deflacionado pela metodologia do próprio IBGE), por posição na ocupação/categoria do emprego. |
| Pesquisa de origem | PNAD Contínua trimestral. |
| Status da tabela | **CONFIRMADO ATIVA** via metadados (`servicodados.ibge.gov.br/api/v3/agregados/5440/metadados`). Série 201201-202602. Nome oficial confirmado: "Rendimento médio mensal real das pessoas de 14 anos ou mais de idade ocupadas na semana de referência com rendimento de trabalho, habitualmente e efetivamente recebidos no trabalho principal, por posição na ocupação e categoria do emprego no trabalho principal". |
| Documentação metodológica | Nota sobre correção no cálculo dos deflatores: `https://ftp.ibge.gov.br/Trabalho_e_Rendimento/Pesquisa_Nacional_por_Amostra_de_Domicilios_continua/Nota_Tecnica/2015_04_09_pnadc_calculo_dos_deflatores.pdf`. |
| Método de acesso | API de Agregados confirmada e testada (metadados). API SIDRA para valores — mesma sintaxe da Tabela 4093, não testada especificamente com chamada de valores nesta rodada. Microdados públicos no mesmo diretório FTP da Tabela 4093. |
| Periodicidade | Trimestral. |
| Histórico | 201201-202602. |
| Dimensões (nesta tabela) | Posição na ocupação / categoria do emprego (11 categorias). Território: Brasil, Grande Região, UF. Cortes por sexo, instrução ou grupamento de atividade estão em outras tabelas (5436, 5438, 5442), não na 5440. |
| Revisões conhecidas | Mesma reponderação 2025 (Censo 2022) da Tabela 4093. Adicionalmente: **erro histórico documentado pelo próprio IBGE** — entre jan/2012 e jan/2015, os pesos regionais do deflator usaram indevidamente o INPC em vez do IPCA; posteriormente corrigido (nota técnica específica). |
| Calendário | Mesmo calendário institucional único da PNAD Contínua. |
| Limitações | Herdadas do desenho amostral (erro amostral); sensibilidade do valor real ao método de deflacionamento regional; rendimento "habitual" é autodeclarado. |
| **Classificação de automação** | **B — dado bruto do IBGE já deflacionado**: API de metadados confirmada, chamada de valores não testada especificamente nesta rodada. **E — para a etapa de deflacionamento adicional do DIEESE** (ver achado abaixo), por depender de documento interno do DIEESE não disponível publicamente. |

### Achado a validar — risco de dupla deflação

O material interno do DIEESE registra que os valores de rendimento passam por deflacionamento próprio, via "Nota Técnica DIEESE" (maio/2015, atualizada out/2018). A pesquisa confirmou que a **própria Tabela 5440 do IBGE já entrega o valor em termos REAIS**, com metodologia de deflacionamento documentada e própria do IBGE (incluindo um erro histórico já corrigido, ver acima). Isso levanta uma pergunta metodológica que não pôde ser resolvida nesta pesquisa (a Nota Técnica DIEESE não foi localizada publicamente nem está nos materiais já lidos):

- **Hipótese A**: o DIEESE aplica seu próprio deflator sobre um valor que já é real (dupla deflação) — risco metodológico.
- **Hipótese B**: o DIEESE parte de uma série de valores nominais (não a 5440) e aplica seu próprio deflator — nesse caso não há duplicidade, mas a fonte de entrada usada pelo DIEESE seria outra tabela, ainda não identificada.

**Esta é uma questão que exige validação humana e/ou acesso à Nota Técnica DIEESE — não deve ser presumida em nenhuma direção.**

---

## Tabela 8881 — Volume de vendas, comércio (PMC)

**Achado importante (Lote 02, 2026-09-22)**: o material do DIEESE descreve este indicador como "comércio/serviços/indústria (PMC/PMS/PIM)", citando uma única tabela (8881). A pesquisa confirma que **a Tabela 8881 cobre apenas a Pesquisa Mensal de Comércio (PMC)** — não há PMS (serviços) nem PIM (indústria) nesta tabela, nenhuma classificação de setor além de "Tipos de índice" (receita nominal vs. volume de vendas). As tabelas de PMS e PIM não foram identificadas nesta rodada.

| Campo | Valor |
|---|---|
| O que mede | Índice e variação da receita nominal e do volume de vendas no comércio varejista ampliado (2022=100). |
| Status da tabela | **CONFIRMADO ATIVA** — testada via API, retornou dado real (3.397 registros coletados no piloto, mar/2003-jul/2026). |
| Método de acesso | API SIDRA confirmada: `https://apisidra.ibge.gov.br/values/t/8881/n1/all/v/all/p/all/c11046/all` (classificação `c11046` = "Tipos de índice", confirmada via metadados). |
| Periodicidade | Mensal. |
| Histórico | Desde março/2003. |
| Dimensões | Uma classificação: Tipos de índice (2 categorias — receita nominal; volume de vendas). |
| **Classificação de automação** | **A — API direta**, confirmada por teste real. **Apenas para a parcela comércio** — PMS/PIM permanecem D (não identificadas). |

## Tabela 21777 — PIB per capita (citada pelo DIEESE) — NÃO EXISTE MAIS

**Achado (Lote 02, 2026-09-22)**: a tabela SIDRA 21777, citada no material do DIEESE para PIB per capita, **não existe** — retorna HTTP 400/500 em todas as tentativas de acesso (valores, metadados). Não é bloqueio de acesso; é ausência real da tabela no catálogo atual do SIDRA.

**Candidato de substituição identificado (hipótese, não confirmação)**: **Tabela 6784** — "Produto Interno Bruto, Produto Interno Bruto per capita, População residente e Deflator" — cobre o mesmo tema (PIB per capita em R$ correntes), testada com sucesso via `https://apisidra.ibge.gov.br/values/t/6784/n1/all/v/all/p/last%201`, retornando valor real (R$ 51.693,92 para 2023). Periodicidade anual, histórico 1996-2023 (defasagem de ~2-3 anos, normal para Contas Nacionais anuais).

**Esta substituição não deve ser tratada como confirmada** — é uma hipótese de que 6784 é o que o DIEESE "quis dizer" ao citar 21777, não uma confirmação com a equipe do DIEESE. Ver QF08 em `research/notas/DISCOVERY_FONTES_LOTE_PILOTO_01.md`.

**Classificação de automação**: D para 21777 (não existe). A (mas como hipótese, não confirmação) para 6784.

## Tabela 4097 — População e posição na ocupação

| Campo | Valor |
|---|---|
| O que mede | Pessoas 14+ ocupadas por posição na ocupação e categoria do emprego (empregado setor privado com/sem carteira, trabalhador doméstico, setor público, empregador, conta própria, trabalhador familiar auxiliar). |
| Status da tabela | **CONFIRMADO ATIVA** — testada via API (3.249 registros coletados no piloto), bate 100% com a descrição do material do DIEESE. |
| Método de acesso | API SIDRA confirmada: `https://apisidra.ibge.gov.br/values/t/4097/n1/all/v/all/p/all/c11913/all` (classificação `c11913` = "Posição na ocupação e categoria do emprego"). |
| Periodicidade | Trimestral. |
| Histórico | 1º trimestre/2012 até o mais recente disponível. |
| Unidade | Mil pessoas / %. |
| **Classificação de automação** | **A — API direta**, confirmada por teste real. |

## Tabela 6461 — Taxa de participação na força de trabalho

| Campo | Valor |
|---|---|
| O que mede | Taxa de participação na força de trabalho, pessoas 14+, na semana de referência. |
| Status da tabela | **CONFIRMADO ATIVA** — testada via API (349 registros coletados no piloto), bate com a descrição do material do DIEESE. |
| Método de acesso | API SIDRA confirmada: `https://apisidra.ibge.gov.br/values/t/6461/n1/all/v/all/p/all` (sem classificação adicional — tabela não tem recorte de sexo/idade). |
| Periodicidade | Trimestral. |
| Histórico | 1º trimestre/2012 até o mais recente — **mais longo do que o citado pelo DIEESE** ("1T/2016 a 3T/2025"); o range do material é um recorte de uso interno, não o histórico total disponível na fonte. |
| Unidade | %. |
| **Classificação de automação** | **A — API direta**, confirmada por teste real. |

## Tabela 5906 — PMS (Pesquisa Mensal de Serviços)

**Achado (Lote 05c, 2026-09-22)**: completa, junto com PMC (8881, já confirmada) e PIM (8888, abaixo), o trio de pesquisas mensais de atividade que o material do DIEESE agrega sob o rótulo único "PMC/PMS/PIM".

| Campo | Valor |
|---|---|
| O que mede | Índice e variação da receita nominal e do volume de serviços (2022=100). |
| Status | **CONFIRMADO ATIVA** — tabela vigente (as antigas 6442/6443/6444/8161-8164 estão marcadas "série encerrada"). Testado: `https://apisidra.ibge.gov.br/values/t/5906/n1/all/v/11626/p/last%206/c11046/56726/f/n` retornou variação acumulada em 12 meses real (ex.: jul/2026 = 2,4%). |
| Método de acesso | API SIDRA, variável 11626 ("PMS - Variação acumulada em 12 meses"), classificação 11046, categoria 56726 ("Índice de volume de serviços"). |
| Periodicidade | Mensal. |
| Histórico | jan/2011 até o mês corrente. |
| **Classificação de automação** | **A — API direta**, confirmada por teste real, piloto executado. |

## Tabela 8888 — PIM-PF (Pesquisa Industrial Mensal, Produção Física)

| Campo | Valor |
|---|---|
| O que mede | Produção física industrial, por seções e atividades (índice geral e recortes setoriais). |
| Status | **CONFIRMADO ATIVA** — tabela vigente (antigas 3653/6663/7511.../8159 "encerradas"). Testado: `https://apisidra.ibge.gov.br/values/t/8888/n1/all/v/11604/p/last%206/c544/129314/f/n` retornou variação acumulada em 12 meses real (ex.: jul/2026 = 0,6%, Indústria geral). |
| Método de acesso | API SIDRA, variável 11604 ("PIMPF - Variação acumulada em 12 meses"), classificação 544, categoria 129314 ("Indústria geral"). Existem também tabelas 8887 (grandes categorias econômicas) e 8885 (grupos/classes selecionados), caso o DIEESE precise de recortes adicionais. |
| Periodicidade | Mensal. |
| Histórico | jan/2002 até o mês corrente. |
| **Classificação de automação** | **A — API direta**, confirmada por teste real, piloto executado. |

## Tabela 7063 — INPC (parte da síntese "INPC, ICV e outros indicadores de inflação")

**Achado (Lote 06b, 2026-09-22)**: o indicador do material do DIEESE mistura 3 sub-fontes distintas (INDATEND por e-mail, SIDRA, Portal FGV) numa única tabela consolidada manualmente. Esta ficha cobre apenas a parte INPC/IBGE — as demais estão em `docs/04-fontes/fgv-indatend.md`.

| Campo | Valor |
|---|---|
| O que mede | INPC — variação mensal, acumulada no ano, acumulada em 12 meses e peso mensal, por grupo/subgrupo/item/subitem. |
| Status | **CONFIRMADO ATIVA** — testado: `https://apisidra.ibge.gov.br/values/t/7063/n1/all/v/all/p/last%201/c315/allxt` retornou dado real (ago/2026). |
| Nome oficial | "INPC - Variação mensal, acumulada no ano, acumulada em 12 meses e peso mensal, para o índice geral, grupos, subgrupos, itens e subitens de produtos e serviços (a partir de janeiro/2020)". |
| Periodicidade | Mensal. |
| Histórico | A partir de jan/2020 (mesmo padrão de reestruturação já visto no IPCA/Tabela 7060 — série mais longa exigiria localizar tabela predecessora, não testado). |
| **Classificação de automação** | **A — API direta**, confirmada por teste real. |

## Tabela 8676 — Taxa de sindicalização

**Achado (investigação de lacunas, 2026-09-22)**: este era o único indicador do catálogo original sem NENHUMA fonte identificada. Localizada e confirmada com cross-check exato contra o material do DIEESE.

| Campo | Valor |
|---|---|
| O que mede | Taxa de sindicalização das pessoas 14+ ocupadas, por grupamento de atividade no trabalho principal. |
| Pesquisa de origem | PNAD Contínua **anual** (não a trimestral regular) — módulo "Características Adicionais do Mercado de Trabalho". |
| Status | **CONFIRMADO ATIVA E VALOR CRUZADO COM O MATERIAL.** Testado: `https://apisidra.ibge.gov.br/values/t/8676/n1/1/v/12535/p/2024/c888/47946` retornou **8,9%** para Brasil/2024/Total — bate exatamente com o título do slide do material do DIEESE ("Com taxa de 8,9%, sindicalização cresce pela primeira vez desde 2012"). Teste de 2012 confirmou 16,1% — também consistente com o texto do slide. |
| Método de acesso | API SIDRA e API de Agregados confirmadas. Variável 12535 = "Taxa de sindicalização"; classificação 888 = "Grupamentos de atividades no trabalho principal" (11 categorias, batendo com o recorte do material). |
| Periodicidade | Anual, mas **não contínua** — suplemento não levantado em 2020/2021 (provável disrupção da pandemia). Série real: 2012-2019, hiato, 2022-2024. |
| Dimensões | Brasil e Grandes Regiões apenas (sem UF/município nesta tabela). |
| Tabelas irmãs (mesmo padrão, não testadas neste lote) | 8675 (por nível de instrução), 8677 (por posição na ocupação/categoria do emprego) — mesma pesquisa, caso o DIEESE precise desses recortes. |
| Observação sobre o site do DIEESE | O DIEESE cita este dado em seu próprio Boletim de Conjuntura como "elaboração DIEESE", mas reprocessa a mesma fonte primária (IBGE/SIDRA) — não publica um dataset autônomo. A fonte real e testável é o IBGE, não o DIEESE. |
| **Classificação de automação** | **A — API direta**, confirmada por teste real com valor cruzado, piloto executado. |

## Síntese de classificação de automação (Tabelas IBGE/SIDRA — todos os lotes)

| Tabela | Indicador | Classificação | Confiança |
|---|---|---|---|
| 5932 | PIB Brasil (variação trimestral) | A | Alta — testado, piloto executado |
| 7060 | IPCA e subgrupos (índice geral e grupos oficiais) | A | Alta — testado, piloto executado |
| 7060 | "Serviços" / "Monitorados" (agregados especiais) | D | Não localizado |
| 4093 | Taxa de desocupação | A | Alta — testado, piloto executado |
| 5440 | Rendimento médio real (dado bruto IBGE) | B | Média — metadados testados, valores não |
| 5440 | Deflacionamento adicional DIEESE | E | Depende de documento interno do DIEESE |
| 8881 | Volume de vendas — comércio (PMC) | A | Alta — testado, piloto executado |
| 8881 (implícito) | Volume de vendas — serviços/indústria (PMS/PIM) | D | Tabela não identificada |
| 21777 | PIB per capita (citação original do DIEESE) | D | Tabela não existe |
| 6784 | PIB per capita (candidato de substituição) | A (hipótese) | Não confirmado como intenção do DIEESE — QF08 |
| 4097 | População e posição na ocupação | A | Alta — testado, piloto executado |
| 6461 | Taxa de participação na força de trabalho | A | Alta — testado, piloto executado |
