"""Transformação CURATED do catálogo amplo de ações da B3 (ADR 0010 Fase 2) —
a partir do RAW gravado por `pipelines/ingestao/bloco_6_mercados/coleta_b3_brapi.py`
(brapi.dev, endpoint /api/v2/tickers).

===============================================================================
LIMPEZA FEITA AQUI (não na coleta — a coleta grava o bruto sem filtrar)
===============================================================================
O RAW tem ~780 tickers brutos, mas isso não é ~780 empresas: a B3 lista mais
de uma classe de ação por empresa (ex. PETR3 = ordinária, PETR4 =
preferencial) e um mercado fracionário espelhado para cada classe (sufixo
"F", ex. PETR4F) — testado e confirmado nesta sessão: PETR3/PETR4/PETR4F
devolvem o MESMO `marketCap`, porque é a capitalização da empresa inteira,
não da classe.

Só uma regra de limpeza aqui: descarta qualquer ticker terminado em "F"
(mercado fracionário — não é a linha principal de negociação) e qualquer
ticker sem capitalização de mercado (dado incompleto). Mantém TODAS as
classes de cada empresa (ex. PETR3 e PETR4 separadas) — pedido explícito do
responsável do projeto em 2026-10-26: "eu quero todas as ações... todas as
classes de cada empresa", revertendo uma decisão anterior desta mesma sessão
que mantinha só a classe de maior volume por empresa.

Como o `marketCap` se repete em cada classe da mesma empresa, agrupar por
empresa para não contar a mesma capitalização duas vezes passou a ser
responsabilidade de quem CONSOME este dado para algo sensível a isso — hoje,
só o mapa de calor (`frontend/js/mercados.js`, `montarMapaCalor`), que
deduplica por raiz de ticker na hora de montar o treemap. Busca e ranking de
altas/baixas usam a lista completa, com todas as classes.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from curated_supabase import baixar_objeto_storage, buscar_ultimo_raw

_ENV = {}
_RAIZ_PROJETO = Path(__file__).resolve().parent.parent.parent
_env_path = _RAIZ_PROJETO / ".env"
if _env_path.exists():
    for _linha in _env_path.read_text(encoding="utf-8").splitlines():
        _linha = _linha.strip()
        if not _linha or _linha.startswith("#") or "=" not in _linha:
            continue
        _chave, _, _valor = _linha.partition("=")
        _ENV[_chave.strip()] = _valor.strip()

import os
import urllib.error
import urllib.request

_SUPABASE_URL = _ENV.get("SUPABASE_URL") or os.environ.get("SUPABASE_URL")
_SUPABASE_SERVICE_ROLE_KEY = _ENV.get("SUPABASE_SERVICE_ROLE_KEY") or os.environ.get("SUPABASE_SERVICE_ROLE_KEY")

SCRIPT_ORIGEM = "pipelines/ingestao/bloco_6_mercados/coleta_b3_brapi.py"


# ------------------------------------------------------------------------
# PASSO 1 — baixar o RAW mais recente
# ------------------------------------------------------------------------
def _baixar_raw() -> dict:
    registros = buscar_ultimo_raw(SCRIPT_ORIGEM, limite=1)
    if not registros:
        raise RuntimeError(f"Nenhum RAW encontrado para {SCRIPT_ORIGEM}")
    conteudo = baixar_objeto_storage(registros[0]["storage_path"])
    return json.loads(conteudo.decode("utf-8"))


# ------------------------------------------------------------------------
# PASSO 2 — limpar: descartar fracionário, agrupar por empresa, manter só a
# classe mais líquida (ver docstring do módulo para o raciocínio completo).
# ------------------------------------------------------------------------
def _limpar(resultados: list[dict]) -> list[dict]:
    sem_fracionario = [r for r in resultados if not r["symbol"].endswith("F")]
    com_marketcap = [r for r in sem_fracionario if (r.get("quote") or {}).get("marketCap")]
    return com_marketcap


# ------------------------------------------------------------------------
# PASSO 3 — gravar no banco: upsert em mercado_b3_ativos (catálogo) e
# mercado_b3_serie (ponto do dia). Tabelas novas (migração 0011), fora do
# padrão indicadores/indicadores_serie de propósito — ver docstring e ADR 0010.
# ------------------------------------------------------------------------
def _upsert(caminho: str, corpo: list[dict]) -> None:
    if not _SUPABASE_URL or not _SUPABASE_SERVICE_ROLE_KEY:
        raise RuntimeError("SUPABASE_URL/SUPABASE_SERVICE_ROLE_KEY não configurados em .env")
    headers = {
        "apikey": _SUPABASE_SERVICE_ROLE_KEY,
        "Authorization": f"Bearer {_SUPABASE_SERVICE_ROLE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "resolution=merge-duplicates,return=minimal",
    }
    dados = json.dumps(corpo, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(f"{_SUPABASE_URL}/rest/v1/{caminho}", data=dados, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=60) as resposta:
            resposta.read()
    except urllib.error.HTTPError as erro:
        detalhe = erro.read().decode("utf-8", "replace")[:500]
        raise RuntimeError(f"Falha ao gravar em {caminho}: HTTP {erro.code} — {detalhe}") from erro


def transformar() -> dict:
    dados = _baixar_raw()
    limpos = _limpar(dados.get("results") or [])

    data_referencia = None
    ativos = []
    pontos = []
    for r in limpos:
        quote = r.get("quote") or {}
        ativos.append({
            "ticker": r["symbol"],
            "nome": r.get("longName") or r.get("name") or r["symbol"],
            "setor": r.get("sector"),
            "subsetor": r.get("subsector"),
            "tipo": r.get("subType") or r.get("assetType") or "stock",
        })

    data_coleta = (dados.get("coletado_em") or "")[:10]
    if not data_coleta:
        from datetime import datetime, timezone
        data_coleta = datetime.now(timezone.utc).date().isoformat()

    for r in limpos:
        quote = r.get("quote") or {}
        if quote.get("lastPrice") is None:
            continue
        pontos.append({
            "ticker": r["symbol"],
            "data_referencia": data_coleta,
            "preco": quote.get("lastPrice"),
            "variacao_pct": quote.get("changePercent"),
            "volume": quote.get("volume"),
            "market_cap": quote.get("marketCap"),
        })

    # mercado_b3_ativos.ticker é a chave única do on_conflict (upsert por PK).
    _upsert("mercado_b3_ativos?on_conflict=ticker", ativos)
    # mercado_b3_serie: upsert por (ticker, data_referencia), igual ao padrão
    # já usado em indicadores_serie.
    _upsert("mercado_b3_serie?on_conflict=ticker,data_referencia", pontos)

    return {"ativos": len(ativos), "pontos": len(pontos), "data_referencia": data_coleta}


if __name__ == "__main__":
    resultado = transformar()
    print(
        f"Transformação concluída: {resultado['ativos']} ativos, "
        f"{resultado['pontos']} pontos gravados para {resultado['data_referencia']}."
    )
