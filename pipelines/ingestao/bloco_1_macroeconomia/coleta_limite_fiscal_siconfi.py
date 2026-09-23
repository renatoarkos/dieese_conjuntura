"""Coleta bruta do limite fiscal (prudencial e máximo) de despesa com pessoal, por Unidade
da Federação, via API pública do SICONFI (Tesouro Nacional).

Piloto técnico controlado — ver docs/08-decisoes-adr/0002-expansao-piloto-por-blocos.md
Fonte confirmada em: docs/04-fontes/mdic-tesouro.md (SICONFI, Relatório de Gestão Fiscal)

===============================================================================
COMO FUNCIONA A API DO SICONFI
===============================================================================
O SICONFI (Sistema de Informações Contábeis e Fiscais do Setor Público
Brasileiro), mantido pela Secretaria do Tesouro Nacional, expõe uma API REST
construída sobre Oracle ORDS (Oracle REST Data Services) — por isso a URL
base tem o formato `apidatalake.tesouro.gov.br/ords/siconfi/...`, típico
desse tipo de serviço. Não exige chave nem autenticação para consulta.

O endpoint usado aqui devolve o Relatório de Gestão Fiscal (RGF) — o
demonstrativo, previsto na Lei de Responsabilidade Fiscal, que traz a despesa
com pessoal de cada ente da federação e os limites da LRF (máximo,
prudencial = 0,95×limite máximo, alerta = 0,90×limite máximo):

    https://apidatalake.tesouro.gov.br/ords/siconfi/tt/rgf
        ?an_exercicio={ano}&nr_periodo={periodo}&co_tipo_demonstrativo=RGF
        &co_poder=E&co_esfera=E&in_periodicidade=Q&id_ente={codigo_ibge_uf}

  - `an_exercicio` / `nr_periodo` → ano e quadrimestre do exercício fiscal
                                     (o RGF é quadrimestral: `in_periodicidade=Q`).
  - `co_tipo_demonstrativo=RGF`   → fixa o tipo de relatório (existem outros,
                                     como o RREO, fora do escopo deste script).
  - `co_poder=E`, `co_esfera=E`   → filtram Poder Executivo, esfera Estadual
                                     (o mesmo relatório existe também para
                                     outros poderes/esferas).
  - `id_ente`                     → o código IBGE do ente consultado. AQUI
                                     ESTÁ O PONTO CENTRAL DESTE SCRIPT: a API
                                     devolve dados de UM ente por chamada —
                                     não existe um parâmetro "todas as UFs de
                                     uma vez". Por isso o script itera sobre
                                     as 27 Unidades da Federação e faz uma
                                     requisição por UF (ver `CODIGOS_UF`
                                     abaixo e a função `coletar`).

A resposta de cada chamada é um JSON com uma lista de linhas do
demonstrativo (uma por conta contábil, ex. "DESPESA TOTAL COM PESSOAL - DTP",
"LIMITE MÁXIMO (IX)", "LIMITE PRUDENCIAL (X)") para aquele ente e período.

===============================================================================
O QUE ESTE SCRIPT FAZ, PASSO A PASSO
===============================================================================
1. Define os códigos IBGE das 27 Unidades da Federação (`CODIGOS_UF`) e o
   exercício/quadrimestre a consultar (`AN_EXERCICIO`, `NR_PERIODO`).
2. Para cada UF, monta a URL de consulta (`_url`), busca os dados na API e
   salva a resposta dessa UF, sem alterar nada, em `data/raw/siconfi/`, num
   arquivo próprio por UF (função `coletar`) — mesmo timestamp de coleta
   para todas as 27 chamadas, para deixar claro que pertencem à mesma
   "rodada" de coleta.
3. Registra cada arquivo no Supabase — Storage + linha em `raw_ingestoes`
   (`registrar_coleta`, importado de `pipelines/supabase_raw.py`), uma
   chamada por UF.

Este script NÃO transforma o dado — grava a resposta de cada UF separadamente
e exatamente como recebida, respeitando o princípio de que a camada RAW nunca
deve ser editada manualmente ou pré-processada (ver CLAUDE.md, seção DADOS).
Consolidar as 27 respostas numa única tabela, comparar limites entre estados
ou qualquer outra conta é trabalho da camada STAGING, feito depois, a partir
dos arquivos que este script grava — nunca aqui.
"""

