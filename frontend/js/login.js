// Tela de login: e-mail e senha pelo Supabase Auth. Adaptado de
// painel_saude_mental/painel-web/js/login.js.
(function () {
  'use strict';
  var P = window.Painel;
  var sb = P && P.sb;
  var msg = document.getElementById('msg');

  function mostrar(texto, tipo) {
    msg.textContent = texto;
    msg.className = 'aviso' + (tipo === 'demo' ? ' demo' : '');
    msg.hidden = !texto;
  }

  var params = new URLSearchParams(window.location.search);
  if (params.get('sem-acesso')) mostrar('Sua conta ainda não tem acesso ao painel. Fale com a administração da plataforma.', 'demo');
  else if (params.get('inatividade')) mostrar('Sua sessão foi encerrada por inatividade. Entre de novo.');
  else if (params.get('senha-definida')) mostrar('Senha definida. Entre com seu e-mail e a nova senha.');

  if (!sb) {
    mostrar('O painel não conseguiu iniciar a conexão com o Supabase. Confira js/config.js.', 'demo');
    return;
  }

  sb.auth.getSession().then(function (r) {
    if (r.data && r.data.session) window.location.replace('painel.html');
  });

  var form = document.getElementById('form-login');
  var botao = document.getElementById('entrar');
  form.addEventListener('submit', function (e) {
    e.preventDefault();
    var email = document.getElementById('email').value.trim();
    var senha = document.getElementById('senha').value;
    if (!email || !senha) { mostrar('Informe o e-mail e a senha.'); return; }
    botao.disabled = true;
    mostrar('');
    sb.auth.signInWithPassword({ email: email, password: senha }).then(function (r) {
      if (r.error) {
        botao.disabled = false;
        mostrar(/rate|too many/i.test(r.error.message || '')
          ? 'Muitas tentativas. Aguarde alguns minutos e tente de novo.'
          : 'E-mail ou senha incorretos.');
        document.getElementById('senha').value = '';
        return;
      }
      window.location.replace('painel.html');
    }, function () {
      botao.disabled = false;
      mostrar('Sem conexão com o servidor. Tente de novo.');
    });
  });

  document.getElementById('esqueci').addEventListener('click', function (e) {
    e.preventDefault();
    var email = document.getElementById('email').value.trim();
    if (!email) { mostrar('Digite seu e-mail no campo acima e clique de novo em "Esqueci minha senha".'); return; }
    var destino = window.location.origin + window.location.pathname.replace(/[^/]*$/, '') + 'definir-senha.html';
    sb.auth.resetPasswordForEmail(email, { redirectTo: destino }).then(function () {
      mostrar('Se o e-mail estiver cadastrado, você receberá um link para criar uma nova senha.');
    }, function () {
      mostrar('Não foi possível enviar agora. Tente de novo em alguns minutos.');
    });
  });
})();
