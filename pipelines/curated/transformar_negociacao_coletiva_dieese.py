"""Transformação CURATED de Reajustes salariais e Pisos salariais (ADR 0005)
— extrai os valores de dentro do texto do boletim "De Olho nas Negociações"
em `pipelines/ingestao/bloco_4_mercado_trabalho/coleta_negociacao_coletiva_dieese.py`
(mesmo PDF alimenta os 2 indicadores, por isso 1 script só).

Mesmo princípio de `transformar_ict_dieese.py`: só os trechos em texto
corrido isolado (fora de gráfico) são extraídos.

- **Reajustes**: "A data-base <mês> registrou reajustes acima da variação do
  INPC-IBGE em XX,X% dos N acordos..." (percentual acima do INPC + nº de
  acordos da data-base mais recente) e "...abaixo da variação do INPC atingiu
  XX,X%" (percentual abaixo). O percentual "igual" não é extraído — nenhuma
  frase do texto corrido o declara isoladamente (só aparece dentro do
  gráfico), e 100 − acima − abaixo seria uma inferência, não um dado lido.
  **O "abaixo" nem sempre está no texto corrido** (confirmado comparando a
  edição 72 com a 71: a 71 não tem essa frase isolada naquele mês — só
  dentro do gráfico) — por isso é tratado como campo opcional: quando falta,
  o script publica os outros 3 indicadores normalmente e só avisa no log,
  não inventa o valor nem falha a transformação inteira.
- **Pisos salariais**: "Nas últimas 12 datas-bases, o valor médio foi de
  R$ X, e o mediano, de R$ Y" — usa o agregado de 12 datas-bases (não o
  acumulado do ano corrente, que reinicia em janeiro e teria uma quebra
  artificial na série todo início de ano).

`data_referencia` de todos: 1º dia do mês da data-base mais recente coberta
pelo boletim ("Resultados até <mês> de <ano>", no início do documento).
"""

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from curated_supabase import baixar_objeto_storage, buscar_ultimo_raw, extrair_texto_pdf, registrar_serie

SCRIPT_ORIGEM = "pipelines/ingestao/bloco_4_mercado_trabalho/coleta_negociacao_coletiva_dieese.py"

INDICADOR_REAJUSTE_ACIMA = "reajustes_acima_inpc_pct"
INDICADOR_REAJUSTE_ABAIXO = "reajustes_abaixo_inpc_pct"
INDICADOR_PISO_MEDIO = "piso_salarial_medio"
INDICADOR_PISO_MEDIANO = "piso_salarial_mediano"

MESES = {
    "janeiro": "01", "fevereiro": "02", "março": "03", "abril": "04", "maio": "05", "junho": "06",
    "julho": "07", "agosto": "08", "setembro": "09", "outubro": "10", "novembro": "11", "dezembro": "12",
}

PADRAO_REFERENCIA = re.compile(r"Resultados at[ée] (\w+) de (\d{4})")
PADRAO_ACIMA = re.compile(r"data-base \w+ registrou reajustes acima da varia[çc][ãa]o do INPC-IBGE em (\d+,\d+)% dos (\d+) acordos")
# "abaixo" NÃO é publicado em toda edição — algumas edições (ex. nº 71) não
# têm essa frase isolada no texto corrido naquele mês (só dentro do gráfico,
# não extraível com confiança). Por isso é tratado como campo opcional, não
# obrigatório — ver `transformar()`.
PADRAO_ABAIXO = re.compile(r"percentual de resultados abaixo da varia[çc][ãa]o do INPC atingiu (\d+,\d+)%")
# "o valor médio" às vezes vem como "o valor médio dos pisos" (ex. edição 71)
# — confirmado real variação de redação entre edições, não erro de regex.
PADRAO_PISOS = re.compile(
    r"Nas [úu]ltimas 12 datas-bases, o valor m[ée]dio(?: dos pisos)? foi de R\$ (\d{1,3}(?:\.\d{3})*), e\s*\n?\s*o\s*\n?\s*mediano, de R\$ (\d{1,3}(?:\.\d{3})*)"
)


def _numero_br(texto: str) -> float:
    return float(texto.replace(".", "").replace(",", "."))


def _baixar_pdf() -> bytes:
    registros = buscar_ultimo_raw(SCRIPT_ORIGEM)
    if not registros:
        raise RuntimeError(f"Nenhum RAW com status=sucesso encontrado para {SCRIPT_ORIGEM}")
    return baixar_objeto_storage(registros[0]["storage_path"])


def transformar() -> dict[str, int]:
    texto = extrair_texto_pdf(_baixar_pdf())

    m_ref = PADRAO_REFERENCIA.search(texto)
    if not m_ref:
        raise RuntimeError(
            "Padrão 'Resultados até <mês> de <ano>' não encontrado — sem isso não dá para datar "
            "nenhum dos 4 indicadores deste boletim; o formato pode ter mudado."
        )
    mes_nome, ano = m_ref.groups()
    data_referencia = f"{ano}-{MESES[mes_nome.lower()]}-01"

    resultado: dict[str, int] = {}

    m_acima = PADRAO_ACIMA.search(texto)
    if m_acima:
        pct_acima = _numero_br(m_acima.group(1))
        registrar_serie(INDICADOR_REAJUSTE_ACIMA, [{"data_referencia": data_referencia, "valor": pct_acima}])
        resultado[INDICADOR_REAJUSTE_ACIMA] = 1

    m_abaixo = PADRAO_ABAIXO.search(texto)
    if m_abaixo:
        pct_abaixo = _numero_br(m_abaixo.group(1))
        registrar_serie(INDICADOR_REAJUSTE_ABAIXO, [{"data_referencia": data_referencia, "valor": pct_abaixo}])
        resultado[INDICADOR_REAJUSTE_ABAIXO] = 1
    else:
        print(f"  aviso: percentual 'abaixo do INPC' não está no texto corrido desta edição ({data_referencia}) — pulado, não inventado.")

    m_pisos = PADRAO_PISOS.search(texto)
    if m_pisos:
        piso_medio = _numero_br(m_pisos.group(1))
        piso_mediano = _numero_br(m_pisos.group(2))
        registrar_serie(INDICADOR_PISO_MEDIO, [{"data_referencia": data_referencia, "valor": piso_medio}])
        registrar_serie(INDICADOR_PISO_MEDIANO, [{"data_referencia": data_referencia, "valor": piso_mediano}])
        resultado[INDICADOR_PISO_MEDIO] = 1
        resultado[INDICADOR_PISO_MEDIANO] = 1

    if not resultado:
        raise RuntimeError(
            "Nenhum dos 4 padrões de valor bateu neste boletim (só a referência de data foi "
            "encontrada) — o formato pode ter mudado; não publicar nada."
        )
    return resultado


if __name__ == "__main__":
    for indicador_id, n in transformar().items():
        print(f"Transformação concluída: {n} ponto gravado em indicadores_serie ({indicador_id}).")
