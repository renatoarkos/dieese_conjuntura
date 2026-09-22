# Oportunidades Preliminares de Automação — Materiais P1

## 1. Objetivo e critério de classificação

Classificação preliminar de atividades observadas nos materiais P1, sem qualquer escolha de tecnologia e sem qualquer implementação. Cada atividade foi classificada em uma das quatro categorias abaixo, com base exclusivamente em evidências encontradas nos materiais (fórmulas, fontes citadas, padrões de dados, notas dos slides):

- **A — forte candidata à automação**: fonte identificável, formato estruturado, transformação já expressa em fórmula/regra clara.
- **B — parcialmente automatizável**: parte do processo é estruturado (fonte, formato), mas há etapa de julgamento, consolidação manual de múltiplas fontes, ou formato de origem não identificado nos materiais.
- **C — exige julgamento analítico humano**: envolve escolha editorial, interpretação, ou seleção do que destacar — não é, por natureza, uma atividade mecânica.
- **D — informação insuficiente**: não há evidência suficiente nos materiais P1 para classificar com segurança.

## 2. Classificação por atividade

### 2.1 Obtenção de dados

| Fonte / atividade | Classificação | Evidência |
|---|---|---|
| Séries do BCB/SGS com código citado explicitamente (aba T16) | **A** | Códigos de série citados célula a célula (ex.: "20728", "22019", "20741", "20742") — compatíveis com consulta direta à API pública do SGS/BCB. |
| Tabelas do IBGE/SIDRA com número de tabela citado (T3, T5, T6, T9, T10, T11, T22, T32a-T38) | **A** | Números de tabela SIDRA citados explicitamente nos títulos das abas (ex.: Tabela 5932, 8881, 4093, 4094, 4097, 6461, 5440, 21777, 7063) — compatíveis com consulta direta à API pública do SIDRA/IBGE. |
| Novo CAGED (T39-T45) | **A** | Fonte única e explícita ("Novo Caged – MTE/SEPRT") em todas as abas do bloco; MTE disponibiliza bases estruturadas para este indicador. |
| Dado recebido por e-mail (aba T21, "Fonte: INDATEND (PH/email)") | **D** | Mecanismo de chegada do dado não é uma fonte pública/API — não há evidência de que exista uma alternativa automatizável sem contato direto com a instituição/pessoa. |
| Dados do Sistema de Acompanhamento de Greves (SAG) | **B** | É um sistema próprio do DIEESE (não uma fonte externa) — a automação dependeria de acesso direto ao sistema/base do SAG, não identificado nos materiais P1. |
| Dados do Mediador/MTE (negociação coletiva) | **B** | Fonte institucional identificada, mas os materiais indicam "Consulta em [data]" — sugerindo extração manual pontual, não uma API confirmada nos materiais. |
| Preços de combustíveis (ANP, Petrobrás, IPEADATA) | **B** | Fontes com portais/APIs públicas conhecidas em geral, mas sem série ou endpoint citado especificamente no material — não deve ser presumido sem confirmação. |
| Estimativas de mercado (BCB - Sistema de Expectativas) | **A** | Fonte pública com série amplamente documentada (fora do escopo confirmar endpoint nesta rodada, mas citada explicitamente no material: aba T23/T24). |

### 2.2 Atualização de período

| Atividade | Classificação | Evidência |
|---|---|---|
| Extensão de séries mensais/trimestrais já estruturadas em coluna (maioria das abas de dado bruto) | **A** | Estrutura tabular consistente (data em uma coluna, valor em outra) é compatível com acréscimo automatizado de novas linhas a cada divulgação. |
| Atualização de estimativas/projeções (T23, T24 — "estimativas elaboradas em 28-29/11/2025") | **C** | Estimativas de curto prazo (nowcasting) envolvem escolha de metodologia/premissas — não é apenas inserir um novo dado observado. |

### 2.3 Transformação / cálculo

| Atividade | Classificação | Evidência |
|---|---|---|
| Cálculo de variação percentual período a período | **A** | Fórmula simples e recorrente (`=D9/D8-1`), já presente na planilha (T18, T36). |
| Encadeamento de número-índice (acumulado em 12 meses) | **A** | Padrão `PRODUCT()` recorrente e bem definido (T23, T24). |
| Cálculo de juro real (efeito Fisher) | **A** | Fórmula fixa e documentada dentro da própria aba (T14). |
| Médias móveis / médias trimestrais | **A** | Fórmula `AVERAGE()` sobre intervalos fixos (T26). |
| Consolidação de múltiplas fontes de inflação em uma única tabela (T21: INDATEND, SIDRA, Portal FGV) | **B** | Estrutura tabular já existe, mas a escolha de quais fontes incluir e como conciliá-las é editorial. |
| Deflacionamento de rendimento pelo deflator de Nota Técnica própria do DIEESE (slide 40) | **B** | Metodologia documentada (nota técnica), mas essa nota não está nos materiais P1 — a regra existe, porém não está totalmente visível aqui. |

