"""Coleta bruta dos desembolsos mensais do BNDES via API pública (CKAN) do
Portal de Dados Abertos do BNDES.

Piloto técnico controlado — ver docs/08-decisoes-adr/0002-expansao-piloto-por-blocos.md
Fonte confirmada em: docs/04-fontes/outras-instituicoes-2026-09.md (seção BNDES)

===============================================================================
O QUE ESTE INDICADOR MEDE, E UM AJUSTE DE EXPECTATIVA IMPORTANTE
===============================================================================
Desembolsos do BNDES (financiamentos efetivamente liberados, não só
aprovados), por operação individual — porte de cliente, setor CNAE/BNDES,
UF, produto, instrumento financeiro, forma de apoio (direta/indireta).

Uma investigação anterior classificou esta fonte como "A — API direta"
simples, mas um teste mais aprofundado (antes de escrever este script)
mostrou que o dado é mais granular do que parecia: o dataset completo tem
**3,76 milhões de registros** desde 1995, e só o mês mais recente já tem
mais de 13 mil operações — não é um indicador único já agregado (como
"desembolso total do mês"), é microdado por operação, no mesmo espírito do
Novo CAGED e da RAIS. A classificação correta é **C — microdados**: o dado
bruto é útil e será coletado, mas agregar isso numa série "desembolso mensal
total" (ou por setor/UF) é trabalho de STAGING, não desta coleta.

**Defasagem observada**: no teste feito em 2026-09-24, o mês mais recente
disponível era março/2026 — quase 6 meses de atraso. Isso é maior que a
"atualização trimestral" declarada nos metadados do próprio BNDES; vale
reconferir a defasagem real a cada execução (por isso o script descobre o
mês mais recente dinamicamente, em vez de presumir uma defasagem fixa).

===============================================================================
COMO FUNCIONA A API DO BNDES (CKAN — mesmo protocolo do dados.gov.br, mas
sem a exigência de credencial que o portal federal central passou a ter)
===============================================================================
O portal de dados abertos do BNDES usa CKAN, o mesmo software usado por
muitos catálogos de dados abertos governamentais. O endpoint relevante é o
`datastore_search`, que permite consultar um recurso (aqui, a tabela de
desembolsos mensais) com filtros e ordenação, sem precisar baixar o arquivo
inteiro:

    https://dadosabertos.bndes.gov.br/api/3/action/datastore_search
        ?resource_id={id}&filters={"ano":2026,"mes":3}&limit=50000&sort=ano desc, mes desc

  - `resource_id`  → identifica a tabela específica dentro do conjunto de
                      dados "desembolsos-mensais" (BNDES tem vários
                      conjuntos de dados, cada um com seu próprio ID).
  - `filters`       → um dicionário JSON com filtros de igualdade exata
                       (aqui, ano e mês) — **atenção**: o CKAN tem dois
                       parâmetros parecidos, `q` (busca textual livre, não
                       filtra por campo) e `filters` (filtro exato por
                       campo) — só o segundo funciona para o que este script
                       precisa.
  - `limit`         → quantos registros trazer numa única chamada. Testado:
                       a API aceita um limite alto (dezenas de milhares) numa
                       chamada só, sem precisar paginar com múltiplas
                       requisições — mais simples que o padrão usado para o
                       SICONFI (uma chamada por UF), embora o volume de dado
                       por chamada seja bem maior aqui.
  - `sort`          → usado sem `filters` para descobrir qual é o mês mais
                       recente disponível (ver `_mes_mais_recente` abaixo),
                       antes de fazer a chamada de verdade já filtrada.

===============================================================================
O QUE ESTE SCRIPT FAZ, PASSO A PASSO
===============================================================================
1. Descobre o (ano, mês) mais recente disponível, pedindo 1 registro
   ordenado do mais novo para o mais velho (`_mes_mais_recente`).
2. Busca todos os registros desse mês, filtrados por ano e mês
   (`_buscar_dados`).
3. Salva a resposta bruta em `data/raw/bndes/` (`_salvar_raw`).
4. Registra a coleta no Supabase.

Este script NÃO transforma o dado — grava a resposta bruta da API
exatamente como recebida (ver CLAUDE.md, seção DADOS).
"""

import json
import sys
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from supabase_raw import registrar_coleta

BASE = "https://dadosabertos.bndes.gov.br/api/3/action/datastore_search"
# ID do recurso "desembolsos-mensais" dentro do portal de dados abertos do
# BNDES — confirmado em docs/04-fontes/outras-instituicoes-2026-09.md.
RESOURCE_ID = "179950b8-b504-4cc7-b0db-9c9eed99e9ba"

DESTINO = Path(__file__).resolve().parents[3] / "data" / "raw" / "bndes"


# ------------------------------------------------------------------------
# PASSO 1 — descobrir o mês mais recente disponível
# ------------------------------------------------------------------------
def _mes_mais_recente() -> tuple[int, int]:
    """Pede 1 registro só, ordenado do ano/mês mais novo para o mais velho,
    e lê os campos `ano`/`mes` dele — mais confiável do que presumir uma
    defasagem fixa, já que a defasagem real observada (quase 6 meses) é
    maior que a "atualização trimestral" declarada pelo próprio BNDES.
    """
    params = urllib.parse.urlencode(
        {"resource_id": RESOURCE_ID, "limit": 1, "sort": "ano desc, mes desc"}
    )
    with urllib.request.urlopen(f"{BASE}?{params}", timeout=30) as resposta:
        dados = json.loads(resposta.read().decode("utf-8"))
    registro = dados["result"]["records"][0]
    return registro["ano"], registro["mes"]


# ------------------------------------------------------------------------
# PASSO 2 — buscar todos os registros de um mês
# ------------------------------------------------------------------------
def _buscar_dados(ano: int, mes: int) -> dict:
    """Busca todos os registros do mês, num único pedido (testado: a API
    aceita um `limit` alto sem precisar de múltiplas páginas). `filters`
    precisa ser um JSON de igualdade exata — diferente do parâmetro `q`
    (busca textual livre), que não filtra por campo.
    """
    params = urllib.parse.urlencode(
        {
            "resource_id": RESOURCE_ID,
            "filters": json.dumps({"ano": ano, "mes": mes}),
            "limit": 50000,
        }
    )
    with urllib.request.urlopen(f"{BASE}?{params}", timeout=120) as resposta:
        return json.loads(resposta.read().decode("utf-8"))


# ------------------------------------------------------------------------
# PASSO 3 — salvar a resposta bruta em disco
# ------------------------------------------------------------------------
def _salvar_raw(dados: dict, ano: int, mes: int) -> Path:
    DESTINO.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    arquivo = DESTINO / f"bndes_desembolsos_{ano}{mes:02d}_{timestamp}.json"
    arquivo.write_text(json.dumps(dados, ensure_ascii=False, indent=2), encoding="utf-8")
    return arquivo


# ------------------------------------------------------------------------
# Orquestração: chama os passos acima, nesta ordem
# ------------------------------------------------------------------------
def coletar() -> Path:
    ano, mes = _mes_mais_recente()
    dados = _buscar_dados(ano, mes)
    return _salvar_raw(dados, ano, mes)


if __name__ == "__main__":
    caminho = coletar()
    tamanho_kb = caminho.stat().st_size / 1024
    print(f"Coleta concluída: {caminho} ({tamanho_kb:.1f} KB)")
    registrar_coleta(fonte=DESTINO.name, arquivo=caminho, script=__file__)
