"""Helper mínimo para registrar coletas RAW no Supabase (ADR 0004).

Sem dependências externas — lê credenciais de `.env` na raiz do repositório
(sem depender de `python-dotenv`) e fala com a API REST/Storage do Supabase
via `urllib`, no mesmo espírito de minimalismo do ADR 0001.

Usado pelos scripts de `pipelines/ingestao/` para, além de gravar o arquivo
bruto em `data/raw/` (que continua sendo a cópia local e a fonte de verdade
imediata deste piloto), enviar uma cópia para o bucket `raw` do Supabase
Storage e registrar um log de execução na tabela `raw_ingestoes`.

Falha ao enviar para o Supabase NUNCA deve interromper a coleta em si — se
`.env` não tiver as credenciais (ex. ambiente de outro colaborador), ou se a
chamada à API falhar (ex. arquivo grande além do limite do Storage), a
função apenas avisa em stderr e segue em frente.
"""

from __future__ import annotations

import hashlib
import json
import mimetypes
import sys
import urllib.error
import urllib.request
from pathlib import Path

_RAIZ = Path(__file__).resolve().parent.parent


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


def _requisicao(url: str, dados: bytes, headers: dict[str, str]) -> None:
    req = urllib.request.Request(url, data=dados, headers=headers, method="POST")
    with urllib.request.urlopen(req, timeout=120) as resposta:
        resposta.read()


def registrar_coleta(
    fonte: str,
    arquivo: Path,
    script: str,
    indicador: str | None = None,
    metadata: dict | None = None,
) -> None:
    """Envia `arquivo` para `raw/<fonte>/<nome-do-arquivo>` no Supabase
    Storage e registra a execução em `raw_ingestoes`. `script` é o `__file__`
    do script chamador (convertido para caminho relativo ao repositório).
    Não faz nada se `SUPABASE_URL`/`SUPABASE_SERVICE_ROLE_KEY` não estiverem
    configurados em `.env`.
    """
    if not _SUPABASE_URL or not _SUPABASE_SERVICE_ROLE_KEY:
        return

    try:
        script_rel = Path(script).resolve().relative_to(_RAIZ).as_posix()
    except ValueError:
        script_rel = str(script)

    conteudo = arquivo.read_bytes()
    tamanho_bytes = len(conteudo)
    sha256 = hashlib.sha256(conteudo).hexdigest()
    storage_path = f"{fonte}/{arquivo.name}"
    content_type = mimetypes.guess_type(arquivo.name)[0] or "application/octet-stream"

    headers_comuns = {
        "apikey": _SUPABASE_SERVICE_ROLE_KEY,
        "Authorization": f"Bearer {_SUPABASE_SERVICE_ROLE_KEY}",
    }

    status = "sucesso"
    mensagem_erro = None
    try:
        _requisicao(
            f"{_SUPABASE_URL}/storage/v1/object/raw/{storage_path}",
            conteudo,
            {**headers_comuns, "Content-Type": content_type, "x-upsert": "true"},
        )
    except urllib.error.HTTPError as erro:
        status = "erro"
        corpo_erro = erro.read().decode("utf-8", "replace")[:500]
        mensagem_erro = f"Storage upload falhou: HTTP {erro.code} — {corpo_erro}"
    except (urllib.error.URLError, TimeoutError) as erro:
        status = "erro"
        mensagem_erro = f"Storage upload falhou: {erro}"

    corpo = json.dumps(
        {
            "fonte": fonte,
            "indicador": indicador,
            "script": script_rel,
            "storage_path": f"raw/{storage_path}" if status == "sucesso" else None,
            "tamanho_bytes": tamanho_bytes,
            "sha256": sha256,
            "status": status,
            "mensagem_erro": mensagem_erro,
            "metadata": metadata,
        }
    ).encode("utf-8")

    try:
        _requisicao(
            f"{_SUPABASE_URL}/rest/v1/raw_ingestoes",
            corpo,
            {**headers_comuns, "Content-Type": "application/json", "Prefer": "return=minimal"},
        )
    except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError) as erro:
        detalhe = erro.read().decode("utf-8", "replace")[:300] if isinstance(erro, urllib.error.HTTPError) else str(erro)
        print(f"[supabase_raw] aviso: falha ao registrar log em raw_ingestoes — {detalhe}", file=sys.stderr)
