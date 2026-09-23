"""Coleta bruta da Utilização da Capacidade Instalada (UCI), Indústria de Transformação,
via raspagem controlada do site da CNI (Confederação Nacional da Indústria).

Piloto técnico controlado — ver docs/08-decisoes-adr/0002-expansao-piloto-por-blocos.md
Fonte confirmada em: docs/04-fontes/fmi-cni.md — Lote 05a.

===============================================================================
POR QUE RASPAGEM (SCRAPING) EM VEZ DE API
===============================================================================
A CNI não expõe uma API pública nem um link fixo para o arquivo de dados: a
publicação mensal muda de nome a cada divulgação (ex.
"..._julho2026.xlsx", "..._agosto2026.xlsx", ...), então uma URL fixa
apontando para o arquivo quebraria no mês seguinte. Diferente de outras
fontes deste piloto que expõem uma API de listagem de mídia, a CNI não tem
esse recurso.

A solução adotada é uma raspagem MÍNIMA e DIRECIONADA — não uma raspagem
genérica de estrutura de página (que seria mais frágil a qualquer mudança de
layout do site): o script baixa o HTML da página oficial de estatísticas e
procura, com uma expressão regular, qualquer URL que já venha no formato
esperado do arquivo Excel da "Série Histórica". Isso funciona porque o que
muda mês a mês é só o nome do arquivo (o sufixo com mês/ano) — o padrão do
caminho (domínio + pasta) se mantém estável.

===============================================================================
ALERTA DE ATRIBUIÇÃO
===============================================================================
O material do DIEESE cita a fonte como "CNI - ICEI", mas a UCI NÃO faz parte
do ICEI (Índice de Confiança do Empresário Industrial, um indicador de
expectativa/sentimento) — pertence a outro levantamento da CNI, os
"Indicadores Industriais" (produção, faturamento, emprego, massa salarial,
utilização da capacidade instalada). Ver docs/04-fontes/fmi-cni.md para o
detalhamento da divergência.

===============================================================================
O QUE ESTE SCRIPT FAZ, PASSO A PASSO
===============================================================================
1. Baixa o HTML da página oficial de estatísticas da CNI (`PAGINA_URL`).
2. Procura no HTML, com uma regex (`PADRAO_LINK`), a URL do arquivo .xlsx da
   Série Histórica vigente no momento da coleta (`_localizar_link_atual`) —
   como pode haver mais de uma ocorrência do mesmo link na página, usa a
   primeira depois de ordenar as URLs encontradas, de forma determinística.
3. Baixa o conteúdo binário desse arquivo Excel.
4. Salva o arquivo em `data/raw/cni/`, mantendo o nome original do arquivo
   (prefixado por um timestamp da coleta) — diferente dos scripts de API
   deste piloto, aqui não convertemos nada para JSON: o dado bruto já vem
   nesse formato binário, e é assim que deve ser preservado.
5. Registra a coleta no Supabase — arquivo no Storage + linha em
   `raw_ingestoes` (`registrar_coleta`, importado de `pipelines/supabase_raw.py`).

Este script NÃO transforma o dado — nem sequer abre o Excel para ler seu
conteúdo, só localiza o link e baixa o arquivo como está, respeitando o
princípio de que a camada RAW nunca deve ser editada manualmente ou
pré-processada (ver CLAUDE.md, seção DADOS). Ler as planilhas do Excel e
extrair a série de UCI é trabalho da camada STAGING, feito depois, a partir
do arquivo que este script grava — nunca aqui.
"""

import re
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from supabase_raw import registrar_coleta

# Página oficial de estatísticas da CNI — Indicadores Industriais (não ICEI,
# ver alerta de atribuição acima).
PAGINA_URL = "https://www.portaldaindustria.com.br/estatisticas/indicadores-industriais/"

# Padrão do link do arquivo Excel da Série Histórica: o domínio e a pasta são
# estáveis; só o nome do arquivo (mês/ano da divulgação) muda a cada mês —
# por isso o casamento de padrão, e não uma URL fixa.
PADRAO_LINK = re.compile(
    r"https://static\.portaldaindustria\.com\.br/[^\"'\s]+indicadoresindustriais[^\"'\s]*\.xlsx",
    re.IGNORECASE,
)

DESTINO = Path(__file__).resolve().parents[3] / "data" / "raw" / "cni"


# ------------------------------------------------------------------------
# PASSO 1 — localizar, na página da CNI, o link vigente do arquivo Excel
# ------------------------------------------------------------------------
def _localizar_link_atual() -> str:
    """Baixa o HTML da página de estatísticas e devolve a primeira URL
    (em ordem alfabética, para o resultado ser determinístico) que bate com
    `PADRAO_LINK`.

    Envia um `User-Agent` de navegador porque alguns servidores bloqueiam
    requisições sem esse cabeçalho, tratando-as como bots. `timeout=90`
    (maior que o padrão de 60s usado nos demais scripts) porque este servidor
    foi observado, empiricamente, como lento para responder.

    Levanta `RuntimeError` se nenhum link for encontrado — sinal de que o
    padrão da página mudou e precisa de revisão manual, em vez de o script
    seguir adiante e gravar um "raw" vazio ou incorreto.
    """
    req = urllib.request.Request(PAGINA_URL, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=90) as resposta:  # servidor lento, observado empiricamente
        html = resposta.read().decode("utf-8", errors="replace")

    encontrados = sorted(set(PADRAO_LINK.findall(html)))
    if not encontrados:
        raise RuntimeError(
            "Nenhum link de série histórica encontrado na página da CNI — "
            "o padrão da página pode ter mudado, requer revisão manual."
        )
    return encontrados[0]


# ------------------------------------------------------------------------
# PASSO 2 — baixar o arquivo Excel encontrado
# ------------------------------------------------------------------------
def _baixar_arquivo(url_arquivo: str) -> bytes:
    """Baixa o conteúdo binário do arquivo Excel localizado no passo
    anterior. Mesmo `User-Agent` de navegador do passo 1, pelo mesmo motivo.
    """
    req = urllib.request.Request(url_arquivo, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=60) as resposta:
        return resposta.read()


# ------------------------------------------------------------------------
# PASSO 3 — salvar o arquivo bruto em disco
# ------------------------------------------------------------------------
def _salvar_raw(url_arquivo: str, conteudo: bytes) -> Path:
    """Grava o conteúdo binário tal como recebido — sem qualquer conversão.
    O nome do arquivo é o nome original publicado pela CNI, prefixado por um
    timestamp UTC (`%Y%m%dT%H%M%SZ_`) da coleta, para nunca sobrescrever uma
    coleta anterior mesmo que a CNI reutilize o mesmo nome de arquivo.
    """
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    nome_original = url_arquivo.rsplit("/", 1)[-1]
    arquivo = DESTINO / f"{timestamp}_{nome_original}"
    arquivo.write_bytes(conteudo)
    return arquivo


# ------------------------------------------------------------------------
# Orquestração: chama os passos acima, nesta ordem
# ------------------------------------------------------------------------
def coletar() -> Path:
    DESTINO.mkdir(parents=True, exist_ok=True)
    url_arquivo = _localizar_link_atual()
    conteudo = _baixar_arquivo(url_arquivo)
    return _salvar_raw(url_arquivo, conteudo)


if __name__ == "__main__":
    caminho = coletar()
    tamanho_kb = caminho.stat().st_size / 1024
    print(f"Coleta concluída: {caminho} ({tamanho_kb:.1f} KB)")
    registrar_coleta(fonte=DESTINO.name, arquivo=caminho, script=__file__)
