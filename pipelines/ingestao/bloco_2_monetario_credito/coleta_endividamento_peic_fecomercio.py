"""Coleta bruta da Pesquisa de Endividamento e Inadimplência do Consumidor (PEIC),
FecomercioSP — parte do indicador "endividamento familiar" do material do DIEESE.

Piloto técnico controlado — ver docs/08-decisoes-adr/0002-expansao-piloto-por-blocos.md
Fonte confirmada em: docs/04-fontes/fecomercio-peic.md — Lote 05c.

DECISÃO DE FORMATO DE EXTRAÇÃO: a FecomercioSP não publica API de dados nem link fixo
para o arquivo — cada edição mensal é um novo arquivo Excel anexado ao site (WordPress).
Em vez de raspar HTML da página de estatísticas (frágil), este script usa a API REST
nativa do WordPress (wp-json), que lista os anexos de mídia publicados e já retorna a
URL do arquivo mais recente de forma estruturada — mais robusto que parsear HTML.

Este script NÃO transforma o dado — baixa o workbook mais recente (que já contém, na
aba "Série Histórica", a série completa desde fev/2004) sem abrir/alterar seu conteúdo.
"""

import json
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

LISTAGEM_URL = "https://pesquisas.fecomercio.com.br/wp-json/wp/v2/media?search=PEIC&per_page=30"
DESTINO = Path(__file__).resolve().parents[3] / "data" / "raw" / "fecomercio_peic"


def _arquivo_mais_recente() -> str:
    req = urllib.request.Request(LISTAGEM_URL, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as resposta:
        itens = json.loads(resposta.read().decode("utf-8"))

    candidatos = [
        item for item in itens
        if item.get("source_url", "").lower().endswith(".xlsx")
    ]
    if not candidatos:
        raise RuntimeError("Nenhum arquivo .xlsx encontrado na listagem de mídia do PEIC")

    # A API já retorna em ordem decrescente de data de publicação — o primeiro é o mais recente.
    return candidatos[0]["source_url"]


def coletar() -> Path:
    DESTINO.mkdir(parents=True, exist_ok=True)
    url_arquivo = _arquivo_mais_recente()

    req = urllib.request.Request(url_arquivo, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=60) as resposta:
        conteudo = resposta.read()

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    nome_original = url_arquivo.rsplit("/", 1)[-1]
    arquivo = DESTINO / f"{timestamp}_{nome_original}"
    arquivo.write_bytes(conteudo)
    return arquivo


if __name__ == "__main__":
    caminho = coletar()
    tamanho_kb = caminho.stat().st_size / 1024
    print(f"Coleta concluída: {caminho} ({tamanho_kb:.1f} KB)")
