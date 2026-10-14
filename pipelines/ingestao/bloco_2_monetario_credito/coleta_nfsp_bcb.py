"""Coleta bruta da NFSP — Necessidade de Financiamento do Setor Público (fluxo
acumulado em 12 meses, juros nominais, setor público consolidado, % do PIB)
via API pública do BCB/SGS.

Piloto técnico controlado — ver docs/08-decisoes-adr/0002-expansao-piloto-por-blocos.md
Fonte confirmada em: docs/04-fontes/bcb.md.

===============================================================================
QF07 RESOLVIDA (2026-10-14)
===============================================================================
O código citado pelo material original do DIEESE (5474) não está catalogado
oficialmente pelo BCB. Duas séries candidatas existiam: SGS 5760 ("setor
público consolidado") e SGS 5750 ("Governo Federal e Banco Central", escopo
mais restrito). Resolvida por leitura direta da aba `T17` da planilha interna
mais recente do DIEESE (leitura somente-leitura de `materiais/originais/dieese/`):
o próprio cabeçalho da série já está rotulado "5760" (não mais 5474) — o
DIEESE já migrou internamente para essa série. Confirmado também por
comparação direta de 14 valores mensais (mar/2025 a abr/2026): 12 exatos, 3
mais recentes com diferença de 0,01-0,03 p.p. (revisão normal de dado
preliminar, não divergência de série).

===============================================================================
COMO FUNCIONA A API DO BCB/SGS (vale para todos os scripts "..._bcb.py" que
usam o Sistema Gerenciador de Séries Temporais — SGS)
===============================================================================
O SGS é o sistema de séries temporais do Banco Central. A URL de consulta é
sempre:

    https://api.bcb.gov.br/dados/serie/bcdata.sgs.{codigo}/dados?formato=json

A resposta é uma lista de objetos `{"data": "DD/MM/AAAA", "valor": "..."}`, um
por observação, em ordem cronológica, sem cabeçalho.

===============================================================================
O QUE ESTE SCRIPT FAZ, PASSO A PASSO
===============================================================================
1. Busca a série 5760 na API (`_buscar_dados`).
2. Salva o resultado em `data/raw/bcb_sgs/` com timestamp da coleta
   (`_salvar_raw`).
3. Registra o arquivo no Supabase (Storage + `raw_ingestoes`).

Este script NÃO transforma o dado.
"""

import json
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from supabase_raw import registrar_coleta

CODIGO = "5760"
URL = f"https://api.bcb.gov.br/dados/serie/bcdata.sgs.{CODIGO}/dados?formato=json"

DESTINO = Path(__file__).resolve().parents[3] / "data" / "raw" / "bcb_sgs"


def _buscar_dados() -> list:
    with urllib.request.urlopen(URL, timeout=60) as resposta:
        return json.loads(resposta.read().decode("utf-8"))


def _salvar_raw(dados: list, timestamp: str) -> Path:
    arquivo = DESTINO / f"nfsp_sgs_{CODIGO}_{timestamp}.json"
    arquivo.write_text(json.dumps(dados, ensure_ascii=False, indent=2), encoding="utf-8")
    return arquivo


def coletar() -> Path:
    DESTINO.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    dados = _buscar_dados()
    return _salvar_raw(dados, timestamp)


if __name__ == "__main__":
    caminho = coletar()
    print(f"Coleta concluída: {caminho}")
    registrar_coleta(fonte=DESTINO.name, arquivo=caminho, script=__file__)
