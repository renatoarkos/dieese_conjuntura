"""Coleta bruta dos microdados do Novo CAGED via FTP público do MTE/PDET.

===============================================================================
O QUE É ESTE INDICADOR E POR QUE MICRODADOS (E NÃO API)
===============================================================================
O Novo CAGED (Cadastro Geral de Empregados e Desempregados) registra toda
admissão e desligamento formal de emprego no Brasil. O material do DIEESE usa
duas tabelas agregadas a partir dele: "salário médio de admissão/desligamento"
e "saldo de admissões/desligamentos por grupamento de atividade".

Essas tabelas PRONTAS não têm fonte automatizável estável — o canal oficial de
"tabelas prontas" do Novo CAGED é uma pasta do Google Drive sem URL HTTP fixa
(ver docs/04-fontes/mte-caged.md). O que É estável, público e sem necessidade
de login é o FTP de MICRODADOS BRUTOS (um registro por admissão/desligamento,
não a tabela já somada). Por isso este script baixa microdados, não a tabela
final — a agregação (somar/tabular os microdados nas tabelas que o DIEESE usa)
é uma transformação que pertence à camada STAGING, não à RAW, e não está
implementada aqui.

===============================================================================
DUAS FORMAS DE USAR ESTE SCRIPT
===============================================================================
1. `coletar()` — baixa APENAS o mês mais recente disponível no FTP. É o que
   roda automaticamente toda semana (ver .github/workflows/motores-semanais.yml).
   Guarda o arquivo com um timestamp no nome, porque o mesmo mês pode ser
   republicado pelo MTE com pequenas correções nos dias seguintes à divulgação
   — queremos ver essas revisões, não sobrescrever silenciosamente.

2. `coletar_periodo(mes_inicio, mes_fim)` — baixa TODOS os meses de um
   intervalo (ex.: desde jan/2020, quando a metodologia do Novo CAGED começou,
   até hoje). É para montar uma série histórica local, não para rodar toda
   semana — por isso não tem timestamp no nome (o mês é o identificador) e
   pula arquivos que já existem localmente com o tamanho certo, para poder ser
   interrompido e retomado depois sem perder o que já foi baixado.

Para rodar a coleta histórica pelo terminal:

    python3 pipelines/ingestao/bloco_5_caged/coleta_caged_microdados_ftp.py --historico
    python3 pipelines/ingestao/bloco_5_caged/coleta_caged_microdados_ftp.py --historico 202001 202412

Este script NÃO transforma nem descompacta o dado — grava os arquivos .7z
exatamente como o FTP os entrega (RAW).
"""

import ftplib
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from supabase_raw import registrar_coleta

FTP_HOST = "ftp.mtps.gov.br"
FTP_BASE = "/pdet/microdados/NOVO CAGED"
DESTINO = Path(__file__).resolve().parents[3] / "data" / "raw" / "mte_caged"

# Mês em que o Novo CAGED (metodologia atual) começou a publicar microdados
# nesta estrutura de pastas — não há dados anteriores a este mês no FTP.
INICIO_NOVO_CAGED = "202001"


# ------------------------------------------------------------------------
# PASSO 1 — conectar e navegar no FTP
# ------------------------------------------------------------------------
def _conectar() -> ftplib.FTP:
    """Abre uma conexão anônima com o FTP público do MTE/PDET.

    Não precisa de usuário/senha — é um servidor de dados abertos. O parâmetro
    `encoding = "latin-1"` é necessário porque o servidor devolve nomes de
    arquivo/pasta que não são UTF-8 puro; sem isso, `ftp.nlst()` lança
    `UnicodeDecodeError` (erro observado e corrigido durante o Discovery).
    """
    ftp = ftplib.FTP(FTP_HOST, timeout=60)
    ftp.encoding = "latin-1"
    ftp.login()
    return ftp


def _listar_meses_disponiveis(ftp: ftplib.FTP) -> list[str]:
    """Devolve todos os meses publicados no FTP, no formato 'AAAAMM', em ordem
    crescente. A estrutura de pastas do FTP é .../NOVO CAGED/{ano}/{ano}{mes}/.
    """
    ftp.cwd(FTP_BASE)
    anos = sorted(n for n in ftp.nlst() if n.isdigit())
    meses: list[str] = []
    for ano in anos:
        ftp.cwd(f"{FTP_BASE}/{ano}")
        meses.extend(sorted(n for n in ftp.nlst() if n.isdigit()))
    return meses


