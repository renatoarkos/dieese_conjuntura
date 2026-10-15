# Checklist — pedidos feitos no Antigravity (2026-10-14/15), verificados nesta sessão do Claude Code

## Natureza deste documento

O responsável do projeto trabalhou em paralelo com dois agentes neste repositório: Claude Code (esta sessão) e Antigravity (Google AI, sessão separada, histórico colado nesta conversa). Este documento verifica, item a item, se cada pedido feito no Antigravity está realmente implementado no código atual — não apenas relatado pelo outro agente. A partir de agora, a continuidade do trabalho fica só com o Claude Code (confirmado pelo responsável do projeto: "tente pelo menos voltar ao que era, tomando esse pedido que fiz por lá para fazer por aqui").

Commits do Antigravity já estão integrados ao histórico principal (`git log`): `311729c`, `4d7e737`, `c2bcce6`.

## Como ler o status

- ✅ **Confirmado** — verificado no código atual (classe CSS existe, arquivo existe, referência não quebrada).
- 🟡 **Confirmado com ressalva** — implementado, mas com um problema encontrado e corrigido nesta sessão.
- ⬜ **Não verificável/pendente** — não há evidência de que foi feito.

---

## 1. Geração de imagens (`frontend/img-prompts.json`, 16 ativos)

| Status | Item | Verificação |
|---|---|---|
| ✅ | `hero/hero-home.png` | arquivo existe, referenciado no hero de `index.html` |
| ✅ | `hero/og-compartilhamento.png` | arquivo existe, referenciado nas meta tags Open Graph/Twitter |
| ✅ | 5 ícones de dimensão (`dimensoes/icone-*.png`) | todos existem, referenciados em `inicio.js` e `painel.js` |
| ✅ | `secoes/quem-somos.png`, `o-que-e-dieese-360.png`, `boletim-conjuntura.png` | existem, referenciados nas 3 seções institucionais |
| ✅ | `catalogo/icone-catalogo.png`, `faq/icone-faq.png`, `contato/icone-contato.png`, `meupainel/icone-meu-painel.png` | todos existem e referenciados |
| ✅ | `icons/favicon.png` (+ `.ico`, 16×16, 32×32) | existem, `<link rel="icon">` presente em todas as páginas (`index.html`, `catalogo.html`, `painel.html`, `meu-painel.html`, `indicador.html`, `login.html`, `definir-senha.html`) |
| ✅ | `login/login-lateral.png` | arquivo existe, referenciado em `login.html` e `definir-senha.html` |

## 2. Símbolos de redes sociais e contato (pedido: "Preciso dos simbolos das redes sociais e contatos tb")

| Status | Item | Verificação |
|---|---|---|
| ✅ | Ícones SVG de Instagram, Facebook, X, LinkedIn, YouTube, TikTok no rodapé | 28 `<svg>` presentes em `index.html`, âncora `id="contato"` no rodapé |
| ✅ | Ícones de localização, telefone, WhatsApp, e-mail por categoria | presentes junto aos respectivos blocos de contato no rodapé |

## 3. Imagens de "tela de dashboard" com gráficos reais (pedido: "preciso que as imagens de telas de dash apareçam com graficos e nao assim sem nada")

| Status | Item | Verificação |
|---|---|---|
| ✅ | `hero-home.png`, `o-que-e-dieese-360.png`, `login-lateral.png` regeneradas com gráficos visíveis nas telas | arquivos substituídos (confirmado pelo relato do Antigravity; conteúdo visual não re-verificado pixel a pixel nesta sessão — verificação visual fica a cargo do responsável do projeto) |

## 4. Resumo do dia — grade completa + modal ampliado (pedido por áudio: "o cartão não é para girar nele mesmo... precisa crescer e centralizar numa versão maior, bem diagramada")

| Status | Item | Verificação |
|---|---|---|
| ✅ | Grade de 8 indicadores em destaque, cada um com gráfico completo (não só sparkline) | `montarEstruturaResumoDia`/`preencherDestaque` em `inicio.js`, classe `.destaque-grade` com CSS correspondente |
| ✅ | Clique em qualquer cartão (carrossel de dimensão, grade de destaque, linha de maiores variações) abre modal ampliado, não gira in-place | `cartao-flip.js` reescrito (frente só, sem verso, `ligarCartoesFlip` virou no-op), `cartao-modal.js` reescrito como modal de dois painéis — decisão registrada em `docs/08-decisoes-adr/0007-padrao-cartao-modal-ampliado.md` |
| ✅ | Modal traz gráfico interativo + conceituação + metodologia + fonte + link para página completa | conferido em `cartao-modal.js`, todas as classes `.modal-ind-*` têm CSS correspondente em `styles.css` |
| 🟡 | Tabela de maiores altas/baixas em duas colunas com cor própria, ranking numerado | implementado (`.variacoes-coluna-bloco.altas/.baixas`, `.rank-pos`) — **mas** o array `DESTAQUES` usava o id `reajustes_acima_inpc`, que não existe no catálogo (o real é `reajustes_acima_inpc_pct`); não quebrava nada (há fallback), só trocava silenciosamente qual indicador aparecia. **Corrigido nesta sessão** (commit `1c66c7c`). |
| ✅ | Grade de dimensões em estilo "comercial"/SaaS, com tags de indicadores em vez de texto corrido repetido | `montarGradeDimensoes`/`preencherArvoreDimensoes` em `inicio.js`, classes `.cartao-dimensao-tags`/`.tag-ind` com CSS correspondente |

## 5. Pedido de checklist em si (Antigravity, mensagens finais: "me faça um md com o prompt de tudo que trabalhamos... checklist")

| Status | Item | Verificação |
|---|---|---|
| ⬜ | Arquivo de checklist/retomada pedido ao Antigravity | não encontrado no repositório — não foi gerado antes da sessão mudar para o Claude Code. Este documento substitui esse pedido. |

---

## Itens em andamento pelo Claude Code (não vieram do Antigravity, continuam aqui)

- Microdado completo de RAIS e Novo CAGED (`db/migrations/0007_microdados_rais_caged.sql`, pipelines de carga, ADR `0006-microdados-rais-caged.md`) — schema e scripts prontos, **carga em massa ainda não executada** (pendente: `DATABASE_URL` no `.env` + rodar os scripts).
- Páginas de exploração estilo PDET/MTE para RAIS e CAGED (`rais.html`/`caged.html`) — ainda não criadas, próximo passo depois da carga.
- Limpeza de travessão em `metodologia_md` (33 indicadores) — pendente, baixa prioridade.
- Dimensão de ações/criptoativos (pesquisa Yahoo Finance) — fila separada, não iniciada.

## Observação de processo

Dois agentes editando os mesmos arquivos em paralelo gerou retrabalho (ex.: `cartao-modal.js` foi escrito por mim, depois completamente reescrito pelo Antigravity horas depois) e um bug de digitação não detectado até esta verificação. A partir de agora só o Claude Code segue com o desenvolvimento, conforme confirmado pelo responsável do projeto — isso remove o risco de conflito recorrente.
