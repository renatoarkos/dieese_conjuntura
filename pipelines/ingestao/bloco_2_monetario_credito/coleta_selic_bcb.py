"""Coleta bruta da Taxa Selic via API pública do BCB/SGS.

Piloto técnico controlado — ver docs/08-decisoes-adr/0002-expansao-piloto-por-blocos.md
Fonte confirmada em: docs/04-fontes/bcb.md — achado do Lote Piloto 01 + validação de dados
2026-09-22 (comparação direta com a aba T14 do material do DIEESE, 122 valores mensais).

===============================================================================
COMO FUNCIONA A API DO BCB/SGS (vale para todos os scripts "..._bcb.py" que
usam o Sistema Gerenciador de Séries Temporais — SGS)
===============================================================================
O SGS é o sistema de séries temporais do Banco Central. Cada série (um
indicador específico, como "Selic acumulada no mês" ou "câmbio venda mensal")
tem um CÓDIGO NUMÉRICO fixo, e a URL de consulta é sempre:

    https://api.bcb.gov.br/dados/serie/bcdata.sgs.{codigo}/dados?formato=json

Para achar o código de uma série nova, procure no site do BCB
(www3.bcb.gov.br/sgspub) pelo nome do indicador — a busca mostra o código.
A resposta é uma lista de objetos `{"data": "DD/MM/AAAA", "valor": "..."}`,
um por observação, em ordem cronológica, sem cabeçalho.

===============================================================================
POR QUE DUAS SÉRIES PARA UM SÓ INDICADOR
===============================================================================
A série de Selic usada pelo material do DIEESE é uma COMPOSIÇÃO de duas séries
SGS diferentes ao longo do tempo (confirmado por comparação ponto a ponto com
122 valores mensais do material original — ver docs/04-fontes/bcb.md):
  - SGS 4189 ("Selic acumulada no mês, anualizada base 252"): nov/2015 a jul/2024.
  - SGS 432 ("Meta Selic definida pelo Copom"): ago/2024 em diante.

Este script coleta as DUAS séries completas, cada uma do seu início histórico,
SEM aplicar a regra de corte/troca entre elas — decidir onde cortar uma série
e começar a outra é uma transformação, e transformação é trabalho da camada
STAGING, nunca da RAW (ver CLAUDE.md, seção DADOS).

===============================================================================
POR QUE ESTE SCRIPT TEM RETRY E PAGINAÇÃO (diferente dos demais scripts BCB
deste bloco)
===============================================================================
As duas séries deste indicador somam décadas de histórico (diário e mensal),
e a API do BCB se comportou de forma instável sob chamadas sucessivas nesta
rodada:
  - pedidos sem filtro de data para séries longas às vezes retornam HTTP 406
    — comportamento não documentado oficialmente, descoberto testando na
    prática;
  - mesmo pedidos válidos ocasionalmente vêm com corpo vazio ou erro
    transitório, e funcionam ao repetir a mesma URL pouco depois.

Por isso, para cada série, este script:
  1. tenta buscar o histórico inteiro numa única chamada (mais simples e
     rápido quando funciona);
  2. se isso falhar, pagina em janelas de até 10 anos — limite documentado da
     própria API do BCB desde 26/03/2025 — e concatena os resultados;
  3. em cada chamada HTTP individual, repete algumas vezes com espera
     crescente antes de desistir, porque a instabilidade observada costuma
     ser passageira.

===============================================================================
O QUE ESTE SCRIPT FAZ, PASSO A PASSO
===============================================================================
1. Para cada série em `INICIO_SERIE` (código → data de início), busca o
   histórico completo, com retry e paginação quando necessário
   (`_coletar_serie`, que usa `_buscar_url` por baixo).
2. Salva cada série num arquivo separado em `data/raw/bcb_sgs/`, com o
   código da série e um timestamp da coleta no nome (`_salvar_raw`).
3. Registra cada arquivo no Supabase (Storage + `raw_ingestoes`).

Este script NÃO transforma o dado nem decide qual série vale para qual mês —
grava as duas séries-fonte completas, exatamente como a API as devolve.
"""

import json
import sys
import time
import urllib.error
import urllib.request
from datetime import date, datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from supabase_raw import registrar_coleta

# Data de início de cada série no BCB/SGS (confirmada no Discovery de Fontes).
INICIO_SERIE = {
    "4189": date(1986, 8, 1),
    "432": date(1999, 3, 5),
}

DESTINO = Path(__file__).resolve().parents[3] / "data" / "raw" / "bcb_sgs"


