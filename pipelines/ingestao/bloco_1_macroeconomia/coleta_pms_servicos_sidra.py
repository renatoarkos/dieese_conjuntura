"""Coleta bruta do índice/variação do volume de serviços (PMS — Pesquisa Mensal de
Serviços) via API pública do SIDRA/IBGE.

Piloto técnico controlado — ver docs/08-decisoes-adr/0002-expansao-piloto-por-blocos.md
Fonte confirmada em: docs/04-fontes/ibge-sidra.md (Tabela SIDRA 5906) — Lote 05c.

Completa, junto com PMC (comércio, já coletado) e PIM (indústria), o trio de pesquisas
mensais de atividade citado pelo material do DIEESE sob o rótulo único "PMC/PMS/PIM".

Este script NÃO transforma o dado.
"""

import json
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

URL = "https://apisidra.ibge.gov.br/values/t/5906/n1/all/v/11626/p/all/c11046/56726"
DESTINO = Path(__file__).resolve().parents[3] / "data" / "raw" / "ibge_sidra"


def coletar() -> Path:
    DESTINO.mkdir(parents=True, exist_ok=True)
    with urllib.request.urlopen(URL, timeout=60) as resposta:
        dados = json.loads(resposta.read().decode("utf-8"))

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    arquivo = DESTINO / f"pms_servicos_sidra_5906_{timestamp}.json"
    arquivo.write_text(json.dumps(dados, ensure_ascii=False, indent=2), encoding="utf-8")
    return arquivo


if __name__ == "__main__":
    caminho = coletar()
    print(f"Coleta concluída: {caminho}")
