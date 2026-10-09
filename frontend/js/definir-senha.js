// Convite e recuperação de senha: o Supabase envia um link com a sessão
// temporária no endereço. Adaptado de
// painel_saude_mental/painel-web/js/definir-senha.js (sem alteração de lógica).
(function () {
  'use strict';
  var P = window.Painel;
  var sb = P && P.sb;
  var msg = document.getElementById('msg');
  var form = document.getElementById('form-senha');

  function mostrar(texto) { msg.textContent = texto; msg.hidden = !texto; }

  if (!sb) { mostrar('O painel não conseguiu iniciar a conexão com o Supabase.'); return; }

  var pronto = false;
  function liberar() {
    if (pronto) return;
    pronto = true;
    mostrar('');
    form.hidden = false;
    document.getElementById('nova').focus();
  }

  sb.auth.onAuthStateChange(function (evento, sessao) {
    if (sessao && (evento === 'PASSWORD_RECOVERY' || evento === 'SIGNED_IN' || evento === 'INITIAL_SESSION')) liberar();
  });
  sb.auth.getSession().then(function (r) { if (r.data && r.data.session) liberar(); });
  setTimeout(function () {
    if (!pronto) mostrar('Este link é inválido ou expirou. Peça um novo convite ou use "Esqueci minha senha" no login.');
  }, 4000);

  form.addEventListener('submit', function (e) {
    e.preventDefault();
    var nova = document.getElementById('nova').value;
    var conf = document.getElementById('confirma').value;
    if (nova.length < 12) { mostrar('A senha precisa ter pelo menos 12 caracteres.'); return; }
    if (nova !== conf) { mostrar('As duas senhas não são iguais.'); return; }
    var botao = document.getElementById('salvar');
    botao.disabled = true;
    sb.auth.updateUser({ password: nova }).then(function (r) {
      if (r.error) {
        botao.disabled = false;
        mostrar(/weak|pwned|compromised|should be/i.test(r.error.message || '')
          ? 'Esta senha é fraca ou já apareceu em vazamentos. Escolha outra.'
          : 'Não foi possível salvar a senha. Tente de novo.');
        return;
      }
      sb.auth.signOut().then(function () { window.location.replace('login.html?senha-definida=1'); });
    });
  });
})();
