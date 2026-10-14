// Orquestração da página inicial pública (index.html): ticker de topo,
// resumo do dia (indicador em destaque + maiores variações) e um carrossel
// por dimensão com todos os indicadores publicados. Não exige sessão — os
// números são públicos (ver ADR 0005); só a navegação completa fica atrás
// do login.
(function () {
  'use strict';
  var P = window.Painel;
  var D = window.DIEESE360.dados;
  var esc = P.esc;

  var ORDEM_DIMENSOES = ['macroeconomia', 'monetario_credito', 'inflacao', 'mercado_trabalho', 'caged'];

  var ICONES_DIMENSAO = {
    macroeconomia: 'assets/dimensoes/icone-macroeconomia.png',
    monetario_credito: 'assets/dimensoes/icone-monetario-credito.png',
    inflacao: 'assets/dimensoes/icone-inflacao.png',
    mercado_trabalho: 'assets/dimensoes/icone-mercado-trabalho.png',
    caged: 'assets/dimensoes/icone-caged.png'
  };

  // Texto mais completo por dimensão (o que é, o que cobre, por que importa
  // para a leitura de conjuntura) — complementa a descrição de uma linha já
  // usada em D.DIMENSOES (essa continua servindo o resumo rápido da grade).
  var TEXTO_DIMENSAO = {
    macroeconomia: 'Reúne os indicadores que descrevem o ritmo geral da economia brasileira: Produto Interno Bruto, comércio exterior, investimento, preços de commodities e contas públicas. É a base para situar qualquer leitura setorial dentro do ciclo econômico em curso.',
    monetario_credito: 'Cobre a taxa básica de juros, as taxas cobradas ao tomador final, o crédito concedido pelo sistema financeiro e o endividamento das famílias. Mostra como a política monetária se transmite ao custo do dinheiro no dia a dia de empresas e trabalhadores.',
    inflacao: 'Acompanha os principais índices de preços ao consumidor (IPCA, INPC, IGP-M) e itens sensíveis ao orçamento familiar, como combustíveis. É o contraponto necessário para ler qualquer variação nominal de salário ou renda em termos reais.',
    mercado_trabalho: 'Reúne emprego, desocupação, rendimento, sindicalização e negociação coletiva: o núcleo da pauta histórica do DIEESE, onde a pesquisa socioeconômica se conecta diretamente à atuação sindical.',
    caged: 'Admissões e desligamentos formais apurados por microdado todo mês, com granularidade menor que a RAIS anual. Antecipa movimentos do mercado de trabalho formal entre uma apuração anual e outra.'
  };

  // Indicadores que compõem o ticker de topo: um recorte entre dimensões,
  // priorizando os de atualização mais frequente.
  var TICKER = ['selic', 'cambio_dolar', 'ipca', 'commodities_geral', 'balanca_saldo', 'taxa_desocupacao', 'bndes_desembolsos'];
  // Indicador em destaque no resumo do dia.
  var DESTAQUE = 'cambio_dolar';

  function montarGradeDimensoes() {
    var alvo = document.getElementById('grade-dimensoes');
    var html = '';
    var i = 1;
    Object.keys(D.DIMENSOES).forEach(function (chave) {
      var dim = D.DIMENSOES[chave];
      var icone = ICONES_DIMENSAO[chave] || '';
      html += '<a class="cartao-dimensao" href="#dimensao-' + esc(chave) + '">' +
        '<div class="cartao-dimensao-topo">' +
        '<span class="num">Dimensão ' + (i++) + '</span>' +
        (icone ? '<img src="' + esc(icone) + '" alt="" class="cartao-dimensao-icone" width="48" height="48" loading="lazy">' : '') +
        '</div>' +
        '<h3>' + esc(dim.nome) + '</h3>' +
        '<p>' + esc(dim.descricao) + '</p>' +
        '</a>';
    });
    alvo.innerHTML = html;
  }

  function montarTicker(indicadores, series) {
    var alvo = document.getElementById('ticker-trilho');
    var itens = TICKER.map(function (id) {
      var indicador = indicadores.filter(function (i) { return i.id === id; })[0];
      return indicador ? D.montarItemTicker(indicador, series[id] || []) : '';
    }).filter(Boolean);
    if (!itens.length) { alvo.innerHTML = '<span class="ticker-topo-item">Sem indicadores publicados ainda.</span>'; return; }
    // Duplica a lista para o loop de rolagem ficar contínuo (ver @keyframes ticker-rola, translateX(-50%)).
    alvo.innerHTML = itens.join('') + itens.join('');
  }

  // Tabela de maiores variações: calcula a variação percentual do último
  // ponto sobre o anterior para todo indicador com dados suficientes,
  // ordena e separa as maiores altas das maiores baixas.
  function montarListaVariacoes(indicadores, series, direcao, limite) {
    var linhas = indicadores.map(function (ind) {
      var variacao = D.calcularVariacaoPercentual(series[ind.id] || []);
      return variacao ? { indicador: ind, percentual: variacao.percentual } : null;
    }).filter(Boolean);
    linhas = linhas.filter(function (l) { return direcao === 'alta' ? l.percentual > 0 : l.percentual < 0; });
    linhas.sort(function (a, b) { return Math.abs(b.percentual) - Math.abs(a.percentual); });
    linhas = linhas.slice(0, limite);
    if (!linhas.length) return '<li><span class="nome">Nenhuma variação ' + (direcao === 'alta' ? 'positiva' : 'negativa') + ' no período.</span></li>';
    return linhas.map(function (l) {
      return '<li><a href="indicador.html?id=' + esc(l.indicador.id) + '">' +
        '<span class="nome">' + esc(l.indicador.nome) + '</span>' +
        '<span class="percentual ' + direcao + '">' + (direcao === 'alta' ? '▲' : '▼') + ' ' + Math.abs(l.percentual).toFixed(1) + '%</span>' +
        '</a></li>';
    }).join('');
  }

  function montarResumoDia(indicadores, series) {
    var alvo = document.getElementById('resumo-dia');
    var destaque = indicadores.filter(function (i) { return i.id === DESTAQUE; })[0];
    var serieDestaque = destaque ? (series[destaque.id] || []) : [];

    alvo.innerHTML =
      '<div class="resumo-destaque" id="resumo-destaque-grafico"></div>' +
      '<div class="resumo-variacoes">' +
      '<div><h3>Maiores altas</h3><ul class="resumo-variacoes-lista">' + montarListaVariacoes(indicadores, series, 'alta', 5) + '</ul></div>' +
      '<div><h3>Maiores baixas</h3><ul class="resumo-variacoes-lista">' + montarListaVariacoes(indicadores, series, 'baixa', 5) + '</ul></div>' +
      '</div>';

    var caixaDestaque = document.getElementById('resumo-destaque-grafico');
    if (!destaque || serieDestaque.length < 2) {
      caixaDestaque.innerHTML = '<p class="aviso demo">Indicador em destaque sem pontos suficientes ainda.</p>';
      return;
    }
    var atual = serieDestaque[serieDestaque.length - 1];
    var tendencia = D.calcularTendencia(destaque, serieDestaque);
    var chip = tendencia
      ? '<span class="chip-tendencia ' + tendencia.classe + '">' + tendencia.seta + ' ' + esc(D.formatarValor(destaque, Math.abs(tendencia.delta))) + '</span>'
      : '';
    caixaDestaque.innerHTML =
      '<div class="resumo-destaque-topo">' +
      '<span class="resumo-destaque-rotulo">' + esc(destaque.nome) + '</span>' + chip +
      '</div>' +
      '<strong class="resumo-destaque-valor">' + esc(D.formatarValor(destaque, atual.valor)) + '</strong>' +
      '<p class="resumo-destaque-data">' + esc(D.formatarDataReferencia(atual.data_referencia, destaque.periodicidade)) + '</p>' +
      '<div class="resumo-destaque-grafico-area"></div>' +
      '<a class="link-editorial" href="indicador.html?id=' + esc(destaque.id) + '">Ver série completa →</a>';
    window.DIEESE360.montarGraficoLinha(
      caixaDestaque.querySelector('.resumo-destaque-grafico-area'),
      serieDestaque,
      {
        formatarValor: function (v) { return D.formatarValor(destaque, v); },
        formatarData: D.formatarDataCurta
      }
    );
  }

  function ligarSetasCarrossel(trilho, setaAnterior, setaProxima) {
    function atualizarEstado() {
      setaAnterior.disabled = trilho.scrollLeft <= 4;
      setaProxima.disabled = trilho.scrollLeft >= trilho.scrollWidth - trilho.clientWidth - 4;
    }
    function largurapasso() {
      var item = trilho.querySelector('.carrossel-item');
      return item ? item.getBoundingClientRect().width + 16 : trilho.clientWidth;
    }
    setaAnterior.addEventListener('click', function () { trilho.scrollBy({ left: -largurapasso(), behavior: 'smooth' }); });
    setaProxima.addEventListener('click', function () { trilho.scrollBy({ left: largurapasso(), behavior: 'smooth' }); });
    trilho.addEventListener('scroll', atualizarEstado);
    atualizarEstado();
  }

  function montarSecoesDimensao(indicadoresPorDimensao, series) {
    var raiz = document.getElementById('secoes-dimensao-home');
    var html = ORDEM_DIMENSOES.map(function (chave) {
      var dim = D.DIMENSOES[chave];
      var icone = ICONES_DIMENSAO[chave] || '';
      return (
        '<section class="secao carrossel-dimensao" id="dimensao-' + esc(chave) + '">' +
        '<div class="container">' +
        '<div class="carrossel-cabecalho">' +
        '<div>' +
        '<div class="secao-dimensao-topo">' +
        (icone ? '<img src="' + esc(icone) + '" alt="" class="secao-dimensao-icone" width="40" height="40" loading="lazy">' : '') +
        '<h2>' + esc(dim.nome) + '</h2>' +
        '</div>' +
        '<p class="lead">' + esc(TEXTO_DIMENSAO[chave] || dim.descricao) + '</p>' +
        '</div>' +
        '<div class="carrossel-setas">' +
        '<button type="button" class="carrossel-seta" id="seta-ant-' + esc(chave) + '" aria-label="Indicador anterior de ' + esc(dim.nome) + '">‹</button>' +
        '<button type="button" class="carrossel-seta" id="seta-prox-' + esc(chave) + '" aria-label="Próximo indicador de ' + esc(dim.nome) + '">›</button>' +
        '</div>' +
        '</div>' +
        '<div class="carrossel-trilho" id="carrossel-' + esc(chave) + '"></div>' +
        '</div>' +
        '</section>'
      );
    }).join('');
    raiz.innerHTML = html;

    ORDEM_DIMENSOES.forEach(function (chave) {
      var trilho = document.getElementById('carrossel-' + chave);
      var indicadoresDim = indicadoresPorDimensao[chave] || [];
      if (!indicadoresDim.length) {
        trilho.innerHTML = D.montarCartaoDimensaoPendente(chave);
        return;
      }
      trilho.innerHTML = indicadoresDim.map(function (ind) {
        return '<div class="carrossel-item">' + window.DIEESE360.montarCartaoFlip(ind, series[ind.id] || []) + '</div>';
      }).join('');
      window.DIEESE360.ligarCartoesFlip(trilho);
      ligarSetasCarrossel(trilho, document.getElementById('seta-ant-' + chave), document.getElementById('seta-prox-' + chave));
    });
  }

  function iniciar() {
    montarGradeDimensoes();
    if (!P.sb) {
      document.getElementById('resumo-dia').innerHTML = '<p class="aviso demo">Não foi possível conectar ao Supabase. Confira js/config.js.</p>';
      return;
    }
    D.carregarIndicadores().then(function (indicadores) {
      var ids = indicadores.map(function (i) { return i.id; });
      return Promise.all(ids.map(function (id) { return D.carregarSerie(id, 24); }))
        .then(function (listas) {
          var series = {};
          ids.forEach(function (id, i) { series[id] = listas[i]; });

          var porDimensao = {};
          ORDEM_DIMENSOES.forEach(function (c) { porDimensao[c] = []; });
          indicadores.forEach(function (i) { if (porDimensao[i.dimensao]) porDimensao[i.dimensao].push(i); });

          montarTicker(indicadores, series);
          montarResumoDia(indicadores, series);
          montarSecoesDimensao(porDimensao, series);
          window.DIEESE360.animarEntrada(document.getElementById('resumo-dia'));
        });
    }).catch(function (erro) {
      document.getElementById('resumo-dia').innerHTML = '<p class="aviso demo">' + esc(P.mensagemErro(erro)) + '</p>';
    });
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', iniciar); else iniciar();
})();
