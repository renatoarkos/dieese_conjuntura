# Mapa Slide ↔ Aba — Material P1 (Rodada 2 do Discovery Profundo)

**Status:** documento de pesquisa (`research/notas/`) — não commitado.
**Fonte de evidência:** vínculos técnicos OOXML (`ppt/charts/chartN.xml`, `.rels`) levantados na Frente D de `VALIDACAO_TECNICA_P1.md`, cruzados com os nomes de aba existentes em `principal` (47 abas) e `dieese` (54 abas), e com a leitura de conteúdo slide-a-slide já feita na Rodada 1 (`ANALISE_APRESENTACAO_CONJUNTURA_2025_12.md`).
**Níveis de confiança:**
- **CONFIRMADO** — o gráfico do slide tem, no OOXML, uma fórmula de série apontando para um nome de aba que existe literalmente em ao menos um dos dois Excel P1, com vínculo externo (`TargetMode="External"`) para um arquivo da mesma linhagem ("Apresentação_Conjuntura_...").
- **PROVÁVEL** — há evidência técnica ou de conteúdo forte, mas com alguma lacuna (nome de aba não bate exatamente; gráfico incorporado/congelado em vez de vinculado; ou correspondência por conteúdo/tema sem vínculo OOXML).
- **POSSÍVEL** — apenas correspondência temática/de conteúdo (tabela nativa ou gráfico sem `.rels`), levantada por leitura visual na Rodada 1, sem nenhum vínculo técnico rastreável.
- **NÃO IDENTIFICADO** — nem vínculo técnico nem aba com nome/conteúdo correspondente foram encontrados em nenhum dos dois Excel P1.
- **SEM CORRESPONDÊNCIA** — slide de título, transição ou encerramento, sem indicador associado (não se aplica classificação).

Nenhuma correspondência foi forçada: onde a evidência não permite decidir, o slide é classificado como PROVÁVEL ou NÃO IDENTIFICADO, nunca CONFIRMADO por suposição.

---

## Tabela slide → aba (58 slides)

