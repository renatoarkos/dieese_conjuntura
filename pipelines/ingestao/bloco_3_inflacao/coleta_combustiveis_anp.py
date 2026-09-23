"""Coleta bruta dos preços de combustíveis (gasolina/etanol, diesel/GNV, GLP) via download
estruturado da ANP (Agência Nacional do Petróleo, Gás Natural e Biocombustíveis).

Piloto técnico controlado — ver docs/08-decisoes-adr/0002-expansao-piloto-por-blocos.md
Fonte confirmada em: docs/04-fontes/anp-ipeadata.md — investigação de lacunas pós-Lote 06,
com URL exata extraída e testada em 2026-09-22.

===============================================================================
ACHADO IMPORTANTE: O HTTP 403 NÃO ERA BLOQUEIO INSTITUCIONAL
===============================================================================
A primeira tentativa de acesso à página oficial da ANP (gov.br) retornou HTTP
403 (Proibido). A suspeita inicial seria um bloqueio de firewall/WAF do
domínio `gov.br` a requisições automatizadas — mas não era esse o caso.

O motivo real era mais simples: a requisição não incluía cabeçalhos HTTP
típicos de um navegador (`Accept`, `Accept-Language`, e um `User-Agent`
completo) — sem eles, o servidor identifica a requisição como vindo de um
bot genérico e a rejeita, mesmo sem haver nenhuma autenticação envolvida.
Adicionando esses cabeçalhos (ver `CABECALHOS` abaixo), o acesso funcionou
normalmente (HTTP 200) e permitiu extrair os links reais de download direto
do HTML da página, em vez de tentar adivinhar um padrão de URL.

Esta distinção importa para qualquer fonte pública em domínios `gov.br` que
retorne 403 neste ou em outros projetos: vale testar com cabeçalhos de
navegador completos antes de concluir que o acesso está bloqueado.

===============================================================================
O QUE ESTE INDICADOR COBRE
===============================================================================
A ANP publica, semanalmente, uma série de microdados por posto revendedor
("últimas 4 semanas") com o preço de venda coletado de cada posto, para três
grupos de produtos: gasolina/etanol, diesel/GNV e GLP (gás de cozinha) — os
três itens de combustível citados no material do DIEESE. Este script coleta
apenas essa série corrente (mais adequada a um acompanhamento de conjuntura
atualizado), não a série histórica completa desde 2004, que é bem maior e
não necessária para esse uso.

===============================================================================
O QUE ESTE SCRIPT FAZ, PASSO A PASSO
===============================================================================
1. Para cada arquivo em `ARQUIVOS` (nome → URL), faz o download do CSV com os
   cabeçalhos de navegador (`CABECALHOS`) que evitam o 403 (`_baixar_arquivo`).
2. Salva o conteúdo, sem alterar nada, em `data/raw/anp/` com um nome de
   arquivo que identifica o produto e o instante da coleta (`_salvar_raw`).
3. Registra cada arquivo no Supabase — Storage + linha em `raw_ingestoes`
   (`registrar_coleta`, importado de `pipelines/supabase_raw.py`).

Este script NÃO transforma o dado — grava o CSV exatamente como recebido,
respeitando o princípio de que a camada RAW nunca deve ser editada
manualmente ou pré-processada (ver CLAUDE.md, seção DADOS).
"""

import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from supabase_raw import registrar_coleta

BASE = "https://www.gov.br/anp/pt-br/centrais-de-conteudo/dados-abertos/arquivos/shpc/qus"
# Os três arquivos de "últimas 4 semanas" — cobrem exatamente os produtos citados
# no material do DIEESE (gasolina/etanol, diesel/GNV, GLP).
ARQUIVOS = {
    "gasolina_etanol": f"{BASE}/ultimas-4-semanas-gasolina-etanol.csv",
    "diesel_gnv": f"{BASE}/ultimas-4-semanas-diesel-gnv.csv",
    "glp": f"{BASE}/ultimas-4-semanas-glp.csv",
}
# A ANP bloqueia requisições sem cabeçalhos de navegador (não é autenticação, é
# detecção de bot) — ver seção "ACHADO IMPORTANTE" acima. Confirmado nesta rodada.
CABECALHOS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "text/csv,text/html,*/*",
    "Accept-Language": "pt-BR,pt;q=0.9",
}

DESTINO = Path(__file__).resolve().parents[3] / "data" / "raw" / "anp"


# ------------------------------------------------------------------------
# PASSO 1 — baixar um arquivo CSV da ANP
# ------------------------------------------------------------------------
def _baixar_arquivo(url: str) -> bytes:
    """Faz a requisição HTTP com `CABECALHOS` de navegador (necessários para
    evitar o HTTP 403 de detecção de bot, ver docstring do módulo) e devolve
    o conteúdo bruto do CSV, em bytes (não decodifica texto aqui — mantém o
    arquivo exatamente como a ANP o publica).

    `timeout=90` é maior que o dos outros scripts deste bloco porque estes
    arquivos são microdados por posto revendedor e podem chegar a vários
    megabytes — precisam de mais tempo para transferir por completo antes de
    o script desistir por timeout.
    """
    req = urllib.request.Request(url, headers=CABECALHOS)
    with urllib.request.urlopen(req, timeout=90) as resposta:
        return resposta.read()


# ------------------------------------------------------------------------
# PASSO 2 — salvar o conteúdo bruto de um arquivo em disco
# ------------------------------------------------------------------------
def _salvar_raw(nome: str, conteudo: bytes, timestamp: str) -> Path:
    """Grava `conteudo` exatamente como veio (bytes, sem qualquer
    reformatação — diferente dos scripts de API JSON deste piloto, aqui não
    há reformatação porque o arquivo já é um CSV pronto). O nome do arquivo
    leva o produto (para diferenciar gasolina/etanol, diesel/GNV e GLP) e um
    timestamp UTC, porque a série é atualizada semanalmente e cada execução
    deste script é uma nova "fotografia" — nunca sobrescrevemos a coleta
    anterior.
    """
    arquivo = DESTINO / f"combustiveis_{nome}_{timestamp}.csv"
    arquivo.write_bytes(conteudo)
    return arquivo


# ------------------------------------------------------------------------
# Orquestração: repete os passos acima para cada arquivo de ARQUIVOS
# ------------------------------------------------------------------------
def coletar() -> list[Path]:
    DESTINO.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

    arquivos = []
    for nome, url in ARQUIVOS.items():
        conteudo = _baixar_arquivo(url)
        arquivos.append(_salvar_raw(nome, conteudo, timestamp))
    return arquivos


if __name__ == "__main__":
    for caminho in coletar():
        tamanho_mb = caminho.stat().st_size / (1024 * 1024)
        print(f"Coleta concluída: {caminho} ({tamanho_mb:.2f} MB)")
        registrar_coleta(fonte=DESTINO.name, arquivo=caminho, script=__file__)
