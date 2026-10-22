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

  var ORDEM_DIMENSOES = ['macroeconomia', 'monetario_credito', 'inflacao', 'mercado_trabalho', 'caged', 'mercados'];

  // Mesmos ícones já gerados para os cartões de dimensão da home (ver
  // js/inicio.js) — reaproveitados aqui para nenhuma seção do painel ficar
  // só com texto (pedido do responsável do projeto, 2026-10-14).
  var ICONES_DIMENSAO = {
    macroeconomia: 'assets/dimensoes/icone-macroeconomia.png',
    monetario_credito: 'assets/dimensoes/icone-monetario-credito.png',
    inflacao: 'assets/dimensoes/icone-inflacao.png',
    mercado_trabalho: 'assets/dimensoes/icone-mercado-trabalho.png',
    caged: 'assets/dimensoes/icone-caged.png'
    // 'mercados' sem ícone próprio ainda — ver mesma nota em js/inicio.js.
  };

  function montarSecoesVazias() {
    var raiz = document.getElementById('secoes-dimensao');
    raiz.innerHTML = ORDEM_DIMENSOES.map(function (chave) {
      var dim = D.DIMENSOES[chave];
      var icone = ICONES_DIMENSAO[chave] || '';
      return (
        '<section class="secao-dimensao" id="' + chave + '">' +
        '<div class="secao-dimensao-topo">' +
        (icone ? '<img src="' + esc(icone) + '" alt="" class="secao-dimensao-icone" width="40" height="40" loading="lazy">' : '') +
        '<div><h2>' + esc(dim.nome) + '</h2><p class="lead">' + esc(dim.descricao) + '</p></div>' +
        '</div>' +
        '<div class="grade-indicadores" id="grade-' + chave + '"></div></section>'
      );
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
      window.DIEESE360.ligarRecolherBarraLateral(document.getElementById('lateral-recolher'), document.querySelector('.layout-lateral'));

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
