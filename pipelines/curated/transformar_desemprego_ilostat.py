"""Transformação CURATED do desemprego comparado internacionalmente (ADR 0005) — a
partir do RAW gravado por
`pipelines/ingestao/bloco_4_mercado_trabalho/coleta_desemprego_ilostat.py`
(ILOSTAT/OIT, CSV SDMX).

Headline = SEX='SEX_T' (ambos os sexos) + AGE='AGE_YTHADULT_YGE15' (15 anos
ou mais, a faixa etária ampla equivalente à usada na série do IBGE) —
confirmado inspecionando os códigos reais no CSV. Série ANUAL. **Não é a
mesma série que `taxa_desocupacao`** (SIDRA 4093) — é a estimativa
harmonizada da OIT, usada só para comparação internacional (ver docstring do
script de ingestão).
"""

import csv
import io
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from curated_supabase import baixar_objeto_storage, buscar_ultimo_raw, registrar_serie

SCRIPT_ORIGEM = "pipelines/ingestao/bloco_4_mercado_trabalho/coleta_desemprego_ilostat.py"
INDICADOR_ID = "desemprego_ilostat"
SEXO_ESCOLHIDO = "SEX_T"
FAIXA_ETARIA_ESCOLHIDA = "AGE_YTHADULT_YGE15"


def _baixar_raw() -> bytes:
    registros = buscar_ultimo_raw(SCRIPT_ORIGEM)
    if not registros:
        raise RuntimeError(f"Nenhum RAW com status=sucesso encontrado para {SCRIPT_ORIGEM}")
    return baixar_objeto_storage(registros[0]["storage_path"])


def _montar_pontos(conteudo_csv: bytes) -> list[dict]:
    texto = conteudo_csv.decode("utf-8")
    leitor = csv.DictReader(io.StringIO(texto))
    pontos = []
    for linha in leitor:
        if linha.get("SEX") != SEXO_ESCOLHIDO or linha.get("AGE") != FAIXA_ETARIA_ESCOLHIDA:
            continue
        valor_bruto = linha.get("OBS_VALUE")
        if not valor_bruto:
            continue
        ano = int(linha["TIME_PERIOD"])
        pontos.append({"data_referencia": f"{ano:04d}-01-01", "valor": float(valor_bruto)})
    pontos.sort(key=lambda p: p["data_referencia"])
    return pontos


def transformar() -> int:
    pontos = _montar_pontos(_baixar_raw())
    registrar_serie(INDICADOR_ID, pontos)
    return len(pontos)


if __name__ == "__main__":
    n = transformar()
    print(f"Transformação concluída: {n} pontos gravados em indicadores_serie ({INDICADOR_ID}).")
