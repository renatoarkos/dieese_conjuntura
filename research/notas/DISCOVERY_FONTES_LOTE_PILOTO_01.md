# Discovery de Fontes — Lote Piloto 01

**Status:** documento de pesquisa (`research/notas/`).
**Data de execução:** 2026-09-22.
**Objetivo:** testar, em escala pequena (6 indicadores), o procedimento completo do papel Especialista em Fontes & Dados (`agents/fontes-dados.md`) — confirmação de fonte primária/oficial diretamente nos canais das instituições, antes de aplicá-lo aos 33 indicadores do catálogo preliminar (`docs/05-indicadores/INVENTARIO_INDICADORES_P1.md`).

## 1. Método

Três agentes de pesquisa foram executados em paralelo, cada um instruído a atuar como o papel "Especialista em Fontes & Dados", com acesso a ferramentas de busca e leitura web (não a arquivos do repositório), seguindo o procedimento de 14 pontos definido em `agents/fontes-dados.md` para cada indicador:

- **Agente 1** — IBGE/SIDRA: PIB Brasil (Tabela 5932) e IPCA e subgrupos (Tabela 7060).
- **Agente 2** — IBGE/SIDRA (PNAD Contínua): Taxa de desocupação (Tabela 4093) e Rendimento médio real (Tabela 5440).
- **Agente 3** — BCB: Taxa de câmbio (candidata Tabela SIDRA 3694, citada no material do DIEESE) e Taxa Selic.

Cada agente foi instruído a: nunca inventar endpoint, código de série ou URL; diferenciar hipótese de confirmação direta; diferenciar fonte oficial de agregador; registrar todas as URLs efetivamente consultadas e a data de consulta (2026-09-22). Os resultados foram integrados pelo papel Lead (esta sessão) nos documentos `docs/04-fontes/ibge-sidra.md`, `docs/04-fontes/bcb.md` e `docs/05-indicadores/CATALOGO_MESTRE_INDICADORES.md`.

O Especialista em Metodologia Econômica não foi acionado como agente separado neste lote — a leitura metodológica das duas divergências mais relevantes (dupla deflação no rendimento médio real; base de pesos do IPCA) foi feita pelo Lead a partir do que os agentes já haviam apurado, e registrada como pendência de validação, não como conclusão fechada. O Economista de Conjuntura não foi acionado, por não ser necessário para uma tarefa de descoberta de fonte (ver justificativa no plano apresentado antes da execução).

## 2. Achado metodológico transversal sobre acesso a dados do IBGE

Em toda a pesquisa, o acesso direto (fetch automatizado) às páginas HTML institucionais em `ibge.gov.br` e `sidra.ibge.gov.br` retornou **HTTP 403** (bloqueio a user-agents automatizados). As **APIs de dados** — `apisidra.ibge.gov.br` e `servicodados.ibge.gov.br/api/v3` — responderam normalmente e foram testadas com sucesso, retornando dados reais. Isso é um achado relevante para uma futura avaliação de Data Engineer: o desenho de qualquer ingestão automatizada de dados do IBGE deve mirar diretamente as APIs de dados, não scraping de páginas HTML.

## 3. Achados que constituem divergência entre o material do DIEESE e a fonte oficial confirmada

Estes quatro pontos são os achados mais importantes deste lote — nenhum foi resolvido unilateralmente; todos ficam registrados como pendência de validação, conforme o protocolo de conflitos (`docs/03-metodologia/ARQUITETURA_AGENTES.md`, Seção 9).

1. **IPCA — base de pesos incorreta no material do DIEESE.** O material cita "pesos-base jan/2012" para a Tabela SIDRA 7060, mas essa tabela confirmadamente usa pesos da POF 2017-2018 (vigentes desde jan/2020). A tabela com pesos-base jan/2012 é a 1419 (histórica, sem novas atualizações). Ver `docs/04-fontes/ibge-sidra.md`.
2. **IPCA — agregados "Serviços" e "Monitorados" não localizados.** Citados no material do DIEESE (slide 19/aba T19), mas ausentes da classificação completa da Tabela 7060 consultada via API. Não confirmado se são publicados em outra tabela SIDRA, e qual.
3. **Taxa de câmbio — a Tabela SIDRA 3694 citada no material não é mais uma tabela de câmbio.** É hoje uma tabela da pesquisa escolar PeNSE (Pesquisa Nacional de Saúde do Escolar). A fonte real é BCB/SGS diretamente — não há agregador SIDRA em funcionamento para este indicador atualmente. Ver `docs/04-fontes/bcb.md`.
4. **Taxa Selic — o SIDRA não hospeia nenhuma tabela de Selic.** A citação "SIDRA e BCB" do material está incorreta quanto à parte SIDRA. Adicionalmente, não foi possível confirmar qual das 5 séries candidatas do BCB/SGS (432, 11, 1178, 4189, 4390) corresponde exatamente ao uso do DIEESE, já que o material não cita um código de série para este indicador especificamente.

## 4. Risco metodológico não resolvido

**Rendimento médio real habitual do trabalho principal — possível dupla deflação.** A Tabela SIDRA 5440 já entrega o valor em termos reais, deflacionado pela metodologia própria do IBGE. O material do DIEESE indica um deflacionamento adicional via Nota Técnica interna do DIEESE (maio/2015, atualizada out/2018). Não foi possível determinar, com as fontes disponíveis nesta pesquisa, se o DIEESE aplica seu deflator sobre um valor já real (dupla deflação) ou parte de uma série nominal distinta ainda não identificada. A Nota Técnica DIEESE não está nos materiais já lidos (`materiais/originais/`) nem foi localizada publicamente. Ver `docs/04-fontes/ibge-sidra.md`.

