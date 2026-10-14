// DIEESE 360 — Catálogo Mestre de Indicadores (catalogo.html): lista densa e
// filtrável de todos os indicadores publicados, com fonte/periodicidade/
// classificação visíveis sem precisar abrir a página de cada um. Pública —
// os metadados de catálogo são públicos (ADR 0005), só a navegação interna
// por dimensão fica atrás do login.
(function () {
  'use strict';
  var P = window.Painel;
  var D = window.DIEESE360.dados;
  var esc = P.esc;

  var estado = { indicadores: [], busca: '', dimensao: 'todas' };

  function montarFiltros(indicadores) {
    var dimensoesPresentes = [];
    indicadores.forEach(function (i) {
      if (dimensoesPresentes.indexOf(i.dimensao) === -1) dimensoesPresentes.push(i.dimensao);
    });
    var alvo = document.getElementById('catalogo-filtros');
    var botoes = [{ chave: 'todas', rotulo: 'Todas' }].concat(
      dimensoesPresentes.map(function (d) { return { chave: d, rotulo: (D.DIMENSOES[d] || {}).nome || d }; })
    );
    alvo.innerHTML = botoes.map(function (b) {
      return '<button type="button" class="catalogo-filtro-botao' + (b.chave === estado.dimensao ? ' ativo' : '') + '" data-dimensao="' + esc(b.chave) + '">' + esc(b.rotulo) + '</button>';
    }).join('');
    alvo.querySelectorAll('button').forEach(function (btn) {
      btn.addEventListener('click', function () {
        estado.dimensao = btn.dataset.dimensao;
        alvo.querySelectorAll('button').forEach(function (b) { b.classList.remove('ativo'); });
        btn.classList.add('ativo');
        renderizar();
      });
    });
  }

  function linhasFiltradas() {
    var termo = estado.busca.trim().toLowerCase();
    return estado.indicadores.filter(function (i) {
      if (estado.dimensao !== 'todas' && i.dimensao !== estado.dimensao) return false;
      if (!termo) return true;
      return (i.nome + ' ' + i.fonte).toLowerCase().indexOf(termo) >= 0;
    });
  }

  function renderizar() {
    var linhas = linhasFiltradas();
    document.getElementById('catalogo-contagem').textContent =
      linhas.length + (linhas.length === 1 ? ' indicador encontrado' : ' indicadores encontrados') +
      (estado.indicadores.length ? ' de ' + estado.indicadores.length + ' no catálogo' : '');

    var corpo = document.getElementById('catalogo-corpo');
    if (!linhas.length) {
      corpo.innerHTML = '<tr><td colspan="5">Nenhum indicador bate com esse filtro.</td></tr>';
      return;
    }
    corpo.innerHTML = linhas.map(function (i) {
      return (
        '<tr>' +
        '<td><a href="indicador.html?id=' + esc(i.id) + '">' + esc(i.nome) + '</a></td>' +
        '<td>' + esc((D.DIMENSOES[i.dimensao] || {}).nome || i.dimensao) + '</td>' +
        '<td>' + esc(i.fonte) + '</td>' +
        '<td>' + esc(i.periodicidade) + '</td>' +
        '<td><span class="catalogo-classif">' + esc(i.classificacao) + '</span></td>' +
        '</tr>'
      );
    }).join('');
  }

  function iniciar() {
    if (!P.sb) {
      document.getElementById('catalogo-corpo').innerHTML = '<tr><td colspan="5">Não foi possível conectar ao Supabase.</td></tr>';
      return;
    }
    D.carregarIndicadores().then(function (indicadores) {
      estado.indicadores = indicadores;
      montarFiltros(indicadores);
      renderizar();
    }).catch(function (erro) {
      document.getElementById('catalogo-corpo').innerHTML = '<tr><td colspan="5">' + esc(P.mensagemErro(erro)) + '</td></tr>';
    });

    document.getElementById('catalogo-busca').addEventListener('input', function (e) {
      estado.busca = e.target.value;
      renderizar();
    });
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', iniciar); else iniciar();
})();
