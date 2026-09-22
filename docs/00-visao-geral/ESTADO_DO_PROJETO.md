# Estado do Projeto — DIEESE Conjuntura

## Data de atualização

2026-09-22

## Fase atual

DISCOVERY

## Objetivo da fase

Compreender materiais existentes, indicadores utilizados pelo DIEESE, fontes, necessidades analíticas e requisitos antes de definir arquitetura tecnológica.

## Concluído

- Reconhecimento inicial do ambiente: confirmado acesso de leitura/escrita ao repositório local (`C:\repositorio\dieese\conjuntura`) e inventário superficial de `materiais/` por tipo de arquivo (339 arquivos, ~710 MB) — sem análise de conteúdo.
- `CLAUDE.md` criado na raiz — manual operacional persistente do repositório.
- Estrutura documental e de pesquisa criada: `docs/00-visao-geral/` a `docs/09-backlog/`, `research/literatura/`, `research/fontes/`, `research/benchmarks/`, `research/notas/` e `data/reference/`, com `.gitkeep` nos diretórios ainda vazios.
- `README.md` criado na raiz.
- Repositório Git inicializado (branch `main`).
- `.gitignore` criado, cobrindo Python, JS/TS, notebooks, bancos locais, segredos e camadas derivadas de dados.
- Decisão provisória de governança registrada em `.gitignore`: `materiais/originais/` fica temporariamente fora do versionamento Git convencional (arquivos preservados localmente, não excluídos nem alterados).
- `.env.example` criado, sem credenciais reais.
- Objetos Git órfãos (resultantes de tentativas interrompidas de `git add`) removidos via `git prune`.
- Primeiro commit realizado: `020d0d8` — "chore: establish DIEESE Conjuntura project baseline" (19 arquivos: documentação e estrutura; nenhum material do DIEESE).
- `docs/00-visao-geral/VISAO_DO_PRODUTO.md` criado, registrando a visão inicial do produto — **ainda não commitado** (arquivo untracked no momento desta atualização).

## Em andamento

Preparação para Discovery dos materiais existentes.

## Próximas etapas

1. inventário dos materiais;
2. análise da planilha de conjuntura;
3. análise da apresentação de conjuntura;
4. identificação dos indicadores existentes;
5. validação das fontes;
6. classificação da capacidade de automação;
7. Catálogo Mestre inicial;
8. Biblioteca de Relações Econômicas;
9. levantamento de lacunas;
10. requisitos;
11. arquitetura;
12. ADRs;
13. desenvolvimento.

## Decisões consolidadas

- Estrutura de diretórios do repositório (`docs/`, `research/`, `data/reference/`, `materiais/`) definida e criada.
- `materiais/originais/` permanece preservado localmente e fica temporariamente fora do versionamento Git convencional, sem prejuízo da regra de preservação já estabelecida em `CLAUDE.md`; a estratégia definitiva de armazenamento/versionamento desses materiais será decidida posteriormente por ADR (`docs/08-decisoes-adr/`).

## Decisões abertas

- estratégia definitiva para materiais binários (Git LFS, armazenamento externo ou outra abordagem);
- stack;
- banco;
- backend;
- frontend;
- orquestração;
- infraestrutura;
- deployment;
- arquitetura de IA;
- BI.

## Bloqueios

Nenhum bloqueio real identificado no momento.

## Próxima tarefa recomendada

Inventário estruturado de `materiais/originais/`.

## Regra de atualização

Este documento deverá ser atualizado após marcos relevantes, decisões importantes ou handoffs entre ambientes/agentes.
