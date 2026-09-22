# Comparação dos Dois Excel P1

## 1. Objetivo

Determinar a relação entre os dois arquivos Excel classificados como P1 no inventário de materiais, antes de qualquer análise econômica de conteúdo:

- `materiais/originais/Apresentação de conjuntura/Apresentação_Conjuntura_4T_2025.xlsx` (adiante, **"principal"**) — arquivo situado na pasta de trabalho corrente, ao lado da apresentação `ATR_Conjuntura_2025.12.pptx`.
- `materiais/originais/dieese/Apresentação_Conjuntura_4T_2025 (2).xlsx` (adiante, **"dieese"**) — arquivo cuja localização mudou durante este projeto (ver `research/notas/INVENTARIO_MATERIAIS.md`, seção 3), mas cujo conteúdo não foi alterado por esta equipe.

Nenhum dos dois arquivos foi alterado, movido ou sobrescrito durante esta análise. A leitura foi feita exclusivamente em modo leitura, via biblioteca `openpyxl`.

## 2. Comparação de metadados de arquivo

| Aspecto | principal | dieese |
|---|---|---|
| Caminho | `Apresentação de conjuntura/Apresentação_Conjuntura_4T_2025.xlsx` | `dieese/Apresentação_Conjuntura_4T_2025 (2).xlsx` |
| Tamanho | 457708 bytes (~0.44 MB) | 750393 bytes (~0.72 MB) |
| Hash MD5 | `a5f687a1f95f18cdcf541f6a9ab5a5b4` | `a2ed2efdac96da4a52de12059fa5ba85` |
| Nº de abas | 47 | 54 |

Os hashes MD5 são diferentes — portanto **não são duplicatas exatas** (categoria A descartada).

## 3. Metadados internos do arquivo (propriedades OOXML)

Diferentemente dos metadados do sistema de arquivos (que foram afetados pela movimentação registrada no inventário), as propriedades `docProps/core.xml` embutidas dentro de cada `.xlsx` não foram alteradas por essa movimentação e constituem evidência mais confiável sobre a origem e o histórico de edição de cada arquivo.

| Propriedade | principal | dieese |
|---|---|---|
| Criado em (`dcterms:created`) | 2015-06-05T18:19:34Z | 2015-06-05T18:19:34Z |
| Criador original (`dc:creator`) | Lucas Capelo | Lucas Capelo |
| Última modificação (`dcterms:modified`) | 2026-03-19T13:15:10Z | 2026-06-10T12:10:00Z |
| Último editor (`cp:lastModifiedBy`) | (vazio) | Ricardo Tamashiro |
| Revisão (`cp:revision`) | 3 | 0 |

**EVIDÊNCIA DIRETA**: os dois arquivos compartilham a mesma data de criação original e o mesmo criador original — indicando uma origem comum (provavelmente um modelo/planilha-base único, copiado e depois editado separadamente). A partir daí, divergem: o arquivo "dieese" foi salvo por último em data posterior (10/06/2026) e por uma pessoa diferente (Ricardo Tamashiro) da que aparece no arquivo "principal" (campo vazio, não identificado). O contador de revisão zerado em "dieese" (revision=0) é consistente com o arquivo ter sido salvo por uma versão diferente de suíte de escritório (ver Seção 4), o que pode reiniciar essa contagem.

Isso **não permite concluir com certeza qual arquivo é mais recente em termos de conteúdo útil** — apenas que o arquivo "dieese" foi salvo por último, por outra pessoa, em outro momento. A data de salvamento não implica necessariamente maior relevância analítica.

## 4. Aplicativo de origem

Ambos os arquivos foram salvos por builds do Collabora Office / LibreOffice (não Microsoft Excel nativo):

- principal: `Collabora_Office/25.04.8.1$Linux_X86_64`
- dieese: `Collabora_Office/26.04.1.4$Linux_X86_64`

Versões de build diferentes, reforçando que os arquivos foram editados em momentos/ambientes distintos.

## 5. Estrutura de abas

### 5.1 Contagem e conjuntos

- Abas em comum (mesmo nome nos dois arquivos): **43**
- Abas exclusivas do "principal": **4** — `Plan1`, `T15a`, `T15b`, `T40-43`
- Abas exclusivas do "dieese": **11** — `Planilha1`, `Protegido e desprotegido`, `T15`, `T18a`, `T27`, `T34`, `T34a`, `T41a`, `T41b`, `T4x`, `Ty`

A presença de abas exclusivas em ambos os sentidos indica que os arquivos **não são simplesmente o mesmo arquivo salvo em momentos diferentes** (o que produziria um conjunto de abas idêntico, ou um subconjunto estrito). Há divergência editorial real: abas foram criadas, removidas ou renomeadas de forma independente em cada cópia.

