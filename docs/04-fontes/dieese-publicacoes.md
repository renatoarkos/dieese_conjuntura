# Fontes: Publicações públicas do próprio DIEESE (Cesta Básica, ICT, Balanço das Greves e Negociação Coletiva)

**Data de consulta**: 2026-09-22 (investigação de lacunas conhecidas, pós-Lote 06).

## Contexto

Dois indicadores estavam registrados como 🔴 LACUNA no checklist (arquivo-fonte interno exato não localizado no corpus de 339 materiais). Esta investigação buscou uma alternativa: **o próprio DIEESE publica esses dados publicamente em seu site institucional?** Resposta confirmada: **sim, para ambos** — mas em formato que não permite automação de coleta de dados (PDF vetorizado/imagem, sem tabela extraível).

## Cesta básica x salário mínimo (Pesquisa Nacional da Cesta Básica de Alimentos, DIEESE/Conab)

| Campo | Valor |
|---|---|
| Status | **Fonte pública confirmada e testada — piloto executado.** Diferente de ICT e Greves (abaixo), esta é a fonte **já usada pelo próprio DIEESE**, não apenas um candidato — é o produto institucional público do DIEESE (em parceria com a Conab desde 2024/2025), correspondendo diretamente ao indicador citado no material ("Cesta básica x salário mínimo, elaboração DIEESE"). |
| Conteúdo confirmado por leitura direta do PDF | Boletim "Análise Mensal da Cesta Básica de Alimentos — CONAB e DIEESE", 27 capitais desde ago/2025 (antes, 17 capitais). **Tabela 1** traz, por capital: valor da cesta, variação mensal, **"Porcentagem do Salário Mínimo Líquido"**, **"Tempo de trabalho"** (h:min necessários), variação no ano e em 12 meses — exatamente o indicador citado pelo material do DIEESE. Também calcula o "salário mínimo necessário" (correlato). |
| Método de acesso | Download direto de PDF público, sem login, nome de arquivo previsível: `dieese.org.br/analisecestabasica/{ano}/{ano}{mes}cestabasica.pdf`. Testado e confirmado via `urllib` puro (sem bloqueio, diferente do domínio `gov.br` que tem WAF). |
| Índice de boletins | `dieese.org.br/analisecestabasica/analiseCestaBasicaAnteriores.html` — remonta a pelo menos 2005. |
| Dado granular (produto × cidade) | Confirmado que, desde abr/2018, **não é mais público** — exige assinatura, exceto entidades sindicais filiadas. **Não afeta este indicador**, que usa apenas o dado agregado (% do SM, tempo de trabalho), disponível no boletim público. |
| Periodicidade | Mensal. |
| Histórico | Boletins públicos desde pelo menos 2005; arquivo interno do DIEESE (`SM e Cesta desde 1979[...]`) provavelmente cobre período mais longo (desde 1979) — os boletins PDF isolados exigiriam agregação manual de dezenas de arquivos para reconstruir uma série tão longa. |
| **Classificação de automação** | **B — download estruturado**, confirmado e testado, piloto executado (`pipelines/ingestao/bloco_3_inflacao/coleta_cesta_basica_dieese.py`, com detecção automática do mês mais recente publicado). Extração da tabela de dentro do PDF é tarefa de STAGING, não desta coleta. |

## ICT — Índice da Condição do Trabalho

