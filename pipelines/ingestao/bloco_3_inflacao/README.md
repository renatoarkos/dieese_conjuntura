# Bloco 3 — Inflação e Custo de Vida

Este bloco reúne indicadores sobre a variação de preços e o custo de vida no
Brasil: os dois principais índices oficiais de inflação ao consumidor (IPCA e
INPC), o principal índice de preços de mercado usado em contratos e aluguéis
(IGP-M), o que o mercado financeiro projeta para a inflação futura
(expectativas Focus) e o preço de um item de peso relevante no orçamento
familiar (combustíveis). Formam um grupo porque, juntos, descrevem a mesma
pergunta — "os preços estão subindo, para quem, e o quanto?" — sob ângulos
diferentes: a medição oficial passada (IPCA/INPC), um índice de mercado com
metodologia distinta (IGP-M), a expectativa sobre o futuro (Focus) e um
insumo específico de preço (combustíveis).

Cada script tem uma fonte, um método de acesso e (em dois casos) uma
particularidade de coleta diferente — por isso cada um é descrito em detalhe
abaixo, em vez de descrever um padrão único para o bloco inteiro como no
Bloco 4. Ainda assim, todos seguem a mesma estrutura de código, modelada em
`pipelines/ingestao/bloco_1_macroeconomia/coleta_pib_sidra.py` (padrão
SIDRA/IBGE) e `coleta_cambio_bcb.py` (padrão BCB/SGS): buscam o dado na
fonte, gravam a resposta bruta (sem nenhuma transformação) em `data/raw/`, e
registram a coleta no Supabase. Nenhum deles calcula, agrega ou interpreta o
dado — isso é trabalho das camadas STAGING/CURATED/ANALYTICS, feito depois, a
partir dos arquivos que estes scripts gravam (ver `CLAUDE.md`, seção DADOS).

## Como rodar

Cada script é independente e não recebe argumentos:

```bash
python3 pipelines/ingestao/bloco_3_inflacao/coleta_ipca_sidra.py
```

Ao final, o script imprime o caminho do arquivo gravado (ex.:
`Coleta concluída: data/raw/ibge_sidra/ipca_sidra_7060_20260923T155730Z.json`)
e registra a coleta no Supabase. O nome do arquivo sempre inclui o
código/tabela da fonte e o instante da coleta em UTC — cada execução é uma
nova "fotografia" da série, nunca uma sobrescrita da coleta anterior.

## `coleta_ipca_sidra.py`

- **O que mede**: o IPCA (Índice Nacional de Preços ao Consumidor Amplo) —
  índice geral, com variação mensal, acumulada no ano, acumulada em 12 meses
  e peso mensal. É o índice oficial de inflação usado, entre outras coisas,
  como referência do regime de metas de inflação do Banco Central. Cobre
  famílias com renda de 1 a 40 salários mínimos em áreas urbanas.
- **De onde vem**: Tabela SIDRA 7060, alimentada pelo Sistema Nacional de
  Índices de Preços ao Consumidor (SNIPC/IBGE). Fonte confirmada em
  `docs/04-fontes/ibge-sidra.md`. A tabela cobre apenas a partir de
  janeiro/2020 (pesos da POF 2017-2018); períodos anteriores estão em
  tabelas históricas distintas, não coletadas por este script.
- **Por que este método**: API pública do SIDRA, sem autenticação, com o
  formato de URL padrão do sistema (ver docstring do script). É a via
  confirmada e testada — o acesso direto às páginas HTML institucionais do
  IBGE retorna HTTP 403 (bloqueio a user-agents automatizados), mas a API de
  dados responde normalmente.
- **Passo a passo**: monta a URL da consulta (tabela 7060, todos os
  territórios de nível Brasil, todas as variáveis, todos os períodos,
  classificação `c315/7169` — índice geral, sem abrir por grupo de despesa);
  busca os dados na API (`_buscar_dados`); grava a resposta bruta em disco
  com timestamp (`_salvar_raw`); registra a coleta no Supabase. Coleta apenas
  o índice geral — não inclui os agregados especiais "Serviços" e
  "Monitorados" citados no material do DIEESE, cuja tabela de origem exata
  ainda não foi localizada.

## `coleta_inpc_sidra.py`

- **O que mede**: o INPC (Índice Nacional de Preços ao Consumidor) — índice
  geral, com variação mensal, acumulada no ano, acumulada em 12 meses e peso
  mensal. Calculado pelo mesmo sistema do IBGE que o IPCA (SNIPC), a partir
  da mesma coleta de preços, mas para um público-alvo diferente: famílias de
  renda mais baixa (assalariadas, 1 a 5 salários mínimos), cuja cesta de
  consumo pesa de forma distinta da usada no IPCA.
- **De onde vem**: Tabela SIDRA 7063. Fonte confirmada em
  `docs/04-fontes/ibge-sidra.md`. Mesma cobertura a partir de janeiro/2020
  que a tabela do IPCA. Este script cobre apenas a sub-fonte INPC/IBGE da
  síntese "INPC, ICV e outros indicadores de inflação" do material do
  DIEESE — as demais sub-fontes (IGP-M/FGV, INDATEND) são tratadas em
  scripts e notas próprias.
- **Por que este método**: mesmo raciocínio do IPCA — API pública do SIDRA,
  testada e confirmada, em vez do acesso à página HTML (bloqueado por
  detecção de bot).
