"""Helper mínimo para a camada CURATED (ADR 0005): localizar o RAW mais recente de um
indicador e gravar pontos em `indicadores_serie`.

Mesmo espírito de minimalismo de `pipelines/supabase_raw.py` (stdlib puro, fala com a
API REST/Storage do Supabase via `urllib`) — não é um ORM, é só o suficiente para os
scripts de `pipelines/curated/` lerem o RAW e gravarem a série.

===============================================================================
COMO UM SCRIPT DE pipelines/curated/ ENCONTRA "O RAW MAIS RECENTE DO SEU INDICADOR"
===============================================================================
`raw_ingestoes` não tem o campo `indicador` preenchido de forma confiável (a maioria
dos scripts de `pipelines/ingestao/` não passa esse argumento) — o que É único por
indicador é o campo `script` (caminho relativo do arquivo `.py` que fez a coleta, ex.
"pipelines/ingestao/bloco_1_macroeconomia/coleta_pib_sidra.py"). Por isso
`buscar_ultimo_raw()` filtra por `script`, não por `fonte` nem por `indicador` — uma
pasta RAW como `data/raw/ibge_sidra/` é compartilhada por vários indicadores diferentes
(PIB, PMC, PMS, PIM...), então filtrar só por `fonte` devolveria a coleta mais recente
de QUALQUER um desses indicadores, não necessariamente do que o script quer.

===============================================================================
O QUE ESTE MÓDULO NÃO FAZ
===============================================================================
Não reconstrói arquivos particionados (ver `reconstruir_arquivo()` em
`supabase_raw.py`) — nenhum indicador coberto nesta rodada de `pipelines/curated/`
produz RAW particionado (>45 MB como arquivo único; o CSV da balança comercial é
grande, mas cada ano é um único objeto, abaixo do limite de particionamento). Se um
indicador futuro precisar disso, reaproveitar `reconstruir_arquivo()` diretamente.
"""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unicodedata
import urllib.error
import urllib.request
from pathlib import Path

_RAIZ = Path(__file__).resolve().parent.parent.parent


def _carregar_env() -> dict[str, str]:
    variaveis: dict[str, str] = {}
    caminho_env = _RAIZ / ".env"
    if not caminho_env.exists():
        return variaveis
    for linha in caminho_env.read_text(encoding="utf-8").splitlines():
        linha = linha.strip()
        if not linha or linha.startswith("#") or "=" not in linha:
            continue
        chave, _, valor = linha.partition("=")
        variaveis[chave.strip()] = valor.strip()
    return variaveis


_ENV = {**_carregar_env(), **__import__("os").environ}
_SUPABASE_URL = _ENV.get("SUPABASE_URL")
_SUPABASE_SERVICE_ROLE_KEY = _ENV.get("SUPABASE_SERVICE_ROLE_KEY")


def _headers() -> dict[str, str]:
    return {
        "apikey": _SUPABASE_SERVICE_ROLE_KEY,
        "Authorization": f"Bearer {_SUPABASE_SERVICE_ROLE_KEY}",
    }


def _exigir_credenciais() -> None:
    if not _SUPABASE_URL or not _SUPABASE_SERVICE_ROLE_KEY:
        raise RuntimeError(
            "SUPABASE_URL/SUPABASE_SERVICE_ROLE_KEY não configurados em .env — "
            "scripts de pipelines/curated/ precisam ler o RAW do Supabase, "
            "diferente dos scripts de ingestão (que toleram rodar sem Supabase)."
        )


