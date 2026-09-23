# Fontes: outras instituições brasileiras (rodada de expansão, set/2026)

**Natureza deste documento**: Discovery de Fontes **exploratório**, não amarrado a nenhum dos 33 indicadores do catálogo P1 (`docs/05-indicadores/INVENTARIO_INDICADORES_P1.md`). Responde à lacuna registrada em `docs/04-fontes/CHECKLIST_FONTES_DATALAKE.md` ("Observação sobre completude") e em `docs/00-visao-geral/VISAO_DO_PRODUTO.md`, Seção 5 — domínios (mercado de trabalho formal anual, mercados financeiros, distribuição de renda, dados fiscais federais) ainda sem nenhuma fonte investigada. **Nenhuma destas fontes está ligada a um indicador do catálogo atual** — são candidatas para uma futura rodada de Discovery de Materiais/Requisitos que decida se e como incorporá-las ao escopo.

**Data de consulta de todo este documento**: 2026-09-23. Todos os testes abaixo foram execução real (`curl`/WebFetch), não inferência — ver URLs exatas e evidência de resposta em cada seção, conforme exigido por `CLAUDE.md` e `agents/fontes-dados.md`.

**Escopo desta rodada**: instituições brasileiras cobrindo mercado de trabalho formal (RAIS), mercado financeiro (B3, CVM, ANBIMA), fiscal federal (Receita Federal), fomento (BNDES), catálogo geral (dados.gov.br), e ampliações dentro de instituições já integradas (IPEADATA, IBGE além do SIDRA padrão, BCB além do SGS/Focus).

---

## Síntese (classificação de automação, escala de `agents/fontes-dados.md`)

| Instituição | Classificação | Confiança | Nota |
|---|---|---|---|
| BNDES — Dados Abertos (CKAN) | **A** | Alta — testado, API de consulta estruturada real | Melhor achado da rodada |
| BCB — SCR por sub-região (Olinda) | **A** | Alta — testado, dado granular real | Sistema diferente de SGS/Focus, já documentado em `bcb.md` |
| BCB — Taxas de Juros por Instituição (Olinda) | **A** | Alta — testado | Idem, sistema Olinda separado |
| IPEADATA (para outros indicadores, não combustíveis) | **A** | Alta — testado | Mesma API já registrada em `anp-ipeadata.md`, mas granularidade mensal boa para outros temas (renda, PNAD) |
| IBGE — Agregados/SIDRA além do uso atual (POF, Censo, PIB Municipal) | **A** | Alta — testado | Mesmo mecanismo de acesso já usado pelo projeto (API SIDRA/Agregados), só amplia o escopo de tabelas |
| IBGE — API de Localidades ("Cidades") | **A** | Alta — testado | Metadados territoriais, não indicador econômico em si — útil para join |
| B3 — API de composição de carteira (índices) | **A (não documentada oficialmente)** | Média — testado, funciona, mas é endpoint interno do site, não API pública suportada/versionada | Risco de quebra sem aviso |
| B3 — COTAHIST (séries históricas de cotação) | **B** | Alta — testado, download direto | Arquivo anual grande (~89 MB), não é API |
| CVM — Dados Abertos | **B** | Alta — testado, múltiplos datasets CSV confirmados | Sem API de consulta, só arquivos completos |
| RAIS (PDET/MTE) | **C** | Alta — testado, FTP de microdados confirmado | Mesmo padrão já documentado para CAGED (`mte-caged.md`) — sem tabelas prontas via API |
| Receita Federal — Repositório de Dados Abertos | **B** | Média — testado, arquivos reais confirmados | Não localizado um CSV único de "arrecadação total"; arquivos são temáticos (ITR, repasses, OEA) |
| ANBIMA | **D** | Alta confiança na limitação | API existe mas é comercial/mediante assinatura (testado: 401 sem `client_id`) |
| dados.gov.br (Portal Brasileiro de Dados Abertos, CKAN federal) | **D** | Alta confiança na limitação | API CKAN exige autenticação Bearer (testado: 401 em `package_search` e `package_list`) — mudança de comportamento desde a nota anterior no item 33 do checklist |
| BCB — Painel de Estatísticas Monetárias e de Crédito | **D** | Não aprofundado | Página parece dashboard renderizado via JS (Power BI/Tableau); agregados equivalentes já cobertos via SGS/Olinda |

