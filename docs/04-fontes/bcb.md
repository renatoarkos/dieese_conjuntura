# Fonte: Banco Central do Brasil (BCB)

## Identificação da instituição

- **Instituição produtora**: Banco Central do Brasil (BCB).
- **Sistema de disseminação**: Sistema Gerenciador de Séries Temporais (SGS), via API pública `api.bcb.gov.br`, e Portal de Dados Abertos (`dadosabertos.bcb.gov.br`).
- **Natureza**: fonte primária e oficial para câmbio e taxa de juros (Selic).
- **Data de consulta de todo este documento**: 2026-09-22.

## Achado central deste lote — a citação "SIDRA" do material do DIEESE está incorreta para ambos os indicadores

O material interno do DIEESE cita "SIDRA/BCB Tabela 3694" para câmbio e "SIDRA e BCB" para Selic. A pesquisa direta confirmou que **isso não corresponde à realidade atual**:

- A Tabela SIDRA 3694 **não é uma tabela de câmbio** — é uma tabela da Pesquisa Nacional de Saúde do Escolar (PeNSE), sobre acompanhamento de deveres de casa por pais/responsáveis. Confirmado diretamente via `servicodados.ibge.gov.br/api/v3/agregados/3694/metadados`. Uma varredura pelas tabelas vizinhas (3695-3699, 6295) mostrou que todas pertencem à mesma pesquisa escolar.
- Uma busca em todo o catálogo de agregados do IBGE por "câmbio"/"cambio" e por "selic"/"juro" retornou **zero resultados** — o SIDRA não hospeda, hoje, nenhuma tabela de câmbio ou de Selic.
- **Conclusão**: não há, atualmente, um caso de agregador (SIDRA republicando dado do BCB) em funcionamento para nenhum dos dois indicadores — a única fonte primária real e disponível é o **BCB/SGS diretamente**. A citação "SIDRA" no material do DIEESE provavelmente reflete uma convenção antiga de nomenclatura interna (possivelmente o número "3694" se refere, na verdade, ao código de série do SGS/BCB, não a uma tabela SIDRA) ou um erro de rotulagem. **Recomenda-se validação/correção junto à equipe do DIEESE.**

## Observação operacional geral

- A API pública do BCB (`api.bcb.gov.br/dados/serie/bcdata.sgs.<código>/dados`) **não exige autenticação** e foi testada com sucesso repetidas vezes (via `curl`), retornando JSON válido.
- Padrão confirmado:
  ```
  https://api.bcb.gov.br/dados/serie/bcdata.sgs.<código>/dados?formato=json&dataInicial=dd/MM/aaaa&dataFinal=dd/MM/aaaa
  ```
  (também aceita `/dados/ultimos/N`).
- **Limitação confirmada**: desde 26/03/2025, a API SGS limita consultas de período a 10 anos por requisição — contornável com múltiplas chamadas encadeadas.
- As páginas de metadados do SGS (`www3.bcb.gov.br/sgspub/...`) são renderizadas via JavaScript/sessão e não puderam ser lidas por fetch direto — os nomes oficiais de série foram confirmados via fichas do Portal de Dados Abertos (`dadosabertos.bcb.gov.br/dataset/<código>-...`) quando disponíveis, ou permanecem como hipótese numérica quando não.

---

## Indicador: Taxa de câmbio (venda, média de período)