# ------------------------------------------------------------------------
# Localizar e baixar o RAW mais recente de um indicador
# ------------------------------------------------------------------------
def buscar_ultimo_raw(script_relativo: str, limite: int = 1) -> list[dict]:
    """Devolve as `limite` linhas mais recentes de `raw_ingestoes` cujo campo
    `script` é exatamente `script_relativo` (ex.
    "pipelines/ingestao/bloco_1_macroeconomia/coleta_pib_sidra.py"), mais
    recente primeiro. Só considera `status=sucesso`.
    """
    _exigir_credenciais()
    query = (
        f"script=eq.{urllib.request.quote(script_relativo, safe='')}"
        "&status=eq.sucesso"
        "&order=coletado_em.desc"
        f"&limit={limite}"
    )
    req = urllib.request.Request(
        f"{_SUPABASE_URL}/rest/v1/raw_ingestoes?{query}",
        headers=_headers(),
    )
    with urllib.request.urlopen(req, timeout=60) as resposta:
        return json.loads(resposta.read().decode("utf-8"))


def baixar_objeto_storage(storage_path: str) -> bytes:
    """Baixa o conteúdo de um objeto do Storage pelo caminho gravado em
    `raw_ingestoes.storage_path` (já inclui o prefixo "raw/").
    """
    _exigir_credenciais()
    req = urllib.request.Request(
        f"{_SUPABASE_URL}/storage/v1/object/{storage_path}",
        headers=_headers(),
    )
    with urllib.request.urlopen(req, timeout=120) as resposta:
        return resposta.read()


# ------------------------------------------------------------------------
# Extrair texto de um PDF (boletins institucionais do DIEESE — ICT, Greves,
# De Olho nas Negociações). Usa o binário `pdftotext` (poppler-utils), já
# confirmado presente no runner `ubuntu-latest` do GitHub Actions e instalado
# localmente via MSYS2/Git for Windows. `-layout` preserva a posição
# aproximada do texto na página — necessário porque esses boletins são
# predominantemente gráficos, não texto corrido; `NFC` normaliza acentos
# (alguns PDFs gerados por LibreOffice saem em NFD, o que quebra regex
# literal contra o mesmo texto digitado em UTF-8 normal).
# ------------------------------------------------------------------------
def extrair_texto_pdf(conteudo_pdf: bytes) -> str:
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
        tmp.write(conteudo_pdf)
        caminho_tmp = tmp.name
    try:
        resultado = subprocess.run(
            ["pdftotext", "-layout", "-enc", "UTF-8", caminho_tmp, "-"],
            capture_output=True, text=True, encoding="utf-8", check=True,
        )
    finally:
        Path(caminho_tmp).unlink(missing_ok=True)
    return unicodedata.normalize("NFC", resultado.stdout)


# ------------------------------------------------------------------------
# Gravar pontos em indicadores_serie
# ------------------------------------------------------------------------
def registrar_serie(indicador_id: str, pontos: list[dict]) -> None:
    """Grava `pontos` em `indicadores_serie` via upsert (chave
    `indicador_id, data_referencia`). Cada ponto é um dicionário com, no
    mínimo, `data_referencia` ("AAAA-MM-DD") e `valor` (número) — `metadata`
    é opcional. Não faz nada se `pontos` estiver vazio.
    """
    if not pontos:
        return
    _exigir_credenciais()
    corpo = json.dumps(
        [
            {
                "indicador_id": indicador_id,
                "data_referencia": p["data_referencia"],
                "valor": p["valor"],
                "metadata": p.get("metadata"),
            }
            for p in pontos
        ]
    ).encode("utf-8")
    req = urllib.request.Request(
        f"{_SUPABASE_URL}/rest/v1/indicadores_serie?on_conflict=indicador_id,data_referencia",
        data=corpo,
        headers={
            **_headers(),
            "Content-Type": "application/json",
            "Prefer": "resolution=merge-duplicates,return=minimal",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resposta:
            resposta.read()
    except urllib.error.HTTPError as erro:
        detalhe = erro.read().decode("utf-8", "replace")[:500]
        raise RuntimeError(f"Falha ao gravar indicadores_serie ({indicador_id}): HTTP {erro.code} — {detalhe}") from erro


if __name__ == "__main__":
    print(
        "Este módulo não roda sozinho — é importado pelos scripts de "
        "pipelines/curated/transformar_*.py.",
        file=sys.stderr,
    )
