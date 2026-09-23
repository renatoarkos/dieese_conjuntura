# Fontes: organismos internacionais além do FMI/WEO (rodada de expansão, set/2026)

**Natureza deste documento**: Discovery de Fontes **exploratório**, não amarrado a nenhum dos 33 indicadores do catálogo P1. Responde à mesma lacuna de `docs/00-visao-geral/VISAO_DO_PRODUTO.md`, Seção 5 (comparação internacional Brasil x mundo, ainda não coberta). **Nenhuma destas fontes está ligada a um indicador do catálogo atual** — são candidatas para uma futura decisão de escopo, não uma expansão automática do checklist.

**Data de consulta**: 2026-09-23. Todos os testes abaixo foram execução real (`curl`), não inferência — URLs exatas, código HTTP e trecho real de resposta em cada seção, conforme exige `CLAUDE.md`.

**O que o projeto já integra de fontes internacionais** (não repetido aqui): FMI/SDMX (World Economic Outlook — PIB mundial e por país, variação real anual). Ficha em `docs/04-fontes/fmi-cni.md`.

---

## Síntese (classificação de automação, escala de `agents/fontes-dados.md`)

| Organismo | Classificação | Confiança | Nota |
|---|---|---|---|
| Banco Mundial (World Bank Open Data) | **A** | Alta — testado, dado real do Brasil, sem cadastro | Milhares de indicadores, 1960-presente |
| OIT/ILO (ILOSTAT SDMX) | **A** | Alta — testado, dado real do Brasil | Valores são "estimativas modeladas" do ILO, não a série direta do IBGE |
| BIS (Bank for International Settlements) | **A** | Alta — testado, dado real do Brasil | Câmbio efetivo, crédito internacional |
| OCDE (novo `sdmx.oecd.org`) | **A** | Média-alta — testado, dado real do Brasil, mas catálogo de dataflows é enorme | Brasil só aparece em dataflows "G20"/"key partners", não nos padrão-OCDE |
| Eurostat | **A** | Alta — testado, mas só comércio bilateral Brasil-UE | Não é dado doméstico brasileiro |
| UN Comtrade (camada pública) | **A (limitada)** | Média — testado, funciona, mas camada gratuita é limitada | Complementa, não substitui o Comex Stat já integrado |
| CEPALSTAT (CEPAL/ONU) | **A (parcial)** | Média — API real, mas filtro por país não resolvido nesta rodada | Precisa mais investigação de sintaxe antes de uso |
| FRED (Federal Reserve, EUA) | **B (exige cadastro)** | Alta confiança na limitação | Chave gratuita via cadastro; réplica séries do Banco Mundial para o Brasil (sobreposição parcial) |
| FMI além do WEO (API nova `api.imf.org/external/sdmx/2.1`) | **D** | Catálogo real confirmado, mas sintaxe de consulta não resolvida | API legada foi desligada; datasets modulares (CPI, BOP, GFS etc.) exigem mais uma rodada |

---

## Banco Mundial (World Bank Open Data)

| Campo | Valor |
|---|---|
| Endpoint testado | `https://api.worldbank.org/v2/country/BRA/indicator/NY.GDP.MKTP.KD.ZG?format=json&per_page=5&date=2020:2023` |
| Resultado | **HTTP 200**, JSON real: `{"country":{"value":"Brazil"},"date":"2023","value":3.24165532906981}` (crescimento real do PIB, %a.a.) |
| Autenticação | Nenhuma. |
| Cobertura | Milhares de indicadores de desenvolvimento (PIB, pobreza, educação, saúde, meio ambiente etc.), 1960-presente, atualização conforme fonte original. |
| **Classificação** | **A — API direta**, testada, sem cadastro. Útil para painel comparativo Brasil x mundo em desenvolvimento — não substitui fonte primária nacional já confirmada (SIDRA/BCB). |

## OIT/ILO — ILOSTAT (SDMX)

