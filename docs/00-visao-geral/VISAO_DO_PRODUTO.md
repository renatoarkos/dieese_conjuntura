# DIEESE Conjuntura
## Plataforma de Inteligência Socioeconômica

## 1. Problema

O DIEESE produz, de forma contínua, análises de conjuntura econômica que dependem de um grande volume de dados dispersos em múltiplas fontes oficiais e institucionais — BCB, IBGE/SIDRA, Novo CAGED/MTE, FMI, CNI, FGV, Tesouro Nacional, entre outras. Hoje, a coleta, o tratamento e a atualização recorrente desses dados são realizados majoritariamente de forma manual, mês a mês, o que consome tempo considerável da equipe técnica em tarefas repetitivas de preparação em vez de análise.

Essa dispersão de fontes gera dificuldades adicionais: cada fonte tem sua própria periodicidade, metodologia, formato e calendário de divulgação, o que torna o cruzamento entre indicadores de diferentes origens trabalhoso e sujeito a inconsistências. A manutenção de séries históricas de longo prazo — essenciais para comparação, identificação de tendências e mudanças estruturais — exige atenção constante a revisões metodológicas e mudanças de base realizadas pelas próprias fontes.

Há também uma lacuna de rastreabilidade: sem um registro sistemático de qual dado veio de qual fonte, em qual data, sob qual metodologia e com quais transformações aplicadas, torna-se difícil auditar ou reproduzir uma análise anterior. O tempo gasto na preparação dos dados compete diretamente com o tempo disponível para a etapa que efetivamente agrega valor: transformar dado bruto em evidência analítica capaz de sustentar uma interpretação de conjuntura.

A necessidade central, portanto, é sistematizar de forma permanente e continuada — não pontual — o ciclo completo entre a coleta de dados econômicos e socioeconômicos e a produção de evidência analítica que apoie a análise de conjuntura do DIEESE.

## 2. Visão

A plataforma DIEESE Conjuntura deve ser concebida como uma infraestrutura permanente de inteligência socioeconômica, auditável e reproduzível — não como um dashboard convencional ou um produto de visualização isolado.

O princípio que orienta essa visão é a seguinte cadeia de transformação:

FONTES
→ DADOS
→ INFORMAÇÃO
→ EVIDÊNCIA
→ INTERPRETAÇÃO
→ ANÁLISE DE CONJUNTURA.

Cada etapa dessa cadeia deve ser rastreável e preservada, de modo que seja sempre possível voltar de uma interpretação até a fonte primária que a sustenta.

## 3. Objetivo geral

Construir uma plataforma capaz de coletar, tratar, armazenar, relacionar, explorar, visualizar e apoiar a interpretação de dados relevantes para a análise permanente da conjuntura econômica realizada pelo DIEESE.

## 4. Objetivos específicos

- Automação de coleta de dados junto às fontes oficiais e primárias.
- Integração de APIs de instituições nacionais e internacionais.
- Processamento de microdados quando aplicável.
- Manutenção de séries históricas de longo prazo, preservando comparabilidade e revisões.
- Construção e manutenção de um Catálogo Mestre de Indicadores.
- Produção de dashboards editoriais estruturados.
- Exploração multidimensional dos dados pelo usuário.
- Construção de tabelas dinâmicas.
- Aplicação de filtros e segmentações.
- Produção de visualizações (gráficos, mapas, tabelas).
- Investigação de relações econômicas previstas pela literatura.
- Produção de interpretações baseadas em evidências, nunca em suposições.
- Acompanhamento de calendário de divulgações oficiais.
- Preservação de rastreabilidade em todas as etapas do processo.
- Exportação de resultados e consultas.

## 5. Domínios econômicos

A plataforma deverá contemplar, entre outros, os seguintes domínios econômicos:

atividade econômica; crescimento; mercado de trabalho; emprego; desemprego; subutilização; informalidade; renda; salários; massa salarial; inflação; custo de vida; produção; indústria; serviços; comércio; consumo; investimento; produtividade; crédito; juros; política monetária; política fiscal; contas públicas; setor externo; distribuição de renda; desigualdade; desenvolvimento; proteção social; economia internacional; mercados financeiros.

