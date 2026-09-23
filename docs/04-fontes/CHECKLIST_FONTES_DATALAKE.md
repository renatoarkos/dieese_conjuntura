# Checklist de Fontes para o Datalake — DIEESE Conjuntura

## Natureza deste documento

Checklist mestre de rastreamento de todas as fontes de dados identificadas até o momento para alimentar o futuro datalake da plataforma (camada SOURCE → RAW, conforme `docs/03-metodologia/ARQUITETURA_AGENTES.md`, Seção 7). Este documento é vivo: cresce a cada lote de Discovery de Fontes executado e deve ser atualizado sempre que uma linha mudar de status.

**Papéis envolvidos na construção e manutenção deste checklist**: Especialista em Fontes & Dados (identificação e validação de fonte), Data Engineer (avaliação de método de acesso e classificação de automação), DIEESE Conjuntura Lead (integração e priorização).

**Base**: os 33 indicadores identificados em `docs/05-indicadores/INVENTARIO_INDICADORES_P1.md` (Discovery de materiais P1), mais os itens já aprofundados em `docs/05-indicadores/CATALOGO_MESTRE_INDICADORES.md` (Discovery de Fontes — Lote Piloto 01). Esta lista **não é exaustiva** — cobre apenas os indicadores identificáveis nos três materiais P1 já lidos; o catálogo completo do DIEESE é maior (ver `docs/00-visao-geral/VISAO_DO_PRODUTO.md`, Seção 5, lista de domínios econômicos ainda não coberta por material lido).

## Legenda

**Status de validação de fonte**:
- 🟢 **CONFIRMADO** — pesquisa direta na fonte oficial já realizada, com teste real de acesso (API/download), registrada em `docs/04-fontes/`.
- 🟡 **CITADO, NÃO VALIDADO** — fonte citada no material interno do DIEESE, ainda não confirmada por pesquisa direta.
- 🔴 **LACUNA** — arquivo-fonte ou processo de origem não localizado no corpus de materiais nem publicamente; depende de obtenção junto ao DIEESE.
- ⚪ **NÃO PRIORIZADO** — indicador identificado, mas fora do escopo de qualquer lote de Discovery de Fontes até o momento.

**Classificação de automação** (escala de `agents/fontes-dados.md`): A — API direta · B — download estruturado · C — microdados · D — exige investigação adicional · E — processo manual/específico.

---

## Bloco 1 — Macroeconomia

