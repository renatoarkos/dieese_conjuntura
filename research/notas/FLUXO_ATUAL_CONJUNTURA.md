# Fluxo Atual de Produção da Conjuntura — Reconstrução a partir dos Materiais P1

## 1. Objetivo

Reconstruir, exclusivamente a partir de evidências encontradas nos três materiais P1, o fluxo aparente de produção da apresentação de conjuntura, da fonte primária até a interpretação apresentada. Cada afirmação é classificada como:

- **EVIDÊNCIA DIRETA**: observada diretamente em uma fórmula, célula, referência de arquivo ou texto do material.
- **INFERÊNCIA**: dedução razoável a partir de padrões observados, mas não comprovada diretamente no material.

## 2. Fluxo reconstruído

```
FONTE (oficial/administrativa)
   -> PLANILHA (Apresentação_Conjuntura_4T_2025.xlsx, uma aba por tabela/tema)
   -> TRATAMENTO (fórmulas dentro da própria planilha)
   -> INDICADOR (célula/coluna calculada, ou referência cruzada a outra aba)
   -> GRÁFICO/TABELA (objeto gráfico nativo do Excel, na mesma aba)
   -> APRESENTAÇÃO (slide correspondente em ATR_Conjuntura_2025.12.pptx)
   -> INTERPRETAÇÃO (texto/título/nota do slide, quando presente)
```

Esse fluxo se aplica com boa evidência aos blocos Macroeconomia, Estatísticas Monetárias, Inflação, PNAD e Novo CAGED (juntos, cerca de 47 dos 58 slides). **Não se aplica**, pelo menos não de forma rastreável nos materiais P1, ao bloco "Greves e Negociações Coletivas" (11 slides), cujos dados não foram localizados em nenhuma das 47 abas do Excel "principal" nem nas 54 abas do Excel "dieese" — ver Seção 5.

### 2.1 FONTE -> PLANILHA

**EVIDÊNCIA DIRETA**: quase todas as abas do Excel "principal" terminam com uma linha "Fonte: ..." citando a instituição de origem (IBGE, BCB, CNI, Novo Caged/SEPRT-ME, SICONFI, FMI, PEIC etc. — catálogo completo em `INVENTARIO_INDICADORES_P1.md`). Em pelo menos uma aba (T16), os códigos de série do SGS/BCB são citados célula a célula (ex.: "20728 - Taxa média de juros das operações de crédito..."), permitindo rastreabilidade direta até a série oficial.

**INFERÊNCIA**: não há, nos materiais lidos, evidência de como os dados chegam da fonte até a planilha (download manual, API, cópia de relatório PDF etc.) — apenas o resultado já dentro da planilha. A menção "Fonte: INDATEND (PH/email)" na aba T21 é a única pista textual sobre um mecanismo de chegada de dado (recebimento por e-mail), e é **EVIDÊNCIA DIRETA** de que pelo menos uma fonte não chega por meio público/automatizável sem contato direto com a instituição.

### 2.2 PLANILHA -> TRATAMENTO -> INDICADOR

**EVIDÊNCIA DIRETA** (fórmulas observadas diretamente, sem cópia extensiva de conteúdo, apenas amostras):

| Aba | Nº de fórmulas | Padrão observado | Interpretação técnica |
|---|---|---|---|
| T19 | 1.169 | `=1+(AA5/100)` | conversão de variação percentual em fator multiplicativo, base para número-índice |
| T23 | 310 | `=PRODUCT(C3:C6)` | encadeamento de índice (acumulado), técnica padrão para "acumulado em 12 meses" a partir de variações mensais |
| T24 | 299 | mesmo padrão de T23 | idem, para outro indicador de inflação |
| T18 | 142 | `=(C63/C62)` | variação percentual período a período |
| T14 | 176 | `=((1+B4/100)/(1+C4/100)-1)*100` | cálculo de juro real (efeito Fisher: taxa nominal deflacionada pela inflação) |
| T35 | 179 | `=SUM(E6,H6,N6,O6)` | agregação/composição de subcategorias em uma categoria maior |
| T36 | 73 | `=D9/D8-1` | variação percentual simples |
| T26 | 71 | `=AVERAGE(B2:B4)` | média móvel/trimestral |
| T17 | 11 | `=T14!B102` | referência cruzada entre abas (T17 consome resultado calculado em T14) |
| T45 | 24 | `=T44!B6` | referência cruzada — T45 é tabela auxiliar derivada de T44, não fonte primária própria |

