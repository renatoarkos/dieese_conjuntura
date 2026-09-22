# Inventário de Materiais — DIEESE Conjuntura

## 1. Objetivo

Produzir um inventário físico e uma classificação preliminar do corpus documental em `materiais/originais/`, como etapa que precede — e não substitui — a análise econômica aprofundada do conteúdo. O objetivo aqui é puramente organizacional: mapear o que existe, em que volume, como está estruturado, onde há duplicidade ou versionamento aparente, e propor uma fila de leitura priorizada para o Discovery profundo.

## 2. Metodologia utilizada

O inventário foi construído inteiramente a partir de metadados do sistema de arquivos — caminho, nome, extensão, tamanho, data de modificação e hash MD5 individual de cada arquivo — sem abrir ou interpretar o conteúdo de nenhum documento. `materiais/originais/` foi tratado como estritamente somente leitura: nenhum arquivo foi movido, renomeado, convertido, sobrescrito ou excluído.

A classificação preliminar (categoria e prioridade) foi atribuída por regras heurísticas aplicadas ao caminho e ao nome dos arquivos (por exemplo, presença de siglas como `PNAD`, `CAGED`, `IPCA`, `PIB`, nomes de pastas como `Backup` ou `Definitivo`), sem qualquer leitura do conteúdo. Quando não havia evidência suficiente no nome/caminho, o item foi marcado como `a classificar` (categoria) e/ou `PX` (prioridade), conforme instruído — nenhuma classificação foi forçada.

Duplicidade foi identificada de duas formas: (1) **duplicata exata**, por hash MD5 idêntico; (2) **possível versão**, por nome de arquivo semelhante (ignorando sufixos como `(2)`, `(3)`) em conteúdo diferente. Arquivos situados em qualquer subdiretório chamado `Backup` foram adicionalmente marcados como **backup aparente**. Essas três marcações não são mutuamente exclusivas.

## 3. Visão geral do corpus

- Total de arquivos: **339**
- Volume total: **708.7 MB** (743.094.431 bytes)
- Estrutura física: todo o corpus está sob `materiais/originais/`, distribuído em duas ramificações — a pasta de trabalho corrente `Apresentação de conjuntura/` (que inclui a subpasta `Backup/` com múltiplos cortes mensais e uma grande pasta `Outras versões/` de material histórico 2020–2024) e uma pasta `dieese/`, com um único arquivo.
- **Nota sobre a pasta `dieese/`**: essa pasta e o arquivo que ela contém não faziam parte da estrutura observada no reconhecimento inicial do ambiente (quando o arquivo `Apresentação_Conjuntura_4T_2025 (2).xlsx` estava solto diretamente em `materiais/originais/`). A comparação de metadados do arquivo (data de conteúdo inalterada, data de metadado/local alterada) indica que ele foi movido para dentro de uma nova pasta `dieese/` em algum momento após o reconhecimento inicial e antes do primeiro *baseline* de hash agregado registrado neste projeto. Questionado, o responsável pelo projeto confirmou que essa movimentação foi feita por ele. O conteúdo do arquivo não foi alterado, e o corpus permanece com exatamente os mesmos 339 arquivos e mesmo hash agregado desde o primeiro baseline rastreado.

## 4. Estatísticas

### 4.1 Distribuição por extensão

| Extensão | Arquivos |
|---|---|
| .xlsx | 203 |
| .pptx | 53 |
| .csv | 47 |
| .xls | 15 |
| .pdf | 7 |
| .xlsm | 4 |
| .docx | 4 |
| .ppt | 2 |
| .jpg | 2 |
| .zip | 1 |
| .odp | 1 |

### 4.2 Diretórios com maior concentração de material

