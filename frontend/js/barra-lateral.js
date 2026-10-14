// DIEESE 360 — navegação lateral: as dimensões (seções) e os indicadores de
// cada uma (subseções), sempre à esquerda — mesmo padrão de portais de
// estatística de referência (SIDRA, FRED, Eurostat), agora como menu de
// plataforma de gestão: cada dimensão recolhe/expande (acordeão nativo
// <details>/<summary>, mesmo padrão já usado no FAQ da home), e a barra
// inteira pode ser recolhida para só a tira de ícones/links de dimensão
// (pedido do responsável do projeto, 2026-10-14). Usada em painel.html e
// indicador.html. Cada indicador linka direto para a própria página
// (indicador.html?id=...) — não é modal.
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
      var temAtivo = itens.some(function (ind) { return ind.id === idAtivo; });
      var corpo = itens.length
        ? '<ul class="lateral-lista">' + itens.map(function (ind) {
            return '<li><a class="lateral-link' + (ind.id === idAtivo ? ' ativo' : '') + '" href="indicador.html?id=' + encodeURIComponent(ind.id) + '">' + esc(ind.nome) + '</a></li>';
          }).join('') + '</ul>'
        : '<p class="lateral-vazio">Em breve</p>';
      return (
        '<details class="lateral-secao"' + (temAtivo ? ' open' : '') + '>' +
        '<summary class="lateral-secao-titulo">' + esc(dim.nome) + '</summary>' +
        corpo +
        '</details>'
      );
    }).join('');
    container.innerHTML = html;
  }

  // Recolhe a barra inteira para uma tira estreita (só os títulos de
  // dimensão, sem os indicadores) — alterna uma classe no elemento pai
  // (`.layout-lateral`) que o CSS usa para esconder/mostrar a largura.
  function ligarRecolherBarraLateral(botao, layout) {
    botao.addEventListener('click', function () {
      var recolhida = layout.classList.toggle('lateral-recolhida');
      botao.setAttribute('aria-expanded', recolhida ? 'false' : 'true');
      botao.textContent = recolhida ? '»' : '«';
      try { localStorage.setItem('dieese360_lateral_recolhida', recolhida ? '1' : '0'); } catch (e) { /* localStorage indisponível — ignora, não é crítico */ }
    });
    try {
      if (localStorage.getItem('dieese360_lateral_recolhida') === '1') {
        layout.classList.add('lateral-recolhida');
        botao.setAttribute('aria-expanded', 'false');
        botao.textContent = '»';
      }
    } catch (e) { /* ignora */ }
  }

  window.DIEESE360 = window.DIEESE360 || {};
  window.DIEESE360.montarBarraLateral = montarBarraLateral;
  window.DIEESE360.ligarRecolherBarraLateral = ligarRecolherBarraLateral;
})();
