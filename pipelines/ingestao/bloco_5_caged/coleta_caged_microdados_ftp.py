"""Coleta bruta dos microdados do Novo CAGED via FTP público do MTE/PDET.

Piloto técnico controlado — ver docs/04-fontes/mte-caged.md e
docs/08-decisoes-adr/0002-expansao-piloto-por-blocos.md.

DECISÃO DE FORMATO DE EXTRAÇÃO (registrada aqui por não ter API disponível — ver
docs/04-fontes/mte-caged.md para o comparativo completo):
  - O canal de "tabelas prontas" do Novo CAGED (as que mais se aproximam das Tabelas
    1, 2, 6.1, 9 citadas pelo material do DIEESE) é hoje distribuído via uma pasta do
    Google Drive sem URL HTTP fixa — inadequado para automação estável.
  - O FTP de microdados brutos (ftp.mtps.gov.br) É estável, testado e público, sem
    autenticação. Por isso foi escolhido como fonte de coleta, mesmo entregando
    registros individuais (não as tabelas agregadas prontas).
  - A reconstrução das tabelas agregadas do DIEESE (salário médio de admissão/
    desligamento; saldo por grupamento de atividade e nível geográfico) a partir
    destes microdados é uma transformação que pertence à camada STAGING, não à RAW,
    e NÃO está implementada neste piloto.

Este script coleta apenas o MÊS MAIS RECENTE disponível no FTP (detectado
automaticamente), não o histórico completo desde jan/2020 — uma coleta retroativa
completa (~80 meses, dezenas de GB) é uma decisão de maior porte (volume/tempo de
download), deixada para uma expansão futura deliberada, não para este piloto.

Este script NÃO transforma nem descompacta o dado — grava os arquivos .7z
exatamente como o FTP os entrega (RAW).
"""

import ftplib
from datetime import datetime, timezone
from pathlib import Path

FTP_HOST = "ftp.mtps.gov.br"
FTP_BASE = "/pdet/microdados/NOVO CAGED"
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from supabase_raw import registrar_coleta

DESTINO = Path(__file__).resolve().parents[3] / "data" / "raw" / "mte_caged"


def _mes_mais_recente(ftp: ftplib.FTP) -> tuple[str, str]:
    ftp.cwd(FTP_BASE)
    anos = sorted(n for n in ftp.nlst() if n.isdigit())
    ano_mais_recente = anos[-1]
    ftp.cwd(ano_mais_recente)
    meses = sorted(n for n in ftp.nlst() if n.isdigit())
    mes_mais_recente = meses[-1]
    return ano_mais_recente, mes_mais_recente


def _baixar_com_retomada(ftp: ftplib.FTP, nome_remoto: str, destino: Path, max_tentativas: int = 8) -> None:
    """Baixa um arquivo do FTP com retomada em caso de queda de conexão.

    Observado empiricamente nesta rodada: a transferência do arquivo maior
    (CAGEDMOV, ~55 MB) é interrompida antes de completar, de forma inconsistente —
    instabilidade de rede, não erro de comando. Usa o comando FTP REST para retomar
    a partir do byte já recebido, reabrindo a conexão de controle quando necessário.
    """
    for tentativa in range(1, max_tentativas + 1):
        offset = destino.stat().st_size if destino.exists() else 0
        try:
            with open(destino, "ab") as f:
                if offset:
                    ftp.sendcmd("TYPE I")
                    ftp.voidcmd(f"REST {offset}")
                ftp.retrbinary(f"RETR {nome_remoto}", f.write, rest=offset or None)
            return
        except (OSError, ftplib.error_temp, ftplib.error_proto):
            if tentativa == max_tentativas:
                raise
            # reconecta para a próxima tentativa — a conexão de controle pode ter caído junto.
            try:
                ftp.close()
            except Exception:
                pass
            ftp.connect(FTP_HOST, timeout=60)
            ftp.login()
            ftp.cwd(ftp.pwd())


def coletar() -> list[Path]:
    DESTINO.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

    ftp = ftplib.FTP(FTP_HOST, timeout=60)
    ftp.encoding = "latin-1"  # o servidor devolve nomes de arquivo fora de UTF-8 puro
    ftp.login()  # anônimo — sem credenciais, servidor público
    try:
        ano, mes = _mes_mais_recente(ftp)
        pasta_remota = f"{FTP_BASE}/{ano}/{mes}"
        ftp.cwd(pasta_remota)
        arquivos_remotos = [n for n in ftp.nlst() if n.lower().endswith(".7z")]

        arquivos_locais = []
        for nome in arquivos_remotos:
            destino_arquivo = DESTINO / f"{nome.removesuffix('.7z')}_{timestamp}.7z"
            ftp.cwd(pasta_remota)
            _baixar_com_retomada(ftp, nome, destino_arquivo)
            arquivos_locais.append(destino_arquivo)
        return arquivos_locais
    finally:
        try:
            ftp.quit()
        except Exception:
            pass


if __name__ == "__main__":
    for caminho in coletar():
        tamanho_mb = caminho.stat().st_size / (1024 * 1024)
        print(f"Coleta concluída: {caminho} ({tamanho_mb:.1f} MB)")
        registrar_coleta(fonte=DESTINO.name, arquivo=caminho, script=__file__)
