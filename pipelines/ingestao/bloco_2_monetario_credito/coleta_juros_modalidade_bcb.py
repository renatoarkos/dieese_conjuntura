"""Coleta bruta das taxas médias de juros por modalidade de crédito (recursos
livres, pessoas físicas e jurídicas) via API pública do BCB/SGS.

Piloto técnico controlado — ver docs/08-decisoes-adr/0002-expansao-piloto-por-blocos.md
Fonte confirmada em: docs/04-fontes/bcb.md — os 4 códigos já eram citados célula a
célula no material interno do DIEESE (aba T16), e foram confirmados por chamada
real de API em 2026-09-22.

===============================================================================
COMO FUNCIONA A API DO BCB/SGS (vale para todos os scripts "..._bcb.py" que
usam o Sistema Gerenciador de Séries Temporais — SGS)
===============================================================================
O SGS é o sistema de séries temporais do Banco Central. Cada série (aqui, uma
modalidade específica de crédito) tem um CÓDIGO NUMÉRICO fixo, e a URL de
consulta é sempre:

    https://api.bcb.gov.br/dados/serie/bcdata.sgs.{codigo}/dados?formato=json

A resposta é uma lista de objetos `{"data": "DD/MM/AAAA", "valor": "..."}`, um
por observação, em ordem cronológica, sem cabeçalho.

===============================================================================
O QUE CADA SÉRIE MEDE
===============================================================================
As 4 séries abaixo são taxas médias de juros (% a.a., mensais) cobradas em
operações de crédito com recursos livres — ou seja, linhas cujo custo e
condições o próprio banco define livremente, ao contrário do crédito
direcionado (habitação, rural), que segue regras específicas:
  - 20728: Pessoas jurídicas — Aquisição de veículos.
  - 22019: Pessoas jurídicas — Cartão de crédito rotativo.
  - 20741: Pessoas físicas — Cheque especial.
  - 20742: Pessoas físicas — Crédito pessoal não consignado.

===============================================================================
O QUE ESTE SCRIPT FAZ, PASSO A PASSO
===============================================================================
1. Para cada série em `SERIES` (código → URL), busca os dados na API
   (`_buscar_dados`).
2. Salva cada série num arquivo separado em `data/raw/bcb_sgs/`, com o código
   da série e um timestamp da coleta no nome (`_salvar_raw`).
3. Registra cada arquivo no Supabase (Storage + `raw_ingestoes`).

Este script NÃO transforma o dado — grava cada série SGS separadamente, sem
nenhuma consolidação ou cálculo entre modalidades.
"""

import json
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from supabase_raw import registrar_coleta

# codigo da série SGS -> URL de consulta. Ver docs/04-fontes/bcb.md para o
# nome oficial completo de cada série.
SERIES = {
    "20728": "https://api.bcb.gov.br/dados/serie/bcdata.sgs.20728/dados?formato=json",  # PJ - Aquisição de veículos
    "22019": "https://api.bcb.gov.br/dados/serie/bcdata.sgs.22019/dados?formato=json",  # PJ - Cartão de crédito rotativo
    "20741": "https://api.bcb.gov.br/dados/serie/bcdata.sgs.20741/dados?formato=json",  # PF - Cheque especial
    "20742": "https://api.bcb.gov.br/dados/serie/bcdata.sgs.20742/dados?formato=json",  # PF - Crédito pessoal não consignado
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
    (para diferenciar as 4 modalidades) e um timestamp UTC da coleta, porque
    o BCB pode revisar valores publicados e cada execução é uma nova
    fotografia da série — nunca sobrescrevemos a coleta anterior.
    """
    arquivo = DESTINO / f"juros_modalidade_sgs_{codigo}_{timestamp}.json"
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
