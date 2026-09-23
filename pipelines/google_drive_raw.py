"""Helper para enviar arquivos grandes ao Google Drive, quando eles excedem o
limite de tamanho do Supabase Storage (ADR 0004 previu esse risco; confirmado
na prática com os microdados do CAGED — arquivos `CAGEDMOV` de ~50-57 MB
recebem HTTP 413 "Payload too large" do Storage do Supabase no plano atual).

===============================================================================
POR QUE UMA DEPENDÊNCIA EXTERNA AQUI (exceção documentada ao ADR 0001)
===============================================================================
Autenticar como conta de serviço do Google exige assinar um JWT com RSA-SHA256
usando a chave privada. A biblioteca padrão do Python não tem suporte a
assinatura RSA — as opções seriam (a) implementar RSA à mão (análise de ASN.1
da chave, exponenciação modular, padding PKCS#1) ou (b) usar `cryptography`,
a mesma biblioteca usada por baixo dos panos pelo SDK oficial do Google. Opção
(a) seria muito mais frágil e difícil de manter do que baixar um número maior
de dependência — mesma lógica já usada para justificar o uso de `curl` no
Comex Stat (ver `pipelines/ingestao/bloco_1_macroeconomia/coleta_balanca_comercial_comexstat.py`).
Instalar com: `pip install cryptography`.

===============================================================================
COMO FUNCIONA A AUTENTICAÇÃO DE CONTA DE SERVIÇO DO GOOGLE (JWT Bearer, RFC 7523)
===============================================================================
Diferente de um usuário fazendo login num navegador, uma conta de serviço se
autentica assinando, com sua própria chave privada, uma declaração ("claim")
dizendo quem ela é e o que quer fazer. O Google verifica a assinatura com a
chave pública correspondente (que ele já tem, associada ao `client_email`) e,
se bater, devolve um token de acesso temporário (1 hora). Passo a passo:

1. Monta um cabeçalho JWT (`{"alg": "RS256", "typ": "JWT"}`) e uma declaração
   (`{"iss": email_da_conta, "scope": ..., "aud": ..., "exp": ..., "iat": ...}`).
2. Codifica os dois em Base64URL (variante do Base64 sem `+`/`/`/`=`, usada em
   JWT) e junta com um ponto: `header_b64.claim_b64`.
3. Assina essa string com a chave privada (RSA-SHA256) — é isso que só a
   biblioteca `cryptography` faz aqui, o resto é tudo `urllib`/`base64` puros.
4. Codifica a assinatura em Base64URL e forma o JWT completo:
   `header_b64.claim_b64.assinatura_b64`.
5. Envia esse JWT para `https://oauth2.googleapis.com/token`, pedindo um
   token de acesso — a resposta é um token que vale por 1 hora.

===============================================================================
COMO FUNCIONA O UPLOAD "RESUMABLE" DO DRIVE (necessário para arquivos grandes)
===============================================================================
Para arquivos grandes, o Drive recomenda o modo de upload "resumable": em vez
de mandar o arquivo inteiro numa única requisição (que falha por completo se
a conexão cair no meio — exatamente o problema que motivou este script),
primeiro você abre uma "sessão de upload" (a API devolve uma URL só para essa
sessão), depois envia o conteúdo para essa URL — podendo perguntar, a qualquer
momento, quantos bytes o servidor já recebeu, e continuar de onde parou.
"""

from __future__ import annotations

import base64
import json
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding

_RAIZ = Path(__file__).resolve().parent.parent

DRIVE_SCOPE = "https://www.googleapis.com/auth/drive.file"
TOKEN_URL = "https://oauth2.googleapis.com/token"
UPLOAD_URL = "https://www.googleapis.com/upload/drive/v3/files?uploadType=resumable&supportsAllDrives=true"


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
        variaveis[chave.strip()] = valor.strip().strip('"')
    return variaveis


_ENV = {**_carregar_env(), **__import__("os").environ}
_EMAIL = _ENV.get("GOOGLE_SERVICE_ACCOUNT_EMAIL")
_CHAVE_PRIVADA_PEM = _ENV.get("GOOGLE_SERVICE_ACCOUNT_PRIVATE_KEY", "").replace("\\n", "\n")
_PASTA_CAGED = _ENV.get("GOOGLE_DRIVE_FOLDER_CAGED")


def _base64url(dados: bytes) -> str:
    """Base64 "seguro para URL": troca `+`/`/` por `-`/`_` e remove o
    preenchimento `=` do final — é o formato exigido pelo padrão JWT (RFC 7519),
    diferente do Base64 comum que `base64.b64encode` produz por padrão.
    """
    return base64.urlsafe_b64encode(dados).rstrip(b"=").decode("ascii")


