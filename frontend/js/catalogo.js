// DIEESE 360 — Catálogo Mestre de Indicadores (catalogo.html): todos os
// indicadores publicados, segmentados por dimensão, como grade de cartões
// com dado real (valor atual, variação, sparkline) — não uma tabela de
// metadado cru (2026-10-26, pedido explícito do responsável do projeto
// depois de ver a primeira versão em tabela: "está proibido colocar essa
// estrutura em qualquer parte do site... algo de acordo com o benchmark").
// Reaproveita o mesmo cartão (`cartao-resumo`) já usado em painel.html, só
// acrescentando fonte/classificação no rodapé — nenhuma lógica de
// sparkline/tendência duplicada (ver agents/bi-dataviz.md). Mesma ordem de
// dimensão e mesmo conceito de subgrupo já usados na barra lateral
// (js/barra-lateral.js) e no carrossel da home (js/inicio.js).
(function () {
  'use strict';
  var P = window.Painel;
  var D = window.DIEESE360.dados;
  var esc = P.esc;

  // Mesma ordem usada em inicio.js/painel.js — consistência entre as
  // telas que mostram as dimensões.
  var ORDEM_DIMENSOES = ['macroeconomia', 'monetario_credito', 'inflacao', 'mercado_trabalho', 'mercados'];

  var estado = { indicadores: [], series: {}, busca: '' };

  // Índice rápido (âncora de rolagem — a segmentação visual por seção já
  // cumpre o papel que antes era de um filtro que escondia o resto).
  function montarIndiceRapido(dimensoesPresentes) {
    var alvo = document.getElementById('catalogo-indice');
    alvo.innerHTML = dimensoesPresentes.map(function (chave) {
      var dim = D.DIMENSOES[chave];
      return '<a href="#catalogo-dim-' + esc(chave) + '" class="catalogo-indice-link">' + esc(dim.nome) + '</a>';
    }).join('');
  }

  // Mesmo cartão de painel.html (cartao-resumo), com um rodapé extra de
  // fonte + classificação — a razão de ser do catálogo é mostrar isso sem
  // precisar abrir a página do indicador.
  function montarCartaoCatalogo(indicador, serieAsc) {
    if (!serieAsc.length) return D.montarCartaoVazio(indicador);
    var atual = serieAsc[serieAsc.length - 1];
    var tendencia = D.calcularTendencia(indicador, serieAsc);
    var chip = tendencia
      ? '<span class="chip-tendencia ' + tendencia.classe + '">' + tendencia.seta + ' ' + esc(D.formatarValor(indicador, Math.abs(tendencia.delta))) + '</span>'
      : '';
    return (
      '<article class="cartao-resumo">' +
      '<a class="cartao-resumo-botao" href="indicador.html?id=' + esc(indicador.id) + '" aria-label="' + esc(indicador.nome) + ', ver página completa, gráfico e metodologia">' +
      '<div class="cartao-cabecalho"><span class="cartao-rotulo">' + esc(indicador.nome) + '</span>' + chip + '</div>' +
      '<strong class="cartao-valor">' + esc(D.formatarValor(indicador, atual.valor)) + '</strong>' +
      '<span class="cartao-data">' + esc(D.formatarDataReferencia(atual.data_referencia, indicador.periodicidade)) + '</span>' +
      D.montarSparkline(serieAsc) +
      '<div class="catalogo-cartao-rodape">' +
      '<span class="catalogo-classif">' + esc(indicador.classificacao) + '</span>' +
      '<span class="catalogo-cartao-fonte" title="' + esc(indicador.fonte) + '">' + esc(indicador.fonte) + '</span>' +
      '</div>' +
      '</a>' +
      '</article>'
    );
  }

  // Dentro de uma dimensão: cartões sem subgrupo primeiro, depois cada
  // subgrupo com seu próprio cabeçalho — mesmo critério já usado em
  // barra-lateral.js.
  function montarCorpoDimensao(indicadoresDim) {
    var soltos = [];
    var porSubgrupo = {};
    var ordemSubgrupos = [];
    indicadoresDim.forEach(function (i) {
      var sub = D.subgrupoDoIndicador(i.id);
      if (!sub) { soltos.push(i); return; }
      if (!porSubgrupo[sub]) { porSubgrupo[sub] = []; ordemSubgrupos.push(sub); }
      porSubgrupo[sub].push(i);
    });

    function grade(lista) {
      return '<div class="grade-indicadores catalogo-grade">' + lista.map(function (i) {
        return montarCartaoCatalogo(i, estado.series[i.id] || []);
      }).join('') + '</div>';
    }

    var html = soltos.length ? grade(soltos) : '';
    ordemSubgrupos.forEach(function (sub) {
      html += '<h3 class="catalogo-subgrupo-titulo">' + esc(sub) + '</h3>' + grade(porSubgrupo[sub]);
    });
    return html;
  }

  function montarSecaoDimensao(chave, indicadoresDim) {
    var dim = D.DIMENSOES[chave];
    return (
      '<section class="catalogo-dimensao-secao" id="catalogo-dim-' + esc(chave) + '">' +
      '<div class="catalogo-dimensao-cabecalho">' +
      '<h2>' + esc(dim.nome) + '</h2>' +
      '<span class="catalogo-dimensao-contagem">' + indicadoresDim.length + (indicadoresDim.length === 1 ? ' indicador' : ' indicadores') + '</span>' +
      '</div>' +
      '<p class="catalogo-dimensao-desc">' + esc(dim.descricao) + '</p>' +
      montarCorpoDimensao(indicadoresDim) +
      '</section>'
    );
  }

  // Remove acento antes de comparar — "cambio" precisa achar "câmbio", sem
  // o usuário precisar digitar o acento certo (achado ao testar a busca
  // com dado real, 2026-10-26).
  function semAcento(s) {
    return s.normalize('NFD').replace(/[̀-ͯ]/g, '');
  }

  function linhasFiltradas() {
    var termo = semAcento(estado.busca.trim().toLowerCase());
    if (!termo) return estado.indicadores;
    return estado.indicadores.filter(function (i) {
      return semAcento((i.nome + ' ' + i.fonte).toLowerCase()).indexOf(termo) >= 0;
    });
  }

  function renderizar() {
    var filtrados = linhasFiltradas();
    document.getElementById('catalogo-contagem').textContent =
      filtrados.length + (filtrados.length === 1 ? ' indicador encontrado' : ' indicadores encontrados') +
      (estado.indicadores.length ? ' de ' + estado.indicadores.length + ' no catálogo' : '');

    var raiz = document.getElementById('catalogo-secoes');
    if (!filtrados.length) {
      raiz.innerHTML = '<p class="aviso demo">Nenhum indicador bate com essa busca.</p>';
      return;
    }

    var porDimensao = {};
    filtrados.forEach(function (i) {
      var chave = D.dimensaoEfetiva(i.dimensao);
      (porDimensao[chave] = porDimensao[chave] || []).push(i);
    });

    raiz.innerHTML = ORDEM_DIMENSOES
      .filter(function (chave) { return porDimensao[chave] && porDimensao[chave].length; })
      .map(function (chave) { return montarSecaoDimensao(chave, porDimensao[chave]); })
      .join('');
    window.DIEESE360.animarEntrada && window.DIEESE360.animarEntrada(raiz);
  }

  function iniciar() {
    if (!P.sb) {
      document.getElementById('catalogo-secoes').innerHTML = '<p class="aviso demo">Não foi possível conectar ao Supabase.</p>';
      return;
    }
    D.carregarIndicadores().then(function (indicadores) {
      estado.indicadores = indicadores;
      var dimensoesPresentes = ORDEM_DIMENSOES.filter(function (chave) {
        return indicadores.some(function (i) { return D.dimensaoEfetiva(i.dimensao) === chave; });
      });
      montarIndiceRapido(dimensoesPresentes);

      // Uma única chamada em lote para a série recente de todos os
      // indicadores (não uma consulta por indicador) — mesmo padrão já
      // usado na tabela de variações da home (js/inicio.js). Uma chamada
      // SÓ com todos os ~62 ids de uma vez estourava o limite padrão de
      // 1000 linhas do PostgREST (62 x 24 pontos = 1488) e deixava alguns
      // indicadores sem nenhum ponto (ex. Selic) — testado e confirmado
      // nesta sessão antes de publicar. Busca por dimensão em vez disso
      // (no máximo ~17 indicadores cada, bem abaixo do limite), em
      // paralelo — mesmo padrão já usado nos carrosséis da home.
      return Promise.all(dimensoesPresentes.map(function (chave) {
        var idsDim = indicadores.filter(function (i) { return D.dimensaoEfetiva(i.dimensao) === chave; }).map(function (i) { return i.id; });
        return D.carregarSeriesPorIndicadores(idsDim, 24);
      })).then(function (listasDeSeries) {
        estado.series = {};
        listasDeSeries.forEach(function (series) {
          Object.keys(series).forEach(function (id) { estado.series[id] = series[id]; });
        });
        renderizar();
      });
    }).catch(function (erro) {
      document.getElementById('catalogo-secoes').innerHTML = '<p class="aviso demo">' + esc(P.mensagemErro(erro)) + '</p>';
    });

    document.getElementById('catalogo-busca').addEventListener('input', function (e) {
      estado.busca = e.target.value;
      renderizar();
    });
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', iniciar); else iniciar();
})();