| Campo | Valor |
|---|---|
| Status | **Fonte pública oficial identificada** — muda de LACUNA para fonte confirmada, mas automação permanece limitada. |
| Página institucional | `dieese.org.br/analiseict/ict.html` — página-índice oficial do ICT-DIEESE, confirmada (HTTP 200), lista boletins trimestrais desde pelo menos 2019/2012 (há também estudo cobrindo 2012-2018). |
| Conteúdo | Boletins em HTML (texto/resumo) e PDF. **PDF confirmado como vetorizado/gráfico** (Adobe Illustrator, FlateDecode/Type1C) — os valores do índice aparecem em infográfico, não em tabela de texto plano extraível. |
| Periodicidade | Trimestral. Boletins numerados sequencialmente (nº 8 em jan/2023 até nº 18 em jan/2026, referente ao 3º trimestre de 2025). |
| **Classificação de automação** | **E — manual.** Nenhum caminho A/B confirmado — não há planilha/CSV publicado, apenas boletim em PDF gráfico/HTML de texto corrido. |
| **Alerta de qualidade de pesquisa** | A ferramenta de busca mencionou, em texto-resumo (não em fonte real listada), um valor específico de ICT para 1T/2026 — **não confirmado por leitura direta de página primária**. Não incorporar esse número a nenhum documento do projeto sem reconfirmação. |

## Balanço das Greves (SAG-DIEESE)

| Campo | Valor |
|---|---|
| Status | **Fonte pública oficial identificada** — muda de LACUNA para fonte confirmada, mas automação permanece limitada. |
| Publicação | "Balanço das Greves", série de "Estudos e Pesquisas" (EP) do DIEESE, elaborada a partir do mesmo Sistema de Acompanhamento de Greves (SAG) citado no material interno. |
| URLs confirmadas (fetch direto, HTTP 200) | `dieese.org.br/estudosepesquisas/2025/estPesq111greves.pdf` (EP 111, "Balanço das Greves de 2024", ~1MB, 31 páginas — **ano completo mais recente confirmado**); `dieese.org.br/estudosepesquisas/2026/estPesq112greves.html` (EP 112, "Balanço das greves do 1º semestre de 2025" — **período parcial mais recente confirmado**). |
| Conteúdo | **PDF confirmado como baseado em imagem** (JPEG/DCTDecode) — tabelas e gráficos embutidos como imagem, exigiria OCR para extração, não é texto/tabela nativamente extraível. |
| Periodicidade | Semestral/anual (relatório de ano completo + relatório de 1º semestre separado). Numeração sequencial de EP remonta a pelo menos 2020 (EP 99). |
| **Classificação de automação** | **E — manual.** PDF-imagem, sem planilha/CSV encontrado. |
| **Alerta de qualidade de pesquisa** | A ferramenta de busca mencionou, em texto-resumo, um suposto "EP 114 — Balanço das greves de 2025 — abril/2026" com números específicos (1.006 greves, alta de 14%) — **a URL testada diretamente retornou 404**. Esse EP/dado **não foi confirmado e não deve ser tratado como real** até verificação direta. Classificado como possível alucinação da ferramenta de busca — registrado aqui exatamente para que não seja reintroduzido por engano em rodada futura. |

## Distribuição de reajustes salariais em negociação coletiva