---

## BNDES — Dados Abertos

| Campo | Valor |
|---|---|
| Sistema | Portal CKAN próprio, `dadosabertos.bndes.gov.br`, independente do BNDES institucional. |
| Teste 1 — catálogo | `https://dadosabertos.bndes.gov.br/api/3/action/package_search?q=desembolso&rows=3` → **HTTP 200**, JSON real, 12 resultados, dataset `desembolsos-mensais` (BNDES, dados desde 1995, atualização trimestral). |
| Teste 2 — API de consulta estruturada (não apenas arquivo) | `https://dadosabertos.bndes.gov.br/api/3/action/datastore_search?resource_id=179950b8-b504-4cc7-b0db-9c9eed99e9ba&limit=2` → **HTTP 200**, JSON real e consultável (não apenas CSV estático) — exemplo real de registro: `{"ano":2010,"mes":9,"forma_de_apoio":"DIRETA","produto":"BNDES MERCADO DE CAPITAIS","regiao":"SUDESTE","uf":"RIO DE JANEIRO","setor_bndes":"INDUSTRIA","desembolsos_reais":24753538073.6}`. |
| Teste 3 — CSV completo também disponível | `https://dadosabertos.bndes.gov.br/dataset/102e89ec-836a-4ae0-acc7-74ac2a804c1c/resource/179950b8-b504-4cc7-b0db-9c9eed99e9ba/download/desembolsos-mensais.csv` |
| Formato | JSON (API `datastore_search`, com filtros/paginação via CKAN Data API) ou CSV completo. |
| Periodicidade/Cobertura | Desembolsos mensais desde 1995; atualização trimestral declarada nos metadados. Dimensões: porte de cliente, setor CNAE/BNDES, UF, município, produto, instrumento financeiro. |
| **Classificação** | **A — API direta**, testada com sucesso, inclusive com consulta filtrável (não só dump de arquivo). Nenhuma autenticação exigida. |

## BCB — além do SGS/Focus (Sistema Olinda, múltiplos serviços)

Achado relevante: o BCB expõe **vários serviços Olinda independentes** (protocolo OData), dos quais o projeto já usa apenas `Expectativas/...` (Focus, documentado em `bcb.md`). Dois adicionais testados nesta rodada:

### SCR por sub-região (Sistema de Informações de Crédito)

| Campo | Valor |
|---|---|
| Endpoint testado | `https://olinda.bcb.gov.br/olinda/servico/scr_sub_regiao/versao/v1/odata/scr_sub_regiao(DataBase=@DataBase)?@DataBase=202401&$top=2&$format=json` |
| Resultado | **HTTP 200**, JSON real: `{"DATA_BASE":202401,"CLIENTE":"PF","ESTADO":"BA","SUB_REGIAO":"46","MODALIDADE":"Empréstimo sem Consignação em Folha","RISCO":"D-H","OPERACOES":29250,"CARTEIRA":103818.47,...}` |
| Dimensões | Tipo de cliente (PF/PJ), estado, sub-região, modalidade de crédito, faixa de risco, valores a vencer por prazo. |
| Periodicidade | Mensal, exige parâmetro `DataBase` (AAAAMM); documentação própria em `.../scr_sub_regiao/versao/v1/documentacao`. |
| Acesso confirmado como "ANONIMO" na própria especificação JSON do serviço. |
| **Classificação** | **A — API direta**, testada, sem autenticação. Complementa o item 13 do checklist (Saldo de crédito SFN via SGS) com granularidade territorial que o SGS não oferece. |

