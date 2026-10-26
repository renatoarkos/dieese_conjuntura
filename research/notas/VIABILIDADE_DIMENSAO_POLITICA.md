# Viabilidade de uma "Dimensão Política" (indicadores segmentados por governo)

> **Status: implementado em 2026-10-26.** Página pública em `frontend/politica.html`.
> Período confirmado com o responsável do projeto: desde o início do Plano Real
> (01/07/1994) até hoje. IPCA/INPC foram realimentados via BCB/SGS (séries 433/188)
> em vez do SIDRA, especificamente para cobrir essa janela inteira — antes só tinham
> dado desde 2020 (ver seção 3.3 abaixo, agora resolvida). O restante deste documento
> é mantido como registro do levantamento original, sem alteração.

## 1. Objetivo

Responder, com dado real do banco (não suposição), à pergunta: os indicadores já publicados na plataforma têm histórico suficiente para serem segmentados por governo, do mais antigo ao mais recente, no padrão de reportagem visto em veículos como a Folha de S.Paulo (desmatamento, desemprego, PIB, pobreza, cada um com o eixo do tempo dividido por mandato presidencial)? Este documento é só o levantamento de viabilidade — nenhuma implementação foi feita.

## 2. O que foi medido

Consulta direta a `indicadores_serie` em 2026-10-26: data mais antiga, data mais recente e número de pontos de cada um dos 65 indicadores hoje publicados.

## 3. Achado central: a cobertura é muito desigual

Os 65 indicadores caem em três grupos bem diferentes:

### 3.1 Histórico longo o suficiente para cruzar vários governos (uso imediato)

| Indicador | Início real na plataforma | Pontos | Governos potencialmente cobertos |
|---|---|---|---|
| `cambio_dolar` | 1953 | 884 | Todos desde a redemocratização — **ver ressalva de comparabilidade abaixo** |
| `selic` | 1986 | 1272 | Idem |
| `saldo_credito_sfn_total` | 1988 | 459 | Idem |
| `igpm` | 1989 | 448 | Idem |
| `juros_pf_cheque_especial` | 1994 | 386 | A partir do Plano Real |
| `pib_brasil`, `taxa_investimento` | 1996 | 122 cada | FHC (2º mandato) em diante |
| `commodities_geral/agropecuaria/metal/energia` | 1998 | 345 cada | FHC (2º mandato) em diante |
| `nfsp_setor_publico_consolidado` | 2002 | 286 | Fim do governo FHC em diante |
| `pim_producao_industrial`, `pmc_volume_vendas` | 2003/2004 | ~270 cada | Lula 1 em diante |
| `endividamento_familias_*`, `comprometimento_renda_*` (5 séries) | 2005 | ~258 cada | Lula 1 em diante |
| `saldo_credito_sfn_pf/pj/recursos_*` (5 séries) | 2007 | 234 cada | Lula 2 em diante |
| `juros_pf_credito_pessoal`, `juros_pj_cartao_rotativo`, `juros_pj_veiculos` | 2011 | 186 cada | Dilma em diante |
| `taxa_desocupacao`, `populacao_ocupada`, `rendimento_medio_real`, `taxa_participacao` | 2012 | 58 cada | Dilma em diante — início real da PNAD Contínua, não escolha de coleta |
| `pms_volume_servicos` | 2012 | 165 | Dilma em diante |

Isso já dá, hoje, uns 25 indicadores com densidade real para comparar pelo menos 4 a 6 períodos presidenciais.

### 3.2 Histórico curto por limite real da fonte (não dá para alongar)

- `salario_medio_real_admissao_caged`/`desligamento_caged`: começam em 2020 porque o **Novo CAGED** (a fonte) só existe desde 2020 — o CAGED antigo foi descontinuado. Não há como alongar isso para trás com a mesma metodologia.
- `taxa_sindicalizacao`: módulo anual da PNAD Contínua, só 12 pontos (2012-2025, com hiato em 2020/2021) — mesma limitação de fonte da seção 3.1.

### 3.3 Histórico curto por limite da nossa própria coleta, não da fonte (dá para alongar)

Este é o achado mais importante para decidir se a "dimensão política" é viável logo ou só depois de mais trabalho:

- **`ipca`, `inpc`, `ipca_numero_indice`: só 81 pontos, começando em 2020.** A fonte real (IBGE/SIDRA) tem IPCA mensal desde 1979/1980 e INPC desde data semelhante — isso é de longe a série mais importante para qualquer comparação entre governos (inflação é o indicador político por excelência) e está artificialmente curta na plataforma. **Não investiguei ainda se o script de coleta (`coleta_ipca_sidra.py`) já busca o histórico completo da fonte e só não foi carregado, ou se ele só pega o período recente por desenho** — isso precisa ser confirmado antes de prometer um backfill.
- `combustivel_gasolina/diesel/glp`: só 20 pontos (~1 mês) — a fonte (ANP) publica semanalmente desde pelo menos 2004, então isso também parece limite de coleta, não de fonte.
- `rais_estoque_vinculos_ativos`, `rais_rendimento_medio_dezembro`, `greves_total_ano`, `greves_horas_paradas_ano`, `piso_salarial_medio/mediano`, `reajustes_acima/abaixo_inpc_pct`, `ict_dieese`, `limite_fiscal_pessoal`, `bndes_desembolsos`, `balanca_exportacoes/importacoes/saldo`: **1 a 9 pontos cada**. Isso não é limite de fonte nem de coleta — é só porque o pipeline ficou poucos dias/execuções rodando desde a reconstrução do banco em 15/10/2026 (incidente do Supabase). Esses indicadores vão acumular histórico sozinhos, mês a mês, com o agendamento automático já funcionando — mas levariam anos para cobrir vários governos "organicamente"; teriam que ser alvo de backfill manual se a prioridade for urgente.

