"""Transformação CURATED do ICT-DIEESE (ADR 0005) — extrai o valor do índice
de dentro do texto do boletim PDF em `pipelines/ingestao/bloco_4_mercado_trabalho/
coleta_ict_dieese.py`.

===============================================================================
PRIMEIRO INDICADOR DO CATÁLOGO EXTRAÍDO DE PDF (STAGING embutido na transformação)
===============================================================================
Diferente dos demais indicadores de `pipelines/curated/` (que leem JSON/CSV já
estruturado), este lê um PDF de layout majoritariamente gráfico. O boletim
confirmadamente tem camada de texto real (`pdftotext`, não é imagem escaneada
— ver docstring do script de coleta), mas o modo `-layout` intercala texto de
elementos visualmente sobrepostos (ex. um rótulo de gráfico cai no meio de uma
frase de texto corrido) de forma imprevisível entre edições. Por isso este
script extrai só UMA frase, a mais estável e isolada de todas as testadas
(fora da área dos gráficos): "...ficou em X,XX no (primeiro|segundo|terceiro|
quarto) trimestre de AAAA." — testado e confirmado em 2 edições reais (020 e
021) sem variação de formato. As quebras de sub-dimensão (Inserção
Ocupacional/Desocupação/Rendimento) foram tentadas e descartadas: a frase que
as contém é cortada no meio por um rótulo de gráfico sobreposto
("...dimensão Inserção[quebra]Ocupacional (de 0,62 para 0,57)..."),
inviabilizando um regex confiável — publicar um valor errado aqui seria pior
que não publicar.

===============================================================================
O QUE ESTE SCRIPT FAZ, PASSO A PASSO
===============================================================================
1. Baixa o PDF mais recente já coletado (Storage), via `buscar_ultimo_raw`.
2. Extrai o texto (`extrair_texto_pdf`, poppler/`pdftotext`).
3. Aplica o regex sobre a frase-âncora e converte trimestre+ano em
   `data_referencia` (primeiro dia do trimestre).
4. Grava 1 ponto em `indicadores_serie`.
"""

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from curated_supabase import baixar_objeto_storage, buscar_ultimo_raw, extrair_texto_pdf, registrar_serie

SCRIPT_ORIGEM = "pipelines/ingestao/bloco_4_mercado_trabalho/coleta_ict_dieese.py"
INDICADOR_ID = "ict_dieese"

TRIMESTRE_PARA_MES = {"primeiro": "01", "segundo": "04", "terceiro": "07", "quarto": "10"}

PADRAO = re.compile(r"ficou em (\d+,\d+) no (primeiro|segundo|terceiro|quarto) trimestre de (\d{4})")


def _baixar_pdf() -> bytes:
    registros = buscar_ultimo_raw(SCRIPT_ORIGEM)
    if not registros:
        raise RuntimeError(f"Nenhum RAW com status=sucesso encontrado para {SCRIPT_ORIGEM}")
    return baixar_objeto_storage(registros[0]["storage_path"])


def transformar() -> int:
    texto = extrair_texto_pdf(_baixar_pdf())
    m = PADRAO.search(texto)
    if not m:
        raise RuntimeError(
            "Padrão 'ficou em X,XX no <trimestre> trimestre de AAAA' não encontrado no texto do "
            "boletim ICT mais recente — o formato do boletim pode ter mudado; não publicar valor adivinhado."
        )
    valor_texto, trimestre, ano = m.groups()
    valor = float(valor_texto.replace(",", "."))
    data_referencia = f"{ano}-{TRIMESTRE_PARA_MES[trimestre]}-01"
    registrar_serie(INDICADOR_ID, [{"data_referencia": data_referencia, "valor": valor}])
    return 1


if __name__ == "__main__":
    n = transformar()
    print(f"Transformação concluída: {n} ponto gravado em indicadores_serie ({INDICADOR_ID}).")
