# Validação Técnica dos Materiais P1 — Rodada 2 do Discovery Profundo

**Status:** documento de pesquisa (`research/notas/`) — não commitado.
**Escopo:** os 3 materiais P1 já usados na Rodada 1 (`Apresentação de conjuntura/ATR_Conjuntura_2025.12.pptx`, `Apresentação de conjuntura/Apresentação_Conjuntura_4T_2025.xlsx` ["principal"], `dieese/Apresentação_Conjuntura_4T_2025 (2).xlsx` ["dieese"]), agora inspecionados no nível da estrutura interna OOXML (ZIP), além do que `openpyxl`/`python-pptx` expõem em alto nível.
**Método:** os três arquivos são pacotes ZIP (OOXML). Foram lidos diretamente com o módulo `zipfile` do Python as partes internas (`docProps/core.xml`, `docProps/app.xml`, `xl/workbook.xml`, `xl/externalLinks/*`, `[Content_Types].xml`, `ppt/charts/*.xml`, `ppt/charts/_rels/*.xml.rels`, `ppt/slides/_rels/*.xml.rels`, `ppt/embeddings/*`), sem nenhuma escrita, conversão ou alteração dos arquivos originais. Nenhum arquivo em `materiais/originais/` foi movido, renomeado ou modificado.
**Não realizado nesta rodada (conforme escopo autorizado):** pesquisa na internet, pesquisa de APIs, escolha de tecnologia, criação de banco de dados, desenvolvimento de código de plataforma, criação de agentes, configuração de Antigravity.

---

## Frente A — Comparação técnica aprofundada: principal × dieese

### A.1 Metadados internos (docProps/core.xml, docProps/app.xml)

| Propriedade | principal | dieese |
|---|---|---|
| `dc:creator` (autor original) | Lucas Capelo | Lucas Capelo |
| `cp:lastModifiedBy` (último editor) | (vazio) | Ricardo Tamashiro |
| `dcterms:created` (criação) | 2015-06-05T18:19:34Z | 2015-06-05T18:19:34Z |
| `dcterms:modified` (última modificação) | 2026-03-19T13:15:10Z | 2026-06-10T12:10:00Z |
| `cp:revision` | 3 | 0 |
| Aplicativo/versão | Collabora_Office/25.04.8.1 (LibreOffice) | Collabora_Office/26.04.1.4 (LibreOffice) |
| Tamanho do arquivo | 457.708 bytes | 750.393 bytes |

**Achado central desta subseção:** os dois arquivos compartilham exatamente o mesmo `dc:creator` e a mesma `dcterms:created` (segundo a milissegundo). Isso é evidência direta de que **os dois arquivos descendem do mesmo arquivo-raiz único**, criado em 2015-06-05, reaproveitado e "rolado para frente" (rolling forward) trimestre a trimestre — e não de dois arquivos independentes produzidos separadamente. Essa conclusão já era sugerida na Rodada 1 por indícios indiretos (nomenclatura, estrutura de abas); aqui ela passa a ter uma evidência técnica direta nos metadados internos do arquivo.

A data de última modificação de "dieese" (2026-06-10) é posterior à de "principal" (2026-03-19). Isso por si só não decide qual arquivo é a referência da apresentação 4T/2025 (ver Frente H) — apenas mostra que "dieese" continuou sendo editado depois de "principal" ter parado de ser modificado, o que é compatível com um arquivo de trabalho vivo, continuamente reaproveitado para edições posteriores ao 4T/2025.

`cp:revision` (contador interno de revisões do LibreOffice/Collabora) está em 3 no "principal" e 0 no "dieese" — este campo não é confiável isoladamente (aplicativos diferentes podem reiniciar o contador) e não deve ser usado como evidência de recência ou de "versão final".

### A.2 Abas: nome, ordem, visibilidade

Extração feita via `xml.etree.ElementTree` sobre `xl/workbook.xml` (elemento `<sheets>`/`<sheet>`), com leitura explícita do atributo `state` (visível/oculta). *Nota metodológica: uma primeira tentativa de extração via regex continha um erro que capturava apenas metade das abas (índices ímpares); o erro foi identificado antes de qualquer conclusão ser tirada e corrigido com um parser XML apropriado — os números abaixo já refletem a versão corrigida.*

- **principal:** 47 abas, todas com `state` ausente/`visible`, exceto **`T4b`**, que está **oculta** (`state="hidden"`).
- **dieese:** 54 abas. Ocultas (`state="hidden"`): **`T4b`, `Ty`, `T4x`, `Planilha1`, `T43`, `T44`**. As demais 48 abas de "dieese" são visíveis.

Abas presentes em "dieese" e ausentes em "principal": `Protegido e desprotegido`, `T18a`, `T27`, `T34`, `T34a`, `T41a`, `T41b`, `Ty`, `T4x`, `Planilha1`.
Abas presentes em "principal" e ausentes em "dieese": `T15b`* , `T40-43`, `T42` (nome de aba isolado — ver nota).

