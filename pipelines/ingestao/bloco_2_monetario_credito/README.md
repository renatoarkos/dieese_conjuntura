# Bloco 2 — Monetário e Crédito

Este bloco reúne os scripts de coleta bruta (camada RAW, ver `CLAUDE.md` na raiz do
repositório) dos indicadores que descrevem o custo do dinheiro e o acesso das famílias
ao crédito: a taxa básica de juros da economia (Selic), quanto custa efetivamente tomar
crédito em cada modalidade (cheque especial, crédito pessoal, veículos, cartão
rotativo), o quanto as famílias já estão comprometidas com dívidas e quanto desse
crédito está de fato emprestado, por quem e sob que tipo de recurso. São cinco scripts,
todos com fonte no Banco Central (via SGS) exceto um, que complementa a leitura de
endividamento com a pesquisa de opinião da FecomercioSP — juntos, eles respondem à
pergunta "como está o crédito agora", um recorte que conversa diretamente com a
macroeconomia geral (Bloco 1) mas com foco na política monetária e no bolso das
famílias.

Cada script é independente, autoexecutável e não depende de nenhum outro script deste
bloco para rodar. Nenhum deles transforma dado: cada um busca a resposta de uma fonte
pública e grava exatamente o que recebeu em `data/raw/`, sem calcular, filtrar,
converter ou "limpar" nada — essa é a regra da camada RAW (ver `CLAUDE.md`, seção
DADOS). Todos são Python puro, sem dependências externas (ver
`docs/08-decisoes-adr/0001-stack-minima-piloto-ingestao.md`).

## Como rodar

Cada script roda isoladamente, a partir da raiz do repositório:

```bash
python3 pipelines/ingestao/bloco_2_monetario_credito/coleta_selic_bcb.py
```

Ao final, o script imprime o caminho do(s) arquivo(s) gravado(s) em `data/raw/` e tenta
registrar a coleta no Supabase (upload do arquivo + linha de log em `raw_ingestoes`,
função `registrar_coleta` de `pipelines/supabase_raw.py`) — se as credenciais do
Supabase não estiverem configuradas em `.env`, essa etapa é apenas ignorada, sem
interromper a coleta.

## Os 5 scripts

### `coleta_selic_bcb.py` — Taxa Selic

- **O que mede**: a taxa básica de juros da economia brasileira. A série usada pelo
  material do DIEESE não vem de uma fonte única e constante: é uma composição de duas
  séries do BCB/SGS, confirmada por comparação ponto a ponto com 122 valores mensais do
  material original — SGS 4189 ("Selic acumulada no mês, anualizada base 252") de
  nov/2015 a jul/2024, e SGS 432 ("Meta Selic definida pelo Copom") de ago/2024 em
  diante.
- **De onde vem**: Banco Central do Brasil, Sistema Gerenciador de Séries Temporais
  (SGS).
- **Por que este método**: a API do SGS é pública, sem autenticação, e devolve
  diretamente a lista de observações em JSON — via confirmada em
  `docs/04-fontes/bcb.md`. Como decidir onde cortar uma série e começar a outra é uma
  transformação, o script não aplica essa regra: coleta as duas séries completas, cada
  uma desde seu início histórico, e deixa a composição para a camada STAGING.
- **Particularidade**: as duas séries somam décadas de histórico e a API do BCB se
  mostrou instável sob chamadas sucessivas nesta rodada (erros HTTP 406 e corpos vazios
  intermitentes). Por isso este é o único script do bloco com lógica de retry (repete
  cada chamada HTTP algumas vezes, com espera crescente, antes de desistir) e paginação
  (quando a série é longa demais para vir numa chamada só, busca em janelas de até 10
  anos — limite documentado da própria API desde 26/03/2025 — e concatena o resultado).
- **Passo a passo**: para cada uma das duas séries (`INICIO_SERIE`), tenta buscar o
  histórico completo numa única chamada; se a API rejeitar, pagina em janelas de até 10
  anos; grava cada série num arquivo JSON separado em `data/raw/bcb_sgs/` (nome com o
  código da série e um timestamp UTC compartilhado pelas duas coletas); registra cada
  arquivo no Supabase.

### `coleta_juros_modalidade_bcb.py` — Juros por modalidade de crédito

- **O que mede**: taxas médias de juros (% a.a., mensais) cobradas em quatro modalidades
  de crédito com recursos livres — SGS 20728 (PJ, aquisição de veículos), SGS 22019 (PJ,
  cartão de crédito rotativo), SGS 20741 (PF, cheque especial) e SGS 20742 (PF, crédito
  pessoal não consignado).
- **De onde vem**: Banco Central do Brasil, SGS. Os quatro códigos já eram citados
  célula a célula no material interno do DIEESE (aba T16) — o único ponto do material
  com esse nível de granularidade — e foram confirmados por chamada real de API.
