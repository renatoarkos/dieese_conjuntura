# Bibliotecas Python para dados de mercado/socioeconômicos (rodada de expansão, set/2026)

**Natureza deste documento**: em vez de uma instituição, aqui o "candidato" é uma **biblioteca** — um pacote Python que embrulha o acesso a uma ou mais fontes de dados, geralmente devolvendo o resultado já pronto como `pandas.DataFrame`. Testadas de verdade (`pip install` + chamada real) nesta sessão, 2026-09-23.

**Por que isso importa para o piloto de ingestão**: o projeto usa stdlib puro por padrão (ADR 0001) e só abre exceção para dependência externa quando ela resolve algo que a stdlib genuinamente não cobre bem (ex. `curl` para uma cadeia de certificado TLS quebrada, `cryptography` para assinatura RSA). As bibliotecas abaixo são **atalhos de conveniência**, não pré-requisito — todo dado que elas trazem também dá para buscar com `urllib` puro, do jeito que os outros scripts deste piloto já fazem. Servem para: (a) prototipagem rápida ao investigar uma fonte nova, (b) ensino (mostrar em uma linha o que o `urllib` faz em vinte), (c) um caso de uso muito específico onde a lib resolve algo difícil de replicar à mão (ex. assinatura de token do Yahoo Finance).

---

## Síntese

| Biblioteca | O que cobre | Status do teste | Observação |
|---|---|---|---|
| `yfinance` | Yahoo Finance — ações, índices, câmbio, commodities, futuros | ✅ Funciona, dado real | Não é API oficial de instituição — endpoints não documentados, sem contrato de estabilidade |
| `python-bcb` | Banco Central do Brasil — SGS, Focus, e outros sistemas do BCB | ✅ Funciona, dado real | Import é `bcb`, não `python_bcb`. Cobre o que os scripts deste projeto já fazem via `urllib`, mais conveniente para exploração |
| `sidrapy` | IBGE/SIDRA | ✅ Funciona, dado real | Devolve `pandas.DataFrame` já parseado, mesma API que os scripts deste projeto chamam via `urllib` |
| `ipeadatapy` | IPEADATA | ✅ Funciona, dado real | Complementa `docs/04-fontes/outras-instituicoes-2026-09.md` (seção IPEADATA) |
| `deflatebr` | Deflacionamento de valores nominais em Reais (usa IPEADATA por baixo) | ⚠️ Quebrada nesta versão/ambiente | Bug real de incompatibilidade com Python 3.12/pandas atual — não usar sem corrigir/trocar de versão |
| `pandasdmx` | SDMX genérico (IMF, ECB, Eurostat, OCDE, ILO...) | ⚠️ Quebrada nesta versão/ambiente | Incompatibilidade Python 3.12 + pydantic v1 (erro em `ForwardRef._evaluate`) |
| `sdmx1` | SDMX genérico — sucessora ativamente mantida do `pandasdmx` | ✅ Instala e conecta | Recomendada no lugar do `pandasdmx` para os organismos SDMX de `docs/04-fontes/outras-instituicoes-mundiais-2026-09.md` |

---

## `yfinance` — Yahoo Finance

```python
import yfinance as yf
ticker = yf.Ticker("^BVSP")       # Ibovespa
hist = ticker.history(period="5d")
print(hist[["Close"]])
```

Testado com `^BVSP` (Ibovespa), `BRL=X` (Dólar/Real), `ZS=F` (soja, futuros CBOT) e `CL=F` (petróleo WTI) — todos retornaram preços reais e atuais. **Não é API oficial** — é uma biblioteca que usa endpoints não documentados do Yahoo (pode mudar/quebrar sem aviso prévio). Útil para mercado em tempo real (índices, câmbio, commodities agrícolas/energéticas que afetam a economia brasileira) onde não há alternativa oficial tão prática. Se usada em produção, precisa de tratamento de erro robusto e um plano B (a própria fonte pode ficar indisponível).

## `python-bcb` — Banco Central do Brasil

```python
from bcb import sgs
df = sgs.get({"selic": 432}, last=5)  # mesma serie SGS 432 ja usada em coleta_selic_bcb.py
print(df)
```

Testado com a série 432 (Selic) — retornou valores reais. Cobre exatamente o que `pipelines/ingestao/bloco_2_monetario_credito/coleta_selic_bcb.py` já faz com `urllib` puro; útil para prototipar rapidamente uma série BCB nova antes de escrever o script de coleta definitivo (que continua em `urllib`, por `ADR 0001`).

