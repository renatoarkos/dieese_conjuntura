# pipelines/

Piloto técnico controlado de ingestão de dados — escopo e justificativa registrados em:
- `docs/08-decisoes-adr/0001-stack-minima-piloto-ingestao.md` (stack mínima; escopo original: PIB, IPCA)
- `docs/08-decisoes-adr/0002-expansao-piloto-por-blocos.md` (expansão por blocos; escopo ampliado nos Lotes 02-06)
- `docs/08-decisoes-adr/0003-agendamento-github-actions.md` (agendamento automático)
- `docs/08-decisoes-adr/0004-supabase-raw-storage.md` (armazenamento definitivo do RAW)

**Este NÃO é o desenho definitivo de ingestão da plataforma.** É um piloto mínimo e reversível, restrito a indicadores com fonte **inequivocamente confirmada** pelo Discovery de Fontes (`research/notas/DISCOVERY_FONTES_LOTE_PILOTO_01.md`, Lotes 02-06).

## Por onde começar

Este documento explica a estrutura geral e as decisões que valem para todos os
scripts. Para o passo a passo de cada indicador especificamente — o que ele
mede, de onde vem o dado, e como o código funciona — leia o README de dentro
do bloco correspondente:

- [`bloco_1_macroeconomia/README.md`](ingestao/bloco_1_macroeconomia/README.md) — PIB, câmbio, comércio/serviços/indústria, capacidade instalada, comércio exterior, fiscal
- [`bloco_2_monetario_credito/README.md`](ingestao/bloco_2_monetario_credito/README.md) — Selic, juros por modalidade, endividamento das famílias, crédito
- [`bloco_3_inflacao/README.md`](ingestao/bloco_3_inflacao/README.md) — IPCA, INPC, IGP-M, expectativas de inflação, combustíveis
- [`bloco_4_mercado_trabalho/README.md`](ingestao/bloco_4_mercado_trabalho/README.md) — desocupação, ocupação, participação, sindicalização (PNAD Contínua)
- [`bloco_5_caged/README.md`](ingestao/bloco_5_caged/README.md) — microdados do Novo CAGED

## Anatomia de um script de coleta

Todo script deste piloto segue a mesma forma, para que aprender a ler um sirva
para ler qualquer outro. Usando `coleta_pib_sidra.py` como referência:

1. **Docstring do módulo** — antes de qualquer código, explica: o que o
   indicador mede, de onde vem o dado e por quê, como funciona o protocolo/API
   daquela fonte em geral (não só desta tabela — o objetivo é que dê para
   reconhecer o mesmo padrão numa tabela nova da mesma fonte), e um resumo
   numerado dos passos que o script executa.
2. **Constantes no topo** — a URL (ou dicionário de URLs, quando o script
   coleta mais de uma série) e `DESTINO`, o caminho de `data/raw/` onde o
   resultado é gravado. Ficam separadas do código para que, ao adaptar o
   script para uma fonte parecida, baste trocar essas linhas.
3. **Funções pequenas, uma por etapa** — nomeadas com prefixo `_` (privadas do
   módulo) e um verbo claro: `_buscar_dados`, `_salvar_raw`, `_conectar`,
   `_localizar_link_atual`. Cada uma faz uma coisa só, com uma docstring
   curta explicando o quê e, quando não é óbvio, o porquê (ex. por que um
   `timeout`, por que um `encoding` específico).
4. **`coletar()`** — a função que orquestra: chama as etapas acima, nesta
   ordem, e devolve o(s) `Path` do(s) arquivo(s) gravado(s). Não faz trabalho
   próprio, só encadeia.
5. **`if __name__ == "__main__":`** — roda `coletar()`, imprime o que foi
   feito, e chama `registrar_coleta(...)` para cada arquivo (ver seção
   "Integração com Supabase" abaixo).

Um script deste piloto **nunca transforma o dado** — grava a resposta da
fonte exatamente como recebida (ver `CLAUDE.md`, seção DADOS, camada RAW).
Calcular variações, juntar séries, escolher entre fontes candidatas ou
qualquer outra conta é trabalho de uma camada posterior (STAGING), a partir
do arquivo que o script gravou — nunca dentro do próprio script de coleta.

