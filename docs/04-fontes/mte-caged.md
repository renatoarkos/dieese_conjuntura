# Fonte: Novo CAGED — Ministério do Trabalho e Emprego (MTE) / PDET

## Identificação da instituição

- **Instituição produtora**: hoje, Ministério do Trabalho e Emprego (MTE), via Programa de Disseminação de Estatísticas do Trabalho (PDET).
- **Achado sobre nomenclatura**: o material do DIEESE cita a fonte de forma inconsistente entre indicadores — "MTE" (indicador salário médio) e "SEPRT/ME" (indicador saldo por grupamento). **Não são fontes distintas**: a SEPRT (Secretaria Especial de Previdência e Trabalho, então dentro do Ministério da Economia) era responsável técnica pelo Novo CAGED até 2022; com a recriação do MTE em 2023, a disseminação passou a esse ministério, mesmo programa (PDET), mesma metodologia (vigente desde jan/2020).
- **Data de consulta de todo este documento**: 2026-09-22 (Discovery de Fontes — Lote 04).

## Achado central — não há API pública

Diferente de IBGE/SIDRA e BCB/SGS (ambos com API pública confirmada em lotes anteriores), o Novo CAGED **não tem API**. A pesquisa direta na documentação oficial (`Sobre o Novo Caged.pdf`, obtido via FTP público) confirma 6 canais oficiais de disseminação: (1) Sumário executivo em PDF; (2) Apresentação em PDF; (3) **Tabelas** (workbook agregado); (4) Painel de informações (Power BI); (5) Microdados (FTP); (6) Consulta online — "inexistente neste primeiro momento" (declarado no próprio documento oficial).

### Caminho 1 — Tabelas agregadas (candidato mais próximo do que o DIEESE usa)

- O workbook mensal (ex.: `3-tabelas_Julho de 2026.xlsx`, ~40 MB) é o candidato natural para as tabelas citadas pelo DIEESE (1, 2, 6.1, 9).
- **Hoje é distribuído por uma pasta compartilhada do Google Drive**, linkada na página oficial mensal (`gov.br/trabalho-e-emprego/.../novo-caged`) — **não é uma URL HTTP fixa e programática**. Testado diretamente: confirma-se a existência do arquivo, mas o link do Drive pode mudar de conteúdo/ID ao longo do tempo (não testado ao longo de múltiplos meses nesta rodada).
- **Um padrão de URL antiga e estável existia** (`pdet.mte.gov.br/images/Novo_CAGED/AAAA/AAAAMM/3-tabelas.xlsx`) — testado e confirmado **morto** (404 / sem conexão). O domínio `pdet.mte.gov.br` hoje redireciona para `gov.br`.
- **Não foi possível abrir o conteúdo interno do workbook** (bloqueio de acesso ao Drive sem sessão de navegador) — portanto, **os nomes exatos "TABELA 1", "TABELA 2", "TABELA 6.1", "TABELA 9" citados pelo material do DIEESE não foram confirmados diretamente**. É hipótese plausível (reforçada por um projeto de terceiros não oficial, `github.com/Natanaelsl/NCAGEDdataR`, que descreve processar 11 tabelas do mesmo workbook), não confirmação.
- **Classificação de automação: B, com ressalva forte** — não é uma URL fixa testável programaticamente sem intervenção manual/sessão Google; na prática se aproxima de D para um pipeline 100% automatizado.

### Caminho 2 — Microdados brutos via FTP (único caminho 100% automatizável confirmado)

- **CONFIRMADO E TESTADO**: `ftp://ftp.mtps.gov.br/pdet/microdados/NOVO%20CAGED/` — listagem real de pastas por ano (2020-2026) e mês, cada mês com 3 arquivos `.7z`: `CAGEDMOVAAAAMM` (movimentações dentro do prazo), `CAGEDFORAAAAMM` (fora do prazo), `CAGEDEXCAAAAMM` (exclusões).
- Este é o caminho **realmente estável e automatizável** — mas entrega **microdados brutos** (registros individuais de admissão/desligamento), não as tabelas agregadas que o DIEESE usa. Reconstruir as Tabelas 1, 2, 6.1, 9 a partir daqui exigiria processamento próprio (agregação por grupamento de atividade, nível geográfico, cálculo de saldo, cálculo de salário médio de admissão/desligamento) — uma etapa de engenharia de dados própria, não apenas uma coleta RAW.
- **Classificação de automação: C** (microdados, confirmado e testado) — mas com esforço de engenharia adicional relevante antes de produzir os indicadores finais.