*Nota: "principal" tem `T15a`/`T15b`; "dieese" tem apenas `T15` (sem sufixo a/b) — não é uma aba "ausente" no sentido estrito, é uma aba com nome/particionamento diferente. Ver Frente C para o caso análogo de `T14`.

### A.3 Intervalos nomeados (`<definedNames>`)

Ambos os arquivos declaram os mesmos dois nomes definidos, herdados do arquivo-raiz comum: `base` → `[1]Segmentação!$B$16` e `base1` → `[2]Segmentação!$B$16` (sintaxe de referência externa `[N]NomeDaAba!Célula`, apontando para índices de workbooks externos declarados em `xl/externalLinks/`).

**Uso efetivo verificado:** foi feita varredura por expressão regular em todas as fórmulas de todas as células de ambos os arquivos, procurando (a) a sintaxe bruta de referência externa `[1]`/`[2]` e (b) o uso dos identificadores `base`/`base1` em qualquer fórmula de célula. **Nenhuma ocorrência foi encontrada em nenhum dos dois arquivos.** Conclusão: esses nomes definidos e a referência externa associada são **vestigiais** — sobrevivem nos metadados do workbook (arquivo-raiz de 2015) mas não são utilizados por nenhuma célula ativa nos dois arquivos P1 atuais.

### A.4 Links externos (`xl/externalLinks/`)

Ambos os arquivos declaram exatamente **2 externalLinks**. Em ambos, o alvo (`xl/externalLinks/_rels/externalLinkN.xml.rels`, `TargetMode="External"`) aponta para um arquivo chamado **`Peic_2010.xls`** (caminho relativo, fora do pacote). Este link é o mesmo em "principal" e em "dieese" — reforça a hipótese de arquivo-raiz comum — e, como mostrado em A.3, está vestigial (não referenciado por nenhuma fórmula ativa).

### A.5 Conexões, objetos incorporados, OLE, queries

Varredura de `[Content_Types].xml` e da árvore de pastas do pacote por tipos de conteúdo associados a: `connections.xml`, `queryTable`, `oleObject`, `activeX`, `customXml`, embutimentos (`embeddings/`). **Nenhum dos dois arquivos contém conexões de dados externas (Power Query/ODBC), tabelas de consulta, objetos OLE incorporados ou controles ActiveX.** Os únicos objetos "externos" presentes são os gráficos (`ppt/charts/`, ver Frente D — mas isso pertence ao `.pptx`, não aos `.xlsx`) e os dois external links vestigiais descritos em A.4.

### A.6 Gráficos internos aos próprios arquivos Excel

- **principal:** 222 partes internas no pacote / **47 gráficos** (`xl/charts/chartN.xml`).
- **dieese:** 435 partes internas no pacote / **59 gráficos**.

O maior número de partes e de gráficos em "dieese" é consistente com o maior número de abas e com o fato de ser uma versão cronologicamente mais avançada (mais conteúdo acumulado), não é por si evidência de qualidade superior ou de ser "a versão final".

---

## Frente B — Abas exclusivas de "dieese": investigação individual

Investigação feita com leitura de conteúdo (não apenas nome) de cada aba exclusiva, incluindo estado de visibilidade, presença de fórmulas, presença de gráficos e amostras de linhas. **Instrução seguida à risca: nenhuma conclusão de "rascunho" foi tirada apenas pelo nome da aba** — o critério usado foi evidência de conteúdo (visibilidade, fórmulas, dados, título interno da tabela).

