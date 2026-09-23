"""Coleta bruta do PIB Mundial (variação real, % a.a.) via API pública do FMI (WEO Database).

Piloto técnico controlado — ver docs/08-decisoes-adr/0002-expansao-piloto-por-blocos.md
Fonte confirmada em: docs/04-fontes/fmi-cni.md (dataflow WEO, indicador NGDP_RPCH)

Usa a API SDMX 3.0 do FMI (api.imf.org), sem necessidade de chave/autenticação.

LIMITAÇÃO CONHECIDA: os códigos de país usados pelo dataflow WEO não são ISO3 simples
(ex. "BRA" não funciona diretamente) — este script coleta a consulta com curinga "*"
(todos os países/agregados disponíveis) em vez de filtrar por país específico, evitando
adivinhar um código de país não confirmado. Filtrar por país específico é um refinamento
de STAGING, não desta coleta RAW.

Este script NÃO transforma o dado.
"""

import json
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

URL = (
    "https://api.imf.org/external/sdmx/3.0/data/dataflow/IMF.RES/WEO/~/A.*.NGDP_RPCH"
    "?startPeriod=2016&endPeriod=2030"
)
DESTINO = Path(__file__).resolve().parents[3] / "data" / "raw" / "fmi_weo"


def coletar() -> Path:
    DESTINO.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(URL, headers={"Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as resposta:
        dados = json.loads(resposta.read().decode("utf-8"))

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    arquivo = DESTINO / f"pib_mundial_weo_ngdp_rpch_{timestamp}.json"
    arquivo.write_text(json.dumps(dados, ensure_ascii=False, indent=2), encoding="utf-8")
    return arquivo


if __name__ == "__main__":
    caminho = coletar()
    print(f"Coleta concluída: {caminho}")