## Método de acesso testado e descartado

- `dados.gov.br` (portal CKAN de dados abertos do governo federal): API retornou HTTP 401 (exige chave/autenticação); busca na interface web é uma SPA que não renderizou conteúdo de dataset verificável. **Não confirmado** — nem confirma nem refuta a existência de uma base do CAGED ali.
- Painel Power BI oficial (`app.powerbi.com/view?r=...`) existe e está ativo, mas é uma ferramenta de visualização — não foi testada quanto a exportação de dados brutos.

## Ficha — Indicador: Evolução do salário médio de admissão e desligamento por mês

| Campo | Valor |
|---|---|
| Fonte primária | MTE/PDET (mesmo produtor citado como "MTE" e "SEPRT/ME" no material — sucessão institucional, não fontes distintas). |
| Método de acesso | B (Tabelas, via Drive instável) ou C (microdados FTP, com processamento próprio). |
| Nome da tabela | "3. Tabelas" do Novo CAGED — nome interno "TABELA 9" não confirmado diretamente. |
| Periodicidade | Mensal, desde jan/2020 (metodologia Novo CAGED). |
| Histórico | jan/2020 até jul/2026 (mês mais recente confirmado). Dados anteriores a 2020: CAGED "legado", fonte/formato diferentes, fora do escopo desta ficha. |
| **Classificação de automação** | **B (com ressalva) / C** — não A. Não incluído no piloto técnico nesta rodada. |

## Ficha — Indicador: Saldo de admissões/desligamentos por grupamento de atividade e nível geográfico

| Campo | Valor |
|---|---|
| Fonte primária | MTE/PDET (idem acima). |
| Método de acesso | Idêntico ao indicador anterior — mesmo workbook mensal. |
| Nome da tabela | "3. Tabelas" do Novo CAGED — nomes internos "TABELA 1", "TABELA 2", "TABELA 6.1" não confirmados diretamente, mas o conteúdo oficial do workbook (confirmado no PDF institucional) inclui exatamente "dados mensais e de série histórica desagregados por setor de atividade econômica, grandes regiões, UF e municípios" — compatível com a descrição do DIEESE. |
| Periodicidade | Mensal, desde jan/2020. |
| Histórico | jan/2020 até jul/2026. |
| **Classificação de automação** | **B (com ressalva) / C** — não A. Não incluído no piloto técnico nesta rodada. |

## Por que estes dois indicadores não entraram no piloto técnico

Diferente dos indicadores já automatizados (PIB, IPCA, Câmbio, Selic, PMC, Desocupação, Posição na ocupação, Taxa de participação, Juros por modalidade), o Novo CAGED não tem um endpoint HTTP estável e testável sem intervenção manual. Escrever um script de coleta apontando para uma pasta do Google Drive seria frágil (o link pode mudar) e não condiz com o princípio de reversibilidade/confiabilidade mínima já seguido no piloto (ADR 0001/0002). A alternativa robusta (FTP de microdados) exige uma camada de processamento que ultrapassa o escopo de "coleta bruta sem transformação" da camada RAW.

## Pergunta para validação humana

- **QF09**: a equipe do DIEESE hoje baixa o workbook "3-tabelas" manualmente da página oficial mensal (ou de um link/pasta específica que já conhece e é mais estável que o testado aqui), ou usa os microdados brutos via FTP com processamento próprio? Isso define se a plataforma deve investir em (a) um scraper resiliente da página oficial mensal para localizar o link do Drive a cada mês, ou (b) uma pipeline de agregação própria a partir dos microdados FTP (mais robusta, mais esforço de engenharia).