### Taxas de Juros por Instituição Financeira

| Campo | Valor |
|---|---|
| Endpoint testado | `https://olinda.bcb.gov.br/olinda/servico/taxaJuros/versao/v2/odata/TaxasJurosDiariaPorInicioPeriodo?$top=3&$format=json` |
| Resultado | **HTTP 200**, JSON real por instituição financeira individual: `{"InicioPeriodo":"2026-09-02","Segmento":"PESSOA JURÍDICA","Modalidade":"Adiantamento sobre contratos de câmbio (ACC)...","InstituicaoFinanceira":"ICBC DO BRASIL BM S.A.","TaxaJurosAoMes":0.21,"TaxaJurosAoAno":2.55,"cnpj8":"17453575"}` |
| Diferença do que já é usado | O item 11 do checklist (juros por modalidade, SGS 20728/22019/20741/20742) traz **médias agregadas do sistema**; este serviço traz o **detalhe por instituição financeira individual**, semanal. |
| **Classificação** | **A — API direta**, testada, sem autenticação. |

### Painel de Estatísticas Monetárias e de Crédito

| Campo | Valor |
|---|---|
| URL | `https://www.bcb.gov.br/estatisticas/estatisticasmonetariascredito` |
| Teste | HTTP 200, mas conteúdo renderizado via JavaScript (aparenta ser dashboard tipo Power BI/Tableau embutido) — não foi possível extrair API/endpoint por WebFetch (que não executa JS). **Não investigado a fundo** (ficaria em D — investigação adicional necessária, possivelmente com ferramenta de renderização de página). |
| Observação | Os agregados que este painel provavelmente visualiza (crédito, moeda) já têm rota de API confirmada via SGS (item 13 do checklist) e via SCR acima — risco baixo de gap real, mas fica registrado como pendência. |

## IPEADATA — reavaliação para além de combustíveis

`docs/04-fontes/anp-ipeadata.md` já confirma a API OData4 do IPEADATA (`http://www.ipeadata.gov.br/api/odata4/`), mas descarta seu uso para combustíveis por granularidade **anual**. Nesta rodada, testei a mesma API para outros temas (atividade/renda), com resultado diferente:

| Campo | Valor |
|---|---|
| Teste de metadados | `http://www.ipeadata.gov.br/api/odata4/Metadados?$filter=startswith(SERNOME,'Massa')&$top=5` → **HTTP 200**, retornou série real `PNADC12_MRRTE12` ("Massa de rendimento real de todos os trabalhos efetivos mensais", fonte IBGE/PNAD Contínua, **periodicidade mensal**, deflacionada pelo IPCA). |
| Teste de valores | `http://www.ipeadata.gov.br/api/odata4/ValoresSerie(SERCODIGO='PNADC12_MRRTE12')?$top=3&$orderby=VALDATA desc` → **HTTP 200**, valores mensais reais desde 03/2012 (ex.: `{"VALDATA":"2012-03-01","VALVALOR":285396.0}`). |
| Correção sobre a nota anterior | A limitação de granularidade anual registrada em `anp-ipeadata.md` é **específica das séries `ANP_*`** (Balanço Energético) — **não é uma limitação geral do IPEADATA**. O IPEADATA replica muitas séries do IBGE/PNAD Contínua, BCB e outras fontes primárias com periodicidade mensal/trimestral igual à fonte original. |
| Ressalva importante | Como agregador, o IPEADATA deve ser usado **apenas quando a fonte primária não oferecer o mesmo dado diretamente** (ex.: séries que cruzam IBGE+BCB já calculadas, ou séries históricas descontinuadas na fonte original) — para os indicadores já cobertos diretamente via SIDRA/SGS no catálogo atual, a fonte primária permanece preferível, conforme `CLAUDE.md` ("Priorize fontes oficiais e primárias"). |
| **Classificação** | **A — API direta**, confirmada. Não recomendado substituir fontes primárias já confirmadas; útil para indicadores de renda/distribuição/atividade regional ainda não pesquisados no catálogo P1. |

