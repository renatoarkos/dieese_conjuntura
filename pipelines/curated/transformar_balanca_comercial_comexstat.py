"""Transformação CURATED da balança comercial (ADR 0005) — a partir do RAW gravado por
`pipelines/ingestao/bloco_1_macroeconomia/coleta_balanca_comercial_comexstat.py`
(CSV oficial do MDIC/Comex Stat, um arquivo por fluxo — exportação/importação — com uma
linha por operação, nível NCM).

===============================================================================
COMO O CSV POR OPERAÇÃO VIRA "UM PONTO POR MÊS"
===============================================================================
O CSV bruto tem uma linha por operação de comércio exterior (milhões de linhas
no arquivo do ano inteiro) — não é um indicador pronto. Este script soma a
coluna `VL_FOB` (valor da operação, em US$ FOB) agrupando por `CO_MES`
(`CO_ANO` é sempre o ano corrente, já que o script de ingestão só coleta o ano
vigente), produzindo um total mensal de exportação e um de importação. O saldo
é a diferença entre os dois. Isso é agregação simples (soma), não um cálculo
estatístico — nenhuma suposição é feita sobre o dado além de somar o que já
está lá.

O CSV usa `;` como separador de campo e aspas duplas em todo campo — formato
confirmado em `docs/04-fontes/mdic-tesouro.md` e no próprio arquivo bruto.

===============================================================================
POR QUE ESTE SCRIPT RECONSTRÓI ARQUIVOS PARTICIONADOS
===============================================================================
Os CSVs deste indicador (um ano inteiro de exportação ou importação) passam
fácil de 45 MB — acima do limite que `pipelines/supabase_raw.py` usa para
particionar automaticamente antes do envio ao Storage (ver ADR 0004). Quando
isso acontece, a linha de `raw_ingestoes` não tem `storage_path` preenchido
(fica `None`) — o caminho de cada pedaço vive em `metadata.partes`, na ordem
certa. Descoberto na prática: a primeira versão deste script só olhava
`storage_path`, então nunca achava o CSV de exportação/importação (sempre
particionados) — corrigido baixando e concatenando as partes quando
`storage_path` vem vazio.
"""

import csv
import io
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from curated_supabase import baixar_objeto_storage, buscar_ultimo_raw, registrar_serie

SCRIPT_ORIGEM = "pipelines/ingestao/bloco_1_macroeconomia/coleta_balanca_comercial_comexstat.py"


# ------------------------------------------------------------------------
# PASSO 1 — baixar o CSV mais recente de um fluxo (exportação/importação),
# reconstruindo a partir das partes quando o arquivo foi particionado
# ------------------------------------------------------------------------
def _registro_corresponde(registro: dict, prefixo_arquivo: str) -> bool:
    if prefixo_arquivo in (registro.get("storage_path") or ""):
        return True
    partes = ((registro.get("metadata") or {}).get("partes")) or []
    return any(prefixo_arquivo in p for p in partes)


def _baixar_raw(prefixo_arquivo: str) -> bytes:
    registros = buscar_ultimo_raw(SCRIPT_ORIGEM, limite=8)
    alvo = next((r for r in registros if _registro_corresponde(r, prefixo_arquivo)), None)
    if alvo is None:
        raise RuntimeError(f"Nenhum RAW '{prefixo_arquivo}' encontrado para {SCRIPT_ORIGEM}")

    if alvo.get("storage_path"):
        return baixar_objeto_storage(alvo["storage_path"])

    partes = (alvo.get("metadata") or {}).get("partes") or []
    if not partes:
        raise RuntimeError(f"RAW '{prefixo_arquivo}' sem storage_path e sem partes em metadata — registro inconsistente.")
    return b"".join(baixar_objeto_storage(p) for p in partes)


# ------------------------------------------------------------------------
# PASSO 2 — somar VL_FOB por mês (CO_ANO/CO_MES)
# ------------------------------------------------------------------------
def _somar_por_mes(conteudo_csv: bytes) -> dict[tuple[int, int], float]:
    texto = conteudo_csv.decode("utf-8")
    leitor = csv.DictReader(io.StringIO(texto), delimiter=";", quotechar='"')
    totais: dict[tuple[int, int], float] = {}
    for linha in leitor:
        chave = (int(linha["CO_ANO"]), int(linha["CO_MES"]))
        totais[chave] = totais.get(chave, 0.0) + float(linha["VL_FOB"])
    return totais


def _montar_pontos(totais: dict[tuple[int, int], float]) -> list[dict]:
    return [
        {"data_referencia": f"{ano:04d}-{mes:02d}-01", "valor": round(valor, 2)}
        for (ano, mes), valor in sorted(totais.items())
    ]


def transformar() -> dict[str, int]:
    totais_exportacao = _somar_por_mes(_baixar_raw("exportacao_ncm"))
    totais_importacao = _somar_por_mes(_baixar_raw("importacao_ncm"))

    pontos_exportacao = _montar_pontos(totais_exportacao)
    pontos_importacao = _montar_pontos(totais_importacao)

    meses_comuns = sorted(set(totais_exportacao) & set(totais_importacao))
    pontos_saldo = [
        {
            "data_referencia": f"{ano:04d}-{mes:02d}-01",
            "valor": round(totais_exportacao[(ano, mes)] - totais_importacao[(ano, mes)], 2),
        }
        for ano, mes in meses_comuns
    ]

    registrar_serie("balanca_exportacoes", pontos_exportacao)
    registrar_serie("balanca_importacoes", pontos_importacao)
    registrar_serie("balanca_saldo", pontos_saldo)

    return {
        "balanca_exportacoes": len(pontos_exportacao),
        "balanca_importacoes": len(pontos_importacao),
        "balanca_saldo": len(pontos_saldo),
    }


if __name__ == "__main__":
    resultado = transformar()
    for indicador_id, n in resultado.items():
        print(f"Transformação concluída: {n} pontos gravados em indicadores_serie ({indicador_id}).")
