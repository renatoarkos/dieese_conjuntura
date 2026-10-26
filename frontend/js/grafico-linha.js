// DIEESE 360 — gráfico de linha para a série histórica completa de um
// indicador (usado no painel de detalhe, ver detalhe-indicador.js). Segue a
// especificação da skill de dataviz deste projeto: linha 2px, área a ~10% de
// opacidade, marcador final >=8px, grade horizontal em cinza recessivo,
// rótulo direto no último ponto, crosshair + tooltip no hover (readout com o
// valor em destaque e a data secundária). "Trend over time -> line" —
// references/choosing-a-form.md.
(function () {
  'use strict';

  function reduz() { return !!(window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches); }

  // Escolhe ~4 valores "redondos" para as linhas de grade do eixo Y, dado o
  // intervalo real da série — evita números quebrados tipo "37,42".
  function ticksEixoY(min, max) {
    var intervalo = max - min || 1;
    var passoBruto = intervalo / 4;
    var ordem = Math.pow(10, Math.floor(Math.log10(passoBruto)));
    var passo = Math.ceil(passoBruto / ordem) * ordem;
    var inicio = Math.floor(min / passo) * passo;
    var ticks = [];
    for (var v = inicio; v <= max + passo * 0.01; v += passo) ticks.push(Math.round(v * 1000) / 1000);
    return ticks;
  }

  function montarGraficoLinha(container, serieAsc, opcoes) {
    opcoes = opcoes || {};
    var formatarValor = opcoes.formatarValor || function (v) { return String(v); };
    var formatarData = opcoes.formatarData || function (d) { return d; };

    if (!serieAsc || serieAsc.length < 2) {
      container.innerHTML = '<p class="aviso demo">Pontos insuficientes para desenhar um gráfico (mínimo 2).</p>';
      return;
    }

    var L = 640, A = 300, ML = 56, MR = 16, MT = 16, MB = 32; // margens para caber o eixo
    var valores = serieAsc.map(function (p) { return p.valor; });
    var min = Math.min.apply(null, valores), max = Math.max.apply(null, valores);
    if (min === max) { min -= 1; max += 1; } // evita divisão por zero numa série plana
    var ticksY = ticksEixoY(min, max);
    var minEixo = Math.min(min, ticksY[0]), maxEixo = Math.max(max, ticksY[ticksY.length - 1]);

    var larguraUtil = L - ML - MR, alturaUtil = A - MT - MB;
    function x(i) { return ML + (i / (serieAsc.length - 1)) * larguraUtil; }
    function y(v) { return MT + alturaUtil - ((v - minEixo) / (maxEixo - minEixo)) * alturaUtil; }

    // Posição X de uma data arbitrária (não precisa ser um ponto exato da
    // série) — interpola linearmente entre os dois pontos mais próximos pelo
    // índice. Usado pelos marcadores verticais (opcoes.marcadores), que
    // marcam datas de transição de governo, não pontos de dado.
    function xPelaData(dataIso) {
      var alvo = new Date(dataIso + 'T00:00:00').getTime();
      var primeira = new Date(serieAsc[0].data_referencia + 'T00:00:00').getTime();
      var ultima = new Date(serieAsc[serieAsc.length - 1].data_referencia + 'T00:00:00').getTime();
      if (alvo <= primeira) return x(0);
      if (alvo >= ultima) return x(serieAsc.length - 1);
      for (var i = 0; i < serieAsc.length - 1; i++) {
        var t1 = new Date(serieAsc[i].data_referencia + 'T00:00:00').getTime();
        var t2 = new Date(serieAsc[i + 1].data_referencia + 'T00:00:00').getTime();
        if (alvo >= t1 && alvo <= t2) {
          var fracao = t2 > t1 ? (alvo - t1) / (t2 - t1) : 0;
          return x(i) + fracao * (x(i + 1) - x(i));
        }
      }
      return x(serieAsc.length - 1);
    }

    var pontosXY = serieAsc.map(function (p, i) { return [x(i), y(p.valor)]; });
    var linha = pontosXY.map(function (p, i) { return (i === 0 ? 'M' : 'L') + p[0].toFixed(1) + ',' + p[1].toFixed(1); }).join(' ');
    var ultimo = pontosXY[pontosXY.length - 1];
    var area = linha + ' L' + ultimo[0].toFixed(1) + ',' + (MT + alturaUtil) + ' L' + pontosXY[0][0].toFixed(1) + ',' + (MT + alturaUtil) + ' Z';

    var svgns = 'http://www.w3.org/2000/svg';
    var svg = document.createElementNS(svgns, 'svg');
    svg.setAttribute('viewBox', '0 0 ' + L + ' ' + A);
    svg.setAttribute('class', 'grafico-linha');
    svg.setAttribute('role', 'img');
    svg.setAttribute('aria-label', 'Gráfico de linha da série histórica, de ' + formatarData(serieAsc[0].data_referencia) + ' a ' + formatarData(serieAsc[serieAsc.length - 1].data_referencia));

    var svgHtml = '';
    // grade + rótulos do eixo Y (hairline, recessivo — ver marks-and-anatomy.md)
    ticksY.forEach(function (v) {
      var ty = y(v);
      svgHtml += '<line class="grade" x1="' + ML + '" x2="' + (L - MR) + '" y1="' + ty.toFixed(1) + '" y2="' + ty.toFixed(1) + '"></line>';
      svgHtml += '<text class="rotulo-eixo" x="' + (ML - 8) + '" y="' + ty.toFixed(1) + '" text-anchor="end" dominant-baseline="middle">' + formatarValor(v) + '</text>';
    });
    // rótulos do eixo X: só início, meio e fim (evita poluir com uma data por ponto).
    // Início fica ancorado à esquerda e fim à direita do próprio ponto — senão o
    // texto centralizado nas pontas vaza para fora da viewBox.
    [[0, 'start'], [Math.floor((serieAsc.length - 1) / 2), 'middle'], [serieAsc.length - 1, 'end']].forEach(function (par) {
      var i = par[0], ancora = par[1];
      svgHtml += '<text class="rotulo-eixo" x="' + x(i).toFixed(1) + '" y="' + (A - 8) + '" text-anchor="' + ancora + '">' + formatarData(serieAsc[i].data_referencia) + '</text>';
    });

    // Marcadores verticais opcionais (ex. transições de governo, ver
    // D.GOVERNOS em js/dados.js) — linha tracejada + rótulo pequeno no topo,
    // só para datas que caem dentro do intervalo real da série (fora disso
    // não tem o que marcar). Desenhados antes da linha/área para ficarem
    // "atrás" do dado, nunca por cima dele.
    (opcoes.marcadores || []).forEach(function (m) {
      var tAlvo = new Date(m.data + 'T00:00:00').getTime();
      var tInicio = new Date(serieAsc[0].data_referencia + 'T00:00:00').getTime();
      var tFim = new Date(serieAsc[serieAsc.length - 1].data_referencia + 'T00:00:00').getTime();
      if (tAlvo <= tInicio || tAlvo >= tFim) return;
      var mx = xPelaData(m.data);
      svgHtml += '<line class="marcador-governo" x1="' + mx.toFixed(1) + '" x2="' + mx.toFixed(1) + '" y1="' + MT + '" y2="' + (MT + alturaUtil) + '"></line>';
      svgHtml += '<text class="marcador-governo-rotulo" x="' + mx.toFixed(1) + '" y="' + (MT - 4) + '">' + (m.rotulo ? String(m.rotulo).replace(/&/g, '&amp;').replace(/</g, '&lt;') : '') + '</text>';
    });

    svgHtml += '<path class="area" d="' + area + '"></path>';
    svgHtml += '<path class="linha" d="' + linha + '"></path>';
    svgHtml += '<circle class="ponto-final" cx="' + ultimo[0].toFixed(1) + '" cy="' + ultimo[1].toFixed(1) + '" r="4.5"></circle>';
    svgHtml += '<text class="rotulo-final" x="' + (ultimo[0] - 6).toFixed(1) + '" y="' + (ultimo[1] - 10).toFixed(1) + '" text-anchor="end">' + formatarValor(serieAsc[serieAsc.length - 1].valor) + '</text>';

    // crosshair (começa invisível, ver CSS .grafico-linha .crosshair) — "a X acerta, não o ponto" (interaction.md)
    svgHtml += '<line class="crosshair" x1="0" x2="0" y1="' + MT + '" y2="' + (MT + alturaUtil) + '" opacity="0"></line>';
    svgHtml += '<circle class="crosshair-ponto" r="4" opacity="0"></circle>';
    svgHtml += '<rect class="area-hover" x="' + ML + '" y="' + MT + '" width="' + larguraUtil + '" height="' + alturaUtil + '" fill="transparent"></rect>';

    svg.innerHTML = svgHtml;
    container.innerHTML = '';
    container.appendChild(svg);

    // tooltip de hover — mesmo princípio do mapa: valor em destaque, data secundária
    var tooltip = document.createElement('div');
    tooltip.className = 'grafico-tooltip';
    container.style.position = 'relative';
    container.appendChild(tooltip);

    var crosshair = svg.querySelector('.crosshair');
    var crosshairPonto = svg.querySelector('.crosshair-ponto');
    var areaHover = svg.querySelector('.area-hover');

    function indicePeloX(xSvg) {
      var i = Math.round(((xSvg - ML) / larguraUtil) * (serieAsc.length - 1));
      return Math.max(0, Math.min(serieAsc.length - 1, i));
    }

    areaHover.addEventListener('pointermove', function (e) {
      var ret = svg.getBoundingClientRect();
      var xSvg = ((e.clientX - ret.left) / ret.width) * L;
      var i = indicePeloX(xSvg);
      var px = pontosXY[i][0], py = pontosXY[i][1];
      crosshair.setAttribute('x1', px); crosshair.setAttribute('x2', px); crosshair.setAttribute('opacity', 1);
      crosshairPonto.setAttribute('cx', px); crosshairPonto.setAttribute('cy', py); crosshairPonto.setAttribute('opacity', 1);
      tooltip.innerHTML = '';
      var valorEl = document.createElement('strong');
      valorEl.textContent = formatarValor(serieAsc[i].valor);
      var dataEl = document.createElement('span');
      dataEl.textContent = formatarData(serieAsc[i].data_referencia);
      tooltip.appendChild(valorEl); tooltip.appendChild(dataEl);
      var xPct = (px / L) * 100, yPct = (py / A) * 100;
      tooltip.style.left = xPct + '%'; tooltip.style.top = yPct + '%';
      tooltip.classList.add('visivel');
    });
    areaHover.addEventListener('pointerleave', function () {
      crosshair.setAttribute('opacity', 0);
      crosshairPonto.setAttribute('opacity', 0);
      tooltip.classList.remove('visivel');
    });

    if (!reduz()) {
      var linhaEl = svg.querySelector('path.linha');
      var len = Math.ceil(linhaEl.getTotalLength());
      linhaEl.style.strokeDasharray = len; linhaEl.style.strokeDashoffset = len;
      void linhaEl.getBoundingClientRect();
      linhaEl.style.transition = 'stroke-dashoffset 1s cubic-bezier(.4,.1,.2,1)';
      linhaEl.style.strokeDashoffset = 0;
    }
  }

  window.DIEESE360 = window.DIEESE360 || {};
  window.DIEESE360.montarGraficoLinha = montarGraficoLinha;
})();
