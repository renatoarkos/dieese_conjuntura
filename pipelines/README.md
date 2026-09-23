# pipelines/

Piloto técnico controlado de ingestão de dados — escopo e justificativa registrados em:
- `docs/08-decisoes-adr/0001-stack-minima-piloto-ingestao.md` (stack mínima; escopo original: PIB, IPCA)
- `docs/08-decisoes-adr/0002-expansao-piloto-por-blocos.md` (expansão por blocos; escopo ampliado nos Lotes 02-06)

**Este NÃO é o desenho definitivo de ingestão da plataforma.** É um piloto mínimo e reversível, restrito a indicadores com fonte **inequivocamente confirmada** pelo Discovery de Fontes (`research/notas/DISCOVERY_FONTES_LOTE_PILOTO_01.md`, Lotes 02-06).

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
│   └── coleta_limite_fiscal_siconfi.py       — Limite fiscal por UF (SICONFI, 27 estados)
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
│   └── coleta_negociacao_coletiva_dieese.py  — Reajustes e pisos salariais em negociação coletiva (DIEESE, boletim PDF mensal)
└── bloco_5_caged/
    └── coleta_caged_microdados_ftp.py        — Novo CAGED, microdados brutos (FTP MTE/PDET — sem API)
```

**26 scripts no total**, mais `supabase_raw.py` (helper compartilhado, não é um motor de coleta — ver seção "Integração com Supabase" abaixo).

## Como executar

```bash
python3 pipelines/ingestao/bloco_1_macroeconomia/coleta_pib_sidra.py
python3 pipelines/ingestao/bloco_1_macroeconomia/coleta_cambio_bcb.py
# ...um comando por script, execução manual nesta fase (sem agendamento automático).
```

Cada script grava a resposta bruta da fonte (sem nenhuma transformação) em `data/raw/<fonte>/`, com nome de arquivo incluindo a tabela/série e o timestamp UTC da coleta. `data/raw/` não é versionado no Git (ver `.gitignore`) — é a camada RAW conceitual (`CLAUDE.md`), que nunca deve ser editada manualmente.

## Decisões de formato de extração (todas documentadas no cabeçalho do respectivo script)

- **API direta** (maioria dos scripts): IBGE/SIDRA, BCB/SGS, BCB/Olinda (Focus), FMI/SDMX, SICONFI/ORDS.
- **Download estruturado com descoberta dinâmica de URL**: PEIC/FecomercioSP (via API de listagem de mídia do WordPress — estável, não é raspagem de HTML) e CNI/UCI (via regex sobre a página oficial, porque a CNI não expõe API de listagem — é raspagem direcionada mínima, não scraping de conteúdo).
- **Download estruturado via `curl` (não `urllib`)**: Comex Stat — o servidor `balanca.mdic.gov.br` envia uma cadeia de certificado TLS incompleta, que o módulo `ssl` do Python rejeita mesmo com `certifi`; `curl` resolve a cadeia corretamente. Optou-se por trocar a ferramenta de download (mantendo verificação de certificado ativa) em vez de desabilitar a verificação SSL no Python — ver docstring do script para o raciocínio completo.
- **FTP de microdados brutos**: Novo CAGED — não há API nem link estável de tabelas prontas (pasta Google Drive sem URL fixa); o FTP público é a única fonte estável confirmada, mas entrega microdados, não tabelas agregadas — ver `docs/04-fontes/mte-caged.md`.
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

Todos os 26 scripts, além de gravar em `data/raw/` (que continua sendo a cópia local e a
fonte de verdade imediata deste piloto), agora também chamam `registrar_coleta()`
(`pipelines/supabase_raw.py`) ao final de cada execução bem-sucedida:

- Envia uma cópia do arquivo bruto para o bucket `raw` do Supabase Storage (`raw/<fonte>/<arquivo>`, mesma organização de pastas de `data/raw/<fonte>/`).
- Registra uma linha na tabela `raw_ingestoes` (fonte, script, timestamp, caminho no Storage, tamanho, SHA-256, status).

Testado de ponta a ponta contra o projeto Supabase real, cobrindo os 3 formatos de retorno de `coletar()` existentes no piloto: `Path` único (`coleta_pib_sidra.py`), `Path` único com cálculo de tamanho (`coleta_uci_cni.py`), `list[Path]` com loop (`coleta_cambio_bcb.py`) e `list[Path]` sem loop explícito (`coleta_limite_fiscal_siconfi.py`, 27 arquivos — todos confirmados registrados).

**Falha ao enviar para o Supabase nunca interrompe a coleta em si** — `registrar_coleta()` captura qualquer erro de rede/API e apenas avisa em stderr; a gravação local em `data/raw/` já terá acontecido antes dessa chamada. Também não faz nada (silenciosamente) se `SUPABASE_URL`/`SUPABASE_SERVICE_ROLE_KEY` não estiverem em `.env` — mantém os scripts funcionando em qualquer ambiente sem Supabase configurado.

**Risco não testado nesta rodada**: os dois maiores arquivos do piloto (CAGED `.7z`, ~55 MB; Comex Stat CSV, até ~120 MB) não foram reexecutados para validar o upload ao Storage — o padrão de código é idêntico ao dos scripts testados, mas o limite de tamanho padrão do Storage do Supabase pode rejeitar arquivos muito grandes via upload direto (não-resumível). Se isso acontecer, o comportamento já é seguro (loga `status: erro` em `raw_ingestoes`, não quebra a coleta) — mas a série histórica desses dois indicadores no Storage pode ficar incompleta até isso ser confirmado/ajustado.

## Regras destes scripts

- Nunca transformam o dado — apenas gravam a resposta bruta da fonte.
- Não têm dependência externa além da biblioteca padrão do Python (exceção documentada: `curl` via subprocess para Comex Stat, por questão de TLS do servidor).
- Não são agendados automaticamente — execução manual nesta fase.
- **Explicitamente NÃO cobertos** (ambiguidade de fonte não resolvida, ver ADR 0002 e `research/notas/DISCOVERY_FONTES_LOTE_PILOTO_01.md`): NFSP (QF07), PIB per capita (QF08), Rendimento médio real com deflacionamento DIEESE (QF04), PMS/PIM de recortes específicos além do índice geral, ICT, Greves (lacunas de arquivo-fonte, PDF-imagem sem texto extraível).
- Qualquer expansão a novos blocos/indicadores requer fonte confirmada primeiro (Discovery de Fontes).
