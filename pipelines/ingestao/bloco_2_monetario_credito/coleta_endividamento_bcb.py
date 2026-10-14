"""Coleta bruta do endividamento e comprometimento de renda das famílias com o
Sistema Financeiro Nacional (família de séries RNDBF) via API pública do
BCB/SGS.

Piloto técnico controlado — ver docs/08-decisoes-adr/0002-expansao-piloto-por-blocos.md
Fonte confirmada em: docs/04-fontes/bcb.md — Lote 06a.

===============================================================================
COMO FUNCIONA A API DO BCB/SGS (vale para todos os scripts "..._bcb.py" que
usam o Sistema Gerenciador de Séries Temporais — SGS)
===============================================================================
O SGS é o sistema de séries temporais do Banco Central. Cada série tem um
CÓDIGO NUMÉRICO fixo, e a URL de consulta é sempre:

    https://api.bcb.gov.br/dados/serie/bcdata.sgs.{codigo}/dados?formato=json

A resposta é uma lista de objetos `{"data": "DD/MM/AAAA", "valor": "..."}`, um
por observação, em ordem cronológica, sem cabeçalho.

===============================================================================
POR QUE CINCO SÉRIES PARA UM SÓ INDICADOR
===============================================================================
Este script cobre a parte BCB do indicador "endividamento familiar" do
material do DIEESE — a parte PEIC/FecomercioSP é coletada à parte, em
`coleta_endividamento_peic_fecomercio.py`, neste mesmo bloco.

O material do DIEESE cita esse indicador como "Tabela 27". **QF10 resolvida
em 2026-10-14** por leitura direta da aba `T15` da planilha interna mais
recente do DIEESE (`materiais/originais/dieese/`, leitura somente-leitura):
a própria aba tem uma linha "SGS" expondo os 4 códigos exatos que compõem a
Tabela 27 — 29037 (Endividamento — Total), 29038 (Endividamento — sem
financiamento imobiliário), 29034 (Comprometimento de renda, dessazonalizado
— Total) e 29035 (Comprometimento de renda, dessazonalizado — sem
financiamento imobiliário). 29265 (comprometimento de renda, SEM ajuste
sazonal) não faz parte da Tabela 27 — é mantido aqui como indicador
complementar legítimo (dado real do BCB, só não é o que a Tabela 27 mostra),
não como candidato ambíguo.

===============================================================================
O QUE ESTE SCRIPT FAZ, PASSO A PASSO
===============================================================================
1. Para cada série em `SERIES` (código → URL), busca os dados na API
   (`_buscar_dados`).
2. Salva cada série num arquivo separado em `data/raw/bcb_sgs/`, com o código
   da série e um timestamp da coleta no nome (`_salvar_raw`).
3. Registra cada arquivo no Supabase (Storage + `raw_ingestoes`).

Este script NÃO transforma o dado nem escolhe qual série representa a
"Tabela 27" do DIEESE.
"""

import json
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from supabase_raw import registrar_coleta

# codigo da série SGS -> URL de consulta. Ver docs/04-fontes/bcb.md para o
# nome oficial completo de cada série e o histórico da ambiguidade com a
# "Tabela 27" do material do DIEESE.
SERIES = {
    "29034": "https://api.bcb.gov.br/dados/serie/bcdata.sgs.29034/dados?formato=json",  # Comprometimento de renda, dessazonalizado, Total (Tabela 27)
    "29035": "https://api.bcb.gov.br/dados/serie/bcdata.sgs.29035/dados?formato=json",  # Comprometimento de renda, dessazonalizado, sem financiamento imobiliário (Tabela 27)
    "29265": "https://api.bcb.gov.br/dados/serie/bcdata.sgs.29265/dados?formato=json",  # Comprometimento de renda, SEM ajuste sazonal (complementar, não é Tabela 27)
    "29037": "https://api.bcb.gov.br/dados/serie/bcdata.sgs.29037/dados?formato=json",  # Endividamento das famílias, Total (Tabela 27)
    "29038": "https://api.bcb.gov.br/dados/serie/bcdata.sgs.29038/dados?formato=json",  # Endividamento das famílias, sem financiamento imobiliário (Tabela 27)
}

DESTINO = Path(__file__).resolve().parents[3] / "data" / "raw" / "bcb_sgs"


# ------------------------------------------------------------------------
# PASSO 1 — buscar uma série na API
# ------------------------------------------------------------------------
def _buscar_dados(url: str) -> list:
    """Faz a requisição HTTP e devolve o JSON já decodificado. `timeout=60`
    evita que o script fique parado indefinidamente se a API do BCB não
    responder — nesse caso ele falha de forma visível (exceção), em vez de
    travar silenciosamente.
    """
    with urllib.request.urlopen(url, timeout=60) as resposta:
        return json.loads(resposta.read().decode("utf-8"))


# ------------------------------------------------------------------------
# PASSO 2 — salvar a resposta bruta de uma série em disco
# ------------------------------------------------------------------------
def _salvar_raw(codigo: str, dados: list, timestamp: str) -> Path:
    """Grava a série `codigo` como JSON formatado (só para leitura humana —
    não é transformação de dado). O nome do arquivo leva o código da série
    (para diferenciar as 3 candidatas) e um timestamp UTC da coleta, porque
    o BCB pode revisar valores publicados e cada execução é uma nova
    fotografia da série — nunca sobrescrevemos a coleta anterior.
    """
    arquivo = DESTINO / f"endividamento_sgs_{codigo}_{timestamp}.json"
    arquivo.write_text(json.dumps(dados, ensure_ascii=False, indent=2), encoding="utf-8")
    return arquivo


# ------------------------------------------------------------------------
# Orquestração: repete os passos acima para cada série de SERIES
# ------------------------------------------------------------------------
def coletar() -> list[Path]:
    DESTINO.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

    arquivos = []
    for codigo, url in SERIES.items():
        dados = _buscar_dados(url)
        arquivos.append(_salvar_raw(codigo, dados, timestamp))
    return arquivos


if __name__ == "__main__":
    for caminho in coletar():
        print(f"Coleta concluída: {caminho}")
        registrar_coleta(fonte=DESTINO.name, arquivo=caminho, script=__file__)
