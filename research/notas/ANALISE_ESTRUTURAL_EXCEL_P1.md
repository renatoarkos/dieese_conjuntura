# Análise Estrutural do Excel P1 (arquivo de referência)

## 1. Arquivo analisado

`materiais/originais/Apresentação de conjuntura/Apresentação_Conjuntura_4T_2025.xlsx` — escolhido como referência principal conforme justificado em `COMPARACAO_EXCEL_P1.md`, seção 7. Esta escolha é **provisória** e depende de confirmação humana.

Total de abas: **47**. Nenhuma célula foi alterada; leitura em modo leitura via `openpyxl`.

## 2. Mapa temático segundo a própria aba `Sumário` do arquivo

A aba `Sumário` (dimensões B3:Q10) contém uma tabela-índice explícita relacionando tema, faixa de abas, periodicidade de atualização e bases de dados — reproduzida abaixo (EVIDÊNCIA DIRETA, extraída da própria planilha, sem interpretação):

| Tema | Abas (Slides) | Atualização | Último período | Bases de dados citadas |
|---|---|---|---|---|
| Macroeconomia | T2-T13 | Mensal/Trimestral | ago\|set-25 / 3T | FMI, BCB, IBGE, SECEX, SICONFI |
| Estatísticas Monetárias | T14-T18 | Mensal | set/2025 | BCB¹, PEIC, BCB² |
| Índices de Inflação | T19-T25 | Mensal | set/2025 | IBGE, BCB, ICV |
| PIBxSELIC | T26 | Trimestral | 2T/25 | (não especificada nesta linha) |
| Cesta Básica | T27-T28 | Mensal | jun/2025 | DIEESE |
| PNAD | T32-T38 | Trimestral | 3T/2025 | IBGE |
| CAGED | T39-T44 | Mensal | set/2025 | IBGE |

**OBSERVAÇÃO METODOLÓGICA IMPORTANTE (INFERÊNCIA)**: a faixa "T27-T28" (Cesta Básica) referenciada pelo próprio Sumário **não existe como abas neste arquivo** — não há `T27` nem `T28` no workbook "principal" (ver `COMPARACAO_EXCEL_P1.md`, seção 5.1). A aba `T34`, referenciada implicitamente pela sequência PNAD (T32-T38), também está ausente. Isso indica que a aba `Sumário` é um índice que não foi atualizado após a remoção dessas abas nesta cópia específica — ou que o conteúdo de Cesta Básica migrou para outro lugar (possivelmente diretamente para a apresentação, sem aba dedicada nesta planilha). Achado a validar com a equipe do DIEESE.

## 3. Inventário aba a aba

Para cada aba: nome, tema (segundo Sumário, quando aplicável), dimensões, indícios de tabelas/gráficos/fórmulas, fonte citada explicitamente (quando encontrada na amostra lida) e observações. **Não foram copiados dados célula a célula** — apenas cabeçalhos, linhas de rodapé com citação de fonte, e contagens agregadas.

| Aba | Tema | Dimensões | Fórmulas | Gráficos | Fonte citada (quando identificada) | Observação |
|---|---|---|---|---|---|---|
| `Sumário` | Sem tema no Sumário / técnicas | B3:Q10 | 0 | 0 | não identificada explicitamente na amostra lida | Tema / Slides / Atualização / Último / Bases de Dados |
| `T2` | Macroeconomia | B1:M14 | 0 | 0 | Fonte: FMI - World Economic Outlook Update - July 2025 | PIB Mundial e estimativas - 2016 a 2026
%
Países Selecionados e Mundo
 |
| `T3` | Macroeconomia | A1:B38 | 0 | 1 | Fonte: BCB - Sistema Expectativas de Mercado - PIB Total; SIDRA - IBGE | Tabela 5932 - Taxa de variação do índice de volume trimestral |
| `T4` | Macroeconomia | A1:H11 | 0 | 0 | Fonte: IBGE - Sistema de Contas Nacionais Trimestrais | Indicadores do PIB 
Setores da Economia e Gastos Familiares e Governamentais
%
3º Trimestr |
| `T4b` | Macroeconomia | A1:V124 | 0 | 2 | Fonte: IBGE - SCNT | Série Encadeada do Índice de Volume Trimestral com Ajuste Sazonal |
| `T5` | Macroeconomia | A1:L50 | 0 | 1 | Fonte: IBGE - Contas Nacionais Trimestrais | Tabela 5932 - Taxa de variação do índice de volume trimestral |
| `T6` | Macroeconomia | A1:H34 | 0 | 1 | Fonte: IBGE - Contas Nacionais Trimestrais | Tabela 5932 - Taxa de variação do índice de volume trimestral |
| `T7a` | Macroeconomia | A1:V124 | 0 | 1 | Fonte: IBGE - SCNT | Série Encadeada do Índice de Volume Trimestral com Ajuste Sazonal |
| `T7b` | Macroeconomia | A1:V123 | 0 | 2 | Fonte: IBGE - SCNT | Série Encadeada do Índice de Volume Trimestral com Ajuste Sazonal |
| `T8` | Macroeconomia | A1:T229 | 0 | 1 | Fonte: CNI - ICEI | Mes/Ano / Indicadores Industriais
UCI - Utilização da capacidade instalada% 
Brasil
 C Ind |
