# Anatomia de um motor de coleta

Todo script de coleta deste projeto (`pipelines/ingestao/`) segue a mesma
forma. Este documento explica cada parte, linha por linha, usando um motor
real e simples como exemplo:
`pipelines/ingestao/bloco_1_macroeconomia/coleta_taxa_investimento_sidra.py`.
Depois de entender este, qualquer um dos outros 30 scripts do projeto se lê
com o mesmo roteiro.

## Visão geral das 5 partes

```
1. Docstring do módulo      → o quê, de onde, por quê, como (texto)
2. Constantes no topo        → URL e DESTINO
3. Funções pequenas          → uma por etapa (_buscar_dados, _salvar_raw...)
4. coletar()                 → orquestra as funções, nesta ordem
5. if __name__ == "__main__" → roda coletar() e registra no Supabase
```

## Parte 1 — a docstring

```python
"""Coleta bruta da taxa de investimento (...) via API pública do SIDRA/IBGE.

Piloto técnico controlado — ver docs/08-decisoes-adr/0002-...
Fonte confirmada em: docs/05-indicadores/CATALOGO_MESTRE_INDICADORES.md (...)

===============================================================================
O QUE ESTE INDICADOR MEDE, E COMO FOI ENCONTRADO
===============================================================================
A taxa de investimento mede (...)

===============================================================================
COMO FUNCIONA A API DO SIDRA (vale para todos os scripts "..._sidra.py")
===============================================================================
Ver `coleta_pib_sidra.py` para a explicação completa (...)

===============================================================================
O QUE ESTE SCRIPT FAZ, PASSO A PASSO
===============================================================================
1. Monta a URL (...)
2. Busca os dados (...)
3. Salva a resposta (...)
4. Registra a coleta (...)
"""
```

Isso não é decoração — é a primeira coisa que qualquer pessoa lê antes do
código, e responde às perguntas que mais importam: **o que é este dado**,
**de onde ele vem e por que confiamos nessa fonte**, e **como o protocolo
funciona em geral** (não só para esta tabela — para que, ao encontrar uma
tabela nova do mesmo tipo, a pessoa já saiba montar a URL sozinha).

## Parte 2 — constantes

```python
URL = "https://apisidra.ibge.gov.br/values/t/6727/n1/all/v/all/p/all"
DESTINO = Path(__file__).resolve().parents[3] / "data" / "raw" / "ibge_sidra"
```

A URL fica isolada numa constante, com um comentário explicando o que o
número da tabela significa. `DESTINO` é sempre calculado a partir de
`__file__` (a localização do próprio script) subindo 3 pastas até a raiz do
repositório, depois entrando em `data/raw/<nome-da-fonte>/` — assim o script
funciona não importa de onde for chamado.

## Parte 3 — funções pequenas, uma por etapa

```python
def _buscar_dados() -> list:
    with urllib.request.urlopen(URL, timeout=60) as resposta:
        return json.loads(resposta.read().decode("utf-8"))


def _salvar_raw(dados: list) -> Path:
    DESTINO.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    arquivo = DESTINO / f"taxa_investimento_sidra_6727_{timestamp}.json"
    arquivo.write_text(json.dumps(dados, ensure_ascii=False, indent=2), encoding="utf-8")
    return arquivo
```

Cada função tem nome de verbo, faz uma coisa só, e tem docstring própria
quando algo não é óbvio (por que um timeout de 60s, por que o timestamp no
nome do arquivo). O prefixo `_` (`_buscar_dados`, não `buscar_dados`) sinaliza
que são funções internas do módulo — quem for usar este script de fora só
precisa conhecer `coletar()`.

**Por que salvar sem transformar nada**: a camada RAW (`CLAUDE.md`, seção
DADOS) existe para preservar exatamente o que a fonte respondeu, incluindo
erros de digitação, formatos estranhos, tudo — qualquer limpeza ou cálculo é
trabalho de uma camada posterior (STAGING), nunca do motor de coleta.
`json.dumps(..., indent=2)` aqui é só formatação para leitura humana, não é
uma transformação do dado em si.

## Parte 4 — `coletar()`, a orquestração

```python
def coletar() -> Path:
    dados = _buscar_dados()
    return _salvar_raw(dados)
```

Só chama as etapas na ordem certa. Não faz trabalho próprio — se alguém
quiser entender o fluxo completo do script, olha aqui primeiro.

## Parte 5 — o bloco de execução

```python
if __name__ == "__main__":
    caminho = coletar()
    print(f"Coleta concluída: {caminho}")
    registrar_coleta(fonte=DESTINO.name, arquivo=caminho, script=__file__)
```

Roda `coletar()`, imprime o resultado (para quem estiver rodando manualmente
ver o que aconteceu) e chama `registrar_coleta()` — a função compartilhada de
`pipelines/supabase_raw.py` que envia uma cópia do arquivo ao Supabase
Storage e registra a execução na tabela `raw_ingestoes`. Essa parte é
idêntica em todos os 31 scripts do projeto; nunca precisa ser reescrita.

## Variações desse padrão que você vai encontrar

- **Mais de uma série por vez** (`coleta_cambio_bcb.py`,
  `coleta_commodities_bcb.py`): em vez de uma `URL`, um dicionário
  `SERIES = {código: url}`, e `coletar()` faz um laço chamando
  `_buscar_dados`/`_salvar_raw` para cada uma.
- **Descoberta de edição/URL que muda com o tempo**
  (`coleta_negociacao_coletiva_dieese.py`, `coleta_ict_dieese.py`,
  `coleta_greves_dieese.py`, `coleta_uci_cni.py`): uma função extra antes de
  `_buscar_dados`, que decide qual URL tentar (por número sequencial, por
  regex sobre uma página HTML, ou tentando padrões de nome alternativos).
- **Fonte que não é HTTP** (`coleta_caged_microdados_ftp.py`): o protocolo
  muda (FTP em vez de HTTP), mas a forma continua igual — funções pequenas
  por etapa, `coletar()` orquestrando, bloco final idêntico.
- **Dependência de terceiros por necessidade real**
  (`coleta_balanca_comercial_comexstat.py` usa `curl`;
  `pipelines/google_drive_raw.py` usa a biblioteca `cryptography`): só
  quando a biblioteca padrão do Python genuinamente não resolve algo (uma
  cadeia de certificado TLS quebrada; assinatura criptográfica RSA) — sempre
  documentado no topo do arquivo, explicando por quê.

## Próximo passo

[`04-mapa-de-fontes.md`](04-mapa-de-fontes.md) — onde procurar uma fonte já
investigada antes de começar uma nova, ou
[`05-exercicio-guiado.md`](05-exercicio-guiado.md) para praticar construindo
um motor do zero.
