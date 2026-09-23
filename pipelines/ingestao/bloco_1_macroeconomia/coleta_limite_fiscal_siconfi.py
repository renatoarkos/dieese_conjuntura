"""Coleta bruta do limite fiscal (prudencial e máximo) de despesa com pessoal, por Unidade
da Federação, via API pública do SICONFI (Tesouro Nacional).

Piloto técnico controlado — ver docs/08-decisoes-adr/0002-expansao-piloto-por-blocos.md
Fonte confirmada em: docs/04-fontes/mdic-tesouro.md (SICONFI, Relatório de Gestão Fiscal)

Coleta o Relatório de Gestão Fiscal (RGF) do Poder Executivo estadual, para as 27
Unidades da Federação (26 estados + Distrito Federal), no quadrimestre mais recente
com dados confirmados disponíveis nesta rodada (2026, 1º quadrimestre).

Este script NÃO transforma o dado — grava a resposta de cada UF separadamente.
"""

import json
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

# Códigos IBGE das 27 Unidades da Federação (tabela de referência padrão do IBGE).
CODIGOS_UF = {
    "RO": 11, "AC": 12, "AM": 13, "RR": 14, "PA": 15, "AP": 16, "TO": 17,
    "MA": 21, "PI": 22, "CE": 23, "RN": 24, "PB": 25, "PE": 26, "AL": 27, "SE": 28, "BA": 29,
    "MG": 31, "ES": 32, "RJ": 33, "SP": 35,
    "PR": 41, "SC": 42, "RS": 43,
    "MS": 50, "MT": 51, "GO": 52, "DF": 53,
}

AN_EXERCICIO = 2026
NR_PERIODO = 1  # 1º quadrimestre — período mais recente com dados confirmados nesta rodada
DESTINO = Path(__file__).resolve().parents[3] / "data" / "raw" / "siconfi"


def _url(id_ente: int) -> str:
    return (
        "https://apidatalake.tesouro.gov.br/ords/siconfi/tt/rgf"
        f"?an_exercicio={AN_EXERCICIO}&nr_periodo={NR_PERIODO}"
        "&co_tipo_demonstrativo=RGF&co_poder=E&co_esfera=E&in_periodicidade=Q"
        f"&id_ente={id_ente}"
    )


def coletar() -> list[Path]:
    DESTINO.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    arquivos = []
    for uf, id_ente in CODIGOS_UF.items():
        with urllib.request.urlopen(_url(id_ente), timeout=60) as resposta:
            dados = json.loads(resposta.read().decode("utf-8"))
        arquivo = DESTINO / f"limite_fiscal_{uf}_{AN_EXERCICIO}Q{NR_PERIODO}_{timestamp}.json"
        arquivo.write_text(json.dumps(dados, ensure_ascii=False, indent=2), encoding="utf-8")
        arquivos.append(arquivo)
    return arquivos


if __name__ == "__main__":
    arquivos = coletar()
    print(f"Coleta concluída: {len(arquivos)} arquivos (1 por UF) em {DESTINO}")
