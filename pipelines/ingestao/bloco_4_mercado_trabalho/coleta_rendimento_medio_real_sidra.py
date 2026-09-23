"""Coleta bruta do rendimento médio real habitual do trabalho principal
(PNAD Contínua trimestral) via API pública do SIDRA/IBGE.

Piloto técnico controlado — ver docs/08-decisoes-adr/0002-expansao-piloto-por-blocos.md
Fonte confirmada em: docs/04-fontes/ibge-sidra.md (Tabela SIDRA 5440)

===============================================================================
O QUE A TABELA 5440 MEDE, E POR QUE ELA TINHA FICADO DE FORA DO PILOTO
===============================================================================
Valor médio mensal do rendimento do trabalho habitualmente recebido no
trabalho principal, pessoas de 14+ anos ocupadas, **já em termos reais** (a
própria tabela do IBGE entrega o valor deflacionado, não o valor nominal),
por posição na ocupação e categoria do emprego (empregado com/sem carteira,
setor público, empregador, conta própria etc.).

Esta tabela ficou de fora do piloto original porque, na 1ª rodada de
Discovery de Fontes, só a API de metadados (`servicodados.ibge.gov.br`) foi
testada — confirmando que a tabela existe e está ativa, mas sem testar a
chamada real de valores. Este script fecha essa lacuna: a chamada de valores
foi testada diretamente (233 registros retornados, de 1º tri/2012 a 2º
tri/2026) antes de escrever este script.

**Limitação que continua em aberto, e não é resolvida por este script**: o
material do DIEESE indica um deflacionamento ADICIONAL próprio (Nota Técnica
interna), por cima do valor que a Tabela 5440 já entrega em termos reais. Não
é possível determinar, só com fontes públicas, se isso é uma dupla deflação
(risco metodológico) ou se o DIEESE parte de uma série nominal diferente,
ainda não identificada — ver `docs/04-fontes/ibge-sidra.md`, seção "Achado a
validar". Este script coleta só o dado bruto do IBGE; a etapa de
deflacionamento do DIEESE, se existir, é uma transformação de camada
STAGING/curadoria, não RAW, e depende de acesso a documento interno do
DIEESE que este projeto não tem.

===============================================================================
COMO FUNCIONA A API DO SIDRA (mesmo padrão dos demais scripts "..._sidra.py")
===============================================================================
Ver `coleta_pib_sidra.py` para a explicação completa do formato de URL. A
única diferença aqui: a URL não especifica um código de classificação (ex.
`c2/all` na Tabela 4093) — testado diretamente e confirmado que, quando você
omite a classificação, o SIDRA devolve todas as categorias por padrão (aqui,
as 11 categorias de "posição na ocupação e categoria do emprego", identificada
pelo campo `D4N` na resposta) — não é necessário descobrir o código exato da
classificação para esta tabela.

===============================================================================
O QUE ESTE SCRIPT FAZ, PASSO A PASSO
===============================================================================
1. Monta a URL da consulta (constante `URL`, ver acima).
2. Busca os dados na API (`_buscar_dados`).
3. Salva a resposta, sem alterar nada, em `data/raw/ibge_sidra/` com um nome
   de arquivo que inclui a tabela e o instante da coleta (`_salvar_raw`).
4. Registra a coleta no Supabase — arquivo no Storage + linha em
   `raw_ingestoes` (`registrar_coleta`, importado de `pipelines/supabase_raw.py`).

Este script NÃO transforma o dado — grava a resposta bruta da API exatamente
como recebida, respeitando o princípio de que a camada RAW nunca deve ser
editada manualmente ou pré-processada (ver CLAUDE.md, seção DADOS).
"""

import json
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from supabase_raw import registrar_coleta

# Tabela 5440 do SIDRA: "Rendimento médio mensal real..." — PNAD Contínua
# trimestral. Sem código de classificação: confirmado que a API devolve
# todas as categorias de "posição na ocupação" por padrão nesse caso.
URL = "https://apisidra.ibge.gov.br/values/t/5440/n1/all/v/all/p/all"

DESTINO = Path(__file__).resolve().parents[3] / "data" / "raw" / "ibge_sidra"


# ------------------------------------------------------------------------
# PASSO 1 — buscar os dados na API
# ------------------------------------------------------------------------
def _buscar_dados() -> list:
    """Faz a requisição HTTP e devolve o JSON já decodificado.

    `timeout=90` é maior que o padrão de 60s usado nos outros scripts SIDRA
    deste bloco porque esta consulta traz mais dimensões cruzadas (11
    categorias de posição na ocupação × todos os trimestres desde 2012) e,
    na prática, demora um pouco mais para a API montar a resposta.
    """
    with urllib.request.urlopen(URL, timeout=90) as resposta:
        return json.loads(resposta.read().decode("utf-8"))


# ------------------------------------------------------------------------
# PASSO 2 — salvar a resposta bruta em disco
# ------------------------------------------------------------------------
def _salvar_raw(dados: list) -> Path:
    """Grava `dados` como JSON, formatado (indent=2) só para ficar legível
    para humanos que forem inspecionar o arquivo. Nome do arquivo leva um
    timestamp UTC porque o IBGE revisa dados publicados (ver nota sobre a
    reponderação de 2025 em docs/04-fontes/ibge-sidra.md) — nunca
    sobrescrevemos a coleta anterior.
    """
    DESTINO.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    arquivo = DESTINO / f"rendimento_medio_real_sidra_5440_{timestamp}.json"
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