- **Passo a passo**: monta a URL da consulta (tabela 7063, todos os
  territórios de nível Brasil, todas as variáveis, todos os períodos,
  classificação `c315/7169` — índice geral); busca os dados na API
  (`_buscar_dados`); grava a resposta bruta em disco com timestamp
  (`_salvar_raw`); registra a coleta no Supabase.

## `coleta_igpm_bcb.py`

- **O que mede**: o IGP-M (Índice Geral de Preços — Mercado) — um índice de
  preços amplo (que combina preços ao produtor, ao consumidor e da
  construção civil), usado com frequência como referência em contratos de
  aluguel e outros reajustes de mercado.
- **De onde vem**: calculado e publicado oficialmente pela FGV/IBRE
  (Instituto Brasileiro de Economia da Fundação Getulio Vargas) — não pelo
  Banco Central. Este script, porém, coleta a série do **BCB/SGS (código
  189)**, não do Portal FGV/IBRE diretamente.
- **Por que este método**: o Portal FGV/IBRE não oferece API pública nem
  download gratuito estruturado — o acesso à série é via contrato/assinatura
  paga (confirmado na pesquisa de fontes do projeto). Como o Banco Central
  replica oficialmente a série do IGP-M dentro do seu próprio sistema SGS,
  este script usa essa ROTA ALTERNATIVA gratuita e pública em vez da fonte
  original — o dado é o mesmo, muda só o canal de acesso. Essa rota cobre
  apenas o IGP-M, não os demais índices da FGV eventualmente citados pelo
  material do DIEESE (ex. IPC-Fi, IPC-S), que não têm correspondente
  confirmado no SGS.
- **Passo a passo**: monta a URL de consulta da série SGS 189 (mesmo padrão
  de URL do SGS usado em `coleta_cambio_bcb.py`); busca os dados na API
  (`_buscar_dados`); grava a resposta bruta em disco com timestamp
  (`_salvar_raw`); registra a coleta no Supabase.

## `coleta_expectativas_focus_bcb.py`

- **O que mede**: as expectativas de mercado (Boletim Focus) para IPCA e
  INPC — a pesquisa diária do Banco Central junto a instituições financeiras
  sobre suas projeções futuras para esses indicadores (média, mediana,
  desvio-padrão, mínimo, máximo e número de respondentes, por mês de
  referência projetado).
- **De onde vem**: Sistema de Expectativas de Mercado do BCB, via portal
  Olinda de Dados Abertos — um sistema DIFERENTE do SGS usado pelos outros
  scripts do BCB neste piloto (câmbio, IGP-M). Fonte confirmada em
  `docs/04-fontes/bcb.md`.
- **Por que este método**: API Olinda, protocolo OData — padrão de consulta
  por parâmetros de URL (`$filter`, `$format`), montados com
  `urllib.parse.urlencode` em vez de concatenação simples de texto, porque
  os valores do filtro contêm espaços e aspas que precisam de codificação
  correta. Este é o dado bruto que o DIEESE usa como INSUMO para suas
  próprias estimativas (nowcasting) de INPC/IPCA — não a estimativa em si,
  que é produzida depois, em camada posterior.
- **Passo a passo**: para cada indicador (IPCA, INPC), monta a URL com os
  parâmetros OData do filtro (`_url`); busca os dados na API
  (`_buscar_dados`); grava a resposta de cada indicador num arquivo separado
  em disco com timestamp (`_salvar_raw`); registra cada arquivo no Supabase.

## `coleta_combustiveis_anp.py`

- **O que mede**: os preços de combustíveis coletados semanalmente por posto
  revendedor — gasolina/etanol, diesel/GNV e GLP (gás de cozinha) —, os três
  itens citados no material do DIEESE.
- **De onde vem**: ANP (Agência Nacional do Petróleo, Gás Natural e
  Biocombustíveis), série "últimas 4 semanas" de microdados por posto. Fonte
  confirmada em `docs/04-fontes/anp-ipeadata.md`. Este script coleta apenas
  essa série corrente, não a série histórica completa desde 2004.
- **Por que este método**: download estruturado (CSV) direto do domínio
  `gov.br`, com cabeçalhos HTTP de navegador completos (`User-Agent`,
  `Accept`, `Accept-Language`). A primeira tentativa de acesso, sem esses
  cabeçalhos, retornava HTTP 403 — achado do Discovery deste projeto: **não
  era bloqueio institucional**, e sim detecção de bot por ausência de
  cabeçalhos típicos de navegador. Adicionando-os, o acesso passou a
  funcionar normalmente (HTTP 200), permitindo extrair os links reais de
  download do próprio HTML da página, em vez de adivinhar um padrão de URL.
  Essa lição vale para qualquer outra fonte `gov.br` que retorne 403 neste
  projeto antes de ser descartada como bloqueada.
- **Passo a passo**: para cada um dos três arquivos, faz o download do CSV
  com os cabeçalhos de navegador (`_baixar_arquivo`); grava o conteúdo bruto
  em disco com timestamp (`_salvar_raw`); registra cada arquivo no Supabase.

## Fora do escopo desta rodada

Este bloco também contém `coleta_cesta_basica_dieese.py`, que coleta o
boletim mensal "Análise da Cesta Básica de Alimentos" (DIEESE/Conab)
diretamente do site do DIEESE. Por decisão do responsável do projeto,
registrada em `docs/00-visao-geral/ESTADO_DO_PROJETO.md`, motores de fontes
DIEESE estão pausados por enquanto — esse script não foi alterado nem
documentado nesta rodada.
