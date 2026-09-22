DIEESE CONJUNTURA
Plataforma de Inteligência Socioeconômica
Este repositório contém o projeto DIEESE Conjuntura.
O objetivo é desenvolver uma plataforma permanente de coleta, tratamento, armazenamento, análise, visualização e interpretação de dados econômicos e socioeconômicos destinados à análise de conjuntura.
REGRA PRINCIPAL
Antes de executar qualquer tarefa relevante neste repositório:

1. leia este arquivo;
2. identifique a fase atual do projeto;
3. consulte a documentação relacionada;
4. examine implementações existentes antes de criar novas;
5. preserve rastreabilidade;
6. não faça alterações destrutivas sem autorização.

FONTE DE VERDADE
Decisões permanentes pertencem ao repositório e não somente às conversas com assistentes de IA.
A memória de chats é auxiliar.
Documentação versionada é a fonte de verdade para decisões consolidadas.
PRINCÍPIOS

* Priorize fontes oficiais e primárias.
* Não invente dados.
* Não invente fontes.
* Não invente APIs ou endpoints.
* Não invente datas de divulgação.
* Todo indicador deve possuir metadados.
* Toda transformação deve ser reproduzível.
* Diferencie dado, evidência, hipótese e interpretação.
* Correlação não implica causalidade.
* Preserve perspectivas econômicas concorrentes quando relevantes.
* Não escolha tecnologia antes de compreender os requisitos.
* Documente decisões importantes.

DADOS
A arquitetura conceitual é:
RAW → STAGING → CURATED → ANALYTICS → APPLICATION/API.
RAW
Dados recebidos diretamente das fontes.
Não editar manualmente.
STAGING
Dados submetidos a padronização e preparação inicial.
CURATED
Dados tratados, validados e semanticamente organizados.
ANALYTICS
Indicadores, agregações, transformações, modelos e resultados analíticos.
APPLICATION/API
Camada consumida pela plataforma e demais aplicações.
MATERIAIS ORIGINAIS
Arquivos fornecidos pelo DIEESE ou utilizados como referência devem permanecer preservados.
Nunca sobrescreva um material original.
DESENVOLVIMENTO
Antes de implementar:

1. compreender;
2. pesquisar;
3. especificar;
4. planejar;
5. implementar;
6. testar;
7. validar;
8. documentar.

Não reescreva código funcional sem justificativa.
Prefira mudanças incrementais.
PESQUISA
Para informações atuais:

* pesquise;
* priorize fontes oficiais;
* registre fontes;
* registre data de consulta quando relevante;
* diferencie informação primária de interpretação secundária.

ECONOMIA
A análise deve considerar perspectivas ortodoxas e heterodoxas.
Nenhuma teoria deve ser automaticamente tratada como verdade empírica.
Relações econômicas devem ser investigadas utilizando dados, especificações e métodos adequados.
ESTATÍSTICA
Não aplique métodos mecanicamente.
Verifique pressupostos.
Considere:

* estacionariedade;
* sazonalidade;
* defasagens;
* quebras estruturais;
* endogeneidade;
* causalidade reversa;
* revisões;
* comparabilidade temporal.

SEGURANÇA
Nunca versione:

* senhas;
* tokens;
* API keys;
* credenciais;
* arquivos .env contendo segredos.

Nunca realize operação destrutiva sem autorização explícita.
DOCUMENTAÇÃO
Atualize documentação quando houver:

* nova fonte;
* novo indicador;
* nova metodologia;
* mudança metodológica;
* nova relação econômica;
* decisão arquitetural;
* limitação importante;
* alteração relevante de escopo.

ADR
Decisões arquiteturais importantes deverão ser registradas em:
docs/08-decisoes-adr/
Não substitua uma decisão arquitetural consolidada sem:

1. consultar o ADR anterior;
2. explicar por que precisa mudar;
3. registrar nova decisão.

FASE ATUAL
O projeto encontra-se inicialmente em:
DISCOVERY → PESQUISA → REQUISITOS → ARQUITETURA.
Não iniciar desenvolvimento substancial da aplicação sem autorização.
DEFINITION OF DONE
Uma tarefa relevante não está concluída simplesmente porque código ou documento foi criado.
Verifique:

* resultado;
* consistência;
* fontes;
* testes quando aplicáveis;
* documentação;
* rastreabilidade;
* impactos sobre componentes existentes.

AO FINAL DE CADA TAREFA RELEVANTE
Informe:

1. o que foi analisado;
2. o que foi criado;
3. o que foi alterado;
4. quais arquivos foram afetados;
5. quais fontes foram utilizadas;
6. quais decisões foram tomadas;
7. quais dúvidas permanecem;
8. qual é o próximo passo recomendado.