# ------------------------------------------------------------------------
# PASSO 1 — buscar uma URL na API, com repetição em caso de falha
# ------------------------------------------------------------------------
def _buscar_url(url: str, tentativas: int = 3) -> list[dict]:
    """Faz a requisição HTTP e devolve o JSON já decodificado.

    A API do BCB é intermitentemente instável sob chamadas sucessivas —
    algumas requisições retornam corpo vazio ou HTTP 406 mesmo quando a
    mesma URL funciona isoladamente (observado empiricamente nesta rodada).
    Por isso repete a chamada `tentativas` vezes, com espera crescente
    (2s, 4s, 6s...) entre elas, antes de desistir e propagar o erro.
    """
    ultimo_erro: Exception | None = None
    for tentativa in range(1, tentativas + 1):
        try:
            with urllib.request.urlopen(url, timeout=60) as resposta:
                corpo = resposta.read().decode("utf-8")
            return json.loads(corpo)
        except (urllib.error.HTTPError, json.JSONDecodeError) as erro:
            ultimo_erro = erro
            time.sleep(2 * tentativa)
    raise RuntimeError(f"Falha após {tentativas} tentativas: {url}") from ultimo_erro


# ------------------------------------------------------------------------
# PASSO 2 — buscar o histórico completo de uma série (paginando se preciso)
# ------------------------------------------------------------------------
def _coletar_serie(codigo: str, inicio: date) -> list[dict]:
    """Busca o histórico completo da série `codigo`, desde `inicio`.

    Primeiro tenta pedir a série inteira numa única chamada, sem filtro de
    data. A API do BCB rejeita (HTTP 406) esse tipo de pedido para séries
    longas (ex.: diárias desde 1999) — comportamento não documentado
    oficialmente, descoberto por teste real nesta rodada. Quando isso
    acontece, o contorno é paginar em janelas de até 10 anos (limite
    documentado da API desde 26/03/2025) e concatenar os resultados, sem
    alterar nenhum valor.
    """
    base = f"https://api.bcb.gov.br/dados/serie/bcdata.sgs.{codigo}/dados?formato=json"
    try:
        return _buscar_url(base, tentativas=1)
    except RuntimeError:
        pass  # série longa demais para pedido sem filtro — pagina abaixo

    hoje = date.today()
    pontos: list[dict] = []
    janela_inicio = inicio
    while janela_inicio <= hoje:
        janela_fim = min(date(janela_inicio.year + 10, janela_inicio.month, 1), hoje)
        url = (
            f"{base}&dataInicial={janela_inicio.strftime('%d/%m/%Y')}"
            f"&dataFinal={janela_fim.strftime('%d/%m/%Y')}"
        )
        pontos.extend(_buscar_url(url))
        janela_inicio = janela_fim.replace(day=1)
        if janela_inicio.month == 12:
            janela_inicio = janela_inicio.replace(year=janela_inicio.year + 1, month=1, day=2)
        else:
            janela_inicio = janela_inicio.replace(month=janela_inicio.month + 1, day=2)
    return pontos


# ------------------------------------------------------------------------
# PASSO 3 — salvar a resposta bruta de uma série em disco
# ------------------------------------------------------------------------
def _salvar_raw(codigo: str, dados: list[dict], timestamp: str) -> Path:
    """Grava a série `codigo` como JSON formatado (só para leitura humana —
    não é transformação de dado). O nome do arquivo leva o código da série
    e um timestamp UTC da coleta, porque o BCB pode revisar valores
    publicados e cada execução é uma nova fotografia da série — nunca
    sobrescrevemos a coleta anterior.
    """
    arquivo = DESTINO / f"selic_sgs_{codigo}_{timestamp}.json"
    arquivo.write_text(json.dumps(dados, ensure_ascii=False, indent=2), encoding="utf-8")
    return arquivo


# ------------------------------------------------------------------------
# Orquestração: repete os passos acima para cada série de INICIO_SERIE
# ------------------------------------------------------------------------
def coletar() -> list[Path]:
    DESTINO.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

    arquivos = []
    for codigo, inicio in INICIO_SERIE.items():
        dados = _coletar_serie(codigo, inicio)
        arquivos.append(_salvar_raw(codigo, dados, timestamp))
    return arquivos


if __name__ == "__main__":
    for caminho in coletar():
        print(f"Coleta concluída: {caminho}")
        registrar_coleta(fonte=DESTINO.name, arquivo=caminho, script=__file__)
