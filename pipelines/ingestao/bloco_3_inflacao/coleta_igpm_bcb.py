"""Coleta bruta do IGP-M (Índice Geral de Preços — Mercado, calculado pela FGV/IBRE)
via API pública do BCB/SGS.

Piloto técnico controlado — ver docs/08-decisoes-adr/0002-expansao-piloto-por-blocos.md
Fonte confirmada em: docs/04-fontes/fgv-indatend.md — Lote 06b.

===============================================================================
COMO FUNCIONA A API DO BCB/SGS (vale para todos os scripts "..._bcb.py" que
usam o Sistema Gerenciador de Séries Temporais — SGS)
===============================================================================
O SGS é o sistema de séries temporais do Banco Central. Cada série (um
indicador específico, como "câmbio venda mensal" ou "IGP-M") tem um CÓDIGO
NUMÉRICO fixo, e a URL de consulta é sempre:

    https://api.bcb.gov.br/dados/serie/bcdata.sgs.{codigo}/dados?formato=json

Para achar o código de uma série nova, procure no site do BCB
(www3.bcb.gov.br/sgspub) pelo nome do indicador — a busca mostra o código.
A resposta é uma lista de objetos `{"data": "DD/MM/AAAA", "valor": "..."}`,
um por observação, sempre em ordem cronológica — sem cabeçalho (diferente do
SIDRA, que tem um item de cabeçalho no início da lista).

===============================================================================
POR QUE O IGP-M É COLETADO DO BCB, E NÃO DA FGV — a fonte que o calcula
===============================================================================
Quem calcula e publica oficialmente o IGP-M é a FGV/IBRE (Instituto Brasileiro
de Economia da Fundação Getulio Vargas) — não o Banco Central. Mas o Portal
FGV/IBRE não oferece API pública nem download gratuito estruturado: o acesso
à série é via contrato/assinatura paga, confirmado na pesquisa de fontes
deste projeto (não é uma limitação técnica passageira, é o modelo de
distribuição da FGV para esse dado).

Como o próprio Banco Central REPLICA oficialmente a série do IGP-M dentro do
seu sistema SGS (código 189), este script usa essa rota alternativa, gratuita
e pública, em vez da fonte original. O dado é o mesmo — o BCB não recalcula
nem reinterpreta o índice, apenas o disponibiliza também no seu sistema —,
muda só o canal de acesso. Essa mesma lógica (buscar num sistema que replica
oficialmente um dado cuja fonte primária não tem acesso público) pode valer
para outros indicadores cujo produtor original não ofereça API própria: vale
sempre perguntar se algum órgão público já replica o dado antes de descartar
o indicador por falta de fonte automatizável.

Esta rota cobre APENAS o IGP-M — não os demais índices da FGV eventualmente
citados pelo material do DIEESE (ex. IPC-Fi, IPC-S), que não têm
correspondente confirmado no SGS.

===============================================================================
O QUE ESTE SCRIPT FAZ, PASSO A PASSO
===============================================================================
1. Monta a URL da consulta (constante `URL`, ver acima).
2. Busca os dados na API (`_buscar_dados`).
3. Salva a resposta, sem alterar nada, em `data/raw/bcb_sgs/` com um nome de
   arquivo que inclui o código da série e o instante da coleta (`_salvar_raw`).
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

# Série SGS 189: "IGP-M - Índice geral de preços do mercado", replicada oficialmente
# pelo BCB a partir do dado calculado pela FGV/IBRE. Ver seção acima sobre por que
# a coleta é feita por esta rota alternativa, e não diretamente no Portal FGV.
URL = "https://api.bcb.gov.br/dados/serie/bcdata.sgs.189/dados?formato=json"

DESTINO = Path(__file__).resolve().parents[3] / "data" / "raw" / "bcb_sgs"


# ------------------------------------------------------------------------
# PASSO 1 — buscar os dados na API
# ------------------------------------------------------------------------
def _buscar_dados() -> list:
    """Faz a requisição HTTP e devolve o JSON já decodificado (uma lista de
    dicionários `{"data": ..., "valor": ...}`). `timeout=60` evita que o
    script fique parado indefinidamente se a API do BCB não responder —
    nesse caso ele falha de forma visível (exceção), em vez de travar
    silenciosamente.
    """
    with urllib.request.urlopen(URL, timeout=60) as resposta:
        return json.loads(resposta.read().decode("utf-8"))


# ------------------------------------------------------------------------
# PASSO 2 — salvar a resposta bruta em disco
# ------------------------------------------------------------------------
def _salvar_raw(dados: list) -> Path:
    """Grava `dados` como JSON formatado (indent=2), só para leitura humana —
    não é transformação de dado. O nome do arquivo leva um timestamp UTC
    (`_%Y%m%dT%H%M%SZ`) porque cada execução deste script é uma nova
    "fotografia" da série: o valor publicado pode ser revisto, e queremos
    poder comparar o que a API respondia em momentos diferentes — por isso
    nunca sobrescrevemos a coleta anterior.
    """
    DESTINO.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    arquivo = DESTINO / f"igpm_sgs_189_{timestamp}.json"
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
