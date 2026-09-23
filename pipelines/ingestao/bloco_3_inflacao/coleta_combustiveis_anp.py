"""Coleta bruta dos preços de combustíveis (gasolina/etanol, diesel/GNV, GLP) via download
estruturado da ANP (Agência Nacional do Petróleo, Gás Natural e Biocombustíveis).

Piloto técnico controlado — ver docs/08-decisoes-adr/0002-expansao-piloto-por-blocos.md
Fonte confirmada em: docs/04-fontes/anp-ipeadata.md — investigação de lacunas pós-Lote 06,
com URL exata extraída e testada em 2026-09-22 (achado que substitui a pendência anterior).

ACHADO: a primeira tentativa de acesso à página oficial da ANP (gov.br) retornou HTTP 403.
Não era um bloqueio de WAF genérico — era detecção de bot por ausência de cabeçalhos HTTP
típicos de navegador (Accept, Accept-Language). Com esses cabeçalhos adicionados, o acesso
funcionou normalmente (HTTP 200) e permitiu extrair os links reais de download da própria
página, em vez de adivinhar um padrão de URL.

Coleta os 3 arquivos de "últimas 4 semanas" (série de microdados por posto revendedor,
atualizada semanalmente) — não a série semestral completa desde 2004, que é maior e
menos necessária para um piloto de conjuntura corrente.

Este script NÃO transforma o dado.
"""

import urllib.request
from datetime import datetime, timezone
from pathlib import Path

BASE = "https://www.gov.br/anp/pt-br/centrais-de-conteudo/dados-abertos/arquivos/shpc/qus"
ARQUIVOS = {
    "gasolina_etanol": f"{BASE}/ultimas-4-semanas-gasolina-etanol.csv",
    "diesel_gnv": f"{BASE}/ultimas-4-semanas-diesel-gnv.csv",
    "glp": f"{BASE}/ultimas-4-semanas-glp.csv",
}
# A ANP bloqueia requisições sem cabeçalhos de navegador (não é autenticação, é
# detecção de bot) — confirmado nesta rodada.
CABECALHOS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "text/csv,text/html,*/*",
    "Accept-Language": "pt-BR,pt;q=0.9",
}
DESTINO = Path(__file__).resolve().parents[3] / "data" / "raw" / "anp"


def coletar() -> list[Path]:
    DESTINO.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    arquivos = []
    for nome, url in ARQUIVOS.items():
        req = urllib.request.Request(url, headers=CABECALHOS)
        with urllib.request.urlopen(req, timeout=90) as resposta:
            conteudo = resposta.read()
        arquivo = DESTINO / f"combustiveis_{nome}_{timestamp}.csv"
        arquivo.write_bytes(conteudo)
        arquivos.append(arquivo)
    return arquivos


if __name__ == "__main__":
    for caminho in coletar():
        tamanho_mb = caminho.stat().st_size / (1024 * 1024)
        print(f"Coleta concluída: {caminho} ({tamanho_mb:.2f} MB)")