- **Por que este método**: mesma API pública do SGS, sem autenticação, usada pelos
  demais scripts BCB deste piloto — via direta e já confirmada, sem ambiguidade sobre
  qual código usar (diferente de outros indicadores deste bloco).
- **Passo a passo**: para cada um dos 4 códigos (`SERIES`), busca os dados na API e grava
  um arquivo JSON separado em `data/raw/bcb_sgs/` (nome com o código da série e um
  timestamp UTC compartilhado pelas quatro coletas); registra cada arquivo no Supabase.

### `coleta_endividamento_bcb.py` — Endividamento das famílias (parte BCB)

- **O que mede**: comprometimento de renda e endividamento das famílias com o Sistema
  Financeiro Nacional — três séries candidatas da família RNDBF (Indicadores de
  Endividamento e Comprometimento de Renda das Famílias, Depec/BCB): SGS 29034
  (comprometimento de renda, com ajuste sazonal), SGS 29265 (idem, sem ajuste sazonal) e
  SGS 29037 (endividamento acumulado em 12 meses).
- **De onde vem**: Banco Central do Brasil, SGS. É a parte BCB do indicador
  "endividamento familiar" do material do DIEESE — a outra parte, da pesquisa PEIC da
  FecomercioSP, é coletada pelo script seguinte.
- **Por que este método**: mesma API pública do SGS. O material do DIEESE rotula este
  indicador como "Tabela 27", um nome interno sem correspondência literal confirmada no
  catálogo do BCB — a família RNDBF é a candidata identificada, mas qual das três séries
  (ou combinação delas) corresponde exatamente à "Tabela 27" não está confirmado com
  certeza (ver `docs/04-fontes/bcb.md`). Por isso o script coleta as três como séries
  RAW separadas, sem escolher entre elas — essa escolha é trabalho de STAGING, não de
  RAW.
- **Passo a passo**: para cada um dos 3 códigos (`SERIES`), busca os dados na API e grava
  um arquivo JSON separado em `data/raw/bcb_sgs/` (nome com o código da série e um
  timestamp UTC compartilhado pelas três coletas); registra cada arquivo no Supabase.

### `coleta_endividamento_peic_fecomercio.py` — Endividamento das famílias (PEIC/FecomercioSP)

- **O que mede**: percentual de famílias endividadas e inadimplentes, segundo a Pesquisa
  de Endividamento e Inadimplência do Consumidor (PEIC) — a série histórica mensal
  completa desde fevereiro/2004, publicada como parte de um workbook Excel.
- **De onde vem**: FecomercioSP (Federação do Comércio de Bens, Serviços e Turismo do
  Estado de São Paulo), entidade privada. É a segunda parte do indicador "endividamento
  familiar" do material do DIEESE.
- **Por que este método**: a FecomercioSP não publica API de dados nem link fixo para o
  arquivo — cada edição mensal é um Excel novo anexado ao site, que roda em WordPress.
  Em vez de raspar o HTML da página de estatísticas (frágil a qualquer mudança visual do
  site), o script usa a API REST nativa do WordPress (`wp-json/wp/v2/media`), que já
  existe em qualquer instalação padrão e lista os anexos de mídia publicados de forma
  estruturada, já ordenados por data — mais robusto do que interpretar HTML (ver
  `docs/04-fontes/fecomercio-peic.md`).
- **Passo a passo**: consulta a listagem de mídia filtrando por "PEIC" e identifica o
  arquivo `.xlsx` mais recente; baixa o conteúdo desse arquivo; grava o conteúdo, sem
  abrir nem alterar, em `data/raw/fecomercio_peic/` (nome original prefixado por um
  timestamp UTC da coleta); registra o arquivo no Supabase.

### `coleta_saldo_credito_sfn_bcb.py` — Saldo de crédito do Sistema Financeiro Nacional

- **O que mede**: o saldo da carteira de crédito do Sistema Financeiro Nacional, em seis
  recortes confirmados: total (SGS 20539), pessoas físicas (SGS 20541), pessoas
  jurídicas (SGS 20540), recursos livres (SGS 20542), recursos direcionados (SGS 20593)
  e recursos livres de pessoas físicas (SGS 20570).
- **De onde vem**: Banco Central do Brasil, SGS.
- **Por que este método**: mesma API pública do SGS. Existem outros recortes cruzados
  possíveis (ex. "PJ — recursos livres — total"), mas os códigos candidatos para eles não
  foram testados via API nesta rodada — por isso ficam de fora deste script até serem
  confirmados (ver `docs/04-fontes/bcb.md` para a lista completa dos candidatos não
  incluídos e o motivo).
- **Passo a passo**: para cada um dos 6 códigos (`SERIES`), busca os dados na API e grava
  um arquivo JSON separado em `data/raw/bcb_sgs/` (nome com o código da série e um
  timestamp UTC compartilhado pelas seis coletas); registra cada arquivo no Supabase.
