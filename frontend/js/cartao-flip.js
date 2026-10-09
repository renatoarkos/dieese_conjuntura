// Cartão giratório in-place: clique (ou Enter/Espaço) vira o cartão no próprio
// lugar da grade, mostrando o verso (explicação/fonte/comparação). Mais simples
// que o `cartao-giratorio.js` de painel_saude_mental (que "voa" o cartão até o
// centro da tela como um modal) — aqui não precisa de modal, o cartão já é
// pequeno o bastante para virar sem sair do lugar. Delegado em `document`
// porque os cartões são inseridos dinamicamente por dados.js.
(function () {
  'use strict';

  function virar(interior) {
    var cartao = interior.closest('.cartao-flip');
    var vai_virar = !cartao.classList.contains('virado');
    cartao.classList.toggle('virado', vai_virar);
    interior.setAttribute('aria-pressed', vai_virar ? 'true' : 'false');
  }

  document.addEventListener('click', function (e) {
    var interior = e.target.closest('.cartao-flip-interior');
    if (interior) virar(interior);
  });

  document.addEventListener('keydown', function (e) {
    if (e.key !== 'Enter' && e.key !== ' ') return;
    var interior = e.target.closest('.cartao-flip-interior');
    if (!interior) return;
    e.preventDefault();
    virar(interior);
  });
})();
