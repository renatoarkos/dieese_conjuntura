"""Coleta bruta do índice/variação da produção física industrial (PIM-PF — Pesquisa
Industrial Mensal) via API pública do SIDRA/IBGE.

Piloto técnico controlado — ver docs/08-decisoes-adr/0002-expansao-piloto-por-blocos.md
Fonte confirmada em: docs/04-fontes/ibge-sidra.md (Tabela SIDRA 8888) — Lote 05c.

Completa, junto com PMC (comércio, já coletado) e PMS (serviços), o trio de pesquisas
mensais de atividade citado pelo material do DIEESE sob o rótulo único "PMC/PMS/PIM".

Este script NÃO transforma o dado.
"""

import json
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

URL = "https://apisidra.ibge.gov.br/values/t/8888/n1/all/v/11604/p/all/c544/129314"
DESTINO = Path(__file__).resolve().parents[3] / "data" / "raw" / "ibge_sidra"


def coletar() -> Path:
    DESTINO.mkdir(parents=True, exist_ok=True)
    with urllib.request.urlopen(URL, timeout=60) as resposta:
        dados = json.loads(resposta.read().decode("utf-8"))

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    arquivo = DESTINO / f"pim_industria_sidra_8888_{timestamp}.json"
    arquivo.write_text(json.dumps(dados, ensure_ascii=False, indent=2), encoding="utf-8")
    return arquivo


if __name__ == "__main__":
    caminho = coletar()
    print(f"Coleta concluída: {caminho}")