| Slide | Tema | Vínculo técnico (Rodada 2) | Aba(s) correspondente(s) | Classificação |
|---|---|---|---|---|
| 1 | Capa / identificação | — (slide de título) | — | SEM CORRESPONDÊNCIA |
| 2 | PIB Mundial 2016-2026 | tabela nativa, sem gráfico OOXML | T2 | POSSÍVEL |
| 3 | PIB Brasil e estimativa BC 2010-2026 | chart1: **sem `.rels`, sem `c:externalData`** — gráfico estático | T3/T4/T4b (correspondência temática da Rodada 1; **não confirmada tecnicamente** — o gráfico não carrega nenhum vínculo de origem) | POSSÍVEL |
| 4 | PIB 3T/2025 | tabela nativa, sem gráfico OOXML | T4/T5/T6 | POSSÍVEL |
| 5 | Variação do PIB — demanda | chart2 → aba `T5` (vínculo externo, arquivo "...2025.4T\Apresentação_Conjuntura_4T_2025.xlsx") | T5 | CONFIRMADO |
| 6 | Variação do PIB — oferta | chart3 → `T6` (idem) | T6 | CONFIRMADO |
| 7 | Patamar do PIB, série encadeada | chart4 → `T7a`; chart5 → `T7b` (idem) | T7a/T7b | CONFIRMADO |
| 8 | UCI — Indústria | chart6 → `T8` (idem) | T8 | CONFIRMADO |
| 9 | Volume de vendas — indústria/serviço/comércio | chart7 → `T9` (idem) | T9 | CONFIRMADO |
| 10 | PIB per capita 1996-2024 | chart8 → `T10` (vínculo externo, snapshot "2025.09\Apresentação_Conjuntura_09-25.xlsx") | T10 | CONFIRMADO (aponta para um snapshot de set/2025, não para o arquivo do 4T; conteúdo da aba `T10` bate em ambos) |
| 11 | Câmbio | chart9 → `T11` (SharePoint, mesma linhagem); chart10 → `T11` (local, "2025.4T") | T11 | CONFIRMADO |
| 12 | Balança comercial | chart11 → `T12` (idem 2025.4T) | T12 | CONFIRMADO |
| 13 | Limite fiscal por Estado | chart12 → `T13` (idem) | T13 | CONFIRMADO |
| 14 | Selic, IPCA, juros real | chart13 → `T14` (idem) | T14 (**apenas em "principal"** — ver Frente C de `VALIDACAO_TECNICA_P1.md`: em "dieese" o mesmo conteúdo está em `T18a`) | CONFIRMADO |
| 15 | Endividamento familiar | chart14 → `T15a`; chart15 → `T15b` (idem) | T15a/T15b (em "principal"; "dieese" tem uma única aba `T15`, sem o particionamento a/b) | CONFIRMADO |
| 16 | Juros por modalidade PF/PJ | tabela nativa, sem gráfico OOXML | T16 | POSSÍVEL |
| 17 | Juros da dívida pública | chart16 → `T17` (idem) | T17 | CONFIRMADO |
| 18 | Saldo de crédito SFN | chart17, chart18 → `T18` (idem) | T18 | CONFIRMADO |
| 19 | IPCA e subgrupos 2020-2025 | chart19 → `T19` (idem) | T19 | CONFIRMADO |
| 20 | IPCA e subgrupos 2022-2025 | chart20 → `T20` (idem) | T20 | CONFIRMADO |
| 21 | INPC, ICV e outros | chart21, chart22 → `T21` (idem) | T21 (Rodada 1 também citou `T22`; a evidência técnica desta rodada só confirma `T21` para este slide — `T22` está tecnicamente vinculada ao slide 22, não a este) | CONFIRMADO (para T21) |
| 22 | INPC por grupos | chart23 → `T22` (idem) | T22 | CONFIRMADO |
| 23 | Estimativas INPC | chart24 → `T23` (idem) | T23 | CONFIRMADO |
| 24 | Estimativas IPCA | chart25 → `T24` (idem) | T24 | CONFIRMADO |
| 25 | ICV | chart26, chart27 → `T25` (idem) | T25 | CONFIRMADO |
| 26 | PIB x Selic | chart28 → `T26` (idem) | T26 | CONFIRMADO |
| 27 | Cesta básica, outubro/2025, por localidade | tabela nativa, sem gráfico OOXML | não identificada tecnicamente; tematicamente ligada ao bloco Cesta Básica (ver slide 28 e Frente G) | NÃO IDENTIFICADO |
| 28 | Cesta básica x salário mínimo (evolução) | chart29 → workbook **incorporado** (`Planilha1`), sem vínculo externo | sem aba P1 correspondente; conteúdo compatível com `T27` de "dieese" e com o arquivo do corpus "SM e Cesta desde 1979[...].xlsx" (ver Frente G.1) | PROVÁVEL |
| 29 | Preços de combustíveis | chart30 → aba `Plan2`, vínculo externo para `20251127 - Preços combustíveis.xlsx` (fora do corpus) | sem aba P1 correspondente; arquivo-fonte nomeado tecnicamente, mas ausente do corpus (ver Frente G.2) | NÃO IDENTIFICADO (dentro dos dois P1); PROVÁVEL quanto à linhagem externa |
| 30 | "MERCADO DE TRABALHO" (título) | — | — | SEM CORRESPONDÊNCIA |
| 31 | ICT — Índice de Condição do Trabalho | chart31 → `[ICT - Brasil - PNAD Continua - 202503.xls]Resumo (Tab 1)`, vínculo externo (fora do corpus) | sem aba P1 correspondente; arquivo-fonte nomeado tecnicamente, mas ausente do corpus (ver Frente G.3) | NÃO IDENTIFICADO (dentro dos dois P1); PROVÁVEL quanto à linhagem externa |
| 32 | Desocupação — Brasil e Grandes Regiões | chart32 → `T32a`; chart33 → `T32b` (vínculo "2025.4T") | T32a/T32b | CONFIRMADO |
| 33 | Desocupação por UF | chart34 → série referenciando **`T33A`** (esse nome exato não existe como aba em nenhum dos dois P1; existe `T33`) | T33 (correspondência provável, não idêntica) | PROVÁVEL |
| 34 | Desocupação por faixa etária | chart35 → `T33` (vínculo "2025.4T") | T33 | CONFIRMADO |
| 35 | "Alguns números" (texto corrido) | — (sem gráfico) | — | SEM CORRESPONDÊNCIA |
| 36 | População e posição na ocupação | chart36 → workbook **incorporado** (`Planilha1`), sem vínculo externo | sem aba P1 confirmada tecnicamente; Rodada 1 sugeriu T33/T35/T36 por conteúdo | PROVÁVEL |
| 37 | Posição na ocupação, setor privado | chart37 → `T36` (vínculo "2025.4T") | T36 | CONFIRMADO |
| 38 | Conta própria com/sem CNPJ | chart38 → série referenciando **`T36A`** (não existe como aba; existe `T36`) | T36 (correspondência provável, não idêntica) | PROVÁVEL |
| 39 | Taxa de participação | chart39 → `T37` (vínculo "2025.4T", perfil "ricardo" sem sufixo TAMASHIRO) | T37 | CONFIRMADO |
| 40 | Rendimento médio real | chart40 → `T38` (idem) | T38 | CONFIRMADO |
| 41 | Salário admissão/desligamento | chart41 → `T39` (vínculo snapshot "2025.09") | T39 | CONFIRMADO |
| 42 | Saldo CAGED por grupamento (geral) | tabela nativa, sem gráfico OOXML | T40-43 (Rodada 1) | POSSÍVEL |
| 43 | Saldo CAGED — Indústria | tabela nativa, sem gráfico OOXML | T41 (Rodada 1); tematicamente relacionável à aba oculta `Ty` de "dieese" (staging de Indústria — ver Frente B), sem confirmação técnica | POSSÍVEL |
| 44 | Saldo CAGED — Serviços | tabela nativa, sem gráfico OOXML | T42 (Rodada 1); tematicamente relacionável às abas ocultas `T43`/`T4x` de "dieese" (staging/resumo de Serviços — ver Frente B), sem confirmação técnica | POSSÍVEL |
| 45 | Saldo CAGED — Serviços (nov/24-out/25) | tabela nativa, sem gráfico OOXML; **não recebeu linha própria na tabela da Rodada 1** (tratado só em nota no slide 44) — lacuna identificada nesta rodada | mesma observação do slide 44 (T43/T4x) | POSSÍVEL |
| 46 | Saldo por nível geográfico | chart42 → `T45` (vínculo "2025.4T") | T45 | CONFIRMADO |
| 47 | "GREVES E NEGOCIAÇÕES COLETIVAS" (título) | — | — | SEM CORRESPONDÊNCIA |
| 48 | Número de greves 2017-2024 | chart43 → série referenciando **`T50`** (não existe em nenhum dos dois Excel P1) | nenhuma (ver Frente F: aba existe em versão do arquivo ausente do corpus) | NÃO IDENTIFICADO |
| 49 | Categorias grevistas | tabela nativa, sem gráfico OOXML | nenhuma | NÃO IDENTIFICADO |
| 50 | Reivindicações de greve | chart44 → série referenciando **`T52`** (não existe) | nenhuma (idem 48) | NÃO IDENTIFICADO |
| 51 | Greves 1S/2025 | chart45 → série referenciando **`T53`** (não existe) | nenhuma (idem 48) | NÃO IDENTIFICADO |
| 52 | Sindicalização | chart46 → série referenciando **`T54`** (não existe) | nenhuma (idem 48) | NÃO IDENTIFICADO |
| 53 | Distribuição de reajustes 2015/2024 | chart47: **sem `.rels`, sem `c:externalData`** — gráfico estático | nenhuma | NÃO IDENTIFICADO |
| 54 | Negociações nov/24-out/25 vs INPC | tabela nativa, sem gráfico OOXML | nenhuma | NÃO IDENTIFICADO |
| 55 | Negociações por categoria vs INPC | tabela nativa, sem gráfico OOXML | nenhuma | NÃO IDENTIFICADO |
| 56 | Negociações por categoria vs INPC (2ª tabela) | tabela nativa, sem gráfico OOXML | nenhuma | NÃO IDENTIFICADO |
| 57 | Pisos salariais por categoria | tabela nativa, sem gráfico OOXML | nenhuma — Rodada 1 já havia notado que `T45` existe mas contém conteúdo diferente (grupamentos CAGED, não pisos) | NÃO IDENTIFICADO |
| 58 | Encerramento institucional | — | — | SEM CORRESPONDÊNCIA |