| # | Indicador | Instituição | Tabela/série | Método de acesso | Status | Automação | Próxima ação |
|---|---|---|---|---|---|---|---|
| 1 | PIB Mundial e estimativas | FMI — World Economic Outlook | dataflow WEO, indicador NGDP_RPCH | API SDMX 3.0 confirmada | 🟢 CONFIRMADO (Lote 05a) | A | Nenhuma — piloto executado (codelist de país é refinamento futuro) |
| 2 | PIB Brasil — variação índice de volume trimestral | IBGE — Contas Nacionais Trimestrais | SIDRA 5932 | API SIDRA confirmada | 🟢 CONFIRMADO (Lote Piloto 01) | A | Nenhuma — pronto para contrato de dados |
| 3 | UCI — Utilização da Capacidade Instalada | CNI — **Indicadores Industriais** (não ICEI, como citado no material — ver alerta em `fmi-cni.md`) | Série Histórica (Excel mensal) | Raspagem direcionada (link muda todo mês) confirmada | 🟢 CONFIRMADO (Lote 05a) | B | Nenhuma — piloto executado. Corrigir atribuição "ICEI" no material do DIEESE |
| 4a | Volume de vendas — comércio (PMC) | IBGE | SIDRA 8881 | API SIDRA confirmada | 🟢 CONFIRMADO (Lote 02) | A | Nenhuma — piloto executado |
| 4b | Volume de vendas — serviços (PMS) | IBGE | SIDRA 5906 | API SIDRA confirmada | 🟢 CONFIRMADO (Lote 05c) | A | Nenhuma — piloto executado |
| 4c | Volume de vendas — indústria (PIM) | IBGE | SIDRA 8888 | API SIDRA confirmada | 🟢 CONFIRMADO (Lote 05c) | A | Nenhuma — piloto executado — trio PMC/PMS/PIM completo |
| 5 | PIB per capita | IBGE | SIDRA 21777 **não existe mais** | tabela 21777 retorna erro; candidato 6784 confirmado mas não validado como intenção do DIEESE | 🔴 LACUNA (fonte original) | D (21777) / A hipótese (6784) | **QF08** (validação humana) |
| 6 | Taxa de câmbio (venda, média de período) | BCB | SGS (candidatas 3694/3698) | API SGS confirmada | 🟢 CONFIRMADO (Lote Piloto 01) | A | Confirmar rótulo textual exato da série antes de uso em produção |
| 7 | Balança comercial brasileira | MDIC (Comex Stat) — SECEX é a secretaria dentro do MDIC | CSV oficial por NCM/ano | API existe (metadados confirmados); endpoint agregado requer POST (não testado); CSV oficial confirmado e testado | 🟢 CONFIRMADO (Lote 05b) | B confirmado / A hipótese | Nenhuma para B — piloto executado via CSV |
| 8 | Limite fiscal (prudencial/máximo) por Estado | SICONFI (Tesouro Nacional) | RGF — Relatório de Gestão Fiscal | API REST (Oracle ORDS) confirmada e testada com dados reais | 🟢 CONFIRMADO (Lote 05b) | A | Nenhuma — piloto executado (27 UFs) |

## Bloco 2 — Estatísticas Monetárias e Crédito

| # | Indicador | Instituição | Tabela/série | Método de acesso | Status | Automação | Próxima ação |
|---|---|---|---|---|---|---|---|
| 9a | Taxa Selic | BCB | SGS 4189 (nov/2015-jul/2024) + SGS 432 (ago/2024+) | API SGS confirmada, fonte exata identificada por comparação de 122 valores reais | 🟢 CONFIRMADO (Lote Piloto 01 + validação de dados 2026-09-22) | A | Nenhuma — QF03b (motivo da troca de série) não bloqueia automação |
| 9b | Taxa de juros real (Selic × IPCA, efeito Fisher) | — (transformação, não fonte) | fórmula própria do DIEESE | não aplicável — depende de 9a e 14 | 🟡 depende de 9a | não aplicável | Resolver 9a primeiro |
| 10 | Endividamento e comprometimento de renda das famílias | BCB (família RNDBF, SGS 29034/29265/29037) e PEIC/FecomercioSP | "Tabela 27" sem correspondência literal confirmada; família RNDBF é candidata | Ambas partes confirmadas via API/download | 🟢 CONFIRMADO (Lotes 05c + 06a) | A (BCB) + B (PEIC) | Nenhuma — piloto executado para as duas partes. Confirmar qual série RNDBF é a "Tabela 27" exata |
| 11 | Taxas médias de juros por modalidade (PF/PJ) | BCB/SGS | 20728, 22019, 20741, 20742 | API SGS confirmada | 🟢 CONFIRMADO (Lote 03) | A | Nenhuma — piloto executado |
| 12 | NFSP — Necessidade de Financiamento do Setor Público | BCB | 5474 citado pelo DIEESE **não catalogado oficialmente**; candidatos 5760/5750 com escopos diferentes | API responde para 5474, mas não confirmável; 5760/5750 catalogados e testados | 🔴 LACUNA (ambiguidade de escopo) | D (5474) / A hipótese (5760, 5750) | **QF07** (validação humana) — decidir entre "setor público consolidado" (5760) e "Governo Federal e BC" (5750) |
| 13 | Saldo de crédito do SFN | BCB | SGS 20539/20541/20540/20542/20593/20570 (6 séries) | API SGS confirmada | 🟢 CONFIRMADO (Lote 06a) | A | Nenhuma — piloto executado. 3 recortes adicionais (PJ-livres, PJ-direcionados, PF-direcionados) não testados |

