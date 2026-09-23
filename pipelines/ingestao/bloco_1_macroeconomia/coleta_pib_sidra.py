"""Coleta bruta do PIB Brasil (variação do índice de volume trimestral) via API pública do SIDRA/IBGE.

Piloto técnico controlado — ver docs/08-decisoes-adr/0001-stack-minima-piloto-ingestao.md
Fonte confirmada em: docs/04-fontes/ibge-sidra.md (Tabela SIDRA 5932)

Este script NÃO transforma o dado — grava a resposta bruta da API exatamente como recebida,
respeitando o princípio de que a camada RAW nunca deve ser editada manualmente ou pré-processada
(ver CLAUDE.md, seção DADOS).
"""

import json
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

URL = "https://apisidra.ibge.gov.br/values/t/5932/n1/all/v/all/p/all/c11255/90707"
DESTINO = Path(__file__).resolve().parents[3] / "data" / "raw" / "ibge_sidra"


def coletar() -> Path:
    DESTINO.mkdir(parents=True, exist_ok=True)
    with urllib.request.urlopen(URL, timeout=60) as resposta:
        dados = json.loads(resposta.read().decode("utf-8"))

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    arquivo = DESTINO / f"pib_sidra_5932_{timestamp}.json"
    arquivo.write_text(json.dumps(dados, ensure_ascii=False, indent=2), encoding="utf-8")
    return arquivo


if __name__ == "__main__":
    caminho = coletar()
    print(f"Coleta concluída: {caminho}")
