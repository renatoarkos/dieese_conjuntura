"""Transformação CURATED do INPC — a partir do RAW gravado por
`pipelines/ingestao/bloco_3_inflacao/coleta_inpc_bcb.py` (BCB/SGS, série 188).

Nome do arquivo mantido como `transformar_inpc_sidra.py` por compatibilidade
com o resto do projeto — apesar do nome, a fonte agora é o BCB/SGS. Ver
`coleta_ipca_bcb.py`/`coleta_inpc_bcb.py` para o raciocínio completo da troca
de fonte (2026-10-26): mesmo indicador (`inpc`), histórico bem mais longo.

`coleta_inpc_sidra.py` continua no repositório, não apagado — só deixou de
ser a fonte usada por esta transformação.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from curated_supabase import baixar_objeto_storage, buscar_ultimo_raw, registrar_serie

SCRIPT_ORIGEM = "pipelines/ingestao/bloco_3_inflacao/coleta_inpc_bcb.py"
INDICADOR_ID = "inpc"


def _baixar_raw() -> list:
    registros = buscar_ultimo_raw(SCRIPT_ORIGEM)
    if not registros:
        raise RuntimeError(f"Nenhum RAW com status=sucesso encontrado para {SCRIPT_ORIGEM}")
    return json.loads(baixar_objeto_storage(registros[0]["storage_path"]).decode("utf-8"))


def _data_iso(data_bcb: str) -> str:
    dia, mes, ano = data_bcb.split("/")
    return f"{ano}-{mes}-{dia}"


def _montar_pontos(dados: list) -> list[dict]:
    pontos = []
    for linha in dados:
        valor_bruto = linha.get("valor")
        data_bruta = linha.get("data")
        if valor_bruto is None or not data_bruta:
            continue
        pontos.append({"data_referencia": _data_iso(data_bruta), "valor": float(valor_bruto)})
    return pontos


def transformar() -> int:
    pontos = _montar_pontos(_baixar_raw())
    registrar_serie(INDICADOR_ID, pontos)
    return len(pontos)


if __name__ == "__main__":
    n = transformar()
    print(f"Transformação concluída: {n} pontos gravados em indicadores_serie ({INDICADOR_ID}).")