### 3.4 Fora de escopo para esta dimensão

Os 9 indicadores da dimensão `mercados` (Ibovespa, S&P 500, Bitcoin, ações da B3 etc.) têm só ~1 ano de histórico e, mais importante, **não são indicadores de desempenho de governo** no sentido em que os outros são — são cotação de mercado. Não fazem sentido numa "dimensão política" no mesmo molde.

## 4. Duas ressalvas que precisam ser resolvidas antes de qualquer implementação

### 4.1 Comparabilidade: moeda e metodologia mudaram ao longo do tempo

`cambio_dolar`, `selic`, `igpm` e `saldo_credito_sfn_total` têm pontos anteriores a 1994 (Plano Real) — o Brasil trocou de moeda várias vezes antes disso (cruzeiro → cruzado → cruzado novo → cruzeiro → cruzeiro real → real). Um gráfico de "câmbio em R$" desde 1953 sem marcar essas trocas de moeda e os períodos de hiperinflação anteriores ao Plano Real não é comparável ponto a ponto — exibir isso cru, segmentado por governo, sem essa ressalva explícita, violaria o princípio deste projeto de "comparabilidade temporal" e de não tratar dado bruto como comparável sem verificar pressupostos (`CLAUDE.md`, seção ESTATÍSTICA). Qualquer implementação dessas 4 séries precisa de uma nota metodológica clara sobre o corte pré/pós-Real, ou restringir a comparação entre governos a partir de 1994-1995.

### 4.2 O período de governo mais recente não pode ser presumido

As datas de início/fim de mandato de Sarney até Bolsonaro são fato histórico público, sem ambiguidade. **O que não registro aqui, de propósito, é se já houve uma eleição presidencial em outubro de 2026** (a data corrente desta sessão) nem qualquer resultado dela — isso exigiria checagem em fonte oficial (TSE) no momento da implementação, nunca presumido ou inventado por mim. Enquanto isso, "Lula (2023-)" deve ficar marcado como mandato em curso, com data de término em aberto.

## 5. Risco editorial, não só técnico

Vale registrar, não para decidir sozinho, mas para a decisão ficar explícita: segmentar indicadores socioeconômicos por governo é uma escolha de apresentação que **implicitamente convida a leitura de "qual governo foi melhor"**, mesmo que a intenção seja só organizacional. O `CLAUDE.md` deste projeto já estabelece como princípio permanente: "correlação não implica causalidade", "preserve perspectivas econômicas concorrentes quando relevantes", "nenhuma teoria deve ser automaticamente tratada como verdade empírica". Uma reportagem de jornal pode adotar o recorte "por governo" com uma linha editorial; uma plataforma de um instituto de pesquisa sindical como o DIEESE normalmente precisa de disclaimers mais explícitos — por exemplo, deixar claro que: (a) o resultado de um indicador no mandato X não isola o efeito de políticas daquele governo de fatores externos (choques internacionais, política monetária de outros países, pandemia, etc.); (b) revisões metodológicas e mudanças de fonte ao longo do tempo (ex. CAGED novo vs. antigo, PNAD Contínua substituindo a PNAD antiga em 2012) não são "piora" ou "melhora" do indicador, são mudança de régua. Isso não impede construir a dimensão — só significa que o enquadramento (texto, disclaimers, o que fica de fora) importa tanto quanto o gráfico em si, e idealmente deveria ser alinhado com alguém do DIEESE responsável por esse tipo de decisão editorial, não decidido só tecnicamente.

## 6. Resposta direta à pergunta

**Sim, dá para tabular — para cerca de 25 dos 65 indicadores hoje publicados**, cobrindo de forma real de 4 a 6 períodos presidenciais (de Dilma ou de Lula 1/FHC2 em diante, dependendo do indicador). Os outros ~40 indicadores, ou têm limite genuíno de fonte (CAGED novo, PNAD Contínua), ou simplesmente ainda não acumularam histórico suficiente desde a reconstrução do banco em 15/10/2026 — isso melhora sozinho com o tempo, mas para os casos mais importantes (IPCA/INPC, em especial) vale investigar se dá para fazer um backfill retroativo antes de esperar anos.

## 7. Próximos passos recomendados (nenhum executado ainda)

1. Confirmar se `coleta_ipca_sidra.py`/`coleta_inpc_sidra.py`/`coleta_combustiveis_anp.py` conseguem buscar histórico completo da fonte (não só o período recente) — se sim, um backfill pontual resolve a maior lacuna (seção 3.3) rapidamente.
2. Decidir, com alguém responsável pelo posicionamento editorial do DIEESE, o enquadramento da seção 5 antes de desenhar qualquer tela.
3. Definir a lista exata de governos/períodos a usar (datas públicas, sem ambiguidade até 2023; o período em curso precisa de confirmação de fonte oficial quando chegar a hora).
4. Só depois disso, planejar a implementação em si (schema, se cabe como metadado dos indicadores existentes ou como estrutura própria, e o desenho visual — provavelmente inspirado nos próprios gráficos da Folha mostrados como referência, mas adaptado ao padrão de rigor metodológico já estabelecido neste projeto).