## Contagem por classificação

- **CONFIRMADO:** 28 slides (5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 32, 34, 37, 39, 40, 41, 46)
- **PROVÁVEL:** 8 slides (2, 3, 4, 16, 28, 33, 36, 38)
- **POSSÍVEL:** 4 slides (42, 43, 44, 45)
- **NÃO IDENTIFICADO:** 13 slides (27, 29, 31, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57)
- **SEM CORRESPONDÊNCIA (título/transição/encerramento):** 5 slides (1, 30, 35, 47, 58)

Total: 28 + 8 + 4 + 13 + 5 = 58 slides.

---

## Frente H — Linhagem preliminar por bloco temático

| Bloco | Arquivo/base de origem | Aba(s) | Indicador | Slides | Classificação da linhagem |
|---|---|---|---|---|---|
| Macroeconomia (PIB, câmbio, balança, fiscal) | `Apresentação_Conjuntura_4T_2025.xlsx` ("principal"), fontes primárias FMI/BCB/IBGE/SECEX/SICONFI | T2-T13 | Múltiplos | 2-13 | CONFIRMADA (para os slides com vínculo técnico) / PROVÁVEL (tabelas nativas) |
| Estatísticas monetárias (juros, crédito) | idem | T14-T18 | Múltiplos | 14-18 | CONFIRMADA |
| Inflação (IPCA, INPC, ICV) | idem | T19-T25 | Múltiplos | 19-25 | CONFIRMADA |
| PIB x Selic | idem | T26 | 1 | 26 | CONFIRMADA |
| Cesta básica | arquivo dedicado "SM e Cesta desde 1979[...].xlsx" (corpus) + aba `T27` (apenas em "dieese") | T27 (dieese) | Cesta básica x SM | 27-28 | PROVÁVEL |
| Combustíveis | `20251127 - Preços combustíveis.xlsx` (não presente no corpus); correlato: `Preços combustíveis histórico.xlsx` | — | Preços de combustíveis | 29 | PROVÁVEL (linhagem), NÃO IDENTIFICADA (arquivo exato) |
| ICT | `ICT - Brasil - PNAD Continua - 202503.xls` (não presente no corpus); correlato: `ICT - Dieese - 202302.xls` | — | Índice de Condição do Trabalho | 31 | PROVÁVEL (linhagem), NÃO IDENTIFICADA (arquivo exato) |
| PNAD (mercado de trabalho) | idem "principal" | T32-T38 | Múltiplos | 32-38 | CONFIRMADA (majoritariamente) |
| CAGED | idem "principal"; abas de estágio (`Ty`, `T4x`, `T43`, `T44`) apenas em "dieese", ocultas | T39-T45 | Múltiplos | 39-46 | CONFIRMADA (slides com gráfico) / POSSÍVEL (tabelas nativas) |
| Greves | não localizado no corpus (evidência técnica de abas `T50`,`T52`-`T54` em versão de arquivo ausente) | — | Nº de greves, categorias, reivindicações | 48-52 | NÃO IDENTIFICADA |
| Negociação coletiva / reajustes / pisos | não localizado como arquivo-fonte direto; correlato metodológico: `mediador - economicas 2023.xlsx` (ano-calendário 2023, estrutura de abas diferente) | — | Reajustes, pisos salariais | 53-57 | NÃO IDENTIFICADA (arquivo direto); PROVÁVEL apenas quanto à existência de metodologia recorrente |
