"""Coleta bruta do boletim trimestral "Análise ICT-DIEESE" (Índice da Condição
do Trabalho) via download direto do PDF público no site institucional do
DIEESE.

Piloto técnico controlado — ver docs/08-decisoes-adr/0002-expansao-piloto-por-blocos.md
Fonte confirmada em: docs/04-fontes/dieese-publicacoes.md

===============================================================================
ACHADO QUE MUDA A CLASSIFICAÇÃO DESTE INDICADOR (2026-09-23)
===============================================================================
Uma investigação anterior havia classificado este boletim como "PDF vetorizado
sem texto extraível" (classificação E — manual). Isso estava ERRADO: testado
diretamente com `pdftotext -layout -enc UTF-8`, o texto sai limpo — a
confusão veio de uma ferramenta de leitura que falha silenciosamente nesse
tipo de PDF comprimido (FlateDecode), sem indicar erro.

**Confirmado por comparação direta com a fonte de verdade** (planilha/
apresentação interna do DIEESE): o valor do ICT-DIEESE do 3º trimestre de
2025 na edição mais recente do boletim (nº 18, jan/2026) é 0,68 — idêntico
(arredondamento) ao valor 0,6848 da mesma referência na apresentação interna
de dez/2025. Por isso a classificação sobe de E para B.

===============================================================================
O QUE ESTE INDICADOR MEDE
===============================================================================
O ICT-DIEESE é um índice sintético (0 a 1, quanto maior melhor) sobre
condições de inserção no mercado de trabalho, elaboração própria do DIEESE a
partir de microdados da PNAD Contínua (IBGE), combinando três dimensões:
condição de inserção ocupacional, desocupação e rendimento.

===============================================================================
PADRÃO DE URL — NÃO É UNIFORME ENTRE EDIÇÕES
===============================================================================
Diferente dos outros boletins institucionais do DIEESE já coletados neste
piloto (Cesta Básica, Negociação Coletiva), o nome de arquivo do boletim ICT
mudou de formato ao longo do tempo — confirmado por teste direto:
  - edições mais antigas: `{numero}{ano}.pdf` (ex. `072020.pdf`)
  - edições intermediárias: `{numero}{ano}analiseIct.pdf` (camelCase)
  - edições recentes: `{numero}{ano}analiseict.pdf` (minúsculo)
Por isso a busca por edição tenta os três padrões de nome para cada número
candidato, em vez de assumir um único formato fixo.

Além disso, a página-índice pública (`dieese.org.br/analiseict/ict.html`)
está desatualizada (para de listar bem antes da edição mais recente
confirmada) — não dá para confiar nela para descobrir a edição atual; a
busca por número sequencial (mesma técnica já usada no boletim de negociação
coletiva) é o caminho confiável.

===============================================================================
O QUE ESTE SCRIPT FAZ, PASSO A PASSO
===============================================================================
1. A partir de uma âncora confirmada (edição 18 = jan/2026), estima a edição
   atual pelos meses decorridos (publicação trimestral) e tenta os 3 padrões
   de nome de arquivo, para cada ano candidato, até achar um que responda
   (`_edicao_mais_recente`).
2. Salva o PDF bruto em `data/raw/dieese_ict/` (`_salvar_raw`).
3. Registra a coleta no Supabase.

Este script NÃO transforma o dado — grava o PDF exatamente como recebido.
Extrair os números de dentro do texto (via `pdftotext`) é uma transformação
de camada STAGING, não desta coleta.
"""

import sys
import urllib.error
import urllib.request
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from supabase_raw import registrar_coleta

# Âncora confirmada por leitura direta: edição 18 = boletim de jan/2026
# (dados referentes ao 3º trimestre de 2025).
ANCORA_NUMERO = 18
ANCORA_ANO = 2026
ANCORA_MES = 1

# Os 3 padrões de nome de arquivo já observados, em ordem do mais recente
# para o mais antigo (o mais provável de bater primeiro, para poupar
# tentativas na busca pela edição atual).
PADROES_NOME = [
    "{numero}{ano}analiseict.pdf",
    "{numero}{ano}analiseIct.pdf",
    "{numero}{ano}.pdf",
]

DESTINO = Path(__file__).resolve().parents[3] / "data" / "raw" / "dieese_ict"


def _urls_candidatas(ano: int, numero: int) -> list[str]:
    base = f"https://www.dieese.org.br/analiseict/{ano}"
    return [f"{base}/{padrao.format(numero=numero, ano=ano)}" for padrao in PADROES_NOME]


def _tentar_baixar(url: str) -> bytes | None:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=30) as resposta:
            return resposta.read()
    except urllib.error.HTTPError:
        return None


def _edicao_mais_recente(max_tentativas: int = 8) -> tuple[int, int, bytes]:
    hoje = date.today()
    meses_decorridos = (hoje.year - ANCORA_ANO) * 12 + (hoje.month - ANCORA_MES)
    # publicação é trimestral: cada ~3 meses decorridos, mais 1 edição provável
    numero_estimado = max(ANCORA_NUMERO, ANCORA_NUMERO + meses_decorridos // 3)

    candidato = numero_estimado
    tentativas = 0
    while tentativas < max_tentativas and candidato >= ANCORA_NUMERO:
        for ano in (hoje.year, hoje.year - 1):
            for url in _urls_candidatas(ano, candidato):
                conteudo = _tentar_baixar(url)
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

    arquivo = DESTINO / f"ict_dieese_{numero:03d}_{ano}.pdf"
    arquivo.write_bytes(conteudo)
    return arquivo


if __name__ == "__main__":
    caminho = coletar()
    tamanho_kb = caminho.stat().st_size / 1024
    print(f"Coleta concluída: {caminho} ({tamanho_kb:.1f} KB)")
    registrar_coleta(fonte=DESTINO.name, arquivo=caminho, script=__file__)