| Arquivos | Diretório (relativo a `materiais/originais/`) |
|---|---|
| 54 | `Apresentação de conjuntura/Backup/Outras versões` |
| 51 | `Apresentação de conjuntura/Backup/Dados_2025_05/Dados Brutos` |
| 43 | `Apresentação de conjuntura/Backup/Outras versões/Dados_2024.11/Dados` |
| 38 | `Apresentação de conjuntura/Backup/Dados_2025.03/Dados Brutos` |
| 22 | `Apresentação de conjuntura/Backup/Outras versões/Dados` |
| 22 | `Apresentação de conjuntura/Backup/Outras versões/Dados/Outras` |
| 22 | `Apresentação de conjuntura/Backup/Outras versões/Dados_2024.12/Dados` |
| 14 | `Apresentação de conjuntura/Backup/Dados_2025_07/Dados Brutos` |
| 14 | `Apresentação de conjuntura/Backup/Outras versões/Dados/Outras_05.09.2023` |
| 13 | `Apresentação de conjuntura/Backup/Outras versões/Dados_2024.11` |

## 5. Categorias (classificação preliminar)

| Categoria | Arquivos |
|---|---|
| bases e planilhas | 53 |
| apresentação de conjuntura | 49 |
| mercado de trabalho | 41 |
| atividade econômica | 37 |
| crédito e juros | 34 |
| inflação e custo de vida | 34 |
| a classificar | 27 |
| indústria | 14 |
| reforma trabalhista | 9 |
| comércio | 9 |
| análise de conjuntura | 8 |
| serviços | 8 |
| setor externo | 6 |
| política fiscal | 6 |
| renda e salários | 2 |
| documentos institucionais | 2 |

Dos 339 arquivos, **27** (8%) permanecem como `a classificar` por não apresentarem, no nome ou caminho, evidência suficiente de tema (ex.: `Tabela 5440.xlsx`, `Relatorio_Series.xls`, `chart.csv`, notas técnicas em PDF sem prefixo temático). Esses casos dependerão de abertura do conteúdo na etapa de Discovery profundo.

## 6. Prioridades

| Prioridade | Significado | Arquivos |
|---|---|---|
| P1 | Diretamente relacionado à análise de conjuntura atual | 3 |
| P2 | Potencialmente importante para indicadores, metodologia ou arquitetura | 131 |
| P3 | Material temático ou histórico, análise posterior | 184 |
| P4 | Backup ou duplicata aparente, sem prioridade de leitura agora | 21 |
| PX | Relevância ainda a investigar | 0 |

## 7. Duplicidades e versões

- **Duplicatas exatas** (mesmo hash MD5): 3 grupos, totalizando 6 arquivos.
- **Possíveis versões** (nome semelhante, conteúdo diferente): 103 arquivos em 39 grupos de nome.
- **Backups aparentes** (situados em algum subdiretório `Backup/`): 334 arquivos — a grande maioria do corpus, já que a estrutura de trabalho concentra o material histórico dentro de `Apresentação de conjuntura/Backup/`.

Nenhum arquivo foi excluído, renomeado ou alterado em função dessas marcações — apenas registradas.

### 7.1 Grupos de duplicata exata

- Hash `ed7bb429143a9a2f92ca289055b8e697`:
  - `Apresentação de conjuntura/Backup/Dados_2025.03/Definitivo/Apresentação_Conjuntura_03-25 (2).xlsx`
  - `Apresentação de conjuntura/Backup/Dados_2025_05/Definitivo/Apresentação_Conjuntura_03-25 (2).xlsx`
- Hash `aedfd0524fa71eb5b5299130c2c87729`:
  - `Apresentação de conjuntura/Backup/Outras versões/Dados/Macroeconomia.xlsx`
  - `Apresentação de conjuntura/Backup/Outras versões/Dados/Outras_05.09.2023/Macroeconomia.xlsx`
- Hash `ac550d3f3cb5a0644758596925a112d5`:
  - `Apresentação de conjuntura/Backup/Outras versões/Dados/Monetário.xlsx`
  - `Apresentação de conjuntura/Backup/Outras versões/Dados/Outras_05.09.2023/Monetário.xlsx`

### 7.2 Exemplos de possíveis versões (amostra)