| Aba | Estado | Dimensões | Fórmulas | Gráficos | Conteúdo identificado |
|---|---|---|---|---|---|
| `Ty` | oculta | A1:I15 | 0 | 0 | Tabela "Evolução do saldo por grupamento de atividades econômicas — Indústria — com ajustes — Acumulado do Ano (2025)", fonte Novo Caged/MTE. Dados colados (sem fórmulas). |
| `T4x` | oculta | A1:I27 | 0 | 0 | Tabela análoga a `Ty`, mas para "Serviços", com **17 subcategorias** detalhadas (inclui "Informação, comunicação e atividades financeiras", "Atividades Administrativas...", "Atividades Profissionais...", "Atividades Imobiliárias" etc., que `T43` não tem). |
| `T43` | oculta | A1:E17 | 0 | 0 | Mesma tabela de "Serviços com ajustes", **mas um subconjunto de `T4x`**: mantém a linha-total "Serviços" e apenas as categorias agregadas que aparecem no slide 44 ("Alojamento e alimentação", "Transporte...", "Serviços domésticos", "Outros serviços", bloco "Administração pública..."), omitindo as subcategorias mais granulares presentes em `T4x`. |
| `Planilha1` | oculta | A1:A1 (vazia) | 0 | 0 | Aba vazia de 1 célula — resquício técnico (nome padrão gerado por incorporação/colagem de objeto do LibreOffice/Excel), sem conteúdo analítico. |
| `T44` | oculta | A1:E14 | 0 | 1 | "TABELA 2 — ADMISSÕES, DESLIGAMENTOS E SALDO POR NÍVEL GEOGRÁFICO — DEZEMBRO DE 2025". Nota: o rótulo interno da tabela já cita **dezembro de 2025**, um mês além do período coberto pela apresentação 4T/2025 (que vai até out/2025 nas abas de CAGED de "principal"). |
| `T18a` | visível | A1:W131 | 127 | 1 | "IPCA, Taxa Selic e Juros Real", série `nov-15` a `mar-26`. Ver Frente C — é o conteúdo que em "principal" está na aba `T14`. |
| `T27` | visível | A2:I397 | 747 | 1 | 397 linhas, série "Mês / Salário Mínimo / Cesta Básica em São Paulo / SM÷Cesta", 1994–2026 (última observação: jun/2025 na coluna, com estrutura continuando até 2026 no índice de mês). Ver Frente G — corresponde ao bloco "Cesta Básica" do Sumário. |
| `T34` / `T34a` | visíveis | A1:E31 / A1:C12 | 0 / 0 | 0 / 0 | Tabelas rotuladas como extração direta do SIDRA/IBGE ("Tabela 6402...", "Tabela 4094...") sobre força de trabalho/ocupação — dados colados de tabelas SIDRA, sem fórmulas. |
| `T41a` / `T41b` | visíveis | A2:NY41 / A2:N86 | 0 / 2 | 0 / 1 | Tabelas de apoio ao bloco de admissão/desligamento (Novo Caged), `T41b` com 1 gráfico próprio. |
| `Protegido e desprotegido` | **visível** | A2:O37 | 61 | 3 | "Tabela 2 — Inserção da força de trabalho e proteção do emprego", Mil Pessoas, Brasil, série a partir de `1T/2018`. Aba **substantiva**: visível, com 61 fórmulas ativas e 3 gráficos próprios — é um indicador legítimo e trabalhado (proteção/desproteção do emprego, PNAD Contínua), não um teste. |

**Correção em relação à hipótese registrada na Rodada 1:** o documento `COMPARACAO_EXCEL_P1.md` (Rodada 1) especulou que abas de nome incomum como `Ty`, `T4x` e `Protegido e desprotegido` eram "sugestivas de rascunho/teste" com base principalmente no nome. A evidência de conteúdo da Rodada 2 **não sustenta essa hipótese para `Protegido e desprotegido`**, que é uma aba visível, com fórmulas e gráficos próprios — um indicador de pleno direito, apenas com um nome que não segue o padrão `T<número>`. Já para `Ty` e `T4x`, a hipótese de que sejam material auxiliar/de bastidor (não indicadores finais) é **reforçada por evidência independente do nome**: ambas estão ocultas, sem fórmulas, contêm dados colados, e seu conteúdo é uma versão mais granular/bruta do que aparece consolidado em `T43` (que também está oculta) — ou seja, `Ty`/`T4x` parecem abas de **preparação/estágio intermediário** de tabelas CAGED que foram posteriormente resumidas em `T43`/`T44` (também ocultas) para uso nos slides. Isso é uma inferência sobre função editorial, apoiada em evidência de conteúdo (granularidade, ausência de fórmulas, sobreposição de dados com a aba "resumo"), não uma afirmação categórica sobre a intenção de quem criou as abas.

---

## Frente C — Divergência em `T14`

**Pergunta:** o que explica `T14` conter, em "principal", uma série de Selic/IPCA/juros real, e em "dieese", uma série de endividamento familiar por faixa de renda?

**Evidência levantada:**
1. `T14` em "principal": conteúdo = Selic, IPCA e taxa de juros real, `dez/2016`–`out/2025` — corresponde exatamente ao título e ao período do **slide 14** da apresentação ("Selic, IPCA e taxa de juros real, dez/2016-out/2025").
2. `T14` em "dieese": conteúdo = "Endividamento Familiar, por Faixa de Renda" (fonte CNC) — tema que em "principal" ocupa a aba `T15a` (endividamento/comprometimento de renda, fonte BCB-DSTAT/IBGE e PEIC-Fecomércio).
3. O conteúdo de Selic/IPCA/juros real **não desapareceu** em "dieese" — ele está presente, visível, com 127 fórmulas ativas e um gráfico, na aba `T18a`, com a série estendida até `mar/2026` (ou seja, além do período coberto pela apresentação 4T/2025).
4. A ordem das abas em "dieese" (`T18` seguido de `T18a`) mostra `T18a` inserida logo após o bloco de crédito (`T18`), fisicamente distante de onde `T14` está posicionada no início do workbook.

