"""Coleta bruta do boletim mensal "Análise da Cesta Básica de Alimentos" (DIEESE/Conab)
via download direto do PDF público no site institucional do DIEESE.

Piloto técnico controlado — ver docs/08-decisoes-adr/0002-expansao-piloto-por-blocos.md
Fonte confirmada em: docs/04-fontes/dieese-publicacoes.md — investigação de lacunas
pós-Lote 06, 2026-09-22.

ACHADO: este indicador estava registrado como LACUNA (arquivo interno do DIEESE
`SM e Cesta desde 1979[...].xlsx` não obtido). Esta é uma FONTE PÚBLICA ALTERNATIVA —
o próprio DIEESE publica mensalmente, em parceria com a Conab, um boletim público em
PDF que contém exatamente o indicador "cesta básica x salário mínimo" citado no
material (Tabela 1 do boletim: valor da cesta, % do salário mínimo líquido, tempo de
trabalho necessário, por capital). NÃO é confirmado que é o mesmo arquivo/processo
interno usado pela equipe de conjuntura, mas é o produto oficial público do DIEESE
sobre o mesmo tema.

DECISÃO DE FORMATO DE EXTRAÇÃO: não há API nem CSV — apenas PDF mensal com nome de
arquivo previsível (AAAA/AAAAMMcestabasica.pdf). Este script tenta os últimos meses
a partir do mês corrente, em ordem decrescente, até encontrar o boletim mais recente
publicado (o ciclo de publicação tem alguma defasagem). A extração da tabela de dentro
do PDF (texto/número) é uma transformação e pertence à camada STAGING, não a este
script — aqui apenas o PDF bruto é salvo.

Este script NÃO transforma o dado.
"""

import urllib.error
import urllib.request
from datetime import date, timedelta
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from supabase_raw import registrar_coleta

DESTINO = Path(__file__).resolve().parents[3] / "data" / "raw" / "dieese_cesta_basica"


def _url(ano: int, mes: int) -> str:
    return f"https://www.dieese.org.br/analisecestabasica/{ano}/{ano}{mes:02d}cestabasica.pdf"


def _mes_mais_recente_disponivel(max_meses_para_tras: int = 6) -> tuple[int, int, bytes]:
    candidato = date.today().replace(day=1)
    for _ in range(max_meses_para_tras):
        ano, mes = candidato.year, candidato.month
        url = _url(ano, mes)
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        try:
            with urllib.request.urlopen(req, timeout=30) as resposta:
                return ano, mes, resposta.read()
        except urllib.error.HTTPError:
            candidato = (candidato - timedelta(days=1)).replace(day=1)
    raise RuntimeError(f"Nenhum boletim encontrado nos últimos {max_meses_para_tras} meses")


def coletar() -> Path:
    DESTINO.mkdir(parents=True, exist_ok=True)
    ano, mes, conteudo = _mes_mais_recente_disponivel()

    arquivo = DESTINO / f"cesta_basica_{ano}{mes:02d}.pdf"
    arquivo.write_bytes(conteudo)
    return arquivo


if __name__ == "__main__":
    caminho = coletar()
    tamanho_kb = caminho.stat().st_size / 1024
    print(f"Coleta concluída: {caminho} ({tamanho_kb:.1f} KB)")
    registrar_coleta(fonte=DESTINO.name, arquivo=caminho, script=__file__)