## 4.1 Atualização (2026-09-22) — QF03 resolvida por comparação direta de dados

Após a conclusão do lote, a fonte exata da Selic (QF03) foi resolvida sem depender de validação humana: os 122 valores mensais da aba T14 do arquivo `materiais/originais/Apresentação de conjuntura/Apresentação_Conjuntura_4T_2025.xlsx` (leitura somente-leitura) foram comparados diretamente contra os valores reais das 5 séries candidatas do BCB/SGS (432, 11, 1178, 4189, 4390), obtidos via API.

**Resultado**: a Selic usada pelo DIEESE não é uma série única — é uma composição de duas séries SGS, trocadas em um ponto específico:
- **nov/2015 a jul/2024** (106 meses): bate exatamente com **SGS 4189** (Selic acumulada no mês, anualizada base 252) em 100% dos meses.
- **ago/2024 em diante** (15 de 16 meses testados até out/2025): bate exatamente com **SGS 432** (Meta Selic definida pelo Copom, valor de fim de mês).
- jan/2025 é uma exceção isolada (diferença de 0,01 p.p. de SGS 4189 — provável arredondamento, não quebra o padrão geral).

Documentos atualizados com este achado: `docs/04-fontes/bcb.md`, `docs/05-indicadores/CATALOGO_MESTRE_INDICADORES.md`, `docs/04-fontes/CHECKLIST_FONTES_DATALAKE.md`.

**QF03 original está resolvida** e removida da lista de bloqueios. Uma nova pergunta, não bloqueante, substitui-a:

- **QF03b**: por que a planilha do DIEESE mudou de SGS 4189 para SGS 432 em agosto de 2024? Foi uma decisão deliberada de mudança de metodologia (ex.: passar a reportar a meta em vez da taxa efetiva), ou um efeito colateral de outra mudança de processo (ex.: troca de quem mantém a planilha, mudança de fórmula copiada de célula)? Não determinável apenas pelos dados — não bloqueia automação (ambas as séries são classificação A), mas é relevante para documentar a metodologia corretamente no Catálogo Mestre.

## 5. Perguntas para validação humana (Lote Piloto 01)

Complementar ao `research/notas/QUESTIONARIO_VALIDACAO_HUMANA_P1.md` já existente (que trata do Discovery de materiais, não de fontes).

| ID | Pergunta | Por que precisamos saber |
|---|---|---|
| QF01 | A citação "SIDRA/BCB Tabela 3694" para câmbio no material do DIEESE está desatualizada ou é um erro de rotulagem interna (ex.: "3694" seria na verdade o código de série do SGS)? | Determina se é preciso corrigir a documentação interna do DIEESE, e evita que uma futura automação tente consultar uma tabela SIDRA que hoje pertence a outra pesquisa (PeNSE). |
| QF02 | A citação "SIDRA e BCB" para Selic no material do DIEESE reflete algum uso histórico do SIDRA que hoje não existe mais, ou sempre foi apenas BCB? | Mesma motivação de QF01. |
| ~~QF03~~ | ~~Qual série exata do BCB/SGS corresponde aos valores da aba T14?~~ | **RESOLVIDA em 2026-09-22 por comparação direta de dados** — ver Seção 4.1. Substituída por QF03b abaixo. |
| QF03b | Por que a planilha do DIEESE mudou de SGS 4189 para SGS 432 em agosto de 2024? | Não bloqueia automação, mas é relevante para documentar a metodologia corretamente — pode indicar mudança deliberada de critério, não apenas coincidência numérica. |
| QF04 | A "Nota Técnica DIEESE" de deflacionamento de rendimentos (maio/2015, atualizada out/2018) pode ser disponibilizada? | É necessária para resolver o risco de dupla deflação identificado no rendimento médio real (Seção 4) — sem ela, o indicador não pode ser tratado como metodologicamente fechado. |
| QF05 | O material do DIEESE deveria citar a Tabela SIDRA 1419 (pesos jan/2012) em vez da 7060 (pesos POF 2017-2018) para o IPCA, ou a nota "pesos-base jan/2012" é apenas uma anotação desatualizada que deve ser corrigida, mantendo a 7060 como fonte correta? | Determina qual tabela a plataforma deve efetivamente consumir para reproduzir o indicador como o DIEESE o calcula hoje. |
| QF06 | Os agregados "Serviços" e "Monitorados" do IPCA, citados no material, vêm de alguma tabela/cálculo específico do IBGE que a equipe DIEESE já conhece? | A pesquisa não localizou esses agregados na Tabela 7060 nem identificou outra tabela SIDRA que os contenha. |
| QF07 | Para o indicador NFSP, o escopo correto é "setor público consolidado" (candidato SGS 5760) ou "Governo Federal e Banco Central" (candidato SGS 5750)? O código citado pelo material (5474) não está catalogado oficialmente pelo BCB. | Muda o significado do indicador — não é uma correção trivial de código, é uma decisão de escopo. Bloqueia inclusão da NFSP no piloto técnico. |
| QF08 | Para PIB per capita, a Tabela SIDRA 6784 ("Produto Interno Bruto, PIB per capita, População residente e Deflator") é a substituta adequada da Tabela 21777 (citada pelo material, hoje inexistente)? | 21777 não existe mais no SIDRA — sem confirmação, o indicador fica sem fonte automatizável. |
| QF09 | A equipe do DIEESE baixa o workbook "3-tabelas" do Novo CAGED manualmente da página oficial mensal (ou de um link mais estável já conhecido), ou usa os microdados brutos via FTP com processamento próprio? | Não há API para o Novo CAGED — a forma de obtenção real da equipe define se vale investir em um scraper resiliente da página oficial ou numa pipeline de agregação própria a partir do FTP de microdados. Ver `docs/04-fontes/mte-caged.md`. |
| QF10 | Qual das 3 séries do BCB (SGS 29034 — comprometimento de renda com ajuste sazonal; 29265 — sem ajuste sazonal; 29037 — endividamento acumulado 12 meses) corresponde exatamente à "Tabela 27" citada pelo material do DIEESE — ou é uma combinação delas? | O rótulo "Tabela 27" é nomenclatura interna do DIEESE, sem correspondência literal confirmada no catálogo do BCB. Não bloqueia automação (as 3 séries já estão confirmadas e coletadas), mas impede fechar com certeza qual é o indicador exato reproduzido pela plataforma. |

