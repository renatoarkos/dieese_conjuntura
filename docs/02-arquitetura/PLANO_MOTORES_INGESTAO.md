# Plano de Motores de Ingestão — DIEESE Conjuntura

## Natureza deste documento

Organização de todos os indicadores já pesquisados (Discovery de Fontes, Lotes 02-06 + investigação de lacunas, ver `research/notas/DISCOVERY_FONTES_LOTE_PILOTO_01.md`) por **método de extração**, com o "motor" (script de coleta) correspondente quando já existe, a periodicidade real da fonte, e o que falta para cada grupo virar ingestão contínua. Complementa `docs/02-arquitetura/ROADMAP_DATALAKE_FASES.md` (fases gerais) e `docs/04-fontes/CHECKLIST_FONTES_DATALAKE.md` (detalhe por indicador) — este documento é o índice organizado por **como extrair**, não por **o quê**.

**Achado principal ao montar este plano**: a maior parte dos "motores" já existe. Dos 33 indicadores do catálogo original, **25 já têm script de coleta escrito e testado** (`pipelines/ingestao/`). O que falta não é, na maior parte dos casos, construir mais motores — é decidir **como rodá-los de forma contínua e automática**, respeitando a periodicidade de cada um. Essa decisão (orquestração/agendamento) é tratada na Seção 5, separada da classificação por método, porque é uma decisão de arquitetura ainda em aberto no projeto (`VISAO_DO_PRODUTO.md`, Seção 15).

---

## 1. Legenda dos métodos de extração

| Grupo | Método | O que significa | Confiabilidade do motor |
|---|---|---|---|
| **A** | API própria | Endpoint HTTP dedicado a dados (REST, OData, SDMX), retorna JSON/XML estruturado direto | Alta — resposta estruturada, sem parsing frágil |
| **B** | Download direto de tabela | Arquivo estruturado (CSV/XLSX) em URL fixa ou previsível, sem necessidade de navegar a página | Alta — mas depende de o layout do arquivo não mudar |
| **C** | Microdados brutos | Arquivo com registros individuais (não agregados), exige processamento próprio para virar indicador | Alta na coleta, mas motor "incompleto" sem uma camada de agregação |
| **D** | Raspagem direcionada | A fonte não expõe link fixo — é preciso ler o HTML da página para achar o link do arquivo do mês corrente, depois baixar | Média — depende do HTML da página não mudar de estrutura |
| **E** | Manual / não automatizável | Fonte existe e é pública, mas em formato que não permite extração de dado (PDF-imagem, PDF vetorizado, e-mail) | Não é um "motor" no sentido de scraping — outra solução é necessária |

---

## 2. Grupo A — API própria (19 indicadores, 19 motores prontos)

Todos já têm script funcionando em `pipelines/ingestao/`. Nenhuma ação de engenharia adicional necessária para a coleta em si — só decisão de agendamento (Seção 5).

| # | Indicador | Fonte / série | Periodicidade real | Motor (script) |
|---|---|---|---|---|
| 1 | PIB Brasil | IBGE/SIDRA 5932 | Trimestral (~60 dias após fim do trimestre) | `bloco_1_macroeconomia/coleta_pib_sidra.py` |
| 2 | IPCA (índice geral) | IBGE/SIDRA 7060 | Mensal (~dia 10) | `bloco_3_inflacao/coleta_ipca_sidra.py` |
| 3 | INPC (índice geral) | IBGE/SIDRA 7063 | Mensal | `bloco_3_inflacao/coleta_inpc_sidra.py` |
| 4 | PMC — comércio | IBGE/SIDRA 8881 | Mensal | `bloco_1_macroeconomia/coleta_pmc_comercio_sidra.py` |
| 5 | PMS — serviços | IBGE/SIDRA 5906 | Mensal | `bloco_1_macroeconomia/coleta_pms_servicos_sidra.py` |
| 6 | PIM — indústria | IBGE/SIDRA 8888 | Mensal | `bloco_1_macroeconomia/coleta_pim_industria_sidra.py` |
| 7 | Taxa de desocupação | IBGE/SIDRA 4093 | Trimestral (móvel) | `bloco_4_mercado_trabalho/coleta_desocupacao_sidra.py` |
| 8 | Posição na ocupação | IBGE/SIDRA 4097 | Trimestral | `bloco_4_mercado_trabalho/coleta_posicao_ocupacao_sidra.py` |
| 9 | Taxa de participação | IBGE/SIDRA 6461 | Trimestral | `bloco_4_mercado_trabalho/coleta_taxa_participacao_sidra.py` |
| 10 | Taxa de sindicalização | IBGE/SIDRA 8676 | Anual, irregular (hiato 2020-2021) | `bloco_4_mercado_trabalho/coleta_sindicalizacao_sidra.py` |
| 11 | Taxa de câmbio | BCB/SGS 3694+3698 | Diária (série mensal/anual consolidada) | `bloco_1_macroeconomia/coleta_cambio_bcb.py` |
| 12 | Taxa Selic | BCB/SGS 4189+432 | Diária | `bloco_2_monetario_credito/coleta_selic_bcb.py` |
| 13 | Juros por modalidade (4 séries) | BCB/SGS 20728/22019/20741/20742 | Mensal | `bloco_2_monetario_credito/coleta_juros_modalidade_bcb.py` |
| 14 | Endividamento — parte BCB (3 séries) | BCB/SGS 29034/29265/29037 | Mensal | `bloco_2_monetario_credito/coleta_endividamento_bcb.py` |
| 15 | Saldo de crédito SFN (6 séries) | BCB/SGS 20539+20541+20540+20542+20593+20570 | Mensal | `bloco_2_monetario_credito/coleta_saldo_credito_sfn_bcb.py` |
| 16 | IGP-M (via BCB) | BCB/SGS 189 | Mensal | `bloco_3_inflacao/coleta_igpm_bcb.py` |
| 17 | Expectativas Focus (IPCA/INPC) | BCB/Olinda OData | Diária (dias úteis) | `bloco_3_inflacao/coleta_expectativas_focus_bcb.py` |
| 18 | PIB Mundial | FMI/SDMX (WEO) | Semestral (abr/out) | `bloco_1_macroeconomia/coleta_pib_mundial_fmi.py` |
| 19 | Limite fiscal por UF (27 séries) | SICONFI/ORDS | Quadrimestral | `bloco_1_macroeconomia/coleta_limite_fiscal_siconfi.py` |

