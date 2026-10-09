"""Transformação CURATED do volume de vendas no comércio — PMC (ADR 0005) — a partir do
RAW gravado por `pipelines/ingestao/bloco_1_macroeconomia/coleta_pmc_comercio_sidra.py`
(SIDRA tabela 8881).

A tabela 8881 cruza 6 variáveis (`D2C`: número-índice com/sem ajuste sazonal,
e 4 recortes de variação) com 2 classificações (`D4C`: receita nominal vs.
volume de vendas) — 12 séries diferentes misturadas no mesmo RAW. Este script
usa `D2C=11709` ("Variação mês/mesmo mês do ano anterior") e
`D4C=56736` ("Índice de volume de vendas no comércio varejista ampliado") como
o recorte headline do cartão — mesmo critério de "o que normalmente vira
manchete" usado em `transformar_pib_sidra.py`. Sem o filtro por `D4C`, a
receita nominal e o volume de vendas do mesmo mês ficam misturados na mesma
série (confirmado: produzia dois valores diferentes para o mesmo mês). O
período (`D3C`, formato "AAAAMM") é mensal direto, diferente do PIB/taxa de
investimento (trimestral).
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from curated_supabase import baixar_objeto_storage, buscar_ultimo_raw, registrar_serie

SCRIPT_ORIGEM = "pipelines/ingestao/bloco_1_macroeconomia/coleta_pmc_comercio_sidra.py"
INDICADOR_ID = "pmc_volume_vendas"
D2C_ESCOLHIDO = "11709"  # variação mês/mesmo mês do ano anterior
D4C_ESCOLHIDO = "56736"  # índice de volume de vendas (não receita nominal)


def _baixar_raw() -> list:
    registros = buscar_ultimo_raw(SCRIPT_ORIGEM)
    if not registros:
        raise RuntimeError(f"Nenhum RAW com status=sucesso encontrado para {SCRIPT_ORIGEM}")
    conteudo = baixar_objeto_storage(registros[0]["storage_path"])
    return json.loads(conteudo.decode("utf-8"))


def _data_do_mes(codigo_periodo: str) -> str:
    ano, mes = codigo_periodo[:4], codigo_periodo[4:6]
    return f"{ano}-{mes}-01"


def _montar_pontos(dados: list) -> list[dict]:
    pontos = []
    for linha in dados[1:]:
        if linha.get("D2C") != D2C_ESCOLHIDO or linha.get("D4C") != D4C_ESCOLHIDO:
            continue
        valor_bruto = linha.get("V")
        if valor_bruto in (None, "...", "-", "X"):
            continue
        pontos.append(
            {
                "data_referencia": _data_do_mes(linha["D3C"]),
                "valor": float(valor_bruto),
                "metadata": {"d3n": linha.get("D3N")},
            }
        )
    return pontos


def transformar() -> int:
    dados = _baixar_raw()
    pontos = _montar_pontos(dados)
    registrar_serie(INDICADOR_ID, pontos)
    return len(pontos)


if __name__ == "__main__":
    n = transformar()
    print(f"Transformação concluída: {n} pontos gravados em indicadores_serie ({INDICADOR_ID}).")