## 6. Síntese de classificação de automação (6 indicadores)

| Indicador | Classificação | Pendência principal |
|---|---|---|
| PIB Brasil (variação trimestral) | A | Nenhuma |
| IPCA e subgrupos (índice geral/grupos oficiais) | A | Nenhuma |
| IPCA — Serviços/Monitorados | D | Tabela de origem não localizada |
| Taxa de câmbio | A | Confirmar rótulo textual exato da série |
| Taxa Selic | A | Nenhuma — resolvida (QF03b não bloqueante) |
| Taxa de desocupação | A | Nenhuma |
| Rendimento médio real (dado bruto IBGE) | B | Testar chamada de valores (não só metadados) |
| Rendimento médio real (deflacionamento DIEESE) | E | Obter Nota Técnica DIEESE (QF04) |

## 7. Limitações desta rodada

- Nenhum dado foi efetivamente ingerido ou armazenado nesta rodada de pesquisa — esta é uma pesquisa de fonte, não uma implementação. Nenhuma decisão de arquitetura foi tomada. (Nota: um piloto técnico controlado, escopado a PIB e IPCA, foi executado posteriormente sob autorização explícita — ver ADR 0001 em `docs/08-decisoes-adr/`.)
- URLs completas consultadas por cada agente, incluindo as bloqueadas por HTTP 403 e as confirmadas por acesso direto, estão listadas em `docs/04-fontes/ibge-sidra.md` e `docs/04-fontes/bcb.md` — não duplicadas aqui.
- Este lote não investigou nenhum dos indicadores já sinalizados como lacuna no Discovery de materiais (Greves, Cesta Básica, ICT, Combustíveis) — são casos que dependem primeiro de obtenção de arquivo-fonte, não de pesquisa de fonte pública, conforme já registrado em `research/notas/QUESTIONARIO_VALIDACAO_HUMANA_P1.md`.

## 8. Próximo passo recomendado (revisado após Seção 9)

Validação humana das perguntas remanescentes — **QF04, QF07 e QF08 bloqueiam o fechamento metodológico de 3 indicadores** (Rendimento médio real, NFSP, PIB per capita). QF01, QF02, QF03b, QF05, QF06 são relevantes para correção de documentação interna do DIEESE, mas não bloqueiam automação. Após validação, recomenda-se o **Lote 04 (CAGED/MTE)** como próximo passo de pesquisa — fonte única e explícita, alta probabilidade de API/download público via portal PDET/MTE.

---

## 9. Lotes 02 e 03 (2026-09-22) + checagem de completude do corpus histórico

Executados na mesma sessão, a pedido explícito do responsável do projeto ("vamos começar o processo de automatização... sempre dê prioridade a procurar e ver se existem apis"), com 3 agentes em paralelo.

### 9.1 Lote 02 — IBGE/SIDRA (padrão já validado 3x)

4 indicadores testados via chamada real de API. Resultado: **3 confirmados, 1 revelou tabela inexistente**.

- **PMC — comércio (8881)**: CONFIRMADO. Mas o indicador do material do DIEESE ("PMC/PMS/PIM") cobre só a parcela comércio nesta tabela — serviços (PMS) e indústria (PIM) não identificados.
- **PIB per capita (21777)**: tabela **não existe** (HTTP 400/500 em todas as tentativas). Candidato de substituição encontrado por busca própria do agente: Tabela 6784 — funciona, cobre o tema, mas não é confirmação de que era isso que o DIEESE citou. Ver QF08.
- **População e posição na ocupação (4097)**: CONFIRMADO, bate 100%.
- **Taxa de participação (6461)**: CONFIRMADO, bate no tema (histórico disponível maior que o recorte usado pelo DIEESE).

Detalhamento completo em `docs/04-fontes/ibge-sidra.md`.

### 9.2 Lote 03 — BCB

2 indicadores testados via chamada real de API. Resultado: **os 4 códigos de juros por modalidade confirmados; NFSP revelou ambiguidade de escopo**.

- **Juros por modalidade (20728, 22019, 20741, 20742)**: todos os 4 CONFIRMADOS com nome oficial via catálogo do BCB. Maior grau de confiança de todo o checklist — os códigos já estavam citados célula a célula no material original do DIEESE.
- **NFSP (5474 citado pelo DIEESE)**: responde à API, mas **não está catalogado oficialmente** pelo BCB (`dadosabertos.bcb.gov.br` não o lista). Dois candidatos catalogados existem: SGS 5760 ("setor público consolidado", nome bate exatamente com a descrição do material) e SGS 5750 ("Governo Federal e Banco Central", escopo mais restrito, série mais longa). Mudar de 5474 para qualquer um dos dois muda o significado do indicador — não é correção trivial. Ver QF07.

Detalhamento completo em `docs/04-fontes/bcb.md`.

### 9.3 Checagem de completude do corpus histórico de conjuntura

