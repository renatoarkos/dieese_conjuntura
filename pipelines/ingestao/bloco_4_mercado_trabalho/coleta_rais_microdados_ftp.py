"""Coleta bruta dos microdados da RAIS (Relação Anual de Informações Sociais)
via FTP público do MTE/PDET — mesmo produtor e mesma infraestrutura já usada
para o Novo CAGED.

===============================================================================
POR QUE RAIS, E POR QUE AGORA
===============================================================================
Não fazia parte do catálogo original de 38 indicadores do DIEESE — é expansão
de escopo, autorizada explicitamente pelo responsável do projeto em
2026-10-14 ("Tudo que for dados que nos ajudem a trazer informações
importantes... pode integrar a plataforma. Não precisa pedir autorização").
Pesquisa exploratória anterior (`docs/04-fontes/outras-instituicoes-2026-09.md`,
2026-09-23) já tinha confirmado o acesso técnico — este script executa o que
aquela pesquisa apontou como caminho estável.

===============================================================================
ESTRUTURA REAL DO FTP (confirmada por listagem direta, 2026-10-14)
===============================================================================
`/pdet/microdados/RAIS/{ano}/` contém, para cada ano, um arquivo de
estabelecimentos (RAIS_ESTAB_PUB.7z) e os VÍNCULOS empregatícios partidos em
7 arquivos regionais (não um único arquivo nacional):
  RAIS_VINC_PUB_NORTE.7z, _NORDESTE, _CENTRO_OESTE, _MG_ES_RJ, _SP, _SUL, _NI
(NI = "não identificado", arquivo residual pequeno). Juntos, os 7 arquivos de
vínculos passam de 3,7 GB comprimidos (ano de 2024) — ordens de grandeza
maior que qualquer outra fonte já integrada neste projeto. Por isso este
script baixa SÓ os vínculos (não o arquivo de estabelecimentos, que serve a
um propósito diferente — contagem de empresas, não de trabalhadores).

===============================================================================
POR QUE NÃO VAI PARA O SUPABASE STORAGE (mesma exceção já registrada para o
histórico do Novo CAGED — ver ESTADO_DO_PROJETO.md)
===============================================================================
`supabase_raw.py` particiona automaticamente arquivos >45 MB — para um
arquivo de ~1 GB (SP) isso significa dezenas de partes, um upload muito mais
lento que o download original, sem benefício real (o dado já está público e
reobtível a qualquer momento pelo FTP oficial). Por isso este script grava
só localmente em `data/raw/mte_rais/`, como já é feito para o backfill
histórico do CAGED — rastreabilidade mantida via este script + data+hora do
arquivo, não via Supabase Storage.

===============================================================================
O QUE ESTE SCRIPT FAZ
===============================================================================
`coletar(ano)` baixa os 7 arquivos regionais de vínculos de um ano para
`data/raw/mte_rais/`, pulando qualquer um que já exista localmente (permite
interromper e retomar). Não extrai nem processa — isso é
`pipelines/curated/transformar_rais_dieese.py`.
"""

import ftplib
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

FTP_HOST = "ftp.mtps.gov.br"
FTP_BASE = "/pdet/microdados/RAIS"
DESTINO = Path(__file__).resolve().parents[3] / "data" / "raw" / "mte_rais"

REGIOES = ["NORTE", "NORDESTE", "CENTRO_OESTE", "MG_ES_RJ", "SP", "SUL", "NI"]


def _conectar() -> ftplib.FTP:
    ftp = ftplib.FTP(FTP_HOST, timeout=120, encoding="latin-1")
    ftp.login()
    return ftp


def coletar(ano: int) -> list[Path]:
    DESTINO.mkdir(parents=True, exist_ok=True)
    ftp = _conectar()
    ftp.cwd(f"{FTP_BASE}/{ano}")

    arquivos = []
    for regiao in REGIOES:
        destino = DESTINO / f"RAIS_VINC_PUB_{regiao}_{ano}.7z"
        if destino.exists():
            print(f"{regiao}: já existe localmente, pulando.")
            arquivos.append(destino)
            continue
        print(f"{regiao}: baixando...")
        with open(destino, "wb") as f:
            ftp.retrbinary(f"RETR RAIS_VINC_PUB_{regiao}.7z", f.write)
        arquivos.append(destino)
        print(f"{regiao}: concluído ({destino.stat().st_size / 1e6:.0f} MB).")
    ftp.quit()
    return arquivos


if __name__ == "__main__":
    ano = int(sys.argv[1]) if len(sys.argv) > 1 else 2024
    for caminho in coletar(ano):
        print(f"Disponível: {caminho}")
