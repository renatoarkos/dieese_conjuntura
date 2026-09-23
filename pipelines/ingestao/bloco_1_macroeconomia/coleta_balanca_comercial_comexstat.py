"""Coleta bruta da balança comercial brasileira (exportações e importações por NCM) via
download estruturado do Comex Stat (MDIC).

Piloto técnico controlado — ver docs/08-decisoes-adr/0002-expansao-piloto-por-blocos.md
Fonte confirmada em: docs/04-fontes/mdic-tesouro.md — Lote 05b, com URLs de CSV extraídas
diretamente da página oficial de dados brutos do MDIC nesta rodada.

===============================================================================
POR QUE `curl` (VIA SUBPROCESS) EM VEZ DE `urllib` PURO
===============================================================================
Todos os demais scripts deste piloto usam `urllib.request` (biblioteca padrão
do Python) para HTTP, seguindo a decisão de stack mínima do ADR 0001. Este
script é a exceção deliberada: o servidor `balanca.mdic.gov.br` envia uma
cadeia de certificado TLS incompleta (falta o certificado intermediário), o
que faz o módulo `ssl` do Python — mesmo com o pacote `certifi` instalado —
rejeitar a conexão com o erro `CERTIFICATE_VERIFY_FAILED`. Isso foi
confirmado nesta rodada como um problema de configuração do lado do servidor
do MDIC, não uma vulnerabilidade real a se contornar.

O `curl` do sistema operacional resolve essa mesma cadeia de certificado
corretamente (testado e confirmado: HTTP 200, CSV real) — por isso a escolha
foi usar uma ferramenta que já faz a verificação de certificado de forma
correta e completa (curl), em vez da alternativa mais fácil e mais arriscada
de desabilitar a verificação de certificado dentro do Python (o que
enfraqueceria a segurança da conexão para qualquer outro uso). `curl` é
amplamente disponível em ambientes Linux/macOS/Windows modernos, então essa
troca não compromete a portabilidade do piloto.

===============================================================================
POR QUE HÁ LÓGICA DE RETOMADA (RESUME) NO DOWNLOAD
===============================================================================
Os arquivos anuais de exportação/importação por NCM são grandes (~70-120 MB).
Foi observado empiricamente, nesta rodada, que o servidor do MDIC reseta a
conexão em pontos aleatórios durante o download desses arquivos grandes —
cada tentativa individual costuma transferir de ~100 KB a alguns MB antes de
cair, de forma inconsistente. Não é uma falha de autenticação ou de URL (o
servidor responde HTTP 200/206 em toda tentativa) — é instabilidade de rede
específica deste tipo de transferência. A função `_baixar_com_retomada`
lida com isso chamando `curl -C -` (retoma a partir do byte já baixado, em
vez de recomeçar do zero) repetidamente, até o arquivo ficar completo — um
número alto de tentativas pequenas converge para o arquivo inteiro sem
desperdiçar o que já foi baixado a cada queda.

===============================================================================
ESCOPO DESTA COLETA
===============================================================================
Este script coleta apenas o ano corrente (dados mais recentes) — não o
histórico completo desde 1997. Um backfill do histórico completo é uma
decisão de maior porte (cada arquivo anual tem ~100 MB), deixada para uma
expansão futura deliberada, não incluída neste piloto.

===============================================================================
O QUE ESTE SCRIPT FAZ, PASSO A PASSO
===============================================================================
1. Monta as URLs de exportação e importação do ano corrente (`URLS`).
2. Para cada URL, baixa o CSV com retomada automática em caso de queda de
   conexão (`_baixar_com_retomada`), escrevendo diretamente no arquivo de
   destino em `data/raw/comexstat/` — não há um passo separado de "salvar",
   porque o `curl` já grava no disco enquanto baixa (arquivos deste tamanho
   não deveriam ficar inteiros na memória do processo).
3. Registra cada arquivo no Supabase — Storage + linha em `raw_ingestoes`
   (`registrar_coleta`, importado de `pipelines/supabase_raw.py`).

Este script NÃO transforma o dado — grava o CSV exatamente como o MDIC o
publica, respeitando o princípio de que a camada RAW nunca deve ser editada
manualmente ou pré-processada (ver CLAUDE.md, seção DADOS). Filtrar por NCM,
agregar por período ou qualquer outra conta é trabalho da camada STAGING,
feito depois, a partir do arquivo que este script grava — nunca aqui.
"""

import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from supabase_raw import registrar_coleta

ANO_ATUAL = datetime.now().year

# URLs de download direto do CSV, extraídas da página oficial de dados
# brutos do MDIC (ver docs/04-fontes/mdic-tesouro.md). Um arquivo por fluxo
# (exportação/importação), sempre do ano corrente.
URLS = {
    "exportacao": f"https://balanca.mdic.gov.br/balanca/bd/comexstat-bd/ncm/EXP_{ANO_ATUAL}.csv",
    "importacao": f"https://balanca.mdic.gov.br/balanca/bd/comexstat-bd/ncm/IMP_{ANO_ATUAL}.csv",
}

DESTINO = Path(__file__).resolve().parents[3] / "data" / "raw" / "comexstat"


# ------------------------------------------------------------------------
# PASSO 1 — baixar um arquivo com retomada em caso de queda de conexão
# ------------------------------------------------------------------------
def _baixar_com_retomada(url: str, destino_arquivo: Path, max_tentativas: int = 60) -> None:
    """Baixa um arquivo grande com retomada em caso de queda de conexão.

    Observado empiricamente nesta rodada: o servidor do MDIC reseta a conexão
    em pontos aleatórios de downloads grandes — cada tentativa individual
    costuma transferir de ~100 KB a ~2 MB antes de cair, de forma
    inconsistente. Não é uma falha de autenticação/URL (HTTP 200/206
    confirmado em toda tentativa), é instabilidade de rede específica deste
    ambiente. `curl -C -` retoma a partir do byte já baixado, em vez de
    recomeçar do zero — por isso um número alto de tentativas pequenas ainda
    converge para o arquivo completo.
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


# ------------------------------------------------------------------------
# Orquestração: baixa exportação e importação, nesta ordem
# ------------------------------------------------------------------------
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
        registrar_coleta(fonte=DESTINO.name, arquivo=caminho, script=__file__)