| Campo | Valor |
|---|---|
| O que mede | Valor médio (não o fechamento pontual) da cotação de venda do dólar americano no câmbio livre ao longo de um período (mês ou ano). |
| Fonte primária real | BCB, Departamento de Estatísticas, via SGS. |
| Uso de agregador | **Não confirmado nenhum uso ativo de agregador** — ver achado central acima. |
| Série candidata (anual) | **SGS 3694** — testada via API, retorna série anual desde 1943, valores plausíveis (2023: 4,9953; 2024: 5,3920; 2025: 5,5855 R$/US$). Por cruzamento com o par confirmado 3691/3692 ("compra"/"venda", fim de período, anual — nome oficial confirmado no Portal de Dados Abertos), a série 3693/3694 segue o mesmo padrão (3693=compra, 3694=venda), portanto **hipótese forte, não confirmação textual direta** de que 3694 = venda, média de período, anual. |
| Série candidata (mensal) | **SGS 3698** — hipótese, validada por cross-check numérico: a média simples dos 12 valores mensais de 2024 (5,3895) bate muito próxima do valor anual de 3694 em 2024 (5,3920). |
| Documentação metodológica | Metodologia da taxa de referência PTAX, que alimenta as cotações que compõem as médias: `https://www.bcb.gov.br/conteudo/relatorioinflacao/EstudosEspeciais/EE042_A_taxa_de_cambio_de_referencia_Ptax.pdf` (localizado, não lido integralmente). Regida por Circular BCB 3.506/2010 e Resolução BCB 45/2020 (confirmação indireta, via busca). |
| Método de acesso | **CONFIRMADO** — API pública sem autenticação, testada com sucesso (`bcdata.sgs.3694` e `bcdata.sgs.3698`). |
| Periodicidade | Mensal (série 3698); a série diária subjacente (SGS 1) é atualizada diariamente. Publicação no 1º dia útil após o período de referência (por analogia com a série irmã 3692, confirmada). |
| Histórico | SGS 3694 desde 1943; SGS 3698 (hipótese) desde fevereiro/1953. |
| Dimensões | Série temporal simples (data/valor) — compra/venda e fim-de-período/média-de-período são séries SGS distintas, não dimensões de uma mesma série. |
| Revisões conhecidas | Mudanças na metodologia da PTAX (Circular 3.506/2010, Resolução 45/2020) — não confirmado se afetam a série histórica retroativamente. |
| Calendário | Não há calendário fixo — câmbio livre é divulgado diariamente (Sistema PTAX); o valor mensal/anual sai automaticamente no 1º dia útil após o período. |
| Limitações | (a) citação "SIDRA 3694" do material do DIEESE está incorreta — quem seguir essa referência textual sem checar a URL real acessa a tabela escolar errada; (b) limite de 10 anos por consulta da API SGS; (c) rótulo textual oficial exato de 3694/3698 não confirmado diretamente (apenas por hipótese numérica). |
| **Classificação de automação** | **A — API direta**, acesso público sem autenticação, testado. **Ressalva**: confirmar manualmente o rótulo oficial exato de 3694/3698 antes de uso em produção. |

---

## Indicador: Taxa Selic

