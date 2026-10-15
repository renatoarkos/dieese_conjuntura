// DIEESE 360 — suporte compartilhado para as páginas de exploração de
// microdado (rais.html, caged.html): chamada às funções RPC do Postgres
// (ver db/migrations/0007_microdados_rais_caged.sql) e rótulos oficiais
// para os códigos de UF e CBO (grande grupo) — nenhum rótulo inventado,
// classificações já públicas do IBGE/MTE.
(function () {
  'use strict';
  var P = window.Painel;

  // Código IBGE de UF (2 primeiros dígitos do código de município) -> sigla.
  // Convenção oficial do IBGE, não inventada. "99" não é uma UF real — a
  // RAIS usa esse código para "não identificado"/UF ignorada.
  var UF_POR_CODIGO = {
    '11': 'RO', '12': 'AC', '13': 'AM', '14': 'RR', '15': 'PA', '16': 'AP', '17': 'TO',
    '21': 'MA', '22': 'PI', '23': 'CE', '24': 'RN', '25': 'PB', '26': 'PE', '27': 'AL', '28': 'SE', '29': 'BA',
    '31': 'MG', '32': 'ES', '33': 'RJ', '35': 'SP',
    '41': 'PR', '42': 'SC', '43': 'RS',
    '50': 'MS', '51': 'MT', '52': 'GO', '53': 'DF',
    '99': 'Não identificado'
  };

  // CBO 2002 — Grandes Grupos (1º dígito do código), classificação oficial
  // do Ministério do Trabalho (9 grupos + grupo 0).
  var CBO_GRANDE_GRUPO = {
    '0': 'Forças Armadas, policiais e bombeiros militares',
    '1': 'Membros superiores do poder público, dirigentes e gerentes',
    '2': 'Profissionais das ciências e das artes',
    '3': 'Técnicos de nível médio',
    '4': 'Trabalhadores de serviços administrativos',
    '5': 'Trabalhadores dos serviços, vendedores do comércio',
    '6': 'Trabalhadores agropecuários, florestais e da pesca',
    '7': 'Trabalhadores da produção de bens e serviços industriais (I)',
    '8': 'Trabalhadores da produção de bens e serviços industriais (II)',
    '9': 'Trabalhadores de manutenção e reparação'
  };

  var SEXO_RAIS_CAGED = { '1': 'Masculino', '2': 'Feminino', '3': 'Feminino' }; // RAIS usa 1/2, CAGED usa 1/3

  function rotuloUf(codigo) { return UF_POR_CODIGO[codigo] || codigo || '—'; }

  function listaUfs() {
    return Object.keys(UF_POR_CODIGO)
      .filter(function (c) { return c !== '99'; })
      .map(function (codigo) { return { codigo: codigo, sigla: UF_POR_CODIGO[codigo] }; })
      .sort(function (a, b) { return a.sigla.localeCompare(b.sigla); });
  }
  function rotuloCbo(grupo) { return grupo != null ? (CBO_GRANDE_GRUPO[grupo] || ('Grupo ' + grupo)) : '—'; }
  function rotuloSexo(codigo) { return SEXO_RAIS_CAGED[codigo] || ('Código ' + codigo); }

  function chamarRpc(nome, params) {
    if (!P.sb) return Promise.reject(new Error('Supabase não configurado.'));
    return P.sb.rpc(nome, params || {}).then(function (r) {
      if (r.error) throw r.error;
      return r.data || [];
    });
  }

  function formatarReais(v) {
    if (v == null) return '—';
    return 'R$ ' + Number(v).toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
  }

  function formatarInteiro(v) {
    if (v == null) return '—';
    return Number(v).toLocaleString('pt-BR');
  }

  window.DIEESE360 = window.DIEESE360 || {};
  window.DIEESE360.microdados = {
    rotuloUf: rotuloUf,
    listaUfs: listaUfs,
    rotuloCbo: rotuloCbo,
    rotuloSexo: rotuloSexo,
    chamarRpc: chamarRpc,
    formatarReais: formatarReais,
    formatarInteiro: formatarInteiro
  };
})();