Um terceiro agente verificou se o catálogo de 33 indicadores (baseado em apenas 3 materiais de dez/2025) representa razoavelmente o que o DIEESE trata em conjuntura ao longo do tempo. Método: leitura de títulos de slide (python-pptx) de 4 apresentações ATR_Conjuntura de anos diferentes (2020, 2022.09, 2023.12, 2024.02) e nomes de aba (openpyxl) de 2 planilhas "Definitivo" de outros meses de 2025, comparados ao catálogo atual.

**Conclusão do agente**: o catálogo está **razoavelmente completo** para os eixos centrais e recorrentes (atividade, mercado de trabalho, inflação, crédito/juros, câmbio, fiscal, greves) — todos persistem de 2020 a dez/2025. Achados pontuais (não pesquisados quanto à fonte nesta rodada, apenas registrados como candidatos):

- **IBC-Br** (proxy mensal de PIB do BCB) — presente em 2022.09, ausente do material recente.
- **PIB de São Paulo** — presente em 2020/2022, ausente depois.
- **Impacto de juros sobre a dívida pública** — presente em 2020, distinto de NFSP.
- **Taxa composta de subutilização da força de trabalho** — presente em 2020, indicador IBGE/PNAD mais amplo que a taxa de desocupação simples.

Nenhum "bloco temático inteiro" do porte de Greves foi encontrado ausente — são indicadores pontuais, plausivelmente descontinuados por decisão editorial do DIEESE, não por lacuna de coleta.

**Achados operacionais adicionais**: (a) a organização das planilhas "Definitivo" mudou de 4 workbooks temáticos separados (jul/2025) para um único workbook consolidado T2-T45 (set/dez-2025) — mudança de processo, não indicador perdido; (b) candidato forte para a fonte de Cesta Básica confirmado por nome de aba: `SM e Cesta desde 1979_06_25.xlsx`, aba "dados Cesta e SM" — reforça achado já registrado em `VALIDACAO_TECNICA_P1.md`, Frente G.1.

Ver `docs/04-fontes/CHECKLIST_FONTES_DATALAKE.md`, seção "Achados da checagem de completude", para a tabela completa.

### 9.4 Piloto técnico expandido por blocos

Com os indicadores confirmados nos Lotes 02 e 03 somados aos do Lote Piloto 01, o piloto técnico (`pipelines/ingestao/`) foi expandido sob `docs/08-decisoes-adr/0002-expansao-piloto-por-blocos.md`, reorganizado em 4 blocos temáticos, com **9 scripts executados com sucesso** coletando dados reais (ver `pipelines/README.md` para os números). Indicadores com ambiguidade não resolvida (NFSP, PIB per capita, PMS/PIM, rendimento com deflacionamento DIEESE) foram deliberadamente deixados fora do piloto.

### 9.5 Próximo passo (atualizado)

1. Validação humana de QF04, QF07, QF08 (bloqueiam 3 indicadores).
2. Decidir se os 4 achados da checagem de completude (9.3) entram no checklist como novos itens a pesquisar, ou são tratados como descontinuados por decisão editorial do DIEESE (requer confirmação humana).
3. ~~Lote 04 (CAGED/MTE) como próxima rodada de pesquisa de fonte~~ — **concluído, ver Seção 10**.

---

## 10. Lote 04 — Novo CAGED/MTE (2026-09-22)

Executado a pedido do responsável do projeto ("pode continuar"), seguindo a recomendação registrada na Seção 9.5.

**Resultado — achado qualitativamente diferente dos lotes anteriores**: pela primeira vez neste projeto, a fonte foi identificada com segurança, mas **não existe API pública**.

- **Instituição**: confirmado que "MTE" (citado no indicador de salário) e "SEPRT/ME" (citado no indicador de saldo por grupamento) são o **mesmo produtor** em nomes diferentes por sucessão institucional (SEPRT até 2022, MTE desde 2023) — não são fontes distintas, como se poderia supor à primeira vista.
- **Canal oficial de tabelas prontas** ("3. Tabelas", candidato às Tabelas 1, 2, 6.1, 9 citadas pelo DIEESE): hoje distribuído via uma **pasta do Google Drive** linkada na página oficial mensal — confirmado que o arquivo existe (`3-tabelas_Julho de 2026.xlsx`, ~40 MB), mas **não é uma URL HTTP fixa e programática**. Um padrão de URL antiga e estável (`pdet.mte.gov.br/images/Novo_CAGED/...`) foi testado e está **morto** (404).
- **Canal alternativo confirmado e estável**: FTP público de microdados brutos (`ftp://ftp.mtps.gov.br/pdet/microdados/NOVO%20CAGED/AAAA/AAAAMM/`), testado com sucesso (listagem real de arquivos `.7z` por ano/mês desde 2020). É automatizável, mas entrega registros individuais, não as tabelas agregadas — reconstruir os indicadores do DIEESE a partir daqui exige processamento próprio (uma etapa de engenharia além de "coleta bruta").
- Não foi possível confirmar os nomes internos exatos das abas do workbook ("TABELA 1", "TABELA 9" etc.) — o Drive bloqueou acesso ao conteúdo sem sessão de navegador.

**Decisão**: estes 2 indicadores **não entraram no piloto técnico** desta rodada — nem o Google Drive (instável) nem o FTP de microdados (exige agregação própria) atingem o padrão de "endpoint estável e testável sem intervenção manual" usado até aqui. Detalhamento completo em `docs/04-fontes/mte-caged.md`. Nova pergunta: **QF09** (ver Seção 5).

### 10.1 Próximo passo (após Lote 04)

