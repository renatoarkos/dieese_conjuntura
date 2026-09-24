# Mapa de fontes já investigadas

Antes de pesquisar uma fonte nova, confira esta lista — pode já ter sido
investigada (confirmada, descartada, ou parcialmente resolvida). Cada linha
aponta para a ficha completa em `docs/04-fontes/`, que tem a URL exata, o
teste real e a classificação A-E (ver
[`02-metodologia-de-investigacao.md`](02-metodologia-de-investigacao.md)).

## Fontes já integradas ao catálogo de 36 indicadores (motor construído)

| Ficha | Instituições cobertas |
|---|---|
| `docs/04-fontes/ibge-sidra.md` | IBGE/SIDRA — PIB, IPCA, INPC, PNAD Contínua (desocupação, ocupação, participação, rendimento, sindicalização), PMC/PMS/PIM, taxa de investimento |
| `docs/04-fontes/bcb.md` | Banco Central — SGS (Selic, câmbio, juros, crédito, endividamento, IC-Br), Focus/Olinda |
| `docs/04-fontes/mdic-tesouro.md` | MDIC/Comex Stat (balança comercial), SICONFI/Tesouro (limite fiscal por UF) |
| `docs/04-fontes/fmi-cni.md` | FMI/WEO (PIB mundial), CNI (utilização da capacidade instalada) |
| `docs/04-fontes/fecomercio-peic.md` | FecomercioSP (endividamento das famílias, parte PEIC) |
| `docs/04-fontes/mte-caged.md` | MTE/PDET — Novo CAGED (microdados) |
| `docs/04-fontes/anp-ipeadata.md` | ANP (combustíveis) |
| `docs/04-fontes/dieese-publicacoes.md` | DIEESE — Cesta Básica, ICT, Balanço das Greves, De Olho nas Negociações |
| `docs/04-fontes/fgv-indatend.md` | FGV/IGP-M (via BCB), INDATEND (identificado como planilha interna do DIEESE) |
| `docs/04-fontes/outras-instituicoes-2026-09.md` (BNDES) | BNDES — desembolsos (promovido a motor 2026-09-24; achado que é microdado por operação, classificação C, não A) |
| `docs/04-fontes/outras-instituicoes-mundiais-2026-09.md` (ILOSTAT) | ILOSTAT/OIT — desemprego comparado internacionalmente (promovido a motor 2026-09-24; **não confundir com a série do IBGE já integrada** — ver indicador 38 em `docs/05-indicadores/CATALOGO_MESTRE_INDICADORES.md`) |

## Fontes investigadas, testadas, mas **fora** do catálogo atual (candidatas)

Nenhuma destas está ligada a um indicador do catálogo — são pesquisa
exploratória, prontas para quando o projeto decidir priorizar um domínio
novo (mercado financeiro, comparação internacional, fiscal federal etc.).
Duas linhas (BNDES, ILOSTAT) já foram promovidas a motor de produção — as
fichas continuam valendo como registro do teste original.

| Ficha | O que cobre | Melhores achados (API real, sem cadastro) |
|---|---|---|
| `docs/04-fontes/outras-instituicoes-2026-09.md` | Brasil: RAIS, B3, CVM, ~~BNDES~~ (já integrado), Receita Federal, ANBIMA, dados.gov.br, IPEADATA (outros temas), IBGE além do SIDRA padrão, BCB além do SGS/Focus | BCB/SCR e taxas por instituição |
| `docs/04-fontes/outras-instituicoes-mundiais-2026-09.md` | Mundo: Banco Mundial, ~~ILOSTAT~~ (já integrado), BIS, OCDE, Eurostat, UN Comtrade, CEPALSTAT, FRED, FMI além do WEO | Banco Mundial (usado no exercício guiado), BIS |
| `docs/04-fontes/bibliotecas-python-dados-socioeconomicos-2026-09.md` | Bibliotecas Python de conveniência (não instituições) | `yfinance`, `python-bcb`, `sidrapy`, `ipeadatapy` |

## Como usar este mapa

1. Procure a instituição/tema nesta lista.
2. Se já está aqui, abra a ficha — ela já tem a URL testada, o formato de
   resposta, e diz se dá para automatizar sem cadastro.
3. Se **não** está aqui, é uma fonte genuinamente nova — siga o processo de
   [`02-metodologia-de-investigacao.md`](02-metodologia-de-investigacao.md)
   e crie uma ficha nova em `docs/04-fontes/`, seguindo o mesmo formato das
   existentes (não invente um formato novo).
4. Depois de confirmar e classificar, se for A/B/C e o indicador for
   priorizado, siga [`03-anatomia-de-um-motor.md`](03-anatomia-de-um-motor.md)
   para construir o script.