import json
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from supabase_raw import registrar_coleta

# Códigos IBGE das 27 Unidades da Federação (tabela de referência padrão do IBGE).
CODIGOS_UF = {
    "RO": 11, "AC": 12, "AM": 13, "RR": 14, "PA": 15, "AP": 16, "TO": 17,
    "MA": 21, "PI": 22, "CE": 23, "RN": 24, "PB": 25, "PE": 26, "AL": 27, "SE": 28, "BA": 29,
    "MG": 31, "ES": 32, "RJ": 33, "SP": 35,
    "PR": 41, "SC": 42, "RS": 43,
    "MS": 50, "MT": 51, "GO": 52, "DF": 53,
}

AN_EXERCICIO = 2026
NR_PERIODO = 1  # 1º quadrimestre — período mais recente com dados confirmados nesta rodada

DESTINO = Path(__file__).resolve().parents[3] / "data" / "raw" / "siconfi"


# ------------------------------------------------------------------------
# PASSO 1 — montar a URL de consulta do RGF para uma UF
# ------------------------------------------------------------------------
def _url(id_ente: int) -> str:
    """Monta a URL do endpoint RGF do SICONFI para um único ente (`id_ente` é
    o código IBGE da UF). Fixa Poder Executivo estadual (`co_poder=E`,
    `co_esfera=E`) e periodicidade quadrimestral (`in_periodicidade=Q`), que
    são os parâmetros confirmados em docs/04-fontes/mdic-tesouro.md.
    """
    return (
        "https://apidatalake.tesouro.gov.br/ords/siconfi/tt/rgf"
        f"?an_exercicio={AN_EXERCICIO}&nr_periodo={NR_PERIODO}"
        "&co_tipo_demonstrativo=RGF&co_poder=E&co_esfera=E&in_periodicidade=Q"
        f"&id_ente={id_ente}"
    )


# ------------------------------------------------------------------------
# PASSO 2 — buscar os dados de uma UF na API
# ------------------------------------------------------------------------
def _buscar_dados(id_ente: int) -> dict:
    """Faz a requisição HTTP para uma UF e devolve o JSON já decodificado.
    `timeout=60` evita que o script fique parado indefinidamente se a API do
    SICONFI não responder — nesse caso ele falha de forma visível (exceção),
    em vez de travar silenciosamente no meio do loop de 27 UFs.
    """
    with urllib.request.urlopen(_url(id_ente), timeout=60) as resposta:
        return json.loads(resposta.read().decode("utf-8"))


# ------------------------------------------------------------------------
# PASSO 3 — salvar a resposta bruta de uma UF em disco
# ------------------------------------------------------------------------
def _salvar_raw(uf: str, dados: dict, timestamp: str) -> Path:
    """Grava a resposta da UF `uf` como JSON formatado (indent=2), só para
    leitura humana — não é transformação de dado. O nome do arquivo leva a
    sigla da UF (um arquivo por ente, nunca um arquivo consolidado — ver
    docstring do módulo) e um timestamp UTC compartilhado por toda a rodada
    de 27 chamadas, para identificar que pertencem à mesma coleta.
    """
    arquivo = DESTINO / f"limite_fiscal_{uf}_{AN_EXERCICIO}Q{NR_PERIODO}_{timestamp}.json"
    arquivo.write_text(json.dumps(dados, ensure_ascii=False, indent=2), encoding="utf-8")
    return arquivo


# ------------------------------------------------------------------------
# Orquestração: repete os passos acima para cada uma das 27 UFs
# ------------------------------------------------------------------------
def coletar() -> list[Path]:
    DESTINO.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

    arquivos = []
    for uf, id_ente in CODIGOS_UF.items():
        dados = _buscar_dados(id_ente)
        arquivos.append(_salvar_raw(uf, dados, timestamp))
    return arquivos


if __name__ == "__main__":
    arquivos = coletar()
    print(f"Coleta concluída: {len(arquivos)} arquivos (1 por UF) em {DESTINO}")
    for caminho in arquivos:
        registrar_coleta(fonte=DESTINO.name, arquivo=caminho, script=__file__)
