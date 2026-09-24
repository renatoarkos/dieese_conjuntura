# Fundamentos de APIs

## O que é uma API

API (Application Programming Interface) é, na prática deste projeto, um
endereço na internet que devolve dado bruto — não uma página bonita para
humanos lerem, mas texto estruturado (quase sempre JSON) para um programa
processar. Em vez de abrir o navegador, procurar uma tabela numa página e
copiar os números à mão, um script pede esse mesmo dado direto à fonte, pela
mesma porta que qualquer outro programa usaria.

Exemplo real deste projeto — pedir a série do PIB brasileiro ao IBGE:

```python
import urllib.request

url = "https://apisidra.ibge.gov.br/values/t/5932/n1/all/v/all/p/all/c11255/90707"
with urllib.request.urlopen(url, timeout=60) as resposta:
    dados = resposta.read()  # bytes crus, ainda não interpretados

print(dados[:200])
# b'[{"NC":"N\xc3\xadvel Territorial (C\xc3\xb3digo)","NN":"N\xc3\xadvel Territorial", ...'
```

Isso já é uma chamada de API completa — sem biblioteca nenhuma, só a
biblioteca padrão do Python (`urllib`). O resto deste documento explica cada
peça: por que essa URL tem esse formato, o que fazer com os `bytes` da
resposta, e as variações que aparecem em fontes diferentes.

## REST e a URL como "frase"

A grande maioria das APIs deste projeto (IBGE/SIDRA, Banco Central/SGS,
SICONFI, Banco Mundial...) segue o estilo **REST**: a própria URL descreve o
que você está pedindo, sem precisar de um corpo de requisição complexo. Dá
para ler a URL como uma frase:

```
https://apisidra.ibge.gov.br/values/t/5932/n1/all/v/all/p/all/c11255/90707
                              ^valores  ^tabela ^território ^variável ^período ^classificação
```

"Me dê os *valores* da *tabela* 5932, para *todos* os *territórios* de nível
1, *todas* as *variáveis*, *todos* os *períodos*, na *classificação*
90707." Cada API tem seu próprio vocabulário de segmentos — o padrão do
SIDRA (`t/.../n1/.../v/.../p/...`) é diferente do padrão do Banco Central
(`/dados/serie/bcdata.sgs.{código}/dados`), mas a ideia é a mesma: parâmetros
viram pedaços da própria URL.

**Onde aprender o vocabulário de uma API nova**: a documentação oficial da
fonte (quase sempre tem uma página "API" ou "dados abertos"), ou testando
com curinga (`all`, `*`) e vendo o que volta — foi assim que boa parte das
fontes deste projeto foi confirmada (ver
[`02-metodologia-de-investigacao.md`](02-metodologia-de-investigacao.md)).

## JSON — o formato mais comum de resposta

JSON (JavaScript Object Notation) é texto que representa listas e
dicionários — o mesmo tipo de estrutura que o Python já tem nativamente, por
isso `json.loads()` (da biblioteca padrão) converte a resposta direto em
listas/dicionários Python:

```python
import json

dados = json.loads(resposta_em_bytes.decode("utf-8"))
# agora "dados" é uma lista de dicionários, navegável normalmente:
print(dados[1]["V"])   # "3070"  (o campo "V" = Valor, no padrão SIDRA)
```

Cada fonte usa nomes de campo diferentes dentro do JSON (o SIDRA usa `V`,
`D1N`, `D2N`...; o SGS do BCB usa `data`/`valor`; o Banco Mundial usa outra
estrutura ainda) — por isso o primeiro passo ao investigar uma fonte nova é
sempre olhar um pedaço real da resposta, nunca supor o formato.

## Outros dois protocolos que este projeto já usa

**SDMX** (Statistical Data and Metadata eXchange) — um formato pensado
especificamente para estatística oficial, usado por organismos
internacionais (FMI, Banco Mundial em parte, OCDE, ILOSTAT, BIS, Eurostat —
ver `docs/04-fontes/outras-instituicoes-mundiais-2026-09.md`). A URL segue
um padrão de "dataflow" + "chave" (uma sequência de dimensões separadas por
ponto), e a resposta pode vir em JSON, XML ou CSV, dependendo do cabeçalho
`Accept` que o script manda:

```python
# exemplo real: coleta_pib_mundial_fmi.py
req = urllib.request.Request(url, headers={"Accept": "application/json"})
```

**OData** — usado pelo Banco Central em alguns sistemas (Focus/Expectativas,
SCR) além do SGS clássico. Os parâmetros de filtro vêm depois de um `?`, no
estilo `$filter=Indicador eq 'IPCA'`, e o script usa
`urllib.parse.urlencode()` para montar isso corretamente (ver
`coleta_expectativas_focus_bcb.py`).

## Autenticação e limites de uso

A maioria das fontes que este projeto usa **não exige nenhuma credencial** —
são dados públicos, de instituições que decidiram abrir o acesso. Mas
algumas exigem uma "chave de API" (uma senha de uso, geralmente gratuita,
obtida cadastrando uma conta). O padrão, quando isso acontece, é:

1. A API responde com um erro claro dizendo que falta a chave (nunca invente
   um formato — deixe a própria API dizer o que ela quer). Exemplo real,
   testado neste projeto (`docs/04-fontes/outras-instituicoes-mundiais-2026-09.md`,
   seção FRED):
   ```
   HTTP 400: "Variable api_key is not set. Read https://fred.stlouisfed.org/docs/api/api_key.html..."
   ```
2. Se o cadastro for gratuito e o caso de uso justificar, a chave fica
   guardada em `.env` (nunca no código, nunca versionada — ver
   `CLAUDE.md`, seção SEGURANÇA), do mesmo jeito que já é feito para o
   Supabase e o Google Drive neste projeto.

"Limite de uso" (rate limit) é o número de chamadas que uma API aceita num
intervalo de tempo antes de começar a recusar. A maioria das fontes públicas
deste projeto não tem limite agressivo para o volume que os motores fazem
(uma consulta por indicador, a cada poucas horas/dias) — mas é por isso que
o agendamento deste projeto (`docs/08-decisoes-adr/0003-agendamento-github-actions.md`)
prefere rodar com folga (ex. semanalmente para uma fonte mensal) em vez de
tentar acertar o dia exato de publicação.

## Próximo passo

[`02-metodologia-de-investigacao.md`](02-metodologia-de-investigacao.md) —
como decidir se uma fonte encontrada é confiável o suficiente para virar um
motor de coleta.
