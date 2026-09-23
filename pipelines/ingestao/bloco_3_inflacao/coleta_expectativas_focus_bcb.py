"""Coleta bruta das expectativas de mercado (Boletim Focus) para IPCA e INPC via API
pública Olinda do BCB.

Piloto técnico controlado — ver docs/08-decisoes-adr/0002-expansao-piloto-por-blocos.md
Fonte confirmada em: docs/04-fontes/bcb.md (Sistema de Expectativas de Mercado) — Lote 05c.

===============================================================================
COMO FUNCIONA A API OLINDA (protocolo OData) — sistema diferente do SGS
===============================================================================
Os outros scripts do BCB neste piloto (`coleta_cambio_bcb.py`, `coleta_igpm_bcb.py`)
usam o SGS — cada indicador tem um código numérico fixo e uma URL simples de
consulta. O Sistema de Expectativas de Mercado (Boletim Focus) é um sistema
DIFERENTE, publicado no portal Olinda de Dados Abertos do BCB, que usa o
protocolo OData (um padrão de consulta a dados via parâmetros na própria URL,
usado por várias instituições, não só o BCB).

Em vez de um código de série, a API Olinda tem um ENDPOINT fixo por conjunto de
dados (aqui, `ExpectativaMercadoMensais` — expectativas de indicadores mensais)
e os filtros são passados como parâmetros de query no padrão OData:

  - `$filter` → filtra as linhas, no formato `Campo eq 'Valor'` (aqui,
                `Indicador eq 'IPCA'` ou `Indicador eq 'INPC'`). É o
                equivalente a um `WHERE` de SQL.
  - `$format` → formato da resposta (`json`, o mesmo usado nos demais
                scripts deste piloto).

Como esses parâmetros contêm caracteres especiais (aspas, espaços, o sinal
`$`), a URL não pode ser montada por simples concatenação de texto — por isso
este script usa `urllib.parse.urlencode` para codificá-los corretamente (ver
`_url` abaixo). Esse é o padrão geral para montar qualquer URL com parâmetros
de query: nunca colar valores direto na string, sempre codificar.

A resposta trata os registros dentro de uma chave `"value"` (padrão OData),
diferente tanto do SIDRA (lista com item de cabeçalho) quanto do SGS (lista
simples de `{"data": ..., "valor": ...}`) — por isso este script grava a
resposta exatamente como veio, sem tentar unificar o formato com os outros.

===============================================================================
O QUE É ESTE DADO, E PARA QUE O DIEESE USA
===============================================================================
"Expectativas de mercado" é a pesquisa diária do BCB junto a instituições
financeiras sobre suas projeções futuras para indicadores econômicos — aqui,
IPCA e INPC. Cada registro traz, para um indicador e um mês de referência
futuro, estatísticas como média, mediana, desvio-padrão, mínimo, máximo e
número de respondentes das projeções coletadas naquele dia.

O material do DIEESE usa este dado como INSUMO para suas próprias estimativas
(nowcasting) de INPC/IPCA — ou seja, este script coleta a expectativa de
mercado bruta (o que instituições financeiras projetam), não a estimativa
que o próprio DIEESE produz a partir dela. Calcular ou combinar esse insumo
em uma estimativa é trabalho de camadas posteriores (STAGING/ANALYTICS), não
deste script.

===============================================================================
O QUE ESTE SCRIPT FAZ, PASSO A PASSO
===============================================================================
1. Para cada indicador em `INDICADORES` (IPCA, INPC), monta a URL da consulta
   com os parâmetros OData (`_url`).
2. Busca os dados na API (`_buscar_dados`).
3. Salva a resposta de cada indicador num arquivo separado em
   `data/raw/bcb_focus/` (`_salvar_raw`).
4. Registra cada arquivo no Supabase — Storage + linha em `raw_ingestoes`
   (`registrar_coleta`, importado de `pipelines/supabase_raw.py`).

Este script NÃO transforma o dado — grava a resposta bruta da API exatamente
como recebida, respeitando o princípio de que a camada RAW nunca deve ser
editada manualmente ou pré-processada (ver CLAUDE.md, seção DADOS).
"""

import json
import sys
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from supabase_raw import registrar_coleta

# Endpoint fixo do conjunto "Expectativas de Mercado Mensais" no portal Olinda.
BASE = "https://olinda.bcb.gov.br/olinda/servico/Expectativas/versao/v1/odata/ExpectativaMercadoMensais"
# Indicadores coletados — os dois usados pelo DIEESE como insumo de nowcasting.
INDICADORES = ["IPCA", "INPC"]

DESTINO = Path(__file__).resolve().parents[3] / "data" / "raw" / "bcb_focus"


# ------------------------------------------------------------------------
# PASSO 1 — montar a URL de consulta (protocolo OData) para um indicador
# ------------------------------------------------------------------------
def _url(indicador: str) -> str:
    """Monta a URL do endpoint com os parâmetros OData `$filter` e `$format`
    codificados via `urllib.parse.urlencode` — necessário porque o filtro
    (`Indicador eq 'IPCA'`) contém espaços e aspas, que não podem ir direto
    numa URL sem codificação.
    """
    params = {"$filter": f"Indicador eq '{indicador}'", "$format": "json"}
    return BASE + "?" + urllib.parse.urlencode(params, quote_via=urllib.parse.quote)


# ------------------------------------------------------------------------
# PASSO 2 — buscar os dados de um indicador na API
# ------------------------------------------------------------------------
def _buscar_dados(indicador: str) -> dict:
    """Faz a requisição HTTP para o indicador dado e devolve o JSON já
    decodificado. Envia um `User-Agent` porque este endpoint, diferente do
    SGS, pode rejeitar requisições sem cabeçalho de cliente identificado.
    `timeout=60` evita que o script fique parado indefinidamente se a API
    não responder.
    """
    req = urllib.request.Request(_url(indicador), headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=60) as resposta:
        return json.loads(resposta.read().decode("utf-8"))


# ------------------------------------------------------------------------
# PASSO 3 — salvar a resposta bruta de um indicador em disco
# ------------------------------------------------------------------------
def _salvar_raw(indicador: str, dados: dict, timestamp: str) -> Path:
    """Grava a resposta do indicador como JSON formatado (indent=2), só
    para leitura humana — não é transformação de dado. O nome do arquivo
    leva o indicador (para diferenciar IPCA de INPC) e um timestamp UTC,
    porque a expectativa de mercado é publicada diariamente e cada execução
    deste script é uma nova "fotografia" — nunca sobrescrevemos a coleta
    anterior.
    """
    arquivo = DESTINO / f"expectativas_{indicador.lower()}_{timestamp}.json"
    arquivo.write_text(json.dumps(dados, ensure_ascii=False, indent=2), encoding="utf-8")
    return arquivo


# ------------------------------------------------------------------------
# Orquestração: repete os passos acima para cada indicador de INDICADORES
# ------------------------------------------------------------------------
def coletar() -> list[Path]:
    DESTINO.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

    arquivos = []
    for indicador in INDICADORES:
        dados = _buscar_dados(indicador)
        arquivos.append(_salvar_raw(indicador, dados, timestamp))
    return arquivos


if __name__ == "__main__":
    for caminho in coletar():
        print(f"Coleta concluída: {caminho}")
        registrar_coleta(fonte=DESTINO.name, arquivo=caminho, script=__file__)