## IBGE — além do SIDRA padrão já usado

O projeto já usa a API SIDRA/Agregados (`servicodados.ibge.gov.br/api/v3/agregados/...`) para PIB, IPCA, PNAD Contínua etc. Esta rodada testou se o **mesmo mecanismo de API** cobre os domínios citados na tarefa (POF, Censo, Contas Regionais) — cobre.

| Domínio | Teste | Resultado |
|---|---|---|
| Pesquisa de Orçamentos Familiares (POF) | Busca no catálogo completo `https://servicodados.ibge.gov.br/api/v3/agregados` (2 MB, HTTP 200) por grupo "Pesquisa de Orçamentos Familiares" | Confirmado: tabelas 1594 ("Despesa monetária e não monetária média mensal familiar"), 1595, 1599, 160, entre outras. |
| Censo Demográfico | Mesmo catálogo | Confirmado: dezenas de tabelas (ex.: 10049-10052, "Moradores indígenas...", "Domicílios em setores censitários..."). |
| Contas Regionais / PIB Municipal | Mesmo catálogo | Confirmado: grupo "Produto Interno Bruto dos Municípios" — tabelas 21, 5938, 5939, 599 (inclui Índice de Gini do PIB municipal). Tabela 6784 ("Contas Nacionais Anuais", que inclui PIB per capita) já era candidata registrada no item 5 do checklist (🔴 LACUNA) — **esta pesquisa reforça que 6784 é um agregado real e ativo**, mas não resolve a ambiguidade de escopo já registrada (QF08). |
| API de Localidades/Cidades | `https://servicodados.ibge.gov.br/api/v1/localidades/municipios/3550308` | **HTTP 200**, JSON real com hierarquia territorial completa (município → microrregião → mesorregião → UF → região; e também região imediata/intermediária). Não é indicador econômico, é metadado territorial — útil para enriquecer join geográfico de qualquer indicador municipal/estadual. |
| **Classificação** | **A — API direta** para todos os três domínios (mesmo mecanismo SIDRA/Agregados já validado no projeto) + **A** para API de Localidades. Nota: não testei tabelas específicas do Censo 2022 uma a uma — a confirmação é de que o *domínio* está coberto pelo catálogo de agregados, não de qual tabela exata usar para um indicador específico (isso exigiria uma pergunta de indicador concreta). |

## B3 (Bolsa de Valores do Brasil)

Não há API pública **oficialmente documentada e versionada** da B3 para dados de mercado. Dois caminhos reais foram testados:

### 1. Endpoint interno do site institucional (usado pelo próprio site da B3, sem chave)

| Campo | Valor |
|---|---|
| Endpoint testado | `https://sistemaswebb3-listados.b3.com.br/indexProxy/indexCall/GetPortfolioDay/eyJsYW5ndWFnZSI6InB0LWJyIiwicGFnZU51bWJlciI6MSwicGFnZVNpemUiOjEwLCJpbmRleCI6IklCT1YifQ==` (parâmetro é um JSON `{"language":"pt-br","pageNumber":1,"pageSize":10,"index":"IBOV"}` codificado em base64) |
| Resultado | **HTTP 200**, JSON real com composição teórica do índice Ibovespa na data da consulta (23/09/2026): `{"cod":"ALOS3","asset":"ALLOS","part":"0,537",...}`, `{"cod":"B3SA3","asset":"B3","part":"3,462",...}` — 76 ativos, dados plausíveis e atuais. |
| Limitação | Não é API pública suportada/documentada pela B3 para terceiros — é o backend que alimenta o próprio site institucional. Pode mudar de formato ou ser bloqueado sem aviso. Não recomendado como fonte de produção sem monitoramento redundante. |
| **Classificação** | **A, mas não oficial** — funciona hoje, testado, sem chave, mas fora do padrão de estabilidade das APIs A já documentadas no projeto (SIDRA, SGS, SICONFI). |