## Bloco 3 — Inflação e Custo de Vida

| # | Indicador | Instituição | Tabela/série | Método de acesso | Status | Automação | Próxima ação |
|---|---|---|---|---|---|---|---|
| 14 | IPCA e subgrupos | IBGE | SIDRA 7060 | API SIDRA confirmada | 🟢 CONFIRMADO (Lote Piloto 01), com divergência de pesos-base a validar | A (índice geral/grupos oficiais); D ("Serviços"/"Monitorados") | **QF05/QF06** (validação humana) |
| 15 | INPC, ICV e outros (síntese) | IBGE (SIDRA 7063), FGV (via BCB/SGS 189, só IGP-M), INDATEND (manual) | Ver `docs/04-fontes/fgv-indatend.md` | 3 sub-fontes confirmadas separadamente | 🟢 CONFIRMADO (Lote 06b, mista) | A (INPC) + A (IGP-M via BCB) + E (INDATEND) | Nenhuma — piloto executado para INPC e IGP-M. INDATEND permanece manual por natureza |
| 16 | Estimativas (nowcasting) INPC/IPCA | IBGE e BC (dado) + elaboração própria | Sistema de Expectativas de Mercado (Focus), API Olinda | Insumo bruto confirmado via API (Lote 05c); a estimativa em si é elaboração do DIEESE | 🟢 CONFIRMADO (insumo, Lote 05c) | A (insumos, piloto executado); C (a estimativa em si, exige julgamento) | Nenhuma para o insumo — a fórmula de nowcasting do DIEESE permanece elaboração própria não documentada |
| 17 | ICV — Índice do Custo de Vida | DIEESE (elaboração própria) | Tabela 4 — Var. Anual | processo interno do DIEESE, não é fonte externa | 🟡 CITADO, NÃO VALIDADO | E | Obter metodologia de cálculo do ICV junto ao DIEESE — não é uma pesquisa de fonte pública |
| 18 | PIB trimestral x Selic (cruzamento) | — (justaposição de 2 e 9a) | — | não aplicável — é composição de dois indicadores já cobertos | — | não aplicável | Resolver PIB (✓) e Selic (pendente) |
| 19 | Cesta básica x salário mínimo | DIEESE/Conab — boletim público mensal | `dieese.org.br/analisecestabasica/{ano}/{ano}{mes}cestabasica.pdf` | Download direto confirmado e testado; Tabela 1 do boletim contém exatamente o indicador (% SM líquido, tempo de trabalho) | 🟢 CONFIRMADO — fonte pública real, piloto executado | B | Nenhuma — piloto executado. Arquivo interno `SM e Cesta desde 1979` ainda mais completo historicamente, mas não é mais bloqueante |
| 20 | Preços de combustíveis | ANP — "últimas 4 semanas" (gasolina/etanol, diesel/GNV, GLP) | `.../shpc/qus/ultimas-4-semanas-{produto}.csv` | Download direto confirmado e testado (222 links extraídos da página real) | 🟢 CONFIRMADO — fonte pública real, piloto executado | B | Nenhuma — piloto executado. IPEADATA descartado (granularidade anual incompatível) |
| 21 | ICT — Índice da Condição do Trabalho | DIEESE (elaboração própria) | Boletim trimestral público em `dieese.org.br/analiseict/` — arquivo interno `.xls` ausente do corpus | Fonte pública oficial confirmada (HTTP 200), mas só PDF vetorizado/HTML de texto — sem tabela extraível | 🟢 CONFIRMADO — fonte pública, sem automação (investigação pós-Lote 06) | E | Nenhuma pesquisa adicional útil — formato do PDF impede A/B. **QF32** segue relevante para obter o arquivo interno estruturado |

## Bloco 4 — Mercado de Trabalho (PNAD Contínua)