| Campo | Valor |
|---|---|
| Status | **Fonte pública oficial identificada e reconfirmada (2ª rodada, 2026-09-23)** — melhor do que se imaginava: o próprio DIEESE já calcula e publica o indicador pronto, mensalmente. |
| Publicação | "De Olho nas Negociações" (Boletim de Negociação), série mensal pública do DIEESE — mesmo padrão institucional do ICT e do Balanço das Greves. |
| URLs confirmadas (fetch direto) | `dieese.org.br/boletimnegociacao/2026/boletimnegociacao65.pdf` (edição fev/2026, 316,7 KB) e **`dieese.org.br/boletimnegociacao/2026/boletimnegociacao67.pdf`** (edição "nº 67 – Abril de 2026", 17 slides, baixado e lido página a página na 2ª rodada). Sequência contínua confirmada de edições nº 65-68 (fev-mai/2026) e nº 06 (2021) — histórico desde pelo menos 2021. Padrão de URL previsível: `dieese.org.br/boletimnegociacao/{ano}/boletimnegociacao{n}.pdf`. |
| Conteúdo confirmado por leitura direta (edição 67) | Slides "Reajustes salariais" e "Variação real média": série mensal completa abr/25-mar/26, com % de instrumentos abaixo/igual/acima do INPC, variação real média, quebra por setor econômico (comércio/indústria/rural/serviços) e por região geográfica. Rodapé de cada gráfico: "Fonte: MTE, Mediador — Elaboração: DIEESE". Nota metodológica (última página, citação literal): *"Dados analisados pelo DIEESE a partir dos instrumentos coletivos registrados no Mediador, do Ministério do Trabalho e Emprego, até 9 de abril de 2026"*; usa o INPC/IBGE como referência de inflação; documenta o tratamento de reajustes escalonados/parcelados. |
| ✅ Teste técnico confirmado (2026-09-23) | A 1ª rodada (edição 65) havia classificado o PDF como "majoritariamente imagem/binário, sem texto extraível" — **essa avaliação estava errada**, ou a edição 65 difere da 67. Teste direto com `pdftotext -layout -enc UTF-8` sobre a edição 67 (`bn67.pdf`) extraiu texto limpo, correto e completo — todos os números de reajustes e pisos, por setor e região, mais as notas metodológicas — confirmando camada de texto real, não imagem. Script de coleta (`coleta_negociacao_coletiva_dieese.py`) testado em execução real e encontrou corretamente a edição 72 (setembro/2026, dados até agosto/2026), validando a lógica de busca por número de edição sequencial. |
| Mediador/MTE (fonte citada no material) | Reconfirmado nas duas rodadas: o sistema Mediador **não tem API nem exportação em massa** — formulário de consulta manual, unitário. `dados.gov.br` (CKAN) exige token Bearer institucional mesmo para busca de leitura (HTTP 401 confirmado via `curl` direto) — não é caminho viável sem credencial própria do DIEESE. Nenhum painel BI, "Radar" ou API nova do MTE/CTPS Digital encontrado. |
| Pista não incorporada — termo de fomento MTE-DIEESE | Notícias de terceiros (contec.org.br, contabeis.com.br) mencionam um termo de fomento MTE-DIEESE para a série "Boas Práticas em Negociações" (24 boletins temáticos) e números agregados ("90,5 mil instrumentos coletivos 2023-2025", "75 mil acordos e 16 mil convenções") — **não confirmados em fonte primária** (página oficial do MTE ficou atrás de "Conteúdo Restrito" em todas as tentativas). Tratar como pista de que o DIEESE tem algum acesso estruturado ao Mediador (possivelmente via sistemas internos SACC/SAS), não como dado. |
| Periodicidade | Mensal. |
| Histórico | Desde pelo menos 2021 (edição nº 06) até set/2026 (edição nº 72, confirmada por execução real do piloto técnico, dados até ago/2026). |
| **Classificação de automação** | **B — download estruturado, confirmado e testado, piloto executado** (`pipelines/ingestao/bloco_4_mercado_trabalho/coleta_negociacao_coletiva_dieese.py`, com detecção automática da edição mais recente por número sequencial, âncora edição 67 = abr/2026). Mesmo padrão da Cesta Básica. Não precisa de scraping do Mediador nem de parceria nova — o boletim do próprio DIEESE já resolve ambiguidades (instrumentos multissetoriais, reajustes escalonados) melhor do que uma reconstrução externa. Extração da tabela de dentro do PDF (texto → número) é tarefa de STAGING, não desta coleta. |

## Valor médio dos pisos salariais por categoria