def _obter_token_de_acesso() -> str:
    """Executa o fluxo JWT Bearer (ver docstring do módulo) e devolve um
    token de acesso válido por 1 hora.
    """
    agora = int(time.time())
    cabecalho = {"alg": "RS256", "typ": "JWT"}
    declaracao = {
        "iss": _EMAIL,
        "scope": DRIVE_SCOPE,
        "aud": TOKEN_URL,
        "exp": agora + 3600,
        "iat": agora,
    }
    nao_assinado = f"{_base64url(json.dumps(cabecalho).encode())}.{_base64url(json.dumps(declaracao).encode())}"

    chave_privada = serialization.load_pem_private_key(_CHAVE_PRIVADA_PEM.encode(), password=None)
    assinatura = chave_privada.sign(nao_assinado.encode(), padding.PKCS1v15(), hashes.SHA256())

    jwt = f"{nao_assinado}.{_base64url(assinatura)}"

    dados = urllib.parse.urlencode(
        {"grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer", "assertion": jwt}
    ).encode()
    req = urllib.request.Request(TOKEN_URL, data=dados, method="POST")
    with urllib.request.urlopen(req, timeout=30) as resposta:
        return json.loads(resposta.read().decode())["access_token"]


def _abrir_sessao_de_upload(token: str, nome_arquivo: str, tamanho_bytes: int, content_type: str) -> str:
    """Abre uma sessão de upload "resumable" e devolve a URL dessa sessão
    (vem no cabeçalho HTTP `Location` da resposta).
    """
    metadados = json.dumps({"name": nome_arquivo, "parents": [_PASTA_CAGED]}).encode()
    req = urllib.request.Request(
        UPLOAD_URL,
        data=metadados,
        method="POST",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json; charset=UTF-8",
            "X-Upload-Content-Type": content_type,
            "X-Upload-Content-Length": str(tamanho_bytes),
        },
    )
    with urllib.request.urlopen(req, timeout=30) as resposta:
        return resposta.headers["Location"]


def _enviar_conteudo(url_sessao: str, conteudo: bytes, content_type: str, max_tentativas: int = 5) -> dict:
    """Envia o conteúdo do arquivo para a sessão de upload, com retomada em
    caso de falha. Antes de cada tentativa (exceto a primeira), pergunta ao
    Drive quantos bytes ele já recebeu (`Content-Range: bytes */total`, sem
    corpo) e reenvia só o restante — o mesmo princípio de retomada já usado
    nos scripts de FTP (CAGED) e curl (Comex Stat) deste piloto.
    """
    tamanho_total = len(conteudo)
    offset = 0

    for tentativa in range(1, max_tentativas + 1):
        try:
            req = urllib.request.Request(
                url_sessao,
                data=conteudo[offset:],
                method="PUT",
                headers={
                    "Content-Length": str(tamanho_total - offset),
                    "Content-Range": f"bytes {offset}-{tamanho_total - 1}/{tamanho_total}",
                    "Content-Type": content_type,
                },
            )
            with urllib.request.urlopen(req, timeout=180) as resposta:
                return json.loads(resposta.read().decode())
        except (urllib.error.URLError, TimeoutError):
            if tentativa == max_tentativas:
                raise
            # pergunta ao Drive quanto já recebeu, para retomar só do que falta
            req_status = urllib.request.Request(
                url_sessao,
                method="PUT",
                headers={"Content-Range": f"bytes */{tamanho_total}"},
            )
            try:
                urllib.request.urlopen(req_status, timeout=30)
            except urllib.error.HTTPError as erro:
                intervalo = erro.headers.get("Range")  # ex.: "bytes=0-1048575"
                offset = int(intervalo.split("-")[1]) + 1 if intervalo else 0


def enviar_arquivo_grande(caminho: Path, mime_type: str = "application/octet-stream") -> dict:
    """Envia `caminho` para a pasta do Drive configurada em
    `GOOGLE_DRIVE_FOLDER_CAGED`. Devolve o objeto de arquivo do Drive
    (contém `id` e, quando disponível, `webViewLink`).

    Levanta exceção se `.env` não tiver as credenciais do Google configuradas
    — diferente de `registrar_coleta()` (Supabase), que falha silenciosamente,
    porque este helper só é chamado explicitamente quando já se sabe que o
    Supabase não é suficiente (arquivo grande demais), então uma falha aqui
    deve ser visível, não silenciosa.
    """
    if not _EMAIL or not _CHAVE_PRIVADA_PEM or not _PASTA_CAGED:
        raise RuntimeError(
            "Credenciais do Google Drive não configuradas em .env "
            "(GOOGLE_SERVICE_ACCOUNT_EMAIL / GOOGLE_SERVICE_ACCOUNT_PRIVATE_KEY / GOOGLE_DRIVE_FOLDER_CAGED)"
        )

    conteudo = caminho.read_bytes()
    token = _obter_token_de_acesso()
    url_sessao = _abrir_sessao_de_upload(token, caminho.name, len(conteudo), mime_type)
    return _enviar_conteudo(url_sessao, conteudo, mime_type)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python3 google_drive_raw.py <caminho-do-arquivo>", file=sys.stderr)
        sys.exit(1)

    caminho_arquivo = Path(sys.argv[1])
    resultado = enviar_arquivo_grande(caminho_arquivo)
    print(f"Enviado ao Drive: {resultado.get('webViewLink', resultado.get('id'))}")
