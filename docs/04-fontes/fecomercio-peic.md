# Fonte: FecomercioSP — PEIC (Pesquisa de Endividamento e Inadimplência do Consumidor)

**Data de consulta**: 2026-09-22 (Discovery de Fontes — Lote 05c).

## Endividamento familiar — parte PEIC/FecomercioSP

O indicador "endividamento familiar" do material do DIEESE tem duas fontes distintas: BCB (Tabela 27, já confirmada em `docs/04-fontes/bcb.md`) e PEIC/FecomercioSP (esta ficha).

| Campo | Valor |
|---|---|
| Instituição | Federação do Comércio de Bens, Serviços e Turismo do Estado de São Paulo (FecomercioSP) — entidade privada. |
| Status | **CONFIRMADO — download estruturado (Excel)**, sem API de dados tabulares. |
| Método de acesso | O domínio antigo citado em materiais de referência (`gh.fecomercio.com.br`) está **morto** (falha de DNS). Site atual: `pesquisas.fecomercio.com.br/indicador-peic/`. **Achado favorável**: o site roda em WordPress, que expõe uma API REST nativa de listagem de mídia (`wp-json/wp/v2/media?search=PEIC`), retornando todos os arquivos `.xlsx` publicados, já ordenados por data — mais robusto que raspar HTML, já que é uma API estruturada (ainda que não documentada oficialmente como "API de dados"). |
| URL de exemplo testada | `https://pesquisas.fecomercio.com.br/wp-json/wp/v2/media?search=PEIC&per_page=30` → lista real de arquivos, incluindo `PEIC-Link-Download-202608.xlsx` (mais recente). |
| Conteúdo do arquivo | 4 abas, incluindo **"Série Histórica"** (285 linhas), com a série mensal completa desde **fev/2004**, incluindo "Percentual de Famílias Endividadas" — cobre integralmente o período jan/2023-jun/2025 citado pelo material do DIEESE. |
| Periodicidade | Mensal. |
| Histórico | fev/2004 até o mês mais recente publicado. |
| **Classificação de automação** | **B — download estruturado, confirmado e testado**, com descoberta do arquivo mais recente via API de mídia do WordPress (estável, não é raspagem de HTML). |
