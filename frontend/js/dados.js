// DIEESE 360 — busca indicadores/indicadores_serie no Supabase, formata valores,
// calcula tendência e monta o HTML de cada cartão. Lido por index.html e
// painel.html. Depende de js/app.js (window.Painel.sb) já carregado antes.
(function () {
  'use strict';
  var P = window.Painel;
  var esc = P.esc;

  var DIMENSOES = {
    macroeconomia: { nome: 'Macroeconomia', descricao: 'Atividade econômica, comércio exterior, investimento e contas públicas: o quadro geral da economia brasileira.' },
    monetario_credito: { nome: 'Monetário e crédito', descricao: 'Juros, câmbio, crédito e endividamento das famílias.' },
    inflacao: { nome: 'Inflação', descricao: 'Índices de preços, cesta básica e combustíveis.' },
    mercado_trabalho: { nome: 'Mercado de trabalho', descricao: 'Emprego, rendimento, sindicalização, negociação coletiva e o Novo CAGED.' },
    mercados: { nome: 'Mercados financeiros', descricao: 'Índices de bolsa, ações da B3 e criptoativos, fechamento diário.' }
  };

  // O "Novo CAGED" deixou de ser dimensão de primeiro nível (2026-10-26, a
  // pedido do responsável do projeto: "não faz sentido colocar CAGED fora
  // do mercado de trabalho... coloca como uma subdimensão"). A coluna
  // `indicadores.dimensao` continua gravando 'caged' nas 2 séries (sem
  // migração/UPDATE no banco — subdimensão aqui é só apresentação, não um
  // fato novo sobre o dado) — esta função resolve qual dimensão de
  // primeiro nível usar para agrupar/filtrar/navegar.
  function dimensaoEfetiva(dimensaoBruta) {
    return dimensaoBruta === 'caged' ? 'mercado_trabalho' : dimensaoBruta;
  }

  // Subgrupo (subdimensão) de cada indicador dentro da sua dimensão efetiva
  // — só rótulo de exibição, reversível, sem afetar o catálogo no banco.
  // Indicador sem entrada aqui continua aparecendo solto, como antes deste
  // refinamento (2026-10-26). Levantamento feito a partir do catálogo real:
  // ver research/notas (se houver) ou o histórico desta sessão.
  var SUBGRUPOS = {
    // mercado_trabalho
    salario_medio_real_admissao_caged: 'Novo CAGED',
    salario_medio_real_desligamento_caged: 'Novo CAGED',
    rais_estoque_vinculos_ativos: 'RAIS',
    rais_rendimento_medio_dezembro: 'RAIS',
    ict_dieese: 'Negociação coletiva e sindicalismo',
    piso_salarial_medio: 'Negociação coletiva e sindicalismo',
    piso_salarial_mediano: 'Negociação coletiva e sindicalismo',
    reajustes_acima_inpc_pct: 'Negociação coletiva e sindicalismo',
    reajustes_abaixo_inpc_pct: 'Negociação coletiva e sindicalismo',
    greves_total_ano: 'Negociação coletiva e sindicalismo',
    greves_horas_paradas_ano: 'Negociação coletiva e sindicalismo',
    taxa_sindicalizacao: 'Negociação coletiva e sindicalismo',
    taxa_desocupacao: 'Emprego e renda (PNAD Contínua)',
    populacao_ocupada: 'Emprego e renda (PNAD Contínua)',
    rendimento_medio_real: 'Emprego e renda (PNAD Contínua)',
    taxa_participacao: 'Emprego e renda (PNAD Contínua)',
    desemprego_ilostat: 'Emprego e renda (PNAD Contínua)',

    // inflacao
    ipca: 'Índices de preços',
    inpc: 'Índices de preços',
    igpm: 'Índices de preços',
    ipca_numero_indice: 'Índices de preços',
    combustivel_gasolina: 'Combustíveis',
    combustivel_diesel: 'Combustíveis',
    combustivel_glp: 'Combustíveis',

    // macroeconomia
    balanca_exportacoes: 'Comércio exterior',
    balanca_importacoes: 'Comércio exterior',
    balanca_saldo: 'Comércio exterior',
    commodities_geral: 'Índice de Commodities Brasil',
    commodities_agropecuaria: 'Índice de Commodities Brasil',
    commodities_energia: 'Índice de Commodities Brasil',
    commodities_metal: 'Índice de Commodities Brasil',
    pib_brasil: 'Atividade econômica',
    pim_producao_industrial: 'Atividade econômica',
    pmc_volume_vendas: 'Atividade econômica',
    pms_volume_servicos: 'Atividade econômica',
    taxa_investimento: 'Atividade econômica',

    // monetario_credito
    juros_pf_cheque_especial: 'Juros por modalidade',
    juros_pf_credito_pessoal: 'Juros por modalidade',
    juros_pj_veiculos: 'Juros por modalidade',
    juros_pj_cartao_rotativo: 'Juros por modalidade',
    saldo_credito_sfn_total: 'Crédito do SFN',
    saldo_credito_sfn_pf: 'Crédito do SFN',
    saldo_credito_sfn_pj: 'Crédito do SFN',
    saldo_credito_sfn_recursos_direcionados: 'Crédito do SFN',
    saldo_credito_sfn_recursos_livres: 'Crédito do SFN',
    saldo_credito_sfn_livres_pf: 'Crédito do SFN',
    endividamento_familias_acumulado_12m: 'Endividamento das famílias',
    endividamento_familias_sem_imovel: 'Endividamento das famílias',
    comprometimento_renda_com_ajuste: 'Endividamento das famílias',
    comprometimento_renda_sem_ajuste: 'Endividamento das famílias',
    comprometimento_renda_sem_imovel: 'Endividamento das famílias',

    // mercados
    ibovespa: 'Índices',
    sp500: 'Índices',
    nasdaq: 'Índices',
    dow_jones: 'Índices',
    bitcoin: 'Criptoativos',
    ethereum: 'Criptoativos',
    petr4: 'Ações',
    vale3: 'Ações',
    itub4: 'Ações'
  };

  function subgrupoDoIndicador(indicadorId) {
    return SUBGRUPOS[indicadorId] || null;
  }

  // Mandatos presidenciais desde o início do Plano Real (01/07/1994) — usados
  // pela página "Dimensão Política" (politica.html) para desenhar marcadores
  // verticais nos gráficos de série histórica. Datas de posse/fim de mandato
  // são fato público, sem ambiguidade até 2023; a data de saída de Dilma
  // (31/08/2016, votação final do impeachment no Senado, mesmo dia em que
  // Temer assumiu em caráter definitivo) também é fato histórico público sem
  // ambiguidade. Período em curso (Lula, reeleito no 2º turno de 25/10/2026,
  // confirmado via TRE-SP) fica com `fim: null` — não presumir data de
  // término de um mandato ainda não iniciado.
  //
  // Um marcador por MANDATO individual (2026-10-26, pedido explícito do
  // responsável do projeto: "FHC I, FHC II, Lula I, Lula II... e assim por
  // diante"), substituindo o critério anterior de agrupar sucessão direta
  // num só marcador (ex. "Dilma/Temer") — esse critério anterior era
  // inspirado nos gráficos da Folha de S.Paulo usados como referência
  // inicial, mas o responsável do projeto pediu o recorte mais granular.
  var GOVERNOS = [
    { nome: 'Itamar Franco (pós-Real)', inicio: '1994-07-01', fim: '1995-01-01' },
    { nome: 'FHC I', inicio: '1995-01-01', fim: '1999-01-01' },
    { nome: 'FHC II', inicio: '1999-01-01', fim: '2003-01-01' },
    { nome: 'Lula I', inicio: '2003-01-01', fim: '2007-01-01' },
    { nome: 'Lula II', inicio: '2007-01-01', fim: '2011-01-01' },
    { nome: 'Dilma I', inicio: '2011-01-01', fim: '2015-01-01' },
    { nome: 'Dilma II', inicio: '2015-01-01', fim: '2016-08-31' },
    { nome: 'Temer', inicio: '2016-08-31', fim: '2019-01-01' },
    { nome: 'Bolsonaro', inicio: '2019-01-01', fim: '2023-01-01' },
    { nome: 'Lula III (em curso)', inicio: '2023-01-01', fim: null }
  ];

  // ------------------------------------------------------------------
  // Carregamento
  // ------------------------------------------------------------------
  function carregarIndicadores() {
    return P.sb.from('indicadores').select('*').order('ordem_exibicao').then(function (r) {
      if (r.error) throw r.error;
      return r.data || [];
    });
  }

  function carregarSerie(indicadorId, limite) {
    return P.sb.from('indicadores_serie').select('data_referencia, valor, metadata')
      .eq('indicador_id', indicadorId)
      .order('data_referencia', { ascending: false })
      .limit(limite || 24)
      .then(function (r) {
        if (r.error) throw r.error;
        return (r.data || []).slice().reverse(); // cronológico (mais antigo primeiro)
      });
  }

  // Busca a série de VÁRIOS indicadores numa única consulta, em vez de uma
  // consulta por indicador — a home tem 55 indicadores publicados, e 55
  // requisições em paralelo é o que deixava "Resumo do dia" preso em
  // "carregando" (relatado pelo responsável do projeto, 2026-10-14).
  //
  // Usa a função indicadores_serie_recentes (migração 0008), não uma
  // consulta direta à tabela: o PostgREST corta em 1.000 linhas por padrão,
  // e indicadores_serie já passa de 9.800 linhas no total — uma consulta
  // "in(...) order by data desc" sem essa function corta pelas 1.000 linhas
  // mais recentes DE TODA A CONSULTA, não 1.000 por indicador, derrubando
  // silenciosamente indicadores de periodicidade mais espaçada (anual,
  // quadrimestral) do ticker/carrossel. Achado em auditoria externa
  // (2026-10-15, item C08). A function faz o corte "últimos N por
  // indicador" no banco via window function — nunca depende de quantas
  // linhas o PostgREST decide devolver.
  function carregarSeriesPorIndicadores(indicadorIds, limitePorIndicador) {
    if (!indicadorIds.length) return Promise.resolve({});
    return P.sb.rpc('indicadores_serie_recentes', {
      p_indicador_ids: indicadorIds,
      p_limite: limitePorIndicador || 24
    }).then(function (r) {
      if (r.error) throw r.error;
      var porId = {};
      (r.data || []).forEach(function (linha) {
        (porId[linha.indicador_id] = porId[linha.indicador_id] || []).push(linha);
      });
      return porId; // já vem cronológico (mais antigo primeiro) da function
    });
  }

  // ------------------------------------------------------------------
  // Formatação
  // ------------------------------------------------------------------
  function formatarNumero(valor, casas) {
    return valor.toLocaleString('pt-BR', { minimumFractionDigits: casas, maximumFractionDigits: casas });
  }

  // Sem balde "mil": um salário de R$ 1.951 virando "R$ 2,0 mil" não é mais
  // legível, é menos preciso (perde os centavos) e lê estranho para uma
  // remuneração individual — achado em auditoria externa (2026-10-15, item
  // C03). Só compacta a partir de milhão, faixa em que BNDES/balança/saldo
  // de crédito realmente precisam de um número mais curto.
  function formatarCompacto(valor, casasPequenas) {
    var abs = Math.abs(valor);
    if (abs >= 1e9) return formatarNumero(valor / 1e9, 1) + ' bi';
    if (abs >= 1e6) return formatarNumero(valor / 1e6, 1) + ' mi';
    return formatarNumero(valor, casasPequenas == null ? 1 : casasPequenas);
  }

  // A unidade do catálogo decide o formato — ver migração 0002 para os valores
  // possíveis. Números grandes (R$/US$, ex. BNDES/balança) entram no formato
  // compacto; valores pequenos de moeda (ex. câmbio, ~R$ 5) usam 2 casas, para
  // não perder a precisão que importa numa cotação.
  //
  // "R$ milhões" (ver migração — unidade corrigida em 6 indicadores de saldo
  // de crédito do SFN, 2026-10-15, item C01): o valor bruto já vem em
  // milhões de reais na própria fonte (BCB/SGS) — formatarCompacto espera
  // reais, não milhões, então o valor precisa ser multiplicado de volta
  // antes de formatar, senão o número sai mil vezes menor que o real
  // (R$ 7,4 mi em vez de R$ 7,4 tri, o bug relatado pela auditoria).
  //
  // "%": 2 casas, não 1 — IPCA, Selic, taxa de desocupação etc. são
  // publicados pela fonte oficial com 2 casas; arredondar para 1 descarta
  // precisão real do dado (item C03).
  function formatarValor(indicador, valor) {
    var unidade = indicador.unidade || '';
    if (unidade.indexOf('%') >= 0) return formatarNumero(valor, 2) + '%';
    if (unidade.indexOf('R$ milhões') === 0) return 'R$ ' + formatarCompacto(valor * 1e6, 2);
    if (unidade.indexOf('R$') === 0) return 'R$ ' + formatarCompacto(valor, 2);
    if (unidade.indexOf('US$') === 0) return 'US$ ' + formatarCompacto(valor, 2);
    return formatarNumero(valor, Math.abs(valor) < 10 ? 2 : 1);
  }

  // Versão compacta da data, para eixo/tooltip do gráfico (não repete o
  // texto longo de formatarDataReferencia, que é para o cabeçalho do cartão).
  function formatarDataCurta(dataIso) {
    var d = new Date(dataIso + 'T00:00:00');
    return d.toLocaleDateString('pt-BR', { month: 'short', year: 'numeric' }).replace('.', '');
  }

  function formatarDataReferencia(dataIso, periodicidade) {
    var d = new Date(dataIso + 'T00:00:00');
    if (periodicidade === 'trimestral') {
      var tri = Math.floor(d.getMonth() / 3) + 1;
      return tri + 'º trimestre ' + d.getFullYear();
    }
    if (periodicidade === 'quadrimestral') {
      return d.toLocaleDateString('pt-BR', { month: 'long', year: 'numeric' });
    }
    return d.toLocaleDateString('pt-BR', { month: 'long', year: 'numeric' });
  }

  // ------------------------------------------------------------------
  // Tendência: compara o último ponto com o anterior, e decide se a seta é
  // "boa"/"ruim"/"neutra" conforme indicadores.direcao_positiva — ver nota na
  // migração 0002: é uma convenção de leitura, não um fato objetivo.
  // ------------------------------------------------------------------
  function calcularTendencia(indicador, serieAsc) {
    if (serieAsc.length < 2) return null;
    var atual = serieAsc[serieAsc.length - 1];
    var anterior = serieAsc[serieAsc.length - 2];
    var delta = atual.valor - anterior.valor;
    var direcaoMudanca = delta > 0 ? 'alta' : (delta < 0 ? 'baixa' : 'estavel');
    var classe = 'neutra';
    if (indicador.direcao_positiva === 'alta') classe = delta > 0 ? 'boa' : (delta < 0 ? 'ruim' : 'neutra');
    else if (indicador.direcao_positiva === 'baixa') classe = delta < 0 ? 'boa' : (delta > 0 ? 'ruim' : 'neutra');
    var seta = direcaoMudanca === 'alta' ? '▲' : (direcaoMudanca === 'baixa' ? '▼' : '—');
    return { delta: delta, direcaoMudanca: direcaoMudanca, classe: classe, seta: seta, anterior: anterior };
  }

  // Variação percentual entre os dois últimos pontos — só faz sentido para
  // indicador cuja unidade NÃO é "%": para R$, US$ ou índice, a variação
  // percentual compara preços/níveis igual a um ranking de ativos. Mantida
  // separada de calcularVariacao (abaixo) porque "percentual da percentual"
  // não é uma operação válida — ver nota em calcularVariacao.
  function calcularVariacaoPercentual(serieAsc) {
    if (serieAsc.length < 2) return null;
    var atual = serieAsc[serieAsc.length - 1];
    var anterior = serieAsc[serieAsc.length - 2];
    if (!anterior.valor) return null; // evita divisão por zero
    var percentual = ((atual.valor - anterior.valor) / Math.abs(anterior.valor)) * 100;
    return { percentual: percentual, atual: atual, anterior: anterior };
  }

  // Variação pronta para exibir, já escolhendo a unidade de comparação
  // correta conforme o tipo do indicador: quando o indicador JÁ é expresso
  // em % (taxa de juros, inflação do mês, taxa de desocupação etc.),
  // comparar em variação percentual seria "percentual da percentual" — uma
  // queda de -0,3% para 0,8% viraria uma alta de 356%, um número sem
  // leitura econômica (foi o que o responsável do projeto encontrou no
  // ticker do IPCA, 2026-10-14). Nesse caso a comparação correta é a
  // diferença em pontos percentuais (p.p.) entre os dois períodos. Para os
  // demais indicadores (R$, US$, índice, contagem), variação percentual
  // continua sendo a comparação certa.
  function calcularVariacao(indicador, serieAsc) {
    if (serieAsc.length < 2) return null;
    var anterior = serieAsc[serieAsc.length - 2];
    var ehPercentual = (indicador.unidade || '').indexOf('%') >= 0;
    if (ehPercentual) {
      var atual = serieAsc[serieAsc.length - 1];
      var pp = atual.valor - anterior.valor;
      return { valor: pp, sufixo: 'p.p.', direcao: pp > 0 ? 'alta' : (pp < 0 ? 'baixa' : 'neutra'), anterior: anterior };
    }
    var variacao = calcularVariacaoPercentual(serieAsc);
    if (!variacao) return null;
    return { valor: variacao.percentual, sufixo: '%', direcao: variacao.percentual > 0 ? 'alta' : (variacao.percentual < 0 ? 'baixa' : 'neutra'), anterior: anterior };
  }

  // Retorno % entre o ponto mais recente e o ponto mais próximo de N dias
  // corridos atrás — generaliza calcularVariacaoPercentual (que só compara
  // os dois últimos pontos) para qualquer janela de tempo. Usado na página
  // de mercados financeiros para expor retorno em 1 mês/YTD/12 meses sem
  // precisar abrir o gráfico (inspirado no seletor de período do Yahoo
  // Finance, que já mostra o retorno de cada janela no próprio botão — ver
  // research/notas/INVENTARIO_BENCHMARK_MERCADOS_FINANCEIROS.md, seção 6).
  // `serieAsc` precisa ter histórico suficiente para cobrir `dias`; se o
  // ponto mais antigo disponível for mais recente que a janela pedida,
  // devolve null em vez de comparar contra um "quase lá" enganoso.
  function calcularRetornoPeriodo(serieAsc, dias) {
    if (serieAsc.length < 2) return null;
    var atual = serieAsc[serieAsc.length - 1];
    var dataAtual = new Date(atual.data_referencia + 'T00:00:00');
    var alvo = new Date(dataAtual);
    alvo.setDate(alvo.getDate() - dias);
    var primeiro = new Date(serieAsc[0].data_referencia + 'T00:00:00');
    if (primeiro > alvo) return null; // histórico não cobre a janela pedida
    // Ponto com data mais próxima do alvo, sem passar dele (igual ou mais antigo).
    var base = serieAsc[0];
    for (var i = 0; i < serieAsc.length; i++) {
      var data = new Date(serieAsc[i].data_referencia + 'T00:00:00');
      if (data > alvo) break;
      base = serieAsc[i];
    }
    if (!base.valor) return null;
    var percentual = ((atual.valor - base.valor) / Math.abs(base.valor)) * 100;
    return { percentual: percentual, base: base, atual: atual };
  }

  // Média móvel simples dos últimos `janela` pontos da série (ex.: 20
  // pregões) — a mesma conta usada por qualquer site de mercado para
  // marcar se o preço atual está "acima" ou "abaixo" da própria média
  // recente. Sem histórico suficiente, devolve null (não estima com
  // menos pontos do que a janela pede).
  function calcularMediaMovel(serieAsc, janela) {
    if (serieAsc.length < janela) return null;
    var fatia = serieAsc.slice(serieAsc.length - janela);
    var soma = fatia.reduce(function (acc, p) { return acc + p.valor; }, 0);
    return soma / janela;
  }

  // Volatilidade: desvio padrão das variações percentuais diárias dentro
  // da janela pedida — a mesma métrica que a literatura de mercado usa
  // para medir o quanto um ativo oscila, independente da direção.
  function calcularVolatilidade(serieAsc, janela) {
    if (serieAsc.length < janela + 1) return null;
    var fatia = serieAsc.slice(serieAsc.length - janela - 1);
    var retornos = [];
    for (var i = 1; i < fatia.length; i++) {
      if (!fatia[i - 1].valor) continue;
      retornos.push((fatia[i].valor - fatia[i - 1].valor) / fatia[i - 1].valor);
    }
    if (retornos.length < 2) return null;
    var media = retornos.reduce(function (a, b) { return a + b; }, 0) / retornos.length;
    var variancia = retornos.reduce(function (acc, r) { return acc + Math.pow(r - media, 2); }, 0) / (retornos.length - 1);
    return Math.sqrt(variancia) * 100;
  }

  // Quantos pontos consecutivos, a partir do mais recente, mantêm a mesma
  // direção (alta ou baixa) — equivalente ao "streak" que corretoras e
  // sites de mercado mostram ao lado da cotação.
  function calcularSequencia(serieAsc) {
    if (serieAsc.length < 2) return null;
    var direcao = null, contagem = 0;
    for (var i = serieAsc.length - 1; i > 0; i--) {
      var diff = serieAsc[i].valor - serieAsc[i - 1].valor;
      var sinal = diff > 0 ? 'alta' : (diff < 0 ? 'baixa' : null);
      if (!sinal) break;
      if (direcao === null) direcao = sinal;
      if (sinal !== direcao) break;
      contagem++;
    }
    if (!direcao || contagem === 0) return null;
    return { direcao: direcao, dias: contagem };
  }

  // Posição do valor atual dentro da faixa [mínimo, máximo] — 0 = na
  // mínima, 100 = na máxima do período. Usado para comparar o preço de
  // hoje com a faixa de 52 semanas (ou qualquer outra janela).
  function calcularPosicaoFaixa(valorAtual, minimo, maximo) {
    if (minimo == null || maximo == null || maximo === minimo) return null;
    return ((valorAtual - minimo) / (maximo - minimo)) * 100;
  }

  // Comparações com as próprias métricas que a literatura de mercado usa
  // (média móvel, volatilidade, sequência de altas/baixas, posição na
  // faixa de 52 semanas) — pedido do responsável do projeto (2026-10-26):
  // "mostrar uma análise do que aconteceu fazendo comparações de acordo
  // com as métricas que a literatura usa". Cada frase sai só de número já
  // armazenado, sem narrativa sobre causa — não inventa motivo nem notícia,
  // só compara o dado de hoje com o próprio histórico do ativo. Atualiza
  // sozinho a cada novo ponto que a coleta diária publica, sem trabalho
  // manual.
  function montarComparacoesMercado(indicador, serieAsc) {
    if (serieAsc.length < 6) return [];
    var atual = serieAsc[serieAsc.length - 1];
    var frases = [];

    var sma20 = calcularMediaMovel(serieAsc, 20);
    if (sma20) {
      var diff = ((atual.valor - sma20) / sma20) * 100;
      if (Math.abs(diff) < 0.05) {
        frases.push('Preço praticamente na média móvel de 20 pregões (' + formatarValor(indicador, sma20) + ')');
      } else {
        frases.push('Preço ' + formatarNumero(Math.abs(diff), 1) + '% ' + (diff > 0 ? 'acima' : 'abaixo') + ' da média móvel de 20 pregões (' + formatarValor(indicador, sma20) + ')');
      }
    }

    var vol30 = calcularVolatilidade(serieAsc, 30);
    if (vol30 != null) {
      frases.push('Volatilidade diária nos últimos 30 pregões: ' + formatarNumero(vol30, 1) + '%');
    }

    var seq = calcularSequencia(serieAsc);
    if (seq && seq.dias >= 2) {
      frases.push(seq.dias + ' pregões seguidos em ' + seq.direcao);
    }

    var meta = atual.metadata || {};
    var posFaixa = calcularPosicaoFaixa(atual.valor, meta.minima_52_semanas, meta.maxima_52_semanas);
    if (posFaixa != null) {
      frases.push('A ' + formatarNumero(Math.max(0, Math.min(100, posFaixa)), 0) + '% da faixa entre mínima e máxima de 52 semanas');
    }

    return frases;
  }

  // ------------------------------------------------------------------
  // Sparkline — SVG inline. Linha 2px suavizada (curva Catmull-Rom, não
  // segmentos retos entre pontos — fica menos "serrilhada" com poucos
  // pontos mensais/trimestrais) + área em degradê + ponto final >=8px com
  // anel branco (mesma linguagem do ponto final do gráfico grande, ver
  // js/grafico-linha.js). O traçado da linha é "desenhado" por
  // animacao-dash.js via stroke-dasharray (funciona igual com curva, usa
  // path.getTotalLength(), agnóstico ao tipo de comando do path).
  // ------------------------------------------------------------------
  var _sparklineSeq = 0;
  function _curvaSuave(pontosXY) {
    if (pontosXY.length < 3) {
      return pontosXY.map(function (p, i) { return (i === 0 ? 'M' : 'L') + p[0].toFixed(1) + ',' + p[1].toFixed(1); }).join(' ');
    }
    var d = 'M' + pontosXY[0][0].toFixed(1) + ',' + pontosXY[0][1].toFixed(1);
    for (var i = 0; i < pontosXY.length - 1; i++) {
      var p0 = pontosXY[i - 1] || pontosXY[i];
      var p1 = pontosXY[i];
      var p2 = pontosXY[i + 1];
      var p3 = pontosXY[i + 2] || p2;
      var c1x = p1[0] + (p2[0] - p0[0]) / 6, c1y = p1[1] + (p2[1] - p0[1]) / 6;
      var c2x = p2[0] - (p3[0] - p1[0]) / 6, c2y = p2[1] - (p3[1] - p1[1]) / 6;
      d += ' C' + c1x.toFixed(1) + ',' + c1y.toFixed(1) + ' ' + c2x.toFixed(1) + ',' + c2y.toFixed(1) + ' ' + p2[0].toFixed(1) + ',' + p2[1].toFixed(1);
    }
    return d;
  }
  function montarSparkline(serieAsc) {
    var L = 120, A = 36, M = 4;
    if (serieAsc.length < 2) return '';
    var valores = serieAsc.map(function (p) { return p.valor; });
    var min = Math.min.apply(null, valores), max = Math.max.apply(null, valores);
    var amplitude = (max - min) || 1;
    var passo = (L - M * 2) / (serieAsc.length - 1);
    var pontosXY = valores.map(function (v, i) {
      var x = M + i * passo;
      var y = A - M - ((v - min) / amplitude) * (A - M * 2);
      return [x, y];
    });
    var linha = _curvaSuave(pontosXY);
    var ultimo = pontosXY[pontosXY.length - 1];
    var area = linha + ' L' + ultimo[0].toFixed(1) + ',' + (A - M) + ' L' + pontosXY[0][0].toFixed(1) + ',' + (A - M) + ' Z';
    var gid = 'spark-grad-' + (_sparklineSeq++);
    return (
      '<svg class="cartao-sparkline" viewBox="0 0 ' + L + ' ' + A + '" preserveAspectRatio="none" aria-hidden="true">' +
      '<defs><linearGradient id="' + gid + '" x1="0" y1="0" x2="0" y2="1">' +
      '<stop offset="0%" stop-color="currentColor" stop-opacity=".22"></stop>' +
      '<stop offset="100%" stop-color="currentColor" stop-opacity="0"></stop>' +
      '</linearGradient></defs>' +
      '<path class="area" d="' + area + '" style="fill:url(#' + gid + ')"></path>' +
      '<path class="linha" d="' + linha + '"></path>' +
      '<circle class="ponto" cx="' + ultimo[0].toFixed(1) + '" cy="' + ultimo[1].toFixed(1) + '" r="3.2"></circle>' +
      '</svg>'
    );
  }

  // ------------------------------------------------------------------
  // Cartão-resumo (stat tile): número + tendência + sparkline. É um link de
  // verdade para a página própria do indicador (indicador.html?id=...) — ver
  // js/pagina-indicador.js — não um modal: cada indicador tem sua URL,
  // navegável e compartilhável, como nos grandes portais de estatística.
  // ------------------------------------------------------------------
  function montarCartao(indicador, serieAsc) {
    if (!serieAsc.length) return montarCartaoVazio(indicador);
    var atual = serieAsc[serieAsc.length - 1];
    var tendencia = calcularTendencia(indicador, serieAsc);
    var chip = tendencia
      ? '<span class="chip-tendencia ' + tendencia.classe + '">' + tendencia.seta + ' ' + formatarValor(indicador, Math.abs(tendencia.delta)) + '</span>'
      : '';

    return (
      '<article class="cartao-resumo">' +
      '<a class="cartao-resumo-botao" href="indicador.html?id=' + esc(indicador.id) + '" aria-label="' + esc(indicador.nome) + ', ver página completa, gráfico e tabela">' +
      '<div class="cartao-cabecalho"><span class="cartao-rotulo">' + esc(indicador.nome) + '</span>' + chip + '</div>' +
      '<strong class="cartao-valor">' + formatarValor(indicador, atual.valor) + '</strong>' +
      '<span class="cartao-data">' + esc(formatarDataReferencia(atual.data_referencia, indicador.periodicidade)) + '</span>' +
      montarSparkline(serieAsc) +
      '<span class="cartao-dica">ver indicador →</span>' +
      '</a>' +
      '</article>'
    );
  }

  function montarCartaoVazio(indicador) {
    return (
      '<article class="cartao-pendente">' +
      '<strong>' + esc(indicador.nome) + '</strong>' +
      '<p style="margin-top:8px">Catalogado, sem pontos publicados ainda.</p>' +
      '</article>'
    );
  }

  function montarCartaoDimensaoPendente(dimensao) {
    var info = DIMENSOES[dimensao] || { nome: dimensao };
    return (
      '<div class="cartao-pendente" style="grid-column:1/-1">' +
      '<strong>' + esc(info.nome) + ' ainda não tem indicadores publicados no painel.</strong>' +
      '<p style="margin-top:8px">Os motores de coleta desta dimensão já rodam. Falta a camada de transformação para o painel (ver ADR 0005).</p>' +
      '</div>'
    );
  }

  // ------------------------------------------------------------------
  // Ticker de topo — faixa fina com uma linha só por item (nome, valor,
  // variação), estilo portal de dados de mercado. Usa calcularVariacao, que
  // já escolhe p.p. ou % conforme a unidade do indicador — ver nota lá.
  // ------------------------------------------------------------------
  function montarItemTicker(indicador, serieAsc) {
    if (!serieAsc.length) return '';
    var atual = serieAsc[serieAsc.length - 1];
    var variacao = calcularVariacao(indicador, serieAsc);
    var seta = !variacao ? '—' : (variacao.direcao === 'alta' ? '▲' : (variacao.direcao === 'baixa' ? '▼' : '—'));
    // "vs. <período>" explícito ao lado da variação — sem isso não dá pra
    // saber contra o que o indicador está sendo comparado (pedido do
    // responsável do projeto, 2026-10-14).
    var vsPeriodo = variacao ? 'vs. ' + formatarDataReferencia(variacao.anterior.data_referencia, indicador.periodicidade) : '';
    return (
      '<span class="ticker-topo-item" title="' + esc(vsPeriodo) + '">' +
      '<span class="nome">' + esc(indicador.nome) + '</span>' +
      '<span class="valor">' + esc(formatarValor(indicador, atual.valor)) + '</span>' +
      (variacao ? '<span class="delta ' + esc(variacao.direcao) + '">' + seta + ' ' + formatarNumero(Math.abs(variacao.valor), 1) + ' ' + esc(variacao.sufixo) + '</span>' : '') +
      (vsPeriodo ? '<span class="vs-periodo">' + esc(vsPeriodo) + '</span>' : '') +
      '</span>'
    );
  }

  window.DIEESE360 = window.DIEESE360 || {};
  window.DIEESE360.dados = {
    DIMENSOES: DIMENSOES,
    dimensaoEfetiva: dimensaoEfetiva,
    subgrupoDoIndicador: subgrupoDoIndicador,
    GOVERNOS: GOVERNOS,
    carregarIndicadores: carregarIndicadores,
    carregarSerie: carregarSerie,
    carregarSeriesPorIndicadores: carregarSeriesPorIndicadores,
    formatarValor: formatarValor,
    formatarNumero: formatarNumero,
    formatarDataReferencia: formatarDataReferencia,
    formatarDataCurta: formatarDataCurta,
    calcularTendencia: calcularTendencia,
    calcularVariacaoPercentual: calcularVariacaoPercentual,
    calcularVariacao: calcularVariacao,
    calcularRetornoPeriodo: calcularRetornoPeriodo,
    calcularMediaMovel: calcularMediaMovel,
    calcularVolatilidade: calcularVolatilidade,
    calcularSequencia: calcularSequencia,
    calcularPosicaoFaixa: calcularPosicaoFaixa,
    montarComparacoesMercado: montarComparacoesMercado,
    montarCartao: montarCartao,
    montarCartaoVazio: montarCartaoVazio,
    montarCartaoDimensaoPendente: montarCartaoDimensaoPendente,
    montarItemTicker: montarItemTicker,
    montarSparkline: montarSparkline
  };
})();
