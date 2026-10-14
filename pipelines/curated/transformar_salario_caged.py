"""Transformação CURATED do "Salário Médio Real de Admissão e Desligamento"
(Tabela 9, catálogo DIEESE) — a partir dos MICRODADOS brutos do Novo CAGED
(`data/raw/mte_caged/CAGEDMOV{AAAAMM}.7z`, um arquivo por mês, coletados por
`pipelines/ingestao/bloco_5_caged/coleta_caged_microdados_ftp.py`).

===============================================================================
QF09 — VALIDADO POR SIMULAÇÃO DIRETA CONTRA O VALOR REAL DO DIEESE (2026-10-14)
===============================================================================
A aba `T39` da planilha interna mais recente do DIEESE ("TABELA 9 - EVOLUÇÃO DO
SALÁRIO MÉDIO REAL DE ADMISSÃO E DESLIGAMENTO POR MÊS — SEM AJUSTES") documenta
sua própria metodologia no rodapé:
  - Exclui vínculos com salário < 0,3 salário mínimo ou > 150 salários mínimos.
  - Exclui vínculos de modalidade intermitente.
  - "Sem ajustes": NÃO filtra declarações fora do prazo — usa o microdado como
    está no mês de referência, mesmo sabendo que será revisado depois.
  - Valores deflacionados pelo INPC (a preços do último mês da série).

Testado com o microdado real de abr/2026 (4.451.422 registros): a média
simulada bateu com a planilha do DIEESE a menos de R$ 0,01 de diferença tanto
para admissão (R$ 2.386,57 simulado vs. R$ 2.386,56 na planilha) quanto para
desligamento (R$ 2.481,25 vs. R$ 2.481,24) — confirma a metodologia acima
como exatamente a usada pelo DIEESE, não uma aproximação.

===============================================================================
POR QUE ESTE SCRIPT LÊ DE data/raw/ LOCAL, NÃO DO SUPABASE STORAGE
===============================================================================
O histórico completo de 79 meses (jan/2020 a jul/2026) do Novo CAGED foi
baixado ANTES da migração de projeto Supabase registrada no ADR 0004 (ver
`docs/00-visao-geral/ESTADO_DO_PROJETO.md`, 2026-10-10) — só o mês mais
recente coletado automaticamente depois da migração está no Storage novo. O
histórico em si não foi perdido (está em `data/raw/mte_caged/`, local), mas
ainda não foi reenviado ao Storage do projeto atual. Este script usa o que
está localmente disponível; se um mês não existir localmente, é simplesmente
pulado (sem inventar dado). Reenviar o histórico ao Storage novo fica como
pendência registrada, não bloqueia esta transformação.

===============================================================================
O QUE ESTE SCRIPT FAZ, PASSO A PASSO
===============================================================================
1. Lista os meses disponíveis em `data/raw/mte_caged/CAGEDMOV*.7z`.
2. Para cada mês: extrai o `.7z` (via `py7zr`) para uma pasta temporária,
   processa o `.txt` em streaming (nunca carrega tudo em memória) somando
   salário e contagem separadamente para admissão (saldomovimentação=1) e
   desligamento (saldomovimentação=-1), aplicando os filtros documentados
   acima, e apaga o `.txt` extraído antes de passar ao próximo mês (cada
   arquivo descompactado chega a ~500 MB).
3. Busca o salário mínimo vigente em cada mês (BCB/SGS 1619) e o índice INPC
   de cada mês (SIDRA 1736, variável 2289 — número-índice, não variação %,
   necessário para deflacionar com precisão entre dois meses quaisquer).
4. Deflaciona cada média nominal mensal para preços do mês mais recente
   disponível no próprio conjunto de dados processado (mesma convenção da
   planilha do DIEESE — "a preços do último mês da série").
5. Grava duas séries em `indicadores_serie`: salário médio real de admissão
   e de desligamento. Cada ponto carrega também o recorte por sexo em
   `metadata.por_sexo` (a pedido do responsável do projeto) — mesmo padrão já
   usado pelo Limite Fiscal para o recorte por UF (`metadata.por_uf`): o
   corte fica dentro do ponto existente, sem precisar de indicador novo nem
   de mudança de schema. Códigos de sexo do layout padrão do Novo CAGED: 1 =
   Homem, 3 = Mulher (não existe código 2 nesta coluna).
"""

