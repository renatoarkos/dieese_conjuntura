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
- `docs/00-visao-geral/VISAO_DO_PRODUTO.md` e `docs/03-metodologia/PROTOCOLO_TRABALHO_IA.md` criados, registrando a visão do produto e o protocolo de trabalho entre humanos, Cowork, Claude Code e Antigravity.
- Segundo commit realizado: `52962c0` — "docs: establish product vision and AI collaboration governance" (inclui `VISAO_DO_PRODUTO.md`, `PROTOCOLO_TRABALHO_IA.md` e este documento).
- Inventário físico e classificação preliminar de `materiais/originais/` concluídos (339 arquivos, ~708,7 MB), com registro em `research/notas/INVENTARIO_MATERIAIS.md` e `research/notas/inventario_materiais.csv` (commit `ed16e68`).
- Discovery profundo — rodada 1 concluída sobre os três materiais P1 (dois Excel + apresentação `ATR_Conjuntura_2025.12.pptx`): comparação estrutural dos dois Excel, inventário estrutural do Excel de referência, catálogo preliminar de 33 indicadores, análise integral dos 58 slides da apresentação, reconstrução do fluxo de produção e classificação preliminar de oportunidades de automação. Documentos gerados: `docs/05-indicadores/INVENTARIO_INDICADORES_P1.md`, `research/notas/ANALISE_ESTRUTURAL_EXCEL_P1.md`, `research/notas/ANALISE_APRESENTACAO_CONJUNTURA_2025_12.md`, `research/notas/COMPARACAO_EXCEL_P1.md`, `research/notas/FLUXO_ATUAL_CONJUNTURA.md`, `research/notas/OPORTUNIDADES_AUTOMACAO_P1.md` (ainda não commitados nesta atualização).
- Discovery profundo — rodada 2 (Validação Técnica dos Materiais P1) concluída: inspeção direta da estrutura interna OOXML dos dois Excel e da apresentação (metadados, visibilidade de abas, nomes definidos, links externos, vínculos de gráfico), sem alterar nenhum arquivo original. Principais achados: os dois Excel P1 compartilham o mesmo arquivo-raiz (mesma autoria e data de criação nos metadados internos); a divergência da aba T14 entre os dois arquivos foi explicada como reorganização de rótulos (o conteúdo de Selic/IPCA/juros real foi realocado para a aba T18a em "dieese"); 43 dos 47 gráficos da apresentação são tecnicamente vinculados a um arquivo Excel externo (predominantemente o próprio arquivo "principal"); a origem do bloco "Cesta Básica" foi identificada com boa confiança (aba T27, presente apenas em "dieese", e um arquivo dedicado no corpus); a origem dos blocos "Greves" e "Negociação Coletiva" permanece não localizada no corpus de 339 materiais, embora haja evidência técnica de que as abas de origem existem em uma versão do arquivo ausente do corpus. Documentos gerados/atualizados: `research/notas/VALIDACAO_TECNICA_P1.md` e `research/notas/MAPA_SLIDE_ABA_P1.md` (novos); `research/notas/COMPARACAO_EXCEL_P1.md`, `research/notas/ANALISE_ESTRUTURAL_EXCEL_P1.md`, `research/notas/ANALISE_APRESENTACAO_CONJUNTURA_2025_12.md`, `research/notas/FLUXO_ATUAL_CONJUNTURA.md` (atualizados com adendos) e `docs/05-indicadores/INVENTARIO_INDICADORES_P1.md` (nota de rodapé adicionada, sem alteração de conteúdo). Nenhum destes arquivos foi commitado nesta atualização.

## Em andamento

Aguardando validação humana dos achados das rodadas 1 e 2 do Discovery profundo antes de prosseguir para pesquisa de fontes/APIs na internet, escolha de tecnologia ou qualquer desenvolvimento de código de plataforma — permanecemos em DISCOVERY.

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

Validação humana dos achados das rodadas 1 e 2 do Discovery profundo — em especial: (a) confirmar a conclusão de que "principal" é a referência primária da apresentação 4T/2025, com "dieese" como fonte complementar apenas para a Cesta Básica; (b) fornecer, se possível, os arquivos-fonte de Greves/Negociação Coletiva, Preços de Combustíveis (`20251127 - Preços combustíveis.xlsx`) e ICT (`ICT - Brasil - PNAD Continua - 202503.xls`), hoje ausentes do corpus mas identificados por nome via vínculo técnico. Ver `research/notas/VALIDACAO_TECNICA_P1.md` (seção "Dúvidas que ainda exigem validação humana") para a lista completa.

## Regra de atualização

Este documento deverá ser atualizado após marcos relevantes, decisões importantes ou handoffs entre ambientes/agentes.