| # | Indicador | Instituição | Tabela/série | Método de acesso | Status | Automação | Próxima ação |
|---|---|---|---|---|---|---|---|
| 22 | Taxa de desocupação | IBGE — PNAD Contínua | SIDRA 4093 | API SIDRA e API Agregados confirmadas | 🟢 CONFIRMADO (Lote Piloto 01) | A | Nenhuma — piloto executado |
| 23 | População e posição na ocupação | IBGE — PNAD Contínua | SIDRA 4097 | API SIDRA confirmada | 🟢 CONFIRMADO (Lote 02) | A | Nenhuma — piloto executado |
| 24 | Taxa de participação na força de trabalho | IBGE — PNAD Contínua | SIDRA 6461 | API SIDRA confirmada | 🟢 CONFIRMADO (Lote 02) | A | Nenhuma — piloto executado |
| 25 | Rendimento médio real habitual do trabalho principal | IBGE — PNAD Contínua (bruto, já deflacionado pelo IBGE) + deflacionamento adicional DIEESE | SIDRA 5440 | Chamada de valores testada e confirmada (233 registros); piloto executado (2026-09-23) | 🟢 CONFIRMADO — piloto executado, com alerta de dupla deflação | A (bruto IBGE); E (deflacionamento DIEESE) | **QF04** (validação humana) — obter Nota Técnica DIEESE. Motor de coleta já resolvido, pendência é só metodológica |
| 32 | Taxa de sindicalização | IBGE — PNAD Contínua anual (módulo Características Adicionais do Mercado de Trabalho) | SIDRA 8676 | API SIDRA confirmada, valor de 2024 (8,9%) cruzado exatamente com o slide do material | 🟢 CONFIRMADO — fonte pública real, piloto executado | A | Nenhuma — piloto executado. Único indicador do catálogo original sem nenhuma fonte agora resolvido |

## Bloco 5 — Novo CAGED

| # | Indicador | Instituição | Tabela/série | Método de acesso | Status | Automação | Próxima ação |
|---|---|---|---|---|---|---|---|
| 26 | Evolução do salário médio de admissão/desligamento | Novo CAGED — MTE/PDET (SEPRT é o mesmo produtor, nome antigo) | "3. Tabelas" (workbook mensal) — nome interno "TABELA 9" não confirmado | Sem API; workbook via pasta Google Drive instável (B/D); microdados via FTP confirmado e estável (C, exige processamento próprio) | 🟢 CONFIRMADO — sem API (Lote 04) | B/C (não A) | **QF09** — não incluído no piloto por instabilidade da fonte de tabelas prontas |
| 27 | Saldo de admissões/desligamentos por grupamento de atividade | Novo CAGED — MTE/PDET | idem — "TABELA 1", "TABELA 2", "TABELA 6.1" não confirmadas | idem | 🟢 CONFIRMADO — sem API (Lote 04) | B/C (não A) | idem — ver `docs/04-fontes/mte-caged.md` |

## Bloco 6 — Greves e Negociação Coletiva (bloco de maior lacuna)