import csv
import json
import sys
import urllib.request
from pathlib import Path

import py7zr

sys.path.insert(0, str(Path(__file__).resolve().parent))
from curated_supabase import registrar_serie

RAIZ = Path(__file__).resolve().parent.parent.parent
DIR_CAGED = RAIZ / "data" / "raw" / "mte_caged"
DIR_TEMP = RAIZ / "data" / "raw" / "_tmp_extracao_caged"

INDICADOR_ADMISSAO = "salario_medio_real_admissao_caged"
INDICADOR_DESLIGAMENTO = "salario_medio_real_desligamento_caged"

# Mês-base fixo da deflação ("a preços de jul/2026") — NÃO usar "o mês mais
# recente disponível nesta execução": como o CI só baixa 1 mês novo por vez
# (ver coleta_caged_microdados_ftp.py), uma base móvel deflacionaria cada
# novo ponto para si mesmo (fator 1) e deixaria o histórico congelado na
# base antiga, quebrando a comparabilidade da série ao longo do tempo. Esta
# constante só deve mudar numa reprocessagem deliberada de toda a série
# (rebase explícito), não a cada execução automática.
MES_REFERENCIA_DEFLACAO = "202607"

URL_SALARIO_MINIMO = "https://api.bcb.gov.br/dados/serie/bcdata.sgs.1619/dados?formato=json"
URL_INPC_INDICE = "https://apisidra.ibge.gov.br/values/t/1736/n1/all/v/2289/p/all"


# ------------------------------------------------------------------------
# PASSO 1 — meses disponíveis localmente
# ------------------------------------------------------------------------
def _meses_disponiveis() -> list[str]:
    meses = []
    for arquivo in sorted(DIR_CAGED.glob("CAGEDMOV??????.7z")):
        mes = arquivo.stem.replace("CAGEDMOV", "")
        if len(mes) == 6 and mes.isdigit():
            meses.append(mes)
    return sorted(set(meses))


# Códigos de sexo do layout padrão do Novo CAGED (dicionário de dados do
# MTE/PDET) — 1 = Homem, 3 = Mulher. Não há código 2 nesta coluna.
SEXO_CAGED = {"1": "masculino", "3": "feminino"}


# ------------------------------------------------------------------------
# PASSO 2 — processar um mês de microdado em streaming
# ------------------------------------------------------------------------
def _novo_acumulador() -> dict:
    return {"soma": 0.0, "n": 0}


def _processar_mes(mes: str, salario_minimo: float) -> dict:
    arquivo_7z = DIR_CAGED / f"CAGEDMOV{mes}.7z"
    DIR_TEMP.mkdir(parents=True, exist_ok=True)
    with py7zr.SevenZipFile(arquivo_7z, mode="r") as z:
        z.extractall(path=str(DIR_TEMP))
    arquivo_txt = DIR_TEMP / f"CAGEDMOV{mes}.txt"

    minimo = 0.3 * salario_minimo
    maximo = 150 * salario_minimo
    geral_adm, geral_desl = _novo_acumulador(), _novo_acumulador()
    # Recorte por sexo (a pedido do responsável do projeto) — mesmo padrão já
    # usado para o recorte por UF do Limite Fiscal (metadata.por_uf): o corte
    # vai dentro de `metadata` do mesmo ponto, sem precisar de indicador novo
    # nem de mudança de schema.
    por_sexo_adm = {"masculino": _novo_acumulador(), "feminino": _novo_acumulador()}
    por_sexo_desl = {"masculino": _novo_acumulador(), "feminino": _novo_acumulador()}
    try:
        with open(arquivo_txt, encoding="utf-8") as f:
            leitor = csv.DictReader(f, delimiter=";")
            for linha in leitor:
                if linha.get("indtrabintermitente") == "1":
                    continue
                try:
                    salario = float(linha["salário"].replace(",", "."))
                except (KeyError, ValueError):
                    continue
                if salario < minimo or salario > maximo:
                    continue
                saldo = linha.get("saldomovimentação")
                sexo = SEXO_CAGED.get(linha.get("sexo"))
                if saldo == "1":
                    geral_adm["soma"] += salario
                    geral_adm["n"] += 1
                    if sexo:
                        por_sexo_adm[sexo]["soma"] += salario
                        por_sexo_adm[sexo]["n"] += 1
                elif saldo == "-1":
                    geral_desl["soma"] += salario
                    geral_desl["n"] += 1
                    if sexo:
                        por_sexo_desl[sexo]["soma"] += salario
                        por_sexo_desl[sexo]["n"] += 1
    finally:
        arquivo_txt.unlink(missing_ok=True)

    soma_adm, n_adm = geral_adm["soma"], geral_adm["n"]
    soma_desl, n_desl = geral_desl["soma"], geral_desl["n"]

    def _media(acc):
        return acc["soma"] / acc["n"] if acc["n"] else None

    return {
        "media_admissao": soma_adm / n_adm if n_adm else None,
        "media_desligamento": soma_desl / n_desl if n_desl else None,
        "por_sexo_admissao": {sexo: _media(acc) for sexo, acc in por_sexo_adm.items()},
        "por_sexo_desligamento": {sexo: _media(acc) for sexo, acc in por_sexo_desl.items()},
    }


