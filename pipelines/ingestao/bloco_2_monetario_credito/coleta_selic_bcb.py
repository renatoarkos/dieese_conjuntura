"""Coleta bruta da Taxa Selic via API pública do BCB/SGS.

Piloto técnico controlado — ver docs/08-decisoes-adr/0002-expansao-piloto-por-blocos.md
Fonte confirmada em: docs/04-fontes/bcb.md — achado do Lote Piloto 01 + validação de dados
2026-09-22 (comparação direta com a aba T14 do material do DIEESE, 122 valores mensais).

A série usada pelo DIEESE é uma COMPOSIÇÃO de duas séries SGS diferentes ao longo do tempo:
  - SGS 4189 ("Selic acumulada no mês, anualizada base 252"): nov/2015 a jul/2024.
  - SGS 432 ("Meta Selic definida pelo Copom"): ago/2024 em diante.

Este script coleta as DUAS séries completas, SEM aplicar a regra de corte/troca — essa é uma
decisão de transformação que pertence à camada STAGING, não à RAW. A camada RAW preserva as
séries-fonte exatamente como a API as devolve.
"""

import json
import time
import urllib.error
import urllib.request
from datetime import date, datetime, timezone
from pathlib import Path

# Data de início de cada série no BCB/SGS (confirmada no Discovery de Fontes).
INICIO_SERIE = {
    "4189": date(1986, 8, 1),
    "432": date(1999, 3, 5),
}
DESTINO = Path(__file__).resolve().parents[3] / "data" / "raw" / "bcb_sgs"


def _buscar_url(url: str, tentativas: int = 3) -> list[dict]:
    """A API do BCB é intermitentemente instável sob chamadas sucessivas — algumas
    requisições retornam corpo vazio ou HTTP 406 mesmo quando a mesma URL funciona
    isoladamente (observado empiricamente nesta rodada). Repete com pequena espera."""
    ultimo_erro: Exception | None = None
    for tentativa in range(1, tentativas + 1):
        try:
            with urllib.request.urlopen(url, timeout=60) as resposta:
                corpo = resposta.read().decode("utf-8")
            return json.loads(corpo)
        except (urllib.error.HTTPError, json.JSONDecodeError) as erro:
            ultimo_erro = erro
            time.sleep(2 * tentativa)
    raise RuntimeError(f"Falha após {tentativas} tentativas: {url}") from ultimo_erro


def _coletar_serie(codigo: str, inicio: date) -> list[dict]:
    """Busca o histórico completo de uma série SGS.

    A API do BCB rejeita (HTTP 406) pedidos sem filtro de data para séries longas
    (ex.: diárias desde 1999) — não documentado oficialmente, descoberto por teste real
    nesta rodada. Contorno: paginar em janelas de até 10 anos (limite documentado da API
    desde 26/03/2025) e concatenar os resultados, sem alterar nenhum valor.
    """
    base = f"https://api.bcb.gov.br/dados/serie/bcdata.sgs.{codigo}/dados?formato=json"
    try:
        return _buscar_url(base, tentativas=1)
    except RuntimeError:
        pass  # série longa demais para pedido sem filtro — pagina abaixo

    hoje = date.today()
    pontos: list[dict] = []
    janela_inicio = inicio
    while janela_inicio <= hoje:
        janela_fim = min(date(janela_inicio.year + 10, janela_inicio.month, 1), hoje)
        url = (
            f"{base}&dataInicial={janela_inicio.strftime('%d/%m/%Y')}"
            f"&dataFinal={janela_fim.strftime('%d/%m/%Y')}"
        )
        pontos.extend(_buscar_url(url))
        janela_inicio = janela_fim.replace(day=1)
        if janela_inicio.month == 12:
            janela_inicio = janela_inicio.replace(year=janela_inicio.year + 1, month=1, day=2)
        else:
            janela_inicio = janela_inicio.replace(month=janela_inicio.month + 1, day=2)
    return pontos


def coletar() -> list[Path]:
    DESTINO.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    arquivos = []
    for codigo, inicio in INICIO_SERIE.items():
        dados = _coletar_serie(codigo, inicio)
        arquivo = DESTINO / f"selic_sgs_{codigo}_{timestamp}.json"
        arquivo.write_text(json.dumps(dados, ensure_ascii=False, indent=2), encoding="utf-8")
        arquivos.append(arquivo)
    return arquivos


if __name__ == "__main__":
    for caminho in coletar():
        print(f"Coleta concluída: {caminho}")