| # | Indicador | Instituição | Tabela/série | Método de acesso | Status | Automação | Próxima ação |
|---|---|---|---|---|---|---|---|
| 28 | Valor médio dos pisos salariais por categoria | DIEESE — boletim mensal público "De Olho nas Negociações", slide "Pisos salariais" (edição 67, abr/2026), **lido diretamente** — piso médio R$ 1.846 / mediano R$ 1.719, 1º tri/2026 | `dieese.org.br/boletimnegociacao/{ano}/boletimnegociacao{n}.pdf` | **Teste técnico confirmado**: `pdftotext -layout -enc UTF-8` extrai texto real e limpo; piloto de coleta executado com sucesso (edição 72, set/2026) | 🟢 CONFIRMADO — piloto executado (2ª rodada, 2026-09-23) | B | Extração dos números do texto (STAGING) ainda não implementada. Alerta: valores antigos citados por terceiros (R$ 1.867/R$ 1.736, boletim nº 68) seguem NÃO confirmados — não usar |
| 29 | Número de greves | SAG — DIEESE (sistema interno); publicação pública "Balanço das Greves" (EP 111/2024, EP 112/1S2025) | `dieese.org.br/estudosepesquisas/...greves.pdf` — fonte pública confirmada | PDF baseado em imagem (JPEG), sem tabela extraível sem OCR | 🟢 CONFIRMADO — fonte pública, sem automação (investigação pós-Lote 06) | E | Nenhuma pesquisa adicional útil — formato do PDF impede A/B/C sem OCR. **QF19-QF22** seguem relevantes para o SAG estruturado |
| 30 | Principais categorias grevistas | idem | idem | idem | 🟢 CONFIRMADO — fonte pública, sem automação | E | idem |
| 31 | Principais reivindicações das greves | idem | idem | idem | 🟢 CONFIRMADO — fonte pública, sem automação | E | idem |
| 33 | Distribuição de reajustes salariais em negociação coletiva | DIEESE — boletim mensal público "De Olho nas Negociações", slides "Reajustes salariais"/"Variação real média" (edição 67, abr/2026), **lido diretamente**; Mediador/MTE reconfirmado sem API/exportação em massa; dados.gov.br (CKAN) exige token institucional (401) | `dieese.org.br/boletimnegociacao/{ano}/boletimnegociacao{n}.pdf` | **Teste técnico confirmado**: `pdftotext -layout -enc UTF-8` extrai texto real e limpo; piloto de coleta executado com sucesso (edição 72, set/2026) | 🟢 CONFIRMADO — piloto executado (2ª rodada, 2026-09-23) | B | Extração dos números do texto (STAGING) ainda não implementada. Números de terceiros sobre volume de instrumentos (90,5 mil etc.) seguem NÃO confirmados — tratar como pista, não dado |

---

## Síntese de status (33 indicadores do catálogo P1, atualizado após Lotes 02-06 + investigação de lacunas completa)

| Status | Quantidade | Indicadores |
|---|---|---|
| 🟢 CONFIRMADO (fonte identificada, com API/download) | 27 | PIB Brasil, IPCA, Câmbio, Selic, Desocupação, Rendimento médio real (Lote Piloto 01); PMC-comércio, Posição na ocupação, Taxa de participação (Lote 02); Juros por modalidade (Lote 03); PIB Mundial, Comex Stat, SICONFI, PMS, PIM, Expectativas Focus (Lote 05); INPC, IGP-M (via BCB), Endividamento parte BCB, Saldo de crédito SFN (Lote 06); Cesta básica, Combustíveis, **Taxa de sindicalização (novo)** |
| 🟢 CONFIRMADO (fonte identificada, sem API/instável) | 3 | Salário médio admissão/desligamento, Saldo CAGED por grupamento (Lote 04 — FTP microdados); UCI/CNI (raspagem direcionada); Endividamento parte PEIC (download estruturado) |
| 🟢 CONFIRMADO (fonte manual/pública sem tabela extraível) | 3 | INDATEND (sem fonte pública, E definitivo); ICT; Greves — número/categorias/reivindicações (PDF-imagem, sem OCR) |
| 🟢 CONFIRMADO (fonte identificada, com API/download) — **atualizado** | 29 | (mesma lista anterior) + **Reajustes salariais e Pisos salariais em negociação coletiva (2ª rodada Mediador, 2026-09-23)** — boletim "De Olho nas Negociações", texto extraível confirmado por teste técnico, piloto de coleta executado com sucesso (edição 72, set/2026) |
| 🟡 CITADO, NÃO VALIDADO | 4 | Poucos itens do bloco Macroeconomia restante |
| 🔴 LACUNA (sem nenhuma fonte pública identificada) | 2 | PIB per capita, NFSP — ambos com ambiguidade de escopo que exige decisão do usuário (QF07, QF08), não falta de pesquisa |
| Não aplicável (transformação/cruzamento) | 2 | Juros real (9b), PIB x Selic (18) |
| — | 33+ | Total |