### 2. COTAHIST — séries históricas de cotações (download direto, oficial)

| Campo | Valor |
|---|---|
| URL testada | `https://bvmf.bmfbovespa.com.br/InstDados/SerHist/COTAHIST_A2025.ZIP` |
| Resultado | **HTTP 200**, download real de 89.056.788 bytes (arquivo ZIP válido, confirmado por assinatura de arquivo). Padrão de nome documentado oficialmente pela B3 (`COTAHIST_A{ano}.ZIP` para série anual; existem variantes mensal/diária). |
| Conteúdo | Preço de abertura/fechamento/máximo/mínimo/médio, volume e quantidade negociada, por ativo, por pregão, ano completo — layout fixo (posição de coluna), documentado pela B3. |
| Periodicidade/Histórico | Arquivos anuais desde a década de 1980 (não testado o limite exato); diário/mensal também disponíveis por convenção de nome de arquivo. |
| **Classificação** | **B — download estruturado**, oficial e testado. Caminho mais robusto que o endpoint interno acima para uso em produção. |

## CVM — Dados Abertos

| Campo | Valor |
|---|---|
| Estrutura | Repositório de arquivos estático em `dados.cvm.gov.br/dados/`, organizado por tipo de entidade regulada (sem API de consulta — é HTTP diretório + arquivo). |
| Teste 1 — listagem | `https://dados.cvm.gov.br/dados/` → **HTTP 200**, confirma pastas reais: `ADM_CART/`, `ADM_FII/`, `CIA_ABERTA/`, `FI/`, `FIDC/`, `FII/`, `FIP/`, `CROWDFUNDING/`, entre outras. |
| Teste 2 — cadastro de fundos | `https://dados.cvm.gov.br/dados/FI/CAD/DADOS/cad_fi.csv` → **HTTP 200**, 17.921.602 bytes, CSV real com header `TP_FUNDO;CNPJ_FUNDO;DENOM_SOCIAL;DT_REG;...;VL_PATRIM_LIQ;DT_PATRIM_LIQ;...` e primeira linha de dado real (`FACFIF;00.000.684/0001-2...`). |
| Teste 3 — cadastro de companhias abertas | `https://dados.cvm.gov.br/dados/CIA_ABERTA/CAD/DADOS/cad_cia_aberta.csv` → **HTTP 200**. |
| Formato | CSV (delimitador `;`), arquivos completos por tema — não há filtro/query, é dump total sempre que atualizado. |
| **Classificação** | **B — download estruturado**, confirmado, sem autenticação. Cobre fundos de investimento (patrimônio líquido, rentabilidade), companhias abertas, FIIs, FIDCs — relevante para indicadores de mercado de capitais/poupança financeira caso o escopo do DIEESE Conjuntura venha a incluir esse eixo. |

## RAIS (Relação Anual de Informações Sociais) — PDET/MTE

| Campo | Valor |
|---|---|
| Sistema | Mesmo produtor e mesma infraestrutura já documentada para o Novo CAGED em `docs/04-fontes/mte-caged.md` — FTP público de microdados. |
| Teste | `ftp://ftp.mtps.gov.br/pdet/microdados/RAIS/` → conexão bem-sucedida (FTP 226, transferência completa), listagem real confirmada: pastas anuais de 1985 a 2025 (incluindo "2023 Parcial", "2024 Parcial"), mais pasta `Layouts`. |
| Conteúdo de um ano (testado 2023) | Arquivos `.7z` reais por UF/região: `RAIS_ESTAB_PUB.7z` (127 MB), `RAIS_VINC_PUB_SP.7z` (1,02 GB), `RAIS_VINC_PUB_NORDESTE.7z` (567 MB), etc. — microdados de vínculos empregatícios e estabelecimentos, não tabelas agregadas prontas. |
| Não testado nesta rodada | Se existe algum "workbook" de tabelas agregadas prontas equivalente ao citado para o CAGED (item 26/27 do checklist) — dado o padrão já observado no CAGED (distribuição instável via Google Drive), não foi buscado nesta rodada; ficaria como pendência de uma investigação futura se o DIEESE priorizar um indicador anual baseado em RAIS. |
| **Classificação** | **C — processamento de microdados**, mesmo padrão do CAGED. Sem API, sem tabela pronta confirmada — exige download + descompactação `.7z` + processamento próprio para virar indicador agregado. |