| `T9` | Macroeconomia | A1:S75 | 0 | 1 | Fonte: IBGE - Pesquisa Mensal de Comércio | PMC, PMS e PMI / Tabela 8881 - Índice e variação da receita nominal e do volume de vendas  |
| `T10` | Macroeconomia | A2:B32 | 0 | 1 | Fonte | 21777 - Produto interno bruto per capita em R$ do último ano - R$ |
| `T11` | Macroeconomia | A1:B39 | 0 | 2 | Fonte | Data / 3694 - Taxa de câmbio - Livre - Dólar americano (venda) - Média de período - anual  |
| `T12` | Macroeconomia | A1:J53 | 0 | 1 | Fonte: Secretaria de Comércio Exterior / Ministério do Desenvolvimento, Indústria, Comérci | Totais - Acumulados |
| `T13` | Macroeconomia | B3:O29 | 0 | 1 | não identificada explicitamente na amostra lida | MA / 30.06 |
| `T14` | Estatísticas Monetárias | A1:J125 | 176 | 1 | Fonte: SIDRA e BCB | IPCA, Taxa Selic e Juros Real
%
nov-15 a jul-25 |
| `T15a` | Estatísticas Monetárias | A1:J40 | 0 | 1 | Fonte: FecomercioSP* | Endividamento Familiar, por Faixa de Renda
%
Brasil
Jan/23 a Jun/25 |
| `T15b` | Estatísticas Monetárias | A1:Q212 | 0 | 1 | não identificada explicitamente na amostra lida | Tabela 27 – Crédito do sistema financeiro - Endividamento e comprometimento de renda das f |
| `T16` | Estatísticas Monetárias | A2:AK98 | 9 | 1 | não identificada explicitamente na amostra lida | Taxas médias de juros  por modalidade - Pessoas jurídicas  |
| `T17` | Estatísticas Monetárias | A1:Z184 | 11 | 1 | Fonte: BCB |  5474 - NFSP sem desvalorização cambial (% PIB)
Fluxo Acumulado no Ano
Juros Nominais
Seto |
| `T18` | Estatísticas Monetárias | A1:R143 | 142 | 2 | não identificada explicitamente na amostra lida | Saldo de Crédito do SF: recursos livres e direcionados |
| `T19` | Índices de Inflação | A1:AV172 | 1169 | 1 | Fonte: https://sidra.ibge.gov.br/tabela/7060 | IPCA e Subgrupos
%
Jan/15 a Set/25
 |
