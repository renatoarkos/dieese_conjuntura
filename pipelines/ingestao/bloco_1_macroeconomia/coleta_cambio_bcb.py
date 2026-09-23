"""Coleta bruta da taxa de câmbio (Livre — Dólar americano, venda) via API pública do BCB/SGS.

Piloto técnico controlado — ver docs/08-decisoes-adr/0002-expansao-piloto-por-blocos.md
Fonte confirmada em: docs/04-fontes/bcb.md

Coleta as duas séries candidatas identificadas no Discovery de Fontes: SGS 3694 (anual) e
SGS 3698 (mensal, hipótese de rótulo textual ainda não confirmada por nome oficial — ver
docs/04-fontes/bcb.md). Grava as duas SEM transformação nem escolha entre elas — essa decisão
pertence a uma camada posterior (STAGING), não à RAW.

Este script NÃO transforma o dado.
"""

import json
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

SERIES = {
    "3694": "https://api.bcb.gov.br/dados/serie/bcdata.sgs.3694/dados?formato=json",
    "3698": "https://api.bcb.gov.br/dados/serie/bcdata.sgs.3698/dados?formato=json",
}
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from supabase_raw import registrar_coleta

DESTINO = Path(__file__).resolve().parents[3] / "data" / "raw" / "bcb_sgs"


def coletar() -> list[Path]:
    DESTINO.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    arquivos = []
    for codigo, url in SERIES.items():
        with urllib.request.urlopen(url, timeout=60) as resposta:
            dados = json.loads(resposta.read().decode("utf-8"))
        arquivo = DESTINO / f"cambio_sgs_{codigo}_{timestamp}.json"
        arquivo.write_text(json.dumps(dados, ensure_ascii=False, indent=2), encoding="utf-8")
        arquivos.append(arquivo)
    return arquivos


if __name__ == "__main__":
    for caminho in coletar():
        print(f"Coleta concluída: {caminho}")
        registrar_coleta(fonte=DESTINO.name, arquivo=caminho, script=__file__)