Essas fórmulas demonstram que o tratamento (cálculo de variação, número-índice acumulado, juro real, médias móveis, composição de categorias) ocorre **dentro da própria planilha**, não em uma etapa externa antes dela. Isso é relevante para a Frente G (oportunidades de automação): o "motor de cálculo" já está, em parte, implícito nas fórmulas do Excel, e poderia orientar a lógica de transformação de uma futura camada ANALYTICS da plataforma.

**INFERÊNCIA**: como a leitura foi feita com `data_only=True` para os valores e `data_only=False` apenas para localizar fórmulas (sem copiar a totalidade das fórmulas de cada aba), não é possível afirmar que 100% das transformações estejam cobertas por essa amostra — apenas que o padrão observado nas abas mais densas é consistente e recorrente.

### 2.3 INDICADOR -> GRÁFICO/TABELA (dentro do Excel)

**EVIDÊNCIA DIRETA**: contagem de objetos gráfico por aba (`ws._charts`) mostra que a maioria das 47 abas do arquivo "principal" já contém ao menos 1 gráfico nativo do Excel associado à tabela de dados da própria aba (ex.: T3, T4b, T19, T32b têm entre 1 e 3 gráficos cada). Isso indica que a visualização já é montada dentro da planilha, não apenas no PowerPoint.

### 2.4 GRÁFICO/TABELA -> APRESENTAÇÃO

> **Atualização — Rodada 2 (Validação Técnica):** a pergunta técnica acima foi respondida por inspeção direta do OOXML dos 47 gráficos do `.pptx` (ver `VALIDACAO_TECNICA_P1.md`, Frente D). O que era INFERÊNCIA passa a ser, para a maior parte dos gráficos, **EVIDÊNCIA DIRETA**:

**EVIDÊNCIA DIRETA**: 43 dos 47 gráficos do PowerPoint são **vinculados** (`TargetMode="External"` em `ppt/charts/_rels/chartN.xml.rels`, com fórmula de série apontando para uma aba nomeada) a um arquivo externo — majoritariamente o próprio arquivo "principal" (`.../Planilhas Definitivas/2025.4T/Apresentação_Conjuntura_4T_2025.xlsx"`), com duas exceções pontuais (slide 29: combustíveis; slide 31: ICT) que apontam para arquivos externos específicos não presentes no corpus. Isso não são cópias estáticas — são objetos com vínculo técnico vivo (embora "congelado" no estado da última atualização feita em edição, como é o comportamento padrão de gráficos vinculados no PowerPoint/Excel).

**EVIDÊNCIA DIRETA**: 2 gráficos (slides 28 e 36) são **incorporados**, não vinculados — os dados estão congelados dentro de um workbook Excel mínimo embutido no próprio `.pptx`, sem vínculo vivo com nenhum arquivo externo.

**EVIDÊNCIA DIRETA**: 2 gráficos (slides 3 e 53) são **estáticos/nativos do PowerPoint**, sem nenhuma origem em planilha rastreável a partir do próprio arquivo.

**EVIDÊNCIA DIRETA**: pelo menos 8 slides (49, 51, 54, 55, 56, 57, além de 42, 43 no bloco CAGED) contêm **tabelas nativas do PowerPoint** com dados digitados/colados diretamente no slide, sem qualquer aba de origem localizada — isso é, por definição, uma etapa manual de montagem de apresentação que não depende de (e não está vinculada a) nenhuma planilha auditada nesta rodada.

### 2.5 APRESENTAÇÃO -> INTERPRETAÇÃO

Ver `ANALISE_APRESENTACAO_CONJUNTURA_2025_12.md`, Seção 4, para o detalhamento completo. Em síntese: a esmagadora maioria dos slides apresenta dado com fonte citada, sem interpretação causal textual; um pequeno número de slides (17, 35, 38, 51, 52) contém números-manchete ou texto corrido com leitura editorial explícita, sendo o slide 52 (sindicalização) o único com uma afirmação de tendência de longo prazo não sustentada pelos dados visíveis no próprio slide.

