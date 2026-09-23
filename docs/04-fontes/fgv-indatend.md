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
| Status | **Nenhuma fonte pública identificável.** Busca não retornou nenhuma instituição, sistema ou índice publicamente conhecido com esse nome/sigla. |
| Confirma | O que o material do DIEESE já indicava: "Fonte: INDATEND (PH/e-mail)" — recebimento manual e informal, sem presença pública rastreável. |
| **Classificação de automação** | **E — manual/específico.** Não há indício de que seja automatizável sem mudança de processo institucional do DIEESE (contato direto com quem fornece o dado por e-mail). |

## Síntese

| Sub-fonte | Classificação | Observação |
|---|---|---|
| INPC (IBGE/SIDRA 7063) | A | Ver `docs/04-fontes/ibge-sidra.md` |
| Portal FGV — direto | D | Requer contrato/assinatura |
| IGP-M via BCB/SGS 189 | A | Rota alternativa gratuita, cobre só IGP-M |
| INDATEND | E | Manual, sem fonte pública — confirma classificação já esperada pelo material |
