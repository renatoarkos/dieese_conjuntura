"""Coleta bruta do boletim mensal "De Olho nas Negociações" (DIEESE) via download
direto do PDF público no site institucional do DIEESE.

Piloto técnico controlado — ver docs/08-decisoes-adr/0002-expansao-piloto-por-blocos.md
Fonte confirmada em: docs/04-fontes/dieese-publicacoes.md — 2ª rodada de reinvestigação
do Mediador/MTE, 2026-09-23.

ACHADO: os indicadores "Distribuição de reajustes salariais em negociação coletiva" e
"Valor médio dos pisos salariais por categoria" estavam classificados como LACUNA/D — o
sistema Mediador (MTE), citado como fonte no material do DIEESE, não tem API nem
exportação em massa (confirmado em duas rodadas de investigação). A alternativa correta
não é raspar o Mediador: é usar o boletim que o próprio DIEESE já publica mensalmente,
calculado a partir dos mesmos microdados do Mediador, com metodologia documentada
(reajustes vs. INPC, pisos médio/mediano, por setor e região).

DECISÃO DE FORMATO DE EXTRAÇÃO: não há API nem CSV — apenas PDF mensal com nome de
arquivo previsível (boletimnegociacao{numero}.pdf), numerado sequencialmente (não por
ano/mês como a Cesta Básica). Confirmado por teste técnico direto (`pdftotext -layout
-enc UTF-8`) que o PDF tem camada de texto real extraível, não é imagem/vetor — por isso
a classificação subiu de C para B. A extração dos números de dentro do texto é uma
transformação e pertence à camada STAGING, não a este script — aqui apenas o PDF bruto é
salvo, seguindo a mesma disciplina RAW do restante do pipeline.

DEPENDÊNCIA EXTERNA: `pdftotext` (poppler) é necessário apenas na camada STAGING (não
neste script de coleta, que só baixa o PDF). Documentar como exceção à stack mínima
(ADR 0001), no mesmo espírito da exceção já registrada para `curl` no Comex Stat.

Este script NÃO transforma o dado.
"""

import urllib.error
import urllib.request
from datetime import date
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from supabase_raw import registrar_coleta

DESTINO = Path(__file__).resolve().parents[3] / "data" / "raw" / "dieese_negociacao_coletiva"

# Âncora confirmada por leitura direta: edição 67 = boletim de abril/2026
# (dados até 9/abr/2026), publicada na pasta do ano 2026.
ANCORA_NUMERO = 67
ANCORA_ANO = 2026
ANCORA_MES = 4


def _url(ano: int, numero: int) -> str:
    return f"https://www.dieese.org.br/boletimnegociacao/{ano}/boletimnegociacao{numero}.pdf"


def _tentar_baixar(ano: int, numero: int) -> bytes | None:
    url = _url(ano, numero)
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=30) as resposta:
            return resposta.read()
    except urllib.error.HTTPError:
        return None


def _edicao_mais_recente(max_tentativas: int = 8) -> tuple[int, int, bytes]:
    hoje = date.today()
    meses_decorridos = (hoje.year - ANCORA_ANO) * 12 + (hoje.month - ANCORA_MES)
    numero_estimado = max(ANCORA_NUMERO, ANCORA_NUMERO + meses_decorridos)

    candidato = numero_estimado
    tentativas = 0
    while tentativas < max_tentativas and candidato >= ANCORA_NUMERO:
        for ano in (hoje.year, hoje.year - 1):
            conteudo = _tentar_baixar(ano, candidato)
            if conteudo is not None:
                return ano, candidato, conteudo
        candidato -= 1
        tentativas += 1

    raise RuntimeError(
        f"Nenhuma edição encontrada entre {candidato + 1} e {numero_estimado} "
        f"(âncora conhecida: edição {ANCORA_NUMERO} = {ANCORA_MES:02d}/{ANCORA_ANO})"
    )


def coletar() -> Path:
    DESTINO.mkdir(parents=True, exist_ok=True)
    ano, numero, conteudo = _edicao_mais_recente()

    arquivo = DESTINO / f"boletimnegociacao_{numero:03d}_{ano}.pdf"
    arquivo.write_bytes(conteudo)
    return arquivo


if __name__ == "__main__":
    caminho = coletar()
    tamanho_kb = caminho.stat().st_size / 1024
    print(f"Coleta concluída: {caminho} ({tamanho_kb:.1f} KB)")
    registrar_coleta(fonte=DESTINO.name, arquivo=caminho, script=__file__)