## Estrutura por blocos

Espelha os blocos temáticos de `docs/04-fontes/CHECKLIST_FONTES_DATALAKE.md`.

```
pipelines/ingestao/
├── bloco_1_macroeconomia/
│   ├── coleta_pib_sidra.py                   — PIB Brasil (SIDRA 5932)
│   ├── coleta_cambio_bcb.py                  — Câmbio (BCB/SGS 3694 + 3698)
│   ├── coleta_pmc_comercio_sidra.py          — Volume de vendas comércio, PMC (SIDRA 8881)
│   ├── coleta_pms_servicos_sidra.py          — Volume de serviços, PMS (SIDRA 5906)
│   ├── coleta_pim_industria_sidra.py         — Produção industrial, PIM-PF (SIDRA 8888)
│   ├── coleta_pib_mundial_fmi.py             — PIB Mundial (FMI WEO, API SDMX)
│   ├── coleta_uci_cni.py                     — UCI (CNI Indicadores Industriais, raspagem direcionada)
│   ├── coleta_balanca_comercial_comexstat.py — Balança comercial (MDIC/Comex Stat, CSV via curl)
│   ├── coleta_limite_fiscal_siconfi.py       — Limite fiscal por UF (SICONFI, 27 estados)
│   ├── coleta_commodities_bcb.py             — Índice de Commodities Brasil, IC-Br (BCB/SGS, 4 séries)
│   └── coleta_taxa_investimento_sidra.py     — Taxa de investimento, FBCF/PIB (SIDRA 6727)
├── bloco_2_monetario_credito/
│   ├── coleta_selic_bcb.py                   — Selic (BCB/SGS 4189 + 432, séries separadas)
│   ├── coleta_juros_modalidade_bcb.py        — Juros por modalidade PF/PJ (BCB/SGS 20728, 22019, 20741, 20742)
│   ├── coleta_endividamento_peic_fecomercio.py — Endividamento familiar, parte PEIC (FecomercioSP)
│   ├── coleta_endividamento_bcb.py           — Endividamento familiar, parte BCB (família RNDBF, 3 séries)
│   └── coleta_saldo_credito_sfn_bcb.py       — Saldo de crédito do SFN (6 séries: total/PF/PJ/livres/direcionados)
├── bloco_3_inflacao/
│   ├── coleta_ipca_sidra.py                  — IPCA índice geral (SIDRA 7060)
│   ├── coleta_expectativas_focus_bcb.py      — Expectativas de mercado IPCA/INPC (BCB Focus/Olinda)
│   ├── coleta_inpc_sidra.py                  — INPC índice geral (SIDRA 7063)
│   ├── coleta_igpm_bcb.py                    — IGP-M (FGV, via rota alternativa BCB/SGS 189)
│   ├── coleta_cesta_basica_dieese.py         — Cesta básica x salário mínimo (DIEESE/Conab, boletim PDF mensal)
│   └── coleta_combustiveis_anp.py            — Preços de combustíveis (ANP, últimas 4 semanas)
├── bloco_4_mercado_trabalho/
│   ├── coleta_desocupacao_sidra.py           — Taxa de desocupação (SIDRA 4093)
│   ├── coleta_posicao_ocupacao_sidra.py      — Posição na ocupação (SIDRA 4097)
│   ├── coleta_taxa_participacao_sidra.py     — Taxa de participação (SIDRA 6461)
│   ├── coleta_sindicalizacao_sidra.py        — Taxa de sindicalização (SIDRA 8676)
│   ├── coleta_rendimento_medio_real_sidra.py — Rendimento médio real do trabalho (SIDRA 5440)
│   ├── coleta_negociacao_coletiva_dieese.py  — Reajustes e pisos salariais em negociação coletiva (DIEESE, boletim PDF mensal)
│   ├── coleta_ict_dieese.py                  — Índice da Condição do Trabalho (DIEESE, boletim PDF trimestral)
│   └── coleta_greves_dieese.py               — Número de greves, categorias e reivindicações (DIEESE/SAG, boletim PDF semestral/anual)
└── bloco_5_caged/
    └── coleta_caged_microdados_ftp.py        — Novo CAGED, microdados brutos (FTP MTE/PDET — sem API)
```

