"""Coleta bruta do INPC (variação mensal) via API pública do BCB/SGS, série 188
— substitui `coleta_inpc_sidra.py` como fonte do indicador `inpc`. Mesmo
raciocínio completo documentado em `coleta_ipca_bcb.py` (leia aquele arquivo
primeiro) — este script só troca o código da série SGS.

Testado nesta sessão (2026-10-26): os valores da série 188 batem ponto a
ponto com o `inpc` já publicado na plataforma via SIDRA, para o período em
comum (conferido para 2024) — mesma métrica, fonte com histórico mais longo.
"""

import json
import sys
import time
import urllib.error
import urllib.request
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from supabase_raw import registrar_coleta

CODIGO_SGS = 188
DATA_INICIO = date(1994, 7, 1)  # início do Plano Real
DESTINO = Path(__file__).resolve().parents[3] / "data" / "raw" / "bcb_sgs"


def _blocos_de_decada(inicio: date, fim: date):
    ano = inicio.year
    while ano <= fim.year:
        ano_fim_bloco = min(ano + 9, fim.year)
        yield (
            date(ano, 1, 1) if ano != inicio.year else inicio,
            date(ano_fim_bloco, 12, 31) if ano_fim_bloco != fim.year else fim,
        )
        ano += 10


def _buscar_bloco(data_inicial: date, data_final: date, tentativas: int = 3) -> list:
    url = (
        f"https://api.bcb.gov.br/dados/serie/bcdata.sgs.{CODIGO_SGS}/dados"
        f"?formato=json&dataInicial={data_inicial.strftime('%d/%m/%Y')}"
        f"&dataFinal={data_final.strftime('%d/%m/%Y')}"
    )
    ultimo_erro = None
    for tentativa in range(1, tentativas + 1):
        try:
            with urllib.request.urlopen(url, timeout=60) as resposta:
                return json.loads(resposta.read().decode("utf-8"))
        except (urllib.error.URLError, json.JSONDecodeError) as erro:
            ultimo_erro = erro
            if tentativa < tentativas:
                time.sleep(2 * tentativa)
    print(f"Aviso: bloco {data_inicial}–{data_final} falhou após {tentativas} tentativas: {ultimo_erro}", file=sys.stderr)
    return []


def coletar() -> Path:
    hoje = date.today()
    combinado = []
    for data_inicial, data_final in _blocos_de_decada(DATA_INICIO, hoje):
        combinado.extend(_buscar_bloco(data_inicial, data_final))
        time.sleep(0.5)

    DESTINO.mkdir(parents=True, exist_ok=True)
    from datetime import datetime, timezone
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    arquivo = DESTINO / f"inpc_sgs_{CODIGO_SGS}_{timestamp}.json"
    arquivo.write_text(json.dumps(combinado, ensure_ascii=False, indent=2), encoding="utf-8")
    return arquivo


if __name__ == "__main__":
    caminho = coletar()
    print(f"Coleta concluída: {caminho}")
    registrar_coleta(fonte=DESTINO.name, arquivo=caminho, script=__file__)
