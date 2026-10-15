// DIEESE 360 — página de exploração de microdado da RAIS (rais.html):
// filtros (corte + UF) chamando as funções RPC do Postgres (ver
// db/migrations/0007_microdados_rais_caged.sql), resultado agregado em
// tabela — o navegador nunca baixa os ~58 milhões de vínculos crus.
(function () {
  'use strict';
  var P = window.Painel;
  var esc = P.esc;
  var M = window.DIEESE360.microdados;

  var ANO = 2024;
  var estado = { corte: 'uf', uf: '' };

  var CORTES = {
    uf: {
      rpc: 'rais_por_uf',
      colunas: ['UF', 'Vínculos ativos', 'Remuneração média nominal', 'Remuneração média real'],
      linha: function (l) {
        return [M.rotuloUf(l.uf), M.formatarInteiro(l.vinculos), M.formatarReais(l.remuneracao_media_nominal), M.formatarReais(l.remuneracao_media_real)];
      }
    },
    cbo: {
      rpc: 'rais_por_cbo',
      colunas: ['Ocupação (grande grupo CBO)', 'Vínculos ativos', 'Remuneração média nominal', 'Remuneração média real'],
      linha: function (l) {
        return [M.rotuloCbo(l.cbo_grande_grupo), M.formatarInteiro(l.vinculos), M.formatarReais(l.remuneracao_media_nominal), M.formatarReais(l.remuneracao_media_real)];
      }
    },
    cnae: {
      rpc: 'rais_por_cnae',
      colunas: ['Divisão CNAE 2.0 (código)', 'Vínculos ativos', 'Remuneração média nominal', 'Remuneração média real'],
      linha: function (l) {
        return ['Divisão ' + esc(l.cnae_divisao || '—'), M.formatarInteiro(l.vinculos), M.formatarReais(l.remuneracao_media_nominal), M.formatarReais(l.remuneracao_media_real)];
      }
    },
    sexo: {
      rpc: 'rais_por_sexo_faixa_etaria',
      colunas: ['Sexo', 'Faixa etária (código)', 'Vínculos ativos', 'Remuneração média real'],
      linha: function (l) {
        return [M.rotuloSexo(l.sexo_codigo), 'Faixa ' + (l.faixa_etaria_codigo != null ? l.faixa_etaria_codigo : '—'), M.formatarInteiro(l.vinculos), M.formatarReais(l.remuneracao_media_real)];
      }
    }
  };

  function montarUfs() {
    var alvo = document.getElementById('micro-uf');
    M.listaUfs().forEach(function (uf) {
      var opt = document.createElement('option');
      opt.value = uf.codigo;
      opt.textContent = uf.sigla;
      alvo.appendChild(opt);
    });
  }

  function carregar() {
    var corte = CORTES[estado.corte];
    var status = document.getElementById('micro-status');
    var campoUf = document.getElementById('micro-campo-uf');
    campoUf.style.display = estado.corte === 'uf' ? 'none' : '';
    status.textContent = 'Carregando…';

    var params = { p_ano: ANO };
    if (estado.corte !== 'uf' && estado.uf) params.p_uf = estado.uf;

    document.getElementById('micro-cabecalho').innerHTML = corte.colunas.map(function (c) { return '<th>' + esc(c) + '</th>'; }).join('');

    M.chamarRpc(corte.rpc, params).then(function (linhas) {
      var corpo = document.getElementById('micro-corpo');
      if (!linhas.length) {
        corpo.innerHTML = '<tr><td colspan="' + corte.colunas.length + '">Nenhum registro encontrado — a carga do microdado pode ainda não ter terminado.</td></tr>';
        status.textContent = '';
        return;
      }
      corpo.innerHTML = linhas.map(function (l) {
        return '<tr>' + corte.linha(l).map(function (v) { return '<td>' + v + '</td>'; }).join('') + '</tr>';
      }).join('');
      status.textContent = linhas.length + ' linha(s), ano-base ' + ANO + '.';
    }).catch(function (erro) {
      document.getElementById('micro-corpo').innerHTML = '<tr><td colspan="' + corte.colunas.length + '">' + esc(P.mensagemErro(erro)) + '</td></tr>';
      status.textContent = '';
    });
  }

  function iniciar() {
    montarUfs();
    document.getElementById('micro-corte').addEventListener('change', function (e) {
      estado.corte = e.target.value;
      carregar();
    });
    document.getElementById('micro-uf').addEventListener('change', function (e) {
      estado.uf = e.target.value;
      carregar();
    });
    carregar();
  }

  P.exigirSessao().then(function () { iniciar(); });
})();
