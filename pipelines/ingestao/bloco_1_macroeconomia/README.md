# Bloco 1 — Macroeconomia

Este bloco reúne os scripts de coleta bruta (camada RAW, ver `CLAUDE.md` na raiz do
repositório) dos indicadores macroeconômicos que formam o pano de fundo da conjuntura:
o tamanho e o ritmo da economia (PIB doméstico e mundial), o preço da moeda (câmbio), o
volume de atividade nos três setores que mais pesam no PIB brasileiro (comércio,
serviços e indústria), quanto da capacidade produtiva instalada está sendo usada
(indústria), o resultado das trocas do país com o exterior (balança comercial), o
espaço fiscal dos estados para gastar com pessoal (limite fiscal por UF), o preço das
commodities relevantes para a economia brasileira, e a proporção do PIB destinada a
investimento produtivo (taxa de investimento). São onze indicadores de seis fontes
oficiais diferentes — IBGE, Banco Central, FMI, CNI, MDIC e Tesouro Nacional — que
juntos respondem à pergunta "como vai a economia agora", antes de qualquer recorte de
mercado de trabalho, preços ou renda, que ficam em outros blocos.

Cada script é independente, autoexecutável e não depende de nenhum outro script deste
bloco para rodar. Nenhum deles transforma dado: cada um busca a resposta de uma fonte
pública e grava exatamente o que recebeu em `data/raw/`, sem calcular, filtrar,
converter ou "limpar" nada — essa é a regra da camada RAW (ver `CLAUDE.md`, seção
DADOS). Todos são Python puro, sem dependências externas (ver
`docs/08-decisoes-adr/0001-stack-minima-piloto-ingestao.md`).

## Como rodar

Cada script roda isoladamente, a partir da raiz do repositório:

```bash
python3 pipelines/ingestao/bloco_1_macroeconomia/coleta_pib_sidra.py
```

Ao final, o script imprime o caminho do(s) arquivo(s) gravado(s) em `data/raw/` e tenta
registrar a coleta no Supabase (upload do arquivo + linha de log em `raw_ingestoes`,
função `registrar_coleta` de `pipelines/supabase_raw.py`) — se as credenciais do
Supabase não estiverem configuradas em `.env`, essa etapa é apenas ignorada, sem
interromper a coleta.

## Os 11 scripts

### `coleta_pib_sidra.py` — PIB Brasil

- **O que mede**: variação real (volume, sem efeito-preço) do PIB trimestral do Brasil —
  trimestre ante mesmo trimestre do ano anterior, acumulado em 4 trimestres, acumulado
  no ano e trimestre ante trimestre anterior com ajuste sazonal.
- **De onde vem**: IBGE, Sistema de Contas Nacionais Trimestrais, tabela SIDRA 5932.
- **Por que este método**: a API pública do SIDRA (`apisidra.ibge.gov.br`) responde
  diretamente em JSON, sem chave nem autenticação — é a via confirmada e testada; o
  acesso às páginas HTML institucionais do IBGE, em contraste, retorna bloqueio HTTP 403
  para requisições automatizadas (ver `docs/04-fontes/ibge-sidra.md`).
- **Passo a passo**: monta a URL fixa da tabela 5932 (todos os territórios, todas as
  variáveis, todos os períodos, classificação 90707); busca os dados; grava a lista
  JSON inteira (cabeçalho + valores) em `data/raw/ibge_sidra/`, com o número da tabela e
  um timestamp UTC no nome do arquivo; registra a coleta no Supabase.

### `coleta_cambio_bcb.py` — Câmbio (dólar, venda)

- **O que mede**: a cotação de venda do dólar americano no câmbio livre — duas séries
  candidatas coletadas em paralelo (SGS 3694, média anual; SGS 3698, média mensal),
  porque o material do DIEESE cita "câmbio" sem deixar claro qual delas usa.
- **De onde vem**: Banco Central do Brasil, Sistema Gerenciador de Séries Temporais
  (SGS).