| Campo | Valor |
|---|---|
| O que mede | Taxa básica de juros da economia. Duas variantes relevantes: **meta Selic** (definida pelo Copom a cada ~45 dias, % a.a.) e **Selic efetiva/over** (taxa média das operações compromissadas de um dia útil, % ao dia/mês/anualizada). |
| Fonte primária real | BCB — meta definida pelo Copom; taxa efetiva publicada pelo Departamento de Operações do Mercado Aberto via SGS. |
| Uso de agregador | **Não confirmado nenhum uso ativo de SIDRA** — busca no catálogo de agregados do IBGE por "selic"/"juro" retornou zero resultados. A citação "SIDRA e BCB" do material do DIEESE está incorreta quanto à parte SIDRA. |
| Séries candidatas testadas (todas responderam corretamente via API) | **SGS 432** — "Taxa de juros - Meta Selic definida pelo Copom" (nome oficial confirmado), % a.a., desde 05/03/1999. **SGS 11** — "Taxa de juros - Selic" (nome oficial confirmado), % ao dia, desde 04/06/1986. **SGS 1178** — Selic anualizada base 252 (nome confirmado apenas via página de metadados agregada). **SGS 4189** — Selic acumulada no mês, anualizada base 252, mensal, desde ago/1986. **SGS 4390** — Selic acumulada no mês (% no mês), mensal, desde ago/1986. |
| **Qual série corresponde exatamente ao material do DIEESE** | **CONFIRMADO por comparação direta com os 122 valores mensais da aba T14** (`materiais/originais/Apresentação de conjuntura/Apresentação_Conjuntura_4T_2025.xlsx`, leitura somente-leitura, 2026-09-22) contra as séries reais do BCB/SGS. Resultado: a série **não é uma fonte única constante** — é uma composição de duas séries SGS, trocadas em um ponto específico: <br>• **nov/2015 a jul/2024 (106 meses)**: bate exatamente (diferença < 0,01 p.p. em 100% dos meses) com **SGS 4189** — "Selic acumulada no mês, anualizada base 252". <br>• **ago/2024 em diante** (ago-dez/2024 e fev-out/2025, 15 de 16 meses testados): bate exatamente com **SGS 432** — "Meta Selic definida pelo Copom", valor de fim de mês. <br>• **jan/2025** é o único mês fora do padrão: valor do material (12,25) fica a 0,01 p.p. de SGS 4189 (12,24) e a 1,00 p.p. de SGS 432 (13,25) — provavelmente ainda usando 4189 com arredondamento diferente, um mês isolado na transição. <br>**A causa da mudança de série em ago/2024 não pode ser determinada apenas pelos dados** — é uma decisão de quem mantém a planilha (ver QF03b abaixo). |
| Documentação metodológica | Página de metadados agregada de todas as variantes Selic: `https://www4.bcb.gov.br/pec/series/port/metadados/mg45p.htm` (lida com sucesso). |
| Método de acesso | **CONFIRMADO** — API pública sem autenticação, testada com sucesso para as 5 séries candidatas. |
| Periodicidade | SGS 11 e 432: diárias (432 só muda em decisão do Copom). SGS 4189/4390: mensais. |
| Histórico | SGS 432 desde 05/03/1999; SGS 11 desde 04/06/1986; SGS 4189/4390 desde agosto/1986 (valores testados no período 1985-1996 coerentes com o cenário hiperinflacionário da época, reforçando autenticidade). |
| Dimensões | Série temporal simples. |
| Revisões conhecidas | Não localizada documentação específica de mudança na definição das séries Selic nesta pesquisa (não confirmado se existem). |
| Calendário | Copom se reúne a cada 45 dias (terça/quarta). Calendário 2026 localizado via busca (fontes de imprensa) — página oficial `bcb.gov.br/copom` não lida diretamente. Atas divulgadas às 8h da terça-feira seguinte à reunião. |
| Limitações | (a) a série é uma composição de duas fontes SGS diferentes ao longo do tempo (4189 até jul/2024, 432 a partir de ago/2024) — uma ingestão automatizada precisa replicar essa regra de troca, não assumir uma série única constante; (b) mesmo limite de 10 anos por consulta da API; (c) motivo da troca de série em ago/2024 não documentado, não confirmável só com dados. |
| **Classificação de automação** | **A — API direta**, com a fonte exata agora identificada e confirmada por comparação de 122 pontos de dados reais (ver acima). |

---

## Nota — "Taxa de juros real" (efeito Fisher)

Não é uma fonte de dados bruta: é uma **transformação** calculada pelo DIEESE sobre dois indicadores de entrada (Selic e IPCA), pela fórmula `((1+nominal/100)/(1+inflação/100)-1)*100`. Não possui produtor, série, código, calendário de divulgação ou classificação de automação próprios — depende inteiramente da correta identificação das fontes de Selic (acima) e de IPCA (ver `docs/04-fontes/ibge-sidra.md`). **Classificação de automação: não aplicável** (é fórmula, não fonte).

---

## Achado adicional — QF03 resolvida (2026-09-22)

Comparação direta dos 122 valores mensais da aba T14 (nov/2015-out/2025) contra as séries reais do BCB/SGS confirmou: a Selic usada pelo DIEESE é **SGS 4189 até jul/2024** e **SGS 432 a partir de ago/2024** — uma composição de duas séries, não uma única série constante. Ver ficha completa acima. Nova pergunta registrada (QF03b, em `research/notas/DISCOVERY_FONTES_LOTE_PILOTO_01.md`): por que essa troca ocorreu em ago/2024 — não determinável apenas pelos dados.

## Taxas médias de juros por modalidade (recursos livres, PF/PJ)

**Achado (Lote 03, 2026-09-22)**: o material do DIEESE já cita, célula a célula (aba T16), 4 códigos de série SGS — o único ponto de todo o material P1 com essa granularidade. Todos os 4 foram confirmados por chamada real de API.

