"""Coleta bruta da Utilização da Capacidade Instalada (UCI), Indústria de Transformação,
via raspagem controlada do site da CNI (Confederação Nacional da Indústria).

Piloto técnico controlado — ver docs/08-decisoes-adr/0002-expansao-piloto-por-blocos.md
Fonte confirmada em: docs/04-fontes/fmi-cni.md — Lote 05a.

ALERTA DE ATRIBUIÇÃO: o material do DIEESE cita a fonte como "CNI - ICEI", mas a UCI não
faz parte do ICEI (Índice de Confiança do Empresário Industrial) — pertence a outro
levantamento da CNI, os "Indicadores Industriais". Ver docs/04-fontes/fmi-cni.md.

DECISÃO DE FORMATO DE EXTRAÇÃO: a CNI não tem API nem link fixo — o nome do arquivo
Excel muda a cada divulgação mensal (ex. "..._julho2026.xlsx"). Diferente do caso do
PEIC/FecomercioSP (que tem uma API de listagem de mídia), a CNI não expõe esse tipo de
API, então este script faz uma RASPAGEM mínima e direcionada: busca, na página oficial
de estatísticas, o link para o arquivo .xlsx da "Série Histórica" via correspondência de
padrão de URL (não parsing de estrutura de página, que seria mais frágil), e então baixa
o arquivo encontrado.

Este script NÃO transforma o dado.
"""

import re
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

PAGINA_URL = "https://www.portaldaindustria.com.br/estatisticas/indicadores-industriais/"
PADRAO_LINK = re.compile(
    r"https://static\.portaldaindustria\.com\.br/[^\"'\s]+indicadoresindustriais[^\"'\s]*\.xlsx",
    re.IGNORECASE,
)
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from supabase_raw import registrar_coleta

DESTINO = Path(__file__).resolve().parents[3] / "data" / "raw" / "cni"


def _localizar_link_atual() -> str:
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


def coletar() -> Path:
    DESTINO.mkdir(parents=True, exist_ok=True)
    url_arquivo = _localizar_link_atual()

    req = urllib.request.Request(url_arquivo, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=60) as resposta:
        conteudo = resposta.read()

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    nome_original = url_arquivo.rsplit("/", 1)[-1]
    arquivo = DESTINO / f"{timestamp}_{nome_original}"
    arquivo.write_bytes(conteudo)
    return arquivo


if __name__ == "__main__":
    caminho = coletar()
    tamanho_kb = caminho.stat().st_size / 1024
    print(f"Coleta concluída: {caminho} ({tamanho_kb:.1f} KB)")
    registrar_coleta(fonte=DESTINO.name, arquivo=caminho, script=__file__)
