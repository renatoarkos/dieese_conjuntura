# Bloco 4 — Mercado de Trabalho

Este bloco reúne indicadores sobre a situação da força de trabalho no Brasil:
quantas pessoas estão desocupadas, quantas participam do mercado de trabalho,
sob que tipo de vínculo as pessoas ocupadas trabalham, qual a proporção delas
sindicalizada, e a intensidade/natureza do conflito capital-trabalho. Seis
scripts vêm da mesma pesquisa de origem — a PNAD Contínua (Pesquisa Nacional
por Amostra de Domicílios Contínua) do IBGE — acessada pela API pública do
SIDRA. Três outros vêm de boletins institucionais que o próprio DIEESE
publica (ver seção dedicada mais abaixo). Formam um grupo porque descrevem,
em conjunto, diferentes ângulos da mesma realidade: quem está trabalhando,
quem está procurando trabalho, em que condição, com que grau de organização
coletiva, e como o conflito trabalhista se expressa.

Os seis scripts SIDRA seguem o mesmo padrão de coleta já usado no restante do
projeto (ver `pipelines/ingestao/bloco_1_macroeconomia/coleta_pib_sidra.py`,
o modelo de referência): consultam a API do SIDRA, gravam a resposta bruta
(sem nenhuma transformação) em `data/raw/ibge_sidra/` e registram a coleta no
Supabase. Os três scripts de boletins do DIEESE seguem o padrão de "busca por
edição sequencial + download direto" (ver
`pipelines/ingestao/bloco_3_inflacao/coleta_cesta_basica_dieese.py` para o
primeiro exemplo desse padrão no projeto). Nenhum deles calcula, agrega ou
interpreta o dado — isso é trabalho das camadas STAGING/CURATED/ANALYTICS,
feito depois, a partir dos arquivos que estes scripts gravam (ver
`CLAUDE.md`, seção DADOS).

## Como rodar

Cada script é independente e não recebe argumentos:

```bash
python3 pipelines/ingestao/bloco_4_mercado_trabalho/coleta_desocupacao_sidra.py
```

Ao final, o script imprime o caminho do arquivo gravado (ex.:
`Coleta concluída: data/raw/ibge_sidra/desocupacao_sidra_4093_20260923T155710Z.json`)
e registra a coleta no Supabase. O nome do arquivo sempre inclui o número da
tabela SIDRA de origem e o instante da coleta em UTC — cada execução é uma
nova "fotografia" da série, nunca uma sobrescrita da coleta anterior.

## `coleta_desocupacao_sidra.py`

- **O que mede**: a taxa de desocupação — proporção de pessoas de 14 anos ou
  mais que estão desocupadas (procurando trabalho ativamente e disponíveis
  para começar a trabalhar) em relação à força de trabalho total. É o
  indicador oficial de "taxa de desemprego" do IBGE.
- **De onde vem**: Tabela SIDRA 4093, alimentada pela PNAD Contínua
  trimestral. Fonte confirmada em `docs/04-fontes/ibge-sidra.md`.
- **Passo a passo**: monta a URL da consulta (tabela 4093, todos os
  territórios de nível Brasil, todas as variáveis, todos os períodos,
  classificação por sexo); busca os dados na API (`_buscar_dados`); grava a
  resposta bruta em disco com timestamp (`_salvar_raw`); registra a coleta no
  Supabase.

## `coleta_posicao_ocupacao_sidra.py`

- **O que mede**: quantas pessoas de 14 anos ou mais estão ocupadas, por
  "posição na ocupação e categoria do emprego" — o tipo de vínculo com o
  trabalho (empregada com carteira, sem carteira, setor público, trabalhadora
  doméstica, empregadora, conta própria, trabalhadora familiar auxiliar,
  entre outras). É a base para acompanhar, por exemplo, o peso da
  informalidade entre os ocupados.
- **De onde vem**: Tabela SIDRA 4097, alimentada pela PNAD Contínua
  trimestral. Fonte confirmada em `docs/04-fontes/ibge-sidra.md`.
