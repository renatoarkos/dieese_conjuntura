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

  // opcoes.graficoCompleto: troca a sparkline pequena por uma área vazia
  // marcada com data-grafico-completo (o chamador preenche com
  // DIEESE360.montarGraficoLinha depois de inserir o HTML no DOM — a
  // sparkline é só SVG estático, mas o gráfico completo precisa do elemento
  // já anexado). Usado pelo carrossel de destaque e pelo cartão modal da
  // home (ver inicio.js e cartao-modal.js) — mesmo conteúdo, cartão maior.
  function montarCartaoFlip(indicador, serieAsc, opcoes) {
    opcoes = opcoes || {};
    if (!serieAsc.length) return D.montarCartaoVazio(indicador);
    var atual = serieAsc[serieAsc.length - 1];
    var tendencia = D.calcularTendencia(indicador, serieAsc);
    var chip = tendencia
      ? '<span class="chip-tendencia ' + tendencia.classe + '">' + tendencia.seta + ' ' + esc(D.formatarValor(indicador, Math.abs(tendencia.delta))) + '</span>'
      : '';
    var comparacao = tendencia
      ? tendencia.seta + ' ' + D.formatarValor(indicador, Math.abs(tendencia.delta)) + ' no período, comparado a ' + D.formatarDataReferencia(tendencia.anterior.data_referencia, indicador.periodicidade)
      : 'Ainda não há ponto anterior para comparar.';
    var grafico = opcoes.graficoCompleto
      ? '<div class="cartao-flip-grafico-area" data-grafico-completo="' + esc(indicador.id) + '"></div>'
      : D.montarSparkline(serieAsc);

    return (
      '<article class="cartao-flip' + (opcoes.classeExtra ? ' ' + esc(opcoes.classeExtra) : '') + '">' +
      '<div class="cartao-flip-interior" role="button" tabindex="0" aria-pressed="false" ' +
      'aria-label="' + esc(indicador.nome) + ', clique para virar o cartão e ver a explicação">' +
      '<div class="cartao-flip-frente">' +
      '<div class="cartao-cabecalho"><span class="cartao-rotulo">' + esc(indicador.nome) + '</span>' + chip + '</div>' +
      '<strong class="cartao-valor">' + esc(D.formatarValor(indicador, atual.valor)) + '</strong>' +
      '<span class="cartao-data">' + esc(D.formatarDataReferencia(atual.data_referencia, indicador.periodicidade)) + '</span>' +
      grafico +
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

  // Preenche, para um container já no DOM, todo gráfico completo pendente
  // (ver opcoes.graficoCompleto acima) — chamar depois de innerHTML e de
  // ligarCartoesFlip. seriesPorId: {indicador_id: serieAsc}.
  function preencherGraficosCompletos(container, indicadoresPorId, seriesPorId) {
    container.querySelectorAll('[data-grafico-completo]').forEach(function (el) {
      var id = el.getAttribute('data-grafico-completo');
      var indicador = indicadoresPorId[id];
      var serie = seriesPorId[id] || [];
      if (!indicador || serie.length < 2) { el.innerHTML = '<p class="aviso demo">Pontos insuficientes para o gráfico.</p>'; return; }
      window.DIEESE360.montarGraficoLinha(el, serie, {
        formatarValor: function (v) { return D.formatarValor(indicador, v); },
        formatarData: D.formatarDataCurta
      });
    });
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
  window.DIEESE360.preencherGraficosCompletos = preencherGraficosCompletos;
})();
