# Fontes: FMI (WEO) e CNI (Indicadores Industriais)

**Data de consulta**: 2026-09-22 (Discovery de Fontes — Lote 05a).

## PIB Mundial e estimativas — FMI (World Economic Outlook)

| Campo | Valor |
|---|---|
| Instituição | Fundo Monetário Internacional (FMI/IMF). |
| Status | **CONFIRMADO — API pública SDMX 3.0**, sem chave/autenticação. Testado com sucesso: `https://api.imf.org/external/sdmx/3.0/data/dataflow/IMF.RES/WEO/~/A.*.NGDP_RPCH?startPeriod=2020&endPeriod=2026` retornou dados reais (variação real do PIB, % a.a., por país/agregado). |
| Documentação | `https://data.imf.org/en/Resource-Pages/IMF-API` confirma API SDMX 2.1 e 3.0. O portal de documentação interativa (`portal.api.imf.org`) exige login — mas isso não impede o acesso direto aos dados. |
| Limitação | Os códigos de país do dataflow WEO **não são ISO3 simples** (testar "BRA" retornou zero séries) — é necessário mapear o codelist de país (`COUNTRY`) e de indicador antes de filtrar por país específico. O piloto técnico coleta com curinga `*` (todos os países/agregados) para não adivinhar um código não confirmado. |
| Periodicidade | Semestral (abril e outubro). |
| Histórico | 1980 até o presente + ~5 anos de projeção — cobre o período 2016-2026 do material do DIEESE. |
| **Classificação de automação** | **A — API direta**, confirmada por teste real. |

## UCI — Utilização da Capacidade Instalada — CNI

| Campo | Valor |
|---|---|
| Instituição | Confederação Nacional da Indústria (CNI) — entidade privada. |
| **Alerta de atribuição**: o material do DIEESE cita a fonte como "CNI - ICEI", mas **a UCI não faz parte do ICEI** (Índice de Confiança do Empresário Industrial, um indicador de expectativa/sentimento). A UCI pertence a outro levantamento da CNI — os **"Indicadores Industriais"** (produção, faturamento, emprego, massa salarial, utilização da capacidade instalada). Confirmado por leitura direta das duas páginas oficiais distintas do Portal da Indústria. Recomenda-se sinalizar essa imprecisão ao DIEESE. |
| Status | **CONFIRMADO — download estruturado (Excel)**, sem API nem portal de dados abertos. |
| Método de acesso | Página oficial `portaldaindustria.com.br/estatisticas/indicadores-industriais/` traz link para a "Série Histórica" em Excel. **URL não é estável** — o nome do arquivo muda a cada divulgação mensal (ex.: `..._julho2026.xlsx`). Piloto técnico usa raspagem mínima e direcionada (regex sobre a URL, não parsing de estrutura de página) para localizar o link vigente a cada execução — mais robusto que fixar uma URL que expira. |
| Alternativa não confirmada | Existe também um portal de consulta legado (`indicadores.sistemaindustria.com.br`, tecnologia Java Server Faces) — não expõe API/JSON, é interface HTML de consulta com exportação manual via postback de formulário; não testado quanto à automação. |
| Periodicidade | Mensal. |
| Histórico | Série histórica em Excel cobre múltiplos anos (início exato não determinado nesta rodada). |
| **Classificação de automação** | **B, com ressalva** — arquivo confiável e estruturado uma vez localizado, mas a URL muda a cada mês (instabilidade está na descoberta do link, não no conteúdo do arquivo em si). |

## Síntese

| Indicador | Classificação | Confiança |
|---|---|---|
| PIB Mundial (FMI WEO) | A | Alta — testado, piloto executado |
| UCI (CNI Indicadores Industriais) | B (raspagem direcionada) | Alta — testado, piloto executado |