- **Passo a passo**: monta a URL da consulta (tabela 4097, todos os
  territórios de nível Brasil, todas as variáveis, todos os períodos,
  classificação por posição na ocupação); busca os dados na API
  (`_buscar_dados`); grava a resposta bruta em disco com timestamp
  (`_salvar_raw`); registra a coleta no Supabase.

## `coleta_taxa_participacao_sidra.py`

- **O que mede**: a taxa de participação na força de trabalho — proporção de
  pessoas de 14 anos ou mais que estão na força de trabalho (ocupadas ou
  desocupadas procurando emprego) em relação ao total da população nessa
  faixa etária. É um indicador complementar à taxa de desocupação: mostra
  quantas pessoas participam efetivamente do mercado de trabalho, e não só
  quantas dessas estão sem trabalho.
- **De onde vem**: Tabela SIDRA 6461, alimentada pela PNAD Contínua
  trimestral. Não tem recorte adicional por sexo ou idade nesta tabela.
  Fonte confirmada em `docs/04-fontes/ibge-sidra.md`.
- **Passo a passo**: monta a URL da consulta (tabela 6461, todos os
  territórios de nível Brasil, todas as variáveis, todos os períodos, sem
  classificação adicional); busca os dados na API (`_buscar_dados`); grava a
  resposta bruta em disco com timestamp (`_salvar_raw`); registra a coleta no
  Supabase.

## `coleta_rendimento_medio_real_sidra.py`

- **O que mede**: o valor médio mensal do rendimento do trabalho habitualmente
  recebido no trabalho principal, pessoas de 14+ anos ocupadas, já em termos
  reais (a própria tabela do IBGE entrega deflacionado), por posição na
  ocupação/categoria do emprego.
- **De onde vem**: Tabela SIDRA 5440, alimentada pela PNAD Contínua
  trimestral. Fonte confirmada em `docs/04-fontes/ibge-sidra.md` — era o
  único indicador do catálogo com fonte confirmada que ainda não tinha motor
  construído; a chamada de valores foi testada diretamente antes de escrever
  este script (233 registros, 1º tri/2012 a 2º tri/2026).
- **Diferença em relação aos outros scripts deste bloco**: a URL não
  especifica um código de classificação — testado que, se você omitir, o
  SIDRA devolve todas as categorias de "posição na ocupação" por padrão, sem
  precisar descobrir o código exato.
- **Limitação que este motor não resolve**: o material do DIEESE indica um
  deflacionamento adicional próprio, por cima do valor que a 5440 já entrega
  real — não dá para saber, só com fontes públicas, se isso é dupla deflação
  ou se o DIEESE parte de outra série. Ver `docs/04-fontes/ibge-sidra.md`.
- **Passo a passo**: monta a URL da consulta (tabela 5440, todos os
  territórios de nível Brasil, todas as variáveis, todos os períodos); busca
  os dados na API (`_buscar_dados`); grava a resposta bruta em disco com
  timestamp (`_salvar_raw`); registra a coleta no Supabase.

## `coleta_sindicalizacao_sidra.py`

- **O que mede**: a taxa de sindicalização — proporção de pessoas ocupadas de
  14 anos ou mais que são sindicalizadas, por grupamento de atividade no
  trabalho principal.
- **De onde vem**: Tabela SIDRA 8676. Diferente dos três scripts anteriores
  deste bloco, esta tabela não vem da PNAD Contínua trimestral regular, e
  sim de um suplemento **anual e descontínuo** da mesma pesquisa (módulo
  "Características Adicionais do Mercado de Trabalho") — a série tem um
  hiato em 2020 e 2021 (provável disrupção da pandemia no levantamento) e
  cobre apenas Brasil e Grandes Regiões (sem UF/município). Fonte confirmada
  em `docs/04-fontes/ibge-sidra.md`, com valor de 2024 (8,9%) cruzado
  diretamente contra o material do DIEESE.
