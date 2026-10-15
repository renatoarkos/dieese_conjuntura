"""Carrega o microdado COMPLETO da RAIS (um registro por vínculo) na tabela
`rais_vinculos` (migração 0007), para a página de exploração estilo PDET/MTE
pedida pelo responsável do projeto (2026-10-14): "os dados da RAIS eu
preciso que fiquem completos na plataforma... para eu gerar cruzar da forma
que eu bem entender".

Diferente de `transformar_rais_dieese.py` (que só calcula 2 números
agregados para `indicadores_serie`), este script grava CADA vínculo como
uma linha — por isso usa conexão direta ao Postgres (`DATABASE_URL`, a
connection string de Project Settings > Database no painel do Supabase) com
`COPY`, não a API REST: só a RAIS 2024 tem ~58 milhões de vínculos, volume
grande demais para inserir um a um ou em lotes pequenos via HTTP.

COMO RODAR
====================================================================
    python3 pipelines/curated/carregar_rais_microdados.py [ano]

Pré-requisito: `DATABASE_URL` em `.env` (ex.
"postgresql://postgres:SENHA@db.XXXX.supabase.co:5432/postgres") e o pacote
`psycopg2` instalado (`pip install psycopg2-binary`).

Reaproveita o mesmo padrão de streaming de `transformar_rais_dieese.py`
(extrai uma região `.7z` por vez, processa, apaga o `.txt` em seguida —
nunca as 7 regiões descompactadas ao mesmo tempo, >20GB).

DEFLATOR (ver docs/08-decisoes-adr/0006-microdados-rais-caged.md)
====================================================================
`vl_rem_dezembro_real` usa o número-índice do IPCA (indicador
`ipca_numero_indice`, derivado por `derivar_ipca_numero_indice.py`),
deflacionado para o mês mais recente disponível desse índice — "quanto essa
remuneração valeria em reais de hoje". PROVISÓRIO: não é confirmado que o
IPCA seja o deflator que o próprio DIEESE usa para rendimentos (QF04, em
aberto). Trocar o deflator no futuro é só reprocessar esta carga.
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
DIR_RAIS = RAIZ / "data" / "raw" / "mte_rais"
DIR_TEMP = RAIZ / "data" / "raw" / "_tmp_extracao_rais"
REGIOES = ["NORTE", "NORDESTE", "CENTRO_OESTE", "MG_ES_RJ", "SP", "SUL", "NI"]
TAMANHO_LOTE = 20_000

# Nomes de coluna reais, confirmados por leitura do cabeçalho do arquivo
# (2026-10-14) — não inferidos. Não há coluna de UF direta na RAIS; uf_trab
# é derivado dos 2 primeiros dígitos do código IBGE de 7 dígitos do
# município (convenção oficial do IBGE, não inventada) — fica como código
# numérico de UF (ex. "35" = São Paulo), não sigla; o mapeamento
# código->sigla é estático e conhecido (27 UFs), fica no frontend.
COL_MUNICIPIO_TRAB = "Município Trab - Código"
COL_CBO = "CBO 2002 Ocupação - Código"
COL_CNAE_CLASSE = "CNAE 2.0 Classe - Código"
COL_SEXO = "Sexo - Código"
COL_RACA_COR = "Raça Cor - Código"
COL_FAIXA_ETARIA = "Faixa Etária - Código"
COL_IDADE = "Idade"
COL_ESCOLARIDADE = "Escolaridade Após 2005 - Código"
COL_FAIXA_REM_DEZ_SM = "Faixa Rem Dez (SM) - Código"
COL_REM_DEZEMBRO = "Vl Rem Dezembro Nom"
COL_ATIVO = "Ind Vínculo Ativo 31/12 - Código"
COL_TIPO_VINCULO = "Tipo Vínculo - Código"
COL_NATUREZA_JURIDICA = "Natureza Jurídica - Código"
COL_TAMANHO_ESTAB = "Tamanho Estabelecimento - Código"


def _anos_disponiveis() -> list[int]:
    anos = set()
    for arquivo in DIR_RAIS.glob("RAIS_VINC_PUB_*_*.7z"):
        m = re.search(r"_(\d{4})\.7z$", arquivo.name)
        if m:
            anos.add(int(m.group(1)))
    return sorted(anos)


def _indice_ipca_por_mes() -> tuple[dict[str, float], float]:
    """Devolve ({"AAAA-MM": indice}, indice_mais_recente) a partir da série
    já publicada em indicadores_serie (ver derivar_ipca_numero_indice.py).
    """
    serie = ler_serie_publicada("ipca_numero_indice")
    if not serie:
        raise RuntimeError("ipca_numero_indice vazio — rode derivar_ipca_numero_indice.py antes.")
    por_mes = {p["data_referencia"][:7]: p["valor"] for p in serie}
    indice_recente = serie[-1]["valor"]
    return por_mes, indice_recente


def _conectar():
    if psycopg2 is None:
        raise RuntimeError("psycopg2 não instalado — rode `pip install psycopg2-binary`.")
    database_url = _ENV.get("DATABASE_URL") or os.environ.get("DATABASE_URL")
    if not database_url:
        raise RuntimeError(
            "DATABASE_URL não configurado em .env — pegue em Supabase > Project Settings > "
            "Database > Connection string (URI). Necessário só para esta carga em massa, "
            "não para os demais scripts de pipelines/ (que usam a API REST)."
        )
    return psycopg2.connect(database_url)


def _linhas_regiao(regiao: str, ano: int, indice_por_mes: dict[str, float], indice_recente: float):
    """Gera tuplas prontas para COPY, uma por vínculo da região — streaming,
    nunca acumula a região inteira em memória.
    """
    arquivo_7z = DIR_RAIS / f"RAIS_VINC_PUB_{regiao}_{ano}.7z"
    DIR_TEMP.mkdir(parents=True, exist_ok=True)
    with py7zr.SevenZipFile(arquivo_7z, mode="r") as z:
        nomes = z.getnames()
        z.extractall(path=str(DIR_TEMP))
    arquivo_txt = DIR_TEMP / nomes[0]
    mes_referencia = f"{ano}-12"
    indice_dezembro = indice_por_mes.get(mes_referencia)

    try:
        with open(arquivo_txt, encoding="latin-1") as f:
            leitor = csv.DictReader(f, delimiter=",")
            for linha in leitor:
                def num(campo, default=None):
                    v = (linha.get(campo) or "").strip().replace(",", ".")
                    if not v:
                        return default
                    try:
                        return float(v)
                    except ValueError:
                        return default

                def inteiro(campo, default=None):
                    v = num(campo)
                    return int(v) if v is not None else default

                cbo = (linha.get(COL_CBO) or "").strip()
                cnae = (linha.get(COL_CNAE_CLASSE) or "").strip()
                rem_nom = num(COL_REM_DEZEMBRO)
                rem_real = (
                    round(rem_nom * (indice_recente / indice_dezembro), 2)
                    if rem_nom and indice_dezembro
                    else None
                )

                yield (
                    ano,
                    (linha.get(COL_MUNICIPIO_TRAB) or "").strip()[:2] or None,  # 2 primeiros dígitos do código IBGE de município = UF
                    (linha.get(COL_MUNICIPIO_TRAB) or "").strip() or None,
                    cbo or None,
                    cbo[:1] or None,
                    cnae or None,
                    cnae[:2] or None,
                    inteiro(COL_SEXO),
                    inteiro(COL_RACA_COR),
                    inteiro(COL_FAIXA_ETARIA),
                    inteiro(COL_IDADE),
                    inteiro(COL_ESCOLARIDADE),
                    inteiro(COL_FAIXA_REM_DEZ_SM),
                    rem_nom,
                    rem_real,
                    (linha.get(COL_ATIVO) or "").strip() == "1",
                    inteiro(COL_TIPO_VINCULO),
                    (linha.get(COL_NATUREZA_JURIDICA) or "").strip() or None,
                    inteiro(COL_TAMANHO_ESTAB),
                )
    finally:
        arquivo_txt.unlink(missing_ok=True)


COLUNAS = (
    "ano, uf_trab, municipio_trab_codigo, cbo_2002_codigo, cbo_2002_grande_grupo, "
    "cnae20_classe_codigo, cnae20_divisao, sexo_codigo, raca_cor_codigo, faixa_etaria_codigo, "
    "idade, escolaridade_codigo, faixa_rem_dez_sm_codigo, vl_rem_dezembro_nom, "
    "vl_rem_dezembro_real, vinculo_ativo_3112, tipo_vinculo_codigo, natureza_juridica_codigo, "
    "tamanho_estabelecimento_codigo"
)


def carregar(ano: int | None = None) -> int:
    if ano is None:
        anos = _anos_disponiveis()
        if not anos:
            raise RuntimeError(f"Nenhum RAIS_VINC_PUB_*.7z encontrado em {DIR_RAIS}")
        ano = max(anos)

    indice_por_mes, indice_recente = _indice_ipca_por_mes()
    conexao = _conectar()
    total = 0
    try:
        with conexao:
            with conexao.cursor() as cur:
                cur.execute("delete from rais_vinculos where ano = %s", (ano,))
                for regiao in REGIOES:
                    arquivo = DIR_RAIS / f"RAIS_VINC_PUB_{regiao}_{ano}.7z"
                    if not arquivo.exists():
                        print(f"  aviso: {arquivo.name} não encontrado — pulando {regiao}.")
                        continue
                    n_regiao = 0
                    lote = []
                    for linha in _linhas_regiao(regiao, ano, indice_por_mes, indice_recente):
                        lote.append(linha)
                        if len(lote) >= TAMANHO_LOTE:
                            psycopg2.extras.execute_values(
                                cur, f"insert into rais_vinculos ({COLUNAS}) values %s", lote
                            )
                            n_regiao += len(lote)
                            lote = []
                    if lote:
                        psycopg2.extras.execute_values(
                            cur, f"insert into rais_vinculos ({COLUNAS}) values %s", lote
                        )
                        n_regiao += len(lote)
                    total += n_regiao
                    print(f"  {regiao}: {n_regiao:,} vínculos carregados.")
    finally:
        conexao.close()
    return total


if __name__ == "__main__":
    ano_arg = int(sys.argv[1]) if len(sys.argv) > 1 else None
    total = carregar(ano_arg)
    print(f"Carga concluída: {total:,} vínculos em rais_vinculos.")
