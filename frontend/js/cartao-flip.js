// DIEESE 360 — cartão giratório (flip in-place), usado só na amostra pública
// da home (index.html). Clicar gira o cartão no próprio lugar e revela a
// explicação do indicador — NÃO navega para outra página. A navegação
// completa (gráfico, tabela, infográfico, filtro de período, exportação)
// fica para quem entrar no painel — ver js/pagina-indicador.js. Decisão
// explícita do responsável do projeto: "a ideia aqui não era levar para a
// tela geral... esses dados são apenas uma amostra".
//
// Acessível: operável por teclado (Enter/Espaço), aria-pressed reflete o
// estado, e respeita prefers-reduced-motion (sem a rotação 3D animada, troca
// instantânea de frente/verso).
(function () {
  'use strict';
  var P = window.Painel;
  var D = window.DIEESE360.dados;
  var esc = P.esc;

  function montarCartaoFlip(indicador, serieAsc) {
    if (!serieAsc.length) return D.montarCartaoVazio(indicador);
    var atual = serieAsc[serieAsc.length - 1];
    var tendencia = D.calcularTendencia(indicador, serieAsc);
    var chip = tendencia
      ? '<span class="chip-tendencia ' + tendencia.classe + '">' + tendencia.seta + ' ' + esc(D.formatarValor(indicador, Math.abs(tendencia.delta))) + '</span>'
      : '';
    var comparacao = tendencia
      ? tendencia.seta + ' ' + D.formatarValor(indicador, Math.abs(tendencia.delta)) + ' no período, comparado a ' + D.formatarDataReferencia(tendencia.anterior.data_referencia, indicador.periodicidade)
      : 'Ainda não há ponto anterior para comparar.';

    return (
      '<article class="cartao-flip">' +
      '<div class="cartao-flip-interior" role="button" tabindex="0" aria-pressed="false" ' +
      'aria-label="' + esc(indicador.nome) + ' — clique para virar o cartão e ver a explicação">' +
      '<div class="cartao-flip-frente">' +
      '<div class="cartao-cabecalho"><span class="cartao-rotulo">' + esc(indicador.nome) + '</span>' + chip + '</div>' +
      '<strong class="cartao-valor">' + esc(D.formatarValor(indicador, atual.valor)) + '</strong>' +
      '<span class="cartao-data">' + esc(D.formatarDataReferencia(atual.data_referencia, indicador.periodicidade)) + '</span>' +
      D.montarSparkline(serieAsc) +
      '<span class="cartao-dica">⟳ clique para entender</span>' +
      '</div>' +
      '<div class="cartao-flip-verso">' +
      '<span class="cartao-rotulo">' + esc(indicador.nome) + '</span>' +
      '<p class="cartao-flip-conceito">' + esc(indicador.metodologia_md || '') + '</p>' +
      '<dl class="cartao-flip-meta">' +
      '<dt>Fonte</dt><dd>' + esc(indicador.fonte) + '</dd>' +
      '<dt>Periodicidade</dt><dd>' + esc(indicador.periodicidade) + '</dd>' +
      '</dl>' +
      '<p class="cartao-flip-comparacao">' + esc(comparacao) + '</p>' +
      '<a class="cartao-flip-link" href="indicador.html?id=' + esc(indicador.id) + '">Ver página completa, gráfico e exportação →</a>' +
      '</div>' +
      '</div>' +
      '</article>'
    );
  }

  function ligarCartoesFlip(container) {
    container.querySelectorAll('.cartao-flip-interior').forEach(function (el) {
      function alternar() {
        var cartao = el.parentElement;
        var virado = cartao.classList.toggle('virado');
        el.setAttribute('aria-pressed', virado ? 'true' : 'false');
      }
      el.addEventListener('click', function (e) {
        if (e.target.closest('a')) return; // deixa o link "ver página completa" navegar normalmente
        alternar();
      });
      el.addEventListener('keydown', function (e) {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault();
          alternar();
        }
      });
    });
  }

  window.DIEESE360 = window.DIEESE360 || {};
  window.DIEESE360.montarCartaoFlip = montarCartaoFlip;
  window.DIEESE360.ligarCartoesFlip = ligarCartoesFlip;
})();
