// DIEESE 360 — cartão giratório em janela modal: usado quando não há um
// cartão próprio já na tela para girar no lugar (ex.: clique numa linha da
// tabela de "maiores variações" do resumo do dia). Em vez de navegar para
// indicador.html, abre um cartão grande centralizado — mesmo conteúdo e
// mesma interação de girar do cartao-flip.js, só que como janela, não
// in-place. Decisão explícita do responsável do projeto (2026-10-14): "que
// surgisse um cartão grande girando com esses dados" em vez de levar a uma
// página nova.
//
// Acessível: foco preso dentro do cartão enquanto aberto, Esc fecha, clique
// fora fecha, foco volta pra quem abriu ao fechar, respeita
// prefers-reduced-motion (sem a animação de entrada).
(function () {
  'use strict';
  var overlayEl = null;
  var focoAnterior = null;

  function montarOverlay() {
    if (overlayEl) return;
    overlayEl = document.createElement('div');
    overlayEl.className = 'cartao-modal-fundo';
    overlayEl.innerHTML = '<div class="cartao-modal-caixa" id="cartao-modal-caixa"></div>';
    document.body.appendChild(overlayEl);
    overlayEl.addEventListener('click', function (e) { if (e.target === overlayEl) fecharCartaoModal(); });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && overlayEl.classList.contains('aberto')) fecharCartaoModal();
    });
  }

  function abrirCartaoModal(indicador, serieAsc) {
    montarOverlay();
    var caixa = document.getElementById('cartao-modal-caixa');
    var indicadoresPorId = {}; indicadoresPorId[indicador.id] = indicador;
    var seriesPorId = {}; seriesPorId[indicador.id] = serieAsc;

    caixa.innerHTML =
      '<button type="button" class="cartao-modal-fechar" aria-label="Fechar">×</button>' +
      window.DIEESE360.montarCartaoFlip(indicador, serieAsc, { graficoCompleto: true, classeExtra: 'cartao-modal-cartao' });
    window.DIEESE360.ligarCartoesFlip(caixa);
    window.DIEESE360.preencherGraficosCompletos(caixa, indicadoresPorId, seriesPorId);
    caixa.querySelector('.cartao-modal-fechar').addEventListener('click', fecharCartaoModal);

    focoAnterior = document.activeElement;
    overlayEl.classList.add('aberto');
    document.body.classList.add('cartao-modal-travado');
    var interior = caixa.querySelector('.cartao-flip-interior');
    if (interior) interior.focus();
  }

  function fecharCartaoModal() {
    if (!overlayEl) return;
    overlayEl.classList.remove('aberto');
    document.body.classList.remove('cartao-modal-travado');
    if (focoAnterior && focoAnterior.focus) focoAnterior.focus();
  }

  window.DIEESE360 = window.DIEESE360 || {};
  window.DIEESE360.abrirCartaoModal = abrirCartaoModal;
  window.DIEESE360.fecharCartaoModal = fecharCartaoModal;
})();