- **Por que este método**: a API do SGS (`api.bcb.gov.br/dados/serie/...`) é pública,
  sem autenticação, e devolve diretamente a lista de observações em JSON — via
  confirmada em `docs/04-fontes/bcb.md`. Como não foi possível confirmar, nesta rodada,
  qual das duas séries (ou se as duas) o DIEESE usa, o script coleta ambas em vez de
  escolher por conta própria — decidir entre elas é trabalho de STAGING, não de RAW.
- **Passo a passo**: para cada código de série em `SERIES`, busca os dados na API e
  grava um arquivo JSON separado em `data/raw/bcb_sgs/` (nome com o código da série e um
  timestamp UTC compartilhado pelas duas coletas); registra cada arquivo no Supabase.

### `coleta_pmc_comercio_sidra.py` — Comércio varejista (PMC)

- **O que mede**: índice e variação da receita nominal e do volume de vendas no
  comércio varejista ampliado (base 2022=100).
- **De onde vem**: IBGE, Pesquisa Mensal de Comércio (PMC), tabela SIDRA 8881.
- **Por que este método**: mesma API SIDRA do PIB — acesso direto, sem autenticação,
  confirmado por teste real.
- **Achado relevante**: o material do DIEESE cita este indicador com o rótulo único
  "comércio/serviços/indústria (PMC/PMS/PIM)", mas a tabela 8881 cobre apenas a parcela
  comércio — por isso este script coleta só PMC, e existem dois scripts irmãos para
  completar o trio (ver PMS e PIM abaixo).
- **Passo a passo**: monta a URL da tabela 8881 (todos os territórios, todas as
  variáveis, todos os períodos, classificação "Tipos de índice" completa); busca os
  dados; grava o JSON em `data/raw/ibge_sidra/` com timestamp; registra no Supabase.

### `coleta_pms_servicos_sidra.py` — Serviços (PMS)

- **O que mede**: índice e variação do volume de serviços (base 2022=100).
- **De onde vem**: IBGE, Pesquisa Mensal de Serviços (PMS), tabela SIDRA 5906 (a tabela
  vigente — as antecessoras 6442/6443/6444/8161-8164 estão marcadas como série
  encerrada).
- **Por que este método**: mesma API SIDRA, agora pedindo uma variável específica
  (11626, "PMS - Variação acumulada em 12 meses") em vez de todas — escolha confirmada
  em `docs/04-fontes/ibge-sidra.md`.
- **Passo a passo**: monta a URL da tabela 5906 filtrada pela variável 11626 e pela
  categoria 56726 ("Índice de volume de serviços") da classificação 11046; busca os
  dados; grava o JSON em `data/raw/ibge_sidra/` com timestamp; registra no Supabase.
  Completa, junto com PMC e PIM, o trio "PMC/PMS/PIM" citado pelo DIEESE.

### `coleta_pim_industria_sidra.py` — Indústria (PIM-PF)

- **O que mede**: produção física industrial (índice geral, sem recorte setorial).
- **De onde vem**: IBGE, Pesquisa Industrial Mensal - Produção Física (PIM-PF), tabela
  SIDRA 8888 (a tabela vigente — as antecessoras 3653/6663/7511.../8159 estão marcadas
  como série encerrada).
