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
| Status | **Fonte pública oficial identificada** — muda de LACUNA para fonte confirmada, mas automação permanece limitada. |
| Publicação | "De Olho nas Negociações" (Boletim de Negociação), série mensal pública do DIEESE — mesmo padrão institucional do ICT e do Balanço das Greves. |
| URLs confirmadas (fetch direto) | `dieese.org.br/boletimnegociacao/2026/boletimnegociacao65.pdf` (316,7 KB, baixado). Sequência contínua confirmada de edições nº 65-68 (fev-mai/2026) e nº 06 (2021) — histórico desde pelo menos 2021. |
| Conteúdo | **PDF confirmado como majoritariamente imagem/binário incorporado** — mesmo padrão do ICT e Greves, não extraível como texto/tabela via fetch automatizado. |
| Mediador/MTE (fonte citada no material) | Confirmado que o sistema Mediador **não tem API nem exportação em massa** — é formulário de consulta manual, unitário (um instrumento coletivo por vez). As únicas "APIs" encontradas em `servicos.gov.br` são metadados do catálogo de serviços (descrição, legislação), não dados de negociação coletiva. |
| Periodicidade | Mensal. |
| Histórico | Desde pelo menos 2021 (edição nº 06) até mai/2026 (edição nº 68, mais recente confirmada). |
| **Classificação de automação** | **E — manual.** Fonte pública oficial existe (boletim DIEESE regular), mas PDF sem tabela extraível automaticamente. O Mediador em si não produz a distribuição agregada — só consulta unitária. |

## Valor médio dos pisos salariais por categoria

| Campo | Valor |
|---|---|
| Status | **Parcialmente investigado — nenhuma fonte corrente confirmada.** Dois candidatos, ambos com problema. |
| Candidato 1 — SACC | "Sistema de Informações para Acompanhamento das Negociações Coletivas no Brasil", projeto histórico DIEESE-MTE. **Testado e confirmado FORA DO AR** (`dieese.org.br/sacc/pesquisa.do?method=setup` retorna página de erro). Relatórios históricos localizados ("Balanço de pisos salariais negociados") cobrem apenas **2004-2008** — projeto descontinuado, não serve para série corrente. |
| Candidato 2 — Boletim "De Olho nas Negociações" | Mesmo boletim mensal do indicador de reajustes (acima) — pode cobrir pisos salariais também, mas **não confirmado diretamente**: o PDF não pôde ser lido como tabela (mesmo bloqueio binário/imagem). |
| **ALERTA — dado não confirmado, não usar** | Uma busca citou, via fontes secundárias (artigos de terceiros, não o DIEESE diretamente), valores específicos de piso médio (R$ 1.867) e mediano (R$ 1.736) para jan-abr/2026 do boletim nº 68. **O agente não conseguiu confirmar esses números na fonte primária** (PDF não extraível) — tratar como hipótese não verificada, não como dado real. Mesmo padrão de cautela já aplicado ao caso do "EP 114" de greves nesta sessão. |
| **Classificação de automação** | **D — não confirmado** (SACC fora do ar; cobertura de pisos no boletim mensal não verificada). Se a equipe do DIEESE confirmar que o boletim cobre pisos regularmente, passaria a **E — manual** (mesmo padrão dos demais boletins). |

## Síntese

| Indicador | Status anterior | Status atual | Classificação de automação |
|---|---|---|---|
| Cesta básica x salário mínimo | 🔴 LACUNA | **Fonte pública confirmada e piloto executado** | B — download estruturado |
| ICT | 🔴 LACUNA | Fonte pública oficial identificada (DIEESE) | E — manual |
| Greves (número, categorias, reivindicações) | 🔴 LACUNA | Fonte pública oficial identificada (DIEESE — Balanço das Greves) | E — manual |
| Reajustes salariais em negociação coletiva | 🔴 LACUNA | Fonte pública oficial identificada (DIEESE — "De Olho nas Negociações") | E — manual |
| Pisos salariais por categoria | 🔴 LACUNA | Parcialmente investigado — SACC descontinuado, boletim não confirmado | D — não confirmado |

**Importante**: esta mudança de status não resolve a lacuna de automação — apenas confirma que existe uma fonte pública e oficial (o próprio DIEESE) que poderia, em tese, ser consultada manualmente ou via OCR/extração de PDF em uma fase futura de engenharia. Não substitui o arquivo interno do SAG/ICT como fonte de dado estruturado, e não responde às perguntas já registradas (Q19-Q22 em `QUESTIONARIO_VALIDACAO_HUMANA_P1.md`) sobre o processo interno real do DIEESE.