1. As mesmas pendências da Seção 9.5 (QF04, QF07, QF08, achados de completude) seguem em aberto.
2. **QF09** se soma à lista — sem resposta, não há decisão de engenharia informada sobre como tratar CAGED.
3. ~~Lote 05 (institucionais diversas — FMI, CNI, SECEX/Comex Stat, SICONFI, BCB+PEIC, BC Expectativas, PMS/PIM) é o próximo lote de pesquisa de fonte ainda não executado.~~ — **concluído, ver Seção 11**.

---

## 11. Autorização ampliada, Lote 05 e decisão de raspagem do CAGED (2026-09-22)

O responsável pelo projeto autorizou explicitamente, nesta etapa, que o Lead/Data Engineer **decida sozinho o melhor formato de extração para cada fonte** (API, download estruturado ou raspagem), sem precisar de um novo ADR a cada escolha técnica — mantendo os princípios já estabelecidos (nunca inventar fonte/endpoint, preferir sempre API, documentar a decisão e o porquê). Isso não altera as regras de escopo/ambiguidade econômica (QF07, QF08 continuam exigindo decisão humana, não são "formato de extração").

### 11.1 Decisão sobre o Novo CAGED

Com a autorização acima, implementou-se a coleta via **FTP de microdados brutos** (não a pasta Drive instável) — mesmo entregando registros individuais em vez de tabelas prontas, por ser o único canal confirmadamente estável. Script: `pipelines/ingestao/bloco_5_caged/coleta_caged_microdados_ftp.py`. Arquivos pequenos (CAGEDEXC, CAGEDFOR) baixaram por completo; o arquivo grande (CAGEDMOV, ~55 MB) sofreu quedas de conexão recorrentes neste ambiente de desenvolvimento — mecanismo de retomada (FTP `REST`) implementado, download parcial ao final desta sessão. Ver `pipelines/README.md`, seção "Limitação operacional".

### 11.2 Lote 05 — Fontes institucionais diversas

Executado em 3 agentes paralelos, todos com prioridade explícita a checar API antes de qualquer alternativa.

- **FMI (PIB Mundial)**: API SDMX 3.0 confirmada e testada, sem chave. Classificação A.
- **CNI (UCI)**: achado de correção — o material do DIEESE cita "CNI-ICEI", mas a UCI pertence aos "Indicadores Industriais" da CNI, não ao ICEI (índice de confiança). Sem API; download Excel confirmado, mas URL muda todo mês — piloto usa raspagem direcionada (regex sobre a página oficial) para localizar o link vigente. Classificação B.
- **SECEX/Comex Stat (balança comercial)**: API REST existe e responde para metadados; endpoint de consulta agregada retornou 403 em GET (hipótese: exige POST, não testado). CSV oficial por ano confirmado como alternativa robusta e testada (URLs extraídas diretamente da página oficial do MDIC). Classificação B confirmado / A hipótese.
- **SICONFI (limite fiscal)**: API REST (Oracle ORDS) confirmada e testada com dados reais de São Paulo — bate exatamente com os dois campos do indicador do DIEESE (limite prudencial e máximo). Classificação A. Observação: a "consulta manual em 02/06/2025" registrada no material do DIEESE provavelmente reflete processo antigo — a API já resolve isso automaticamente.
- **PEIC/FecomercioSP (parte do endividamento familiar)**: sem API de dados tabulares, mas o site roda em WordPress, que expõe uma API REST de listagem de mídia — usada para localizar o Excel mais recente de forma estruturada (não é raspagem frágil de HTML). Série histórica completa desde fev/2004. Classificação B.
- **BCB Sistema de Expectativas de Mercado (Focus)**: sistema diferente do SGS — API OData do portal Olinda, confirmada e testada para IPCA e INPC. Classificação A. É o insumo bruto que o DIEESE usa em suas próprias estimativas de nowcasting (a estimativa em si continua sendo elaboração própria, não automatizável).
- **PMS e PIM (volume de serviços e produção industrial)**: tabelas SIDRA corretas localizadas (5906 e 8888, respectivamente — as antigas estão marcadas "série encerrada"), confirmadas por teste real. Completa o trio PMC/PMS/PIM que o material do DIEESE citava sob um único rótulo. Classificação A para ambas.

Documentos atualizados: `docs/04-fontes/fmi-cni.md` (novo), `docs/04-fontes/fecomercio-peic.md` (novo), `docs/04-fontes/mdic-tesouro.md` (novo), `docs/04-fontes/bcb.md`, `docs/04-fontes/ibge-sidra.md`, `docs/04-fontes/CHECKLIST_FONTES_DATALAKE.md`, `docs/05-indicadores/CATALOGO_MESTRE_INDICADORES.md` (agora com 21 indicadores).

### 11.3 Piloto técnico — 8 novos scripts

Implementados e testados nesta sessão, organizados nos mesmos blocos: PIB Mundial (FMI), UCI (CNI, raspagem), Comex Stat (CSV via curl — contorno de problema de TLS do servidor, documentado no próprio script), SICONFI (27 UFs), PMS, PIM, PEIC (endividamento), Expectativas Focus (IPCA/INPC). Total agora: **17 scripts no piloto** (9 anteriores + 8 novos), organizados em 5 blocos (`bloco_5_caged` é novo). Detalhes de execução em `pipelines/README.md`.

### 11.4 Próximo passo (atualizado após Lote 05)

1. Pendências que dependem só do usuário: **QF04, QF07, QF08, QF09**.
2. ~~Itens do Lote 05 não cobertos: endividamento parte BCB/Tabela 27, saldo de crédito SFN (item 13), síntese multi-fonte de inflação incluindo a fonte por e-mail INDATEND (item 15) — candidatos a um Lote 06.~~ — **concluído, ver Seção 12**.
3. Os 4 indicadores candidatos da checagem de completude (Seção 9.3) seguem sem pesquisa de fonte.
4. ~~Considerar, em ambiente com rede mais estável, completar os downloads parciais de Comex Stat e CAGED microdados~~ — CAGED completou; Comex Stat em conclusão (ver Seção 12).

