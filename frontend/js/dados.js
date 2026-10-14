// DIEESE 360 — busca indicadores/indicadores_serie no Supabase, formata valores,
// calcula tendência e monta o HTML de cada cartão. Lido por index.html e
// painel.html. Depende de js/app.js (window.Painel.sb) já carregado antes.
(function () {
  'use strict';
  var P = window.Painel;
  var esc = P.esc;

  var DIMENSOES = {
    macroeconomia: { nome: 'Macroeconomia', descricao: 'Atividade econômica, comércio exterior, investimento e contas públicas — o quadro geral da economia brasileira.' },
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

  // ------------------------------------------------------------------
  // Formatação
  // ------------------------------------------------------------------
  function formatarNumero(valor, casas) {
    return valor.toLocaleString('pt-BR', { minimumFractionDigits: casas, maximumFractionDigits: casas });
  }

  function formatarCompacto(valor, casasPequenas) {
    var abs = Math.abs(valor);
    if (abs >= 1e9) return formatarNumero(valor / 1e9, 1) + ' bi';
    if (abs >= 1e6) return formatarNumero(valor / 1e6, 1) + ' mi';
    if (abs >= 1e3) return formatarNumero(valor / 1e3, 1) + ' mil';
    return formatarNumero(valor, casasPequenas == null ? 1 : casasPequenas);
  }

  // A unidade do catálogo decide o formato — ver migração 0002 para os valores
  // possíveis. Números grandes (R$/US$, ex. BNDES/balança) entram no formato
  // compacto; valores pequenos de moeda (ex. câmbio, ~R$ 5) usam 2 casas, para
  // não perder a precisão que importa numa cotação — os demais mostram 1 casa.
  function formatarValor(indicador, valor) {
    var unidade = indicador.unidade || '';
    if (unidade.indexOf('%') >= 0) return formatarNumero(valor, 1) + '%';
    if (unidade.indexOf('R$') === 0) return 'R$ ' + formatarCompacto(valor, 2);
    if (unidade.indexOf('US$') === 0) return 'US$ ' + formatarCompacto(valor, 2);
    return formatarNumero(valor, 1);
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
      '<a class="cartao-resumo-botao" href="indicador.html?id=' + esc(indicador.id) + '" aria-label="' + esc(indicador.nome) + ' — ver página completa, gráfico e tabela">' +
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
      '<p style="margin-top:8px">Os motores de coleta desta dimensão já rodam — falta a camada de transformação para o painel (ver ADR 0005).</p>' +
      '</div>'
    );
  }

  // ------------------------------------------------------------------
  // Ticker — indicadores de atualização mais frequente (periodicidade mensal).
  // ------------------------------------------------------------------
  function montarItemTicker(indicador, serieAsc) {
    if (!serieAsc.length) return '';
    var atual = serieAsc[serieAsc.length - 1];
    var tendencia = calcularTendencia(indicador, serieAsc);
    var classeSeta = tendencia ? (tendencia.direcaoMudanca === 'baixa' ? 'baixa' : (tendencia.direcaoMudanca === 'alta' ? 'alta' : 'neutra')) : 'neutra';
    var periodo = formatarDataReferencia(atual.data_referencia, indicador.periodicidade);
    var comparacao = tendencia
      ? 'vs. ' + formatarDataReferencia(tendencia.anterior.data_referencia, indicador.periodicidade)
      : 'sem período anterior';
    return (
      '<span class="ticker-item">' +
      '<span class="rotulo">' + esc(indicador.nome) + '</span>' +
      '<span class="ticker-linha1">' +
      '<span class="valor">' + formatarValor(indicador, atual.valor) + '</span>' +
      (tendencia ? '<span class="delta ' + classeSeta + '">' + tendencia.seta + ' ' + formatarValor(indicador, Math.abs(tendencia.delta)) + '</span>' : '') +
      '</span>' +
      '<span class="ticker-linha2">' + esc(periodo) + ' · ' + esc(comparacao) + '</span>' +
      '</span>'
    );
  }

  window.DIEESE360 = window.DIEESE360 || {};
  window.DIEESE360.dados = {
    DIMENSOES: DIMENSOES,
    carregarIndicadores: carregarIndicadores,
    carregarSerie: carregarSerie,
    formatarValor: formatarValor,
    formatarDataReferencia: formatarDataReferencia,
    formatarDataCurta: formatarDataCurta,
    calcularTendencia: calcularTendencia,
    montarCartao: montarCartao,
    montarCartaoVazio: montarCartaoVazio,
    montarCartaoDimensaoPendente: montarCartaoDimensaoPendente,
    montarItemTicker: montarItemTicker,
    montarSparkline: montarSparkline
  };
})();