**31 scripts no total**, mais `supabase_raw.py` e `google_drive_raw.py` (helpers compartilhados, não são motores de coleta — ver seção "Integração com Supabase" abaixo).

## Como executar

Cada script pode ser rodado individualmente:

```bash
python3 pipelines/ingestao/bloco_1_macroeconomia/coleta_pib_sidra.py
python3 pipelines/ingestao/bloco_1_macroeconomia/coleta_cambio_bcb.py
```

Isso é útil para testar um script sozinho ou rodar uma coleta avulsa. Na
prática, porém, os 31 scripts já rodam **sozinhos e agendados**, via GitHub
Actions (`.github/workflows/motores-{diarios,semanais,mensais}.yml` — ver
ADR 0003), agrupados por frequência de publicação da fonte, não por script
individual.

Cada script grava a resposta bruta da fonte (sem nenhuma transformação) em `data/raw/<fonte>/`, com nome de arquivo incluindo a tabela/série e o timestamp UTC da coleta. `data/raw/` não é versionado no Git (ver `.gitignore`) — é a camada RAW conceitual (`CLAUDE.md`), que nunca deve ser editada manualmente. Uma cópia de cada arquivo também vai para o Supabase Storage (ver "Integração com Supabase" abaixo) — esse é o destino definitivo da série histórica, não `data/raw/` local nem os artifacts do GitHub Actions.

## Decisões de formato de extração (todas documentadas no cabeçalho do respectivo script)

- **API direta** (maioria dos scripts): IBGE/SIDRA, BCB/SGS, BCB/Olinda (Focus), FMI/SDMX, SICONFI/ORDS.
- **Download estruturado com descoberta dinâmica de URL**: PEIC/FecomercioSP (via API de listagem de mídia do WordPress — estável, não é raspagem de HTML) e CNI/UCI (via regex sobre a página oficial, porque a CNI não expõe API de listagem — é raspagem direcionada mínima, não scraping de conteúdo).
- **Download estruturado via `curl` (não `urllib`)**: Comex Stat — o servidor `balanca.mdic.gov.br` envia uma cadeia de certificado TLS incompleta, que o módulo `ssl` do Python rejeita mesmo com `certifi`; `curl` resolve a cadeia corretamente. Optou-se por trocar a ferramenta de download (mantendo verificação de certificado ativa) em vez de desabilitar a verificação SSL no Python — ver docstring do script para o raciocínio completo.
- **FTP de microdados brutos**: Novo CAGED — não há API nem link estável de tabelas prontas (pasta Google Drive sem URL fixa); o FTP público é a única fonte estável confirmada, mas entrega microdados, não tabelas agregadas — ver `docs/04-fontes/mte-caged.md` e `bloco_5_caged/README.md`. Único script com duas formas de coleta: `coletar()` (mês mais recente, é o que roda agendado) e `coletar_periodo(mes_inicio, mes_fim)` (um intervalo de meses, para montar série histórica local sob demanda — não faz parte do agendamento automático).
- **Rota alternativa via outra instituição**: IGP-M — o Portal FGV/IBRE não expõe API pública (acesso via contrato/assinatura); o BCB replica oficialmente o IGP-M via SGS (código 189), usado como fonte — ver `docs/04-fontes/fgv-indatend.md`.
- **Download direto com detecção automática de mês mais recente**: Cesta Básica — a fonte era registrada como lacuna (arquivo interno não obtido); a pesquisa encontrou que o próprio DIEESE publica mensalmente, em parceria com a Conab, um boletim PDF público com exatamente o indicador citado. O script tenta os últimos meses a partir do corrente até achar o mais recente publicado — ver `docs/04-fontes/dieese-publicacoes.md`.
- **Download direto com detecção automática de edição mais recente (numeração sequencial, não ano/mês)**: Negociação Coletiva — o Mediador/MTE (fonte citada no material) não tem API nem exportação em massa (confirmado em duas rodadas de investigação), mas o próprio DIEESE publica mensalmente o boletim "De Olho nas Negociações", já calculando reajustes vs. INPC e pisos salariais a partir dos microdados do Mediador. Diferente da Cesta Básica, a URL usa número de edição sequencial, não ano/mês — o script parte de uma âncora confirmada (edição 67 = abril/2026) e estima a edição corrente pelos meses decorridos, testado com sucesso encontrando a edição 72 (setembro/2026) numa execução real. **Confirmado por teste técnico (`pdftotext -layout -enc UTF-8`) que o PDF tem texto real extraível** (diferente do ICT e do Balanço das Greves, que são PDF-imagem) — por isso este é o único dos quatro boletins institucionais do DIEESE classificado como B, não E. Extração da tabela (STAGING) ainda não implementada.
- **Cabeçalhos HTTP de navegador para evitar detecção de bot**: Combustíveis (ANP) — a página oficial retornava HTTP 403 sem cabeçalhos `Accept`/`Accept-Language`, mas funcionou normalmente ao adicioná-los. Não era um bloqueio institucional — ver `docs/04-fontes/anp-ipeadata.md`.