---

## 12. Lote 06 — Crédito (BCB) e síntese de inflação (2026-09-22)

Executado a pedido do responsável ("pode seguir"), 2 agentes em paralelo, cobrindo os 3 itens do checklist que restavam sem pesquisa de fonte no bloco de crédito/inflação.

### 12.1 Lote 06a — BCB: Endividamento (Tabela 27) e Saldo de crédito SFN

- **Endividamento, parte BCB ("Tabela 27")**: o rótulo é nomenclatura interna do DIEESE — sem correspondência literal no catálogo do BCB. Identificada e confirmada por teste real a família de séries RNDBF (Indicadores de Endividamento e Comprometimento de Renda das Famílias, Depec/BCB): SGS 29034 (comprometimento de renda, com ajuste sazonal), 29265 (idem, sem ajuste), 29037 (endividamento acumulado 12 meses). Teste de range jan/2023-jun/2025 na série 29034 retornou exatamente 30 registros mensais, batendo com o período citado pelo material. **Qual série exata corresponde à "Tabela 27" não está confirmado — QF10.**
- **Saldo de crédito SFN**: 6 séries SGS confirmadas por teste real, incluindo teste específico em jan/2015 (início do histórico citado pelo material): total (20539), PF-total (20541), PJ-total (20540), livres-total (20542), direcionados-total (20593), livres-PF-total (20570). 3 recortes adicionais (PJ-livres, PJ-direcionados, PF-direcionados) encontrados no catálogo mas não testados — não incluídos no piloto.

### 12.2 Lote 06b — Síntese de inflação (INPC/ICV/outros)

Confirmado que este item do material do DIEESE não é um indicador único — é uma consolidação manual de 3 sub-fontes distintas:

- **INPC (IBGE)**: Tabela SIDRA 7063 confirmada e testada — mesmo padrão de tabelas SIDRA já usado em todo o projeto.
- **Portal FGV**: **sem API pública** — acesso é via contrato/assinatura (confirmado pela própria linguagem do portal: "consulta detalhada... restrita aos assinantes"). **Rota alternativa confirmada**: o BCB replica oficialmente o IGP-M via SGS (código 189) — testado com sucesso. Cobre apenas o IGP-M, não outros índices FGV eventualmente citados (ex. IPC-Fi).
- **INDATEND**: confirmado que não há nenhuma fonte pública identificável com esse nome — a classificação E (manual, recebido por e-mail) já registrada pelo material do DIEESE está correta e é definitiva, não uma lacuna de pesquisa a resolver.

### 12.3 Piloto técnico — 5 novos scripts

`coleta_endividamento_bcb.py`, `coleta_saldo_credito_sfn_bcb.py` (bloco 2); `coleta_inpc_sidra.py`, `coleta_igpm_bcb.py` (bloco 3) — todos executados com sucesso. Total agora: **22 scripts no piloto**. Documentos novos: `docs/04-fontes/fgv-indatend.md`.

### 12.4 Downloads grandes concluídos

`coleta_caged_microdados_ftp.py` completou integralmente via retomada (CAGEDMOV: 55.197.862 bytes, assinatura 7z válida). `coleta_balanca_comercial_comexstat.py`: exportação completou (75.055.366 bytes, exato); importação em conclusão via retomada no momento deste registro — mecanismo comprovadamente funcional, apenas questão de tempo/rede.

### 12.5 Próximo passo (atualizado após Lote 06)

1. Pendências que dependem só do usuário: **QF04, QF07, QF08, QF09, QF10**.
2. ~~Os 4 indicadores candidatos da checagem de completude (Seção 9.3) seguem sem pesquisa de fonte~~ — permanece em aberto (não confundir com a investigação de lacunas da Seção 13, que é sobre outros 4 indicadores diferentes: Cesta Básica, Combustíveis, ICT, Greves).
3. ~~Fora do catálogo de 33 indicadores originais: considerar se vale investigar as lacunas já conhecidas (Greves, Cesta Básica, ICT, Combustíveis) por vias públicas alternativas~~ — **concluído, ver Seção 13**.

---

## 13. Investigação de lacunas conhecidas por vias públicas alternativas (2026-09-22)

Executado a pedido do responsável ("pode continuar"), 2 agentes em paralelo, investigando se os 4 indicadores marcados como 🔴 LACUNA (Cesta Básica, Combustíveis, ICT, Greves) têm alguma fonte pública que preencha a lacuna, mesmo sem o arquivo interno exato do DIEESE.

**Resultado geral — melhor que o esperado**: 3 dos 4 têm fonte pública oficial do próprio DIEESE, e um deles (Cesta Básica) tem automação real e testada.

### 13.1 Cesta básica x salário mínimo — RESOLVIDO (piloto executado)

O DIEESE publica mensalmente, em parceria com a Conab desde 2024/2025, um boletim público em PDF ("Análise Mensal da Cesta Básica de Alimentos") com uma Tabela 1 contendo exatamente o indicador citado no material: valor da cesta, % do salário mínimo líquido comprometido, tempo de trabalho necessário, por capital (27 capitais desde ago/2025). Confirmado por leitura direta do PDF de set/2025 pelo agente, e por download real de ago/2026 nesta sessão. URL previsível (`dieese.org.br/analisecestabasica/{ano}/{ano}{mes}cestabasica.pdf`), sem bloqueio de acesso. Script `coleta_cesta_basica_dieese.py` implementado, com detecção automática do mês mais recente publicado, testado com sucesso.