## `sidrapy` — IBGE/SIDRA

```python
import sidrapy
df = sidrapy.get_table(
    table_code="4093", territorial_level="1", ibge_territorial_code="all",
    period="last%205", variable="all",
)
```

Testado com a Tabela 4093 (desocupação) — retornou `DataFrame` real com as mesmas colunas (`D1C`, `D1N`, `D2C`...) que os scripts deste projeto já recebem em JSON bruto via `urllib`. Mesma relação com o projeto que o `python-bcb`: atalho de prototipagem, não substituto dos scripts de produção.

## `ipeadatapy` — IPEADATA

```python
import ipeadatapy as ip
series = ip.list_series(name="PIB")     # busca series pelo nome
dados = ip.timeseries("BM12_PIB12")     # baixa a serie completa
```

Testado com a série `BM12_PIB12` — retornou valores mensais reais em R$. Complementa a investigação institucional já registrada em `docs/04-fontes/outras-instituicoes-2026-09.md` (a API OData4 do IPEADATA, chamada via `urllib`) — esta biblioteca é só uma camada de conveniência sobre a mesma API.

## `deflatebr` — deflacionamento de valores nominais

**Não funcionou nesta sessão.** Dois bugs reais encontrados em sequência ao testar:
1. A assinatura documentada aceita datas como string, mas o código internamente exige `datetime.datetime` (não `datetime.date`) — a docstring está desatualizada.
2. Mesmo corrigindo isso, um erro interno de indexação do `pandas` (`KeyError` dentro de um `.apply()` com lambda por posição) quebra antes de devolver o resultado — parece incompatibilidade com uma versão mais nova do `pandas` do que a testada pelos mantenedores da lib.

**Relevância que motivou o teste**: essa biblioteca resolveria exatamente o problema em aberto do indicador "Rendimento médio real" (possível dupla deflação, QF04, ver `docs/04-fontes/ibge-sidra.md`) — mas, quebrada como está, não é recomendável depender dela agora. Se o projeto precisar de deflacionamento automatizado no futuro, a alternativa seria implementar a fórmula diretamente (é simples: `valor_real = valor_nominal * indice_base / indice_periodo`), usando a série de INPC/IPCA que o projeto já coleta, em vez de uma dependência externa quebrada.

## `pandasdmx` (não usar) → `sdmx1` (usar no lugar)

`pandasdmx` — a biblioteca mais conhecida historicamente para SDMX em Python — **não importa nesta versão do Python** (3.12): quebra dentro do `pydantic` com `TypeError: ForwardRef._evaluate() missing 1 required keyword-only argument`, um problema de compatibilidade entre versões antigas de `pydantic`/`pandasdmx` e mudanças na stdlib do Python 3.10+.

`sdmx1` é o fork/sucessor ativamente mantido do mesmo projeto, com o mesmo propósito (cliente genérico para qualquer fonte que fale o protocolo SDMX — IMF, ECB, Eurostat, OCDE, ILO, BIS...). Testado: conecta normalmente (`sdmx.Client("ILO")`). Não foi testado até uma consulta de dado completa nesta rodada (a investigação institucional em `docs/04-fontes/outras-instituicoes-mundiais-2026-09.md` já cobriu esses mesmos organismos via `curl` puro) — mas é a opção recomendada caso o projeto decida usar uma biblioteca de conveniência para os organismos SDMX no futuro, em vez de montar a URL manualmente.

---

## Recomendação de uso no projeto

Nenhuma destas bibliotecas deveria substituir os scripts de produção já escritos (que seguem `ADR 0001`, stdlib-only, por reprodutibilidade e ausência de dependência frágil). O uso recomendado é:
- **Prototipagem/exploração**: ao investigar uma fonte nova, usar a lib de conveniência (`sidrapy`, `python-bcb`, `ipeadatapy`) para confirmar rapidamente se um dado existe e como ele se parece, antes de escrever o script definitivo em `urllib` puro.
- **Ensino**: mostrar a mesma chamada em uma linha (via lib) e em `urllib` puro (como o projeto realmente implementa) ajuda a explicar o que está acontecendo por baixo do capô — é basicamente o que a seção "Anatomia de um script de coleta" de `pipelines/README.md` já ensina, só que a lib esconde essa etapa.
- **Casos onde a lib resolve algo genuinamente difícil**: `yfinance` (evita reimplementar o protocolo do Yahoo) e, se `sdmx1` se confirmar estável, o protocolo SDMX (que é mais complexo de montar à mão que uma URL REST simples).
