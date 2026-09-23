# Roadmap por Fases — Construção do Datalake (DIEESE Conjuntura)

## Natureza deste documento

Sequência de fases propostas para levar as fontes de dados identificadas em `docs/04-fontes/CHECKLIST_FONTES_DATALAKE.md` até uma plataforma de dados operacional (SOURCE → RAW → STAGING → CURATED → ANALYTICS → APPLICATION/API, conforme `docs/03-metodologia/ARQUITETURA_AGENTES.md`, Seção 7). Este é um documento de **planejamento e desenho** (papel Data Engineer, "atua principalmente em desenho e avaliação" durante a fase DISCOVERY) — **não escolhe tecnologia, não contém código, e não autoriza implementação**. Cada fase indica explicitamente se pode ser executada dentro da fase DISCOVERY atual ou se depende de transição de fase e autorização humana.

## Papéis envolvidos

- **Especialista em Fontes & Dados**: mantém o checklist de fontes, executa lotes de Discovery de Fontes.
- **Data Engineer**: desenha contratos de dados, avalia viabilidade de ingestão, propõe testes de dados — sem implementar.
- **Especialista em Metodologia Econômica**: valida comparabilidade, transformações e limitações de cada indicador antes de qualquer contrato ser fechado.
- **Economista de Conjuntura**: prioriza quais indicadores são mais relevantes para o painel de conjuntura, quando houver mais candidatos do que capacidade de execução.
- **DIEESE Conjuntura Lead**: coordena as fases, identifica quando uma fase exige autorização humana, mantém `ESTADO_DO_PROJETO.md` atualizado.

---

## Fase 0 — Discovery de Fontes (em andamento)

**Compatível com DISCOVERY — pode continuar sem autorização adicional.**

Mapear e confirmar, para cada indicador do checklist, a fonte primária real, o método de acesso e a classificação de automação — por lotes, conforme já iniciado.

- ✅ Lote Piloto 01 concluído (6 indicadores).
- ⏳ Lotes 02-05 propostos em `CHECKLIST_FONTES_DATALAKE.md`.
- ⏳ Lote de Lacunas depende de ação humana (obtenção de arquivo/documento), não de pesquisa adicional.

**Saída desta fase**: checklist com todas as linhas em status 🟢 CONFIRMADO ou 🔴 LACUNA formalmente registrada (nunca 🟡 indefinidamente).

## Fase 1 — Especificação de contratos de dados

**Compatível com DISCOVERY — é desenho, não implementação.**

Para cada fonte já confirmada (status 🟢), o Data Engineer formaliza um contrato de dados: schema esperado, granularidade, chave(s) de identificação única, frequência de atualização, forma de tratar revisões, e onde o dado se encaixaria conceitualmente nas camadas RAW → STAGING → CURATED (sem implementar nenhuma delas).

Procedimento por indicador, conforme `agents/data-engineer.md`:
```
fonte → acesso → formato → granularidade → chaves → histórico → revisões
     → ingestão → validação → armazenamento conceitual → transformação
     → publicação → observabilidade
```

**Critério de entrada**: indicador com status 🟢 CONFIRMADO no checklist.
**Saída desta fase**: um documento de contrato de dados por indicador (ou por fonte, quando vários indicadores compartilham a mesma fonte/padrão de API), em `docs/04-fontes/` ou subpasta dedicada, a definir quando o volume justificar.

## Fase 2 — Validação metodológica dos contratos

**Compatível com DISCOVERY.**

O Especialista em Metodologia Econômica revisa cada contrato de dados proposto na Fase 1 quanto a comparabilidade, sazonalidade, defasagens, quebras estruturais e limitações — antes de qualquer contrato ser considerado fechado. Já há dois pontos pendentes desta natureza identificados no Lote Piloto 01: a possível dupla deflação no rendimento médio real, e a divergência de base de pesos do IPCA (ver `research/notas/DISCOVERY_FONTES_LOTE_PILOTO_01.md`).

**Saída desta fase**: contratos de dados marcados como "metodologicamente validados" ou "pendente de validação humana" (quando a dúvida não puder ser resolvida só com evidência disponível).

---

## Ponto de decisão — fim do que é possível sem autorização explícita

As fases 0-2 acima são compreensão, pesquisa e especificação — compatíveis com a fase DISCOVERY conforme `CLAUDE.md` ("DESENVOLVIMENTO: 1. compreender; 2. pesquisar; 3. especificar; ..."). **A partir da Fase 3, qualquer avanço envolve escrever código de ingestão real e, portanto, escolher alguma tecnologia** (linguagem, biblioteca de acesso HTTP, formato de arquivo de saída, forma de agendar execução) — o que esbarra diretamente em duas regras já registradas neste projeto e confirmadas por você nesta sessão:

- `CLAUDE.md`: "Não escolha tecnologia antes de compreender os requisitos" e "Não iniciar desenvolvimento substancial da aplicação sem autorização" — fase atual é DISCOVERY, não ARQUITETURA.
- `VISAO_DO_PRODUTO.md`, Seção 15: stack, backend, banco de dados, orquestrador etc. seguem explicitamente **não decididos**.
- `agents/data-engineer.md`: o papel Data Engineer "não deve escolher tecnologia prematuramente" nem "iniciar implementação substancial durante a fase de Discovery sem autorização humana explícita".

As fases abaixo (3 em diante) estão desenhadas, mas **não devem ser iniciadas sem uma decisão explícita sua sobre este ponto** — inclusive porque mesmo um "piloto técnico mínimo" já é, na prática, uma escolha de tecnologia (qual linguagem, qual biblioteca), ainda que pequena e reversível.

