# ADR 0007 — Padrão de interação: Cartão Modal Ampliado (sem flip in-place)

**Data:** 2026-10-15  
**Status:** APROVADO E VIGENTE — regra permanente  
**Autor:** Registrado por solicitação explícita do responsável do projeto

---

## Contexto

A implementação anterior usava um cartão giratório (flip in-place, rotação 3D CSS)
que, ao ser clicado, virava o pequeno cartão de carrossel ou grade mostrando o
verso com a metodologia. O resultado era:

- O gráfico desaparecia ao virar;
- O texto de metodologia ficava espremido num box de ~220px com `overflow-y: auto`
  gerando uma barra de rolagem vertical feia dentro do cartão;
- A experiência era confusa: o usuário via o gráfico sumir e aparecia texto truncado.

O responsável do projeto declarou explicitamente: **"não é para virar o pequeno
mas ao clicar precisa aparecer em animação o cartão maior com o painel de cada
gráfico"**.

---

## Decisão

**Ao clicar em QUALQUER cartão de indicador — em carrossel de dimensão, em grade
de destaque ou em linha de Maiores Altas/Baixas — abrir um MODAL AMPLIADO.**

Nunca girar/flipar o cartão pequeno in-place.

### Layout do Modal

O modal (`cartao-modal.js`, `.modal-ind-*`) tem dois painéis:

| Esquerda (60%) | Direita (40%) |
|---|---|
| Gráfico interativo em alta resolução (min-height 260px) | Conceituação socioeconômica |
| Período e crosshair | Metodologia e cálculo |
| | Dados de referência (fonte, periodicidade, unidade) |
| | Notas explicativas |
| | Link → página completa do indicador |

---

## Consequências

1. `cartao-flip.js`: a função `montarCartaoFlip` agora produz apenas a **frente**
   do cartão (sem verso HTML). `ligarCartoesFlip` é um **no-op** mantido só por
   compatibilidade de chamada.

2. `cartao-modal.js`: completamente reescrito para renderizar o modal de dois painéis.

3. `inicio.js`: `preencherCarrossel` envolve cada cartão em um `<div data-id role=button>`
   que, ao clicar, chama `window.DIEESE360.abrirCartaoModal(ind, serie)`.

4. `styles.css`: classes `.cartao-flip-interior`, `.cartao-flip.virado`,
   `overflow-y: auto` no verso foram removidas. `.cartao-flip-verso { display: none }`.

---

## Proibições (não reverter)

- **PROIBIDO** reativar `transform: rotateY(180deg)` em cartões pequenos de carrossel.
- **PROIBIDO** exibir texto de metodologia dentro de um box com scrollbar em cartão pequeno.
- **PROIBIDO** esconder o gráfico ao exibir metodologia.
- O modal deve sempre ter largura mínima de `min(960px, 96vw)` e gráfico de pelo menos 260px de altura.