**26 scripts de piloto técnico** (`pipelines/ingestao/`), organizados em 5 blocos — ver `docs/08-decisoes-adr/0002-expansao-piloto-por-blocos.md`. Todos testados e executados com sucesso.

**Marco final desta rodada de investigação de lacunas**: dos 11 indicadores 🔴 LACUNA no início da sessão, restam apenas **2** — e ambos não são mais "falta de pesquisa", são decisões de escopo que dependem do usuário (QF07 para NFSP, QF08 para PIB per capita). **Todos os 33 indicadores do catálogo P1 original já passaram por investigação de fonte.**

**Marco (2ª rodada, 2026-09-23 — reinvestigação Mediador/MTE)**: Reajustes salariais e Pisos salariais deixam de ser "PDF sem tabela extraível"/"sem fonte corrente" e passam a classificação **B** — o próprio DIEESE calcula e publica os dois indicadores mensalmente no boletim "De Olho nas Negociações", com metodologia documentada, e o teste técnico (`pdftotext -layout -enc UTF-8`) confirmou camada de texto real extraível, diferente do ICT e do Balanço das Greves (PDF-imagem). Piloto de coleta implementado e executado com sucesso, elevando o total de scripts de 25 para 26 e o total de indicadores automatizáveis (A/B/C) de 27 para 29.

**Achado transversal da investigação de lacunas**: 3 dos 4 indicadores antes marcados como LACUNA "cega" (Cesta Básica, ICT, Greves) na verdade têm fonte pública oficial do próprio DIEESE — a lacuna real não era de existência de dado público, mas de o material interno usar um processo diferente (arquivo próprio) do produto institucional público equivalente. Apenas Sindicalização e Negociação Coletiva/Reajustes/Pisos permanecem sem nenhuma fonte pública identificada.

## Achados da checagem de completude do corpus histórico (2026-09-22)

Verificação de amostra (4 apresentações ATR_Conjuntura de 2020, 2022, 2023 e 2024, mais 2 planilhas "Definitivo" de outros meses de 2025) contra o catálogo de 33 indicadores — ver `research/notas/DISCOVERY_FONTES_LOTE_PILOTO_01.md`, Seção 9, para o relatório completo. **Conclusão geral: o catálogo está razoavelmente completo** para os eixos centrais e recorrentes (atividade, mercado de trabalho, inflação, crédito/juros, câmbio, fiscal, greves). Itens pontuais identificados como possivelmente descontinuados, não incluídos no checklist:

| Indicador candidato | Presente em | Ausente em | Observação |
|---|---|---|---|
| IBC-Br (Índice de Atividade Econômica do BC) | 2022.09 | 2020, 2023.12, 2024.02, dez/2025 | Proxy mensal de PIB, indicador padrão de mercado — descontinuado no material recente |
| PIB de São Paulo | 2020, 2022 | 2023.12, 2024.02, dez/2025 | Recorte regional específico |
| Impacto de juros sobre a dívida pública | 2020 | anos seguintes | Distinto de NFSP (item 12) |
| Taxa composta de subutilização da força de trabalho | 2020 | anos seguintes | Indicador IBGE/PNAD mais amplo que taxa de desocupação simples |

Nenhum destes foi pesquisado quanto à fonte nesta rodada — ficam registrados como candidatos para decisão futura (incluir no checklist e pesquisar, ou tratar como descontinuados por decisão editorial do DIEESE — requer confirmação humana).

**Achado adicional relevante**: a organização interna das planilhas "Definitivo" do DIEESE mudou entre jul/2025 (4 workbooks temáticos separados, numeração de aba própria) e set/dez-2025 (workbook único consolidado, numeração T2-T45) — evidência de mudança de processo de consolidação, não de indicador perdido. Também foi localizado um candidato forte para a fonte de Cesta Básica: `SM e Cesta desde 1979_06_25.xlsx`, aba "dados Cesta e SM" — reforça o achado já registrado na Rodada 2 do Discovery de materiais (`VALIDACAO_TECNICA_P1.md`, Frente G.1).

