# Agentes — DIEESE Conjuntura

## Objetivo deste diretório

Este diretório reúne as instruções operacionais portáteis dos papéis especializados do projeto DIEESE Conjuntura, formalizados em `docs/03-metodologia/ARQUITETURA_AGENTES.md`. Cada arquivo aqui traduz um desses papéis em uma instrução reutilizável — algo que pode ser dado a um agente de IA (em qualquer ferramenta) para que ele atue consistentemente com o que o projeto já decidiu sobre esse papel.

## Agentes disponíveis

| Arquivo | Papel |
|---|---|
| `conjuntura-lead.md` | DIEESE Conjuntura Lead — coordenação multidisciplinar |
| `economista-conjuntura.md` | Economista de Conjuntura — interpretação econômica |
| `fontes-dados.md` | Especialista em Fontes & Dados — descoberta e validação de fontes |
| `metodologia-economica.md` | Especialista em Metodologia Econômica — consistência conceitual e estatística |
| `data-engineer.md` | Data Engineer — desenho e avaliação de engenharia de dados |

A descrição completa de cada papel — missão, responsabilidades, limites, diagrama de coordenação, padrões de colaboração e protocolo de conflitos — está em `docs/03-metodologia/ARQUITETURA_AGENTES.md`. Os arquivos deste diretório são a versão operacional, pronta para ser usada como instrução de um agente; `ARQUITETURA_AGENTES.md` é a versão de referência, que explica o porquê da arquitetura.

## Como utilizar

1. Escolha o papel adequado à tarefa (ou consulte o Lead, quando não estiver claro qual papel se aplica).
2. Forneça o conteúdo do arquivo correspondente como instrução do agente na ferramenta em uso (prompt de sistema, arquivo de configuração de agente, ou mecanismo equivalente).
3. O agente deve seguir, antes de qualquer tarefa relevante, a leitura obrigatória listada no início de cada arquivo — que inclui sempre `CLAUDE.md`, `docs/00-visao-geral/ESTADO_DO_PROJETO.md`, `docs/03-metodologia/PROTOCOLO_TRABALHO_IA.md`, `docs/03-metodologia/ARQUITETURA_AGENTES.md`, e os documentos específicos da tarefa.
4. O resultado do trabalho do agente deve ser registrado no repositório quando gerar conhecimento relevante e persistente (ver Definition of Done em cada arquivo), não apenas permanecer em uma conversa.

## Agentes são papéis, não memória

Os agentes descritos neste diretório **não são a memória principal do projeto**. Eles representam papéis especializados para execução de tarefas — não instâncias com memória própria, não uma fonte de verdade paralela, e não um substituto para a documentação do repositório. Um agente pode ser instanciado, usado e encerrado a qualquer momento, em qualquer ferramenta, sem perda de continuidade para o projeto, desde que seus resultados relevantes tenham sido devidamente registrados na documentação.

## CLAUDE.md e a documentação prevalecem

Em qualquer conflito aparente entre o que está escrito nos arquivos deste diretório e o que está registrado em `CLAUDE.md`, em `docs/03-metodologia/PROTOCOLO_TRABALHO_IA.md`, em `docs/03-metodologia/ARQUITETURA_AGENTES.md` ou em `docs/00-visao-geral/ESTADO_DO_PROJETO.md`, **prevalece a documentação do repositório**. Os arquivos deste diretório existem para operacionalizar essa documentação, nunca para substituí-la ou contradizê-la.

## Adaptação à sintaxe de cada ferramenta

Os arquivos aqui são escritos em markdown simples e neutro, deliberadamente portáteis entre Claude Cowork, Claude Code, Antigravity e ambientes futuros. Cada ferramenta pode exigir uma sintaxe própria para declarar um agente (por exemplo, um cabeçalho de configuração específico, um formato de arquivo particular, ou um mecanismo de registro de subagente). **O conteúdo destes arquivos pode e deve ser adaptado a essa sintaxe específica quando necessário** — o que não pode mudar, nessa adaptação, é o conteúdo substantivo: missão, responsabilidades, procedimento, limites e regras obrigatórias registrados em cada um.

## Versionamento

Qualquer alteração relevante nas instruções de um agente — mudança de missão, de responsabilidades, de procedimento, de limites ou das regras obrigatórias — deve ser versionada no repositório, com commit próprio e mensagem clara, assim como qualquer outra alteração de documentação relevante do projeto (`docs/03-metodologia/PROTOCOLO_TRABALHO_IA.md`, Seção 1 e Seção 5). Ajustes puramente de adaptação sintática a uma ferramenta específica (sem mudança de conteúdo substantivo) não precisam necessariamente ser registrados aqui, mas alterações de conteúdo sim.
