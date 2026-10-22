// Configuração PÚBLICA do projeto Supabase. É seguro versionar e servir ao navegador.
// A chave "publishable" só funciona dentro das regras de permissão (RLS) do banco —
// `indicadores`/`indicadores_serie` têm leitura pública por decisão (ver ADR 0005);
// `perfis` só permite cada pessoa ler o próprio registro.
//
// NUNCA coloque aqui a chave secreta (sb_secret_...) nem a service_role.
window.PAINEL_CONFIG = {
  SUPABASE_URL: 'https://gdggtyioygsmehnvzxvc.supabase.co',
  SUPABASE_PUBLISHABLE_KEY: 'sb_publishable_pdacpz0yHuHztDx3fnNR6g_FtLN3xBv',
  // Minutos sem uso até a sessão da área interna encerrar sozinha.
  INATIVIDADE_MINUTOS: 30
};