## Lotes de Discovery de Fontes

- **Lote 02 (SIDRA padrão) — ✅ CONCLUÍDO 2026-09-22**: itens 4a, 9a (parte IPCA já do Lote Piloto 01), 23, 24 confirmados. Item 5 (PIB per capita) revelou tabela inexistente — vira lacuna, não confirmação.
- **Lote 03 (BCB) — ✅ CONCLUÍDO 2026-09-22**: item 11 confirmado (4 séries, maior confiança do checklist). Item 12 (NFSP) revelou ambiguidade de escopo — vira lacuna com decisão pendente.
- **Lote 04 (CAGED/MTE) — ✅ CONCLUÍDO 2026-09-22**: itens 26, 27 — fonte confirmada (MTE/PDET), mas **sem API**. Workbook de tabelas prontas distribuído via pasta Google Drive instável (não é URL fixa); único caminho automatizável estável é o FTP de microdados brutos, que exige processamento próprio. Não entrou no piloto técnico — ver `docs/04-fontes/mte-caged.md` e QF09.
- **Lote 05 (institucionais diversas) — ✅ CONCLUÍDO 2026-09-22**: itens 1 (FMI — A), 3 (CNI — B, alerta de atribuição ICEI corrigido), 4b/4c (PMS/PIM — A, trio completo), 7 (Comex Stat — B confirmado/A hipótese), 8 (SICONFI — A), 10 parte PEIC (B), 16 (BC Expectativas/Focus — A). Não cobertos neste lote: item 10 parte BCB/Tabela 27, item 13 (saldo de crédito SFN), item 15 (síntese multi-fonte de inflação, inclui a fonte por e-mail INDATEND).
- **Lote de Lacunas (depende de ação humana, não de pesquisa)** — itens 19-21, 28-33: dependem de obtenção de arquivo/documento/acesso a sistema junto ao DIEESE (perguntas já registradas em `QUESTIONARIO_VALIDACAO_HUMANA_P1.md` e `DISCOVERY_FONTES_LOTE_PILOTO_01.md`).
- **Lote de Decisões de Escopo (não é pesquisa, é decisão humana)** — itens 5 (PIB per capita: aceitar 6784?) e 12 (NFSP: 5760 ou 5750?) — a pesquisa já esgotou o que dava para confirmar; falta decisão da equipe do DIEESE (QF07, QF08).
- **Lote 06 (crédito e síntese de inflação) — ✅ CONCLUÍDO 2026-09-22**: item 10 completo (Tabela 27/BCB — família RNDBF, 3 séries, mais PEIC já confirmado); item 13 completo (Saldo de crédito SFN, 6 séries); item 15 completo (síntese de inflação separada em 3 sub-fontes: INPC via IBGE, IGP-M via BCB, INDATEND confirmado como manual/sem fonte pública).

## Observação sobre completude

Este checklist cobre apenas os 33 indicadores identificáveis nos três materiais P1 já lidos. `VISAO_DO_PRODUTO.md`, Seção 5, lista domínios econômicos mais amplos (distribuição de renda, desenvolvimento regional, proteção social, mercados financeiros, economia internacional além de câmbio/comércio) que **não têm nenhum indicador correspondente neste checklist** — não porque sejam irrelevantes, mas porque ainda não foram objeto de nenhuma rodada de Discovery de materiais ou de fontes. Um checklist verdadeiramente completo do escopo da plataforma exigirá uma rodada de Discovery adicional sobre materiais P2/P3 (ver priorização em `research/notas/INVENTARIO_MATERIAIS.md`, Seção 9) e/ou levantamento direto de requisitos com a equipe do DIEESE.
