"""Coleta bruta do PIB Mundial (variação real, % a.a.) via API pública do FMI, base de
dados WEO (World Economic Outlook).

Piloto técnico controlado — ver docs/08-decisoes-adr/0002-expansao-piloto-por-blocos.md
Fonte confirmada em: docs/04-fontes/fmi-cni.md (dataflow WEO, indicador NGDP_RPCH)

===============================================================================
COMO FUNCIONA A API SDMX 3.0 DO FMI
===============================================================================
O FMI publica suas bases de dados (WEO, IFS, BOP etc.) através de uma API que
segue o padrão internacional SDMX (Statistical Data and Metadata eXchange),
usado por vários organismos estatísticos internacionais (FMI, Eurostat, OCDE).
Não é preciso chave nem autenticação para consultar dados públicos. O formato
geral da URL de consulta é:

    https://api.imf.org/external/sdmx/3.0/data/dataflow/{agencia}/{dataflow}/{versao}/{filtro}

  - `dataflow/IMF.RES/WEO/~` → identifica o "dataflow" (a base de dados) que
                                se quer consultar: agência `IMF.RES`, dataflow
                                `WEO`, `~` = versão mais recente disponível.
                                Cada base de dados do FMI (WEO, IFS, ...) tem
                                seu próprio identificador de dataflow.
  - `A.*.NGDP_RPCH`            → o filtro, no formato
                                {frequência}.{área/país}.{indicador}:
                                  - `A`          = frequência anual.
                                  - `*`          = curinga para
                                                   área/país — "todas as
                                                   áreas/países disponíveis"
                                                   (ver limitação abaixo).
                                  - `NGDP_RPCH`  = código do indicador
                                                   ("variação percentual do
                                                   PIB real", a métrica de
                                                   crescimento do WEO).
  - `?startPeriod=...&endPeriod=...` → filtro de intervalo de anos, como em
                                        qualquer API REST comum.

A resposta é um JSON estruturado no padrão SDMX (não uma lista simples de
registros como no SIDRA ou no SGS) — este script grava essa estrutura exatamente
como veio, sem reformatar ou "achatar" em tabela; isso é trabalho de STAGING.

===============================================================================
LIMITAÇÃO CONHECIDA — por que a consulta usa curinga "*" em vez do país
===============================================================================
Os códigos de país usados pelo dataflow WEO não são ISO3 simples: testar
"BRA" diretamente não retorna nenhuma série (confirmado em
docs/04-fontes/fmi-cni.md). Descobrir o código correto exigiria mapear o
codelist `COUNTRY` do FMI antes de filtrar — um passo de investigação que não
foi fechado nesta rodada. Para não adivinhar um código não confirmado, este
script coleta com o curinga "*" (todos os países/agregados disponíveis) e
deixa qualquer filtragem por país específico para a camada STAGING, a partir
deste arquivo bruto.

===============================================================================
O QUE ESTE SCRIPT FAZ, PASSO A PASSO
===============================================================================
1. Monta a URL da consulta (constante `URL`, ver acima) e o cabeçalho HTTP
   `Accept: application/json`, pedindo explicitamente a resposta em JSON.
2. Busca os dados na API (`_buscar_dados`).
3. Salva a resposta, sem alterar nada, em `data/raw/fmi_weo/` com um nome de
   arquivo que inclui o instante da coleta (`_salvar_raw`).
4. Registra a coleta no Supabase — arquivo no Storage + linha em
   `raw_ingestoes` (`registrar_coleta`, importado de `pipelines/supabase_raw.py`).

Este script NÃO transforma o dado — grava a resposta bruta da API exatamente
como recebida, respeitando o princípio de que a camada RAW nunca deve ser
editada manualmente ou pré-processada (ver CLAUDE.md, seção DADOS). Filtrar
por país, calcular médias ou qualquer outra conta é trabalho da camada
STAGING, feito depois, a partir do arquivo que este script grava — nunca aqui.
"""

import json
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from supabase_raw import registrar_coleta

# Dataflow WEO (World Economic Outlook) do FMI, indicador NGDP_RPCH ("variação
# percentual do PIB real"), frequência anual, todos os países/agregados (*).
URL = (
    "https://api.imf.org/external/sdmx/3.0/data/dataflow/IMF.RES/WEO/~/A.*.NGDP_RPCH"
    "?startPeriod=2016&endPeriod=2030"
)

DESTINO = Path(__file__).resolve().parents[3] / "data" / "raw" / "fmi_weo"


# ------------------------------------------------------------------------
# PASSO 1 — buscar os dados na API
# ------------------------------------------------------------------------
def _buscar_dados() -> dict:
    """Faz a requisição HTTP e devolve o JSON já decodificado.

    O cabeçalho `Accept: application/json` é enviado explicitamente porque
    APIs SDMX costumam suportar múltiplos formatos de resposta (JSON, XML,
    CSV) — sem pedir o formato, a API poderia responder em outro. `timeout=60`
    evita que o script fique parado indefinidamente se a API do FMI não
    responder — nesse caso ele falha de forma visível (exceção), em vez de
    travar silenciosamente.
    """
    req = urllib.request.Request(URL, headers={"Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as resposta:
        return json.loads(resposta.read().decode("utf-8"))


# ------------------------------------------------------------------------
# PASSO 2 — salvar a resposta bruta em disco
# ------------------------------------------------------------------------
def _salvar_raw(dados: dict) -> Path:
    """Grava `dados` como JSON formatado (indent=2), só para leitura humana —
    não é transformação de dado. O nome do arquivo leva um timestamp UTC
    (`_%Y%m%dT%H%M%SZ`) porque o FMI revisa e reprojeta a série a cada
    divulgação (abril e outubro) — cada execução deste script é uma nova
    fotografia da base, e nunca sobrescrevemos a coleta anterior.
    """
    DESTINO.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    arquivo = DESTINO / f"pib_mundial_weo_ngdp_rpch_{timestamp}.json"
    arquivo.write_text(json.dumps(dados, ensure_ascii=False, indent=2), encoding="utf-8")
    return arquivo


# ------------------------------------------------------------------------
# Orquestração: chama os passos acima, nesta ordem
# ------------------------------------------------------------------------
def coletar() -> Path:
    dados = _buscar_dados()
    return _salvar_raw(dados)


if __name__ == "__main__":
    caminho = coletar()
    print(f"Coleta concluída: {caminho}")
    registrar_coleta(fonte=DESTINO.name, arquivo=caminho, script=__file__)
