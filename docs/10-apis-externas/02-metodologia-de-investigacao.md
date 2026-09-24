# Metodologia de investigação de fontes

## A regra mais importante do projeto

`CLAUDE.md`, seção PRINCÍPIOS, é direto: **não invente dado, não invente
fonte, não invente API ou endpoint**. Isso não é um detalhe de estilo — é a
diferença entre uma plataforma confiável e uma que espalha número errado. Na
prática, significa:

- Nunca escrever uma URL "que provavelmente funciona" sem testá-la de
  verdade.
- Nunca citar um valor que apareceu só num resumo de busca — só o que foi
  lido diretamente da fonte primária.
- Quando uma ferramenta de busca ou um resumo de terceiro menciona um
  número, tratar como **pista**, não como dado, até confirmar na fonte
  original.

Este projeto já teve dois episódios reais de "alucinação de ferramenta de
busca" — um número de greves ("EP 114") e um valor de piso salarial — que
apareceram em resumos de busca mas não existiam na fonte real (a URL deu
404). Os dois ficaram registrados em `docs/04-fontes/dieese-publicacoes.md`
exatamente para não serem reintroduzidos por engano numa rodada futura. A
lição: **sempre teste a URL final você mesmo antes de escrever um número em
qualquer documento**.

## A escala de classificação (A a E)

Toda fonte investigada neste projeto recebe uma classificação, definida em
`agents/fontes-dados.md`:

| Classificação | O que significa | Exemplo real |
|---|---|---|
| **A** | API direta — chamada HTTP simples, resposta estruturada (JSON/XML/CSV) | SIDRA, SGS do BCB, SICONFI |
| **B** | Download estruturado — não é uma API de consulta, mas um arquivo (CSV, PDF com texto extraível) num endereço previsível | Comex Stat (CSV), boletins do DIEESE (PDF com `pdftotext`) |
| **C** | Microdados — dado bruto, não agregado, que ainda precisa de processamento próprio para virar indicador | Novo CAGED (FTP), RAIS |
| **D** | Exige investigação adicional — a fonte existe mas algo não foi confirmado (sintaxe, escopo, ambiguidade) | FMI além do WEO (sintaxe SDMX não resolvida nesta rodada) |
| **E** | Processo manual/específico — não há caminho de automação, ou a fonte é um processo interno de outra instituição | INDATEND (planilha interna do DIEESE, distribuída por e-mail) |

Uma fonte pode subir ou descer de classificação conforme se aprende mais
sobre ela — isso já aconteceu várias vezes neste projeto. O caso mais visível:
os boletins de ICT e Balanço das Greves do DIEESE foram classificados E
("PDF-imagem, sem texto extraível") numa primeira investigação, e depois
corrigidos para B quando um teste técnico direto (`pdftotext -layout -enc UTF-8`)
provou que o texto saía limpo — a ferramenta de leitura usada na primeira
tentativa é que falhava silenciosamente, não a fonte. **A lição: um "não dá"
inicial vale a pena ser testado de novo com uma ferramenta diferente antes de
aceitar como definitivo.**

## O processo, passo a passo

1. **Identificar o candidato**: uma instituição, um arquivo, uma menção no
   material do DIEESE ("Fonte: X") — qualquer pista de onde o dado pode vir.
2. **Testar de verdade**: uma chamada HTTP real (`curl`, `urllib`, ou uma
   biblioteca de conveniência para prototipar rápido — ver
   `docs/04-fontes/bibliotecas-python-dados-socioeconomicos-2026-09.md`).
   Nunca presumir que uma URL "deveria" funcionar.
3. **Ler a resposta real**: confirmar que o dado que voltou é o que você
   esperava (nome do campo, unidade, período) — não só que o HTTP retornou
   200.
4. **Classificar** (A-E) e documentar em `docs/04-fontes/`, seguindo o
   formato já usado (uma ficha por instituição/lote, com URL exata, código
   HTTP, trecho real de resposta).
5. **Se for construir o motor**: seguir o padrão descrito em
   [`03-anatomia-de-um-motor.md`](03-anatomia-de-um-motor.md).

## Validação cruzada — o padrão mais rigoroso deste projeto

Quando existe uma fonte de referência independente (ex. a planilha interna
que o DIEESE já usa), o teste mais forte não é só "a API respondeu" — é
comparar o valor da API/boletim público com o valor da fonte de referência,
número a número. Foi assim que a reclassificação do ICT e do Balanço das
Greves foi confirmada nesta sessão: não bastou o `pdftotext` funcionar, foi
preciso abrir a apresentação interna do DIEESE e conferir que os valores
batiam exatamente (ex.: 880 greves em 2024 nos dois lados; reajustes
salariais com o mesmo percentual até a casa decimal). Sempre que houver uma
fonte de referência disponível, use-a — é a diferença entre "parece certo" e
"está confirmado".

## Próximo passo

[`03-anatomia-de-um-motor.md`](03-anatomia-de-um-motor.md) — depois de
confirmar que a fonte é real e classificá-la, como transformar isso num
script de coleta.
