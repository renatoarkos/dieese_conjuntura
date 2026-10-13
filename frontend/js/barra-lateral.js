// DIEESE 360 — navegação lateral: as 5 dimensões (seções) e os indicadores de
// cada uma (subseções), sempre à esquerda — mesmo padrão de portais de
// estatística de referência (SIDRA, FRED, Eurostat). Usada em painel.html e
// indicador.html. Cada indicador linka direto para a própria página
// (indicador.html?id=...) — não é mais um modal.
(function () {
  'use strict';
  var esc = (window.Painel && window.Painel.esc) || function (s) { return String(s); };

  function montarBarraLateral(container, indicadores, idAtivo) {
    var D = window.DIEESE360.dados;
    var porDimensao = {};
    Object.keys(D.DIMENSOES).forEach(function (c) { porDimensao[c] = []; });
    indicadores.forEach(function (ind) { if (porDimensao[ind.dimensao]) porDimensao[ind.dimensao].push(ind); });

    var html = Object.keys(D.DIMENSOES).map(function (chave) {
      var dim = D.DIMENSOES[chave];
      var itens = porDimensao[chave];
      var corpo = itens.length
        ? '<ul class="lateral-lista">' + itens.map(function (ind) {
            return '<li><a class="lateral-link' + (ind.id === idAtivo ? ' ativo' : '') + '" href="indicador.html?id=' + encodeURIComponent(ind.id) + '">' + esc(ind.nome) + '</a></li>';
          }).join('') + '</ul>'
        : '<p class="lateral-vazio">Em breve</p>';
      return (
        '<div class="lateral-secao">' +
        '<h3 class="lateral-secao-titulo">' + esc(dim.nome) + '</h3>' +
        corpo +
        '</div>'
      );
    }).join('');
    container.innerHTML = html;
  }

  window.DIEESE360 = window.DIEESE360 || {};
  window.DIEESE360.montarBarraLateral = montarBarraLateral;
})();
