"""Coleta bruta das taxas médias de juros por modalidade (recursos livres, PF/PJ) via API
pública do BCB/SGS.

Piloto técnico controlado — ver docs/08-decisoes-adr/0002-expansao-piloto-por-blocos.md
Fonte confirmada em: docs/04-fontes/bcb.md — os 4 códigos já eram citados célula a célula no
material interno do DIEESE (aba T16), e foram confirmados por chamada real de API em 2026-09-22.

Este script NÃO transforma o dado — grava cada série SGS separadamente, sem consolidação.
"""

import json
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

SERIES = {
    "20728": "https://api.bcb.gov.br/dados/serie/bcdata.sgs.20728/dados?formato=json",  # PJ - Aquisição de veículos
    "22019": "https://api.bcb.gov.br/dados/serie/bcdata.sgs.22019/dados?formato=json",  # PJ - Cartão de crédito rotativo
    "20741": "https://api.bcb.gov.br/dados/serie/bcdata.sgs.20741/dados?formato=json",  # PF - Cheque especial
    "20742": "https://api.bcb.gov.br/dados/serie/bcdata.sgs.20742/dados?formato=json",  # PF - Crédito pessoal não consignado
}
DESTINO = Path(__file__).resolve().parents[3] / "data" / "raw" / "bcb_sgs"


def coletar() -> list[Path]:
    DESTINO.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    arquivos = []
    for codigo, url in SERIES.items():
        with urllib.request.urlopen(url, timeout=60) as resposta:
            dados = json.loads(resposta.read().decode("utf-8"))
        arquivo = DESTINO / f"juros_modalidade_sgs_{codigo}_{timestamp}.json"
        arquivo.write_text(json.dumps(dados, ensure_ascii=False, indent=2), encoding="utf-8")
        arquivos.append(arquivo)
    return arquivos


if __name__ == "__main__":
    for caminho in coletar():
        print(f"Coleta concluída: {caminho}")
