"""Coleta bruta do saldo da carteira de crédito do Sistema Financeiro Nacional
— total e recortado por tomador (pessoas físicas/jurídicas) e tipo de recurso
(livre/direcionado) — via API pública do BCB/SGS.

Piloto técnico controlado — ver docs/08-decisoes-adr/0002-expansao-piloto-por-blocos.md
Fonte confirmada em: docs/04-fontes/bcb.md — Lote 06a.

===============================================================================
COMO FUNCIONA A API DO BCB/SGS (vale para todos os scripts "..._bcb.py" que
usam o Sistema Gerenciador de Séries Temporais — SGS)
===============================================================================
O SGS é o sistema de séries temporais do Banco Central. Cada série (aqui, um
recorte específico do saldo de crédito) tem um CÓDIGO NUMÉRICO fixo, e a URL
de consulta é sempre:

    https://api.bcb.gov.br/dados/serie/bcdata.sgs.{codigo}/dados?formato=json

A resposta é uma lista de objetos `{"data": "DD/MM/AAAA", "valor": "..."}`, um
por observação, em ordem cronológica, sem cabeçalho.

===============================================================================
O QUE CADA SÉRIE MEDE, E POR QUE SÓ ESTAS 6
===============================================================================
As 6 séries abaixo foram confirmadas por teste real da API (incluindo teste
específico no período de início do histórico citado pelo material do
DIEESE):
  - 20539: Total (pessoas físicas + jurídicas, recursos livres + direcionados).
  - 20541: Pessoas físicas — Total.
  - 20540: Pessoas jurídicas — Total.
  - 20542: Recursos livres — Total.
  - 20593: Recursos direcionados — Total.
  - 20570: Recursos livres — Pessoas físicas — Total.

Existem outros recortes cruzados possíveis (ex.: "PJ — recursos livres —
total", "PF — recursos direcionados — total"), mas os códigos candidatos para
eles NÃO foram testados via API nesta rodada — por isso ficam de fora deste
script até serem confirmados (ver docs/04-fontes/bcb.md para o detalhe de
quais candidatos existem e por que não entraram).

===============================================================================
O QUE ESTE SCRIPT FAZ, PASSO A PASSO
===============================================================================
1. Para cada série em `SERIES` (código → URL), busca os dados na API
   (`_buscar_dados`).
2. Salva cada série num arquivo separado em `data/raw/bcb_sgs/`, com o código
   da série e um timestamp da coleta no nome (`_salvar_raw`).
3. Registra cada arquivo no Supabase (Storage + `raw_ingestoes`).

Este script NÃO transforma o dado — grava cada série SGS separadamente, sem
somar ou comparar os recortes entre si.
"""

import json
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from supabase_raw import registrar_coleta

# codigo da série SGS -> URL de consulta. Ver docs/04-fontes/bcb.md para o
# nome oficial completo de cada série e a lista de recortes ainda não
# confirmados.
SERIES = {
    "20539": "https://api.bcb.gov.br/dados/serie/bcdata.sgs.20539/dados?formato=json",  # Total (PF+PJ, livres+direcionados)
    "20541": "https://api.bcb.gov.br/dados/serie/bcdata.sgs.20541/dados?formato=json",  # Pessoas físicas - Total
    "20540": "https://api.bcb.gov.br/dados/serie/bcdata.sgs.20540/dados?formato=json",  # Pessoas jurídicas - Total
    "20542": "https://api.bcb.gov.br/dados/serie/bcdata.sgs.20542/dados?formato=json",  # Recursos livres - Total
    "20593": "https://api.bcb.gov.br/dados/serie/bcdata.sgs.20593/dados?formato=json",  # Recursos direcionados - Total
    "20570": "https://api.bcb.gov.br/dados/serie/bcdata.sgs.20570/dados?formato=json",  # Recursos livres - Pessoas físicas - Total
}

DESTINO = Path(__file__).resolve().parents[3] / "data" / "raw" / "bcb_sgs"


# ------------------------------------------------------------------------
# PASSO 1 — buscar uma série na API
# ------------------------------------------------------------------------
def _buscar_dados(url: str) -> list:
    """Faz a requisição HTTP e devolve o JSON já decodificado. `timeout=60`
    evita que o script fique parado indefinidamente se a API do BCB não
    responder — nesse caso ele falha de forma visível (exceção), em vez de
    travar silenciosamente.
    """
    with urllib.request.urlopen(url, timeout=60) as resposta:
        return json.loads(resposta.read().decode("utf-8"))


# ------------------------------------------------------------------------
# PASSO 2 — salvar a resposta bruta de uma série em disco
# ------------------------------------------------------------------------
def _salvar_raw(codigo: str, dados: list, timestamp: str) -> Path:
    """Grava a série `codigo` como JSON formatado (só para leitura humana —
    não é transformação de dado). O nome do arquivo leva o código da série
    (para diferenciar os 6 recortes) e um timestamp UTC da coleta, porque o
    BCB pode revisar valores publicados e cada execução é uma nova
    fotografia da série — nunca sobrescrevemos a coleta anterior.
    """
    arquivo = DESTINO / f"saldo_credito_sfn_sgs_{codigo}_{timestamp}.json"
    arquivo.write_text(json.dumps(dados, ensure_ascii=False, indent=2), encoding="utf-8")
    return arquivo


# ------------------------------------------------------------------------
# Orquestração: repete os passos acima para cada série de SERIES
# ------------------------------------------------------------------------
def coletar() -> list[Path]:
    DESTINO.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

    arquivos = []
    for codigo, url in SERIES.items():
        dados = _buscar_dados(url)
        arquivos.append(_salvar_raw(codigo, dados, timestamp))
    return arquivos


if __name__ == "__main__":
    for caminho in coletar():
        print(f"Coleta concluída: {caminho}")
        registrar_coleta(fonte=DESTINO.name, arquivo=caminho, script=__file__)
