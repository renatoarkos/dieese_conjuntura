"""Coleta bruta da balança comercial brasileira (exportações e importações por NCM) via
download estruturado do Comex Stat (MDIC).

Piloto técnico controlado — ver docs/08-decisoes-adr/0002-expansao-piloto-por-blocos.md
Fonte confirmada em: docs/04-fontes/mdic-tesouro.md — Lote 05b, com URLs de CSV extraídas
diretamente da página oficial de dados brutos do MDIC nesta rodada.

DECISÃO TÉCNICA — uso de `curl` via subprocess em vez de `urllib` puro: o servidor
`balanca.mdic.gov.br` envia uma cadeia de certificado TLS incompleta (falta o
intermediário), o que faz o módulo `ssl` do Python (mesmo com o pacote `certifi`)
rejeitar a conexão com CERTIFICATE_VERIFY_FAILED — confirmado nesta rodada. O `curl`
do sistema operacional resolve a cadeia corretamente (testado e confirmado: HTTP 200,
CSV real). Este é um problema confirmado de configuração do lado do servidor do MDIC,
não uma vulnerabilidade a contornar — por isso a escolha foi usar uma ferramenta que já
faz a verificação de certificado corretamente (curl), em vez de desabilitar a
verificação de certificado no Python (o que enfraqueceria a segurança da conexão).
`curl` é amplamente disponível em ambientes Linux/macOS/Windows modernos.

Este script coleta apenas o ano corrente (dados mais recentes) — não o histórico
completo desde 1997 (cada arquivo anual tem ~100 MB; um backfill completo é uma decisão
de maior porte, deixada para expansão futura deliberada).

Este script NÃO transforma o dado.
"""

import subprocess
from datetime import datetime, timezone
from pathlib import Path

ANO_ATUAL = datetime.now().year
URLS = {
    "exportacao": f"https://balanca.mdic.gov.br/balanca/bd/comexstat-bd/ncm/EXP_{ANO_ATUAL}.csv",
    "importacao": f"https://balanca.mdic.gov.br/balanca/bd/comexstat-bd/ncm/IMP_{ANO_ATUAL}.csv",
}
DESTINO = Path(__file__).resolve().parents[3] / "data" / "raw" / "comexstat"


def _baixar_com_retomada(url: str, destino_arquivo: Path, max_tentativas: int = 60) -> None:
    """Baixa um arquivo grande com retomada em caso de queda de conexão.

    Observado empiricamente nesta rodada: o servidor do MDIC reseta a conexão em
    pontos aleatórios de downloads grandes — cada tentativa individual costuma
    transferir de ~100 KB a ~2 MB antes de cair, de forma inconsistente. Não é uma
    falha de autenticação/URL (HTTP 200/206 confirmado em toda tentativa), é
    instabilidade de rede específica deste ambiente. `curl -C -` retoma a partir do
    byte já baixado, em vez de recomeçar do zero — por isso um número alto de
    tentativas pequenas ainda converge para o arquivo completo.
    """
    for tentativa in range(1, max_tentativas + 1):
        try:
            # --speed-limit/--speed-time: aborta cedo se a conexão travar (em vez de
            # esperar o timeout inteiro) — observado nesta rodada que a conexão tanto
            # reseta quanto, às vezes, trava sem enviar dado algum.
            resultado = subprocess.run(
                [
                    "curl", "-sS", "-C", "-", "--connect-timeout", "15",
                    "--speed-limit", "1000", "--speed-time", "10",
                    "-o", str(destino_arquivo), url,
                ],
                capture_output=True,
                timeout=45,
            )
        except subprocess.TimeoutExpired:
            if tentativa == max_tentativas:
                raise RuntimeError(f"Falha ao baixar {url}: timeout em todas as {max_tentativas} tentativas")
            continue

        if resultado.returncode == 0:
            return
        # código 56 = "Recv failure: Connection was reset"; 28 = timeout do curl — ambos retomáveis.
        if resultado.returncode not in (56, 18, 28) or tentativa == max_tentativas:
            raise RuntimeError(
                f"Falha ao baixar {url} após {tentativa} tentativa(s): "
                f"curl código {resultado.returncode} — "
                f"{resultado.stderr.decode(errors='replace')}"
            )

    raise RuntimeError(f"Falha ao baixar {url}: número máximo de tentativas excedido")


def coletar() -> list[Path]:
    DESTINO.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    arquivos = []
    for nome, url in URLS.items():
        destino_arquivo = DESTINO / f"{nome}_ncm_{ANO_ATUAL}_{timestamp}.csv"
        _baixar_com_retomada(url, destino_arquivo)
        arquivos.append(destino_arquivo)
    return arquivos


if __name__ == "__main__":
    for caminho in coletar():
        tamanho_mb = caminho.stat().st_size / (1024 * 1024)
        print(f"Coleta concluída: {caminho} ({tamanho_mb:.1f} MB)")
