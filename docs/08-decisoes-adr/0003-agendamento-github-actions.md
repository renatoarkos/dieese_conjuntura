# ADR 0003 — Agendamento dos motores via GitHub Actions (cron)

## Status

Aceito — 2026-09-23. **Implementação parcial**: workflows escritos e prontos; ativação real (push para GitHub) pendente de autorização explícita, pois o repositório ainda não tem remoto configurado.

## Contexto

`docs/02-arquitetura/PLANO_MOTORES_INGESTAO.md` identificou que 25 dos 27 indicadores automatizáveis já têm motor de coleta funcionando (`pipelines/ingestao/`), mas todos rodam manualmente. Para a plataforma ter dados "sempre atualizados", os motores precisam rodar sozinhos, respeitando a periodicidade de cada fonte.

O responsável pelo projeto escolheu explicitamente, entre as opções apresentadas (cron local, função agendada em nuvem, orquestrador completo, adiar decisão), a opção **"função agendada em nuvem"**, com recomendação de GitHub Actions.

## Decisão

- **Mecanismo de agendamento**: GitHub Actions, usando o gatilho `schedule` (sintaxe cron) — não exige servidor próprio, roda em runners efêmeros do GitHub, gratuito para repositórios públicos e com cota generosa para privados.
- **Estrutura**: 3 workflows por faixa de frequência (não um por indicador, para manter o número de arquivos gerenciável):
  - `motores-diarios.yml` — Selic e Expectativas Focus (as únicas fontes que de fato mudam todo dia).
  - `motores-semanais.yml` — todos os motores de periodicidade mensal ou mais frequente (IPCA, INPC, PMC, PMS, PIM, Câmbio, Juros por modalidade, Endividamento BCB, Saldo de crédito, IGP-M, Comex Stat, PEIC, Cesta Básica, UCI, CAGED, Combustíveis). Rodar semanalmente uma fonte mensal é seguro (a nova publicação é capturada dentro de até 7 dias) e evita depender de saber o dia exato de divulgação de cada fonte.
  - `motores-mensais.yml` — motores de periodicidade trimestral ou mais espaçada (PIB Brasil, Desocupação, Posição na ocupação, Taxa de participação, SICONFI, PIB Mundial/FMI, Taxa de sindicalização). Mesma lógica: rodar mensalmente uma fonte trimestral é seguro.
- **Por que essa granularidade e não uma cron por fonte real**: os calendários de divulgação exatos (dia do mês/trimestre) não foram confirmados para todas as fontes neste Discovery — pesquisas mais frequentes que a periodicidade real são seguras e baratas (chamadas de API leves), então é preferível superamostrar a arriscar perder uma divulgação por errar a data exata.
- **Persistência do resultado (RAW)**: cada workflow publica `data/raw/` como **artifact do próprio GitHub Actions** (retenção padrão de 90 dias). Esta é uma escolha **mínima e reversível**, não a decisão definitiva de armazenamento — evita comprometer prematuramente a escolha de provedor de nuvem/banco de dados, que segue em aberto (`VISAO_DO_PRODUTO.md`, Seção 15).

## O que este ADR NÃO decide

- **Não escolhe o armazenamento definitivo do RAW/STAGING/CURATED** — artifacts do Actions são temporários (90 dias) e servem apenas para este piloto de agendamento, não para produção.
- **Não ativa o agendamento de fato** — os workflows só passam a rodar quando o repositório tiver um remoto no GitHub e os arquivos forem enviados (`git push`). Isso não foi feito automaticamente porque criar/configurar um remoto e publicar o repositório é uma ação visível externamente, que requer autorização explícita separada.
- **Não cobre os motores dos Grupos C/D/E** do Plano de Motores — CAGED (falta camada de agregação antes de fazer sentido agendar), UCI (incluído no semanal, mas com risco maior de quebra por ser raspagem), e os 6 indicadores sem motor possível (Grupo E) não entram em nenhum workflow.

## Consequências

- Assim que o repositório for publicado no GitHub (remoto configurado + push), os 3 workflows começam a rodar automaticamente nos horários definidos, sem ação manual adicional.
- Os `data/raw/` gerados em cada execução ficam disponíveis como artifacts por 90 dias — suficiente para validar o funcionamento contínuo, mas não para série histórica de longo prazo (isso depende da decisão de armazenamento definitivo).
- Falhas de execução (ex.: fonte fora do ar, mudança de layout) aparecem no painel de Actions do GitHub — não há alerta automático configurado nesta rodada (poderia ser adicionado depois, ex. notificação por e-mail/Slack em caso de falha).