Chama atenção, no conjunto exclusivo de "dieese", a presença de abas com nomes que sugerem material de teste/rascunho não finalizado: `Ty`, `T4x`, `Protegido e desprotegido`, `T18a`, `T34`, `T34a`, `T41a`, `T41b`. Já o conjunto exclusivo de "principal" (`T15a`, `T15b`, `T40-43`, `Plan1`) é mais enxuto e não contém nomes com essa característica.

`Plan1` (principal) e `Planilha1` (dieese) são, muito provavelmente, a mesma aba em branco padrão criada automaticamente pelo LibreOffice/Collabora ao salvar — o nome padrão muda conforme a configuração de idioma/versão do aplicativo. Não representam conteúdo relevante em nenhum dos dois arquivos.

### 5.2 Discrepância notável: aba `T14`

Entre as abas de mesmo nome, `T14` apresenta a divergência mais significativa encontrada:

| | principal | dieese |
|---|---|---|
| Dimensões | A1:J125 | A1:N22 |
| Linhas | 125 | 22 |
| Última célula não vazia (col. A/B) | "Elaboração: DIEESE" | "Fonte: CNC" |

O conteúdo de `T14` em "dieese" (22 linhas, terminando em "Fonte: CNC") é estruturalmente diferente do conteúdo de `T14` em "principal" (125 linhas, terminando em "Elaboração: DIEESE", com fonte "SIDRA e BCB" identificada dentro da aba). Isso sugere que a mesma etiqueta de aba (`T14`) foi reutilizada para conteúdos distintos nas duas cópias — possivelmente um teste ou substituição de fonte de dados (CNC = Confederação Nacional do Comércio, um candidato possível para uma série de crédito/inadimplência) que não foi propagado (ou foi revertido) na cópia "principal". **Este ponto específico exige validação humana antes de qualquer uso analítico da aba T14 de qualquer um dos arquivos.**

> **Atualização — Rodada 2 (Validação Técnica, ver `VALIDACAO_TECNICA_P1.md`, Frente C):** a inspeção OOXML aprofundada confirmou que `T14` em "dieese" contém "Endividamento Familiar, por Faixa de Renda" (fonte CNC), e que o conteúdo de Selic/IPCA/juros real que ocupava `T14` em "principal" **não foi perdido nem é um teste** — está presente, visível, com 127 fórmulas ativas e gráfico próprio, na aba `T18a` de "dieese" (série estendida até mar/2026). A hipótese mais sustentada pela evidência é a de uma **reorganização de rótulos de aba** em um arquivo continuamente reaproveitado ao longo de sucessivos trimestres, não uma substituição de fonte de dados nem um teste abandonado. A dúvida sobre o momento exato dessa reorganização permanece em aberto (ver seção de dúvidas de `VALIDACAO_TECNICA_P1.md`).

### 5.3 Outras abas em comum: divergências menores

Abas como `T19` têm dimensões próximas entre os dois arquivos (principal: A1:AV172, 172 linhas; dieese: A1:AV178, 178 linhas), consistente com a hipótese de que "dieese" incorpora alguns períodos adicionais de dados nessa série específica, sem alteração estrutural relevante. Já a aba `T2` (PIB Mundial) também diverge em dimensões (principal: B1:M14; dieese: B1:N15) e contém, em "dieese", uma nota adicional ("*Última versão constava dados apenas de 2025-2027") ausente em "principal" — indicativo de uma atualização/nota inserida posteriormente nessa cópia.

Esta comparação foi feita em uma amostra de abas (`Sumário`, `T2`, `T14`, `T19`, `T26`, `T32a`, `T39`), não na totalidade — ver Seção 7 (Limitações).

## 6. Classificação da relação

**Classificação: C — versões diferentes do mesmo trabalho.**

Fundamentação:

- Origem comum comprovada por metadados internos (mesma data de criação, mesmo criador original).
- Divergência editorial real e bidirecional: cada cópia tem abas que a outra não tem (4 exclusivas do principal, 11 exclusivas do dieese).
- Pelo menos uma aba de mesmo nome (`T14`) contém conteúdo estruturalmente distinto entre as duas cópias.
- Modificação por pessoas e em datas diferentes, registrada nos metadados internos do próprio arquivo.

Não se trata de (A) duplicatas exatas — hashes diferentes e estrutura diferente. Não se trata de (B) praticamente equivalentes — a diferença de 7 abas e a divergência de conteúdo em T14 são materiais demais para essa categoria. Também não parece ser (D) arquivos complementares (não há indício de que um contenha uma metade do trabalho e o outro a outra metade) — antes, parecem duas ramificações de edição de uma mesma planilha-base.