**Classificação segundo os critérios definidos na tarefa (A–E):**
- **A (uma substituiu a outra):** não se aplica — o conteúdo de "principal"/`T14` não foi descartado em "dieese", apenas realocado.
- **B (indicadores diferentes):** aproximadamente correto no nível da *etiqueta* `T14` (os dois arquivos têm, sob o mesmo rótulo, indicadores diferentes), mas isso por si só sugere um problema de nomenclatura/reorganização, não duas linhas de pesquisa paralelas e independentes.
- **C (mudança metodológica):** não há evidência de mudança de metodologia nos indicadores em si — Selic/IPCA/juros real continua calculada com a mesma estrutura de fórmulas (apenas em outra aba), e endividamento por faixa de renda é um indicador que já existia em "principal" (`T15a`, embora com fonte BCB/PEIC em vez de CNC — possível mudança de fonte, não confirmável com os materiais lidos).
- **D (versão intermediária):** parcialmente compatível — "dieese" parece ser um estágio posterior do mesmo arquivo em que abas foram reorganizadas.
- **E (evidência insuficiente):** não é o caso — há evidência direta e específica (localização do conteúdo em `T18a`, datas de referência mais avançadas) que permite uma explicação, apenas não headline única A/C/D "pura".

**Conclusão (evitando forçar uma categoria única):** a evidência disponível aponta para uma **reorganização de rótulos de aba ao longo do tempo em um arquivo continuamente reaproveitado**, e não para uma divergência de conteúdo aleatória, um erro de cópia, ou duas linhas de pesquisa paralelas. Em algum momento entre a edição que gerou "principal" (referência 4T/2025) e a edição mais avançada capturada em "dieese", o conteúdo de Selic/IPCA/juros real foi movido da aba `T14` para uma nova aba `T18a`, e a aba `T14` foi reaproveitada para outro indicador (endividamento por faixa de renda). **Não foi possível determinar, apenas com os dois arquivos, se essa realocação ocorreu numa única operação de reorganização do workbook ou gradualmente** — essa é uma pergunta que permanece em aberto para validação humana (ver seção "Dúvidas").

---

## Frente D — Relação técnica Excel ↔ PowerPoint

Inspeção de `ppt/charts/chartN.xml` (elemento `<c:externalData>` e fórmulas de série `<c:f>`) e de `ppt/charts/_rels/chartN.xml.rels` (atributo `TargetMode`) para os **47 gráficos** do `.pptx`.

### D.1 Classificação geral

| Tipo de vínculo | Definição operacional | Nº de gráficos |
|---|---|---|
| **VINCULADO AO EXCEL** | `.rels` do gráfico tem `TargetMode="External"` com caminho para um arquivo `.xlsx`/`.xls` fora do pacote, e a fórmula de série (`<c:f>`) referencia um nome de aba | **43 de 47** |
| **INCORPORADO NO POWERPOINT** | `.rels` do gráfico aponta, via relação interna (`Type=".../relationships/package"`), para um workbook `.xlsx` embutido dentro do próprio `.pptx` (`ppt/embeddings/Microsoft_Excel_WorksheetN.xlsx`) | **2** (charts 29 e 36, slides 28 e 36) |
| **OBJETO NATIVO DO POWERPOINT / IMAGEM ESTÁTICA** | Sem `.rels` de dados externos; fórmulas de série usam apenas rótulos genéricos (`"0"`, `"1"`, `categories`, `label 0`) | **2** (charts 1 e 47, slides 3 e 53) |
| **INDETERMINADO** | — | 0 |

### D.2 Para onde apontam os 43 gráficos "VINCULADO AO EXCEL"

Os caminhos declarados (`Target`, `TargetMode="External"`) revelam nomes de usuário e estruturas de pasta reais dos sistemas de quem produz a apresentação:

- `file:///C:\Users\ricardo.TAMASHIRO\Nextcloud3\Apresentação de conjuntura\Planilhas Definitivas\2025.4T\Apresentação_Conjuntura_4T_2025.xlsx` — maioria dos gráficos (slides 5–9, 11–15, 17–26, 32–34, 37–38, 46, 48, 50–52), mesmo nome de arquivo que "principal".
- `file:///C:\Users\lucascapelo.PRODUCAOTECNICA\Nextcloud3\Apresentação de conjuntura\Planilhas Definitivas\2025.09\Apresentação_Conjuntura_09-25.xlsx` — slides 10 e 41 (um snapshot de **setembro/2025**, anterior ao 4T/2025, indicando que alguns gráficos não foram atualizados para o arquivo do trimestre corrente).
- `https://dieeseorgbr-my.sharepoint.com/personal/lucascapelo_dieese_org_br/Documents/Apresentação_Conjuntura_09-25.xlsx` — slide 11 (uma série do mesmo slide aponta para a cópia local, outra para o SharePoint — mesmo arquivo lógico, dois caminhos de acesso).
- `file:///C:\Users\ricardo\Nextcloud\Apresentação de conjuntura\Planilhas Definitivas\2025.4T\Apresentação_Conjuntura_4T_2025.xlsx` — slides 39 e 40 (perfil de usuário "ricardo", sem o sufixo ".TAMASHIRO" — mesma pessoa, outra máquina/perfil).
- `file:///C:\Users\ricardo.TAMASHIRO\Nextcloud\Conjuntura\Dados\20251127 - Preços combustíveis.xlsx` — slide 29 (combustíveis).
- `file:///C:\Users\ricardo\Nextcloud2\Conjuntura\Dados\2025.12\ICT - Brasil - PNAD Continua - 202503.xls` — slide 31 (ICT).

