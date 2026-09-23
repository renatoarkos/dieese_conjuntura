"""Coleta bruta do "Balanço das Greves" (Sistema de Acompanhamento de Greves —
SAG, DIEESE) via download direto do PDF público no site institucional do
DIEESE.

Piloto técnico controlado — ver docs/08-decisoes-adr/0002-expansao-piloto-por-blocos.md
Fonte confirmada em: docs/04-fontes/dieese-publicacoes.md

===============================================================================
ACHADO QUE MUDA A CLASSIFICAÇÃO DESTE INDICADOR (2026-09-23)
===============================================================================
Uma investigação anterior havia classificado este boletim como "PDF baseado
em imagem, sem texto extraível" (classificação E — manual). Isso estava
ERRADO: testado diretamente com `pdftotext -layout -enc UTF-8`, o texto sai
limpo em todas as edições testadas (de 2016 até a mais recente).

**Confirmado por comparação direta com a fonte de verdade** (apresentação
interna do DIEESE, slides 48-51): os números do boletim EP 111 (ano completo
de 2024) batem EXATAMENTE com os da apresentação interna — total de 880
greves, e as 5 principais reivindicações com a mesma porcentagem em todas as
casas decimais (reajuste salarial 36,7%, condições de trabalho 25,2%, atraso
de salário 23,9%, alimentação 21,5%, PCS 16,0%). O boletim do 1º semestre de
2025 (EP 112) também bate: "536 greves", idêntico à apresentação interna. Por
isso a classificação sobe de E para B.

**Alerta que continua valendo**: uma busca anterior mencionou um suposto "EP
114" com números específicos — a URL testada deu 404. Esse número nunca foi
confirmado e não deve ser usado.

===============================================================================
O QUE ESTE INDICADOR MEDE
===============================================================================
Número de greves no Brasil, por esfera (privada/funcionalismo público/
empresas estatais), principais categorias grevistas e principais
reivindicações — fonte primária: Sistema de Acompanhamento de Greves (SAG),
sistema interno do DIEESE que monitora notícias de imprensa. Publicado
semestral/anualmente na série "Estudos e Pesquisas" (EP).

**Limitação metodológica documentada nos próprios boletins**: os números de
períodos recentes são revisados retroativamente entre edições (o SAG segue
processando notícias depois da publicação original) — ao montar uma série
histórica, usar sempre o valor da edição MAIS RECENTE para cada período, não
concatenar valores de edições antigas.

===============================================================================
PADRÃO DE URL — MUDOU DE PASTA E DE FORMATO AO LONGO DO TEMPO
===============================================================================
Confirmado por teste direto: até por volta de 2022/2023 os boletins ficavam
em `dieese.org.br/balancodasgreves/{ano}/`, com nomes inconsistentes
(`estPesq84balancogreves2016.pdf`, `estPesq87balancoGreves2017.pdf` — note a
troca de maiúscula em "balancoGreves"). A partir de ~2024, migraram para
`dieese.org.br/estudosepesquisas/{ano}/`, com nome `estPesq{numero}greves.pdf`.
Este script tenta os dois padrões de pasta/nome para cada número de edição
candidato — mais simples e mais robusto que tentar adivinhar exatamente
quando a mudança de padrão aconteceu.

===============================================================================
O QUE ESTE SCRIPT FAZ, PASSO A PASSO
===============================================================================
1. A partir de uma âncora confirmada (EP 112 = 1º semestre de 2025), tenta
   os números de edição seguintes (mais recentes) e, se não achar, anteriores,
   testando as duas combinações de pasta/nome para cada um
   (`_edicao_mais_recente`).
2. Salva o PDF bruto em `data/raw/dieese_greves/` (`_salvar_raw`).
3. Registra a coleta no Supabase.

Este script NÃO transforma o dado — grava o PDF exatamente como recebido.
Extrair os números de dentro do texto (via `pdftotext`) é uma transformação
de camada STAGING, não desta coleta.
"""

import sys
import urllib.error
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from supabase_raw import registrar_coleta

# Âncora confirmada por leitura direta: EP 112 = boletim do 1º semestre de
# 2025, publicado em 2026, pasta "estudosepesquisas".
ANCORA_NUMERO = 112
ANCORA_ANO_PUBLICACAO = 2026

DESTINO = Path(__file__).resolve().parents[3] / "data" / "raw" / "dieese_greves"


def _urls_candidatas(ano: int, numero: int) -> list[str]:
    return [
        # padrão mais recente (2024+), o mais provável de bater primeiro
        f"https://www.dieese.org.br/estudosepesquisas/{ano}/estPesq{numero}greves.pdf",
        # padrões mais antigos (até ~2023), variações de maiúscula/sufixo
        f"https://www.dieese.org.br/balancodasgreves/{ano}/estPesq{numero}balancogreves{ano}.pdf",
        f"https://www.dieese.org.br/balancodasgreves/{ano}/estPesq{numero}balancoGreves{ano}.pdf",
        f"https://www.dieese.org.br/balancodasgreves/{ano}/estPesq{numero}Greves.pdf",
        f"https://www.dieese.org.br/balancodasgreves/{ano}/estPesq{numero}Greves{ano}.pdf",
    ]


def _tentar_baixar(url: str) -> bytes | None:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=30) as resposta:
            return resposta.read()
    except urllib.error.HTTPError:
        return None


def _edicao_mais_recente(max_tentativas: int = 6) -> tuple[int, bytes]:
    """Tenta primeiro edições MAIS NOVAS que a âncora (pode ter saído uma
    edição nova desde a última pesquisa), depois cai para a própria âncora e
    edições mais antigas se nada mais recente for encontrado.
    """
    anos_para_tentar = [ANCORA_ANO_PUBLICACAO, ANCORA_ANO_PUBLICACAO + 1, ANCORA_ANO_PUBLICACAO - 1]

    # 1) tenta edições mais novas que a âncora, da mais nova para a mais velha
    for numero in range(ANCORA_NUMERO + max_tentativas, ANCORA_NUMERO, -1):
        for ano in anos_para_tentar:
            for url in _urls_candidatas(ano, numero):
                conteudo = _tentar_baixar(url)
                if conteudo is not None:
                    return numero, conteudo

    # 2) confirma a própria âncora
    for ano in anos_para_tentar:
        for url in _urls_candidatas(ano, ANCORA_NUMERO):
            conteudo = _tentar_baixar(url)
            if conteudo is not None:
                return ANCORA_NUMERO, conteudo

    raise RuntimeError(f"Nenhuma edição encontrada a partir da âncora EP {ANCORA_NUMERO}")


def coletar() -> Path:
    DESTINO.mkdir(parents=True, exist_ok=True)
    numero, conteudo = _edicao_mais_recente()

    arquivo = DESTINO / f"greves_dieese_ep{numero:03d}.pdf"
    arquivo.write_bytes(conteudo)
    return arquivo


if __name__ == "__main__":
    caminho = coletar()
    tamanho_kb = caminho.stat().st_size / 1024
    print(f"Coleta concluída: {caminho} ({tamanho_kb:.1f} KB)")
    registrar_coleta(fonte=DESTINO.name, arquivo=caminho, script=__file__)
