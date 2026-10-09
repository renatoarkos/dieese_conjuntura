// Animação de entrada do painel: os cartões surgem em sequência, os números
// contam do zero até o valor, e a linha da sparkline se desenha. Adaptado de
// painel_saude_mental/painel-web/js/animacao-dash.js (mesma técnica — ver lá
// para a versão original, com barras/listas que este painel não usa).
// Uso: DIEESE360.animarEntrada(elementoRaiz) — pode ser chamado de novo para
// repetir a animação (ex. depois de trocar de aba de dimensão).
(function () {
  'use strict';

  function reduz() { return !!(window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches); }

  function tracarSparklines(raiz, atraso) {
    Array.prototype.forEach.call(raiz.querySelectorAll('.cartao-sparkline path.linha'), function (l) {
      if (!l.getTotalLength) return;
      var len = Math.ceil(l.getTotalLength());
      l.style.transition = 'none'; l.style.strokeDasharray = len; l.style.strokeDashoffset = len;
      void l.getBoundingClientRect();
      l.style.transition = 'stroke-dashoffset 1.1s cubic-bezier(.4,.1,.2,1) ' + atraso + 'ms';
      l.style.strokeDashoffset = 0;
    });
    Array.prototype.forEach.call(raiz.querySelectorAll('.cartao-sparkline .area, .cartao-sparkline circle'), function (p) {
      p.style.transition = 'none'; p.style.opacity = '0';
      void p.getBoundingClientRect();
      p.style.transition = 'opacity .6s ease ' + (atraso + 500) + 'ms';
      p.style.opacity = '';
    });
  }

  function animarEntrada(raiz) {
    if (!raiz || reduz()) return;
    var cartoes = Array.prototype.slice.call(raiz.querySelectorAll('.cartao-flip, .cartao-dimensao, .cartao-pendente'));
    cartoes.forEach(function (c, i) {
      var atraso = i * 90;
      c.classList.remove('anim-cartao'); void c.offsetWidth;
      c.style.animationDelay = atraso + 'ms';
      c.classList.add('anim-cartao');
      var fim = function () { c.classList.remove('anim-cartao'); c.style.animationDelay = ''; };
      c.addEventListener('animationend', fim, { once: true });
      setTimeout(fim, atraso + 1200);
      tracarSparklines(c, atraso + 300);
    });
  }

  window.DIEESE360 = window.DIEESE360 || {};
  window.DIEESE360.animarEntrada = animarEntrada;
})();
