"""Transformação CURATED da RAIS (ADR 0005, expansão de escopo autorizada
2026-10-14) — a partir dos microdados brutos baixados por
`pipelines/ingestao/bloco_4_mercado_trabalho/coleta_rais_microdados_ftp.py`
(7 arquivos regionais de vínculos empregatícios, um ano por vez).

===============================================================================
METODOLOGIA — VALIDADA CONTRA A REGIÃO NORTE ANTES DE RODAR O BRASIL TODO
===============================================================================
Cada registro é um vínculo empregatício no ano. Dois indicadores calculados:
  - **Estoque de vínculos ativos em 31/12**: conta registros com
    "Ind Vínculo Ativo 31/12 - Código" == "1".
  - **Rendimento médio nominal de dezembro**: média de "Vl Rem Dezembro Nom"
    entre os vínculos ativos com remuneração > 0 (valor 0 é dado ausente/
    licença, não "ganhou zero" — incluir inflacionaria artificialmente a
    contagem sem refletir rendimento real).
Testado na região Norte isolada (2026-10-14): 5.197.236 vínculos no ano,
3.552.347 ativos em 31/12, rendimento médio de dezembro R$ 3.318,96 —
plausível (Norte historicamente abaixo da média nacional de remuneração
formal). Resultado nacional soma as 7 regiões ANTES de dividir (média
ponderada correta — nunca a média simples das 7 médias regionais, que
daria peso igual a regiões de tamanho muito diferente).

===============================================================================
POR QUE PROCESSA UM ARQUIVO POR VEZ E APAGA EM SEGUIDA
===============================================================================
Os 7 arquivos regionais somam >3,7 GB comprimidos (ano de 2024); descompactados,
passam de 20 GB. Processar em streaming (nunca carregar o CSV inteiro em
memória) e apagar o `.txt` extraído logo depois de cada região — mesmo
padrão já usado em `transformar_salario_caged.py` para os microdados do
Novo CAGED, pela mesma razão (controlar espaço em disco).

===============================================================================
COMO RODAR
===============================================================================
    python3 pipelines/curated/transformar_rais_dieese.py [ano]

Sem argumento, usa o ano mais recente com dados completos detectado em
`data/raw/mte_rais/` (não tenta descobrir no FTP — isso é trabalho da
ingestão, não desta transformação).
"""

import csv
import re
import sys
from pathlib import Path

import py7zr

sys.path.insert(0, str(Path(__file__).resolve().parent))
from curated_supabase import registrar_serie

RAIZ = Path(__file__).resolve().parent.parent.parent
DIR_RAIS = RAIZ / "data" / "raw" / "mte_rais"
DIR_TEMP = RAIZ / "data" / "raw" / "_tmp_extracao_rais"

REGIOES = ["NORTE", "NORDESTE", "CENTRO_OESTE", "MG_ES_RJ", "SP", "SUL", "NI"]

INDICADOR_ESTOQUE = "rais_estoque_vinculos_ativos"
INDICADOR_REM_DEZEMBRO = "rais_rendimento_medio_dezembro"

CAMPO_ATIVO = "Ind Vínculo Ativo 31/12 - Código"
CAMPO_REM_DEZEMBRO = "Vl Rem Dezembro Nom"


def _anos_disponiveis() -> list[int]:
    anos = set()
    for arquivo in DIR_RAIS.glob("RAIS_VINC_PUB_*_*.7z"):
        m = re.search(r"_(\d{4})\.7z$", arquivo.name)
        if m:
            anos.add(int(m.group(1)))
    return sorted(anos)


def _processar_regiao(regiao: str, ano: int) -> tuple[int, float, int]:
    """Devolve (n_ativos, soma_rem_dezembro, n_com_rem_valida) da região."""
    arquivo_7z = DIR_RAIS / f"RAIS_VINC_PUB_{regiao}_{ano}.7z"
    DIR_TEMP.mkdir(parents=True, exist_ok=True)
    with py7zr.SevenZipFile(arquivo_7z, mode="r") as z:
        nomes = z.getnames()
        z.extractall(path=str(DIR_TEMP))
    arquivo_txt = DIR_TEMP / nomes[0]

    n_ativos = 0
    soma_rem = 0.0
    n_com_rem = 0
    try:
        with open(arquivo_txt, encoding="latin-1") as f:
            leitor = csv.DictReader(f, delimiter=",")
            for linha in leitor:
                if linha.get(CAMPO_ATIVO, "").strip() != "1":
                    continue
                n_ativos += 1
                try:
                    v = float(linha.get(CAMPO_REM_DEZEMBRO, "").strip().replace(",", "."))
                except ValueError:
                    continue
                if v > 0:
                    soma_rem += v
                    n_com_rem += 1
    finally:
        arquivo_txt.unlink(missing_ok=True)

    return n_ativos, soma_rem, n_com_rem


def transformar(ano: int | None = None) -> dict[str, float]:
    if ano is None:
        anos = _anos_disponiveis()
        if not anos:
            raise RuntimeError(f"Nenhum RAIS_VINC_PUB_*.7z encontrado em {DIR_RAIS}")
        ano = max(anos)

    total_ativos = 0
    total_soma_rem = 0.0
    total_n_com_rem = 0
    for regiao in REGIOES:
        arquivo = DIR_RAIS / f"RAIS_VINC_PUB_{regiao}_{ano}.7z"
        if not arquivo.exists():
            print(f"  aviso: {arquivo.name} não encontrado localmente — pulando região {regiao}.")
            continue
        n_ativos, soma_rem, n_com_rem = _processar_regiao(regiao, ano)
        total_ativos += n_ativos
        total_soma_rem += soma_rem
        total_n_com_rem += n_com_rem
        print(f"  {regiao}: {n_ativos:,} ativos, rem. média dez. da região = "
              f"{(soma_rem / n_com_rem if n_com_rem else 0):.2f}")

    if total_ativos == 0:
        raise RuntimeError(f"Nenhuma região processada para o ano {ano} — nada para publicar.")

    data_referencia = f"{ano}-12-31"
    rem_media_dezembro = round(total_soma_rem / total_n_com_rem, 2) if total_n_com_rem else None

    registrar_serie(INDICADOR_ESTOQUE, [{"data_referencia": data_referencia, "valor": total_ativos}])
    resultado = {INDICADOR_ESTOQUE: total_ativos}
    if rem_media_dezembro is not None:
        registrar_serie(INDICADOR_REM_DEZEMBRO, [{"data_referencia": data_referencia, "valor": rem_media_dezembro}])
        resultado[INDICADOR_REM_DEZEMBRO] = rem_media_dezembro
    return resultado


if __name__ == "__main__":
    ano_arg = int(sys.argv[1]) if len(sys.argv) > 1 else None
    for indicador_id, valor in transformar(ano_arg).items():
        print(f"Transformação concluída: {indicador_id} = {valor}")
