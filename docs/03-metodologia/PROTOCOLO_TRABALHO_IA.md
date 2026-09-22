# Protocolo de Trabalho com IA — DIEESE Conjuntura

## 1. Fonte persistente de verdade

O repositório Git e sua documentação versionada constituem a fonte persistente de verdade do projeto.

Conversas com ferramentas de IA constituem contexto operacional auxiliar e não substituem a documentação persistente.

Decisões relevantes tomadas durante conversas deverão ser incorporadas à documentação apropriada quando se tornarem permanentes.

## 2. CLAUDE.md

Todo agente ou ambiente com acesso ao repositório deverá ler CLAUDE.md antes de realizar tarefa relevante.

As instruções persistentes ali registradas prevalecem sobre inferências feitas apenas a partir da estrutura dos arquivos.

## 3. Estado do projeto

Antes de iniciar nova sessão relevante de trabalho, consultar:

docs/00-visao-geral/ESTADO_DO_PROJETO.md

Esse documento deve permitir compreender rapidamente:

- fase atual;
- trabalho concluído;
- trabalho em andamento;
- próximas etapas;
- decisões consolidadas;
- decisões abertas;
- bloqueios.

## 4. Divisão preferencial de responsabilidades

### Claude Cowork

Utilização preferencial para:

- Discovery;
- pesquisa;
- análise documental;
- levantamento e validação de fontes;
- planejamento;
- documentação;
- organização de conhecimento;
- coordenação de tarefas extensas;
- preparação de especificações.

### Claude Code

Utilização preferencial para:

- implementação;
- engenharia de dados;
- integrações;
- pipelines;
- testes;
- banco de dados;
- backend;
- frontend;
- refatoração;
- debugging;
- manutenção do código.

### Antigravity

Utilização preferencial como:

- ambiente de desenvolvimento;
- ambiente de trabalho assistido por agentes;
- apoio à execução e coordenação de tarefas de engenharia;
- interface de desenvolvimento quando aplicável.

Essa divisão é preferencial e não representa uma limitação absoluta das capacidades de cada ferramenta.

## 5. Git

Antes de realizar alterações relevantes:

1. verificar git status;
2. compreender alterações já existentes;
3. identificar arquivos não versionados;
4. evitar sobrescrever trabalho pendente;
5. realizar alterações pequenas e rastreáveis;
6. executar testes aplicáveis;
7. revisar o diff;
8. realizar commits coerentes e semanticamente delimitados.

Não realizar operações destrutivas no histórico Git sem autorização humana explícita.

## 6. Concorrência entre agentes

Evitar que dois agentes alterem simultaneamente os mesmos arquivos sem coordenação.

Quando houver trabalho paralelo, preferir:

- tarefas independentes;
- arquivos diferentes;
- branches diferentes quando apropriado;
- escopos claramente delimitados.

Antes de modificar arquivo potencialmente trabalhado por outro agente, verificar o estado do repositório.

## 7. Materiais originais

materiais/originais/ constitui corpus documental de referência e deve ser tratado como SOMENTE LEITURA, salvo autorização humana explícita.

O fato de esse diretório estar provisoriamente ignorado pelo Git NÃO autoriza:

- alteração;
- exclusão;
- renomeação;
- movimentação;
- sobrescrita.

A estratégia definitiva de armazenamento e versionamento dos materiais binários ainda é uma decisão aberta.

## 8. Decisões arquiteturais

Decisões arquiteturais relevantes deverão ser registradas em:

docs/08-decisoes-adr/

Cada decisão deverá registrar, quando aplicável:

- contexto;
- problema;
- alternativas consideradas;
- decisão;
- justificativa;
- consequências;
- status.

Hipóteses e possibilidades não devem ser apresentadas como decisões aprovadas.

## 9. Pesquisa

Resultados relevantes de pesquisa deverão ser persistidos em:

research/

ou:

docs/

conforme sua natureza.

Pesquisa exploratória, notas e evidências intermediárias devem preferencialmente permanecer em research/.

Conhecimento consolidado do projeto deverá migrar para docs/ quando apropriado.

## 10. Implementação

Não implementar funcionalidades substanciais antes de existir compreensão suficiente:

- do problema;
- do requisito;
- dos dados;
- da fonte;
- das regras metodológicas;
- das dependências relevantes.

Durante a fase de Discovery, desenvolvimento substancial depende de autorização humana explícita.

## 11. Handoff entre ambientes e agentes

Ao transferir trabalho entre Cowork, Claude Code, Antigravity ou outro agente, registrar quando necessário:

- tarefa executada;
- estado atual;
- arquivos alterados;
- testes realizados;
- decisões tomadas;
- pendências;
- riscos;
- próximo passo recomendado.

O arquivo:

docs/00-visao-geral/ESTADO_DO_PROJETO.md

deverá ser atualizado após marcos relevantes, e não necessariamente após cada pequena operação.

## 12. Autoridade humana

Dependem de validação humana explícita:

- mudanças relevantes de escopo;
- decisões arquiteturais de alto impacto;
- operações destrutivas;
- exclusão de dados;
- alteração de materiais originais;
- mudanças relevantes na metodologia econômica;
- decisões que comprometam a rastreabilidade ou reprodutibilidade.

## 13. Segurança

Nenhum agente deverá registrar no repositório:

- senhas;
- tokens;
- chaves privadas;
- API keys reais;
- credenciais;
- secrets.

.env.example poderá conter apenas nomes e documentação de variáveis, nunca valores secretos reais.

## 14. Discovery antes da implementação

Enquanto o projeto estiver formalmente na fase DISCOVERY, o objetivo prioritário será compreender:

- materiais;
- indicadores;
- fontes;
- metodologias;
- relações econômicas;
- necessidades dos usuários;
- requisitos.

A arquitetura tecnológica deverá decorrer dessas descobertas e requisitos, e não precedê-los sem justificativa.

## 15. Rastreabilidade

Sempre que possível, deverá ser possível reconstruir:

FONTE
→ DADO ORIGINAL
→ TRANSFORMAÇÃO
→ INDICADOR
→ EVIDÊNCIA
→ VISUALIZAÇÃO
→ INTERPRETAÇÃO.

Esse princípio deverá orientar posteriormente a arquitetura de dados da plataforma.
