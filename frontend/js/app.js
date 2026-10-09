// Módulo comum das páginas internas do DIEESE 360: cliente Supabase, sessão,
// perfil e encerramento por inatividade. Adaptado de painel_saude_mental/painel-web
// (mesmo padrão, ver docs/08-decisoes-adr/0005-...) — sem o sistema de rascunho
// automático nem papéis/perfis múltiplos, que esta primeira versão não usa.
(function () {
  'use strict';

  var cfg = window.PAINEL_CONFIG || {};

  var sb = null;
  if (cfg.SUPABASE_URL && cfg.SUPABASE_PUBLISHABLE_KEY && window.supabase && window.supabase.createClient) {
    sb = window.supabase.createClient(cfg.SUPABASE_URL, cfg.SUPABASE_PUBLISHABLE_KEY, {
      auth: { persistSession: true, autoRefreshToken: true, detectSessionInUrl: true }
    });
  }

  function esc(s) {
    return String(s == null ? '' : s).replace(/[&<>"']/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
    });
  }

  function mensagemErro(e) {
    var m = (e && (e.message || e.error_description)) || String(e || 'Erro desconhecido');
    if (/row-level security|permission denied|42501/i.test(m)) return 'Você não tem permissão para esta operação.';
    if (/Failed to fetch|NetworkError|Load failed/i.test(m)) return 'Sem conexão com o servidor. Tente de novo.';
    if (/JWT expired|invalid JWT/i.test(m)) return 'Sua sessão expirou. Entre de novo.';
    return m;
  }

  function irParaLogin(motivo) {
    var q = motivo ? '?' + motivo + '=1' : '';
    window.location.replace('login.html' + q);
  }

  var tempoLimite = null;
  function reiniciarInatividade() {
    var minutos = Number(cfg.INATIVIDADE_MINUTOS) || 30;
    clearTimeout(tempoLimite);
    tempoLimite = setTimeout(function () { sair('inatividade'); }, minutos * 60 * 1000);
  }
  function vigiarInatividade() {
    ['click', 'keydown', 'mousemove', 'touchstart', 'scroll'].forEach(function (ev) {
      window.addEventListener(ev, throttle(reiniciarInatividade, 5000), { passive: true });
    });
    reiniciarInatividade();
  }
  function throttle(fn, ms) {
    var ultimo = 0;
    return function () { var agora = Date.now(); if (agora - ultimo > ms) { ultimo = agora; fn(); } };
  }

  function sair(motivo) {
    var fim = function () { irParaLogin(motivo); };
    if (!sb) return fim();
    sb.auth.signOut().then(fim, fim);
  }

  // Exige sessão e perfil ativo. Resolve com { user, perfil } ou redireciona.
  function exigirSessao() {
    if (!sb) {
      mostrarFalhaConfig();
      return new Promise(function () {});
    }
    return sb.auth.getSession().then(function (r) {
      var sessao = r && r.data && r.data.session;
      if (!sessao) { irParaLogin(); return new Promise(function () {}); }
      return sb.from('perfis').select('id, nome, email, ativo').eq('id', sessao.user.id).maybeSingle()
        .then(function (res) {
          var p = res && res.data;
          if (!p || !p.ativo) {
            return sb.auth.signOut().then(function () { irParaLogin('sem-acesso'); return new Promise(function () {}); });
          }
          montarTopo(p);
          vigiarInatividade();
          return { user: sessao.user, perfil: p };
        });
    });
  }

  function montarTopo(p) {
    var nome = document.getElementById('usuario-nome');
    if (nome) nome.textContent = p.nome;
    var btn = document.getElementById('sair');
    if (btn) btn.addEventListener('click', function (e) { e.preventDefault(); sair(); });
  }

  function mostrarFalhaConfig() {
    var div = document.createElement('div');
    div.className = 'aviso demo';
    div.style.margin = '24px';
    div.textContent = 'O painel não conseguiu iniciar a conexão com o Supabase. Confira js/config.js e se js/vendor/supabase.js carregou.';
    document.body.prepend(div);
  }

  function aviso(texto, tipo) {
    var el = document.getElementById('toast');
    if (!el) {
      el = document.createElement('div');
      el.id = 'toast';
      el.setAttribute('role', 'status');
      el.setAttribute('aria-live', 'polite');
      document.body.appendChild(el);
    }
    el.className = 'toast ' + (tipo || '');
    el.textContent = texto;
    el.hidden = false;
    clearTimeout(aviso._t);
    aviso._t = setTimeout(function () { el.hidden = true; }, 5000);
  }

  window.Painel = {
    sb: sb,
    cfg: cfg,
    esc: esc,
    mensagemErro: mensagemErro,
    exigirSessao: exigirSessao,
    sair: sair,
    aviso: aviso,
    irParaLogin: irParaLogin
  };
})();
