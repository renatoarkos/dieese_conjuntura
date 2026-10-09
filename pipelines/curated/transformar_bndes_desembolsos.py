"""Transformação CURATED dos desembolsos do BNDES (ADR 0005) — a partir do RAW gravado
por `pipelines/ingestao/bloco_1_macroeconomia/coleta_bndes_desembolsos.py` (CKAN,
microdados por operação do mês mais recente disponível).

O RAW é uma lista de operações individuais (13 mil+ no mês mais recente
testado) — este script soma o campo `desembolsos_reais` de todas elas,
produzindo o desembolso total do mês. Essa soma simples é a única
transformação feita aqui; quebrar por setor/UF/porte de empresa (como o
próprio RAW permite) é extensão futura, não implementada nesta rodada.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from curated_supabase import baixar_objeto_storage, buscar_ultimo_raw, registrar_serie

SCRIPT_ORIGEM = "pipelines/ingestao/bloco_1_macroeconomia/coleta_bndes_desembolsos.py"
INDICADOR_ID = "bndes_desembolsos"


def _baixar_raw() -> dict:
    registros = buscar_ultimo_raw(SCRIPT_ORIGEM)
    if not registros:
        raise RuntimeError(f"Nenhum RAW com status=sucesso encontrado para {SCRIPT_ORIGEM}")
    conteudo = baixar_objeto_storage(registros[0]["storage_path"])
    return json.loads(conteudo.decode("utf-8"))


def _montar_ponto(dados: dict) -> dict | None:
    registros = dados.get("result", {}).get("records", [])
    if not registros:
        return None
    ano, mes = registros[0]["ano"], registros[0]["mes"]
    total = sum(float(r["desembolsos_reais"]) for r in registros)
    return {
        "data_referencia": f"{ano:04d}-{mes:02d}-01",
        "valor": round(total, 2),
        "metadata": {"numero_operacoes": len(registros)},
    }


def transformar() -> int:
    dados = _baixar_raw()
    ponto = _montar_ponto(dados)
    if ponto is None:
        return 0
    registrar_serie(INDICADOR_ID, [ponto])
    return 1


if __name__ == "__main__":
    n = transformar()
    print(f"Transformação concluída: {n} ponto(s) gravado(s) em indicadores_serie ({INDICADOR_ID}).")