| Nome normalizado | Ocorrências | Exemplo de caminhos |
|---|---|---|
| atr_reforma trabalhista_dezembro2021 | 9 | `Apresentação de conjuntura/ATR_Reforma trabalhista_dezembro2021 (2).pptx` (+8 outro(s)) |
| monetario | 7 | `Apresentação de conjuntura/Backup/Outras versões/Dados/Monetário (3).xlsx` (+6 outro(s)) |
| atr_conjuntura_2022.05 | 6 | `Apresentação de conjuntura/Backup/Outras versões/ATR_Conjuntura_2022.05 (2).pptx` (+5 outro(s)) |
| atr_conjuntura_2022.03 | 5 | `Apresentação de conjuntura/Backup/Outras versões/ATR_Conjuntura_2022.03 (2).pptx` (+4 outro(s)) |
| apresentacao_conjuntura_03-25 | 4 | `Apresentação de conjuntura/Backup/Dados_2025.03/Definitivo/Apresentação_Conjuntura_03-25 (2).xlsx` (+3 outro(s)) |
| demonstrreservas_m | 3 | `Apresentação de conjuntura/Backup/Dados_2025_05/Dados Brutos/DemonstrReservas_M.xlsx` (+2 outro(s)) |
| atr_conjuntura_08.2020 | 3 | `Apresentação de conjuntura/Backup/Outras versões/ATR_Conjuntura_08.2020 (2).pptx` (+2 outro(s)) |
| atr_conjuntura_2022.01.21 | 3 | `Apresentação de conjuntura/Backup/Outras versões/ATR_Conjuntura_2022.01.21 (2).pptx` (+2 outro(s)) |
| macroeconomia | 3 | `Apresentação de conjuntura/Backup/Outras versões/Dados/Macroeconomia.xlsx` (+2 outro(s)) |
| apresentacao_conjuntura_4t_2025 | 2 | `Apresentação de conjuntura/Apresentação_Conjuntura_4T_2025.xlsx` (+1 outro(s)) |
| 20741 | 2 | `Apresentação de conjuntura/Backup/Dados_2025.03/Dados Brutos/20741.csv` (+1 outro(s)) |
| 20742 | 2 | `Apresentação de conjuntura/Backup/Dados_2025.03/Dados Brutos/20742.csv` (+1 outro(s)) |

(lista completa de status por arquivo em `inventario_materiais.csv`, coluna `duplicate_status`)

## 8. Conjuntos documentais identificados

| Conjunto | Arquivos | Descrição |
|---|---|---|
| snapshot-2025-05 | 61 | Corte de maio/2025 (Backup/Dados_2025_05) — Dados Brutos + Definitivo. |
| snapshot-historico-dados | 58 | Pasta genérica `Outras versões/Dados/` (sem data explícita no nome) e suas subpastas (`Outras/`, `Outras_05.09.2023/`) — dados brutos e planilhas históricas diversas, aparentemente de 2023. |
| snapshot-2024-11 | 56 | Corte histórico de novembro/2024 (Outras versões/Dados_2024.11) — inclui pasta interna `Dados/`. |
| snapshot-2025-03 | 47 | Corte de março/2025 (Backup/Dados_2025.03) — Dados Brutos + Definitivo. |
| serie-historica-atr-conjuntura | 47 | Série histórica de apresentações `ATR_Conjuntura_*.pptx` (2020–2024) em `Backup/Outras versões/`, com múltiplas duplicatas de nome (sufixos `(2)`, `(3)`...). |
| snapshot-2024-12 | 30 | Corte histórico de dezembro/2024 (Outras versões/Dados_2024.12) — inclui pasta interna `Dados/`. |
| snapshot-2025-07 | 19 | Corte de julho/2025 (Backup/Dados_2025_07) — Dados Brutos + Definitivo. |
| reforma-trabalhista-dez2021 | 9 | Material sobre a reforma trabalhista (dezembro/2021), em múltiplos formatos (pptx, ppt, odp) e cópias, tanto na raiz da pasta de trabalho quanto em `Backup/Outras versões/`. |
| snapshot-2024-09 | 6 | Corte histórico de setembro/2024 (Outras versões/Dados_2024.09). |
| conjuntura-4T2025-atual | 3 | Apresentação e planilha-base do período corrente (4º trimestre de 2025) — inclui a possível versão paralela em `dieese/`. |
| snapshot-2025-09 | 3 | Corte de setembro/2025 (Backup/Setembro 2025) — apresentação + planilha do mês imediatamente anterior ao período corrente. |

## 9. Fila recomendada para Discovery profundo