### 2.4 Consolidação

| Atividade | Classificação | Evidência |
|---|---|---|
| Agregação de subcategorias em categoria maior via fórmula (T35: `SUM()` de posições na ocupação) | **A** | Regra de composição já expressa em fórmula clara e replicável. |
| Tabela auxiliar derivada de outra aba via referência cruzada (T45 a partir de T44; T17 a partir de T14) | **A** | Referência direta de célula a célula entre abas — mecanismo replicável. |
| Consolidação de dados de greves/negociação coletiva diretamente em tabelas do PowerPoint | **D** | Não há aba de origem identificada nos materiais P1 — não é possível avaliar o quão estruturado é o processo anterior a essa consolidação. |

### 2.5 Geração de gráfico

| Atividade | Classificação | Evidência |
|---|---|---|
| Gráficos já embutidos nas abas do Excel, associados diretamente à tabela de dados da mesma aba | **A** | 47 gráficos nativos identificados nas 47 abas do arquivo "principal" — padrão consistente aba->gráfico. |
| Transposição do gráfico do Excel para o slide correspondente | **B** | Correspondência temática forte entre gráficos do Excel e do PowerPoint, mas não foi confirmado neste Discovery se o vínculo é dinâmico (linked object) ou uma cópia estática — ver `FLUXO_ATUAL_CONJUNTURA.md`, seção 2.4. |

### 2.6 Montagem da apresentação

| Atividade | Classificação | Evidência |
|---|---|---|
| Inserção de números-manchete isolados no slide (ex.: "R$ 987 bilhões", "536 greves") | **C** | Escolha editorial de destaque — exige julgamento sobre o que é noticiável no período. |
| Redação de notas metodológicas nos slides (ex.: explicação de deflator, de composição de categoria) | **C** | Redação textual explicativa, não mecânica. |
| Ordenação e agrupamento dos slides em blocos temáticos com slides de título (30, 47) | **C** | Decisão editorial sobre estrutura narrativa do documento. |
| Preenchimento de tabelas nativas do PowerPoint com dados sem vínculo de planilha identificado (greves, negociação coletiva) | **D** | Sem visibilidade da etapa anterior (ver 2.4 acima) — não é possível avaliar se a digitação em si é evitável sem saber onde os dados residem antes disso. |

### 2.7 Interpretação

| Atividade | Classificação | Evidência |
|---|---|---|
| Slide de síntese textual do trimestre ("Alguns números", slide 35) | **C** | Seleção e verbalização de quais comparações destacar (sexo, raça, formalidade) — julgamento analítico. |
| Título com leitura de tendência de longo prazo (slide 52, sindicalização) | **C** | Requer conhecimento de série histórica além do período mostrado no slide — julgamento analítico, não cálculo mecânico. |

## 3. Síntese

| Categoria | Nº de atividades listadas | Predominância |
|---|---|---|
| A — forte candidata | 11 | Obtenção de dados de fontes com identificador citado (BCB/SGS, SIDRA, CAGED), cálculos de transformação já expressos em fórmula, geração de gráfico dentro do Excel |
| B — parcialmente automatizável | 6 | Fontes institucionais sem endpoint confirmado, consolidação de múltiplas fontes, transposição Excel -> PowerPoint |
| C — exige julgamento humano | 6 | Toda a camada de montagem editorial da apresentação e de interpretação textual |
| D — informação insuficiente | 4 | Tudo relacionado ao bloco "Greves e Negociações Coletivas" (sem planilha de origem identificada) e a uma fonte recebida por e-mail |

**Leitura geral (INFERÊNCIA, não uma recomendação de implementação)**: o material sugere que a camada de *obtenção e tratamento numérico* dos indicadores dos blocos Macroeconomia, Monetário, Inflação, PNAD e CAGED já segue um padrão estruturado e potencialmente automatizável (categoria A), enquanto a camada de *montagem narrativa da apresentação e interpretação* (categorias C) é, por natureza, dependente de julgamento técnico humano — consistente com o princípio de `VISAO_DO_PRODUTO.md` de que a interpretação assistida deve apoiar, não substituir, o julgamento dos analistas do DIEESE. O bloco de greves/negociação coletiva (categoria D) é o principal ponto cego desta rodada de Discovery: não há, nos materiais P1, visibilidade suficiente sobre sua cadeia de produção para classificá-lo com confiança.

## 4. Limitações

- Esta classificação não avalia esforço, custo ou viabilidade técnica de implementação — apenas a natureza estrutural/editorial da atividade observada.
- Nenhuma tecnologia foi considerada ou recomendada nesta rodada, conforme instrução da tarefa e da fase DISCOVERY do projeto (`CLAUDE.md`).
- Atividades classificadas como D podem, na prática, ser tão automatizáveis quanto as classificadas como A — a classificação D reflete apenas a insuficiência de evidência nos materiais P1 lidos, não uma característica real da atividade.
