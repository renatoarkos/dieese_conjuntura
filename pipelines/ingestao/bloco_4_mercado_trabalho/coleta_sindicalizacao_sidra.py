"""Coleta bruta da taxa de sindicalização das pessoas ocupadas, por grupamento de
atividade, via API pública do SIDRA/IBGE.

Piloto técnico controlado — ver docs/08-decisoes-adr/0002-expansao-piloto-por-blocos.md
Fonte confirmada em: docs/04-fontes/ibge-sidra.md — investigação de lacunas,
2026-09-22.

ACHADO: este indicador estava sem NENHUMA fonte confirmada no projeto. Localizada e
testada a Tabela SIDRA 8676 (PNAD Contínua anual, módulo "Características Adicionais
do Mercado de Trabalho") — valor de 2024 (8,9%) bate exatamente com o número citado no
título do slide do material do DIEESE ("Com taxa de 8,9%, sindicalização cresce pela
primeira vez desde 2012"), confirmando que é a fonte correta.

NOTA SOBRE A SÉRIE: não é anual contínua — o suplemento não foi levantado em 2020 e
2021 (provável disrupção da pandemia no desenho da pesquisa). Série real: 2012-2019,
hiato, 2022-2024. Nível territorial disponível: apenas Brasil e Grandes Regiões (sem
UF/município).

===============================================================================
COMO FUNCIONA A API DO SIDRA (vale para todos os scripts "..._sidra.py")
===============================================================================
O SIDRA é o sistema de tabelas do IBGE. Toda consulta pela API segue o mesmo
formato de URL, com "segmentos" separados por barra — cada um filtra uma
dimensão da tabela:

    https://apisidra.ibge.gov.br/values/t/{tabela}/n1/{territorio}/v/{variavel}/p/{periodo}/c888/{classificacao}

  - `t/8676`     → número da tabela no SIDRA (cada tabela do IBGE tem um ID
                   fixo; 8676 é "Taxa de sindicalização", resultado do módulo
                   anual "Características Adicionais do Mercado de Trabalho"
                   da PNAD Contínua). Para achar o número de outra tabela,
                   procure no site sidra.ibge.gov.br e copie da URL da tabela.
  - `n1/all`     → nível territorial (n1 = Brasil) e "all" = todos os
                   territórios desse nível (aqui só existe 1: o próprio
                   Brasil). Esta tabela também está disponível por Grande
                   Região (n2) — não há recorte por UF/município.
  - `v/12535`    → qual variável da tabela trazer. Diferente de outros
                   scripts deste bloco, aqui não usamos "all": pedimos
                   diretamente a variável 12535, que é a "Taxa de
                   sindicalização" — a tabela tem outras variáveis (como o
                   número absoluto de sindicalizados) que não interessam a
                   este indicador.
  - `p/all`      → quais períodos trazer ("all" = a série completa
                   disponível, incluindo o hiato de 2020/2021 — ver nota
                   acima).
  - `c888/all`   → um filtro de classificação específico desta tabela (aqui:
                   `c888` é "Grupamentos de atividades no trabalho principal",
                   com 11 categorias; "all" traz todas). Cada tabela do SIDRA
                   tem suas próprias classificações — o número do código
                   muda de tabela para tabela.

A resposta é sempre uma lista de objetos JSON, onde o PRIMEIRO item é o
cabeçalho (nomes das colunas) e os demais são os valores — por isso este
script não faz nenhuma limpeza: grava a lista inteira exatamente como veio.

===============================================================================
O QUE ESTE SCRIPT FAZ, PASSO A PASSO
===============================================================================
1. Monta a URL da consulta (constante `URL`, ver acima).
2. Busca os dados na API (`_buscar_dados`).
3. Salva a resposta, sem alterar nada, em `data/raw/ibge_sidra/` com um nome
   de arquivo que inclui a tabela e o instante da coleta (`_salvar_raw`).
4. Registra a coleta no Supabase — arquivo no Storage + linha em
   `raw_ingestoes` (`registrar_coleta`, importado de `pipelines/supabase_raw.py`).

O QUE A TABELA 8676 MEDE: a proporção de pessoas ocupadas de 14 anos ou mais
que são sindicalizadas, por grupamento de atividade no trabalho principal.
Ao contrário dos outros três scripts deste bloco — que vêm da PNAD Contínua
TRIMESTRAL, levantada todo trimestre — este indicador vem de um suplemento
ANUAL e descontínuo da mesma pesquisa (módulo "Características Adicionais do
Mercado de Trabalho"), por isso a série tem um hiato em 2020 e 2021 e não
deve ser tratada como uma série trimestral comum.

Este script NÃO transforma o dado — grava a resposta bruta da API exatamente
como recebida, respeitando o princípio de que a camada RAW nunca deve ser
editada manualmente ou pré-processada (ver CLAUDE.md, seção DADOS). Calcular
variações, preencher o hiato ou qualquer outra conta é trabalho da camada
STAGING, feito depois, a partir do arquivo que este script grava — nunca aqui.
"""

import json
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from supabase_raw import registrar_coleta

# Tabela 8676 do SIDRA: "Taxa de sindicalização" — PNAD Contínua anual (módulo
# "Características Adicionais do Mercado de Trabalho"). Variável 12535 = "Taxa
# de sindicalização"; classificação c888 = "Grupamentos de atividades no
# trabalho principal".
URL = "https://apisidra.ibge.gov.br/values/t/8676/n1/all/v/12535/p/all/c888/all"

DESTINO = Path(__file__).resolve().parents[3] / "data" / "raw" / "ibge_sidra"


# ------------------------------------------------------------------------
# PASSO 1 — buscar os dados na API
# ------------------------------------------------------------------------
def _buscar_dados() -> list:
    """Faz a requisição HTTP e devolve o JSON já decodificado (uma lista de
    dicionários — o primeiro é o cabeçalho, os demais são os valores).

    `timeout=60` existe porque a API do SIDRA pode demorar alguns segundos
    quando a tabela pedida tem muitos dados ("p/all" traz a série inteira,
    incluindo o hiato de 2020/2021) — sem timeout, um problema de rede
    deixaria o script parado indefinidamente em vez de falhar de forma
    visível.
    """
    with urllib.request.urlopen(URL, timeout=60) as resposta:
        return json.loads(resposta.read().decode("utf-8"))


# ------------------------------------------------------------------------
# PASSO 2 — salvar a resposta bruta em disco
# ------------------------------------------------------------------------
def _salvar_raw(dados: list) -> Path:
    """Grava `dados` como JSON, formatado (indent=2) só para ficar legível
    para humanos que forem inspecionar o arquivo — isso não é uma
    transformação do dado, é só formatação de texto.

    O nome do arquivo leva um timestamp UTC (`_%Y%m%dT%H%M%SZ`) porque cada
    execução deste script é uma nova "fotografia" da série: o IBGE pode
    revisar dados publicados, e queremos poder comparar o que a API
    respondia em momentos diferentes — por isso nunca sobrescrevemos a
    coleta anterior.
    """
    DESTINO.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    arquivo = DESTINO / f"sindicalizacao_sidra_8676_{timestamp}.json"
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