**Achado relevante:** os nomes de usuário identificados nos caminhos (`ricardo.TAMASHIRO`, `lucascapelo.PRODUCAOTECNICA`, `ricardo`) e o e-mail do SharePoint (`lucascapelo_dieese_org_br`) são consistentes com os nomes já vistos em `dc:creator`/`cp:lastModifiedBy` dos dois arquivos Excel P1 (Lucas Capelo, Ricardo Tamashiro) — reforçando que os três materiais P1 pertencem à mesma cadeia de produção e às mesmas duas pessoas, não a fontes desconhecidas.

Os slides 29 (combustíveis) e 31 (ICT) — marcados na Rodada 1 como "BAIXA confiança / não localizado no Excel P1" — agora têm **fonte externa identificada com nome de arquivo específico**, mesmo que esse arquivo não esteja fisicamente presente no corpus de 339 materiais (ver Frente G para arquivos correlatos encontrados no corpus).

### D.3 Os 2 gráficos incorporados (não vinculados)

- **Slide 28 (chart29, cesta básica):** dados incorporados em um workbook interno mínimo (`ppt/embeddings/Microsoft_Excel_Worksheet1.xlsx`, 8.987 bytes), cuja única aba interna se chama `Planilha1` (nome padrão gerado por colar/incorporar, sem relação com a nomenclatura `T<n>` do Excel P1). Os dados estão congelados no momento em que foram colados — não há vínculo vivo com nenhum arquivo externo.
- **Slide 36 (chart36):** mesma situação, workbook incorporado `Microsoft_Excel_Worksheet2.xlsx` (10.593 bytes), aba interna também chamada `Planilha1`.

### D.4 Os 2 gráficos totalmente estáticos

- **Slide 3 (chart1)** e **slide 53 (chart47):** não têm nenhum `.rels` de dados e usam apenas rótulos de série genéricos e sem célula/aba de origem. São objetos gráficos construídos diretamente no PowerPoint (ou colados como imagem/objeto sem dados subjacentes rastreáveis), sem qualquer vínculo, vivo ou congelado, com uma planilha.

**Nenhum vínculo foi alterado, reparado ou modificado durante esta inspeção**, conforme instruído.

---

## Frente E — Mapa Slide ↔ Aba

Ver documento dedicado: [`MAPA_SLIDE_ABA_P1.md`](./MAPA_SLIDE_ABA_P1.md), com os 58 slides classificados em CONFIRMADO / PROVÁVEL / POSSÍVEL / NÃO IDENTIFICADO.

**Resumo quantitativo** (detalhado no documento dedicado): dos 58 slides, 40 têm ao menos um gráfico com vínculo técnico rastreável (OOXML) a uma aba nomeada; os 18 restantes são slides de título/transição/encerramento (4), slides compostos só por tabela nativa sem gráfico vinculado (11) ou slides de texto corrido (1), além de casos específicos detalhados no mapa.

---

## Frente F — Greves e Negociações Coletivas

**Procedimento:** primeiro, busca por nome/caminho/metadado nos 339 materiais do inventário (`research/notas/inventario_materiais.csv`), com palavras-chave (sem acento): `greve`, `sag`, `negociaca(o)`, `reajuste`, `piso`, `mediador`, `sindical`, `instrumento coletivo`, `dissidio`, `convencao coletiv`. Resultado: **1 arquivo candidato** — `Apresentação de conjuntura/Backup/Outras versões/Dados/Outras/mediador - economicas 2023.xlsx`.

**Leitura seletiva desse arquivo** (não foi feita leitura profunda de nenhum outro material não relacionado):

- 29 abas. Abas centrais: `dados` (10.653 linhas — extração bruta de instrumentos coletivos registrados no sistema Mediador/MTE, com colunas `entrada`, `solicitação`, `nível`, `tipo`, `setor (laboral)`, `atividade (laboral)`, `registro no mediador`, `início/fim da vigência`, `partes`, `região`, `uf`), `painel_instrumentos`, `painel_regiao`, `painel_setor`, `pisos` (valores de pisos salariais mínimos por decil, 2023), `reajustes` (distribuição de reajustes salariais e comparação com INPC-IBGE, por data-base, 2023), `inflacao` (INPC/IPCA/ICV por data-base), além de diversas abas de gráfico (`graf-infl`, `graf1-reaj` … `graf_pisos regiao`).
- **Este arquivo é sobre negociação coletiva (instrumentos, pisos, reajustes salariais) extraída do sistema Mediador/MTE — não sobre greves em si** (não há dado de número de greves, categorias grevistas ou reivindicações). Cobre o ano-calendário de **2023**, não 2025.
- Está em uma pasta de nome `Backup/Outras versões/Dados/Outras`, e sua estrutura de abas (nomes descritivos como `painel_instrumentos`, `reajustes`) é **completamente diferente** da convenção `T<número>` usada nos dois Excel P1.

