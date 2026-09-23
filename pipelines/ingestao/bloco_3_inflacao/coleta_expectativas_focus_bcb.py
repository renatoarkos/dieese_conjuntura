"""Coleta bruta das expectativas de mercado (Boletim Focus) para IPCA e INPC via API
pública Olinda do BCB.

Piloto técnico controlado — ver docs/08-decisoes-adr/0002-expansao-piloto-por-blocos.md
Fonte confirmada em: docs/04-fontes/bcb.md (Sistema de Expectativas de Mercado) — Lote 05c.

Este é um sistema diferente do SGS (Selic, câmbio, juros) — usa o portal Olinda de Dados
Abertos do BCB, protocolo OData. O material do DIEESE usa este sistema como insumo para
suas estimativas próprias (nowcasting) de INPC/IPCA (abas T23/T24) — este script coleta
apenas o dado de expectativa de mercado bruto, não a estimativa própria do DIEESE.

Este script NÃO transforma o dado.
"""

import json
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

BASE = "https://olinda.bcb.gov.br/olinda/servico/Expectativas/versao/v1/odata/ExpectativaMercadoMensais"
INDICADORES = ["IPCA", "INPC"]
DESTINO = Path(__file__).resolve().parents[3] / "data" / "raw" / "bcb_focus"


def _url(indicador: str) -> str:
    params = {"$filter": f"Indicador eq '{indicador}'", "$format": "json"}
    return BASE + "?" + urllib.parse.urlencode(params, quote_via=urllib.parse.quote)


def coletar() -> list[Path]:
    DESTINO.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    arquivos = []
    for indicador in INDICADORES:
        req = urllib.request.Request(_url(indicador), headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=60) as resposta:
            dados = json.loads(resposta.read().decode("utf-8"))
        arquivo = DESTINO / f"expectativas_{indicador.lower()}_{timestamp}.json"
        arquivo.write_text(json.dumps(dados, ensure_ascii=False, indent=2), encoding="utf-8")
        arquivos.append(arquivo)
    return arquivos


if __name__ == "__main__":
    for caminho in coletar():
        print(f"Coleta concluída: {caminho}")
