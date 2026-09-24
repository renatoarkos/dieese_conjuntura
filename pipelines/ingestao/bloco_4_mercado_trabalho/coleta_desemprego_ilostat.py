"""Coleta bruta da taxa de desemprego do Brasil (estimativa harmonizada
internacionalmente) via API pública SDMX do ILOSTAT (Organização
Internacional do Trabalho — OIT/ILO).

Piloto técnico controlado — ver docs/08-decisoes-adr/0002-expansao-piloto-por-blocos.md
Fonte confirmada em: docs/04-fontes/outras-instituicoes-mundiais-2026-09.md (seção ILOSTAT)

===============================================================================
O QUE ESTE INDICADOR MEDE, E POR QUE NÃO SUBSTITUI A TAXA DE DESOCUPAÇÃO JÁ
COLETADA (coleta_desocupacao_sidra.py)
===============================================================================
Este é o dataflow `DF_UNE_2EAP_SEX_AGE_RT` do ILOSTAT — taxa de desemprego
por sexo e faixa etária, rotulada pela própria OIT como **"ILO - Modelled
Estimates"**: uma estimativa que a OIT calcula e ajusta para ser comparável
entre países com metodologias nacionais diferentes de pesquisa domiciliar.

**Isso não é a mesma coisa que a Tabela SIDRA 4093** (já coletada por
`coleta_desocupacao_sidra.py`), que é a taxa de desocupação calculada
diretamente pelo IBGE a partir da PNAD Contínua, sem nenhum ajuste de
harmonização internacional. As duas séries vão ter valores diferentes para o
mesmo período — isso é esperado, não um erro. O valor deste indicador só
serve para **comparar o Brasil com outros países** na mesma base
metodológica; para qualquer análise só do Brasil, a série do IBGE continua
sendo a referência.

===============================================================================
COMO FUNCIONA A API DO ILOSTAT (SDMX — mesmo protocolo usado por outros
organismos internacionais, ver docs/10-apis-externas/01-fundamentos-de-apis.md)
===============================================================================
A URL segue o padrão SDMX: agência,dataflow,versão / chave separada por
pontos (cada ponto é uma dimensão — aqui: país.frequência.medida.sexo.idade):

    https://sdmx.ilo.org/rest/data/ILO,DF_UNE_2EAP_SEX_AGE_RT,1.0/BRA....

  - `BRA`  → primeira dimensão (país) fixada em Brasil.
  - `....` → as demais dimensões (frequência, medida, sexo, idade) deixadas
             vazias entre pontos, o equivalente a "todas" no SDMX — a
             resposta traz todas as combinações.

**Achado importante deste script**: o servidor do ILOSTAT retorna
`HTTP 403 Forbidden` para uma requisição sem cabeçalho `User-Agent` de
navegador — mesmo padrão já visto na ANP (`docs/04-fontes/anp-ipeadata.md`)
e agora confirmado aqui também: não é um bloqueio institucional aos dados em
si, é detecção de bot por cabeçalho incompleto.

===============================================================================
O QUE ESTE SCRIPT FAZ, PASSO A PASSO
===============================================================================
1. Monta a URL da consulta (constante `URL`), pedindo os últimos anos
   disponíveis, em formato CSV (mais simples de armazenar e ler que o XML
   SDMX completo).
2. Busca os dados na API, com cabeçalhos de navegador (`_buscar_dados`).
3. Salva a resposta em `data/raw/ilostat/` (`_salvar_raw`).
4. Registra a coleta no Supabase.

Este script NÃO transforma o dado.
"""

import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from supabase_raw import registrar_coleta

# Dataflow DF_UNE_2EAP_SEX_AGE_RT do ILOSTAT: taxa de desemprego por sexo e
# faixa etária, estimativa modelada da OIT. Chave "BRA...." = Brasil, todas
# as demais dimensões. startPeriod amplo o suficiente para cobrir revisões
# de anos anteriores, que a OIT às vezes publica.
URL = "https://sdmx.ilo.org/rest/data/ILO,DF_UNE_2EAP_SEX_AGE_RT,1.0/BRA....?startPeriod=2010"

# Cabeçalhos necessários para não receber HTTP 403 (detecção de bot, não
# bloqueio institucional — ver docstring do módulo). `Accept: text/csv` pede
# à API para responder em CSV, em vez do XML SDMX completo por padrão.
CABECALHOS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "text/csv",
}

DESTINO = Path(__file__).resolve().parents[3] / "data" / "raw" / "ilostat"


# ------------------------------------------------------------------------
# PASSO 1 — buscar os dados na API
# ------------------------------------------------------------------------
def _buscar_dados() -> bytes:
    req = urllib.request.Request(URL, headers=CABECALHOS)
    with urllib.request.urlopen(req, timeout=60) as resposta:
        return resposta.read()


# ------------------------------------------------------------------------
# PASSO 2 — salvar a resposta bruta em disco
# ------------------------------------------------------------------------
def _salvar_raw(conteudo: bytes) -> Path:
    DESTINO.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    arquivo = DESTINO / f"desemprego_bra_ilostat_{timestamp}.csv"
    arquivo.write_bytes(conteudo)
    return arquivo


# ------------------------------------------------------------------------
# Orquestração: chama os passos acima, nesta ordem
# ------------------------------------------------------------------------
def coletar() -> Path:
    conteudo = _buscar_dados()
    return _salvar_raw(conteudo)


if __name__ == "__main__":
    caminho = coletar()
    tamanho_kb = caminho.stat().st_size / 1024
    print(f"Coleta concluída: {caminho} ({tamanho_kb:.1f} KB)")
    registrar_coleta(fonte=DESTINO.name, arquivo=caminho, script=__file__)