Esta lista representa o ponto de partida do escopo temático e poderá ser ampliada ao longo do projeto.

## 6. Fontes

A plataforma deverá priorizar sempre fontes primárias e oficiais de dados econômicos e socioeconômicos, nacionais e internacionais, conforme já indicado nas instruções operacionais do repositório (CLAUDE.md).

A lista inicial de instituições consideradas — como DIEESE, IBGE/SIDRA, Banco Central do Brasil, Ministério do Trabalho e Emprego, Tesouro Nacional, Receita Federal, MDIC, Ipea, OIT/ILOSTAT, CEPAL, FMI, Banco Mundial, OCDE, BIS, FRED, entre outras — não deve ser tratada como exaustiva. Fontes privadas poderão complementar a análise quando necessário, desde que claramente identificadas como tal.

A definição detalhada, endpoint a endpoint, de cada fonte pertence a `docs/04-fontes/` e será construída progressivamente, sem se antecipar nesta etapa de visão.

## 7. Catálogo Mestre de Indicadores

O Catálogo Mestre de Indicadores deve ser concebido como a camada semântica central da plataforma — o vocabulário comum que conecta fontes, dados, indicadores e interpretações.

Cada indicador deverá, progressivamente, possuir:

- identificação;
- conceito;
- fonte;
- metodologia;
- periodicidade;
- unidade;
- abrangência;
- dimensões;
- histórico;
- transformações;
- atualização;
- relações com outros indicadores;
- relações teóricas;
- limitações;
- status de automação.

O preenchimento efetivo do Catálogo depende da análise dos materiais e das fontes, etapa que ainda não foi iniciada. Este documento apenas registra sua função estrutural na plataforma.

## 8. Biblioteca de Relações Econômicas

A plataforma deverá manter uma Biblioteca de Relações Econômicas destinada à investigação empírica de relações propostas pela teoria econômica, considerando tanto abordagens ortodoxas quanto heterodoxas.

A biblioteca deverá incluir inicialmente, entre outras:

- Curva de Phillips;
- Phillips com expectativas;
- Lei de Okun;
- Curva de Beveridge;
- Regra de Taylor;
- efeito Fisher;
- estrutura a termo dos juros;
- pass-through cambial;
- Marshall-Lerner;
- J-Curve;
- multiplicador keynesiano;
- acelerador;
- Kaldor-Verdoorn;
- relações kaleckianas;
- Goodwin;
- wage-led growth;
- profit-led growth;
- Prebisch-Singer;
- restrição externa de Thirlwall;
- Minsky;
- financeirização;
- wage curve;
- produtividade e salários;
- inflação de custos;
- inflação de demanda;
- conflito distributivo;
- expectativas e inflação.

Fica explícito que o sistema não deverá, em nenhuma hipótese, declarar automaticamente uma teoria econômica como verdadeira ou falsa. O objetivo da Biblioteca é verificar se existem evidências compatíveis com determinada relação para o período, a população, a especificação e os dados efetivamente analisados — nunca emitir veredito definitivo sobre a teoria em si.

## 9. Explorador de Dados

A plataforma deverá permitir, progressivamente, que o usuário:

- selecione indicadores;
- selecione períodos;
- selecione territórios;
- selecione dimensões;
- aplique filtros;
- aplique segmentações;
- combine séries;
- transforme séries;
- produza gráficos;
- produza mapas;
- produza tabelas;
- produza tabelas dinâmicas;
- exporte resultados;
- futuramente, salve consultas.

## 10. Dashboards editoriais

Dashboards editoriais são visualizações previamente estruturadas pela equipe técnica, com narrativa e seleção de indicadores definidas para comunicar uma leitura específica da conjuntura.

Eles se diferenciam do Explorador de Dados (seção 9), que oferece exploração livre e multidimensional pelo próprio usuário, sem uma narrativa pré-definida. Os dois modos deverão coexistir na plataforma, atendendo a necessidades distintas: comunicação editorial e investigação analítica autônoma.

