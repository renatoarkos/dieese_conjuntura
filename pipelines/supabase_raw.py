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
chamada à API falhar, a função apenas avisa em stderr e segue em frente.

===============================================================================
ARQUIVOS GRANDES: PARTICIONAMENTO AUTOMÁTICO
===============================================================================
O plano atual do Supabase Storage rejeita arquivos acima de 50 MB (HTTP 413
"Payload too large") — confirmado na prática com os microdados do CAGED
(`CAGEDMOV*.7z`, ~50-57 MB cada). Em vez de depender de outro serviço externo
para esses arquivos (uma tentativa de usar o Google Drive esbarrou em
limitações fora do nosso controle — conta de serviço sem cota própria, Drive
Compartilhado indisponível no plano, domínio do Workspace não verificado —
ver `docs/08-decisoes-adr/0004-supabase-raw-storage.md`), este módulo divide
qualquer arquivo acima de `LIMITE_PARTE_BYTES` em partes menores antes de
enviar, e registra em `raw_ingestoes.metadata` como remontar o arquivo
original depois (lista de partes, na ordem). Cada parte é só um pedaço
sequencial de bytes do arquivo original — remontar é simplesmente concatenar
as partes na ordem certa (ver `reconstruir_arquivo()` abaixo).
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

# Margem de segurança abaixo do limite real do Storage (50 MB) — evita ficar
# testando o limite exato a cada mudança de plano/configuração do Supabase.
LIMITE_PARTE_BYTES = 45 * 1024 * 1024


def _requisicao(url: str, dados: bytes, headers: dict[str, str], metodo: str = "POST") -> None:
    req = urllib.request.Request(url, data=dados, headers=headers, method=metodo)
    with urllib.request.urlopen(req, timeout=120) as resposta:
        resposta.read()


def _enviar_objeto(storage_path: str, conteudo: bytes, content_type: str) -> tuple[str, str | None]:
    """Envia um único objeto (arquivo inteiro ou uma parte dele) para o
    Storage. Devolve `(status, mensagem_erro)` — nunca levanta exceção, quem
    chama decide o que fazer com o status.
    """
    headers_comuns = {
        "apikey": _SUPABASE_SERVICE_ROLE_KEY,
        "Authorization": f"Bearer {_SUPABASE_SERVICE_ROLE_KEY}",
    }
    try:
        _requisicao(
            f"{_SUPABASE_URL}/storage/v1/object/raw/{storage_path}",
            conteudo,
            {**headers_comuns, "Content-Type": content_type, "x-upsert": "true"},
        )
        return "sucesso", None
    except urllib.error.HTTPError as erro:
        corpo_erro = erro.read().decode("utf-8", "replace")[:500]
        return "erro", f"Storage upload falhou: HTTP {erro.code} — {corpo_erro}"
    except (urllib.error.URLError, TimeoutError) as erro:
        return "erro", f"Storage upload falhou: {erro}"


def reconstruir_arquivo(partes_em_ordem: list[Path], destino: Path) -> Path:
    """Remonta um arquivo original a partir das partes baixadas do Storage
    (a lista, na ordem certa, fica salva em `raw_ingestoes.metadata.partes`).
    Só concatena bytes — nenhuma transformação.
    """
    with open(destino, "wb") as saida:
        for parte in partes_em_ordem:
            saida.write(parte.read_bytes())
    return destino


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
    content_type = mimetypes.guess_type(arquivo.name)[0] or "application/octet-stream"
    metadata = dict(metadata or {})

    if tamanho_bytes <= LIMITE_PARTE_BYTES:
        storage_path = f"{fonte}/{arquivo.name}"
        status, mensagem_erro = _enviar_objeto(storage_path, conteudo, content_type)
        storage_path_final = f"raw/{storage_path}" if status == "sucesso" else None
    else:
        # Arquivo grande demais para um único objeto — divide em partes
        # sequenciais de LIMITE_PARTE_BYTES e envia cada uma separadamente.
        partes: list[str] = []
        status, mensagem_erro = "sucesso", None
        num_partes = -(-tamanho_bytes // LIMITE_PARTE_BYTES)  # arredonda para cima
        for indice in range(num_partes):
            inicio = indice * LIMITE_PARTE_BYTES
            pedaco = conteudo[inicio : inicio + LIMITE_PARTE_BYTES]
            nome_parte = f"{arquivo.name}.part{indice + 1:03d}"
            storage_path_parte = f"{fonte}/{nome_parte}"
            status_parte, erro_parte = _enviar_objeto(storage_path_parte, pedaco, "application/octet-stream")
            if status_parte == "erro":
                status, mensagem_erro = "erro", f"Falha na parte {indice + 1}/{num_partes}: {erro_parte}"
                break
            partes.append(f"raw/{storage_path_parte}")
        metadata["particionado"] = True
        metadata["partes"] = partes
        metadata["total_partes"] = num_partes
        storage_path_final = None

    headers_comuns = {
        "apikey": _SUPABASE_SERVICE_ROLE_KEY,
        "Authorization": f"Bearer {_SUPABASE_SERVICE_ROLE_KEY}",
    }
    corpo = json.dumps(
        {
            "fonte": fonte,
            "indicador": indicador,
            "script": script_rel,
            "storage_path": storage_path_final,
            "tamanho_bytes": tamanho_bytes,
            "sha256": sha256,
            "status": status,
            "mensagem_erro": mensagem_erro,
            "metadata": metadata or None,
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
