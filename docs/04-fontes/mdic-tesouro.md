# Fontes: MDIC (Comex Stat) e Tesouro Nacional (SICONFI)

## Identificação das instituições

- **Balança comercial**: Ministério do Desenvolvimento, Indústria, Comércio e Serviços (MDIC), plataforma Comex Stat. O material do DIEESE cita "SECEX" (Secretaria de Comércio Exterior) — é a secretaria dentro do MDIC responsável pelos dados, não uma instituição separada.
- **Limite fiscal por Estado**: Secretaria do Tesouro Nacional (STN), Sistema de Informações Contábeis e Fiscais do Setor Público Brasileiro (SICONFI).
- **Data de consulta**: 2026-09-22 (Discovery de Fontes — Lote 05b).

## Balança comercial brasileira (Comex Stat)

| Campo | Valor |
|---|---|
| O que mede | Exportações e importações brasileiras, saldo comercial, por NCM/SH, UF, país, mensal. |
| Status da API | **API REST real e ativa, parcialmente confirmada**: `https://api-comexstat.mdic.gov.br/general/dates/years` testado com sucesso (retornou `{"data":{"max":"2026","min":"1997"}}`). O endpoint principal de consulta agregada (`/general`) retornou HTTP 403 em tentativas via GET — evidência (não confirmação) de que esse endpoint exige requisição **POST** com corpo JSON, método não testável pela ferramenta de busca usada nesta pesquisa. Documentação oficial (`/docs`) também bloqueada (403) ao fetch direto. |
| Alternativa confirmada | **Download CSV estruturado, oficial e documentado**: página `gov.br/mdic/.../base-de-dados-bruta` confirma exportação/importação por NCM (1997-2026, arquivo anual), por município (1997-2026), histórico 1989-1996 — separador `;`, atualizado até set/2026. |
| Periodicidade | Mensal. |
| Histórico | 1997-2026 (detalhado); 1989-1996 (agregado). |
| **Classificação de automação** | **B — confirmado** (CSV oficial, download estruturado). **A — hipótese forte, não fechada**: API existe e responde para metadados, mas o endpoint de consulta agregada precisa ser testado com POST antes de confirmar classificação A. |

## Limite fiscal (prudencial e máximo) por Estado — SICONFI

| Campo | Valor |
|---|---|
| O que mede | Despesa total com pessoal como % da Receita Corrente Líquida (RCL) ajustada, e os limites da Lei de Responsabilidade Fiscal (prudencial = 0,95×limite máximo; alerta = 0,90×limite máximo) por Unidade da Federação. |
| Status da API | **CONFIRMADO E TESTADO COM SUCESSO.** Endpoint: `https://apidatalake.tesouro.gov.br/ords/siconfi/tt/rgf?an_exercicio={ano}&nr_periodo={periodo}&co_tipo_demonstrativo=RGF&co_poder=E&co_esfera=E&in_periodicidade=Q&id_ente={codigo_ibge_uf}`. Testado para São Paulo (id_ente=35), 3º quadrimestre 2023 — retornou JSON real com: "DESPESA TOTAL COM PESSOAL - DTP" (42,33% da RCL), "LIMITE MÁXIMO (IX)" (49% da RCL), "LIMITE PRUDENCIAL (X) = 0,95×IX", "LIMITE DE ALERTA (XI) = 0,90×IX" — **bate exatamente com os dois indicadores citados no material do DIEESE** (limite prudencial e máximo). |
| Periodicidade | Quadrimestral (Relatório de Gestão Fiscal — RGF, conforme LRF). |
| Histórico | Múltiplos exercícios confirmados (testado 2023, 2024); RGF publicado desde meados dos anos 2000. |
| Observação | O material do DIEESE registra "consulta em 02/06/2025" — indício de que a equipe usa o portal web manualmente. A API já existe e resolve o mesmo dado de forma automatizada; a consulta manual provavelmente reflete processo herdado, não limitação real da fonte. |
| **Classificação de automação** | **A — confirmado**, API REST sem autenticação, testada com sucesso, JSON estruturado com os campos exatos do indicador. |

## Síntese de classificação de automação

| Indicador | Classificação | Confiança |
|---|---|---|
| Balança comercial (Comex Stat) | B confirmado / A hipótese (requer teste POST) | Alta para B, média para A |
| Limite fiscal por Estado (SICONFI) | A | Alta — testado com dados reais |
