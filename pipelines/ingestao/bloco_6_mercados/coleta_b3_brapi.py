"""Coleta bruta do catálogo amplo de ações da B3 via brapi.dev (ADR 0010,
Fase 2 do plano de ampliação de "Mercados financeiros").

===============================================================================
POR QUE A BRAPI.DEV, E NÃO SÓ A YAHOO FINANCE
===============================================================================
O endpoint gratuito da Yahoo Finance já usado pelo resto deste bloco
(`coleta_mercados_yahoo.py`) não devolve `marketCap` para nenhum tipo de
ativo (confirmado em 2026-10-23) — sem isso não dá para fazer um mapa de
calor no padrão "Finviz" (tamanho do bloco = capitalização de mercado).
Pesquisado e testado nesta sessão (2026-10-26): a brapi.dev, API brasileira
dedicada à B3, tem um endpoint `/api/v2/tickers` que devolve, numa única
chamada paginada, símbolo, nome, setor, subsetor e um bloco `quote` com
preço, variação %, volume e capitalização de mercado — tudo no plano
GRATUITO (o endpoint `/api/v2/stocks/screener`, mais rico em fundamentos,
é pago — testado e confirmado HTTP 403 no plano gratuito).

===============================================================================
CHAVE DE API
===============================================================================
Exige `BRAPI_TOKEN` em `.env` (conta criada pelo responsável do projeto em
2026-10-26, plano gratuito: 15.000 requisições/mês). Enviada como
`Authorization: Bearer <token>`. Nunca usada em código que roda no
navegador — só aqui, em processo de backend/ingestão.

===============================================================================
O QUE ESTE SCRIPT FAZ, PASSO A PASSO
===============================================================================
1. Busca todas as páginas de `/api/v2/tickers?type=stock` (776 tickers em 4
   páginas de 250, confirmado nesta sessão — `limit=250` é o máximo aceito).
2. Salva a resposta combinada (todas as páginas) num único arquivo RAW em
   `data/raw/brapi/`.
3. Registra o arquivo no Supabase.

Este script NÃO filtra, deduplica nem escolhe uma classe de ação por empresa
— grava exatamente o que a fonte devolveu (inclusive tickers fracionários e
classes repetidas da mesma empresa). Essa limpeza é trabalho de
`transformar_b3_brapi.py` (camada CURATED), não da coleta.
"""

import json
import os
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from supabase_raw import registrar_coleta

RAIZ = Path(__file__).resolve().parents[3]
DESTINO = RAIZ / "data" / "raw" / "brapi"

_LIMITE_POR_PAGINA = 250


def _carregar_token() -> str:
    env = {}
    caminho_env = RAIZ / ".env"
    if caminho_env.exists():
        for linha in caminho_env.read_text(encoding="utf-8").splitlines():
            linha = linha.strip()
            if not linha or linha.startswith("#") or "=" not in linha:
                continue
            chave, _, valor = linha.partition("=")
            env[chave.strip()] = valor.strip()
    token = env.get("BRAPI_TOKEN") or os.environ.get("BRAPI_TOKEN")
    if not token:
        raise RuntimeError("BRAPI_TOKEN não configurado em .env")
    return token


# ------------------------------------------------------------------------
# PASSO 1 — buscar uma página de /api/v2/tickers
# ------------------------------------------------------------------------
def _buscar_pagina(token: str, pagina: int) -> dict:
    url = (
        "https://brapi.dev/api/v2/tickers"
        f"?type=stock&limit={_LIMITE_POR_PAGINA}&page={pagina}"
        "&sortBy=marketCap&sortOrder=desc"
    )
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"})
    with urllib.request.urlopen(req, timeout=30) as resposta:
        return json.loads(resposta.read().decode("utf-8"))


def coletar() -> Path:
    token = _carregar_token()
    DESTINO.mkdir(parents=True, exist_ok=True)

    primeira = _buscar_pagina(token, 1)
    todos = list(primeira.get("results") or [])
    total_paginas = primeira.get("pagination", {}).get("totalPages", 1)

    for pagina in range(2, total_paginas + 1):
        time.sleep(0.3)  # educado com a cota mensal, sem pressa nenhuma aqui
        dados_pagina = _buscar_pagina(token, pagina)
        todos.extend(dados_pagina.get("results") or [])

    combinado = {
        "results": todos,
        "facets": primeira.get("facets"),
        "totalItems": primeira.get("pagination", {}).get("totalItems"),
        "coletado_em": datetime.now(timezone.utc).isoformat(),
    }

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    arquivo = DESTINO / f"b3_tickers_{timestamp}.json"
    arquivo.write_text(json.dumps(combinado, ensure_ascii=False, indent=2), encoding="utf-8")
    return arquivo


if __name__ == "__main__":
    try:
        caminho = coletar()
        print(f"Coleta concluída: {caminho}")
        registrar_coleta(fonte=DESTINO.name, arquivo=caminho, script=__file__)
    except urllib.error.HTTPError as erro:
        corpo = erro.read().decode("utf-8", "replace")[:500]
        print(f"Falha na coleta da brapi.dev: HTTP {erro.code} — {corpo}", file=sys.stderr)
        sys.exit(1)