- **Passo a passo**: monta a URL da consulta (tabela 8676, todos os
  territórios de nível Brasil, variável 12535 — "Taxa de sindicalização",
  todos os períodos disponíveis, classificação por grupamento de atividade);
  busca os dados na API (`_buscar_dados`); grava a resposta bruta em disco
  com timestamp (`_salvar_raw`); registra a coleta no Supabase.

## Boletins institucionais do próprio DIEESE

Três scripts deste bloco não vêm do IBGE/SIDRA — coletam boletins públicos
que o próprio DIEESE publica, calculados a partir de fontes que ele mesmo
processa (Mediador/MTE, PNAD Contínua, notícias de imprensa). Todos os três
foram reclassificados de "PDF sem automação" (E) para "download estruturado"
(B) depois de um teste técnico direto (`pdftotext -layout -enc UTF-8`) e,
nos dois últimos, de uma validação cruzada rigorosa contra a apresentação
interna do DIEESE (`materiais/originais/`) — os números batem exatamente.

### `coleta_negociacao_coletiva_dieese.py`

- **O que mede**: dois indicadores do mesmo boletim — distribuição dos
  reajustes salariais negociados em comparação com o INPC, e valor
  médio/mediano dos pisos salariais por categoria.
- **De onde vem**: boletim mensal "De Olho nas Negociações", que o DIEESE
  calcula a partir dos instrumentos coletivos registrados no Mediador (MTE)
  — o Mediador em si não tem API nem exportação em massa (confirmado em duas
  rodadas de investigação), mas o boletim do DIEESE já entrega o resultado
  calculado. Fonte confirmada em `docs/04-fontes/dieese-publicacoes.md`.
- **Passo a passo**: a partir de uma âncora de edição conhecida, estima e
  testa a edição mais recente (numeração sequencial, não ano/mês); baixa o
  PDF; registra a coleta no Supabase.

### `coleta_ict_dieese.py`

- **O que mede**: o Índice da Condição do Trabalho (ICT-DIEESE) — índice
  sintético (0 a 1) sobre condições de inserção no mercado de trabalho, a
  partir da PNAD Contínua, combinando inserção ocupacional, desocupação e
  rendimento.
- **De onde vem**: boletim trimestral público do DIEESE. **Validado**: valor
  do 3º tri/2025 no boletim público (0,68) bate exatamente com o mesmo
  trimestre na apresentação interna do DIEESE (0,6848). Fonte confirmada em
  `docs/04-fontes/dieese-publicacoes.md`.
- **Particularidade**: o nome do arquivo do boletim mudou de padrão ao longo
  do tempo (3 formatos diferentes já observados) — o script tenta os três
  para cada edição candidata.
- **Passo a passo**: estima a edição mais recente pela âncora conhecida;
  tenta os 3 padrões de nome de arquivo; baixa o PDF; registra no Supabase.

### `coleta_greves_dieese.py`

- **O que mede**: três indicadores do mesmo boletim — número de greves,
  principais categorias grevistas e principais reivindicações, por esfera
  (privada/funcionalismo público/empresas estatais).
- **De onde vem**: "Balanço das Greves", série de Estudos e Pesquisas do
  DIEESE, a partir do Sistema de Acompanhamento de Greves (SAG) — mais de 45
  mil registros desde 1978, alimentado por notícias de imprensa. **Validado**:
  total de greves de 2024 (880) e as 5 principais reivindicações (percentuais
  idênticos até a casa decimal) batem exatamente entre o boletim público e a
  apresentação interna do DIEESE. Fonte confirmada em
  `docs/04-fontes/dieese-publicacoes.md`.
- **Particularidade**: a pasta e o nome do arquivo mudaram ao longo do tempo
  (`balancodasgreves/` até ~2023, `estudosepesquisas/` depois) — o script
  tenta as duas combinações para cada edição candidata.
- **Limitação documentada no próprio boletim**: os números de períodos
  recentes são revisados retroativamente entre edições — ao montar série
  histórica, usar sempre o valor da edição mais recente para cada período.
- **Passo a passo**: tenta primeiro edições mais novas que a âncora conhecida
  (pode ter saído uma edição nova), depois a própria âncora; baixa o PDF;
  registra no Supabase.
