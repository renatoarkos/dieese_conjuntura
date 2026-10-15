// DIEESE 360 — Modal ampliado de indicador (ADR 0007, registrado 2026-10-14)
//
// REGRA PERMANENTE: Nunca girar o cartão pequeno in-place com scrollbar.
// Ao clicar em QUALQUER cartão de indicador (carrossel ou grade de destaque),
// abre esta janela modal ampliada com:
//   - Cabeçalho com valor atual, badge de variação e período de referência
//   - Gráfico interativo em alta resolução (min-height 280px)
//   - Seções estruturadas: Conceituação, Metodologia, Fonte Oficial, Notas
//   - Botão direto para a página completa do indicador
//
// Acessível: foco preso dentro do modal enquanto aberto, Esc fecha,
// clique fora fecha, foco volta para quem abriu ao fechar,
// respeita prefers-reduced-motion.
(function () {
  'use strict';
  var overlayEl = null;
  var focoAnterior = null;
  var P = window.Painel;
  var D = window.DIEESE360.dados;
  var esc = P.esc;

  function montarOverlay() {
    if (overlayEl) return;
    overlayEl = document.createElement('div');
    overlayEl.className = 'modal-ind-fundo';
    overlayEl.setAttribute('role', 'dialog');
    overlayEl.setAttribute('aria-modal', 'true');
    overlayEl.setAttribute('aria-label', 'Detalhes do indicador');
    overlayEl.innerHTML = '<div class="modal-ind-caixa" id="modal-ind-caixa"></div>';
    document.body.appendChild(overlayEl);
    overlayEl.addEventListener('click', function (e) {
      if (e.target === overlayEl) fecharCartaoModal();
    });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && overlayEl.classList.contains('aberto')) fecharCartaoModal();
    });
  }

  function abrirCartaoModal(indicador, serieAsc) {
    montarOverlay();
    var caixa = document.getElementById('modal-ind-caixa');
    var tendencia = D.calcularTendencia(indicador, serieAsc);
    var atual = serieAsc && serieAsc.length ? serieAsc[serieAsc.length - 1] : null;

    var valorStr = atual ? esc(D.formatarValor(indicador, atual.valor)) : '—';
    var dataStr = atual ? esc(D.formatarDataReferencia(atual.data_referencia, indicador.periodicidade)) : '';
    var badge = '';
    if (tendencia) {
      var sinal = tendencia.delta >= 0 ? '+' : '';
      var cls = tendencia.classe === 'boa' ? 'modal-badge-alta' : tendencia.classe === 'ruim' ? 'modal-badge-baixa' : 'modal-badge-neutra';
      badge = '<span class="modal-ind-badge ' + cls + '">' +
        tendencia.seta + ' ' + sinal + esc(D.formatarValor(indicador, tendencia.delta)) +
        ' vs. ' + esc(D.formatarDataReferencia(tendencia.anterior.data_referencia, indicador.periodicidade)) +
        '</span>';
    }

    var conceito = indicador.conceituacao || indicador.conceito || '';
    var metodologia = indicador.metodologia_md || indicador.metodologia || '';
    var fonte = indicador.fonte || '';
    var notas = indicador.notas_explicativas || indicador.notas || '';
    var periodicidade = indicador.periodicidade || '';
    var unidade = indicador.unidade || '';

    caixa.innerHTML =
      '<div class="modal-ind-topo">' +
        '<div class="modal-ind-meta">' +
          '<span class="modal-ind-kicker">' + esc(indicador.dimensao || '') + '</span>' +
          '<h2 class="modal-ind-titulo">' + esc(indicador.nome) + '</h2>' +
          '<div class="modal-ind-stat">' +
            '<strong class="modal-ind-valor">' + valorStr + '</strong>' +
            '<div class="modal-ind-stat-sub">' +
              '<span class="modal-ind-data">' + dataStr + '</span>' +
              badge +
            '</div>' +
          '</div>' +
        '</div>' +
        '<button type="button" class="modal-ind-fechar" aria-label="Fechar detalhes">✕</button>' +
      '</div>' +
      '<div class="modal-ind-corpo">' +
        '<div class="modal-ind-grafico-area">' +
          '<div class="modal-ind-grafico-caixa" id="modal-grafico-' + esc(indicador.id) + '"></div>' +
        '</div>' +
        '<div class="modal-ind-info">' +
          (conceito ? '<section class="modal-ind-secao"><h3>Conceituação socioeconômica</h3><p>' + esc(conceito) + '</p></section>' : '') +
          (metodologia ? '<section class="modal-ind-secao"><h3>Metodologia e cálculo</h3><p>' + esc(metodologia) + '</p></section>' : '') +
          '<section class="modal-ind-secao modal-ind-secao-meta">' +
            '<h3>Dados de referência</h3>' +
            '<dl class="modal-ind-dl">' +
            (fonte ? '<dt>Fonte</dt><dd>' + esc(fonte) + '</dd>' : '') +
            (periodicidade ? '<dt>Periodicidade</dt><dd>' + esc(periodicidade) + '</dd>' : '') +
            (unidade ? '<dt>Unidade</dt><dd>' + esc(unidade) + '</dd>' : '') +
            '</dl>' +
          '</section>' +
          (notas ? '<section class="modal-ind-secao"><h3>Notas explicativas</h3><p>' + esc(notas) + '</p></section>' : '') +
          '<a class="modal-ind-link-completo" href="indicador.html?id=' + esc(indicador.id) + '">' +
            'Ver página completa com exportação e filtros →' +
          '</a>' +
        '</div>' +
      '</div>';

    // Render chart
    var graficoCaixa = document.getElementById('modal-grafico-' + indicador.id);
    if (graficoCaixa && serieAsc && serieAsc.length >= 2) {
      window.DIEESE360.montarGraficoLinha(graficoCaixa, serieAsc, {
        formatarValor: function (v) { return D.formatarValor(indicador, v); },
        formatarData: D.formatarDataCurta
      });
    } else if (graficoCaixa) {
      graficoCaixa.innerHTML = '<p class="modal-grafico-vazio">Pontos insuficientes para o gráfico.</p>';
    }

    caixa.querySelector('.modal-ind-fechar').addEventListener('click', fecharCartaoModal);
    focoAnterior = document.activeElement;
    overlayEl.classList.add('aberto');
    document.body.classList.add('modal-ind-travado');
    var fechar = caixa.querySelector('.modal-ind-fechar');
    if (fechar) fechar.focus();
  }

  function fecharCartaoModal() {
    if (!overlayEl) return;
    overlayEl.classList.remove('aberto');
    document.body.classList.remove('modal-ind-travado');
    if (focoAnterior && focoAnterior.focus) focoAnterior.focus();
  }

  window.DIEESE360 = window.DIEESE360 || {};
  window.DIEESE360.abrirCartaoModal = abrirCartaoModal;
  window.DIEESE360.fecharCartaoModal = fecharCartaoModal;
})();
