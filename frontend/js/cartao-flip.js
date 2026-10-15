// DIEESE 360 — cartão de indicador (montagem HTML apenas)
//
// ADR 0007 (2026-10-14 — REGRA PERMANENTE): Nenhum cartão pequeno vira
// in-place com rotação 3D nem scrollbar. Clicar em qualquer cartão de
// indicador (carrossel de dimensão ou grade de destaque da home) abre
// SEMPRE o modal ampliado via window.DIEESE360.abrirCartaoModal —
// ver cartao-modal.js. Esta função monta apenas o HTML frontal do cartão
// (frente com valor + sparkline + dica de clique). A lógica de navegação
// e o conteúdo metodológico ficam no modal.
//
// ligarCartoesFlip agora é um alias para compatibilidade: não faz flip,
// apenas garante que cliques disparam o modal (uso em preencherDestaque
// de inicio.js — o handler real é no wrapper, mas mantemos o fallback).
(function () {
  'use strict';
  var P = window.Painel;
  var D = window.DIEESE360.dados;
  var esc = P.esc;

  // Monta o HTML do cartão (frente apenas — sem verso; o verso existe no modal ampliado).
  // opcoes.graficoCompleto: substitui sparkline por container para grafico interativo.
  // opcoes.classeExtra: classe adicional no <article>.
  function montarCartaoFlip(indicador, serieAsc, opcoes) {
    opcoes = opcoes || {};
    if (!serieAsc.length) return D.montarCartaoVazio(indicador);
    var atual = serieAsc[serieAsc.length - 1];
    var tendencia = D.calcularTendencia(indicador, serieAsc);
    var chip = tendencia
      ? '<span class="chip-tendencia ' + tendencia.classe + '">' + tendencia.seta + ' ' + esc(D.formatarValor(indicador, Math.abs(tendencia.delta))) + '</span>'
      : '';
    var grafico = opcoes.graficoCompleto
      ? '<div class="cartao-flip-grafico-area" data-grafico-completo="' + esc(indicador.id) + '"></div>'
      : D.montarSparkline(serieAsc);

    return (
      '<article class="cartao-flip' + (opcoes.classeExtra ? ' ' + esc(opcoes.classeExtra) : '') + '" ' +
      'title="Clique para ver o gráfico ampliado e metodologia">' +
      '<div class="cartao-flip-frente">' +
      '<div class="cartao-cabecalho"><span class="cartao-rotulo">' + esc(indicador.nome) + '</span>' + chip + '</div>' +
      '<strong class="cartao-valor">' + esc(D.formatarValor(indicador, atual.valor)) + '</strong>' +
      '<span class="cartao-data">' + esc(D.formatarDataReferencia(atual.data_referencia, indicador.periodicidade)) + '</span>' +
      grafico +
      '<span class="cartao-dica">↗ ver gráfico e metodologia</span>' +
      '</div>' +
      '</article>'
    );
  }

  // Preenche gráficos completos em containers data-grafico-completo.
  // Chamar depois de inserir HTML no DOM.
  function preencherGraficosCompletos(container, indicadoresPorId, seriesPorId) {
    container.querySelectorAll('[data-grafico-completo]').forEach(function (el) {
      var id = el.getAttribute('data-grafico-completo');
      var indicador = indicadoresPorId[id];
      var serie = seriesPorId[id] || [];
      if (!indicador || serie.length < 2) {
        el.innerHTML = '<p class="aviso demo">Pontos insuficientes para o gráfico.</p>';
        return;
      }
      window.DIEESE360.montarGraficoLinha(el, serie, {
        formatarValor: function (v) { return D.formatarValor(indicador, v); },
        formatarData: D.formatarDataCurta
      });
    });
  }

  // Compatibilidade: não faz flip in-place. No-op (os handlers reais
  // são registrados nos wrappers .destaque-card-wrapper e .carrossel-item
  // em inicio.js). Mantido para não quebrar chamadas legadas.
  function ligarCartoesFlip(container) {
    // Nada — o flip in-place está desativado por ADR 0007.
    // Cliques nos cartões sobem para o wrapper e disparam abrirCartaoModal.
  }

  window.DIEESE360 = window.DIEESE360 || {};
  window.DIEESE360.montarCartaoFlip = montarCartaoFlip;
  window.DIEESE360.ligarCartoesFlip = ligarCartoesFlip;
  window.DIEESE360.preencherGraficosCompletos = preencherGraficosCompletos;
})();
