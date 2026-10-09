"""Transformação CURATED da taxa de câmbio (ADR 0005) — a partir do RAW gravado por
`pipelines/ingestao/bloco_1_macroeconomia/coleta_cambio_bcb.py` (BCB/SGS).

===============================================================================
POR QUE A SÉRIE 3698 (NÃO A 3694)
===============================================================================
O script de ingestão coleta as duas séries candidatas (SGS 3694 e 3698, ver
docstring daquele script) porque não estava confirmado qual o DIEESE usa. Essa
escolha é justamente o tipo de decisão que pertence à camada CURATED (ver
CLAUDE.md, seção DADOS) — e aqui ela é feita: **3698** (média mensal), por ser
a mais útil para um cartão de painel que atualiza mês a mês. Se no futuro ficar
confirmado que o DIEESE usa a 3694 (média anual), trocar só a constante
`CODIGO_ESCOLHIDO` abaixo.

===============================================================================
POR QUE PRECISA FILTRAR O STORAGE_PATH (E NÃO SÓ PEGAR "O RAW MAIS RECENTE")
===============================================================================
`coleta_cambio_bcb.py` grava as duas séries no MESMO script (`script=__file__`
é idêntico para ambas) — por isso `buscar_ultimo_raw` sozinho devolveria uma
mistura de arquivos 3694 e 3698. Este script pede várias linhas recentes e
pega a primeira cujo nome de arquivo contém "_3698_".
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from curated_supabase import baixar_objeto_storage, buscar_ultimo_raw, registrar_serie

SCRIPT_ORIGEM = "pipelines/ingestao/bloco_1_macroeconomia/coleta_cambio_bcb.py"
INDICADOR_ID = "cambio_dolar"
CODIGO_ESCOLHIDO = "3698"


# ------------------------------------------------------------------------
# PASSO 1 — baixar o RAW mais recente da série 3698 especificamente
# ------------------------------------------------------------------------
def _baixar_raw() -> list:
    registros = buscar_ultimo_raw(SCRIPT_ORIGEM, limite=10)
    alvo = next(
        (r for r in registros if f"_{CODIGO_ESCOLHIDO}_" in (r.get("storage_path") or "")),
        None,
    )
    if alvo is None:
        raise RuntimeError(f"Nenhum RAW da série SGS {CODIGO_ESCOLHIDO} encontrado para {SCRIPT_ORIGEM}")
    conteudo = baixar_objeto_storage(alvo["storage_path"])
    return json.loads(conteudo.decode("utf-8"))


# ------------------------------------------------------------------------
# PASSO 2 — converter "DD/MM/AAAA" (formato do BCB/SGS) em "AAAA-MM-DD"
# ------------------------------------------------------------------------
def _data_iso(data_bcb: str) -> str:
    dia, mes, ano = data_bcb.split("/")
    return f"{ano}-{mes}-{dia}"


# ------------------------------------------------------------------------
# PASSO 3 — montar os pontos
# ------------------------------------------------------------------------
def _montar_pontos(dados: list) -> list[dict]:
    return [
        {"data_referencia": _data_iso(linha["data"]), "valor": float(linha["valor"])}
        for linha in dados
    ]


def transformar() -> int:
    dados = _baixar_raw()
    pontos = _montar_pontos(dados)
    registrar_serie(INDICADOR_ID, pontos)
    return len(pontos)


if __name__ == "__main__":
    n = transformar()
    print(f"Transformação concluída: {n} pontos gravados em indicadores_serie ({INDICADOR_ID}).")
