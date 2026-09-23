"""Coleta bruta do Índice de Commodities Brasil (IC-Br) via API pública do
BCB/SGS.

Piloto técnico controlado — ver docs/08-decisoes-adr/0002-expansao-piloto-por-blocos.md
Fonte confirmada em: docs/05-indicadores/CATALOGO_MESTRE_INDICADORES.md (indicador novo,
achado em investigação de completude da planilha do DIEESE, 2026-09-23)

===============================================================================
O QUE ESTE INDICADOR MEDE, E COMO FOI ENCONTRADO
===============================================================================
O IC-Br é um índice calculado pelo próprio BCB (Departamento Econômico —
Depec) que acompanha o preço, em reais, de uma cesta de commodities
relevantes para a economia brasileira, dividido em três subíndices: preços
agropecuários, metálicos e energéticos, mais o índice geral. Base 100 =
média de 2006.

Este indicador não estava em nenhum dos 33 indicadores do catálogo P1
original — foi encontrado ao abrir um arquivo da própria planilha de dados do
DIEESE (`materiais/originais/.../Índice de Commodities .xlsx`), cuja última
linha de dados trazia explicitamente "Fonte: BCB-Depec" e os códigos de série
originais (27574-27577), que bateram exatamente com séries reais do SGS.

===============================================================================
COMO FUNCIONA A API DO BCB/SGS (mesmo padrão dos demais scripts "..._bcb.py")
===============================================================================
Ver `coleta_cambio_bcb.py` para a explicação completa do protocolo SGS. Aqui,
4 séries relacionadas (o índice geral e seus 3 subíndices) são coletadas
juntas, no mesmo padrão de `SERIES = {código: url}` já usado nos outros
scripts deste piloto que trazem mais de uma série por vez.

===============================================================================
O QUE ESTE SCRIPT FAZ, PASSO A PASSO
===============================================================================
1. Para cada série em `SERIES` (código → URL), busca os dados na API
   (`_buscar_dados`).
2. Salva cada série num arquivo separado em `data/raw/bcb_sgs/`
   (`_salvar_raw`).
3. Registra cada arquivo no Supabase.

Este script NÃO transforma o dado.
"""

import json
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from supabase_raw import registrar_coleta

# código da série SGS -> URL de consulta. As 4 séries do Índice de
# Commodities Brasil (IC-Br), confirmadas em planilha do DIEESE e testadas
# diretamente na API — todas com dado real até ago/2026 no teste.
SERIES = {
    "27574": "https://api.bcb.gov.br/dados/serie/bcdata.sgs.27574/dados?formato=json",  # IC-Br geral
    "27575": "https://api.bcb.gov.br/dados/serie/bcdata.sgs.27575/dados?formato=json",  # IC-Br Agropecuária
    "27576": "https://api.bcb.gov.br/dados/serie/bcdata.sgs.27576/dados?formato=json",  # IC-Br Metal
    "27577": "https://api.bcb.gov.br/dados/serie/bcdata.sgs.27577/dados?formato=json",  # IC-Br Energia
}

DESTINO = Path(__file__).resolve().parents[3] / "data" / "raw" / "bcb_sgs"


# ------------------------------------------------------------------------
# PASSO 1 — buscar uma série na API
# ------------------------------------------------------------------------
def _buscar_dados(url: str) -> list:
    with urllib.request.urlopen(url, timeout=60) as resposta:
        return json.loads(resposta.read().decode("utf-8"))


# ------------------------------------------------------------------------
# PASSO 2 — salvar a resposta bruta de uma série em disco
# ------------------------------------------------------------------------
def _salvar_raw(codigo: str, dados: list, timestamp: str) -> Path:
    arquivo = DESTINO / f"commodities_sgs_{codigo}_{timestamp}.json"
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