---

## 3. Grupo B — Download direto de tabela/arquivo (4 indicadores, 4 motores prontos)

Sem API, mas com arquivo estruturado em local fixo ou previsível. Todos já testados.

| # | Indicador | Fonte / arquivo | Periodicidade real | Motor (script) |
|---|---|---|---|---|
| 20 | Balança comercial | MDIC/Comex Stat, CSV anual (`EXP_{ano}.csv`, `IMP_{ano}.csv`) | Mensal (arquivo do ano corrente atualizado) | `bloco_1_macroeconomia/coleta_balanca_comercial_comexstat.py` |
| 21 | Preços de combustíveis | ANP, CSV "últimas 4 semanas" | Semanal | `bloco_3_inflacao/coleta_combustiveis_anp.py` |
| 22 | Endividamento — parte PEIC | FecomercioSP, Excel (descoberto via API de mídia WordPress) | Mensal | `bloco_2_monetario_credito/coleta_endividamento_peic_fecomercio.py` |
| 23 | Cesta básica x salário mínimo | DIEESE/Conab, PDF (boletim mensal) | Mensal | `bloco_3_inflacao/coleta_cesta_basica_dieese.py` |

**Nota sobre o item 23**: diferente dos demais deste grupo, o "arquivo estruturado" é um PDF com uma tabela regular dentro — a coleta bruta já funciona, mas **extrair o número de dentro do PDF é uma etapa de STAGING ainda não implementada** (ver Seção 6).

---

## 4. Grupo C e D — Microdados e raspagem direcionada (2 indicadores, 2 motores prontos com ressalva)

| # | Indicador | Fonte | Método | Periodicidade real | Motor (script) | Ressalva |
|---|---|---|---|---|---|---|
| 24 | CAGED — salário admissão/desligamento e saldo por grupamento (2 indicadores) | MTE/PDET, FTP de microdados | **C — microdados** | Mensal | `bloco_5_caged/coleta_caged_microdados_ftp.py` | Coleta traz registros individuais, não o indicador pronto — falta uma etapa de agregação (STAGING) para reconstruir os números que o DIEESE usa |
| 25 | UCI — Utilização da Capacidade Instalada | CNI, Excel (link muda todo mês) | **D — raspagem direcionada** | Mensal | `bloco_1_macroeconomia/coleta_uci_cni.py` | Regex sobre a página oficial para achar o link vigente a cada execução — mais frágil que os grupos A/B se a CNI mudar o layout da página |

---

## 5. Grupo E — Sem motor possível (não são candidatos a scraping/API)

Estes indicadores têm fonte pública identificada, mas em formato que **não permite extração automatizada de dado** — não adianta "criar um motor melhor", o formato em si (PDF-imagem, PDF vetorizado, e-mail) impede. São soluções de processo, não de engenharia de coleta.

| Indicador | Fonte pública | Formato | Alternativa possível |
|---|---|---|---|
| ICT | Boletim trimestral DIEESE | PDF vetorizado/gráfico | OCR sobre gráfico (baixa confiabilidade) ou obter arquivo interno do DIEESE |
| Greves (3 indicadores) | Balanço das Greves DIEESE | PDF baseado em imagem | OCR (exigiria projeto à parte) ou obter o SAG estruturado do DIEESE |
| Reajustes em negociação coletiva | Boletim "De Olho nas Negociações" DIEESE | PDF imagem/binário | Idem acima |
| INDATEND | Recebido por e-mail | Não é arquivo público | Mudança de processo institucional (não é fonte pública) |
| Pisos salariais | Nenhuma fonte corrente confirmada (SACC fora do ar) | — | Contato direto com o DIEESE |

---

## 6. Indicadores pendentes de decisão de escopo (não é extração, é "qual dado exatamente")

