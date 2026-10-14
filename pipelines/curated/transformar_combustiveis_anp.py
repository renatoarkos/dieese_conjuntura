"""Transformação CURATED dos preços de combustíveis (ADR 0005) — a partir do RAW
gravado por `pipelines/ingestao/bloco_3_inflacao/coleta_combustiveis_anp.py`
(ANP, microdados por posto revendedor, "últimas 4 semanas", 3 arquivos CSV).

===============================================================================
COMO O MICRODADO POR POSTO VIRA "UM PREÇO POR DIA"
===============================================================================
Cada CSV tem uma linha por posto revendedor que reportou preço numa data —
dezenas de milhares de linhas por arquivo. Este script agrupa por
`Data da Coleta` e tira a média simples do `Valor de Venda` nacional, para UM
produto representativo por arquivo (cada arquivo mistura produtos
correlatos): GASOLINA (não a aditivada) no arquivo de gasolina/etanol,
DIESEL S10 (o tipo hoje predominante no mercado brasileiro, não o DIESEL
comum) no arquivo de diesel/GNV, e GLP no arquivo de GLP (produto único,
sem escolha a fazer). Isso é uma média aritmética simples sobre o que já
está no arquivo — nenhuma ponderação ou estimativa é inventada aqui.
"""

import csv
import io
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from curated_supabase import baixar_objeto_storage, buscar_ultimo_raw, registrar_serie

SCRIPT_ORIGEM = "pipelines/ingestao/bloco_3_inflacao/coleta_combustiveis_anp.py"

# prefixo do arquivo -> (produto representativo, id do indicador)
ARQUIVO_PARA_PRODUTO = {
    "combustiveis_gasolina_etanol": ("GASOLINA", "combustivel_gasolina"),
    "combustiveis_diesel_gnv": ("DIESEL S10", "combustivel_diesel"),
    "combustiveis_glp": ("GLP", "combustivel_glp"),
}


def _baixar_raw(prefixo_arquivo: str) -> bytes:
    registros = buscar_ultimo_raw(SCRIPT_ORIGEM, limite=10)
    alvo = next((r for r in registros if prefixo_arquivo in (r.get("storage_path") or "")), None)
    if alvo is None:
        raise RuntimeError(f"Nenhum RAW '{prefixo_arquivo}' encontrado para {SCRIPT_ORIGEM}")
    return baixar_objeto_storage(alvo["storage_path"])


def _data_iso(data_anp: str) -> str:
    dia, mes, ano = data_anp.split("/")
    return f"{ano}-{mes}-{dia}"


def _media_nacional_por_dia(conteudo_csv: bytes, produto: str) -> dict[str, float]:
    texto = conteudo_csv.decode("latin-1")
    leitor = csv.DictReader(io.StringIO(texto), delimiter=";")
    somas: dict[str, float] = {}
    contagens: dict[str, int] = {}
    for linha in leitor:
        if linha.get("Produto") != produto:
            continue
        valor_texto = (linha.get("Valor de Venda") or "").replace(",", ".").strip()
        if not valor_texto:
            continue
        data_iso = _data_iso(linha["Data da Coleta"])
        somas[data_iso] = somas.get(data_iso, 0.0) + float(valor_texto)
        contagens[data_iso] = contagens.get(data_iso, 0) + 1
    return {data: somas[data] / contagens[data] for data in somas}


def transformar() -> dict[str, int]:
    resultado = {}
    for prefixo, (produto, indicador_id) in ARQUIVO_PARA_PRODUTO.items():
        conteudo = _baixar_raw(prefixo)
        medias = _media_nacional_por_dia(conteudo, produto)
        pontos = [{"data_referencia": data, "valor": round(valor, 3)} for data, valor in sorted(medias.items())]
        registrar_serie(indicador_id, pontos)
        resultado[indicador_id] = len(pontos)
    return resultado


if __name__ == "__main__":
    for indicador_id, n in transformar().items():
        print(f"Transformação concluída: {n} pontos gravados em indicadores_serie ({indicador_id}).")