| Código SGS | Nome oficial confirmado | Histórico | Valor de exemplo (jul/2026) |
|---|---|---|---|
| 20728 | Taxa média de juros das operações de crédito com recursos livres — Pessoas jurídicas — Aquisição de veículos | desde 03/2011 | 18,92% a.a. |
| 22019 | Taxa média de juros das operações de crédito com recursos livres — Pessoas jurídicas — Cartão de crédito rotativo | desde 03/2011 | 230,36% a.a. (alta volatilidade mês a mês — natureza da modalidade, não erro) |
| 20741 | Taxa média de juros das operações de crédito com recursos livres — Pessoas físicas — Cheque especial | desde 07/1994 (série mais longa das 4) | 137,30% a.a. |
| 20742 | Taxa média de juros das operações de crédito com recursos livres — Pessoas físicas — Crédito pessoal não consignado | desde 03/2011 | 110,95% a.a. |

Nomes oficiais confirmados via catálogo `dadosabertos.bcb.gov.br/api/3/action/package_search?q=<código>`. Todos periodicidade mensal, unidade % a.a.

**Classificação de automação: A — API direta**, para as 4 séries, confirmada por teste real e piloto técnico executado (`pipelines/ingestao/bloco_2_monetario_credito/coleta_juros_modalidade_bcb.py`).

## NFSP — Necessidade de Financiamento do Setor Público

**Achado importante (Lote 03, 2026-09-22)**: o código citado pelo material do DIEESE ("Tabela 5474") **responde à API mas não está no catálogo oficial de metadados do BCB** (`dadosabertos.bcb.gov.br` retorna zero resultados para 5474). O valor retornado (8,20-8,53% do PIB, mensal, desde 12/2001) é plausível e muito próximo, mas não idêntico, a séries catalogadas.

**Candidatos catalogados e confirmados**:
- **SGS 5760** — "NFSP sem desvalorização cambial (% PIB) — Fluxo acumulado em 12 meses — Juros nominais — Total — **Setor público consolidado**" — nome bate exatamente com a descrição do material do DIEESE. Histórico desde 11/2002. Valores recentes 8,28-8,80% do PIB.
- **SGS 5750** — mesma métrica, mas escopo "**Governo Federal e Banco Central**" (exclui estados/municípios/estatais). Histórico mais longo, desde 12/1991. Valores mais baixos (~7,3-7,9%).

**Esta é uma ambiguidade real de escopo, não apenas de rótulo** — 5760 (setor público total) e 5750 (só Governo Federal + BC) medem coisas diferentes. Trocar "5474" por um dos dois sem confirmação da equipe do DIEESE mudaria o significado do indicador. **Não incluído no piloto técnico** por este motivo — ver QF07 em `research/notas/DISCOVERY_FONTES_LOTE_PILOTO_01.md`.

**Classificação de automação**: D para 5474 (não catalogado, não confirmável). A (hipótese, não confirmação) para 5760 e 5750.

## Sistema de Expectativas de Mercado (Boletim Focus) — insumo para estimativas de INPC/IPCA

**Achado (Lote 05c, 2026-09-22)**: sistema **diferente** do SGS (que cobre Selic, câmbio, juros) — é o portal Olinda de Dados Abertos do BCB, protocolo OData. O material do DIEESE usa este sistema como insumo para suas próprias estimativas (nowcasting) de INPC/IPCA (abas T23/T24) — o dado bruto de expectativa de mercado, não a estimativa própria do DIEESE, foi confirmado.

| Campo | Valor |
|---|---|
| Status | **CONFIRMADO E TESTADO** — API OData pública, sem autenticação. |
| Endpoint | `https://olinda.bcb.gov.br/olinda/servico/Expectativas/versao/v1/odata/ExpectativaMercadoMensais?$filter=Indicador eq '<IPCA\|INPC>'&$format=json` (parâmetros precisam de URL-encoding). Testado com sucesso para IPCA e INPC — retornou registros reais com campos: Indicador, Data (coleta), DataReferencia (mês/ano previsto), Media, Mediana, DesvioPadrao, Mínimo, Máximo, número de respondentes. |
| Periodicidade | Publicação diária (dias úteis). |
| Histórico | Extenso — teste trouxe registros desde 2018 sem esforço adicional; série contínua desde a criação do Boletim Focus. |
| **Classificação de automação** | **A — API direta**, confirmada por teste real, piloto executado (para IPCA e INPC). |

## Endividamento e comprometimento de renda das famílias — parte BCB ("Tabela 27")