**Conclusão sobre a origem dos blocos de Greves e Negociações Coletivas (slides 47–57):**
1. A Rodada 2 (Frente D) já havia estabelecido, por evidência técnica direta nas fórmulas de série dos gráficos, que os slides 48, 50, 51 e 52 (greves) referenciam abas `T50`, `T52`, `T53` e `T54` de um workbook do mesmo caminho/nome de "principal" — ou seja, **a origem em planilha desses slides existe**, mas em uma versão do arquivo mais completa/avançada do que qualquer uma das duas cópias P1 disponíveis (que vão até `T45`).
2. A busca no corpus de 339 materiais **não localizou** o arquivo que efetivamente contém `T50`–`T54`, nem um arquivo específico do Sistema de Acompanhamento de Greves (SAG-DIEESE) com dados de 2025.
3. O arquivo `mediador - economicas 2023.xlsx` demonstra que o **DIEESE tem um processo interno recorrente e estabelecido** para produzir exatamente este tipo de painel (instrumentos coletivos, pisos, reajustes vs. INPC, extraídos do Mediador/MTE) — o que é consistente, em termos de metodologia, com o conteúdo dos slides 53–57 (reajustes, pisos por categoria). **Isso não prova, porém, que este arquivo específico de 2023 foi a fonte direta dos slides de 2025** — os nomes de aba não coincidem com a convenção `T<n>`, o ano-calendário é diferente, e o arquivo está numa pasta de "outras versões"/backup.
4. Nenhum arquivo relacionado especificamente a **greves** (contagem, categorias grevistas, reivindicações — a base típica do SAG-DIEESE) foi localizado no corpus de 339 materiais.

**Resultado formal:** origem dos dados de greves = **NÃO LOCALIZADA no corpus atual**, com evidência técnica de que existe (existiu) uma aba de origem em uma versão mais completa do arquivo "principal"/"dieese", ausente do corpus. Origem dos dados de negociação coletiva/reajustes/pisos = **NÃO LOCALIZADA como arquivo-fonte direto**, mas há evidência de metodologia/processo recorrente comparável em `mediador - economicas 2023.xlsx` (ano diferente, estrutura de abas diferente).

---

## Frente G — Cesta Básica

**Procedimento:** busca por palavras-chave (sem acento) `cesta`, `alimentaca(o)`, `preco`, `combustivel`, `gasolina`, `diesel`, `ict`, `condicao do trabalho` no inventário de 339 materiais, seguida de leitura seletiva dos candidatos mais fortes.

### G.1 Cesta Básica — CONFIRMADO

- O Sumário de **ambos** os arquivos Excel P1 (`principal` e `dieese`) declara, na sua tabela de conteúdo interna, a linha `Cesta Básica | T27-T28 | Mensal | jun/2025 | DIEESE` — ou seja, os dois arquivos **já afirmavam** ter esse bloco, mesmo "principal" não contendo mais as abas correspondentes fisicamente.
- A aba `T27` está presente (visível) em "dieese": 397 linhas, colunas "Mês / Salário Mínimo Corrente / Cesta Básica em São Paulo Corrente / Salário Mínimo ÷ Cesta Básica", cobrindo 1994 até a estrutura de índice de 2026 (última observação de valor: jun/2025).
- Um arquivo correlato e **estruturalmente idêntico** foi localizado no corpus, em três pastas de snapshot diferentes: `SM e Cesta desde 1979.xlsx` (pastas `Backup/Dados_2025.03/Definitivo/` e `Backup/Dados_2025_05/Definitivo/`) e `SM e Cesta desde 1979_06_25.xlsx` (pasta `Backup/Dados_2025_07/Definitivo/`). A versão mais recente localizada (`..._06_25.xlsx`) tem uma única aba, "dados Cesta e SM", com o **mesmo cabeçalho** ("Salário Mínimo e Cesta Básica Alimentar no Município de São Paulo" / "Mês", "Salário Mínimo Corrente", "Cesta Básica em São Paulo Corrente", "Sal. Mínimo / Cesta Básica"), 564 linhas, indo até **junho/2025** — data de última observação idêntica à de `T27` em "dieese".
- **Conclusão:** o bloco "Cesta Básica" (slide 28, chart29 — incorporado, não vinculado, ver Frente D.3) tem origem identificável com alta confiança na série "Salário Mínimo × Cesta Básica (São Paulo)", elaboração própria DIEESE, mantida em arquivos de nome `SM e Cesta desde 1979[...].xlsx` versionados trimestralmente, e replicada na aba `T27` de "dieese". Essa é a explicação direta para a referência "T27-T28" no Sumário de ambos os P1: a aba existe/existiu, mas foi removida de "principal" em algum momento (permanecendo apenas em "dieese" e no arquivo-fonte dedicado do corpus).

### G.2 Preços de combustíveis — PROVÁVEL

