"""Coleta bruta do IPCA — índice geral (variação mensal, acumulada no ano, acumulada em 12 meses,
peso mensal) via API pública do SIDRA/IBGE.

Piloto técnico controlado — ver docs/08-decisoes-adr/0001-stack-minima-piloto-ingestao.md
Fonte confirmada em: docs/04-fontes/ibge-sidra.md (Tabela SIDRA 7060)

ATENÇÃO: esta tabela cobre apenas a partir de janeiro/2020 (pesos POF 2017-2018) — não é a mesma
base de pesos citada no material interno do DIEESE ("jan/2012"), que corresponde à Tabela SIDRA
1419 (histórica). Ver alerta completo em docs/04-fontes/ibge-sidra.md e a pergunta de validação
humana QF05 em research/notas/DISCOVERY_FONTES_LOTE_PILOTO_01.md.

Este script coleta apenas o índice geral (categoria 7169) — não inclui os agregados especiais
"Serviços" e "Monitorados" citados no material do DIEESE, cuja tabela de origem não foi
localizada nesta rodada (classificação D, ver docs/04-fontes/CHECKLIST_FONTES_DATALAKE.md).

Este script NÃO transforma o dado — grava a resposta bruta da API exatamente como recebida.
"""

import json
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

URL = "https://apisidra.ibge.gov.br/values/t/7060/n1/all/v/all/p/all/c315/7169"
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from supabase_raw import registrar_coleta

DESTINO = Path(__file__).resolve().parents[3] / "data" / "raw" / "ibge_sidra"


def coletar() -> Path:
    DESTINO.mkdir(parents=True, exist_ok=True)
    with urllib.request.urlopen(URL, timeout=60) as resposta:
        dados = json.loads(resposta.read().decode("utf-8"))

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    arquivo = DESTINO / f"ipca_sidra_7060_{timestamp}.json"
    arquivo.write_text(json.dumps(dados, ensure_ascii=False, indent=2), encoding="utf-8")
    return arquivo


if __name__ == "__main__":
    caminho = coletar()
    print(f"Coleta concluída: {caminho}")
    registrar_coleta(fonte=DESTINO.name, arquivo=caminho, script=__file__)
