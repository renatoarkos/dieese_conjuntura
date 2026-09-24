# Exercício guiado — construindo um motor do zero

Este exercício usa uma fonte já investigada e confirmada, mas que ainda não
tem motor de coleta: o **Banco Mundial** (World Bank Open Data), documentado
em `docs/04-fontes/outras-instituicoes-mundiais-2026-09.md`. O objetivo é
praticar o processo completo — testar, entender a resposta, escrever o
script no padrão do projeto — com uma fonte real, não um exemplo fictício.

Indicador escolhido: **crescimento real do PIB (% a.a.)**, código
`NY.GDP.MKTP.KD.ZG`, para o Brasil — já testado e documentado, então este
exercício foca em construir o script, não em descobrir se a fonte existe.

## Passo 1 — testar a chamada manualmente

Antes de escrever qualquer script, confirme a chamada você mesmo:

```bash
curl "https://api.worldbank.org/v2/country/BRA/indicator/NY.GDP.MKTP.KD.ZG?format=json&per_page=20"
```

Repare na estrutura da resposta: é uma **lista de duas posições** — a
primeira é metadado de paginação (`page`, `pages`, `total`...), a segunda é a
lista de valores de verdade. Isso é diferente do padrão do SIDRA (onde o
primeiro item da lista é o cabeçalho) — cada fonte tem seu próprio formato,
por isso este passo nunca pode ser pulado.

```python
import json, urllib.request

url = "https://api.worldbank.org/v2/country/BRA/indicator/NY.GDP.MKTP.KD.ZG?format=json&per_page=20"
with urllib.request.urlopen(url, timeout=30) as r:
    dados = json.loads(r.read().decode("utf-8"))

print(type(dados), len(dados))       # <class 'list'> 2
print(dados[0])                      # metadado de paginação
print(dados[1][0])                   # primeiro valor de verdade
```

## Passo 2 — decidir o que preservar

Pergunta: o script deve gravar a lista inteira (`dados`, incluindo o
metadado de paginação) ou só a parte de valores (`dados[1]`)?

Resposta, pela regra da camada RAW (`CLAUDE.md`, seção DADOS): **a lista
inteira, sem tirar nada** — o script não decide o que é "importante" dentro
da resposta, só grava exatamente o que voltou. Separar metadado de valor é
trabalho de STAGING.

## Passo 3 — escrever o script

Tente escrever você mesmo, seguindo a estrutura de
[`03-anatomia-de-um-motor.md`](03-anatomia-de-um-motor.md), antes de olhar a
referência abaixo. Onde salvar: `data/raw/worldbank/`. Nome de arquivo
sugerido: inclua o código do indicador e um timestamp, como os outros
scripts já fazem.

<details>
<summary>Referência — clique para ver depois de tentar</summary>

```python
"""Coleta bruta do crescimento real do PIB (%a.a.) do Brasil via API pública
do Banco Mundial (World Bank Open Data).

Fonte confirmada em: docs/04-fontes/outras-instituicoes-mundiais-2026-09.md

Este script NÃO transforma o dado.
"""

import json
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from supabase_raw import registrar_coleta

# Indicador NY.GDP.MKTP.KD.ZG = crescimento real do PIB (%a.a.), país BRA.
URL = "https://api.worldbank.org/v2/country/BRA/indicator/NY.GDP.MKTP.KD.ZG?format=json&per_page=100"

DESTINO = Path(__file__).resolve().parents[3] / "data" / "raw" / "worldbank"


def _buscar_dados() -> list:
    with urllib.request.urlopen(URL, timeout=30) as resposta:
        return json.loads(resposta.read().decode("utf-8"))


def _salvar_raw(dados: list) -> Path:
    DESTINO.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    arquivo = DESTINO / f"pib_crescimento_bra_worldbank_{timestamp}.json"
    arquivo.write_text(json.dumps(dados, ensure_ascii=False, indent=2), encoding="utf-8")
    return arquivo


def coletar() -> Path:
    dados = _buscar_dados()
    return _salvar_raw(dados)


if __name__ == "__main__":
    caminho = coletar()
    print(f"Coleta concluída: {caminho}")
    registrar_coleta(fonte=DESTINO.name, arquivo=caminho, script=__file__)
```

</details>

## Passo 4 — testar de ponta a ponta

```bash
python3 -m py_compile caminho/do/seu_script.py   # confere sintaxe
python3 caminho/do/seu_script.py                  # roda de verdade
```

Confira: o arquivo foi gravado em `data/raw/worldbank/`? O conteúdo bate com
o que você viu no Passo 1? Se as credenciais do Supabase estiverem
configuradas em `.env`, confirme também que uma linha nova apareceu na
tabela `raw_ingestoes` (mesma consulta usada em toda esta documentação:
`SELECT * FROM raw_ingestoes WHERE fonte = 'worldbank' ORDER BY id DESC`).

## O que este exercício não cobre (de propósito)

Este script coleta só um indicador, um país. O Banco Mundial tem milhares de
indicadores e ~200 países — decidir quais outros indicadores/países valem a
pena automatizar é uma decisão de escopo do projeto, não deste exercício.
Se for adiante: siga o mesmo padrão de "vários candidatos, mesma função"
já usado em `coleta_cambio_bcb.py` (um dicionário de indicadores/países em
vez de uma URL fixa).