| Campo | Valor |
|---|---|
| Base correta | `sdmx.ilo.org` (a base `www.ilo.org/sdmx` redireciona/retorna 404). |
| Endpoint testado | `https://sdmx.ilo.org/rest/data/ILO,DF_UNE_2EAP_SEX_AGE_RT,1.0/BRA....?startPeriod=2022&endPeriod=2023` (formato CSV) |
| Resultado | **HTTP 200**, dado real: taxa de desemprego, Brasil, 2022 = 9,231%, rotulado `"ILO - Modelled Estimates"`. |
| **Alerta importante** | São **estimativas modeladas/harmonizadas** do ILO para comparação internacional entre países — **não** a série direta da PNAD Contínua (já confirmada via SIDRA, indicador 22 do catálogo). Só usar para comparação Brasil x mundo, nunca como substituto da fonte nacional. |
| **Classificação** | **A — API direta**, testada, sem cadastro. Diretamente relevante para um projeto de conjuntura do mercado de trabalho — permite comparar o Brasil com outros países usando a mesma metodologia harmonizada. |

## BIS — Bank for International Settlements

| Campo | Valor |
|---|---|
| Endpoint testado | `https://stats.bis.org/api/v2/data/dataflow/BIS/WS_EER/1.0/M.N.B.BR?startPeriod=2023-01&endPeriod=2023-06` (formato CSV) |
| Resultado | **HTTP 200** de primeira tentativa, dado real: taxa de câmbio efetiva nominal do Brasil, jun/2023 = 115,33 (base 100 = média 2020). |
| Autenticação | Nenhuma. |
| Cobertura | Taxas de câmbio efetivas, crédito internacional, estatísticas bancárias — séries mensais/trimestrais, longo histórico. |
| **Classificação** | **A — API direta**, testada, sem cadastro. Complementa o câmbio nominal (BCB/SGS, indicador 6) com uma medida ponderada por parceiros comerciais. |

## OCDE — novo `sdmx.oecd.org`

| Campo | Valor |
|---|---|
| Atenção | A API legada `stats.oecd.org/SDMX-JSON` está **deprecada**. Usar a nova base `sdmx.oecd.org/public/rest/`. |
| Endpoint testado | `https://sdmx.oecd.org/public/rest/data/OECD.SDD.NAD,DSD_NAMAIN1@DF_QNA_EXPENDITURE_GROWTH_G20,/all?startPeriod=2023-Q1&endPeriod=2023-Q4` (header `Accept: application/vnd.sdmx.data+csv;version=1.0.0`) |
| Resultado | **HTTP 200**, dado real: variação trimestral do consumo das famílias, Brasil, 4T/2023 = 6,22%. |
| **Alerta importante** | O Brasil só aparece em dataflows **"G20"/"key partners"**, não nos dataflows padrão "OECD" (só países-membro). O catálogo de dataflows é enorme (1300+) — qualquer integração futura precisa mapear caso a caso quais dataflows incluem o Brasil. |
| **Classificação** | **A — API direta**, testada, sem cadastro para consultas de baixo volume — mas exige investigação dataflow-a-dataflow antes de qualquer piloto técnico. |

## Eurostat

| Campo | Valor |
|---|---|
| Endpoint testado | `https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/ext_lt_maineu?format=JSON&partner=BR&lang=en&sinceTimePeriod=2022` |
| Resultado | **HTTP 200**, formato JSON-stat, dado real: exportações UE27→Brasil (2022) = € 42.822,5 milhões; saldo comercial UE-Brasil (2022) = -€ 7.084,3 milhões. |
| **Limitação** | Só cobre comércio bilateral Brasil-UE — não é dado doméstico brasileiro. |
| **Classificação** | **A — API direta**, testada, sem cadastro. Complementar ao Comex Stat (já integrado) para o recorte específico Brasil-UE. |

## UN Comtrade (Nações Unidas)

| Campo | Valor |
|---|---|
| Endpoint testado | `https://comtradeapi.un.org/public/v1/preview/C/A/HS?reporterCode=76&period=2022&partnerCode=0&cmdCode=TOTAL&flowCode=X` (reporterCode 76 = Brasil) |
| Resultado | **HTTP 200**, JSON real: exportações totais do Brasil (2022) = US$ 186.402.909 (valor FOB, recorte parcial de modo de transporte). |
| **Limitação** | Camada pública "preview" é limitada (linhas/granularidade reduzidas) — não é o dataset completo. |
| **Classificação** | **A, com limitação** — complementa mas não substitui o Comex Stat já confirmado (indicador 7 do catálogo). Útil para a perspectiva do comércio bilateral global, não brasileiro isolado. |

## CEPAL/ECLAC — CEPALSTAT

