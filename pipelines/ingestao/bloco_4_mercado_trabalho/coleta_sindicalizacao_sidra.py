"""Coleta bruta da taxa de sindicalização das pessoas ocupadas, por grupamento de
atividade, via API pública do SIDRA/IBGE.

Piloto técnico controlado — ver docs/08-decisoes-adr/0002-expansao-piloto-por-blocos.md
Fonte confirmada em: docs/04-fontes/ibge-sidra.md — investigação de lacunas, 2026-09-22.

ACHADO: este indicador estava sem NENHUMA fonte confirmada no projeto. Localizada e
testada a Tabela SIDRA 8676 (PNAD Contínua anual, módulo "Características Adicionais
do Mercado de Trabalho") — valor de 2024 (8,9%) bate exatamente com o número citado no
título do slide do material do DIEESE ("Com taxa de 8,9%, sindicalização cresce pela
primeira vez desde 2012"), confirmando que é a fonte correta.

NOTA SOBRE A SÉRIE: não é anual contínua — o suplemento não foi levantado em 2020 e
2021 (provável disrupção da pandemia no desenho da pesquisa). Série real: 2012-2019,
hiato, 2022-2024. Nível territorial disponível: apenas Brasil e Grandes Regiões (sem
UF/município).

Este script NÃO transforma o dado.
"""

import json
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

URL = "https://apisidra.ibge.gov.br/values/t/8676/n1/all/v/12535/p/all/c888/all"
DESTINO = Path(__file__).resolve().parents[3] / "data" / "raw" / "ibge_sidra"


def coletar() -> Path:
    DESTINO.mkdir(parents=True, exist_ok=True)
    with urllib.request.urlopen(URL, timeout=60) as resposta:
        dados = json.loads(resposta.read().decode("utf-8"))

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    arquivo = DESTINO / f"sindicalizacao_sidra_8676_{timestamp}.json"
    arquivo.write_text(json.dumps(dados, ensure_ascii=False, indent=2), encoding="utf-8")
    return arquivo


if __name__ == "__main__":
    caminho = coletar()
    print(f"Coleta concluída: {caminho}")