> **Esta seção (7) é a conclusão provisória da Rodada 1, mantida aqui para registro histórico. Ela foi revista e substituída na Rodada 2 — ver Seção 9, abaixo, e o documento `VALIDACAO_TECNICA_P1.md` (Frente H) para a conclusão vigente, apoiada em evidência técnica direta (metadados internos, vínculos OOXML dos gráficos do `.pptx`) e não apenas em indícios indiretos.**

## 7. Qual arquivo deve ser a referência principal

Para fins desta rodada de Discovery profundo (Frentes B e C), a **aba de trabalho recomendada é a do arquivo "principal"** (`Apresentação de conjuntura/Apresentação_Conjuntura_4T_2025.xlsx`), pelos seguintes motivos:

1. Está fisicamente localizado na mesma pasta de trabalho corrente que a apresentação `ATR_Conjuntura_2025.12.pptx`, sugerindo pareamento direto com o material já priorizado.
2. Possui um conjunto de abas mais enxuto, sem nomes sugestivos de rascunho/teste (`Ty`, `T4x`, `Protegido e desprotegido`), o que é consistente com um arquivo mais próximo de uma versão "final" de referência.
3. Era o arquivo já presente na localização original de `materiais/originais/` antes do achado da pasta `dieese/` (ver `INVENTARIO_MATERIAIS.md`, seção 3).

**Ressalva importante**: o fato de "dieese" ter sido salvo por último (10/06/2026, por outra pessoa) é um contraindício que não pode ser descartado — é possível que "dieese" contenha correções ou dados mais recentes que ainda não foram incorporados ao "principal", especialmente à luz da divergência na aba T14. **Esta escolha de referência é provisória para fins de inventário estrutural (Frente B/C) e deve ser confirmada por um responsável humano do DIEESE antes de qualquer uso analítico ou operacional.**

## 8. Limitações desta comparação

- A comparação de conteúdo célula a célula não foi feita para a totalidade das 47 (principal) / 54 (dieese) abas — apenas para uma amostra de 7 abas com relevância temática (Sumário, T2, T14, T19, T26, T32a, T39), para não configurar cópia extensiva de conteúdo dos materiais originais.
- Gráficos e fórmulas não foram comparados fórmula a fórmula entre os dois arquivos; apenas contagens agregadas foram obtidas para o arquivo "principal" (ver `ANALISE_ESTRUTURAL_EXCEL_P1.md`).
- Não foi possível determinar, apenas por metadados, qual arquivo é "mais correto" ou "mais atualizado" em termos de conteúdo analítico — apenas qual foi salvo por último.

## 9. Adendo — Rodada 2 (Validação Técnica): conclusão revista

A conclusão provisória da Seção 7 (recomendar "principal" com base em localização de pasta e ausência de nomes "suspeitos") foi **substituída** por uma conclusão apoiada em evidência técnica direta, obtida na Rodada 2 e detalhada em `VALIDACAO_TECNICA_P1.md` (Frentes A e H):

- Os metadados internos (`docProps/core.xml`) confirmam que os dois arquivos compartilham exatamente o mesmo autor original e a mesma data/hora de criação (2015-06-05T18:19:34Z) — são o **mesmo arquivo-raiz**, não duas ramificações independentes.
- O Sumário interno de "principal" está alinhado ao período 4T/2025 da apresentação (datas "Último" em ago/set-2025); o de "dieese" já reflete um período posterior (mar/abr-2026) — "dieese" é uma edição **cronologicamente mais avançada** do mesmo arquivo, não uma versão alternativa do mesmo período.
- 43 dos 47 gráficos do `.pptx` `ATR_Conjuntura_2025.12.pptx` têm vínculo técnico externo (`TargetMode="External"`) apontando para um arquivo de mesmo nome e pasta de "principal" ("Planilhas Definitivas/2025.4T/Apresentação_Conjuntura_4T_2025.xlsx"); nenhum aponta para um arquivo com sufixo "(2)" ou para a pasta "dieese".
- **Conclusão revista: "ambos são necessários, com papéis distintos"** — "principal" é a referência primária para reconstruir o pipeline da apresentação 4T/2025; "dieese" é indispensável apenas como fonte complementar para os poucos elementos que "principal" não contém mais (notadamente a aba `T27`, Cesta Básica). Não se trata de recomendar "dieese" por ser mais recente — ao contrário, é justamente por ser uma edição posterior que ele não deve ser tratado como a referência do 4T/2025.

Ver `VALIDACAO_TECNICA_P1.md`, Frente H, para a matriz comparativa completa e a fundamentação detalhada.