**Achado (Lote 06a, 2026-09-22)**: o rótulo "Tabela 27" é nomenclatura interna do DIEESE — não há correspondência literal no catálogo do BCB. A família de séries RNDBF (Indicadores de Endividamento e Comprometimento de Renda das Famílias, Depec/BCB) é a candidata correta, com 3 séries confirmadas por teste real:

| Código SGS | Nome oficial confirmado | Histórico |
|---|---|---|
| 29034 | Comprometimento de renda das famílias com o serviço da dívida com o SFN — com ajuste sazonal (RNDBF) | desde 03/2005 |
| 29265 | Idem, sem ajuste sazonal | desde 03/2005 |
| 29037 | Endividamento das famílias com o SFN em relação à renda acumulada dos últimos 12 meses (RNDBF) | desde 01/2005 |

Teste de range jan/2023-jun/2025 (período citado pelo material do DIEESE) na série 29034 retornou exatamente 30 registros mensais — bate com o período. **Qual série (ou combinação) corresponde exatamente à "Tabela 27" não está confirmado com certeza** — recomenda-se validar contra a planilha original do DIEESE antes de tratar como fechado.

**Classificação de automação**: **A — API direta**, confirmada por teste real para as 3 séries, piloto executado (coleta as 3 como séries RAW separadas, sem decidir a combinação).

## Saldo de crédito do Sistema Financeiro Nacional

**Achado (Lote 06a, 2026-09-22)**: BCB publica via SGS o conjunto "Saldo da carteira de crédito", com quebras por tomador (PF/PJ) e tipo de recurso (livre/direcionado). 6 séries confirmadas por teste real (incluindo teste específico no período jan/2015, início do histórico citado pelo material):

| Código SGS | Nome oficial confirmado |
|---|---|
| 20539 | Saldo da carteira de crédito — Total (PF+PJ, livres+direcionados) |
| 20541 | Saldo da carteira de crédito — Pessoas físicas — Total |
| 20540 | Saldo da carteira de crédito — Pessoas jurídicas — Total |
| 20542 | Saldo da carteira de crédito com recursos livres — Total |
| 20593 | Saldo da carteira de crédito com recursos direcionados — Total |
| 20570 | Saldo da carteira de crédito com recursos livres — Pessoas físicas — Total |

**Recortes adicionais não confirmados** (candidatos encontrados por busca no catálogo, NÃO testados via API — não usar sem confirmação): PJ-recursos livres-total (SGS 20543), PJ-recursos direcionados-total (SGS 20594); não foi encontrado um código único para "PF-recursos direcionados-total" (pode exigir soma de sub-séries, ex. financiamento imobiliário + crédito rural).

**Classificação de automação**: **A — API direta** para as 6 séries confirmadas, piloto executado. **D** para os 3 recortes adicionais não testados.

## Síntese de classificação de automação (BCB — todos os lotes)

| Indicador | Classificação | Confiança | Pendência |
|---|---|---|---|
| Taxa de câmbio (venda, média de período) | A | Alta — testado, piloto executado | Confirmar rótulo textual exato de 3694/3698 |
| Taxa Selic | A | Alta — fonte exata confirmada, piloto executado | QF03b (motivo da troca) — não bloqueia automação |
| Taxa de juros real (transformação) | Não aplicável | — | Depende de Selic (✓) + IPCA (✓) resolvidos |
| Juros por modalidade (4 séries) | A | Alta — testado, piloto executado | Nenhuma |
| NFSP (5474 citado pelo DIEESE) | D | Não catalogado oficialmente | QF07 — decisão entre 5760 (setor público total) e 5750 (Gov. Federal + BC) |
| Expectativas de Mercado — Focus (IPCA/INPC) | A | Alta — testado, piloto executado | Nenhuma |
| Endividamento familiar — parte BCB ("Tabela 27", família RNDBF, 3 séries) | A | Alta — testado, piloto executado | Confirmar qual série corresponde exatamente à "Tabela 27" |
| Saldo de crédito SFN (6 séries confirmadas) | A | Alta — testado, piloto executado | 3 recortes adicionais (PJ-livres, PJ-direcionados, PF-direcionados) não testados |
| IGP-M via BCB/SGS 189 (rota alternativa ao Portal FGV) | A | Alta — testado, piloto executado | Cobre só IGP-M, não outros índices FGV |
