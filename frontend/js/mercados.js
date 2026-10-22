// Página dedicada "Mercados financeiros" (mercados.html) — layout no padrão
// de painel de bolsa (hero com os 4 índices + tabelas por categoria), bem
// diferente do cartão-padrão do resto da plataforma, a pedido do responsável
// do projeto (2026-10-15): "que a visualização fosse igual aos dos
// principais sites de bolsas de valores". Ver ADR 0010 — esta dimensão não é
// dado produzido pelo DIEESE, por isso fica numa página separada, não
// misturada ao carrossel das outras 6 dimensões.
(function () {
  'use strict';
  var P = window.Painel;
  var D = window.DIEESE360.dados;
  var esc = P.esc;

  var INDICES = ['ibovespa', 'sp500', 'nasdaq', 'dow_jones'];
  var CRIPTO = ['bitcoin', 'ethereum'];
  var ACOES = ['petr4', 'vale3', 'itub4'];
  var TODOS = INDICES.concat(CRIPTO, ACOES);

  function formatarVariacaoAbs(indicador, serieAsc) {
    var t = D.calcularTendencia(indicador, serieAsc);
    if (!t) return '<span class="mercados-sem-dado">—</span>';
    var sinal = t.delta > 0 ? '+' : '';
    return '<span class="mercados-variacao ' + t.direcaoMudanca + '">' + t.seta + ' ' + sinal + esc(D.formatarValor(indicador, t.delta)) + '</span>';
  }

  function formatarVariacaoPct(indicador, serieAsc) {
    var v = D.calcularVariacao(indicador, serieAsc);
    if (!v) return '<span class="mercados-sem-dado">—</span>';
    var sinal = v.valor > 0 ? '+' : '';
    return '<span class="mercados-variacao ' + v.direcao + '">' + sinal + D.formatarNumero(v.valor, 2) + '%</span>';
  }

  function montarCardHero(indicador, serieAsc) {
    if (!serieAsc.length) return '';
    var atual = serieAsc[serieAsc.length - 1];
    var t = D.calcularTendencia(indicador, serieAsc);
    return (
      '<a class="mercados-hero-card" href="indicador.html?id=' + esc(indicador.id) + '">' +
      '<span class="mercados-hero-nome">' + esc(indicador.nome) + '</span>' +
      '<strong class="mercados-hero-valor">' + esc(D.formatarValor(indicador, atual.valor)) + '</strong>' +
      '<span class="mercados-hero-variacoes">' + formatarVariacaoAbs(indicador, serieAsc) + formatarVariacaoPct(indicador, serieAsc) + '</span>' +
      D.montarSparkline(serieAsc) +
      '</a>'
    );
  }

  function montarLinhaTabela(indicador, serieAsc) {
    if (!serieAsc.length) {
      return '<tr><td>' + esc(indicador.nome) + '</td><td colspan="4" class="mercados-sem-dado">Sem dado publicado ainda.</td></tr>';
    }
    var atual = serieAsc[serieAsc.length - 1];
    return (
      '<tr class="mercados-linha" data-id="' + esc(indicador.id) + '" tabindex="0" role="button" aria-label="' + esc(indicador.nome) + ', ver gráfico e metodologia">' +
      '<td class="mercados-col-nome"><strong>' + esc(indicador.nome) + '</strong><span>' + esc(indicador.fonte.replace(/^Yahoo Finance \(ticker /, '').replace(/\)$/, '')) + '</span></td>' +
      '<td class="mercados-col-grafico">' + D.montarSparkline(serieAsc) + '</td>' +
      '<td class="mercados-col-valor">' + esc(D.formatarValor(indicador, atual.valor)) + '</td>' +
      '<td class="mercados-col-variacao">' + formatarVariacaoAbs(indicador, serieAsc) + '</td>' +
      '<td class="mercados-col-variacao">' + formatarVariacaoPct(indicador, serieAsc) + '</td>' +
      '</tr>'
    );
  }

  function montarTabela(idTabela, ids, indicadoresPorId, series) {
    var corpo = document.getElementById(idTabela);
    if (!corpo) return;
    corpo.innerHTML = ids.map(function (id) {
      var indicador = indicadoresPorId[id];
      if (!indicador) return '';
      return montarLinhaTabela(indicador, series[id] || []);
    }).join('');
    corpo.querySelectorAll('.mercados-linha').forEach(function (linha) {
      function abrir() { window.location.href = 'indicador.html?id=' + encodeURIComponent(linha.getAttribute('data-id')); }
      linha.addEventListener('click', abrir);
      linha.addEventListener('keydown', function (e) { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); abrir(); } });
    });
  }

  function iniciar() {
    D.carregarIndicadores().then(function (indicadores) {
      var porId = {};
      indicadores.forEach(function (i) { porId[i.id] = i; });
      var disponiveis = TODOS.filter(function (id) { return porId[id]; });
      if (!disponiveis.length) {
        document.getElementById('mercados-hero').innerHTML = '<p class="aviso demo">Nenhum dado de mercado publicado ainda.</p>';
        return Promise.resolve();
      }
      return D.carregarSeriesPorIndicadores(disponiveis, 60).then(function (series) {
        document.getElementById('mercados-hero').innerHTML = INDICES.map(function (id) {
          return porId[id] ? montarCardHero(porId[id], series[id] || []) : '';
        }).join('');
        montarTabela('mercados-corpo-cripto', CRIPTO, porId, series);
        montarTabela('mercados-corpo-acoes', ACOES, porId, series);
        document.querySelectorAll('.mercados-atualizado').forEach(function (el) {
          var pontos = series[INDICES[0]] || [];
          if (!pontos.length) return;
          var d = new Date(pontos[pontos.length - 1].data_referencia + 'T00:00:00');
          el.textContent = 'Última atualização: ' + d.toLocaleDateString('pt-BR', { day: '2-digit', month: 'long', year: 'numeric' });
        });
        window.DIEESE360.animarEntrada && window.DIEESE360.animarEntrada(document.body);
      });
    }).catch(function (erro) {
      document.getElementById('mercados-hero').innerHTML = '<p class="aviso demo">' + esc(P.mensagemErro(erro)) + '</p>';
    });
  }

  document.addEventListener('DOMContentLoaded', iniciar);
})();
