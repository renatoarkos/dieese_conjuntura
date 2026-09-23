"""Coleta bruta da Pesquisa de Endividamento e Inadimplência do Consumidor
(PEIC), FecomercioSP — parte do indicador "endividamento familiar" do
material do DIEESE (a outra parte, do BCB, é coletada em
`coleta_endividamento_bcb.py`, neste mesmo bloco).

Piloto técnico controlado — ver docs/08-decisoes-adr/0002-expansao-piloto-por-blocos.md
Fonte confirmada em: docs/04-fontes/fecomercio-peic.md — Lote 05c.

===============================================================================
COMO FUNCIONA A API REST DO WORDPRESS (padrão transferível para qualquer site
em WordPress que publique arquivos como anexo de mídia)
===============================================================================
A FecomercioSP não publica uma API de dados nem um link fixo para o arquivo
da pesquisa — cada edição mensal é um novo arquivo Excel anexado ao site, que
roda em WordPress. Em vez de acessar a página de estatísticas e extrair o
link do arquivo a partir do HTML (abordagem frágil: qualquer mudança visual
no site quebra o script), este script usa a API REST NATIVA do WordPress,
que já existe em qualquer instalação padrão e lista os anexos de mídia
publicados de forma estruturada:

    https://<site>/wp-json/wp/v2/media?search={termo}&per_page={n}

  - `search=PEIC`   → filtra só os anexos cujo título/descrição contém "PEIC"
                      (sem isso, a listagem traria todo tipo de mídia do site).
  - `per_page=30`   → quantos itens trazer por página (30 é mais do que o
                      necessário; a API já devolve em ordem decrescente de
                      data de publicação).

A resposta é uma lista de objetos JSON, um por anexo, cada um com um campo
`source_url` com a URL direta do arquivo — sem precisar interpretar HTML.
Esse mesmo padrão `wp-json/wp/v2/media` funciona em qualquer site WordPress
que não tenha desativado a API REST padrão.

===============================================================================
O QUE ESTE SCRIPT FAZ, PASSO A PASSO
===============================================================================
1. Consulta a API de mídia do WordPress filtrando por "PEIC" e identifica o
   arquivo `.xlsx` mais recente (`_localizar_arquivo_mais_recente`).
2. Baixa o conteúdo desse arquivo (`_baixar_arquivo`).
3. Salva o conteúdo, sem abrir nem alterar, em `data/raw/fecomercio_peic/`
   (`_salvar_raw`).
4. Registra a coleta no Supabase (Storage + `raw_ingestoes`).

Este script NÃO transforma o dado — baixa o workbook mais recente (que já
contém, na aba "Série Histórica", a série completa desde fev/2004) exatamente
como publicado, sem abrir ou alterar seu conteúdo.
"""

import json
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from supabase_raw import registrar_coleta

LISTAGEM_URL = "https://pesquisas.fecomercio.com.br/wp-json/wp/v2/media?search=PEIC&per_page=30"

DESTINO = Path(__file__).resolve().parents[3] / "data" / "raw" / "fecomercio_peic"


# ------------------------------------------------------------------------
# PASSO 1 — descobrir a URL do arquivo Excel mais recente
# ------------------------------------------------------------------------
def _localizar_arquivo_mais_recente() -> str:
    """Consulta a listagem de mídia do WordPress e devolve a URL do `.xlsx`
    mais recente.

    A API já retorna os itens em ordem decrescente de data de publicação —
    por isso basta pegar o primeiro candidato que termina em `.xlsx` (a
    busca por "PEIC" pode trazer outros tipos de anexo, como imagens usadas
    no próprio site).
    """
    req = urllib.request.Request(LISTAGEM_URL, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as resposta:
        itens = json.loads(resposta.read().decode("utf-8"))

    candidatos = [
        item for item in itens
        if item.get("source_url", "").lower().endswith(".xlsx")
    ]
    if not candidatos:
        raise RuntimeError("Nenhum arquivo .xlsx encontrado na listagem de mídia do PEIC")

    return candidatos[0]["source_url"]


# ------------------------------------------------------------------------
# PASSO 2 — baixar o conteúdo do arquivo
# ------------------------------------------------------------------------
def _baixar_arquivo(url: str) -> bytes:
    """Baixa o conteúdo bruto (bytes) do arquivo Excel. Mantém o mesmo
    `User-Agent` usado na listagem, por consistência — o servidor pode
    tratar requisições sem esse cabeçalho de forma diferente.
    """
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=60) as resposta:
        return resposta.read()


# ------------------------------------------------------------------------
# PASSO 3 — salvar o arquivo bruto em disco
# ------------------------------------------------------------------------
def _salvar_raw(conteudo: bytes, nome_original: str, timestamp: str) -> Path:
    """Grava `conteudo` exatamente como recebido, sem abrir o Excel nem
    inspecionar suas abas — abrir/reformatar já seria uma transformação, que
    não pertence à camada RAW. O nome do arquivo leva o nome original
    publicado pela FecomercioSP prefixado por um timestamp UTC da coleta,
    porque cada edição mensal é um arquivo novo e queremos preservar todas
    as coletas, nunca sobrescrever uma anterior.
    """
    arquivo = DESTINO / f"{timestamp}_{nome_original}"
    arquivo.write_bytes(conteudo)
    return arquivo


# ------------------------------------------------------------------------
# Orquestração: chama os passos acima, nesta ordem
# ------------------------------------------------------------------------
def coletar() -> Path:
    DESTINO.mkdir(parents=True, exist_ok=True)

    url_arquivo = _localizar_arquivo_mais_recente()
    conteudo = _baixar_arquivo(url_arquivo)

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    nome_original = url_arquivo.rsplit("/", 1)[-1]
    return _salvar_raw(conteudo, nome_original, timestamp)


if __name__ == "__main__":
    caminho = coletar()
    tamanho_kb = caminho.stat().st_size / 1024
    print(f"Coleta concluída: {caminho} ({tamanho_kb:.1f} KB)")
    registrar_coleta(fonte=DESTINO.name, arquivo=caminho, script=__file__)