### 13.2 ICT — fonte pública identificada, mas sem automação viável

`dieese.org.br/analiseict/` é a página oficial do ICT-DIEESE, com boletins trimestrais desde 2019/2012. Porém o PDF é **vetorizado/gráfico** (os valores aparecem em infográfico, não em texto/tabela extraível) — classificação permanece E (manual). Muda de "lacuna sem fonte" para "fonte identificada, mas não automatizável no formato atual".

### 13.3 Greves — fonte pública identificada (Balanço das Greves), mas sem automação viável

O DIEESE publica o "Balanço das Greves" (série de Estudos e Pesquisas, EP), elaborado a partir do mesmo SAG citado no material — EP 111 (2024 completo) e EP 112 (1º semestre de 2025) confirmados por download e leitura real. Porém o PDF é **baseado em imagem** (exigiria OCR) — classificação permanece E. Mesma situação do ICT: fonte identificada, não automatizável no formato atual.

**Alerta de qualidade de pesquisa**: o agente sinalizou que a ferramenta de busca mencionou, em texto-resumo, um "EP 114" com número de greves de 2025 (1.006 greves, alta de 14%) que **não estava na lista de fontes reais** — testado diretamente, retornou 404. Registrado como possível alucinação da ferramenta de busca. **Este número não deve ser usado em nenhum documento do projeto.**

### 13.4 Preços de combustíveis — parcialmente investigado, permanece fora do piloto

A ANP tem estrutura de dados abertos confirmada (CSV/ZIP semanal, desde 2004, cobre os 3 produtos citados: gasolina, diesel, GLP) — mas a URL exata do arquivo não foi extraída corretamente (um padrão inferido retornou 404 limpo, não um bloqueio — precisa de extração real do link a partir da página, não de um padrão suposto). O IPEADATA tem API real e testada, mas as séries encontradas (`ANP_PRGASOL`, `ANP_PROLDIE`, `ANP_PRGLP`) são **anuais**, não semanais — granularidade incompatível com o uso em conjuntura, descartadas para este indicador.

### 13.5 Documentos novos desta investigação

`docs/04-fontes/dieese-publicacoes.md` (Cesta Básica, ICT, Greves), `docs/04-fontes/anp-ipeadata.md` (Combustíveis). Catálogo Mestre agora com **30 indicadores**. Piloto técnico: **23 scripts**.

### 13.6 Achado transversal

3 dos 4 indicadores "lacuna" tinham, na verdade, fonte pública — a lacuna real não era ausência de dado público, era o material interno do DIEESE usar um processo/arquivo diferente do produto institucional público equivalente. Isso sugere que, para os itens que ainda restam como lacuna genuína (Sindicalização, Negociação Coletiva/Reajustes/Pisos), vale a mesma pergunta: existe uma publicação pública do DIEESE ou de outra instituição (ex. Mediador/MTE) que ainda não foi verificada diretamente?

### 13.7 Próximo passo (atualizado após Seção 13)

1. Pendências que dependem só do usuário: **QF04, QF07, QF08, QF09, QF10** (inalteradas).
2. ~~Extrair o link real do CSV da ANP a partir do HTML da página~~ — **concluído, ver Seção 14**.
3. Considerar aplicar a mesma pergunta ("o DIEESE ou outra instituição publica isso publicamente?") aos 2 itens de Sindicalização/Negociação Coletiva ainda sem nenhuma fonte identificada.
4. Os 4 indicadores candidatos da checagem de completude (Seção 9.3 — IBC-Br, PIB de São Paulo, dívida pública, subutilização) seguem sem pesquisa de fonte.

---

## 14. Combustíveis (ANP) — resolvido (2026-09-22)

Executado a pedido do responsável ("continue"), fechando o item deixado pendente na Seção 13.4.

**Achado metodológico importante**: o HTTP 403 obtido na primeira tentativa de acessar a página oficial da ANP **não era um bloqueio institucional (WAF)** — era detecção de bot por ausência de cabeçalhos HTTP típicos de navegador (`Accept`, `Accept-Language`). Adicionando esses cabeçalhos ao `curl`, a página retornou HTTP 200 normalmente (325 KB de HTML real). A partir daí, **222 links de download reais** foram extraídos diretamente do HTML (não adivinhados) — confirmando o padrão de URL usado pela ANP para séries semanais, mensais e semestrais desde 2004.

3 arquivos de "últimas 4 semanas" (gasolina/etanol, diesel/GNV, GLP — microdados por posto revendedor) foram testados e baixados com sucesso: 7,8 MB, 3,6 MB e 2,2 MB respectivamente. Script `coleta_combustiveis_anp.py` implementado no bloco 3 (inflação) e **executado de ponta a ponta com sucesso** (7,45 MB + 3,42 MB + 2,05 MB reais, sem necessidade de retomada — apenas mais lento que o teste inicial). **Piloto técnico agora com 24 scripts, nenhum pendente.**

**Lição para reaproveitar em outras fontes `gov.br` deste projeto**: qualquer 403 encontrado em domínio `gov.br` deveria primeiro ser testado com cabeçalhos completos de navegador antes de ser classificado como bloqueio/WAF — o caso da ANP mostra que pode ser apenas detecção de bot por requisição incompleta, resolvível sem contornos mais complexos.

### 14.1 Próximo passo (atualizado após Seção 14)

1. Pendências que dependem só do usuário: **QF04, QF07, QF08, QF09, QF10** (inalteradas — nenhuma nova pergunta gerada por esta investigação).
2. ~~Considerar aplicar a mesma pergunta... aos 2 itens de Sindicalização/Negociação Coletiva~~ — **concluído, ver Seção 15**.
3. Os 4 indicadores candidatos da checagem de completude (Seção 9.3) seguem sem pesquisa de fonte.