## 3. Pontos de possível retrabalho identificados

- **Duplicidade aparente entre slides 55 e 56** (mesmo cabeçalho de tabela, "Negociações por categoria — comparação com INPC") — pode indicar montagem manual por cópia de slide sem remoção do anterior, ou duas visões complementares não diferenciadas no texto.
- **Slides 43 e 44** têm títulos quase idênticos ("Evolução do saldo por grupamento de atividades econômicas") com a mesma nota de rodapé ("Outras = imobiliárias, profissionais e administrativas") — possível cópia de slide com alteração incompleta do texto, ou dois recortes setoriais (indústria/serviços) que não ficaram claramente diferenciados nos textos capturados.
- **Divergência de conteúdo na aba T14** entre as cópias "principal" e "dieese" (ver `COMPARACAO_EXCEL_P1.md`) sugere que ao menos uma edição/teste não foi sincronizada entre as duas cópias do arquivo-base — um risco de retrabalho ou de uso inadvertido da versão desatualizada.
- **Bloco de "Cesta Básica" (T27-T28) e "Greves e Negociações Coletivas"**, referenciados na aba `Sumário` ou aparecendo na apresentação, mas sem aba correspondente encontrada no Excel "principal" — indica que parte do fluxo de produção passa por fora deste arquivo (outra planilha não incluída nos materiais P1, ou lançamento direto na apresentação).

## 4. Relações econômicas identificadas (Frente H)

### 4.1 Relações explícitas no material

Nenhum slide ou aba afirma textualmente uma relação causal entre dois indicadores econômicos distintos (ex.: nenhuma frase do tipo "a queda do PIB causou o aumento do desemprego"). O material se limita a apresentar indicadores lado a lado ou em sequência temática, sem declarar mecanismo causal. Duas exceções parciais, ainda assim sem linguagem causal:

- **Slide 26** (PIB trimestral x Selic — média trimestral, 2008-2025): apresenta as duas séries no mesmo gráfico, o que é uma prática consistente com a investigação de uma relação de política monetária e atividade (aproximação a uma leitura de transmissão da política monetária sobre o produto), mas **sem qualquer teste estatístico, defasagem ou texto interpretativo** — é uma justaposição visual, não uma relação testada.
- **Slide 14 / aba T14** (Selic, IPCA e taxa de juros real): a fórmula de cálculo do juro real, `=((1+nominal)/(1+inflação)-1)`, é a aplicação direta do **efeito Fisher** (relação entre taxa nominal, taxa real e inflação esperada/observada) — mas o material aplica a fórmula como definição contábil, não como uma relação testada empiricamente com dados e especificação (ex.: não há regressão, não há teste de causalidade).

### 4.2 Relações candidatas para investigação futura

A partir do conjunto de indicadores presentes no material (não do texto do material, que não sugere nenhuma delas explicitamente), a biblioteca de relações econômicas de `VISAO_DO_PRODUTO.md` (seção 8) oferece candidatas plausíveis para investigação futura, quando a plataforma alcançar a fase de motor analítico:

| Relação candidata | Indicadores presentes no material que a tornariam testável | Observação |
|---|---|---|
| Efeito Fisher / estrutura de juros | Selic, IPCA, juros real (T14) | Já há cálculo contábil do juro real no material — mas não um teste da relação em si |
| Curva de Phillips / Phillips com expectativas | Taxa de desocupação (PNAD), IPCA/INPC (T19-T24) | Ambas as séries presentes nos materiais P1, mas em abas/fontes diferentes, nunca cruzadas no material |
| Lei de Okun | PIB (T3-T7b), taxa de desocupação (T32a/T32b) | Ambas presentes, nunca cruzadas no material |
| Regra de Taylor | Selic (T14/T26), IPCA (T19) | Presentes, não cruzadas nesta forma |
| Salário real e produtividade | Rendimento médio real (T38), sem indicador de produtividade nos materiais P1 | Produtividade ausente — relação não testável apenas com os materiais P1 |
| Conflito distributivo / inflação de custos | Reajustes salariais vs. INPC (slides 53-55), IPCA/INPC | Presentes, mas apenas como comparação direta de dois números, não como teste de relação |
| Pass-through cambial | Taxa de câmbio (T11), IPCA (T19) | Ambas presentes, nunca cruzadas no material |

