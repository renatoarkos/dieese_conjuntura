"""Coleta bruta do IPCA (variação mensal) via API pública do BCB/SGS, série 433
— substitui `coleta_ipca_sidra.py` como fonte do indicador `ipca` (ver
pipelines/curated/transformar_ipca_sidra.py e
research/notas/VIABILIDADE_DIMENSAO_POLITICA.md).

===============================================================================
POR QUE TROCAR DE FONTE (SIDRA → BCB/SGS) PARA O MESMO INDICADOR
===============================================================================
`coleta_ipca_sidra.py` usa a tabela SIDRA 7060, que por desenho do IBGE só
cobre o período a partir de jan/2020 (pesos da POF 2017-2018, vigentes desde
essa data — ver docstring daquele script). Isso deixava o indicador `ipca` da
plataforma artificialmente curto (só ~80 pontos), insuficiente para qualquer
análise de série longa (ex. a "dimensão política", que precisa do IPCA desde
o Plano Real, 1994).

Testado nesta sessão (2026-10-26): a série BCB/SGS 433 ("IPCA — Variação
mensal") tem dado real desde pelo menos jul/1994 e os valores batem
exatamente com os já publicados pela plataforma via SIDRA para o período em
comum (conferido ponto a ponto para 2024) — é a MESMA métrica (variação
mensal do IPCA, calculada e publicada oficialmente pelo IBGE; o BCB só
replica a série, como já faz para o IGP-M, ver `coleta_igpm_bcb.py`), só com
histórico mais longo disponível pela via do BCB.

`coleta_ipca_sidra.py` continua no repositório, não apagado — só deixa de
ser a fonte usada pela transformação (mesmo tratamento dado a esquemas
obsoletos neste projeto, ex. migração 0007/ADR 0008).

===============================================================================
POR QUE A COLETA É FEITA EM BLOCOS, NÃO NUMA CHAMADA SÓ
===============================================================================
Testado nesta sessão: pedir a série 433 inteira (sem filtro de data, ou com
um intervalo muito longo, ex. 1980-2026) falha com "Requisição inválida" do
lado do BCB — mas o MESMO tipo de pedido, em intervalos de ~10 anos, funciona
normalmente. O comportamento não foi 100% consistente nos testes (às vezes um
intervalo pequeno também falhou, de forma aparentemente intermitente) — por
isso este script tenta cada bloco algumas vezes antes de desistir dele,
seguindo em frente para o próximo bloco em vez de travar a coleta inteira por
causa de uma falha pontual numa década.

===============================================================================
O QUE ESTE SCRIPT FAZ, PASSO A PASSO
===============================================================================
1. Para cada bloco de ~10 anos entre 01/07/1994 (início do Plano Real) e hoje,
   busca a série SGS 433 nesse intervalo, tentando até 3 vezes por bloco.
2. Junta os blocos numa lista única, em ordem cronológica.
3. Salva o resultado combinado em `data/raw/bcb_sgs/` (mesmo padrão dos
   demais scripts "..._bcb.py" deste projeto).
4. Registra a coleta no Supabase.

Este script NÃO transforma o dado — grava a resposta bruta da API, só
combinando os blocos (que são só uma forma técnica de pedir o mesmo dado em
partes, não uma transformação de conteúdo).
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

CODIGO_SGS = 433
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
    arquivo = DESTINO / f"ipca_sgs_{CODIGO_SGS}_{timestamp}.json"
    arquivo.write_text(json.dumps(combinado, ensure_ascii=False, indent=2), encoding="utf-8")
    return arquivo


if __name__ == "__main__":
    caminho = coletar()
    print(f"Coleta concluída: {caminho}")
    registrar_coleta(fonte=DESTINO.name, arquivo=caminho, script=__file__)
