"""Coleta bruta do endividamento e comprometimento de renda das famílias com o Sistema
Financeiro Nacional (RNDBF) via API pública do BCB/SGS.

Piloto técnico controlado — ver docs/08-decisoes-adr/0002-expansao-piloto-por-blocos.md
Fonte confirmada em: docs/04-fontes/bcb.md — Lote 06a.

Parte BCB do indicador "endividamento familiar" do material do DIEESE (a parte
PEIC/FecomercioSP já foi coletada em coleta_endividamento_peic_fecomercio.py, no
bloco 2). O material cita "Tabela 27" — rótulo interno do DIEESE, sem correspondência
literal confirmada no catálogo do BCB. As 3 séries abaixo são a família RNDBF completa
(comprometimento de renda, com e sem ajuste sazonal; e endividamento das famílias) —
coletadas como séries RAW separadas; qual série (ou combinação) corresponde
exatamente à "Tabela 27" do DIEESE é uma decisão de STAGING, não desta coleta.

Este script NÃO transforma o dado.
"""

import json
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

SERIES = {
    "29034": "https://api.bcb.gov.br/dados/serie/bcdata.sgs.29034/dados?formato=json",  # Comprometimento de renda, com ajuste sazonal
    "29265": "https://api.bcb.gov.br/dados/serie/bcdata.sgs.29265/dados?formato=json",  # Comprometimento de renda, sem ajuste sazonal
    "29037": "https://api.bcb.gov.br/dados/serie/bcdata.sgs.29037/dados?formato=json",  # Endividamento das famílias (acumulado 12 meses)
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
        arquivo = DESTINO / f"endividamento_sgs_{codigo}_{timestamp}.json"
        arquivo.write_text(json.dumps(dados, ensure_ascii=False, indent=2), encoding="utf-8")
        arquivos.append(arquivo)
    return arquivos


if __name__ == "__main__":
    for caminho in coletar():
        print(f"Coleta concluída: {caminho}")
        registrar_coleta(fonte=DESTINO.name, arquivo=caminho, script=__file__)
