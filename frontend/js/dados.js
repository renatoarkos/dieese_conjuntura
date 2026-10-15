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
    mercado_trabalho: { nome: 'Mercado de trabalho', descricao: 'Emprego, rendimento, sindicalização e negociação coletiva.' },
    caged: { nome: 'Novo CAGED', descricao: 'Admissões e desligamentos formais, por microdado.' }
  };

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

  // ------------------------------------------------------------------
  // Sparkline — SVG inline. Linha 2px + área a 8% de opacidade + ponto final
  // >=8px (ver skill de dataviz, marks-and-anatomy). O traçado da linha é
  // "desenhado" por animacao-dash.js via stroke-dasharray.
  // ------------------------------------------------------------------
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
    var linha = pontosXY.map(function (p, i) { return (i === 0 ? 'M' : 'L') + p[0].toFixed(1) + ',' + p[1].toFixed(1); }).join(' ');
    var ultimo = pontosXY[pontosXY.length - 1];
    var area = linha + ' L' + ultimo[0].toFixed(1) + ',' + (A - M) + ' L' + pontosXY[0][0].toFixed(1) + ',' + (A - M) + ' Z';
    return (
      '<svg class="cartao-sparkline" viewBox="0 0 ' + L + ' ' + A + '" preserveAspectRatio="none" aria-hidden="true">' +
      '<path class="area" d="' + area + '"></path>' +
      '<path class="linha" d="' + linha + '"></path>' +
      '<circle cx="' + ultimo[0].toFixed(1) + '" cy="' + ultimo[1].toFixed(1) + '" r="3"></circle>' +
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
    carregarIndicadores: carregarIndicadores,
    carregarSerie: carregarSerie,
    carregarSeriesPorIndicadores: carregarSeriesPorIndicadores,
    formatarValor: formatarValor,
    formatarDataReferencia: formatarDataReferencia,
    formatarDataCurta: formatarDataCurta,
    calcularTendencia: calcularTendencia,
    calcularVariacaoPercentual: calcularVariacaoPercentual,
    calcularVariacao: calcularVariacao,
    montarCartao: montarCartao,
    montarCartaoVazio: montarCartaoVazio,
    montarCartaoDimensaoPendente: montarCartaoDimensaoPendente,
    montarItemTicker: montarItemTicker,
    montarSparkline: montarSparkline
  };
})();
