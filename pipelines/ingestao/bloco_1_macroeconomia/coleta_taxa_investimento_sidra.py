"""Coleta bruta da taxa de investimento (Formação Bruta de Capital Fixo em
relação ao PIB) via API pública do SIDRA/IBGE.

Piloto técnico controlado — ver docs/08-decisoes-adr/0002-expansao-piloto-por-blocos.md
Fonte confirmada em: docs/05-indicadores/CATALOGO_MESTRE_INDICADORES.md (indicador novo,
achado em investigação de completude da planilha do DIEESE, 2026-09-23)

===============================================================================
O QUE ESTE INDICADOR MEDE, E COMO FOI ENCONTRADO
===============================================================================
A taxa de investimento mede a proporção da Formação Bruta de Capital Fixo
(FBCF — gasto em máquinas, equipamentos, construção etc., o investimento
produtivo da economia) em relação ao PIB, trimestral, já calculada e
publicada pelo próprio IBGE nas Contas Nacionais Trimestrais — não é preciso
calcular FBCF/PIB manualmente a partir de duas tabelas separadas.

Este indicador não estava em nenhum dos 33 indicadores do catálogo P1
original — foi encontrado ao abrir um arquivo da própria planilha de dados do
DIEESE (`materiais/originais/.../taxa_invest.xlsx`), cujo título de tabela
("Tabela 6727 - Taxa de investimento") e rodapé de fonte ("Fonte: IBGE -
Contas Nacionais Trimestrais") apontaram direto para a tabela SIDRA
correspondente — testada e confirmada com dado real.

===============================================================================
COMO FUNCIONA A API DO SIDRA (vale para todos os scripts "..._sidra.py")
===============================================================================
Ver `coleta_pib_sidra.py` para a explicação completa do formato de URL. Aqui,
como em outros casos já vistos neste piloto, a consulta não precisa
especificar uma classificação — a Tabela 6727 tem uma única variável ("Taxa
de investimento") e nenhum corte adicional, então `v/all/p/all` já traz a
série completa.

===============================================================================
O QUE ESTE SCRIPT FAZ, PASSO A PASSO
===============================================================================
1. Monta a URL da consulta (constante `URL`, ver acima).
2. Busca os dados na API (`_buscar_dados`).
3. Salva a resposta em `data/raw/ibge_sidra/` (`_salvar_raw`).
4. Registra a coleta no Supabase.

Este script NÃO transforma o dado — grava a resposta bruta da API exatamente
como recebida (ver CLAUDE.md, seção DADOS).
"""

import json
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from supabase_raw import registrar_coleta

# Tabela 6727 do SIDRA: "Taxa de investimento" — Contas Nacionais Trimestrais.
URL = "https://apisidra.ibge.gov.br/values/t/6727/n1/all/v/all/p/all"

DESTINO = Path(__file__).resolve().parents[3] / "data" / "raw" / "ibge_sidra"


# ------------------------------------------------------------------------
# PASSO 1 — buscar os dados na API
# ------------------------------------------------------------------------
def _buscar_dados() -> list:
    with urllib.request.urlopen(URL, timeout=60) as resposta:
        return json.loads(resposta.read().decode("utf-8"))


# ------------------------------------------------------------------------
# PASSO 2 — salvar a resposta bruta em disco
# ------------------------------------------------------------------------
def _salvar_raw(dados: list) -> Path:
    """O IBGE revisa a taxa de investimento entre divulgações (confirmado:
    entre duas cópias da planilha do DIEESE, o mesmo trimestre apareceu com
    valores diferentes — 16,8% numa versão, 16,6% na versão seguinte) — por
    isso o timestamp no nome do arquivo, nunca sobrescrevendo a coleta
    anterior.
    """
    DESTINO.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    arquivo = DESTINO / f"taxa_investimento_sidra_6727_{timestamp}.json"
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
