// DIEESE 360 — página de exploração de microdado do Novo CAGED (caged.html):
// mesmo padrão de rais.js, ver comentário lá. Admissão/desligamento/saldo em
// vez de estoque, competência (AAAAMM) em vez de ano.
(function () {
  'use strict';
  var P = window.Painel;
  var esc = P.esc;
  var M = window.DIEESE360.microdados;

  var estado = { corte: 'uf', uf: '', competencia: '' };

  var CORTES = {
    uf: {
      rpc: 'caged_por_uf',
      colunas: ['UF', 'Admissões', 'Desligamentos', 'Saldo', 'Salário médio admissão (real)'],
      linha: function (l) {
        return [M.rotuloUf(l.uf), M.formatarInteiro(l.admissoes), M.formatarInteiro(l.desligamentos), M.formatarInteiro(l.saldo), M.formatarReais(l.salario_medio_admissao_real)];
      }
    },
    cbo: {
      rpc: 'caged_por_cbo',
      colunas: ['Ocupação (grande grupo CBO)', 'Admissões', 'Desligamentos', 'Saldo', 'Salário médio admissão (real)'],
      linha: function (l) {
        return [M.rotuloCbo(l.cbo_grande_grupo), M.formatarInteiro(l.admissoes), M.formatarInteiro(l.desligamentos), M.formatarInteiro(l.saldo), M.formatarReais(l.salario_medio_admissao_real)];
      }
    },
    cnae: {
      rpc: 'caged_por_cnae',
      colunas: ['Seção CNAE 2.0 (código)', 'Admissões', 'Desligamentos', 'Saldo', 'Salário médio admissão (real)'],
      linha: function (l) {
        return ['Seção ' + esc(l.cnae_secao || '—'), M.formatarInteiro(l.admissoes), M.formatarInteiro(l.desligamentos), M.formatarInteiro(l.saldo), M.formatarReais(l.salario_medio_admissao_real)];
      }
    },
    sexo: {
      rpc: 'caged_por_sexo',
      colunas: ['Sexo', 'Admissões', 'Desligamentos', 'Saldo', 'Salário médio admissão (real)'],
      linha: function (l) {
        return [M.rotuloSexo(l.sexo_codigo), M.formatarInteiro(l.admissoes), M.formatarInteiro(l.desligamentos), M.formatarInteiro(l.saldo), M.formatarReais(l.salario_medio_admissao_real)];
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

    var params = {};
    if (estado.competencia && /^\d{6}$/.test(estado.competencia)) params.p_competencia = estado.competencia;
    if (estado.corte !== 'uf' && estado.uf) params.p_uf = estado.uf;

    document.getElementById('micro-cabecalho').innerHTML = corte.colunas.map(function (c) { return '<th>' + esc(c) + '</th>'; }).join('');

    M.chamarRpc(corte.rpc, params).then(function (linhas) {
      var corpo = document.getElementById('micro-corpo');
      if (!linhas.length) {
        corpo.innerHTML = '<tr><td colspan="' + corte.colunas.length + '">Nenhum registro encontrado — a carga do microdado pode ainda não ter terminado, ou a competência informada não existe.</td></tr>';
        status.textContent = '';
        return;
      }
      corpo.innerHTML = linhas.map(function (l) {
        return '<tr>' + corte.linha(l).map(function (v) { return '<td>' + v + '</td>'; }).join('') + '</tr>';
      }).join('');
      status.textContent = linhas.length + ' linha(s)' + (estado.competencia ? ', competência ' + estado.competencia : ', todos os meses carregados') + '.';
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
    var debounce;
    document.getElementById('micro-competencia').addEventListener('input', function (e) {
      clearTimeout(debounce);
      debounce = setTimeout(function () {
        estado.competencia = e.target.value.trim();
        carregar();
      }, 500);
    });
    carregar();
  }

  P.exigirSessao().then(function () { iniciar(); });
})();
