// Mapa de calor (treemap) genérico, em SVG puro — sem nenhuma biblioteca de
// gráficos nova, mesmo princípio de grafico-linha.js (desenha à mão). Usado
// hoje só pela página de mercados (mercados.html, dimensão "mercados", ver
// ADR 0010 Fase 2), mas escrito sem nenhuma dependência de mercados
// especificamente — recebe {rotulo, valor, cor} e desenha.
//
// Algoritmo "squarify" (Bruls, Huizing, van Wijk, 2000): a cada passo, monta
// uma fileira de blocos tentando manter a proporção largura/altura de cada
// bloco o mais próxima de 1:1 possível, encaixando a fileira no lado mais
// curto do espaço restante. É o mesmo princípio usado por Finviz/TradingView
// para o mapa de calor de ações (ver
// research/notas/INVENTARIO_BENCHMARK_MERCADOS_FINANCEIROS.md, seção 3.8).
(function () {
  'use strict';

  // ------------------------------------------------------------------
  // Squarify — recebe itens com `.valor` (todos > 0) já ordenados
  // decrescente, e a área disponível; devolve os mesmos itens com
  // `.x/.y/.largura/.altura` preenchidos (mesma unidade da área recebida).
  // ------------------------------------------------------------------
  function piorRazao(fileira, ladoCurto, areaFileira) {
    var maxA = -Infinity, minA = Infinity;
    fileira.forEach(function (it) {
      if (it._area > maxA) maxA = it._area;
      if (it._area < minA) minA = it._area;
    });
    var s2 = ladoCurto * ladoCurto;
    var a2 = areaFileira * areaFileira;
    return Math.max((s2 * maxA) / a2, a2 / (s2 * minA));
  }

  function squarify(itens, x, y, largura, altura) {
    if (!itens.length) return itens;
    var areaTotal = largura * altura;
    var somaValores = itens.reduce(function (s, it) { return s + it.valor; }, 0);
    if (somaValores <= 0) return itens;
    var escala = areaTotal / somaValores;
    var restantes = itens.map(function (it) { it._area = it.valor * escala; return it; });

    var rx = x, ry = y, rw = largura, rh = altura;
    var i = 0;
    while (i < restantes.length) {
      var fileira = [restantes[i]];
      var areaFileira = restantes[i]._area;
      var ladoCurto = Math.min(rw, rh);
      var melhorRazao = piorRazao(fileira, ladoCurto, areaFileira);
      var j = i + 1;
      while (j < restantes.length) {
        var testeFileira = fileira.concat([restantes[j]]);
        var testeArea = areaFileira + restantes[j]._area;
        var testeRazao = piorRazao(testeFileira, ladoCurto, testeArea);
        if (testeRazao <= melhorRazao) {
          fileira = testeFileira; areaFileira = testeArea; melhorRazao = testeRazao; j++;
        } else break;
      }
      if (rw >= rh) {
        var colLargura = rh > 0 ? areaFileira / rh : 0;
        var cy = ry;
        fileira.forEach(function (it) {
          var itAltura = colLargura > 0 ? it._area / colLargura : 0;
          it.x = rx; it.y = cy; it.largura = colLargura; it.altura = itAltura;
          cy += itAltura;
        });
        rx += colLargura; rw -= colLargura;
      } else {
        var linhaAltura = rw > 0 ? areaFileira / rw : 0;
        var cx = rx;
        fileira.forEach(function (it) {
          var itLargura = linhaAltura > 0 ? it._area / linhaAltura : 0;
          it.x = cx; it.y = ry; it.largura = itLargura; it.altura = linhaAltura;
          cx += itLargura;
        });
        ry += linhaAltura; rh -= linhaAltura;
      }
      i += fileira.length;
    }
    return itens;
  }

  window.DIEESE360 = window.DIEESE360 || {};
  window.DIEESE360.treemap = { squarify: squarify };
})();
