# Fontes: Portal FGV e INDATEND (síntese de inflação)

**Data de consulta**: 2026-09-22 (Discovery de Fontes — Lote 06b).

## Contexto

O indicador "INPC, ICV e outros indicadores de inflação (síntese)" do material do DIEESE (aba T21/T22) consolida manualmente **3 sub-fontes distintas**: IBGE (INPC, ver `docs/04-fontes/ibge-sidra.md`, Tabela 7063), Portal FGV, e INDATEND. Esta ficha cobre as duas últimas.

## Portal FGV (índices de preços: IGP-M, IGP-DI, IPC-Fi/IPC-S etc.)

| Campo | Valor |
|---|---|
| Status — portal direto | **NÃO CONFIRMADO — sem API pública.** Testados `portalibre.fgv.br/indices-de-precos`, `portal-da-inflacao-ibre.fgv.br`, `portalibre.fgv.br/en/fgv-dados`. Nenhum expõe endpoint REST/JSON ou download CSV/XLS gratuito e estruturado. O próprio portal declara que a consulta detalhada à maior parte das séries "ocorre mediante contrato e está restrita aos assinantes do FGV IBRE Dados" — acesso pago/por assinatura, não API pública. |
| **Rota alternativa CONFIRMADA**: BCB/SGS replica o IGP-M oficialmente. Testado `https://api.bcb.gov.br/dados/serie/bcdata.sgs.189/dados/ultimos/5?formato=json` — retornou 5 valores mensais reais de 2026 (ex.: 04/2026 = 2,73; 08/2026 = -0,22), consistentes com o IGP-M. | **Cobre apenas o IGP-M**, não os demais índices FGV eventualmente citados (ex. IPC-Fi, IPC-S) — esses não têm correspondente SGS confirmado, não testado nesta rodada. |
| Periodicidade | Mensal (IGP-M via BCB SGS). |
| Histórico | SGS mantém séries longas (não testada a profundidade completa nesta rodada — apenas "últimos 5"). |
| **Classificação de automação** | Portal FGV direto: **D — não confirmado**, acesso documentado é via contrato/assinatura. Via BCB/SGS 189 (IGP-M apenas): **A — API direta**, confirmada por teste real. |

## INDATEND

| Campo | Valor |
|---|---|
| Status | **Identificado com evidência primária direta (2026-09-23)** — não é uma instituição/índice de mercado externo. É o nome de arquivo de uma planilha Excel **interna do próprio DIEESE**, encontrada nos materiais originais do projeto: `materiais/originais/Apresentação de conjuntura/Backup/.../INDATEND {ano}_{mês}.xlsx` (3 cópias localizadas, de 2023, 2024 e 2025 — arquivada mensalmente como backup). |
| Título real do documento | Gravado nos metadados internos do próprio arquivo (`docProps/core.xml`): **"IBGE - Índices de Preços ao Consumidor"**. Criado em 2003, mantido até pelo menos ago/2025. Autor registrado: conta genérica do setor técnico do DIEESE ("TECNICOS-3"), não pessoa nomeada. |
| O que a planilha realmente é | Um banco de dados mestre que consolida manualmente, mês a mês, ~11 séries de preços/financeiras já conhecidas: ICV-DIEESE (elaboração própria, geral + 3 estratos), INPC-IBGE, IPCA-IBGE, IPC-FIPE, IPC-FGV, IGP-M, IGP-DI, IPA-DI, câmbio médio, salário mínimo (nominal e necessário), poupança (BCB SGS 196), TR mensal (BCB SGS 7811), BTN+TR. Todas as séries que já têm classificação neste catálogo continuam com a mesma classificação — nada muda para elas. |
| Citação original confirmada | `research/notas/DISCOVERY_FONTES_LOTE_PILOTO_01.md`, linha 77: a aba T21 da apresentação de conjuntura ("Outros Indicadores de Inflação") cita **"FONTE: INDATEND (PH/email)"** — bate exatamente com o conteúdo da planilha (as mesmas séries "outras" aparecem na aba Banco do arquivo INDATEND). "PH" são provavelmente as iniciais de quem mantém/envia o arquivo por e-mail — não confirmado, não é relevante para automação. |
| **Conclusão** | INDATEND não é uma fonte a ser automatizada — é o *processo de trabalho* (planilha interna + envio por e-mail) por trás de uma linha do material que já mistura fontes já cobertas por outros motores deste catálogo (INPC, IGP-M) com duas séries sem automação própria (ICV-DIEESE, elaboração própria da instituição; IPC-FIPE, da Fundação Instituto de Pesquisas Econômicas — não pesquisado neste projeto). |
| **Classificação de automação** | **E — manual, confirmado por evidência primária** (antes: "E, fonte desconhecida"; agora: "E, fonte é processo de trabalho interno do próprio DIEESE, com o dado bruto já identificado nos materiais originais do projeto"). Não é lacuna de pesquisa nem de engenharia — só mudaria se o DIEESE decidisse automatizar o próprio processo interno de atualização dessa planilha. |

## Síntese

| Sub-fonte | Classificação | Observação |
|---|---|---|
| INPC (IBGE/SIDRA 7063) | A | Ver `docs/04-fontes/ibge-sidra.md` |
| Portal FGV — direto | D | Requer contrato/assinatura |
| IGP-M via BCB/SGS 189 | A | Rota alternativa gratuita, cobre só IGP-M |
| INDATEND | E | Manual — identificado: planilha interna do próprio DIEESE (achada em `materiais/originais/`), não instituição externa |
