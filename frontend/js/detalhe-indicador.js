// DIEESE 360 — painel de detalhe de um indicador: abre, ao clicar num
// cartão-resumo, dois cartões novos lado a lado — um com a informação
// completa (conceito, fonte, comparação) e outro com o gráfico da série
// histórica inteira (ver js/grafico-linha.js). Acessível (foco preso, ESC
// fecha, clique no fundo fecha) e respeita prefers-reduced-motion — mesmo
// princípio do cartão giratório modal de painel_saude_mental/painel-web,
// adaptado para abrir 2 cartões em vez de virar 1.
(function () {
  'use strict';
  var P = window.Painel;
  var D = window.DIEESE360.dados;
  var esc = P.esc;
  var aberto = null;

  function reduz() { return !!(window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches); }
  function elementosFocaveis(raiz) {
    return Array.prototype.filter.call(
      raiz.querySelectorAll('button, [href], input, [tabindex]:not([tabindex="-1"])'),
      function (e) { return !e.disabled && e.getClientRects().length > 0; }
    );
  }

  function montarCartaoInfo(indicador, serieAsc) {
    var tendencia = D.calcularTendencia(indicador, serieAsc);
    var atual = serieAsc[serieAsc.length - 1];
    var comparacao = tendencia
      ? tendencia.seta + ' ' + D.formatarValor(indicador, Math.abs(tendencia.delta)) + ' no período, comparado a ' + D.formatarDataReferencia(tendencia.anterior.data_referencia, indicador.periodicidade)
      : 'Ainda não há ponto anterior para comparar.';

    var div = document.createElement('div');
    div.className = 'detalhe-cartao detalhe-info';
    div.innerHTML =
      '<h3>' + esc(indicador.nome) + '</h3>' +
      '<p class="explicacao">' + esc(indicador.metodologia_md || ('Indicador de ' + ((D.DIMENSOES[indicador.dimensao] || {}).nome || indicador.dimensao) + '.')) + '</p>' +
      '<dl>' +
      '<dt>Último dado</dt><dd>' + esc(D.formatarValor(indicador, atual.valor)) + ' — ' + esc(D.formatarDataReferencia(atual.data_referencia, indicador.periodicidade)) + '</dd>' +
      '<dt>Fonte</dt><dd>' + esc(indicador.fonte) + '</dd>' +
      '<dt>Periodicidade</dt><dd>' + esc(indicador.periodicidade) + '</dd>' +
      '<dt>Classificação</dt><dd>' + esc(indicador.classificacao) + ' — ver docs/04-fontes</dd>' +
      '</dl>' +
      '<p class="comparacao">' + esc(comparacao) + '</p>';
    return div;
  }

  function montarCartaoGrafico(indicador, serieAsc) {
    var div = document.createElement('div');
    div.className = 'detalhe-cartao detalhe-grafico';
    div.innerHTML =
      '<h3>Série histórica completa</h3>' +
      '<p class="explicacao">' + serieAsc.length + (serieAsc.length === 1 ? ' ponto' : ' pontos') + ', de ' + esc(D.formatarDataCurta(serieAsc[0].data_referencia)) + ' a ' + esc(D.formatarDataCurta(serieAsc[serieAsc.length - 1].data_referencia)) + '.</p>' +
      '<div class="grafico-linha-caixa"></div>';
    window.DIEESE360.montarGraficoLinha(div.querySelector('.grafico-linha-caixa'), serieAsc, {
      formatarValor: function (v) { return D.formatarValor(indicador, v); },
      formatarData: D.formatarDataCurta
    });
    return div;
  }

  function fechar() {
    if (!aberto) return;
    var raiz = aberto.raiz, origem = aberto.origem;
    document.removeEventListener('keydown', teclas, true);
    raiz.remove();
    document.body.style.overflow = aberto.rolagemAnterior;
    aberto = null;
    if (origem && origem.isConnected && origem.focus) origem.focus({ preventScroll: true });
  }

  function teclas(e) {
    if (e.key === 'Escape') { e.preventDefault(); fechar(); return; }
    if (e.key !== 'Tab' || !aberto) return;
    var lista = elementosFocaveis(aberto.painel);
    if (!lista.length) return;
    var primeiro = lista[0], ultimo = lista[lista.length - 1];
    if (e.shiftKey && document.activeElement === primeiro) { e.preventDefault(); ultimo.focus(); }
    else if (!e.shiftKey && document.activeElement === ultimo) { e.preventDefault(); primeiro.focus(); }
  }

  function abrirDetalhe(id, origem) {
    if (aberto) fechar();
    var registro = window.DIEESE360.registro && window.DIEESE360.registro[id];
    if (!registro) return;
    var indicador = registro.indicador, serieAsc = registro.serieAsc;

    var fundo = document.createElement('div');
    fundo.className = 'detalhe-fundo';
    var painel = document.createElement('div');
    painel.className = 'detalhe-painel';
    painel.setAttribute('role', 'dialog');
    painel.setAttribute('aria-modal', 'true');
    painel.setAttribute('aria-label', indicador.nome);

    var topo = document.createElement('div');
    topo.className = 'detalhe-topo';
    topo.innerHTML = '<button type="button" class="detalhe-fechar" aria-label="Fechar">&times;</button>';
    var corpo = document.createElement('div');
    corpo.className = 'detalhe-corpo';
    corpo.appendChild(montarCartaoInfo(indicador, serieAsc));
    corpo.appendChild(montarCartaoGrafico(indicador, serieAsc));

    painel.appendChild(topo);
    painel.appendChild(corpo);

    var raiz = document.createElement('div');
    raiz.className = 'detalhe-raiz';
    raiz.appendChild(fundo);
    raiz.appendChild(painel);
    document.body.appendChild(raiz);

    aberto = { raiz: raiz, painel: painel, origem: origem, rolagemAnterior: document.body.style.overflow };
    document.body.style.overflow = 'hidden';
    document.addEventListener('keydown', teclas, true);
    fundo.addEventListener('click', fechar);
    topo.querySelector('.detalhe-fechar').addEventListener('click', fechar);

    if (!reduz()) {
      raiz.classList.add('detalhe-entrando');
      requestAnimationFrame(function () { raiz.classList.remove('detalhe-entrando'); });
    }
    topo.querySelector('.detalhe-fechar').focus();
  }

  document.addEventListener('click', function (e) {
    var botao = e.target.closest('[data-abrir-detalhe]');
    if (botao) abrirDetalhe(botao.dataset.abrirDetalhe, botao);
  });

  window.DIEESE360.abrirDetalhe = abrirDetalhe;
})();
