"""Transformação CURATED do "Balanço das Greves" (ADR 0005) — extrai o total
de greves e as horas paradas do ano de dentro do texto do boletim PDF em
`pipelines/ingestao/bloco_4_mercado_trabalho/coleta_greves_dieese.py`.

Mesmo princípio de `transformar_ict_dieese.py`: extrai só os valores que
aparecem em texto corrido isolado (título "Balanço das Greves de AAAA") e na
linha "Total" da TABELA 1 ("Greves e horas paradas — Brasil, AAAA"), que
ficam fora da área de gráficos sobrepostos — não tenta reconstruir os dados
por esfera (pública/privada) nem por categoria/reivindicação, que aparecem
em tabelas e gráficos mais complexos, fora do escopo desta primeira versão.

Periodicidade real: o boletim "Balanço das Greves" é anual (fecha o ano
anterior completo) — `data_referencia` é sempre 1º de janeiro do ano coberto.
"""

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from curated_supabase import baixar_objeto_storage, buscar_ultimo_raw, extrair_texto_pdf, registrar_serie

SCRIPT_ORIGEM = "pipelines/ingestao/bloco_4_mercado_trabalho/coleta_greves_dieese.py"
INDICADOR_TOTAL = "greves_total_ano"
INDICADOR_HORAS = "greves_horas_paradas_ano"

PADRAO_ANO = re.compile(r"Balan[çc]o das Greves de (\d{4})")
PADRAO_TOTAL = re.compile(r"Total\s+(\d{1,3}(?:\.\d{3})*)\s+100(?:,0)?\s+(\d{1,3}(?:\.\d{3})*)\s+100")


def _numero_br(texto: str) -> float:
    return float(texto.replace(".", ""))


def _baixar_pdf() -> bytes:
    registros = buscar_ultimo_raw(SCRIPT_ORIGEM)
    if not registros:
        raise RuntimeError(f"Nenhum RAW com status=sucesso encontrado para {SCRIPT_ORIGEM}")
    return baixar_objeto_storage(registros[0]["storage_path"])


def transformar() -> dict[str, int]:
    texto = extrair_texto_pdf(_baixar_pdf())

    m_ano = PADRAO_ANO.search(texto)
    m_total = PADRAO_TOTAL.search(texto)
    if not m_ano or not m_total:
        raise RuntimeError(
            "Padrão de título/tabela do Balanço das Greves não encontrado — o formato do boletim "
            "pode ter mudado; não publicar valor adivinhado."
        )

    ano = m_ano.group(1)
    total_greves = _numero_br(m_total.group(1))
    horas_paradas = _numero_br(m_total.group(2))
    data_referencia = f"{ano}-01-01"

    registrar_serie(INDICADOR_TOTAL, [{"data_referencia": data_referencia, "valor": total_greves}])
    registrar_serie(INDICADOR_HORAS, [{"data_referencia": data_referencia, "valor": horas_paradas}])
    return {INDICADOR_TOTAL: 1, INDICADOR_HORAS: 1}


if __name__ == "__main__":
    for indicador_id, n in transformar().items():
        print(f"Transformação concluída: {n} ponto gravado em indicadores_serie ({indicador_id}).")