## Receita Federal — Repositório de Dados Abertos

| Campo | Valor |
|---|---|
| Portal de navegação | `https://www.gov.br/receitafederal/pt-br/acesso-a-informacao/dados-abertos` — 18 categorias temáticas (Arrecadação, Cadastros, Distribuição de Renda, Grandes Números do IRPF, Carga Tributária etc.), mas a própria página de índice **não expõe links diretos de arquivo** (confirmado via WebFetch). |
| Repositório de arquivos real | `https://www.gov.br/receitafederal/dados` — confirmado via WebFetch como repositório com arquivos nomeados individualmente (não apenas navegação). |
| Teste de download direto | `https://www.gov.br/receitafederal/dados/arrecadacao-itr.csv` → **HTTP 200**, 6.787.568 bytes. Observação: apesar da extensão `.csv` na URL, o conteúdo real é um **arquivo ZIP** (assinatura `PK`) contendo `Valores de Arrecadação ITR.csv` — confirmado pela análise dos primeiros bytes. Isso é uma particularidade real da fonte, registrada para não confundir quem for implementar o parser. |
| Outros arquivos reais confirmados na listagem (não baixados individualmente) | `2026-10-09 - VALORES REPASSADOS DE 2013 A 2026.csv`, `2026-09-09-anexo-i-apuracao-repasse-corrente-2026.csv`, `Anexo I - Portaria 319_2023.csv`, `2026-02-24-Anexo I - HABILITADOS FDCA 2026.csv`, entre outros — arquivos de repasse de arrecadação (FUNDAF, FDCA) e de programas específicos, não um CSV único de "arrecadação federal total" mensal. |
| **Limitação honesta** | Não foi localizado, nesta rodada, um arquivo único e direto para a série mais genérica de interesse macro ("arrecadação total federal, mensal") — os arquivos confirmados são temáticos e pontuais (ITR, repasses a fundos, OEA). Encontrar o arquivo exato equivalente ao indicador "carga tributária"/"arrecadação total" exigiria uma investigação adicional dirigida a um indicador específico, não apenas a existência do repositório. |
| **Classificação** | **B — download estruturado**, confirmado para arquivos existentes (repositório real, não portal fictício), mas com **D — investigação adicional necessária** para localizar o arquivo específico de "arrecadação total" se este vier a ser um indicador priorizado. |

## ANBIMA

| Campo | Valor |
|---|---|
| API institucional | `api.anbima.com.br` — teste em `https://api.anbima.com.br/feed/precos-indices/v1/titulos-publicos/mercado-secundario-TPF` → **HTTP 401**, corpo: `"Client Id in the request, identified by HEADER client_id, is invalid. Check docs.sensedia.com"` — confirma que a API **existe e está ativa**, mas exige credencial (`client_id`) obtida via cadastro. |
| Portal de desenvolvedores | `https://developers.anbima.com.br` (consultado via WebFetch) confirma: (a) modelo de **assinatura** ("Conheça nossas APIs antes da assinatura"), (b) existe **sandbox gratuito para testes** sem necessidade de produção, (c) cadastro obrigatório em `admin-developers.anbima.com.br`, (d) autenticação OAuth2. Não foi possível confirmar nesta pesquisa se algum plano é 100% gratuito em produção (a página não detalha preços) — não invento essa informação; fica como pendência de contato direto com a ANBIMA se o indicador for priorizado. |
| **Classificação** | **D — investigação adicional necessária** (não é A, porque não está livremente acessível sem cadastro/possível custo; não é uma "ausência de caminho" porque a API existe e tem sandbox). Se o DIEESE priorizar um indicador de renda fixa/fundos, vale abrir cadastro no sandbox para testar viabilidade prática antes de decidir. |