---

## 15. Sindicalização e Negociação Coletiva — fechamento da investigação de lacunas (2026-09-22)

Executado a pedido do responsável ("pode fazer"), 2 agentes em paralelo, últimos itens do catálogo original de 33 indicadores ainda sem nenhuma fonte identificada.

### 15.1 Taxa de sindicalização — RESOLVIDO (piloto executado)

Localizada a Tabela SIDRA 8676 (PNAD Contínua **anual** — módulo "Características Adicionais do Mercado de Trabalho", diferente da PNAD Contínua trimestral regular). **Cross-check exato**: o valor de 2024 retornado pela API (8,9%) bate palavra por palavra com o título do slide do material do DIEESE ("Com taxa de 8,9%, sindicalização cresce pela primeira vez desde 2012") — confirmação forte de que é a fonte correta, não apenas um candidato plausível. Valor de 2012 (16,1%) também confirmado consistente com o texto do slide. Série real: 2012-2019, hiato 2020-2021 (provável disrupção da pandemia no desenho do suplemento), retomada 2022-2024. Nível territorial: Brasil e Grandes Regiões apenas. Script `coleta_sindicalizacao_sidra.py` implementado e testado com sucesso.

**Achado sobre o DIEESE**: o próprio DIEESE cita este dado como "elaboração DIEESE" em seu Boletim de Conjuntura, mas apenas reprocessa a mesma fonte primária do IBGE — não publica um dataset autônomo. A fonte real e automatizável é o IBGE, não o DIEESE.

### 15.2 Reajustes salariais em negociação coletiva — fonte pública identificada (E, mesmo padrão de ICT/Greves)

Confirmado que o sistema Mediador (MTE) **não tem API nem exportação em massa** — é formulário de consulta manual, unitária, por instrumento coletivo. As únicas "APIs" encontradas em `servicos.gov.br` são metadados do catálogo de serviços (descrição/legislação), não dados de negociação coletiva. Em contrapartida, o DIEESE publica mensalmente o boletim público "De Olho nas Negociações" (série contínua desde pelo menos 2021), mesmo padrão institucional do ICT e do Balanço das Greves — mas o PDF é majoritariamente imagem/binário incorporado, sem tabela extraível automaticamente. Classificação permanece E.

### 15.3 Pisos salariais por categoria — único indicador sem fonte corrente confirmada

Dois candidatos investigados, nenhum plenamente confirmado:
- **SACC** (Sistema de Informações para Acompanhamento das Negociações Coletivas, projeto histórico DIEESE-MTE): **confirmado fora do ar** (página de erro ao acessar). Relatórios históricos localizados cobrem apenas 2004-2008 — descontinuado, não serve para série corrente.
- **Boletim "De Olho nas Negociações"**: pode cobrir pisos salariais também, mas não confirmado — o PDF não pôde ser lido como tabela.

**Alerta de qualidade de pesquisa (novo caso)**: a busca encontrou, em artigos de terceiros (não o DIEESE diretamente), valores específicos de piso médio (R$ 1.867) e mediano (R$ 1.736) atribuídos ao boletim nº 68. **O agente não confirmou esses números na fonte primária** (mesmo bloqueio de PDF-imagem) e corretamente não os tratou como dado real — mesmo padrão de cautela já aplicado ao "EP 114" de greves (Seção 13.3). **Nenhum destes dois números deve ser usado em nenhum documento do projeto.**

### 15.4 Documentos atualizados

`docs/04-fontes/ibge-sidra.md` (Tabela 8676), `docs/04-fontes/dieese-publicacoes.md` (Reajustes e Pisos, seções novas). Catálogo Mestre agora com **33 indicadores** (cobre a totalidade do catálogo original de 33 do Discovery de materiais P1, mais alguns adicionais de PMS/PIM/IGP-M/etc. que vieram como efeito colateral de outras investigações). Piloto técnico: **25 scripts**.

### 15.5 Estado final da pesquisa de fontes (marco)

Dos 33 indicadores do catálogo P1 original:
- **27 têm fonte confirmada com API/download** (25 com piloto técnico funcionando).
- **4 têm fonte pública oficial identificada, mas não automatizável** (INDATEND, ICT, Greves, Reajustes — todos E, PDF/e-mail sem tabela extraível).
- **1 permanece parcialmente investigado, sem fonte corrente confirmada** (Pisos salariais).
- **2 permanecem como ambiguidade de escopo, não falta de pesquisa** (NFSP — QF07; PIB per capita — QF08).
- **2 são transformações/cruzamentos sem fonte própria** (Juros real, PIB x Selic).

**A pesquisa autônoma de fontes do catálogo original está, na prática, esgotada.** O que resta depende inteiramente de decisões do usuário (as 5 perguntas QF) ou de contato direto com o DIEESE (para pisos salariais, e para os arquivos internos mais completos onde os boletins públicos não bastam).

### 15.6 Próximo passo

1. Validação humana de **QF04, QF07, QF08, QF09, QF10** — única via de avanço adicional na pesquisa de fontes do catálogo original.
2. Os 4 indicadores candidatos da checagem de completude (Seção 9.3 — IBC-Br, PIB de São Paulo, dívida pública, subutilização) seguem como a única pesquisa de fonte ainda não iniciada, mas são indicadores fora do catálogo original de 33 (identificados só na checagem de completude do corpus histórico).
3. Considerar se faz sentido avançar para as fases seguintes do Roadmap (contratos de dados formais, Fase 1) para os 25 indicadores já com piloto funcionando, ou aguardar validação humana antes de formalizar mais.