# ------------------------------------------------------------------------
# PASSO 2 — baixar um arquivo, com retomada em caso de queda de conexão
# ------------------------------------------------------------------------
def _baixar_com_retomada(ftp: ftplib.FTP, nome_remoto: str, destino: Path, max_tentativas: int = 8) -> None:
    """Baixa um arquivo do FTP, retomando de onde parou se a conexão cair.

    Observado empiricamente durante o Discovery: a transferência do arquivo
    maior (CAGEDMOV, ~50 MB) às vezes é interrompida antes de completar, de
    forma inconsistente — é instabilidade de rede do ambiente, não erro do
    servidor (confirmado testando o mesmo download fora deste ambiente). A
    técnica usada é a mesma de um "continuar download" de navegador: o comando
    FTP `REST <bytes>` diz ao servidor para começar a enviar a partir de um
    certo byte, em vez de do início.
    """
    for tentativa in range(1, max_tentativas + 1):
        offset = destino.stat().st_size if destino.exists() else 0
        try:
            with open(destino, "ab") as f:  # "ab" = append binary, continua o arquivo existente
                if offset:
                    ftp.sendcmd("TYPE I")  # modo binário, exigido pelo protocolo antes de REST
                    ftp.voidcmd(f"REST {offset}")
                ftp.retrbinary(f"RETR {nome_remoto}", f.write, rest=offset or None)
            return
        except (OSError, ftplib.error_temp, ftplib.error_proto):
            if tentativa == max_tentativas:
                raise
            # A conexão de controle pode ter caído junto com a de dados —
            # a única forma confiável de continuar é reconectar do zero.
            try:
                ftp.close()
            except Exception:
                pass
            ftp.connect(FTP_HOST, timeout=60)
            ftp.login()


# ------------------------------------------------------------------------
# PASSO 3a — coleta recorrente: só o mês mais recente (roda toda semana)
# ------------------------------------------------------------------------
def coletar() -> list[Path]:
    """Baixa os microdados do mês mais recente publicado no FTP.

    Usado pelo workflow agendado (motores-semanais.yml). Cada execução grava
    um arquivo novo com timestamp — não sobrescreve a coleta anterior — porque
    o MTE às vezes republica o mesmo mês com pequenas correções nos dias
    seguintes à primeira divulgação, e queremos preservar esse histórico de
    revisões, não apenas a versão mais recente.
    """
    DESTINO.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

    ftp = _conectar()
    try:
        mes_mais_recente = _listar_meses_disponiveis(ftp)[-1]
        ano = mes_mais_recente[:4]
        pasta_remota = f"{FTP_BASE}/{ano}/{mes_mais_recente}"
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


# ------------------------------------------------------------------------
# PASSO 3b — coleta histórica: um intervalo de meses (roda sob demanda)
# ------------------------------------------------------------------------
def coletar_periodo(mes_inicio: str = INICIO_NOVO_CAGED, mes_fim: str | None = None) -> list[Path]:
    """Baixa os microdados de TODOS os meses entre `mes_inicio` e `mes_fim`
    (formato 'AAAAMM', ambos incluídos). Se `mes_fim` não for informado, usa o
    mês mais recente disponível no FTP.

    Diferente de `coletar()`: os nomes de arquivo NÃO levam timestamp (o mês
    já identifica o arquivo de forma única) e meses já baixados localmente,
    com o mesmo tamanho do arquivo remoto, são pulados — assim é seguro parar
    esta coleta no meio (ex.: perda de conexão) e rodar de novo depois sem
    baixar tudo outra vez.
    """
    DESTINO.mkdir(parents=True, exist_ok=True)

    ftp = _conectar()
    try:
        todos_os_meses = _listar_meses_disponiveis(ftp)
        limite_fim = mes_fim or todos_os_meses[-1]
        meses_no_intervalo = [m for m in todos_os_meses if mes_inicio <= m <= limite_fim]

        arquivos_locais = []
        for mes in meses_no_intervalo:
            ano = mes[:4]
            pasta_remota = f"{FTP_BASE}/{ano}/{mes}"
            ftp.cwd(pasta_remota)
            arquivos_remotos = {n: ftp.size(n) for n in ftp.nlst() if n.lower().endswith(".7z")}

            for nome, tamanho_remoto in arquivos_remotos.items():
                destino_arquivo = DESTINO / nome  # sem timestamp: 1 arquivo por mês, de forma estável
                ja_completo = destino_arquivo.exists() and destino_arquivo.stat().st_size == tamanho_remoto
                if ja_completo:
                    print(f"Já baixado, pulando: {destino_arquivo}")
                    arquivos_locais.append(destino_arquivo)
                    continue
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
    if "--historico" in sys.argv:
        posicao = sys.argv.index("--historico")
        argumentos_extras = sys.argv[posicao + 1 :]
        inicio = argumentos_extras[0] if len(argumentos_extras) >= 1 else INICIO_NOVO_CAGED
        fim = argumentos_extras[1] if len(argumentos_extras) >= 2 else None
        arquivos = coletar_periodo(inicio, fim)
    else:
        arquivos = coletar()

    for caminho in arquivos:
        tamanho_mb = caminho.stat().st_size / (1024 * 1024)
        print(f"Coleta concluída: {caminho} ({tamanho_mb:.1f} MB)")
        registrar_coleta(fonte=DESTINO.name, arquivo=caminho, script=__file__)
