"""Carrega o microdado COMPLETO do Novo CAGED (um registro por movimentação
de admissão/desligamento) na tabela `caged_movimentacoes` (migração 0007),
para a página de exploração estilo PDET/MTE — mesmo propósito e mesma
infraestrutura de `carregar_rais_microdados.py` (ler esse script primeiro,
a documentação de deflator/conexão/streaming é a mesma, não repetida aqui).

Diferente da RAIS (um arquivo por região, por ano), o CAGED é um arquivo por
MÊS (`CAGEDMOV{AAAAMM}.7z`), e o mês mais recente pode ter sido baixado mais
de uma vez (o MTE republica correções do mês corrente — ver
`coleta_caged_microdados_ftp.py`); este script usa sempre a versão mais
recente de cada mês (nome com timestamp mais alto, ou o arquivo sem
timestamp se não houver correção).

COMO RODAR
    python3 pipelines/curated/carregar_caged_microdados.py [AAAAMM]

Sem argumento, carrega todos os meses disponíveis localmente que ainda não
foram carregados (reprocessa um mês = apaga as linhas daquele mês antes,
idempotente).
"""

from __future__ import annotations

import csv
import os
import re
import sys
from pathlib import Path

import py7zr

sys.path.insert(0, str(Path(__file__).resolve().parent))
from curated_supabase import _ENV, ler_serie_publicada  # noqa: E402

try:
    import psycopg2
    import psycopg2.extras
except ImportError:  # pragma: no cover
    psycopg2 = None

RAIZ = Path(__file__).resolve().parent.parent.parent
DIR_CAGED = RAIZ / "data" / "raw" / "mte_caged"
DIR_TEMP = RAIZ / "data" / "raw" / "_tmp_extracao_caged_micro"
TAMANHO_LOTE = 20_000


def _arquivo_mais_recente_por_mes() -> dict[str, Path]:
    candidatos: dict[str, list[tuple[str, Path]]] = {}
    for arquivo in DIR_CAGED.glob("CAGEDMOV??????*.7z"):
        m = re.match(r"CAGEDMOV(\d{6})(?:_(\d{8}T\d{6}Z))?\.7z$", arquivo.name)
        if not m:
            continue
        mes, timestamp = m.group(1), m.group(2) or ""
        candidatos.setdefault(mes, []).append((timestamp, arquivo))
    return {mes: sorted(versoes, key=lambda t: t[0])[-1][1] for mes, versoes in candidatos.items()}


def _indice_ipca_por_mes() -> tuple[dict[str, float], float]:
    serie = ler_serie_publicada("ipca_numero_indice")
    if not serie:
        raise RuntimeError("ipca_numero_indice vazio — rode derivar_ipca_numero_indice.py antes.")
    por_mes = {p["data_referencia"][:7]: p["valor"] for p in serie}
    return por_mes, serie[-1]["valor"]


def _conectar():
    if psycopg2 is None:
        raise RuntimeError("psycopg2 não instalado — rode `pip install psycopg2-binary`.")
    database_url = _ENV.get("DATABASE_URL") or os.environ.get("DATABASE_URL")
    if not database_url:
        raise RuntimeError("DATABASE_URL não configurado em .env — ver carregar_rais_microdados.py.")
    return psycopg2.connect(database_url)


COLUNAS = (
    "competencia_mov, regiao, uf, municipio_codigo, cnae20_secao, cnae20_subclasse, "
    "saldo_movimentacao, tipo_movimentacao_codigo, cbo2002_codigo, cbo2002_grande_grupo, "
    "categoria_codigo, grau_instrucao_codigo, idade, raca_cor_codigo, sexo_codigo, "
    "salario_mensal, salario_mensal_real, trabalho_intermitente, trabalho_parcial"
)


