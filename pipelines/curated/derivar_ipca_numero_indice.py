"""Deriva o número-índice do IPCA, encadeado a partir da série de variação
mensal já publicada (indicador `ipca`), e publica como novo indicador
`ipca_numero_indice`.

POR QUE ISSO EXISTE
====================================================================
A RAIS e o Novo CAGED trazem remuneração/salário em valor NOMINAL. Para
guardar também um valor deflacionado (ver migração 0007,
`vl_rem_dezembro_real`/`salario_mensal_real`), é preciso um número-índice de
preços, não uma variação percentual mês a mês — e o indicador `ipca` já
publicado na plataforma é a variação mensal (%), não o índice acumulado.

Esta é uma TRANSFORMAÇÃO, não uma fonte nova: o número-índice é calculado
por encadeamento multiplicativo padrão (every ponto = ponto anterior ×
(1 + variação/100)), a partir de um dado que já está na própria plataforma,
com base 100 no primeiro mês disponível. É reproduzível e auditável — não é
"inventar dado" (CLAUDE.md).

RESSALVA METODOLÓGICA (registrada também na migração 0007 e no ADR 0006):
o IPCA é usado aqui como deflator PROVISÓRIO, por ser o índice mais comum em
portais de dados públicos — não é confirmado que seja o deflator que o
próprio DIEESE usa para rendimentos (essa é a pergunta em aberto QF04,
e-mail enviado à equipe do DIEESE, sem resposta até o momento). Se/quando
QF04 for respondida, trocar a base de cálculo aqui é a única mudança
necessária — os valores `_real` em rais_vinculos/caged_movimentacoes
dependem só deste número-índice, não precisam ser recalculados na mão.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from curated_supabase import ler_serie_publicada, registrar_serie  # noqa: E402


def derivar() -> list[dict]:
    serie_variacao = ler_serie_publicada("ipca")
    if not serie_variacao:
        raise RuntimeError("Série 'ipca' (variação mensal) não encontrada em indicadores_serie — rode transformar_ipca_sidra.py antes.")

    indice = 100.0
    pontos = []
    for i, ponto in enumerate(serie_variacao):
        if i > 0:
            indice *= 1 + (ponto["valor"] / 100.0)
        pontos.append({
            "data_referencia": ponto["data_referencia"],
            "valor": round(indice, 6),
            "metadata": {"base": f"100 em {serie_variacao[0]['data_referencia']}", "derivado_de": "ipca"},
        })
    return pontos


if __name__ == "__main__":
    pontos = derivar()
    registrar_serie("ipca_numero_indice", pontos)
    print(f"ipca_numero_indice: {len(pontos)} pontos publicados "
          f"({pontos[0]['data_referencia']} = {pontos[0]['valor']} ... "
          f"{pontos[-1]['data_referencia']} = {pontos[-1]['valor']})")