- Localizado no corpus: `Apresentação de conjuntura/Backup/Outras versões/Dados/Preços combustíveis histórico.xlsx`, aba única `Plan1` (770 linhas), com colunas "Governo", "Presidente da Petrobrás", "Tempo do PPI", "Mês", "Ano", "Vigência", "Gasolina Preço Refinaria (litro R$)", "Diesel S-10 Preço Refinaria (litro R$)" — série histórica desde 2002.
- O alvo externo identificado na Frente D.2 para o gráfico do slide 29 é `20251127 - Preços combustíveis.xlsx` — nome de arquivo diferente (datado de 27/11/2025) e não presente no corpus.
- **Conclusão:** mesma família temática e estrutura conceitual (preços de combustíveis por governo/período, elaboração com base em dados de referência de preços de refinaria), mas **não é o mesmo arquivo** que alimenta o gráfico do slide 29 — é um arquivo histórico correlato, não a fonte direta identificada tecnicamente. Classificação: PROVÁVEL parentesco/linhagem, arquivo-fonte exato ainda não localizado no corpus.

### G.3 ICT — Índice de Condições de Trabalho — PROVÁVEL

- Localizados no corpus: `Apresentação de conjuntura/Backup/Outras versões/Dados/ICT - Dieese - 202302.xls` (vintage fev/2023, abas "Resumo (Tab 1)" e "Plan1", com dimensões "Condição de inserção ocupacional", "Desocupação", "Rendimento", "ICT-DIEESE", série 2012.01–2023.02) e `Apresentação de conjuntura/Backup/Outras versões/Dados_2024.11/Boletim ICT-DIEESE - n14 - 2024_2 - Gráficos (1).xlsx`.
- O alvo externo identificado na Frente D.2 para o gráfico do slide 31 é `ICT - Brasil - PNAD Continua - 202503.xls`, com aba `Resumo (Tab 1)` — **mesmo nome de aba** ("Resumo (Tab 1)") do arquivo de 2023 encontrado no corpus, mas vintage mais recente (mar/2025) e nome de arquivo diferente.
- **Conclusão:** a coincidência do nome da aba interna ("Resumo (Tab 1)") entre o arquivo do corpus (fev/2023) e o alvo do link vivo (mar/2025) é evidência **direta e específica** de que se trata da mesma metodologia/planilha-modelo, atualizada trimestral ou semestralmente sob nomes de arquivo que incorporam a data de referência. O arquivo exato que alimenta o slide 31 (vintage 202503) não está no corpus; o arquivo de vintage 202302 está, e serve como evidência da estrutura/metodologia do indicador. Classificação: PROVÁVEL parentesco direto, arquivo-fonte exato da apresentação não presente no corpus.

---

## Frente H — Linhagem preliminar e matriz comparativa

### H.1 Matriz comparativa: principal × dieese

| Critério | principal | dieese |
|---|---|---|
| Data de criação (metadado) | 2015-06-05 (idêntica) | 2015-06-05 (idêntica) |
| Autoria original | Lucas Capelo | Lucas Capelo |
| Última edição (metadado) | 2026-03-19 | 2026-06-10 (mais recente) |
| Último editor | (não registrado) | Ricardo Tamashiro |
| Nº de abas | 47 | 54 |
| Datas "Último" no Sumário interno (macro/juros/inflação) | ago/set-2025, 3T/2025 — **coincide com o período "4T 2025" da apresentação** | mar/abr-2026, 1T/2026 — **período posterior ao 4T/2025** |
| Faixa CAGED declarada no Sumário | T39-T44 | T39-T42 (faixa reduzida; T43/T44 ocultas) |
| Conteúdo de `T14` | Selic/IPCA/juros real (bate com slide 14 da apresentação) | Endividamento familiar (conteúdo de Selic/IPCA/juros real realocado para `T18a`, série estendida até mar/2026) |
| Abas exclusivas relevantes | `T40-43` (nome de aba isolado) | `T27` (Cesta Básica), `T18a`, `Protegido e desprotegido`, `T34`/`T34a`, `T41a`/`T41b` |
| Sinal de conteúdo mais avançado no tempo | — | `T44` traz tabela rotulada "dezembro de 2025" (além do período do 4T/2025); `T18a` vai até mar/2026 |
| Caminhos-alvo dos gráficos vinculados do `.pptx` (Frente D) | Predominantemente arquivos de caminho "2025.4T"/"Apresentação_Conjuntura_4T_2025.xlsx" — **mesmo nome do arquivo "principal"** | Nenhum gráfico do `.pptx` aponta para um caminho contendo "(2)" ou para o arquivo "dieese" especificamente |
| Inconsistência interna notável | Sumário cita "T27-T28" (Cesta Básica) que não existe mais no arquivo | Sumário também cita "T27-T28", mas só `T27` existe (falta `T28` em ambos) |
| Evidência de uso efetivo pela apresentação 4T/2025 | **Alta** — nome de arquivo e período batem com os alvos dos vínculos do `.pptx` | **Baixa como fonte direta da apresentação 4T/2025** — mas alta como continuidade documental do mesmo arquivo em data posterior |

### H.2 Conclusão sobre o arquivo de referência

Seguindo a instrução de **não escolher simplesmente o arquivo mais recente**, e apoiando a conclusão apenas nas evidências acima:

**Conclusão: opção (3) — ambos são necessários, mas com papéis distintos e não intercambiáveis.**

