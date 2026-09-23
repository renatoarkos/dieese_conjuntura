# Visão de Diferencial Competitivo e Benchmark de Portais — Backlog

## Natureza deste documento

Registro de uma diretriz de produto dada pelo responsável do projeto em 2026-09-22, para não se perder entre o trabalho operacional de Discovery de Fontes. **Não é um requisito detalhado nem uma decisão de arquitetura** — é uma diretriz de ambição a ser desdobrada em requisitos concretos quando o projeto avançar da fase DISCOVERY para REQUISITOS.

## O que foi dito

> "Meu objetivo é construir o melhor portal de dados de conjuntura do país, apresentando todos os nossos objetivos, trazendo algo nunca visto nos portais de dados do Brasil. Futuramente faça um benchmark em todos os principais sites do país para posicionar o nosso e mostrar nossos diferenciais."

## Interpretação (não deve ser tratada como requisito fechado)

- A plataforma DIEESE Conjuntura não deve ser apenas funcionalmente equivalente a outros portais de dados socioeconômicos existentes no Brasil — deve buscar diferenciação real.
- Isso é consistente com os princípios já registrados em `docs/00-visao-geral/VISAO_DO_PRODUTO.md` (rastreabilidade ponta a ponta, distinção dado/evidência/hipótese/interpretação, Explorador de Dados + Dashboards editoriais coexistindo, interpretação assistida) — a ambição aqui é que esses princípios, combinados, resultem em algo que hoje não existe nos portais brasileiros equivalentes.

## Tarefa futura registrada: Benchmark de portais de dados

**Explicitamente marcada como "futuramente" pelo responsável do projeto — não deve ser executada agora.** Quando chegar a hora (provavelmente na fase REQUISITOS ou ARQUITETURA, com mais clareza sobre o que a plataforma vai efetivamente oferecer), realizar um benchmark comparativo dos principais portais de dados socioeconômicos do Brasil, cobrindo, no mínimo:

### Candidatos a benchmark (lista inicial, não exaustiva — a confirmar no momento da execução)

- **IBGE/SIDRA** e o novo portal de dados do IBGE — referência técnica de disseminação, mas sem camada de interpretação.
- **IPEADATA** — agregador histórico de séries de múltiplas fontes.
- **Banco Central — Dados Abertos / SGS / Olinda** — referência de API pública bem documentada.
- **Portal Brasileiro de Dados Abertos (dados.gov.br)** — referência institucional federal (já identificado, neste projeto, como tendo limitações de acesso via API sem chave).
- **Painéis de outras entidades de pesquisa/sindicais** (ex.: DIEESE atual, FGV/IBRE, outros institutos de pesquisa econômica com dashboards públicos).
- Outros portais setoriais relevantes a identificar no momento (ex.: Boletim Focus do BC, painéis de emprego do MTE/PDET).

### O que o benchmark deve avaliar (proposta inicial, a refinar)

- Cobertura temática e profundidade histórica.
- Rastreabilidade fonte → dado → indicador (poucos portais brasileiros expõem isso claramente).
- Distinção entre dado bruto e interpretação (a maioria dos portais existentes só expõe dado).
- Qualidade da experiência de exploração de dados (filtros, cruzamentos, exportação).
- Frequência e transparência de atualização / calendário de divulgação.
- Acessibilidade técnica (existência de API, documentação, licença de uso dos dados).
- Qualquer recurso de "interpretação assistida" ou leitura de conjuntura já oferecido por concorrentes (esperado: pouco ou nenhum, dado o histórico do setor — mas deve ser verificado, não presumido).

### Responsável sugerido

Papel Lead, com apoio do Economista de Conjuntura (para avaliar relevância analítica dos concorrentes) — não é uma tarefa de Fontes & Dados nem de Data Engineer isoladamente, é uma análise de posicionamento de produto.

## Registro de decisão

Nenhuma decisão foi tomada aqui — este documento apenas preserva a diretriz e propõe um esqueleto de execução futura, para que não se perca durante o trabalho de Discovery de Fontes em andamento.