| Campo | Valor |
|---|---|
| Status | **Fonte pública oficial identificada e confirmada (2ª rodada, 2026-09-23)** — muda de "nenhuma fonte corrente confirmada" (D) para o mesmo achado do indicador de reajustes: o boletim "De Olho nas Negociações" cobre pisos salariais também, e isso agora foi **lido diretamente**, não apenas suposto. |
| Candidato 1 — SACC | "Sistema de Informações para Acompanhamento das Negociações Coletivas no Brasil", projeto histórico DIEESE-MTE. Continua **sem série corrente** (relatórios localizados cobrem só 2004-2008), mas a 2ª rodada observou que `dieese.org.br/sacc/pesquisa.do?method=setup` responde com uma **tela de erro do próprio sistema**, não um "fora do ar" genérico — pode valer revisita futura, mas não é necessário: o boletim mensal (candidato 2) já resolve o indicador. |
| Candidato 2 — Boletim "De Olho nas Negociações" (**confirmado**) | Slide "Pisos salariais" da edição 67 (lido diretamente): piso médio e mediano nacional — **R$ 1.846 / R$ 1.719 no 1º trimestre de 2026** —, aberto por setor econômico e por região geográfica. Nota metodológica explícita: considera apenas um valor por instrumento coletivo quando há mais de um piso definido, e exclui pisos de estagiário/aprendiz. Mesmo rodapé de fonte: "Fonte: MTE, Mediador — Elaboração: DIEESE". |
| **ALERTA — números antigos permanecem não confirmados, não usar** | Os valores citados na 1ª rodada (piso médio R$ 1.867 / mediano R$ 1.736, jan-abr/2026, boletim nº 68) vieram de fonte secundária (artigo de terceiro) e **seguem não confirmados** — não foram reencontrados nem contradizem diretamente os novos números (edições diferentes: 67 vs. 68), mas continuam fora de qualquer documento do projeto até confirmação direta na fonte primária. Os números **R$ 1.846 / R$ 1.719** acima, ao contrário, foram lidos diretamente do PDF baixado (edição 67) e podem ser usados como confirmados para aquele trimestre/edição específicos. |
| **Classificação de automação** | **B — download estruturado, confirmado e testado, piloto executado** (mesmo script do indicador de reajustes — os dois vêm do mesmo boletim/PDF). |

## Síntese

| Indicador | Status anterior | Status atual (pós 2ª rodada, 2026-09-23) | Classificação de automação |
|---|---|---|---|
| Cesta básica x salário mínimo | 🔴 LACUNA | **Fonte pública confirmada e piloto executado** | B — download estruturado |
| ICT | 🔴 LACUNA | Fonte pública oficial identificada (DIEESE) — PDF-imagem, sem texto extraível | E — manual |
| Greves (número, categorias, reivindicações) | 🔴 LACUNA | Fonte pública oficial identificada (DIEESE — Balanço das Greves) — PDF-imagem, sem texto extraível | E — manual |
| Reajustes salariais em negociação coletiva | 🔴 LACUNA | **Fonte pública confirmada, texto extraível testado, piloto executado** (DIEESE — "De Olho nas Negociações") | B — download estruturado |
| Pisos salariais por categoria | 🔴 LACUNA | **Fonte pública confirmada, texto extraível testado, piloto executado** (mesmo boletim) | B — download estruturado |

**Importante**: a 2ª rodada não deu API ao Mediador (continua sem) — deu algo melhor: os dois indicadores já vêm **calculados** pelo próprio DIEESE, com metodologia documentada, sem precisar reconstruir a lógica de negócio (instrumentos multissetoriais, pisos múltiplos, exclusões) por conta própria. Testado tecnicamente com `pdftotext -layout -enc UTF-8`: o PDF tem camada de texto real (diferente do ICT e do Balanço das Greves, que são imagem). Piloto de coleta implementado e executado com sucesso (`pipelines/ingestao/bloco_4_mercado_trabalho/coleta_negociacao_coletiva_dieese.py`). Próximo passo técnico (STAGING, não coberto por este piloto): extrair os números do texto (regex sobre o layout de `pdftotext`, similar ao que a Cesta Básica vai precisar). Se o projeto precisar de granularidade maior que setor/região (ex. por categoria/sindicato específico), o caminho é pedido interno à equipe do DIEESE que produz o boletim (provável ligação aos sistemas SACC/SAS internos), não engenharia de scraping externo.