- **Por que este método**: mesma API SIDRA, variável 11604 ("PIMPF - Variação acumulada
  em 12 meses") e classificação 544, categoria 129314 ("Indústria geral").
- **Passo a passo**: monta a URL da tabela 8888 filtrada por essa variável e categoria;
  busca os dados; grava o JSON em `data/raw/ibge_sidra/` com timestamp; registra no
  Supabase. Fecha, junto com PMC e PMS, o trio "PMC/PMS/PIM".

### `coleta_pib_mundial_fmi.py` — PIB Mundial

- **O que mede**: variação real do PIB (% a.a.), por país/agregado — indicador
  `NGDP_RPCH` do WEO.
- **De onde vem**: Fundo Monetário Internacional (FMI), base de dados World Economic
  Outlook (WEO).
- **Por que este método**: API pública SDMX 3.0 do FMI (`api.imf.org`), padrão usado por
  vários organismos estatísticos internacionais, sem chave nem autenticação — via
  confirmada em `docs/04-fontes/fmi-cni.md`.
- **Limitação conhecida**: os códigos de país do dataflow WEO não são ISO3 simples
  (testar "BRA" diretamente não retorna nada); em vez de adivinhar um código não
  confirmado, o script consulta com curinga `*` (todos os países/agregados) e deixa
  qualquer filtro por país para a camada STAGING.
- **Passo a passo**: monta a URL do dataflow WEO filtrado pelo indicador NGDP_RPCH,
  frequência anual, todos os países, período 2016-2030; busca os dados pedindo
  explicitamente resposta em JSON; grava a estrutura SDMX bruta em `data/raw/fmi_weo/`
  com timestamp; registra no Supabase.

### `coleta_uci_cni.py` — Utilização da Capacidade Instalada (UCI)

- **O que mede**: Utilização da Capacidade Instalada na Indústria de Transformação.
- **De onde vem**: Confederação Nacional da Indústria (CNI), levantamento "Indicadores
  Industriais" — **não** o ICEI (Índice de Confiança do Empresário Industrial), como o
  material do DIEESE cita; são dois levantamentos distintos da CNI (ver
  `docs/04-fontes/fmi-cni.md`).
- **Por que este método**: a CNI não expõe API nem link fixo — o arquivo Excel da Série
  Histórica muda de nome a cada divulgação mensal (ex. "..._julho2026.xlsx"). O script
  faz uma raspagem mínima e direcionada: baixa o HTML da página oficial de estatísticas
  e usa uma expressão regular para localizar a URL do Excel vigente, em vez de fazer o
  parsing da estrutura da página (mais frágil a mudanças de layout).
- **Passo a passo**: baixa o HTML da página; aplica a regex e pega a primeira URL
  encontrada (ordenada, para ser determinística); baixa o conteúdo binário desse Excel;
  grava o arquivo em `data/raw/cni/`, mantendo o nome original prefixado por um
  timestamp; registra no Supabase. Se a regex não encontrar nenhum link, o script falha
  explicitamente (sinal de que a página mudou de padrão), em vez de seguir adiante.

### `coleta_balanca_comercial_comexstat.py` — Balança comercial

- **O que mede**: exportações e importações brasileiras por NCM, do ano corrente.
- **De onde vem**: MDIC (Ministério do Desenvolvimento, Indústria, Comércio e
  Serviços), plataforma Comex Stat — dados brutos em CSV, um arquivo por fluxo
  (exportação/importação).
- **Por que este método**: os arquivos CSV são grandes (~70-120 MB) e o servidor
  `balanca.mdic.gov.br` envia uma cadeia de certificado TLS incompleta, que o módulo
  `ssl` do Python rejeita mesmo com `certifi` (`CERTIFICATE_VERIFY_FAILED`) — um
  problema confirmado do lado do servidor do MDIC, não uma vulnerabilidade a contornar.
  O `curl` do sistema resolve essa cadeia corretamente, por isso o script chama `curl`
  via `subprocess` em vez de `urllib` (única exceção à stack mínima baseada em
  `urllib` usada no resto do piloto). Além disso, o servidor reseta a conexão em pontos
  aleatórios de downloads grandes — por isso o script usa `curl -C -` (retomada a partir
  do byte já baixado) dentro de um laço de até 60 tentativas, em vez de reiniciar o
  download do zero a cada queda.
- **Escopo**: coleta apenas o ano corrente — um backfill do histórico completo (desde
  1997) é uma decisão de maior porte, deixada para expansão futura deliberada.
- **Passo a passo**: monta as URLs de exportação e importação do ano corrente; baixa
  cada CSV com a lógica de retomada, escrevendo direto em `data/raw/comexstat/` (sem
  manter o arquivo inteiro em memória); registra cada arquivo no Supabase.

### `coleta_limite_fiscal_siconfi.py` — Limite fiscal por UF

- **O que mede**: despesa com pessoal do Poder Executivo estadual e os limites da Lei de
  Responsabilidade Fiscal (limite máximo e limite prudencial = 0,95×máximo), por Unidade
  da Federação.
- **De onde vem**: Secretaria do Tesouro Nacional, SICONFI (Sistema de Informações
  Contábeis e Fiscais do Setor Público Brasileiro), Relatório de Gestão Fiscal (RGF).
- **Por que este método**: API REST pública construída sobre Oracle ORDS
  (`apidatalake.tesouro.gov.br/ords/siconfi/...`), sem chave nem autenticação — via
  confirmada e testada em `docs/04-fontes/mdic-tesouro.md`. A API devolve dados de um
  único ente por chamada (não existe parâmetro "todas as UFs de uma vez"), por isso o
  script itera sobre as 27 Unidades da Federação e faz uma requisição por UF.
- **Passo a passo**: para cada uma das 27 UFs (dicionário `CODIGOS_UF`, código IBGE),
  monta a URL do RGF para o exercício/quadrimestre configurado (`AN_EXERCICIO`,
  `NR_PERIODO`), busca os dados e grava um arquivo JSON próprio dessa UF em
  `data/raw/siconfi/`, todos com o mesmo timestamp de rodada; registra cada um dos 27
  arquivos no Supabase.

### `coleta_commodities_bcb.py` — Índice de Commodities Brasil (IC-Br)

- **O que mede**: preço, em reais, de uma cesta de commodities relevantes para a
  economia brasileira — índice geral e 3 subíndices (agropecuária, metal, energia).
- **De onde vem**: Banco Central do Brasil, Departamento Econômico (BCB/Depec), via SGS
  — códigos 27574 (geral), 27575, 27576, 27577.
- **Como foi achado**: **não estava em nenhum dos 33 indicadores do catálogo P1
  original** — apareceu ao abrir a própria planilha de dados do DIEESE
  (`materiais/originais/.../Índice de Commodities .xlsx`, achada numa investigação de
  completude em 2026-09-23), cujo rodapé citava "Fonte: BCB-Depec" e os códigos de série
  exatos — confirmados por teste real na API antes de escrever o script.
- **Por que este método**: mesmo padrão SGS já usado por `coleta_cambio_bcb.py` e outros
  scripts BCB deste piloto — 4 séries relacionadas coletadas juntas.
- **Passo a passo**: para cada código de série em `SERIES`, busca os dados na API e
  grava um arquivo JSON separado em `data/raw/bcb_sgs/`; registra cada arquivo no
  Supabase.

### `coleta_taxa_investimento_sidra.py` — Taxa de investimento (FBCF/PIB)

- **O que mede**: proporção do PIB destinada a investimento produtivo (Formação Bruta de
  Capital Fixo — máquinas, equipamentos, construção), já calculada pelo IBGE.
- **De onde vem**: IBGE, Contas Nacionais Trimestrais, tabela SIDRA 6727.
- **Como foi achado**: mesma investigação de completude — arquivo
  `materiais/originais/.../taxa_invest.xlsx` do próprio DIEESE, cujo título ("Tabela 6727
  - Taxa de investimento") apontou direto para a tabela SIDRA correspondente.
- **Revisão observada**: entre duas cópias da planilha do DIEESE (nov/2024 e dez/2024), o
  mesmo trimestre (2º tri/2024) mudou de 16,8% para 16,6% — revisão típica do IBGE entre
  divulgações; o script sempre grava com timestamp, nunca sobrescreve.
- **Passo a passo**: monta a URL fixa da tabela 6727 (todos os territórios, todas as
  variáveis, todos os períodos — sem precisar de classificação, a tabela só tem uma
  variável); busca os dados; grava o JSON em `data/raw/ibge_sidra/` com timestamp;
  registra no Supabase.
