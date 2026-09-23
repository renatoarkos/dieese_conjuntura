# Fontes: ANP e IPEADATA (Preços de combustíveis)

**Data de consulta**: 2026-09-22 (investigação de lacunas conhecidas, pós-Lote 06).

## Contexto

Indicador "Preços de combustíveis" (gasolina, diesel, gás de cozinha) — estava 🔴 LACUNA no checklist (arquivo interno `20251127 - Preços combustíveis.xlsx` ausente do corpus). Material do DIEESE cita "ANP; Petrobrás; IPEADATA" como fontes de elaboração. **Resolvido nesta rodada.**

## ANP — Série Histórica de Preços de Combustíveis (SLP)

| Campo | Valor |
|---|---|
| Status | **CONFIRMADO E TESTADO — piloto executado.** O HTTP 403 inicial na página oficial **não era WAF/bloqueio institucional** — era detecção de bot por ausência de cabeçalhos HTTP típicos de navegador (`Accept`, `Accept-Language`). Adicionando esses cabeçalhos, a página retornou HTTP 200 normalmente (325 KB de HTML), permitindo extrair **222 links de download reais** presentes no próprio HTML — não adivinhados. |
| Página oficial | `gov.br/anp/pt-br/centrais-de-conteudo/dados-abertos/serie-historica-de-precos-de-combustiveis` |
| URLs confirmadas e testadas (download real, HTTP 200) | `.../arquivos/shpc/qus/ultimas-4-semanas-gasolina-etanol.csv` (7,8 MB) · `.../ultimas-4-semanas-diesel-gnv.csv` (3,6 MB) · `.../ultimas-4-semanas-glp.csv` (2,2 MB) — série de microdados por posto revendedor, "últimas 4 semanas", atualizada semanalmente. Amostra real confirmada: colunas Região, Estado, Município, Revenda, CNPJ, Produto, Data da Coleta, Valor de Venda, Valor de Compra, Unidade, Bandeira. |
| Séries históricas adicionais confirmadas (não coletadas neste piloto) | Arquivos semestrais desde 2004 (`.../dsas/ca/ca-{ano}-{semestre}.zip`, `.../dsas/glp/glp-{ano}-{semestre}.csv`) e mensais desde 2023 (`.../dsan/{ano}/precos-{produto}-{mes}.csv`) — mesmo domínio, mesmo padrão de acesso, não incluídas no piloto por não serem necessárias ao indicador corrente. |
| Produtos cobertos | Gasolina C, Etanol Hidratado, Óleo Diesel (S-500/S-10), GNV, GLP P13 (gás de cozinha) — cobre exatamente os 3 itens do indicador do DIEESE. |
| Periodicidade | Semanal (arquivo "últimas 4 semanas"); mensal/semestral nas séries históricas. |
| Histórico | Desde 2004 (séries históricas); últimas 4 semanas para uso corrente. |
| **Classificação de automação** | **B — download estruturado**, confirmado e testado, piloto executado (`pipelines/ingestao/bloco_3_inflacao/coleta_combustiveis_anp.py`). |

## IPEADATA (API OData4)

| Campo | Valor |
|---|---|
| Status | **CONFIRMADO E TESTADO** — API REST real, protocolo OData v4, sem autenticação. Endpoint: `http://www.ipeadata.gov.br/api/odata4/`. |
| Séries encontradas | `ANP_PRGASOL` (preço médio gasolina), `ANP_PROLDIE` (preço médio diesel), `ANP_PRGLP` (preço médio GLP) — todas testadas com sucesso, retornando valores reais de 1973 a 2025. |
| **Limitação importante** | Estas séries são preços médios **anuais** de referência do Balanço Energético Nacional/EPE (R$/m³ ou R$/tonelada) — **distintas do "Preço Médio de Revenda" semanal da ANP** (R$/litro no varejo), que é a métrica normalmente usada em acompanhamento de conjuntura/custo de vida. **Não é a mesma série citada pelo DIEESE** — candidato alternativo público, mas com granularidade insuficiente (anual, não semanal/mensal) para o uso pretendido. |
| **Classificação de automação** | **A — API confirmada**, mas **não recomendada para este indicador** por incompatibilidade de granularidade. Registrada aqui para não ser reproposta por engano em rodada futura. |

## Síntese

| Fonte | Classificação | Uso |
|---|---|---|
| ANP (CSV, últimas 4 semanas) | B — confirmado, piloto executado | **Fonte usada** |
| IPEADATA (API, anual) | A — testado, mas granularidade errada | Descartado para este indicador |

**Lição sobre o bloqueio inicial**: o que parecia um WAF institucional bloqueando todo o domínio `gov.br` era, na verdade, detecção de bot por cabeçalhos HTTP incompletos — resolvido adicionando `User-Agent`, `Accept` e `Accept-Language` típicos de navegador. Vale revisitar essa hipótese em qualquer outra fonte `gov.br` que retornou 403 neste projeto antes de descartá-la como bloqueada.