- **"principal" é o arquivo de referência primário para reconstruir o pipeline de dados da apresentação `ATR_Conjuntura_2025.12.pptx`** (o material P1 mais importante para a análise de conjuntura em si): seu Sumário interno está alinhado ao período 4T/2025 declarado na apresentação, e a esmagadora maioria (43 de 47) dos gráficos do `.pptx` tem vínculo técnico direto (`TargetMode="External"`) apontando para um arquivo de mesmo nome e mesma pasta de "Planilhas Definitivas/2025.4T". Isso não é uma escolha por recência — é uma escolha por **coincidência temporal e nominal com os vínculos técnicos verificados**.
- **"dieese" não deve ser tratado como a referência da apresentação 4T/2025** — seus próprios metadados internos (datas do Sumário, conteúdo de `T44`/`T18a`) mostram que é uma edição **posterior** do mesmo arquivo-raiz, já incorporando dados de dezembro/2025 e do 1º trimestre de 2026.
- **"dieese" é, no entanto, indispensável como fonte complementar** para os poucos elementos que "principal" não contém mais, mas que a própria apresentação e o próprio Sumário de "principal" referenciam: a aba `T27` (Cesta Básica) é hoje a única cópia, entre os dois P1, do indicador que corresponde ao slide 28. Sem "dieese", esse elo ficaria completamente sem evidência em planilha.
- Para os blocos de **Greves e Negociações Coletivas** (slides 47–57), **nenhum dos dois arquivos** contém as abas de origem (`T50`–`T54` e equivalentes) — a evidência técnica (Frente D) mostra que essas abas existem em alguma versão do arquivo não presente no corpus atual.

Esta conclusão é sobre os **dois arquivos Excel especificamente**; não substitui a necessidade de, no futuro, obter diretamente do DIEESE uma cópia mais completa e/ou mais próxima em data ao fechamento de `ATR_Conjuntura_2025.12.pptx` (04/12/2025), que contenha as abas `T50`–`T54` e a versão exata de `20251127 - Preços combustíveis.xlsx` e `ICT - Brasil - PNAD Continua - 202503.xls`.

---

## Dúvidas que ainda exigem validação humana

1. A reorganização de `T14`→`T18a` (Frente C) ocorreu numa única operação ou gradualmente? Houve uma versão intermediária entre "principal" e "dieese" que não está no corpus?
2. Qual é a fonte exata (arquivo, planilha, sistema) dos dados de número/categorias/reivindicações de greves dos slides 48–51 — presumivelmente o Sistema de Acompanhamento de Greves (SAG-DIEESE), mas nenhum arquivo desse sistema foi localizado no corpus de 339 materiais.
3. O arquivo `mediador - economicas 2023.xlsx` é de fato o predecessor metodológico direto dos slides 53–57 (reajustes/pisos), ou existe um arquivo equivalente mais recente (2024/2025) não presente no corpus?
4. Confirmar com a equipe DIEESE se `20251127 - Preços combustíveis.xlsx` e `ICT - Brasil - PNAD Continua - 202503.xls` (arquivos-alvo identificados tecnicamente nos vínculos do `.pptx`, mas ausentes do corpus) podem ser obtidos para completar a cadeia de evidência desses dois indicadores.
5. Por que `cp:lastModifiedBy` está vazio em "principal" mas preenchido ("Ricardo Tamashiro") em "dieese" — decorrência de configuração do aplicativo usado na última edição, sem impacto na análise, mas vale confirmar.
6. Confirmar se T33A/T36A (fórmulas de série dos gráficos dos slides 33 e 38) referenciam de fato as abas T33/T36 (nome de tabela/intervalo interno com sufixo "A" dentro da mesma aba) ou uma aba distinta ausente do corpus — a evidência atual (fórmula com sufixo "A" sem aba correspondente com esse nome exato) não permite decidir com segurança entre as duas hipóteses (ver `MAPA_SLIDE_ABA_P1.md`, classificação PROVÁVEL para os slides 33 e 38).

## Erros factuais da Rodada 1 corrigidos nesta rodada

- `COMPARACAO_EXCEL_P1.md` (Rodada 1) atribuía a abas como `Ty`/`T4x`/`Protegido e desprotegido` uma leitura de "possível rascunho" apoiada majoritariamente no nome. A Rodada 2 manteve essa leitura para `Ty`/`T4x` (agora apoiada em evidência independente: estado oculto + ausência de fórmulas + sobreposição de dados com a aba-resumo `T43`), mas **a descartou para `Protegido e desprotegido`**, que é uma aba visível, com 61 fórmulas e 3 gráficos próprios — um indicador de pleno direito.
- Os indicadores de "Preços de combustíveis" (slide 29) e "ICT" (slide 31), registrados em `INVENTARIO_INDICADORES_P1.md` com confiança BAIXA e nota "não localizado no Excel principal", agora têm o nome do arquivo-fonte externo identificado tecnicamente (ver Frente D.2 e Frente G.2/G.3) — a nota de "não localizado" continua correta quanto à ausência física do arquivo no corpus, mas passa a ser possível apontar exatamente qual arquivo (nome e caminho) seria necessário obter.