**Importante**: a listagem acima identifica apenas que os *indicadores de entrada* para essas relações estão total ou parcialmente presentes nos materiais P1 — não constitui, de forma alguma, um teste, uma evidência ou uma afirmação de que a relação se verifica para este período ou especificação. Qualquer teste efetivo exigirá planejamento metodológico próprio (estacionariedade, defasagens, quebras estruturais etc., conforme `CLAUDE.md`), fora do escopo desta rodada de Discovery.

## 5. O que fica fora do fluxo reconstruído

O bloco "Greves e Negociações Coletivas" (SAG, Mediador/MTE) não tem, nos materiais P1, uma planilha de origem identificada. Isso quebra o fluxo FONTE→PLANILHA→...→APRESENTAÇÃO para esses 11 slides: a evidência disponível permite apenas concluir FONTE (SAG/Mediador) → APRESENTAÇÃO diretamente, sem visibilidade sobre a etapa de tratamento. Essa é uma lacuna real de rastreabilidade dentro do escopo dos materiais P1 — não necessariamente uma lacuna no processo real do DIEESE, que pode manter essas planilhas em outro arquivo não incluído nesta rodada.

## 6. Limitações

- Este fluxo foi reconstruído por inferência de padrões (nomes de aba, fórmulas, fontes citadas, correspondência temática com slides) — não por rastreamento técnico de vínculos de dados entre arquivos (o que exigiria inspecionar relações OOXML internas, fora do escopo desta rodada).
- Não foi possível confirmar se os gráficos do PowerPoint são objetos vinculados ao Excel ou cópias estáticas.
- A reconstrução cobre os materiais P1; não há garantia de que o processo real do DIEESE siga exatamente esse fluxo fora destes três arquivos.

## 7. Adendo — Rodada 2 (Validação Técnica): Greves, Negociação Coletiva e Cesta Básica

- **Cesta básica (slides 27-29):** o bloco tem origem identificável com boa confiança. A série "Salário Mínimo × Cesta Básica (São Paulo)", elaboração própria DIEESE, existe na aba `T27` do arquivo "dieese" (ausente do "principal") e em um arquivo dedicado versionado trimestralmente no corpus (`SM e Cesta desde 1979[...].xlsx`), com dados até a mesma data de referência (jun/2025). O Sumário de ambos os arquivos P1 já declarava esse bloco ("Cesta Básica | T27-T28"), o que agora fica explicado: a aba existiu e existe em "dieese", mas foi removida de "principal".
- **Combustíveis (slide 29) e ICT (slide 31):** têm arquivo-fonte nomeado tecnicamente via vínculo do gráfico (`20251127 - Preços combustíveis.xlsx` e `ICT - Brasil - PNAD Continua - 202503.xls`, respectivamente), mas nenhum dos dois arquivos está presente no corpus de 339 materiais. Arquivos correlatos da mesma família temática (`Preços combustíveis histórico.xlsx`, `ICT - Dieese - 202302.xls`) foram localizados no corpus e confirmam a linhagem metodológica, sem serem o arquivo exato.
- **Greves e Negociação Coletiva (slides 47-57):** nenhum arquivo-fonte foi localizado no corpus de 339 materiais. Há, porém, evidência técnica direta (fórmulas de série dos gráficos dos slides 48, 50, 51 e 52) de que as abas de origem (`T50`, `T52`, `T53`, `T54`) existem em uma versão do arquivo de mesmo nome/linhagem de "principal", mais completa do que qualquer uma das duas cópias P1 disponíveis (que vão até `T45`). Um arquivo correlato de metodologia (`mediador - economicas 2023.xlsx`, ano-calendário 2023, estrutura de abas diferente) foi localizado e demonstra que o DIEESE tem um processo recorrente para produzir painéis de negociação coletiva a partir do sistema Mediador/MTE — mas não é o arquivo-fonte direto identificado tecnicamente.

Detalhamento completo em `VALIDACAO_TECNICA_P1.md` (Frentes F e G).
