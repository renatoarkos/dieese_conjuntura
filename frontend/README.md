# frontend/ — DIEESE 360

Interface do DIEESE 360, decidida e construída conforme
`docs/08-decisoes-adr/0005-dieese-360-frontend-e-camada-curated.md`: HTML/CSS/JS
puro (sem framework, sem bundler), `supabase-js` vendorizado, mesmo padrão já
validado em `painel_saude_mental/painel-web`.

## Estrutura

- `index.html` — página pública (hero, dimensões, amostra de indicadores, ticker).
- `login.html` / `definir-senha.html` — Supabase Auth.
- `painel.html` — área interna (pós-login): navegação pelas 5 dimensões.
- `css/styles.css` — identidade visual do DIEESE (tokens herdados de `painel-web`) + componentes novos (ticker, cartão giratório, sparkline, mapa por UF).
- `js/dados.js` — busca `indicadores`/`indicadores_serie` no Supabase, formata valores, calcula tendência, monta o HTML dos cartões.
- `js/mapa-uf.js` — mapa coroplético por UF (malha oficial do IBGE, vendorizada em `assets/mapas/malha_uf.geojson`), usado hoje só pelo indicador "Limite fiscal de pessoal".
- `js/cartao-flip.js` / `js/animacao-dash.js` — interação de virar o cartão e animação de entrada.
- `img-prompts.json` — especificação das imagens de marca a gerar (mesmo formato de `painel-web/img-prompts.json`) — **as imagens em si ainda não foram geradas**.

## Como rodar localmente

Não há build — é preciso só um servidor estático (abrir `index.html` direto
como `file://` não funciona, porque `fetch()` do mapa e dos módulos precisa de
HTTP). Qualquer servidor estático serve, por exemplo:

```
cd frontend
python3 -m http.server 8080
```

E abrir `http://localhost:8080/`.

## Pendências antes de usar de verdade

1. **Aplicar a migração 0002** (`db/migrations/0002_criar_camada_curated.sql`) no SQL Editor do Supabase — mesma limitação do ADR 0004, as chaves de API não permitem DDL (ver `db/README.md`).
2. **Rodar os scripts de `pipelines/curated/`** pelo menos uma vez (manualmente ou esperando a próxima execução agendada dos workflows) para popular `indicadores_serie` — sem isso os cartões ficam todos "sem pontos publicados".
3. **Criar a primeira conta de acesso ao painel interno**: Supabase Dashboard → Authentication → Users → convidar por e-mail; depois inserir a linha correspondente em `perfis` (não existe gatilho automático ligando `auth.users` a `perfis` nesta rodada):
   ```sql
   insert into perfis (id, nome, email) values
     ('<uuid do usuário em auth.users>', 'Nome da pessoa', 'email@dieese.org.br');
   ```
4. **Gerar as imagens de `img-prompts.json`** e publicá-las em `assets/` — o painel funciona sem elas (os espaços decorativos simplesmente ficam sem imagem), mas a identidade visual completa depende disso.
5. **Deploy** — não feito nesta rodada (ação externa visível, requer autorização separada, ver ADR 0005).

## O que falta (fora do escopo desta rodada)

- As outras 4 dimensões (Monetário/Crédito, Inflação, Mercado de Trabalho, CAGED) aparecem no painel interno com um estado "em construção" — a interface já está pronta, falta repetir o padrão de `pipelines/curated/` para os indicadores de cada bloco.
- UCI/CNI e PIB Mundial/FMI (2 dos 12 indicadores do `bloco_1_macroeconomia`) não têm transformação CURATED ainda — ver ADR 0005 para o motivo (não é falta de prioridade, é um RAW que precisa de mais investigação antes de confiar num parser).
