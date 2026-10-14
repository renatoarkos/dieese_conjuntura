// Orquestração da página inicial pública (index.html): ticker, cartões de
// dimensão e a amostra curada de indicadores. Não exige sessão — os números
// são públicos (ver ADR 0005); só a navegação completa fica atrás do login.
(function () {
  'use strict';
  var P = window.Painel;
  var D = window.DIEESE360.dados;
  var esc = P.esc;

  // Amostra curada para a home (10 dos 14 indicadores já publicados) — os
  // 4 subíndices restantes do IC-Br e a quebra por UF do limite fiscal
  // (via mapa) ficam para quem entrar no painel.
  var AMOSTRA = [
    'pib_brasil', 'cambio_dolar', 'commodities_geral', 'taxa_investimento',
    'balanca_saldo', 'bndes_desembolsos', 'limite_fiscal_pessoal',
    'pmc_volume_vendas', 'pms_volume_servicos', 'pim_producao_industrial'
  ];
  // Indicadores mensais que compõem o ticker de topo.
  var TICKER = ['cambio_dolar', 'commodities_geral', 'balanca_saldo', 'pmc_volume_vendas', 'pms_volume_servicos', 'pim_producao_industrial', 'bndes_desembolsos'];

  var ICONES_DIMENSAO = {
    macroeconomia: 'assets/dimensoes/icone-macroeconomia.png',
    monetario_credito: 'assets/dimensoes/icone-monetario-credito.png',
    inflacao: 'assets/dimensoes/icone-inflacao.png',
    mercado_trabalho: 'assets/dimensoes/icone-mercado-trabalho.png',
    caged: 'assets/dimensoes/icone-caged.png'
  };

  function montarGradeDimensoes() {
    var alvo = document.getElementById('grade-dimensoes');
    var html = '';
    var i = 1;
    Object.keys(D.DIMENSOES).forEach(function (chave) {
      var dim = D.DIMENSOES[chave];
      var icone = ICONES_DIMENSAO[chave] || '';
      html += '<div class="cartao-dimensao">' +
        '<div class="cartao-dimensao-topo">' +
          '<span class="num">Dimensão ' + (i++) + '</span>' +
          (icone ? '<img src="' + esc(icone) + '" alt="" class="cartao-dimensao-icone" width="48" height="48" loading="lazy">' : '') +
        '</div>' +
        '<h3>' + esc(dim.nome) + '</h3>' +
        '<p>' + esc(dim.descricao) + '</p>' +
      '</div>';
    });
    alvo.innerHTML = html;
  }

  function montarTicker(indicadores, series) {
    var alvo = document.getElementById('ticker-trilho');
    var itens = TICKER.map(function (id) {
      var indicador = indicadores.filter(function (i) { return i.id === id; })[0];
      return indicador ? D.montarItemTicker(indicador, series[id] || []) : '';
    }).filter(Boolean);
    if (!itens.length) { alvo.innerHTML = '<span class="ticker-item"><span class="rotulo">Sem indicadores publicados ainda.</span></span>'; return; }
    // Duplica a lista para o loop de rolagem ficar contínuo (ver @keyframes ticker-rola, translateX(-50%)).
    alvo.innerHTML = itens.join('') + itens.join('');
  }

  function montarAmostra(indicadores, series) {
    var alvo = document.getElementById('grade-amostra');
    var html = AMOSTRA.map(function (id) {
      var indicador = indicadores.filter(function (i) { return i.id === id; })[0];
      return indicador ? window.DIEESE360.montarCartaoFlip(indicador, series[id] || []) : '';
    }).join('');
    alvo.innerHTML = html || '<p>Nenhum indicador publicado ainda.</p>';
    window.DIEESE360.ligarCartoesFlip(alvo);
  }

  function iniciar() {
    montarGradeDimensoes();
    if (!P.sb) {
      document.getElementById('grade-amostra').innerHTML = '<p class="aviso demo">Não foi possível conectar ao Supabase — confira js/config.js.</p>';
      return;
    }
    D.carregarIndicadores().then(function (indicadores) {
      var idsNecessarios = {};
      AMOSTRA.concat(TICKER).forEach(function (id) { idsNecessarios[id] = true; });
      var ids = Object.keys(idsNecessarios);
      return Promise.all(ids.map(function (id) { return D.carregarSerie(id, 24); }))
        .then(function (listas) {
          var series = {};
          ids.forEach(function (id, i) { series[id] = listas[i]; });
          montarTicker(indicadores, series);
          montarAmostra(indicadores, series);
          window.DIEESE360.animarEntrada(document.getElementById('grade-amostra'));
        });
    }).catch(function (erro) {
      document.getElementById('grade-amostra').innerHTML = '<p class="aviso demo">' + esc(P.mensagemErro(erro)) + '</p>';
    });
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', iniciar); else iniciar();
})();