## Notas sobre séries compostas ou com pendência de mapeamento

- **Selic** (`coleta_selic_bcb.py`): grava as duas séries-fonte (SGS 4189 e SGS 432) separadamente, sem aplicar a regra de corte (4189 até jul/2024, 432 a partir de ago/2024) confirmada em `docs/04-fontes/bcb.md`. Essa composição é uma transformação e pertence à camada STAGING, não à RAW.
- **Endividamento familiar, parte BCB** (`coleta_endividamento_bcb.py`): coleta as 3 séries candidatas da família RNDBF — qual série (ou combinação) corresponde exatamente à "Tabela 27" citada pelo material do DIEESE não está confirmado com certeza (ver `docs/04-fontes/bcb.md`).
- **Saldo de crédito SFN** (`coleta_saldo_credito_sfn_bcb.py`): coleta 6 das possíveis séries — 3 recortes adicionais (PJ-livres, PJ-direcionados, PF-direcionados) foram localizados no catálogo do BCB mas não testados via API, então ficam fora do piloto.

## Limitação operacional observada nesta rodada (não é problema de fonte)

Dois scripts envolvem arquivos grandes (dezenas/centenas de MB) e, neste ambiente de desenvolvimento específico, sofreram quedas de conexão recorrentes durante a transferência (confirmado: a fonte responde HTTP 200, os dados são reais — a conexão cai no meio, de forma inconsistente). Ambos implementam retomada automática (curl `-C -` / FTP `REST`).

- `coleta_caged_microdados_ftp.py`: **completou com sucesso** — `CAGEDMOV202607...7z` chegou a 55.197.862 bytes (tamanho exato esperado), assinatura de arquivo 7z verificada e válida.
- `coleta_balanca_comercial_comexstat.py`: **completou com sucesso** — exportação (`EXP_2026.csv`) 75.055.366 bytes e importação (`IMP_2026.csv`) 120.181.098 bytes, ambos batendo exatamente com o `Content-Length` declarado pelo servidor. Os dois downloads grandes do piloto confirmam que a lógica de retomada funciona corretamente de ponta a ponta.

## Integração com Supabase (ADR 0004)

Todos os 31 scripts, além de gravar em `data/raw/` (que continua sendo a cópia local e a
fonte de verdade imediata deste piloto), agora também chamam `registrar_coleta()`
(`pipelines/supabase_raw.py`) ao final de cada execução bem-sucedida:

- Envia uma cópia do arquivo bruto para o bucket `raw` do Supabase Storage (`raw/<fonte>/<arquivo>`, mesma organização de pastas de `data/raw/<fonte>/`).
- Registra uma linha na tabela `raw_ingestoes` (fonte, script, timestamp, caminho no Storage, tamanho, SHA-256, status).

