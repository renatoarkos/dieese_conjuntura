"""Coleta bruta do IGP-M (Índice Geral de Preços — Mercado, FGV) via API pública do
BCB/SGS.

Piloto técnico controlado — ver docs/08-decisoes-adr/0002-expansao-piloto-por-blocos.md
Fonte confirmada em: docs/04-fontes/fgv-indatend.md — Lote 06b.

DECISÃO DE FORMATO DE EXTRAÇÃO: o Portal FGV/IBRE não expõe API pública nem download
gratuito estruturado (acesso é via contrato/assinatura, confirmado nesta rodada). O
BCB replica oficialmente o IGP-M via SGS (código 189) — usado aqui como rota
alternativa gratuita e pública. Cobre APENAS o IGP-M, não os demais índices FGV
eventualmente citados pelo material do DIEESE (ex. IPC-Fi, IPC-S), que não têm
correspondente SGS confirmado.

Este script NÃO transforma o dado.
"""

import json
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

URL = "https://api.bcb.gov.br/dados/serie/bcdata.sgs.189/dados?formato=json"
DESTINO = Path(__file__).resolve().parents[3] / "data" / "raw" / "bcb_sgs"


def coletar() -> Path:
    DESTINO.mkdir(parents=True, exist_ok=True)
    with urllib.request.urlopen(URL, timeout=60) as resposta:
        dados = json.loads(resposta.read().decode("utf-8"))

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    arquivo = DESTINO / f"igpm_sgs_189_{timestamp}.json"
    arquivo.write_text(json.dumps(dados, ensure_ascii=False, indent=2), encoding="utf-8")
    return arquivo


if __name__ == "__main__":
    caminho = coletar()
    print(f"Coleta concluída: {caminho}")
