// DIEESE 360 — página dedicada de um indicador (indicador.html?id=...):
// cabeçalho + conceito, filtro de período, e 3-4 formas de visualizar a
// mesma série (gráfico, tabela, infográfico, e mapa por UF quando
// regionalizado), mais exportação para Excel. Pública — os números já são
// públicos (ADR 0005); só ajusta o cabeçalho conforme há ou não sessão.
(function () {
  'use strict';
  var P = window.Painel;
  var D = window.DIEESE360.dados;
  var esc = P.esc;

  var INDICADORES_COM_MAPA_UF = { limite_fiscal_pessoal: true };
  var PERIODOS = [
    { chave: '12', rotulo: 'Últimos 12' },
    { chave: '24', rotulo: 'Últimos 24' },
    { chave: '60', rotulo: 'Últimos 60' },
    { chave: 'tudo', rotulo: 'Tudo' }
  ];

  var estado = { indicador: null, serieCompleta: [], periodo: 'tudo', vista: 'grafico' };

  function idDaUrl() {
    var params = new URLSearchParams(window.location.search);
    return params.get('id');
  }

  function filtrarPorPeriodo(serieAsc, periodo) {
    if (periodo === 'tudo') return serieAsc;
    var n = parseInt(periodo, 10);
    return serieAsc.slice(-n);
  }

  // ------------------------------------------------------------------
  // Cabeçalho do indicador (número, tendência, conceito, metadados)
  // ------------------------------------------------------------------
  function montarCabecalho(indicador, serieAsc) {
    var atual = serieAsc[serieAsc.length - 1];
    var tendencia = D.calcularTendencia(indicador, serieAsc);
    var chip = tendencia
      ? '<span class="chip-tendencia ' + tendencia.classe + '">' + tendencia.seta + ' ' + esc(D.formatarValor(indicador, Math.abs(tendencia.delta))) + '</span>'
      : '';
    var comparacao = tendencia
      ? tendencia.seta + ' ' + D.formatarValor(indicador, Math.abs(tendencia.delta)) + ' no período, comparado a ' + D.formatarDataReferencia(tendencia.anterior.data_referencia, indicador.periodicidade)
      : 'Ainda não há ponto anterior para comparar.';

    // Comparações de mercado (média móvel, volatilidade, sequência, faixa
    // de 52 semanas) — só para a dimensão mercados, onde essas métricas
    // fazem sentido; atualiza sozinho a cada ponto novo publicado, sem
    // depender de redação manual (ver D.montarComparacoesMercado).
    var comparacoesMercado = indicador.dimensao === 'mercados' ? D.montarComparacoesMercado(indicador, serieAsc) : [];
    var blocoComparacoes = comparacoesMercado.length
      ? '<div class="indicador-comparacoes-mercado"><strong>Comparações</strong><ul>' +
        comparacoesMercado.map(function (f) { return '<li>' + esc(f) + '</li>'; }).join('') +
        '</ul></div>'
      : '';

    var dimensaoEfetiva = D.dimensaoEfetiva(indicador.dimensao);
    return (
      '<a class="indicador-voltar" href="painel.html#' + esc(dimensaoEfetiva) + '">← ' + esc((D.DIMENSOES[dimensaoEfetiva] || {}).nome || 'Painel') + '</a>' +
      '<div class="indicador-cabecalho">' +
      '<h1>' + esc(indicador.nome) + '</h1>' +
      '<div class="indicador-stat"><strong>' + esc(D.formatarValor(indicador, atual.valor)) + '</strong>' + chip + '</div>' +
      '<p class="indicador-data">' + esc(D.formatarDataReferencia(atual.data_referencia, indicador.periodicidade)) + '</p>' +
      '</div>' +
      '<p class="indicador-conceito">' + esc(indicador.metodologia_md || '') + '</p>' +
      '<dl class="indicador-meta">' +
      '<dt>Fonte</dt><dd>' + esc(indicador.fonte) + '</dd>' +
      '<dt>Periodicidade</dt><dd>' + esc(indicador.periodicidade) + '</dd>' +
      '<dt>Classificação</dt><dd>' + esc(indicador.classificacao) + '</dd>' +
      '<dt>Comparação mais recente</dt><dd>' + esc(comparacao) + '</dd>' +
      '</dl>' +
      blocoComparacoes
    );
  }

  // ------------------------------------------------------------------
  // As 4 vistas
  // ------------------------------------------------------------------
  function montarVistaGrafico(container, indicador, serieAsc) {
    container.innerHTML = '<div class="grafico-linha-caixa"></div>';
    window.DIEESE360.montarGraficoLinha(container.querySelector('.grafico-linha-caixa'), serieAsc, {
      formatarValor: function (v) { return D.formatarValor(indicador, v); },
      formatarData: D.formatarDataCurta
    });
  }

  function montarVistaTabela(container, indicador, serieAsc) {
    var linhas = serieAsc.slice().reverse(); // mais recente primeiro, como em qualquer tabela de série que se preze
    container.innerHTML =
      '<div class="tabela-serie-caixa"><table class="tabela-serie">' +
      '<thead><tr><th>Data de referência</th><th>Valor</th></tr></thead>' +
      '<tbody>' + linhas.map(function (p) {
        return '<tr><td>' + esc(D.formatarDataReferencia(p.data_referencia, indicador.periodicidade)) + '</td><td class="tabela-serie-valor">' + esc(D.formatarValor(indicador, p.valor)) + '</td></tr>';
      }).join('') + '</tbody>' +
      '</table></div>';
  }

  function montarVistaInfografico(container, indicador, serieAsc) {
    var valores = serieAsc.map(function (p) { return p.valor; });
    var min = Math.min.apply(null, valores), max = Math.max.apply(null, valores);
    var media = valores.reduce(function (a, b) { return a + b; }, 0) / valores.length;
    var pMin = serieAsc.filter(function (p) { return p.valor === min; })[0];
    var pMax = serieAsc.filter(function (p) { return p.valor === max; })[0];
    var atual = serieAsc[serieAsc.length - 1];

    container.innerHTML =
      '<div class="infografico">' +
      '<div class="infografico-hero"><span class="infografico-rotulo">Valor mais recente</span><strong>' + esc(D.formatarValor(indicador, atual.valor)) + '</strong><span class="infografico-data">' + esc(D.formatarDataReferencia(atual.data_referencia, indicador.periodicidade)) + '</span></div>' +
      '<div class="infografico-grade">' +
      '<div class="infografico-caixa"><span class="infografico-rotulo">Maior valor do período</span><strong>' + esc(D.formatarValor(indicador, max)) + '</strong><span class="infografico-data">' + esc(D.formatarDataCurta(pMax.data_referencia)) + '</span></div>' +
      '<div class="infografico-caixa"><span class="infografico-rotulo">Menor valor do período</span><strong>' + esc(D.formatarValor(indicador, min)) + '</strong><span class="infografico-data">' + esc(D.formatarDataCurta(pMin.data_referencia)) + '</span></div>' +
      '<div class="infografico-caixa"><span class="infografico-rotulo">Média do período</span><strong>' + esc(D.formatarValor(indicador, media)) + '</strong><span class="infografico-data">' + serieAsc.length + ' pontos</span></div>' +
      '</div>' +
      '</div>';
  }

  function montarVistaMapa(container, indicador, serieAsc) {
    var ultimo = serieAsc[serieAsc.length - 1];
    var porUf = (ultimo.metadata && ultimo.metadata.por_uf) || {};
    var linhasTabela = Object.keys(porUf)
      .map(function (sigla) { return { sigla: sigla, valor: porUf[sigla] }; })
      .sort(function (a, b) { return b.valor - a.valor; });
    container.innerHTML =
      '<div class="detalhe-mapa-corpo">' +
      '<div class="detalhe-mapa-coluna"><div class="mapa-svg-caixa detalhe-mapa-svg"></div></div>' +
      '<div class="detalhe-mapa-tabela"><table class="tabela-uf"><tbody>' +
      linhasTabela.map(function (l) { return '<tr><td class="tabela-uf-sigla">' + esc(l.sigla) + '</td><td class="tabela-uf-valor">' + esc(D.formatarValor(indicador, l.valor)) + '</td></tr>'; }).join('') +
      '</tbody></table></div>' +
      '</div>';
    window.DIEESE360.montarMapaUF(container.querySelector('.detalhe-mapa-svg'), porUf, {
      legenda: true,
      formatarValor: function (v) { return D.formatarValor(indicador, v); }
    });
  }

  var VISTAS = { grafico: montarVistaGrafico, tabela: montarVistaTabela, infografico: montarVistaInfografico, mapa: montarVistaMapa };

  function renderizarVistaAtual() {
    var serieFiltrada = filtrarPorPeriodo(estado.serieCompleta, estado.periodo);
    var container = document.getElementById('vista-corpo');
    VISTAS[estado.vista](container, estado.indicador, serieFiltrada);
    window.DIEESE360.animarEntrada(container);
    return serieFiltrada;
  }

  // ------------------------------------------------------------------
  // Filtros (período) + abas de vista + exportar
  // ------------------------------------------------------------------
  function montarControles(indicador) {
    var ehRegionalizado = !!INDICADORES_COM_MAPA_UF[indicador.id];
    var abasVista = [
      { chave: 'grafico', rotulo: 'Gráfico' },
      { chave: 'tabela', rotulo: 'Tabela' },
      { chave: 'infografico', rotulo: 'Infográfico' }
    ];
    if (ehRegionalizado) abasVista.push({ chave: 'mapa', rotulo: 'Mapa por UF' });

    var html =
      '<div class="indicador-controles">' +
      '<div class="filtro-periodo" role="group" aria-label="Período">' +
      PERIODOS.map(function (p) { return '<button type="button" class="filtro-periodo-botao' + (p.chave === estado.periodo ? ' ativo' : '') + '" data-periodo="' + p.chave + '">' + esc(p.rotulo) + '</button>'; }).join('') +
      '</div>' +
      '<button type="button" class="btn btn-secundario btn-pequeno" id="btn-exportar">⬇ Baixar em Excel</button>' +
      '</div>' +
      '<div class="vista-abas" role="tablist">' +
      abasVista.map(function (a) { return '<button type="button" class="vista-aba' + (a.chave === estado.vista ? ' ativa' : '') + '" role="tab" data-vista="' + a.chave + '">' + esc(a.rotulo) + '</button>'; }).join('') +
      '</div>' +
      '<div class="vista-corpo" id="vista-corpo"></div>';
    return html;
  }

  function ligarControles(indicador) {
    document.querySelectorAll('.filtro-periodo-botao').forEach(function (b) {
      b.addEventListener('click', function () {
        document.querySelectorAll('.filtro-periodo-botao').forEach(function (x) { x.classList.remove('ativo'); });
        b.classList.add('ativo');
        estado.periodo = b.dataset.periodo;
        renderizarVistaAtual();
      });
    });
    document.querySelectorAll('.vista-aba').forEach(function (b) {
      b.addEventListener('click', function () {
        document.querySelectorAll('.vista-aba').forEach(function (x) { x.classList.remove('ativa'); });
        b.classList.add('ativa');
        estado.vista = b.dataset.vista;
        renderizarVistaAtual();
      });
    });
    document.getElementById('btn-exportar').addEventListener('click', function () {
      var serieFiltrada = filtrarPorPeriodo(estado.serieCompleta, estado.periodo);
      var rotuloPeriodo = (PERIODOS.filter(function (p) { return p.chave === estado.periodo; })[0] || {}).rotulo || 'Série completa';
      window.DIEESE360.exportarSerieExcel(indicador, serieFiltrada, rotuloPeriodo);
    });
  }

  // ------------------------------------------------------------------
  // Cabeçalho da página: mostra sessão se houver, sem exigir login
  // ------------------------------------------------------------------
  function ajustarCabecalhoSessao() {
    if (!P.sb) return;
    P.sb.auth.getSession().then(function (r) {
      var sessao = r && r.data && r.data.session;
      if (!sessao) return;
      return P.sb.from('perfis').select('nome, ativo').eq('id', sessao.user.id).maybeSingle().then(function (res) {
        var perfil = res && res.data;
        if (!perfil || !perfil.ativo) return;
        document.getElementById('usuario-nome').textContent = perfil.nome;
        var sair = document.getElementById('sair');
        sair.hidden = false;
        sair.addEventListener('click', function (e) { e.preventDefault(); P.sair(); });
      });
    });
  }

  // ------------------------------------------------------------------
  function iniciar() {
    ajustarCabecalhoSessao();
    var id = idDaUrl();
    var raiz = document.getElementById('conteudo-indicador');
    if (!id) { raiz.innerHTML = '<p class="aviso demo">Nenhum indicador informado na URL.</p>'; return; }
    if (!P.sb) { raiz.innerHTML = '<p class="aviso demo">Não foi possível conectar ao Supabase.</p>'; return; }

    D.carregarIndicadores().then(function (indicadores) {
      window.DIEESE360.montarBarraLateral(document.getElementById('barra-lateral'), indicadores, id);
      window.DIEESE360.ligarRecolherBarraLateral(document.getElementById('lateral-recolher'), document.querySelector('.layout-lateral'));
      var indicador = indicadores.filter(function (i) { return i.id === id; })[0];
      if (!indicador) { raiz.innerHTML = '<p class="aviso demo">Indicador não encontrado.</p>'; return; }
      document.title = indicador.nome + ' · DIEESE 360';

      return D.carregarSerie(id, 2000).then(function (serieAsc) {
        if (!serieAsc.length) {
          raiz.innerHTML =
            '<a class="indicador-voltar" href="painel.html">← Painel</a>' +
            '<div class="indicador-cabecalho"><h1>' + esc(indicador.nome) + '</h1></div>' +
            '<p class="aviso demo">Catalogado, sem pontos publicados ainda.</p>';
          return;
        }
        estado.indicador = indicador;
        estado.serieCompleta = serieAsc;
        if (INDICADORES_COM_MAPA_UF[indicador.id]) estado.vista = 'mapa';

        raiz.innerHTML = montarCabecalho(indicador, serieAsc) + montarControles(indicador);
        ligarControles(indicador);
        renderizarVistaAtual();
        window.DIEESE360.animarEntrada(raiz);
      });
    }).catch(function (erro) {
      raiz.innerHTML = '<p class="aviso demo">' + esc(P.mensagemErro(erro)) + '</p>';
    });
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', iniciar); else iniciar();
})();
