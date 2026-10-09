// Orquestração do painel interno (painel.html): exige sessão, monta as abas
// das 5 dimensões e renderiza os cartões — e, para o limite fiscal por UF, o
// mapa coroplético (ver js/mapa-uf.js) em vez de um cartão único com média.
(function () {
  'use strict';
  var P = window.Painel;
  var D = window.DIEESE360.dados;
  var esc = P.esc;

  var ORDEM_DIMENSOES = ['macroeconomia', 'monetario_credito', 'inflacao', 'mercado_trabalho', 'caged'];
  var INDICADOR_MAPA = 'limite_fiscal_pessoal'; // regionalizado — vira mapa, não cartão (ver DISCOVERY desta sessão)

  function montarAbas() {
    var abas = document.getElementById('abas-dimensao');
    var html = ORDEM_DIMENSOES.map(function (chave, i) {
      var dim = D.DIMENSOES[chave];
      return '<button type="button" class="aba-dimensao' + (i === 0 ? ' ativa' : '') + '" data-dimensao="' + chave + '">' + esc(dim.nome) + '</button>';
    }).join('');
    abas.innerHTML = html;
    abas.addEventListener('click', function (e) {
      var botao = e.target.closest('.aba-dimensao');
      if (!botao) return;
      trocarAba(botao.dataset.dimensao);
    });
  }

  function trocarAba(chave) {
    document.querySelectorAll('.aba-dimensao').forEach(function (b) { b.classList.toggle('ativa', b.dataset.dimensao === chave); });
    document.querySelectorAll('.painel-dimensao').forEach(function (p) { p.classList.toggle('ativa', p.id === 'painel-dim-' + chave); });
    var painelAtivo = document.getElementById('painel-dim-' + chave);
    if (painelAtivo) window.DIEESE360.animarEntrada(painelAtivo);
  }

  function montarPainelMacroeconomia(container, indicadoresDim, series) {
    var indicadorMapa = indicadoresDim.filter(function (i) { return i.id === INDICADOR_MAPA; })[0];
    var outros = indicadoresDim.filter(function (i) { return i.id !== INDICADOR_MAPA; });

    var html = '';
    if (indicadorMapa && series[INDICADOR_MAPA] && series[INDICADOR_MAPA].length) {
      var ultimo = series[INDICADOR_MAPA][series[INDICADOR_MAPA].length - 1];
      var porUf = (ultimo.metadata && ultimo.metadata.por_uf) || {};
      html += (
        '<div class="mapa-caixa" style="margin-bottom:24px">' +
        '<div class="mapa-cabecalho"><h3>' + esc(indicadorMapa.nome) + '</h3>' +
        '<span class="cartao-data">Média nacional: ' + esc(D.formatarValor(indicadorMapa, ultimo.valor)) + ' · ' + esc(D.formatarDataReferencia(ultimo.data_referencia, indicadorMapa.periodicidade)) + '</span></div>' +
        '<p style="color:var(--cinza-700);font-size:.88rem;margin-bottom:14px">' + esc(indicadorMapa.metodologia_md || '') + '</p>' +
        '<div class="mapa-svg-caixa" id="mapa-limite-fiscal"></div>' +
        '</div>'
      );
    }
    html += '<div class="grade-indicadores" id="grade-macroeconomia"></div>';
    container.innerHTML = html;

    var grade = document.getElementById('grade-macroeconomia');
    grade.innerHTML = outros.map(function (indicador) { return D.montarCartao(indicador, series[indicador.id] || []); }).join('') || '<p>Nenhum outro indicador publicado ainda.</p>';

    if (indicadorMapa && series[INDICADOR_MAPA] && series[INDICADOR_MAPA].length) {
      var ultimoMapa = series[INDICADOR_MAPA][series[INDICADOR_MAPA].length - 1];
      var porUfMapa = (ultimoMapa.metadata && ultimoMapa.metadata.por_uf) || {};
      window.DIEESE360.montarMapaUF(document.getElementById('mapa-limite-fiscal'), porUfMapa, {
        legenda: true,
        formatarValor: function (v) { return D.formatarValor(indicadorMapa, v); }
      });
    }
  }

  function montarPainelPendente(container, chave) {
    container.innerHTML = '<div class="grade-indicadores">' + D.montarCartaoDimensaoPendente(chave) + '</div>';
  }

  function iniciar(perfil) {
    montarAbas();
    var raizPaineis = document.getElementById('paineis-dimensao');
    raizPaineis.innerHTML = ORDEM_DIMENSOES.map(function (chave, i) {
      return '<div class="painel-dimensao' + (i === 0 ? ' ativa' : '') + '" id="painel-dim-' + chave + '"></div>';
    }).join('');

    D.carregarIndicadores().then(function (indicadores) {
      var porDimensao = {};
      ORDEM_DIMENSOES.forEach(function (c) { porDimensao[c] = []; });
      indicadores.forEach(function (i) { if (porDimensao[i.dimensao]) porDimensao[i.dimensao].push(i); });

      var idsMacro = porDimensao.macroeconomia.map(function (i) { return i.id; });
      return Promise.all(idsMacro.map(function (id) { return D.carregarSerie(id, 24); })).then(function (listas) {
        var series = {};
        idsMacro.forEach(function (id, i) { series[id] = listas[i]; });

        montarPainelMacroeconomia(document.getElementById('painel-dim-macroeconomia'), porDimensao.macroeconomia, series);
        ORDEM_DIMENSOES.slice(1).forEach(function (chave) {
          montarPainelPendente(document.getElementById('painel-dim-' + chave), chave);
        });

        window.DIEESE360.animarEntrada(document.getElementById('painel-dim-macroeconomia'));
      });
    }).catch(function (erro) {
      raizPaineis.innerHTML = '<p class="aviso demo">' + esc(P.mensagemErro(erro)) + '</p>';
    });
  }

  P.exigirSessao().then(function (ctx) { iniciar(ctx.perfil); });
})();
