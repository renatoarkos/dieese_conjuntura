# Bloco 5 — Novo CAGED (microdados)

Este bloco cobre os indicadores derivados do Novo CAGED (Cadastro Geral de
Empregados e Desempregados): salário médio de admissão/desligamento, e saldo
de admissões/desligamentos por grupamento de atividade econômica. É o único
bloco cuja fonte é **microdados** em vez de uma tabela já pronta — e por isso
funciona de um jeito diferente dos outros blocos.

## Por que microdados, e não uma API

O canal oficial de "tabelas prontas" do Novo CAGED — as que mais se
aproximariam das tabelas que o material do DIEESE usa — é hoje distribuído
numa pasta do Google Drive sem URL fixa, o que não dá para automatizar de
forma estável (ver `docs/04-fontes/mte-caged.md`). O que existe, de forma
pública, estável e sem necessidade de login, é o **FTP de microdados brutos**
(`ftp.mtps.gov.br`): um registro por admissão ou desligamento, não a tabela já
somada por mês/setor/UF.

Por isso este bloco coleta o microdado bruto (arquivos `.7z`), não o
indicador final. **Somar esses registros nas tabelas que o DIEESE usa é uma
transformação — pertence à camada STAGING, e ainda não está implementada.**
O que este script garante é que o dado bruto necessário para fazer essa
transformação, a qualquer momento, já esteja disponível localmente.

## Como rodar

```bash
# Coleta recorrente: só o mês mais recente (é o que roda toda semana, agendado)
python3 pipelines/ingestao/bloco_5_caged/coleta_caged_microdados_ftp.py

# Coleta histórica: um intervalo de meses, para montar uma série temporal local
python3 pipelines/ingestao/bloco_5_caged/coleta_caged_microdados_ftp.py --historico
python3 pipelines/ingestao/bloco_5_caged/coleta_caged_microdados_ftp.py --historico 202001 202412
```

## `coleta_caged_microdados_ftp.py` — passo a passo

O FTP organiza os arquivos em pastas `NOVO CAGED/{ano}/{ano}{mês}/`, cada uma
com até 3 arquivos `.7z`: `CAGEDMOV` (movimentações do mês — o maior, ~50 MB),
`CAGEDEXC` (exclusões/retificações de meses anteriores) e `CAGEDFOR` (dados
de admissões/desligamentos do setor rural — Lei 5.889). Nem todo mês tem os
3 arquivos.

O script tem duas funções de coleta, que compartilham a mesma lógica de
conexão e download:

1. **`coletar()`** — descobre o mês mais recente disponível e baixa os
   arquivos `.7z` dessa pasta. Cada execução grava um arquivo novo com
   timestamp no nome (`CAGEDMOV202607_20260923T...Z.7z`), porque o MTE às
   vezes republica o mesmo mês com pequenas correções nos dias seguintes à
   divulgação — queremos preservar esse histórico de revisões, não
   sobrescrever silenciosamente. É esta função que o workflow agendado chama.

2. **`coletar_periodo(mes_inicio, mes_fim)`** — baixa todos os meses de um
   intervalo. Diferente da anterior: o nome do arquivo NÃO leva timestamp (o
   mês já identifica o arquivo de forma única, ex. `CAGEDMOV202001.7z`), e um
   mês que já foi baixado localmente com o tamanho certo é pulado — por isso é
   seguro interromper essa coleta no meio (são ~4,2 GB no total, desde
   jan/2020) e rodar de novo depois sem perder o que já foi baixado nem
   duplicar arquivo.

Por baixo dos panos, as duas funções usam:

- **`_conectar()`** — abre a conexão FTP anônima. Usa `encoding = "latin-1"`
  porque o servidor devolve nomes de arquivo/pasta fora de UTF-8 puro — sem
  isso, listar os arquivos lança `UnicodeDecodeError`.
- **`_listar_meses_disponiveis(ftp)`** — navega pelas pastas de ano e devolve
  todos os meses publicados, em ordem.
- **`_baixar_com_retomada(ftp, nome_remoto, destino)`** — baixa um arquivo,
  retomando de onde parou se a conexão cair no meio (usa o comando FTP `REST`,
  o mesmo princípio de um "continuar download" de navegador). Isso existe
  porque o arquivo maior (`CAGEDMOV`) às vezes tem a transferência interrompida
  antes de completar — instabilidade de rede, não erro do servidor.

## Arquivos grandes e o Supabase Storage

Os arquivos `CAGEDMOV` (~45-57 MB) excedem o limite de 50 MB do plano atual
do Supabase Storage. `registrar_coleta()` (`pipelines/supabase_raw.py`)
detecta isso automaticamente e divide o arquivo em partes menores antes do
envio — sem precisar de nenhuma mudança neste script. Ver a seção
"Integração com Supabase" em `pipelines/README.md` para os detalhes de como
o particionamento e a reconstrução funcionam.

## O que ainda falta (camada STAGING, fora deste piloto)

- Descompactar os arquivos `.7z` e ler os registros (são arquivos de largura
  fixa/delimitados — o layout exato está documentado nos manuais do Novo
  CAGED, não neste repositório ainda).
- Agregar os registros nas tabelas que o DIEESE usa: salário médio de
  admissão/desligamento por mês; saldo de admissões/desligamentos por
  grupamento de atividade e nível geográfico.
- Ver `docs/04-fontes/mte-caged.md` (QF09) para as perguntas ainda abertas
  sobre como o DIEESE hoje obtém essas tabelas internamente.