## dados.gov.br (Portal Brasileiro de Dados Abertos, CKAN federal)

| Campo | Valor |
|---|---|
| Teste 1 | `https://dados.gov.br/api/3/action/package_search?q=emprego&rows=3` → **HTTP 401 Unauthorized**, corpo vazio, header `WWW-Authenticate: Bearer`. |
| Teste 2 | `https://dados.gov.br/api/3/action/package_list` (sem parâmetros) → **HTTP 401**, mesmo padrão. |
| Teste 3 | Domínio legado `http://dados.gov.br/...` → **HTTP 301** (redireciona para o mesmo domínio https, sujeito à mesma exigência). |
| Achado | O portal federal **mudou de comportamento** em relação ao já registrado no item 33 do checklist (que citava "exige token institucional (401)" apenas para um dataset específico do Mediador/MTE) — **agora a própria API de busca geral do catálogo (`package_search`, `package_list`) exige autenticação Bearer**, não é mais possível nem listar o catálogo publicamente sem token. Isso é diferente dos portais CKAN institucionais próprios (BNDES, BCB), que continuam anônimos — o bloqueio parece ser uma política específica do portal federal central, não do protocolo CKAN em si. |
| **Classificação** | **D — investigação adicional necessária** (como caminho central/agregador). Continua válido como **catálogo de referência para localizar a instituição produtora** (navegação HTML pelo site funciona normalmente), mas não como via de acesso automatizado sem credencial. Prefira sempre o portal CKAN próprio da instituição produtora (ex.: `dadosabertos.bndes.gov.br`, `dadosabertos.bcb.gov.br`) quando existir — já confirmados anônimos nesta pesquisa. |

---

## Observações metodológicas e limites desta rodada

- Todos os testes acima foram execução real via `curl`/WebFetch nesta sessão (2026-09-23), com URL exata, código HTTP e trecho real de resposta registrados — nenhuma fonte, endpoint ou dado foi presumido sem teste, conforme `CLAUDE.md` e `agents/fontes-dados.md`.
- Nenhum destes achados está amarrado a um indicador específico do catálogo P1 — são candidatos de expansão de escopo. Antes de qualquer piloto técnico (pipeline de ingestão), é necessário: (1) confirmar com a equipe do DIEESE se algum destes domínios (mercado de trabalho formal anual, mercado financeiro, fiscal federal) entra no escopo da plataforma; (2) se sim, repetir o procedimento completo do papel Especialista em Fontes & Dados (14 pontos) para o indicador específico que for priorizado — esta rodada cobriu apenas "existe caminho de acesso automatizável", não "qual série exata corresponde a qual indicador do DIEESE".
- **Fase do projeto**: conforme `CLAUDE.md`, o projeto está em DISCOVERY → PESQUISA → REQUISITOS → ARQUITETURA. Este documento é pesquisa pura — nenhum pipeline de ingestão foi criado ou modificado para estas fontes.

## Próximo passo recomendado

Não iniciar piloto técnico para nenhuma destas fontes sem antes: (a) validar com o DIEESE se os domínios cobertos (RAIS, mercado financeiro via B3/CVM, fiscal via Receita Federal) fazem parte do escopo pretendido da plataforma; (b) se algum indicador concreto for definido, repetir a investigação de fonte já com o indicador específico em mãos (esta rodada é de descoberta de caminho de acesso institucional, não de indicador).