## Fase 3 — Decisão mínima de stack de ingestão (requer ADR + autorização humana)

**✅ CONCLUÍDA em 2026-09-22.** Registrada em `docs/08-decisoes-adr/0001-stack-minima-piloto-ingestao.md`: Python 3 (biblioteca padrão), sem framework/orquestrador/banco, gravação da resposta bruta da API em `data/raw/`, execução manual. Escopo restrito a PIB Brasil e IPCA (índice geral).

## Fase 4 — Piloto técnico controlado

**✅ CONCLUÍDA em 2026-09-22** para os 2 indicadores do escopo do ADR 0001. Scripts em `pipelines/ingestao/` (`coleta_pib_sidra.py`, `coleta_ipca_sidra.py`), executados com sucesso:

- **PIB Brasil (SIDRA 5932)**: 489 registros reais coletados, cobrindo 1996 T1 a 2026 T2, todas as 4 variáveis do indicador (taxa trimestral a.a., acumulada 4 trimestres, acumulada no ano, trimestre/trimestre anterior).
- **IPCA índice geral (SIDRA 7060)**: 321 registros reais coletados, cobrindo jan/2020 a ago/2026, variação mensal/acumulada no ano/acumulada em 12 meses/peso mensal.

Dados gravados sem nenhuma transformação em `data/raw/ibge_sidra/` (não versionado, conforme `.gitignore` preexistente e ADR 0001). Validou o padrão SOURCE → RAW ponta a ponta para os 2 candidatos naturais do checklist.

**Expandida em 2026-09-22** sob `docs/08-decisoes-adr/0002-expansao-piloto-por-blocos.md` — ver Fase 5.

## Fase 5 — Expansão gradual (indicadores A/B)

**✅ Primeira expansão concluída em 2026-09-22.** Após dois novos lotes de Discovery de Fontes (Lote 02 — SIDRA; Lote 03 — BCB) confirmarem mais 6 indicadores, o piloto foi expandido para 9 scripts organizados em 4 blocos temáticos (`pipelines/ingestao/bloco_1_macroeconomia/`, `bloco_2_monetario_credito/`, `bloco_3_inflacao/`, `bloco_4_mercado_trabalho/`), todos executados com sucesso:

- **Bloco 1 — Macroeconomia**: PIB Brasil, Câmbio (2 séries), PMC-comércio.
- **Bloco 2 — Monetário e Crédito**: Selic (2 séries), Juros por modalidade (4 séries).
- **Bloco 3 — Inflação**: IPCA índice geral.
- **Bloco 4 — Mercado de Trabalho**: Desocupação, Posição na ocupação, Taxa de participação.

Indicadores com ambiguidade de fonte não resolvida (NFSP, PIB per capita, PMS/PIM, Rendimento médio real com deflacionamento DIEESE) foram deliberadamente deixados fora — automatizar uma fonte incerta violaria o princípio de não inventar fonte/dado.

**Próxima expansão** depende de novo lote de Discovery de Fontes (Lote 04 — CAGED/MTE é o recomendado) ou de validação humana das pendências (QF04, QF07, QF08).

## Fase 6 — Indicadores complexos (C/D/E) e lacunas

Indicadores que exigem processamento de microdados, decisão de processo (fontes por e-mail, consolidação manual), ou que hoje são lacuna (Greves, Cesta Básica, ICT, Combustíveis, Negociação Coletiva) — dependem primeiro da resolução das perguntas de validação humana já registradas, e alguns podem nunca ser totalmente automatizáveis (ex.: ICV, deflacionamento próprio do DIEESE), permanecendo como ingestão assistida/manual por desenho, não por limitação técnica temporária.

## Fase 7 — Camadas STAGING → CURATED → ANALYTICS → APPLICATION/API

Desenho conceitual (ainda sem tecnologia) de como os dados RAW ingeridos nas fases anteriores são padronizados (STAGING), validados e organizados semanticamente (CURATED), transformados em indicadores/agregações (ANALYTICS) e disponibilizados à plataforma (APPLICATION/API) — incluindo o Catálogo Mestre de Indicadores como camada semântica central. Este desenho pode começar em paralelo às fases 3-6, como especificação, mas sua implementação depende das mesmas fases de autorização.

---

## Quadro-resumo

| Fase | O que é | Status |
|---|---|---|
| 0 — Discovery de Fontes | Pesquisa e confirmação de fonte | ✅ Lote Piloto 01 concluído |
| 1 — Contratos de dados | Especificação (schema, chaves, frequência) | ⏳ Não iniciada formalmente |
| 2 — Validação metodológica | Revisão de comparabilidade/limitações | ⏳ Parcial (achados registrados, formalização pendente) |
| 3 — Decisão de stack mínima | ADR + autorização | ✅ Concluída (ADR 0001, 2026-09-22) |
| 4 — Piloto técnico controlado | Código real, 2 indicadores | ✅ Concluída (PIB e IPCA, 2026-09-22) |
| 5 — Expansão gradual | Código real, demais indicadores A/B | ✅ Primeira expansão concluída (9 scripts, 4 blocos, 2026-09-22) — expansões futuras dependem de novos lotes de Discovery de Fontes |
| 6 — Indicadores complexos/lacunas | Depende de validação humana + processo | ⛔ Bloqueada por perguntas já registradas (QF01-QF06, QF19-QF33) |
| 7 — STAGING→CURATED→ANALYTICS→API | Desenho conceitual + implementação | ⏳ Não iniciada |
