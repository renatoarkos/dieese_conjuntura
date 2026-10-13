// Orquestração do painel interno (painel.html): exige sessão, monta a barra
// lateral (ver barra-lateral.js) e uma seção por dimensão, cada uma com a
// grade de cartões-resumo — cada cartão é um link para a página própria do
// indicador (indicador.html?id=..., ver pagina-indicador.js). Este arquivo
// não decide mais nada sobre como mostrar um indicador específico (mapa,
// gráfico etc.) — isso é responsabilidade exclusiva da página do indicador.
(function () {
  'use strict';
  var P = window.Painel;
  var D = window.DIEESE360.dados;
  var esc = P.esc;

  var ORDEM_DIMENSOES = ['macroeconomia', 'monetario_credito', 'inflacao', 'mercado_trabalho', 'caged'];

  function montarSecoesVazias() {
    var raiz = document.getElementById('secoes-dimensao');
    raiz.innerHTML = ORDEM_DIMENSOES.map(function (chave) {
      var dim = D.DIMENSOES[chave];
      return '<section class="secao-dimensao" id="' + chave + '"><h2>' + esc(dim.nome) + '</h2><p class="lead">' + esc(dim.descricao) + '</p><div class="grade-indicadores" id="grade-' + chave + '"></div></section>';
    }).join('');
  }

  function carregarEMontarGrade(chave, indicadoresDim) {
    var grade = document.getElementById('grade-' + chave);
    if (!indicadoresDim.length) { grade.innerHTML = D.montarCartaoDimensaoPendente(chave); return Promise.resolve(); }
    var ids = indicadoresDim.map(function (i) { return i.id; });
    return Promise.all(ids.map(function (id) { return D.carregarSerie(id, 24); })).then(function (listas) {
      var series = {};
      ids.forEach(function (id, i) { series[id] = listas[i]; });
      grade.innerHTML = indicadoresDim.map(function (ind) { return D.montarCartao(ind, series[ind.id] || []); }).join('');
      window.DIEESE360.animarEntrada(grade);
    });
  }

  function iniciar() {
    D.carregarIndicadores().then(function (indicadores) {
      window.DIEESE360.montarBarraLateral(document.getElementById('barra-lateral'), indicadores, null);

      var porDimensao = {};
      ORDEM_DIMENSOES.forEach(function (c) { porDimensao[c] = []; });
      indicadores.forEach(function (i) { if (porDimensao[i.dimensao]) porDimensao[i.dimensao].push(i); });

      montarSecoesVazias();
      return Promise.all(ORDEM_DIMENSOES.map(function (chave) { return carregarEMontarGrade(chave, porDimensao[chave]); }));
    }).catch(function (erro) {
      document.getElementById('conteudo-painel').innerHTML = '<p class="aviso demo">' + esc(P.mensagemErro(erro)) + '</p>';
    });
  }

  P.exigirSessao().then(function () { iniciar(); });
})();
