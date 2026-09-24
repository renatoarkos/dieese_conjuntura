# APIs externas — referência técnica e trilha de aprendizado

Esta pasta reúne, num só lugar, tudo que é preciso saber para **investigar uma
fonte de dados nova, testá-la de verdade e construir um motor de coleta** no
padrão já usado por este projeto — do conceito mais básico (o que é uma API)
até um exercício guiado, construindo um motor do zero.

Não repete o que já está em `docs/04-fontes/` (cada ficha de fonte continua
lá, é o lugar certo para "qual URL, qual campo, qual valor real testado").
Esta pasta ensina o **método**: como chegar a essas fichas, e como usá-las
para escrever um script.

## Trilha de leitura

1. **[`01-fundamentos-de-apis.md`](01-fundamentos-de-apis.md)** — o que é uma
   API, os formatos e protocolos que este projeto já usa na prática (REST,
   JSON, SDMX, OData), autenticação, limites de uso. Do zero, com exemplos
   reais tirados dos motores já construídos.
2. **[`02-metodologia-de-investigacao.md`](02-metodologia-de-investigacao.md)**
   — como este projeto decide se uma fonte é confiável e automatizável, a
   escala de classificação A-E, e a regra mais importante do projeto: nunca
   inventar dado, fonte ou número.
3. **[`03-anatomia-de-um-motor.md`](03-anatomia-de-um-motor.md)** — a
   estrutura que todo script de coleta deste projeto segue, explicada
   passo a passo, com um motor real comentado linha a linha.
4. **[`04-mapa-de-fontes.md`](04-mapa-de-fontes.md)** — índice de tudo que já
   foi investigado (dentro e fora do catálogo atual): instituições
   brasileiras, organismos internacionais, bibliotecas Python de apoio —
   cada uma com link direto para a ficha completa em `docs/04-fontes/`.
5. **[`05-exercicio-guiado.md`](05-exercicio-guiado.md)** — um exercício
   prático completo: escolher uma fonte já confirmada mas sem motor
   construído, e escrever o script do zero, seguindo o mesmo processo usado
   em todos os outros.

## Como usar esta pasta

- **Se você nunca mexeu com API antes**: comece pelo documento 1, na ordem.
- **Se você já sabe o que é uma API, mas é novo neste projeto**: vá direto
  para o 2 (a regra de nunca inventar dado é a mais importante deste
  projeto) e o 3 (o padrão de código).
- **Se você já entende o padrão e só quer achar uma fonte para um indicador
  novo**: vá direto para o 4.
- **Se você quer praticar construindo um motor de verdade**: vá para o 5.
