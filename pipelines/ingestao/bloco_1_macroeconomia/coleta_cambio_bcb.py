"""Coleta bruta da taxa de câmbio (Livre — Dólar americano, venda) via API
pública do BCB/SGS.

Piloto técnico controlado — ver docs/08-decisoes-adr/0002-expansao-piloto-por-blocos.md
Fonte confirmada em: docs/04-fontes/bcb.md

===============================================================================
COMO FUNCIONA A API DO BCB/SGS (vale para todos os scripts "..._bcb.py" que
usam o Sistema Gerenciador de Séries Temporais — SGS)
===============================================================================
O SGS é o sistema de séries temporais do Banco Central. Cada série (um
indicador específico, como "câmbio venda mensal" ou "Selic diária") tem um
CÓDIGO NUMÉRICO fixo, e a URL de consulta é sempre:

    https://api.bcb.gov.br/dados/serie/bcdata.sgs.{codigo}/dados?formato=json

Para achar o código de uma série nova, procure no site do BCB
(www3.bcb.gov.br/sgspub) pelo nome do indicador — a busca mostra o código.
A resposta é uma lista de objetos `{"data": "DD/MM/AAAA", "valor": "..."}`,
um por observação, sempre em ordem cronológica — sem cabeçalho (diferente do
SIDRA, que tem um item de cabeçalho no início da lista).

===============================================================================
POR QUE DUAS SÉRIES PARA UM SÓ INDICADOR
===============================================================================
O material do DIEESE cita "câmbio" sem deixar claro qual série exata do BCB
usa. O Discovery de Fontes encontrou duas séries candidatas — SGS 3694 (média
anual) e SGS 3698 (média mensal) — e, como não dava para confirmar qual delas
(ou se as duas) o DIEESE usa, este script baixa AMBAS. Decidir qual usar (ou
descartar uma) é uma transformação/curadoria que pertence à camada STAGING,
não a este script — aqui só coletamos o que existe, sem escolher por conta
própria.

===============================================================================
O QUE ESTE SCRIPT FAZ, PASSO A PASSO
===============================================================================
1. Para cada série em `SERIES` (código → URL), busca os dados na API
   (`_buscar_dados`).
2. Salva cada série num arquivo separado em `data/raw/bcb_sgs/`
   (`_salvar_raw`) — mesmo padrão de nome de arquivo que os demais scripts
   BCB/SGS deste piloto, trocando só o prefixo do indicador.
3. Registra cada arquivo no Supabase (Storage + `raw_ingestoes`).

Este script NÃO transforma o dado nem escolhe entre as duas séries.
"""

import json
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from supabase_raw import registrar_coleta

# codigo da série SGS -> URL de consulta. Ver docs/04-fontes/bcb.md para o
# porquê de cada código ser candidato a esta série.
SERIES = {
    "3694": "https://api.bcb.gov.br/dados/serie/bcdata.sgs.3694/dados?formato=json",
    "3698": "https://api.bcb.gov.br/dados/serie/bcdata.sgs.3698/dados?formato=json",
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
    (para diferenciar 3694 de 3698) e um timestamp UTC, porque o BCB pode
    revisar valores publicados e cada execução é uma nova fotografia da
    série — nunca sobrescrevemos a coleta anterior.
    """
    arquivo = DESTINO / f"cambio_sgs_{codigo}_{timestamp}.json"
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
