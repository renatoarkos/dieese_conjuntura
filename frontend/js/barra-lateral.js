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

  // Monta a lista de indicadores de uma dimensão, separando quem tem
  // subgrupo (rótulo + sublista, ex. "Novo CAGED" dentro de "Mercado de
  // trabalho") de quem não tem (lista direta, como sempre foi). A ordem dos
  // subgrupos é a ordem em que aparecem pela primeira vez na lista de
  // indicadores (que já vem ordenada por nome do catálogo).
  function montarCorpoDimensao(itens, idAtivo) {
    var soltos = [];
    var porSubgrupo = {};
    var ordemSubgrupos = [];
    itens.forEach(function (ind) {
      var subgrupo = window.DIEESE360.dados.subgrupoDoIndicador(ind.id);
      if (!subgrupo) { soltos.push(ind); return; }
      if (!porSubgrupo[subgrupo]) { porSubgrupo[subgrupo] = []; ordemSubgrupos.push(subgrupo); }
      porSubgrupo[subgrupo].push(ind);
    });

    function montarLista(lista) {
      return '<ul class="lateral-lista">' + lista.map(function (ind) {
        return '<li><a class="lateral-link' + (ind.id === idAtivo ? ' ativo' : '') + '" href="indicador.html?id=' + encodeURIComponent(ind.id) + '">' + esc(ind.nome) + '</a></li>';
      }).join('') + '</ul>';
    }

    var partes = [];
    if (soltos.length) partes.push(montarLista(soltos));
    ordemSubgrupos.forEach(function (subgrupo) {
      partes.push('<p class="lateral-subgrupo">' + esc(subgrupo) + '</p>' + montarLista(porSubgrupo[subgrupo]));
    });
    return partes.join('') || '<p class="lateral-vazio">Em breve</p>';
  }

  function montarBarraLateral(container, indicadores, idAtivo) {
    var D = window.DIEESE360.dados;
    var porDimensao = {};
    Object.keys(D.DIMENSOES).forEach(function (c) { porDimensao[c] = []; });
    indicadores.forEach(function (ind) {
      var chave = D.dimensaoEfetiva(ind.dimensao);
      if (porDimensao[chave]) porDimensao[chave].push(ind);
    });

    var html = Object.keys(D.DIMENSOES).map(function (chave) {
      var dim = D.DIMENSOES[chave];
      var itens = porDimensao[chave];
      var temAtivo = itens.some(function (ind) { return ind.id === idAtivo; });
      return (
        '<details class="lateral-secao"' + (temAtivo ? ' open' : '') + '>' +
        '<summary class="lateral-secao-titulo">' + esc(dim.nome) + '</summary>' +
        montarCorpoDimensao(itens, idAtivo) +
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