## 11. Divulgações

A plataforma deverá contar com uma área dedicada — DIVULGAÇÕES — responsável por acompanhar os calendários oficiais de divulgação dos indicadores monitorados.

A visão futura desse módulo é aproximar progressivamente as seguintes etapas:

DIVULGAÇÃO PREVISTA
→ PUBLICAÇÃO DETECTADA
→ INGESTÃO
→ VALIDAÇÃO
→ ATUALIZAÇÃO
→ RECÁLCULO
→ INTERPRETAÇÃO.

Nenhuma data de divulgação deverá ser inventada; todas devem ser extraídas de calendários oficiais das próprias instituições produtoras.

## 12. Interpretação assistida

A plataforma deverá, futuramente, apoiar a produção de interpretações preliminares baseadas em evidências calculadas a partir dos dados — nunca substituir o julgamento técnico dos analistas do DIEESE.

Para isso, é fundamental manter clara a separação entre:

DADO
→ EVIDÊNCIA
→ HIPÓTESE
→ INTERPRETAÇÃO.

A interpretação assistida deverá ajudar a responder perguntas como:

- O que mudou?
- Quanto mudou?
- Como se compara historicamente?
- Houve aceleração ou desaceleração?
- Houve mudança de tendência?
- Quais componentes explicam a mudança?
- Quais outros indicadores se relacionam?
- Quais hipóteses econômicas são compatíveis?
- Quais interpretações alternativas existem?
- Quais são as limitações?

## 13. Princípios metodológicos

- Rastreabilidade de todo dado utilizado, da fonte até a interpretação final.
- Reprodutibilidade de toda transformação aplicada aos dados.
- Transparência sobre fontes, metodologias e limitações.
- Qualidade dos dados, com verificações sistemáticas.
- Preservação histórica de séries e de materiais originais.
- Pluralismo teórico, sem privilégio automático de uma escola de pensamento econômico.
- Documentação de decisões, fontes, indicadores e metodologias como fonte de verdade do projeto.
- Distinção clara entre associação estatística e causalidade.
- Distinção clara entre evidência e interpretação.

## 14. Usuários

Consideram-se, nesta fase inicial, os seguintes perfis de usuário da plataforma:

- técnicos;
- economistas;
- pesquisadores;
- analistas responsáveis pela análise de conjuntura.

Personas detalhadas ainda não foram construídas e não pertencem a esta etapa do Discovery.

## 15. Decisões ainda abertas

Ficam explicitamente registradas como NÃO decididas neste momento:

- stack tecnológica;
- backend;
- frontend;
- banco de dados definitivo;
- provedor de cloud;
- orquestrador;
- arquitetura final de componentes de IA;
- ferramenta definitiva de Business Intelligence;
- design final da interface.

Nenhuma dessas decisões deve ser antecipada por este documento ou por qualquer outro produzido nesta fase de Discovery.

## 16. Critério de evolução

A plataforma deverá evoluir de uma lógica que responde apenas:

“Qual é o valor?”

para uma lógica que responde:

“O que mudou?”
“Quanto mudou?”
“Como se compara historicamente?”
“Quem explica a mudança?”
“Com quais fenômenos se relaciona?”
“Que teorias ajudam a investigar esse comportamento?”
“Que evidências sustentam cada interpretação?”
“Quais interpretações alternativas existem?”
“O que será divulgado em seguida?”

## 17. Natureza deste documento

Este documento registra a VISÃO INICIAL do produto DIEESE Conjuntura e poderá evoluir ao longo da fase de Discovery, à medida que os materiais forem analisados, as fontes investigadas e os requisitos consolidados.

Possibilidades descritas aqui não são requisitos aprovados. Hipóteses técnicas mencionadas não são decisões arquiteturais. Qualquer decisão permanente deverá ser registrada separadamente, em sua devida instância (requisitos, arquitetura ou ADR), conforme estabelecido em CLAUDE.md.