Proposta baseada exclusivamente em metadados (caminho, nome, prioridade e agrupamento) — sujeita a revisão após a primeira leitura de conteúdo:

1. `Apresentação de conjuntura/ATR_Conjuntura_2025.12.pptx` — apresentação de conjuntura mais recente (P1).
2. `Apresentação de conjuntura/Apresentação_Conjuntura_4T_2025.xlsx` — planilha-base da apresentação mais recente (P1).
3. `dieese/Apresentação_Conjuntura_4T_2025 (2).xlsx` — possível versão paralela/anterior do mesmo período; comparar com o item 2 para entender divergências antes de descartar como redundante (P1).
4. `Apresentação de conjuntura/Backup/Setembro 2025/ATR_Conjuntura_2025.09.pptx` e `Apresentação_Conjuntura_09-25.xlsx` — corte completo do mês imediatamente anterior disponível, útil para comparação estrutural e metodológica com o período atual (P2, grupo `snapshot-2025-09`).
5. `Apresentação de conjuntura/Backup/Dados_2025_07/Definitivo/*` (5 arquivos: Macroeconomia, Novo Caged, Preços_Inflação, SM e Cesta) — conjunto "Definitivo" mais recente antes de setembro, bom ponto de partida para levantar quais indicadores já são tratados por tema (P2, grupo `snapshot-2025-07`).
6. `Apresentação de conjuntura/Backup/Dados_2025_05/Definitivo/*` e `Dados_2025.03/Definitivo/*` — para entender a evolução da metodologia/indicadores ao longo do primeiro semestre de 2025 (P2).

Não foram identificados, apenas pelos metadados, candidatos adicionais claramente mais relevantes que os dois arquivos citados na tarefa (`Apresentação_Conjuntura_4T_2025.xlsx` e `ATR_Conjuntura_2025.12.pptx`) — eles de fato aparentam ser os documentos mais atuais do corpus. O achado relevante foi a existência de uma possível versão paralela desses mesmos documentos (item 3) que merece verificação antes de ser descartada.

## 10. Limitações da classificação preliminar

- A classificação de categoria e prioridade foi feita **exclusivamente por caminho e nome de arquivo**, sem abrir nenhum documento — é necessariamente aproximada.
- 27 arquivos ficaram como `a classificar` por falta de evidência textual suficiente no nome (ex.: nomes genéricos como `chart.csv`, `Relatorio_Series.xls`, ou códigos de tabela sem prefixo temático como `Tabela 5440.xlsx`, que em outros pontos do corpus aparece nomeada como `PNAD - 5440 - Rendimento...xlsx`).
- "Possível versão" foi inferida por semelhança de nome normalizado; isso pode incluir falsos positivos (nomes coincidentes por acaso) e não captura versões com nomes muito diferentes entre si.
- A prioridade P1 foi atribuída à pasta de trabalho corrente e à pasta `dieese/`; arquivos de anos anteriores relevantes para série histórica de longo prazo podem estar sub-priorizados (P3) mesmo quando conceitualmente importantes para a plataforma.
- O achado sobre a pasta `dieese/` (seção 3) foi esclarecido diretamente com o responsável pelo projeto durante esta tarefa; registra-se aqui para rastreabilidade.
- Hashes individuais foram calculados para todos os 339 arquivos sem custo operacional excessivo (leitura sequencial, sem escrita).

## 11. Próximos passos recomendados

1. Autorização humana para iniciar a leitura de conteúdo dos materiais P1 (itens 1–3 da fila da seção 9).
2. Leitura da planilha-base e da apresentação mais recentes para identificar indicadores efetivamente utilizados (alimenta o Catálogo Mestre de Indicadores, `docs/05-indicadores/`).
3. Comparação entre `Apresentação_Conjuntura_4T_2025.xlsx` (pasta de trabalho) e `dieese/Apresentação_Conjuntura_4T_2025 (2).xlsx` para entender a natureza da divergência.
4. Ampliar a leitura para o conjunto `snapshot-2025-09` e os `Definitivo` de 2025 para levantar fontes e periodicidade dos indicadores.
5. Somente depois disso, revisitar os 27 itens `a classificar` e refinar a categorização.