Não entram nesta classificação por método porque a pesquisa de fonte já esgotou o que dava para confirmar sozinha — falta você decidir o que cada um deve significar antes de qualquer motor ser construído.

| Indicador | Pendência | Pergunta |
|---|---|---|
| NFSP | Dois candidatos SGS com escopos diferentes (setor público total vs. só União+BC) | QF07 |
| PIB per capita | Tabela original não existe mais; candidato de substituição não confirmado | QF08 |
| Rendimento médio real (parte DIEESE) | Risco de dupla deflação | QF04 |
| Selic (qual série em cada trecho) | Motor já coleta as 2 séries-fonte; falta decidir a regra de corte | QF03b (não bloqueante) |
| Endividamento "Tabela 27" | Motor já coleta as 3 séries candidatas; falta saber qual é a certa | QF10 (não bloqueante) |

---

## 7. O que falta de verdade para "dados sempre atualizados, em tempo real, por periodicidade"

Aqui está o ponto central da sua pergunta. **Não é construir mais motores** — 25 dos 27 indicadores automatizáveis já têm um. O que falta são três coisas de natureza diferente:

### 7.1 Agendamento/orquestração — DECIDIDO (2026-09-23)

**Resolvido.** O responsável pelo projeto escolheu "função agendada em nuvem", especificamente GitHub Actions — ver `docs/08-decisoes-adr/0003-agendamento-github-actions.md`.

Implementado: 3 workflows em `.github/workflows/` (`motores-diarios.yml`, `motores-semanais.yml`, `motores-mensais.yml`), cobrindo os 25 scripts existentes, validados sintaticamente. **Pendente apenas de ativação**: o repositório ainda não tem remoto no GitHub configurado — os workflows só passam a rodar de fato após `git push` para um repositório GitHub, ação que requer autorização explícita separada (criar/publicar um repositório é uma ação visível externamente).

Armazenamento do resultado de cada execução: artifacts do próprio GitHub Actions (90 dias de retenção) — escolha mínima e reversível, não a decisão definitiva de armazenamento de dados (que segue em aberto).

### 7.2 Camada STAGING (transformação — quase nada implementada ainda)

Mesmo com o motor rodando todo dia, o dado bruto (RAW) não é o indicador pronto. Faltam, no mínimo:
- Selic: aplicar a regra de corte entre as duas séries coletadas.
- Endividamento "Tabela 27": escolher a série certa entre as 3 coletadas.
- CAGED: agregar os microdados brutos nos números que o DIEESE usa (salário médio, saldo por grupamento).
- Cesta básica: extrair o número de dentro do PDF.
- Todos os demais: pelo menos validação básica (o valor chegou? está no intervalo esperado? é mais recente que o anterior?).

### 7.3 "Tempo real" — expectativa a calibrar

Vale alinhar expectativa: nenhuma dessas fontes publica em tempo real no sentido literal — a mais rápida (Selic, Focus) é diária; a maioria é mensal; algumas são trimestrais ou mais espaçadas. "Tempo real" aqui, na prática, significa **"atualizado assim que a fonte publica, sem atraso humano"** — o que já é um salto grande frente ao processo manual atual do DIEESE, mesmo sem ser literalmente instantâneo.

---

## 8. Ordem de construção — estado atual

1. ~~Decidir o agendador mínimo~~ — **feito** (ADR 0003, GitHub Actions).
2. ~~Agendar os motores do Grupo A~~ — **feito** (workflows escritos, cobrindo os 19 motores A + 4 B + CAGED + UCI = 25 no total).
3. **Ativar de fato** — requer remoto no GitHub + push. Aguardando autorização.
4. **Fechar STAGING dos casos já resolvidos e simples** (Selic, Endividamento Tabela 27) — só espera suas respostas QF03b/QF10.
5. **Resolver a agregação do CAGED** antes de tratar seu resultado como indicador utilizável — a coleta já está agendada (workflow semanal), mas o dado bruto (microdados) ainda não vira número pronto sozinho.
6. **Monitorar o motor do CNI (raspagem)** após ativação — é o mais frágil, incluído no workflow semanal com `continue-on-error` para não travar os demais motores se ele falhar.
7. **Grupo E fica de fora de qualquer workflow** — não é scraping, é aguardar contato com o DIEESE ou decidir uma solução de captura manual assistida dentro da própria plataforma.

---

## 9. Síntese numérica

| Grupo | Indicadores | Motores prontos | Falta só agendar | Falta mais alguma coisa |
|---|---|---|---|---|
| A — API própria | 19 | 19 | 19 | — |
| B — Download direto | 4 | 4 | 3 | Cesta básica precisa de extração de PDF |
| C — Microdados | 2 (mesmo motor) | 1 | — | Precisa de agregação antes de agendar |
| D — Raspagem | 1 | 1 | 1 | Precisa de monitoramento de falha |
| E — Manual | 6 | 0 | — | Não é um problema de motor |
| Pendente de escopo | 3 | parcial | — | Depende de você (QF04/07/08) |
| **Total investigado** | **33+** | **25 scripts** | **23 prontos para agendar hoje** | — |