| `T20` | Índices de Inflação | A1:E9 | 0 | 1 | Fonte: IBGE e BCB | IPCA e Subgrupos
2022 a 2025
Acumulado em 12 meses
% |
| `T21` | Índices de Inflação | A2:D54 | 0 | 3 | FONTE: INDATEND  (PH/email) | 1) Outros Indicadores de Inflação |
| `T22` | Índices de Inflação | B7:Q22 | 0 | 1 | Fonte: IBGE - Índice Nacional de Preços ao Consumidor | Tabela 7063 - INPC - Variação mensal, acumulada no ano, acumulada em 12 meses e peso mensa |
| `T23` | Índices de Inflação | A2:T111 | 310 | 1 | Fonte: BCB - Sistema de Expectativas de Mercado; IBGE/SIDRA | Usamos a media |
| `T24` | Índices de Inflação | A2:I111 | 299 | 1 | Fonte: BCB - Sistema de Expectativas de Mercado; IBGE/SIDRA | IPCA E ESTIMATIVA DE INFLAÇÃO  |
| `T25` | Índices de Inflação | B2:F14 | 0 | 2 | Fonte: ICV (Tabela 4 - Var. Anual (%) | Fonte: ICV (Tabela 4 - Var. Anual (%) |
| `T26` | PIB x SELIC | A1:J217 | 71 | 1 | Fonte | Data / 4189 - Taxa de juros - Selic acumulada no mês anualizada base 252 - % a.a. / Períod |
| `T32a` | PNAD | A1:D61 | 0 | 1 | Fonte: IBGE - Pesquisa Nacional por Amostra de Domicílios Contínua trimestral | Tabela 4093 - Pessoas de 14 anos ou mais de idade, total, na força de trabalho, ocupadas,  |
| `T32b` | PNAD | A1:R23 | 12 | 2 | Fonte: IBGE - Pesquisa Nacional por Amostra de Domicílios Contínua trimestral | Tabela 4093 - Pessoas de 14 anos ou mais de idade, total, na força de trabalho, ocupadas,  |
| `T33` | PNAD | A1:R11 | 0 | 2 | Fonte: IBGE - Pesquisa Nacional por Amostra de Domicílios Contínua trimestral | Tabela 4094 - Pessoas de 14 anos ou mais de idade, total, na força de trabalho, ocupadas,  |
| `T35` | PNAD | A1:R67 | 179 | 2 | Fonte: IBGE - Pesquisa Nacional por Amostra de Domicílios Contínua trimestral | Tabela 4097 - Pessoas de 14 anos ou mais de idade, ocupadas na semana de referência, por p |
| `T35b` | PNAD | B1:P26 | 14 | 0 | não identificada explicitamente na amostra lida | 3º trimestre 2025 |
| `T36` | PNAD | A1:U30 | 73 | 1 | não identificada explicitamente na amostra lida | Tabela 4097 - Pessoas de 14 anos ou mais de idade, ocupadas na semana de referência, por p |
| `T37` | PNAD | A1:B60 | 0 | 1 | Fonte: IBGE - Pesquisa Nacional por Amostra de Domicílios Contínua trimestral | Tabela 6461 - Taxa de participação na força de trabalho, na semana de referência, das pess |
| `T38` | PNAD | A1:C13 | 0 | 1 | Fonte: IBGE - Pesquisa Nacional por Amostra de Domicílios Contínua trimestral | Tabela 5440 - Rendimento médio mensal real das pessoas de 14 anos ou mais de idade ocupada |
| `T39` | Novo CAGED | A1:E67 | 0 | 1 | Fonte: Novo Caged – MTE. | TABELA 9 - EVOLUÇÃO DO SALÁRIO MÉDIO REAL DE ADMISSÃO E DESLIGAMENTO POR MÊS - SEM AJUSTES |
| `Slide 39` | Novo CAGED | A1:A1 | 0 | 1 | não identificada explicitamente na amostra lida | (sem cabeçalho textual identificável na amostra lida) |
| `T40-43` | Novo CAGED | A1:KQ39 | 0 | 0 | Fonte: Novo Caged – MTE. | TABELA 1 - ADMISSÕES, DESLIGAMENTOS E SALDO POR GRUPAMENTO DE ATIVIDADES ECONÔMICAS E SEÇÃ |
| `T40` | Novo CAGED | A1:I15 | 0 | 0 | Fonte: Novo Caged – MTE. | TABELA 6.1 - EVOLUÇÃO MENSAL DE ESTOQUE, ADMISSÕES, DESLIGAMENTOS E SALDO POR GRUPAMENTO D |
| `T41` | Novo CAGED | A1:I15 | 0 | 0 | Fonte: Novo Caged – MTE. | Evolução do saldo por grupamento de atividades econômicas 
Indústria - com ajustes – Últim |
| `T42` | Novo CAGED | A1:I27 | 0 | 0 | Fonte: Novo Caged – MTE. | Evolução do saldo por grupamento de atividades econômicas 
Serviços - com ajustes –  Últim |
| `T43` | Novo CAGED | A1:E17 | 0 | 0 | não identificada explicitamente na amostra lida | Evolução do saldo por grupamento de atividades econômicas 
Serviços - com ajustes –  Últim |
| `T44` | Novo CAGED | A1:E14 | 0 | 1 | Fonte: Novo Caged – MTE. | TABELA 2 - ADMISSÕES, DESLIGAMENTOS E SALDO POR NÍVEL GEOGRÁFICO - SETEMBRO DE 2025 |
| `T45` | Novo CAGED | B27:F33 | 24 | 1 | não identificada explicitamente na amostra lida | (sem cabeçalho textual identificável na amostra lida) |
| `Plan1` | Sem tema no Sumário / técnicas | A1:A1 | 0 | 0 | não identificada explicitamente na amostra lida | (sem cabeçalho textual identificável na amostra lida) |

## 4. Leitura por bloco temático

### 4.1 Macroeconomia (T2-T13)

Bloco cobre PIB mundial (T2, fonte FMI/WEO), PIB brasileiro trimestral em diferentes recortes — por ótica de oferta/demanda, série encadeada com ajuste sazonal (T3-T7b, fonte IBGE - Contas Nacionais Trimestrais/SCNT), indicadores industriais e UCI (T8, fonte CNI-ICEI), volume de vendas comércio/serviços/indústria (T9, fonte IBGE - PMC/PMS/PIM), PIB per capita (T10), taxa de câmbio (T11), balança comercial (T12, fonte SECEX/MDIC) e um indicador por Unidade da Federação ainda não identificado com segurança (T13, ver `INVENTARIO_INDICADORES_P1.md`, confiança BAIXA). As abas T4b, T7a e T7b têm dimensões grandes (até 124 linhas x 22 colunas) e concentram séries longas com ajuste sazonal — candidatas a maior esforço de tratamento metodológico.

### 4.2 Estatísticas Monetárias (T14-T18)

Cobre Selic, IPCA e juros real (T14 — ver divergência com a cópia "dieese" registrada em `COMPARACAO_EXCEL_P1.md`), endividamento/comprometimento de renda das famílias (T15a/T15b, fonte BCB/PEIC), taxas médias de juros por modalidade PF/PJ (T16, fonte BCB), NFSP/juros nominais do setor público (T17, referencia a própria aba T14 via fórmula cruzada) e saldo de crédito do SFN (T18, com 142 fórmulas — o maior volume de cálculo do bloco). T14 e T19 concentram, respectivamente, 176 e 1.169 fórmulas — os maiores volumes de tratamento matemático dentro da planilha.

### 4.3 Índices de Inflação (T19-T26)

Bloco mais denso do arquivo em termos de fórmulas: T19 (IPCA e subgrupos, 1.169 fórmulas, fonte IBGE/SIDRA tabela 7060), T23 e T24 (estimativas de INPC/IPCA com encadeamento via `PRODUCT()`, 310 e 299 fórmulas respectivamente — ver `FLUXO_ATUAL_CONJUNTURA.md`), T21 ("Outros Indicadores de Inflação", que cita múltiplas fontes distintas — INDATEND, Portal FGV, SIDRA — sugerindo consolidação manual de fontes externas), T25 (ICV — Índice do Custo de Vida, próprio do DIEESE, fonte citada apenas como "ICV"). T26 mistura Selic e PIB trimestral com médias móveis (`AVERAGE`) por trimestre.

### 4.4 PNAD (T32a-T38)

Todas as abas deste bloco citam explicitamente a mesma fonte: "IBGE - Pesquisa Nacional por Amostra de Domicílios Contínua trimestral". Cobre força de trabalho/ocupação/desocupação (T32a/T32b, tabela IBGE 4093), outra segmentação da mesma pesquisa (T33, tabela 4094), posição na ocupação (T35/T35b/T36, tabela 4097, com 179 e 73 fórmulas respectivamente), taxa de participação na força de trabalho (T37, tabela 6461) e rendimento médio real (T38, tabela 5440). A aba `T34`, que apareceria na sequência lógica T32-T38, está ausente nesta cópia (presente em "dieese" como T34/T34a — ver `COMPARACAO_EXCEL_P1.md`).

### 4.5 Novo CAGED (T39-T45)

Todas as abas citam "Fonte: Novo Caged – MTE". Cobre evolução do salário médio de admissão/desligamento (T39, tabela 9), uma tabela ampla e pouco convencional (`T40-43`, 303 colunas — provavelmente uma extração bruta multi-tabela, ver observação abaixo), e evolução do saldo de admissões/desligamentos por grupamento de atividade e nível geográfico (T40 a T44). `T45` (24 fórmulas) referencia `T44` via fórmula cruzada (`=T44!B6`), funcionando como uma tabela auxiliar/resumo derivada de T44 — não uma fonte primária própria. `Slide 39` é uma aba de 1 célula, aparentemente técnica (elo de suporte para um slide específico), sem conteúdo analítico próprio.


**Observação sobre `T40-43`**: dimensões A1:KQ39 (303 colunas) são atípicas para as demais abas do arquivo (a maioria tem menos de 50 colunas). É consistente com uma extração tabular bruta (ex.: cruzamento de atividade econômica x mês, lado a lado) mantida como base para as abas T40-T43 subsequentes, e não como uma peça de leitura direta.

## 5. O que NÃO foi encontrado nesta planilha

- Nenhuma aba relacionada a **greves, negociação coletiva ou sindicalização**, embora esse seja um eixo temático extenso na apresentação (`ATR_Conjuntura_2025.12.pptx`, slides 47-57 — ver `ANALISE_APRESENTACAO_CONJUNTURA_2025_12.md`). Os dados desse eixo não têm, portanto, origem identificada neste arquivo Excel P1.

- Nenhuma aba de **Cesta Básica** (T27-T28), apesar de referenciada no próprio Sumário do arquivo.

- Nenhuma tabela nativa do Excel (`ws.tables`) foi encontrada em nenhuma das 47 abas — todas as tabelas aparentes são faixas de células formatadas manualmente, não objetos "Tabela" do Excel/LibreOffice.

## 6. Limitações

- A "finalidade aparente" e o "tema" de cada aba foram inferidos a partir de cabeçalhos e citações de fonte visíveis nas primeiras linhas/últimas linhas lidas — não houve leitura de todas as células de todas as abas.

- Gráficos foram contados por objeto (`ws._charts`), mas seus títulos internos nem sempre puderam ser extraídos (muitos gráficos usam referência a células para o título, não texto estático).

- A aba T13 não teve fonte nem tema identificados com confiança suficiente (ver `INVENTARIO_INDICADORES_P1.md`).

## 7. Adendo — Rodada 2 (Validação Técnica): estrutura interna OOXML

Inspeção adicional feita diretamente no pacote ZIP do arquivo (sem qualquer alteração), complementando a leitura via `openpyxl`. Detalhamento completo em `VALIDACAO_TECNICA_P1.md` (Frente A).

- **Visibilidade das abas:** das 47 abas, apenas **`T4b` está oculta** (`state="hidden"` em `xl/workbook.xml`); as demais 46 são visíveis. Isso não havia sido verificado na Rodada 1 (que usava apenas `openpyxl` em modo padrão, sem checar o atributo de visibilidade).
- **Intervalos nomeados:** o workbook declara dois nomes definidos herdados de um arquivo-raiz comum de 2015 (`base`, `base1`), apontando por sintaxe de referência externa (`[N]Segmentação!Célula`) para um arquivo externo `Peic_2010.xls`. Uma varredura por regex em todas as fórmulas de todas as células **não encontrou nenhum uso ativo** desses nomes nem da sintaxe de referência externa — são vestigiais.
- **Links externos declarados (`xl/externalLinks/`):** 2, ambos apontando para `Peic_2010.xls` (vestigiais, ver acima).
- **Conexões de dados, Power Query, objetos OLE, ActiveX:** nenhum encontrado.
- **Gráficos internos ao próprio Excel:** 47 (`xl/charts/chartN.xml`), consistente com a contagem por planilha já registrada na Rodada 1.
- **Metadados de autoria:** `dc:creator` = "Lucas Capelo"; `dcterms:created` = 2015-06-05T18:19:34Z; `dcterms:modified` = 2026-03-19T13:15:10Z. Estes metadados, comparados aos do arquivo "dieese" (`materiais/originais/dieese/Apresentação_Conjuntura_4T_2025 (2).xlsx`), confirmam que os dois arquivos descendem do mesmo arquivo-raiz — ver `COMPARACAO_EXCEL_P1.md`, Seção 9.
- **Sobre a Seção 5 (o que não foi encontrado):** a Rodada 2 aprofundou a busca por Cesta Básica e Greves/Negociação Coletiva no corpus mais amplo de 339 materiais (não apenas neste arquivo). Resultado: Cesta Básica tem origem identificável com boa confiança (aba `T27`, presente apenas no arquivo "dieese", e um arquivo dedicado no corpus, "SM e Cesta desde 1979[...].xlsx"); Greves/Negociação Coletiva permanecem sem arquivo-fonte identificado no corpus, embora haja evidência técnica (nas fórmulas de série dos gráficos do `.pptx`) de que as abas de origem (`T50`, `T52`-`T54`) existem em uma versão do arquivo não presente no corpus. Ver `VALIDACAO_TECNICA_P1.md`, Frentes F e G, para o detalhamento completo.