Testado de ponta a ponta contra o projeto Supabase real, cobrindo os 3 formatos de retorno de `coletar()` existentes no piloto: `Path` único (`coleta_pib_sidra.py`), `Path` único com cálculo de tamanho (`coleta_uci_cni.py`), `list[Path]` com loop (`coleta_cambio_bcb.py`) e `list[Path]` sem loop explícito (`coleta_limite_fiscal_siconfi.py`, 27 arquivos — todos confirmados registrados).

**Falha ao enviar para o Supabase nunca interrompe a coleta em si** — `registrar_coleta()` captura qualquer erro de rede/API e apenas avisa em stderr; a gravação local em `data/raw/` já terá acontecido antes dessa chamada. Também não faz nada (silenciosamente) se `SUPABASE_URL`/`SUPABASE_SERVICE_ROLE_KEY` não estiverem em `.env` — mantém os scripts funcionando em qualquer ambiente sem Supabase configurado.

**Arquivos grandes (>45 MB): particionados automaticamente.** Confirmado na prática: o Storage do Supabase rejeita arquivos acima de 50 MB (HTTP 413). `registrar_coleta()` detecta isso e divide o arquivo em partes sequenciais antes do envio — cada parte como um objeto separado, com a lista de partes (em ordem) salva em `raw_ingestoes.metadata`. `reconstruir_arquivo()` remonta o original a partir das partes (testado: hash SHA-256 idêntico ao original após reconstrução). Nenhuma ação extra é necessária nos scripts de coleta — o particionamento acontece dentro de `supabase_raw.py`, de forma transparente. Uma tentativa de usar o Google Drive como destino alternativo para esses arquivos foi abandonada por limitações de conta/plano fora do nosso controle — ver `docs/08-decisoes-adr/0004-supabase-raw-storage.md` para o histórico completo. O código ficou pronto em `pipelines/google_drive_raw.py`, não usado atualmente.

## Regras destes scripts

- Nunca transformam o dado — apenas gravam a resposta bruta da fonte.
- Não têm dependência externa além da biblioteca padrão do Python (exceção documentada: `curl` via subprocess para Comex Stat, por questão de TLS do servidor).
- Rodam agendados via GitHub Actions (ver ADR 0003) — execução manual (`python3 <script>`) continua funcionando para testes e coletas avulsas.
- **Motores para fontes DIEESE — pausa revista (2026-09-23)**: uma pausa geral (2026-09-23, mesma data) havia sido decidida para não investir mais engenharia em fontes DIEESE enquanto se aguardava planilha própria. Testado depois, no mesmo dia, com uma validação rigorosa (comparação número a número contra a apresentação interna do DIEESE em `materiais/originais/`): os boletins públicos de ICT e Greves, que antes pareciam PDF-imagem/vetorizado, na verdade têm texto extraível de verdade e batem exatamente com a fonte interna — erro de uma ferramenta de leitura, não da fonte. Com essa evidência, o responsável do projeto autorizou construir os motores de ICT e Greves também. Hoje os 5 motores de fonte DIEESE (`coleta_cesta_basica_dieese.py`, `coleta_negociacao_coletiva_dieese.py`, `coleta_ict_dieese.py`, `coleta_greves_dieese.py`) estão todos rodando, testados e validados. Só **INDATEND** continua sem motor — não por falta de fonte, mas porque é confirmadamente um processo de trabalho interno do DIEESE (planilha + e-mail), não uma fonte externa (ver `docs/04-fontes/fgv-indatend.md`).
- **Explicitamente NÃO cobertos** (ambiguidade de fonte não resolvida, ver ADR 0002 e `research/notas/DISCOVERY_FONTES_LOTE_PILOTO_01.md`): NFSP (QF07), PIB per capita (QF08), Rendimento médio real com deflacionamento DIEESE (QF04) — este último, aliás, é o único indicador com fonte 100% confirmada (SIDRA 5440) que ainda não tem motor construído.
- Qualquer expansão a novos blocos/indicadores requer fonte confirmada primeiro (Discovery de Fontes).
