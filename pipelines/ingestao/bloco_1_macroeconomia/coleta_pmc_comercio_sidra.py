"""Coleta bruta do índice/variação da receita nominal e do volume de vendas no comércio
varejista ampliado (PMC) via API pública do SIDRA/IBGE.

Piloto técnico controlado — ver docs/08-decisoes-adr/0002-expansao-piloto-por-blocos.md
Fonte confirmada em: docs/04-fontes/ibge-sidra.md (Tabela SIDRA 8881)

ATENÇÃO: o material do DIEESE descreve este indicador como "comércio/serviços/indústria
(PMC/PMS/PIM)", mas a Tabela 8881 cobre APENAS a Pesquisa Mensal de Comércio (PMC) —
as tabelas de PMS (serviços) e PIM (indústria) não foram identificadas nesta rodada de
Discovery de Fontes. Este script coleta somente a parcela comércio.

Este script NÃO transforma o dado.
"""

import json
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

URL = "https://apisidra.ibge.gov.br/values/t/8881/n1/all/v/all/p/all/c11046/all"
DESTINO = Path(__file__).resolve().parents[3] / "data" / "raw" / "ibge_sidra"


def coletar() -> Path:
    DESTINO.mkdir(parents=True, exist_ok=True)
    with urllib.request.urlopen(URL, timeout=60) as resposta:
        dados = json.loads(resposta.read().decode("utf-8"))

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    arquivo = DESTINO / f"pmc_comercio_sidra_8881_{timestamp}.json"
    arquivo.write_text(json.dumps(dados, ensure_ascii=False, indent=2), encoding="utf-8")
    return arquivo


if __name__ == "__main__":
    caminho = coletar()
    print(f"Coleta concluída: {caminho}")