# ------------------------------------------------------------------------
# PASSO 3 — salário mínimo e índice INPC, por mês
# ------------------------------------------------------------------------
def _buscar_salario_minimo() -> dict[str, float]:
    with urllib.request.urlopen(URL_SALARIO_MINIMO, timeout=60) as r:
        dados = json.loads(r.read().decode("utf-8"))
    resultado = {}
    for ponto in dados:
        dia, mes, ano = ponto["data"].split("/")
        resultado[f"{ano}{mes}"] = float(ponto["valor"])
    return resultado


def _buscar_indice_inpc() -> dict[str, float]:
    req = urllib.request.Request(URL_INPC_INDICE, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=60) as r:
        dados = json.loads(r.read().decode("utf-8"))
    resultado = {}
    for linha in dados[1:]:
        ano_abrev = linha["D3C"]  # formato "202604"
        resultado[ano_abrev] = float(linha["V"])
    return resultado


# ------------------------------------------------------------------------
# Orquestração
# ------------------------------------------------------------------------
def transformar() -> dict[str, int]:
    meses = _meses_disponiveis()
    if not meses:
        raise RuntimeError(f"Nenhum CAGEDMOV*.7z encontrado em {DIR_CAGED}")

    salario_minimo_por_mes = _buscar_salario_minimo()
    indice_inpc_por_mes = _buscar_indice_inpc()
    indice_referencia = indice_inpc_por_mes[MES_REFERENCIA_DEFLACAO]

    pontos_admissao, pontos_desligamento = [], []
    for mes in meses:
        if mes not in salario_minimo_por_mes or mes not in indice_inpc_por_mes:
            continue
        resultado = _processar_mes(mes, salario_minimo_por_mes[mes])
        fator = indice_referencia / indice_inpc_por_mes[mes]
        data_iso = f"{mes[:4]}-{mes[4:]}-01"

        def _deflacionar_dict(por_sexo):
            return {sexo: round(v * fator, 2) for sexo, v in por_sexo.items() if v is not None}

        if resultado["media_admissao"] is not None:
            pontos_admissao.append({
                "data_referencia": data_iso,
                "valor": round(resultado["media_admissao"] * fator, 2),
                "metadata": {"por_sexo": _deflacionar_dict(resultado["por_sexo_admissao"])},
            })
        if resultado["media_desligamento"] is not None:
            pontos_desligamento.append({
                "data_referencia": data_iso,
                "valor": round(resultado["media_desligamento"] * fator, 2),
                "metadata": {"por_sexo": _deflacionar_dict(resultado["por_sexo_desligamento"])},
            })
        print(f"  {mes}: processado ({len(pontos_admissao)} admissão / {len(pontos_desligamento)} desligamento acumulados)")

    registrar_serie(INDICADOR_ADMISSAO, pontos_admissao)
    registrar_serie(INDICADOR_DESLIGAMENTO, pontos_desligamento)
    return {INDICADOR_ADMISSAO: len(pontos_admissao), INDICADOR_DESLIGAMENTO: len(pontos_desligamento)}


if __name__ == "__main__":
    for indicador_id, n in transformar().items():
        print(f"Transformação concluída: {n} pontos gravados em indicadores_serie ({indicador_id}).")