def _linhas_mes(arquivo_7z: Path, mes: str, indice_do_mes: float | None, indice_recente: float):
    DIR_TEMP.mkdir(parents=True, exist_ok=True)
    with py7zr.SevenZipFile(arquivo_7z, mode="r") as z:
        nomes = z.getnames()
        z.extractall(path=str(DIR_TEMP))
    arquivo_txt = DIR_TEMP / nomes[0]
    data_iso = f"{mes[:4]}-{mes[4:]}-01"

    try:
        with open(arquivo_txt, encoding="utf-8") as f:
            leitor = csv.DictReader(f, delimiter=";")
            for linha in leitor:
                def num(campo):
                    v = (linha.get(campo) or "").strip().replace(",", ".")
                    try:
                        return float(v) if v else None
                    except ValueError:
                        return None

                def inteiro(campo):
                    v = num(campo)
                    return int(v) if v is not None else None

                cbo = (linha.get("cbo2002ocupação") or "").strip()
                saldo_raw = (linha.get("saldomovimentação") or "").strip()
                saldo = int(saldo_raw) if saldo_raw in ("1", "-1") else None
                salario = num("salário")
                salario_real = (
                    round(salario * (indice_recente / indice_do_mes), 2)
                    if salario and indice_do_mes else None
                )

                yield (
                    (linha.get("competênciamov") or data_iso.replace("-", "")[:6]).strip() or mes,
                    (linha.get("região") or "").strip() or None,
                    (linha.get("uf") or "").strip() or None,
                    (linha.get("município") or "").strip() or None,
                    (linha.get("seção") or "").strip() or None,
                    (linha.get("subclasse") or "").strip() or None,
                    saldo,
                    (linha.get("tipomovimentação") or "").strip() or None,
                    cbo or None,
                    cbo[:1] or None,
                    inteiro("categoria"),
                    inteiro("graudeinstrução"),
                    inteiro("idade"),
                    inteiro("raçacor"),
                    inteiro("sexo"),
                    salario,
                    salario_real,
                    (linha.get("indtrabintermitente") or "").strip() == "1",
                    (linha.get("indtrabparcial") or "").strip() == "1",
                )
    finally:
        arquivo_txt.unlink(missing_ok=True)


def carregar(meses_alvo: list[str] | None = None) -> int:
    disponiveis = _arquivo_mais_recente_por_mes()
    if not disponiveis:
        raise RuntimeError(f"Nenhum CAGEDMOV*.7z encontrado em {DIR_CAGED}")
    meses = meses_alvo or sorted(disponiveis.keys())

    indice_por_mes, indice_recente = _indice_ipca_por_mes()
    conexao = _conectar()
    total = 0
    try:
        with conexao:
            with conexao.cursor() as cur:
                for mes in meses:
                    arquivo = disponiveis.get(mes)
                    if not arquivo:
                        print(f"  aviso: {mes} não encontrado localmente — pulando.")
                        continue
                    cur.execute("delete from caged_movimentacoes where competencia_mov = %s", (mes,))
                    n_mes = 0
                    lote = []
                    for linha in _linhas_mes(arquivo, mes, indice_por_mes.get(f"{mes[:4]}-{mes[4:]}"), indice_recente):
                        lote.append(linha)
                        if len(lote) >= TAMANHO_LOTE:
                            psycopg2.extras.execute_values(
                                cur, f"insert into caged_movimentacoes ({COLUNAS}) values %s", lote
                            )
                            n_mes += len(lote)
                            lote = []
                    if lote:
                        psycopg2.extras.execute_values(
                            cur, f"insert into caged_movimentacoes ({COLUNAS}) values %s", lote
                        )
                        n_mes += len(lote)
                    total += n_mes
                    print(f"  {mes} ({arquivo.name}): {n_mes:,} movimentações carregadas.")
    finally:
        conexao.close()
    return total


if __name__ == "__main__":
    meses_arg = sys.argv[1:] if len(sys.argv) > 1 else None
    total = carregar(meses_arg)
    print(f"Carga concluída: {total:,} movimentações em caged_movimentacoes.")