| Campo | Valor |
|---|---|
| Endpoint testado | `https://api-cepalstat.cepal.org/cepalstat/api/v1/indicator/145/data?id_pais[]=222&lang=en` (id 222 = Brasil, confirmado na lista de países da própria API) |
| Resultado | **HTTP 200**, JSON real (25.627 registros no indicador testado). |
| **Limitação** | O parâmetro `id_pais` não filtrou de fato o resultado nesta rodada — extrair um valor específico do Brasil exige mapear a dimensão real dos dados (`dim_208`), não resolvido neste teste. |
| **Classificação** | **A, parcial** — API real e funcional, mas precisa de mais uma rodada de investigação de sintaxe de filtro antes de uso em produção. Organismo especializado em América Latina, relevante para comparação regional. |

## FRED — Federal Reserve Economic Data (EUA)

| Campo | Valor |
|---|---|
| Endpoint testado | `https://api.stlouisfed.org/fred/series/observations?series_id=MKTGDPBRA646NWDB&file_type=json` |
| Resultado | **HTTP 400**, erro real e explícito: `"Variable api_key is not set. Read https://fred.stlouisfed.org/docs/api/api_key.html..."` |
| Processo de cadastro | Confirmado: `fred.stlouisfed.org/docs/api/api_key.html` responde HTTP 200 — cadastro gratuito de conta no site, chave liberada na hora. |
| Observação | O FRED também replica séries do Banco Mundial para o Brasil (ex. `MKTGDPBRA646NWDB` = PIB em USD correntes) — sobreposição parcial com o item Banco Mundial acima. Mais útil como agregador de conveniência (interface unificada para muitas fontes) do que como fonte primária adicional. |
| **Classificação** | **B — exige cadastro/chave**, gratuito, processo confirmado. |

## FMI além do WEO

| Campo | Valor |
|---|---|
| API legada (desligada) | `dataservices.imf.org/REST/SDMX_JSON.svc` — testado, conexão falhou (não é mais servida). |
| API nova | `api.imf.org/external/sdmx/2.1` — confirmada real: `.../dataflow/IMF.STA` retorna HTTP 200 com catálogo extenso e real de dataflows modulares (`CPI`, `BOP`, `COFER`, `EER`, `GFS`, `FAS`, `ANEA` etc.) — o antigo "IFS" monolítico não existe mais como tal, foi decomposto. |
| **Limitação** | Não foi possível, no tempo desta rodada, extrair uma observação limpa do Brasil (a sintaxe de chave SDMX de 5 dimensões testada para `CPI` retornou séries vazias) — isso não confirma ausência de dado, é lacuna de investigação de sintaxe/codelist, não de existência da fonte. |
| **Classificação** | **D — investigação adicional necessária.** API real e acessível, catálogo real, mas precisa de mais uma rodada dedicada (checar codelists via `/codelist/IMF.STA/...`) antes de declarar um indicador específico como confirmado. |

---

## Observações metodológicas e limites desta rodada

- Todos os testes foram execução real via `curl` nesta sessão (2026-09-23) — nenhuma fonte, endpoint ou dado foi presumido sem teste.
- Nenhum destes achados está amarrado a um indicador específico do catálogo P1. Antes de qualquer piloto técnico: (1) confirmar com a equipe do DIEESE se comparação internacional entra no escopo da plataforma; (2) se sim, escolher o indicador específico e repetir a investigação de fonte já com ele em mãos.
- Fonte primária nacional (SIDRA, BCB, SICONFI etc.) continua preferível a organismos internacionais para dado **doméstico** brasileiro, por `CLAUDE.md` ("Priorize fontes oficiais e primárias") — estas fontes servem para **comparação Brasil x mundo**, um eixo novo, não coberto hoje.

## Próximo passo recomendado

Se o projeto priorizar um painel comparativo internacional, os candidatos mais robustos e imediatamente utilizáveis (sem cadastro, testados com dado real do Brasil) são, em ordem de prontidão: **Banco Mundial** (mais amplo, mais simples), **ILOSTAT** (mercado de trabalho, tema central do projeto) e **BIS** (câmbio efetivo). OCDE, Eurostat, UN Comtrade e CEPALSTAT exigem mapeamento adicional de dataflow/filtro antes de um piloto técnico.
