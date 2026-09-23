"""Coleta bruta do saldo da carteira de crédito do Sistema Financeiro Nacional (total,
PF, PJ, recursos livres/direcionados) via API pública do BCB/SGS.

Piloto técnico controlado — ver docs/08-decisoes-adr/0002-expansao-piloto-por-blocos.md
Fonte confirmada em: docs/04-fontes/bcb.md — Lote 06a.

Coleta as 6 séries confirmadas por teste real nesta rodada. NÃO inclui os recortes
"PJ — recursos livres — total" (SGS 20543), "PJ — recursos direcionados — total"
(SGS 20594) nem "PF — recursos direcionados — total" (nenhum código único
identificado) — esses candidatos foram encontrados por busca no catálogo do BCB mas
NÃO testados via API nesta rodada, então ficam fora do piloto até confirmação.

Este script NÃO transforma o dado.
"""

import json
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

SERIES = {
    "20539": "https://api.bcb.gov.br/dados/serie/bcdata.sgs.20539/dados?formato=json",  # Total (PF+PJ, livres+direcionados)
    "20541": "https://api.bcb.gov.br/dados/serie/bcdata.sgs.20541/dados?formato=json",  # Pessoas físicas - Total
    "20540": "https://api.bcb.gov.br/dados/serie/bcdata.sgs.20540/dados?formato=json",  # Pessoas jurídicas - Total
    "20542": "https://api.bcb.gov.br/dados/serie/bcdata.sgs.20542/dados?formato=json",  # Recursos livres - Total
    "20593": "https://api.bcb.gov.br/dados/serie/bcdata.sgs.20593/dados?formato=json",  # Recursos direcionados - Total
    "20570": "https://api.bcb.gov.br/dados/serie/bcdata.sgs.20570/dados?formato=json",  # Recursos livres - Pessoas físicas - Total
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
        arquivo = DESTINO / f"saldo_credito_sfn_sgs_{codigo}_{timestamp}.json"
        arquivo.write_text(json.dumps(dados, ensure_ascii=False, indent=2), encoding="utf-8")
        arquivos.append(arquivo)
    return arquivos


if __name__ == "__main__":
    for caminho in coletar():
        print(f"Coleta concluída: {caminho}")
        registrar_coleta(fonte=DESTINO.name, arquivo=caminho, script=__file__)
