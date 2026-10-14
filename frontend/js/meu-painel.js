// DIEESE 360 — "Meu painel" (meu-painel.html): montagem customizada de
// indicadores num grid arrastável/redimensionável (GridStack.js, vendorizado
// em js/vendor/gridstack.js). A pedido explícito do responsável do projeto
// (2026-10-14): "arrastar os gráficos dentro do quadro dando a melhor
// dimensionalidade a cada um". Versão inicial (ver conversa sobre escopo
// realista de "BI completo"): só gráfico de linha por enquanto, mais tipos
// de visualização ficam para uma rodada seguinte.
//
// O layout salvo é só {id: indicador_id, x, y, w, h} por cartão — o dado em
// si nunca é salvo aqui, vem sempre ao vivo de indicadores_serie. Um
// indicador removido/renomeado não corrompe o layout, só some do grid.
(function () {
  'use strict';
  var P = window.Painel;
  var D = window.DIEESE360.dados;
  var esc = P.esc;

  var grid = null;
  var indicadoresPorId = {};
  var usuarioId = null;
  var painelIdSalvo = null; // id da linha em paineis_customizados, se já existe

  function mostrarStatus(texto, tipo) {
    var el = document.getElementById('meupainel-status');
    el.textContent = texto;
    el.hidden = false;
    el.className = 'aviso' + (tipo ? ' ' + tipo : '');
  }

  function atualizarVazio() {
    var vazio = grid.engine.nodes.length === 0;
    document.getElementById('meupainel-vazio').hidden = !vazio;
  }

  // ------------------------------------------------------------------
  // Um cartão do grid: título + seletor de tipo de gráfico (só linha por
  // enquanto, UI já pronta para mais) + botão remover + corpo do gráfico.
  // ------------------------------------------------------------------
  function montarConteudoCartao(indicador) {
    return (
      '<div class="meupainel-cartao">' +
      '<div class="meupainel-cartao-topo">' +
      '<strong>' + esc(indicador.nome) + '</strong>' +
      '<button type="button" class="meupainel-remover" aria-label="Remover ' + esc(indicador.nome) + ' do painel">×</button>' +
      '</div>' +
      '<div class="meupainel-cartao-corpo" data-indicador="' + esc(indicador.id) + '"><p class="lateral-carregando">Carregando…</p></div>' +
      '</div>'
    );
  }

  function renderizarGrafico(elCorpo, indicador) {
    D.carregarSerie(indicador.id, 60).then(function (serieAsc) {
      if (!serieAsc.length) { elCorpo.innerHTML = '<p class="aviso demo">Sem pontos publicados.</p>'; return; }
      elCorpo.innerHTML = '<div class="grafico-linha-caixa"></div>';
      window.DIEESE360.montarGraficoLinha(elCorpo.querySelector('.grafico-linha-caixa'), serieAsc, {
        formatarValor: function (v) { return D.formatarValor(indicador, v); },
        formatarData: D.formatarDataCurta
      });
    }).catch(function (erro) {
      elCorpo.innerHTML = '<p class="aviso demo">' + esc(P.mensagemErro(erro)) + '</p>';
    });
  }

  function adicionarCartao(indicador, posicao) {
    if (grid.engine.nodes.some(function (n) { return n.id === indicador.id; })) {
      P.aviso(indicador.nome + ' já está no painel.', '');
      return;
    }
    var opcoes = Object.assign({ id: indicador.id, w: 4, h: 3, content: montarConteudoCartao(indicador) }, posicao || {});
    var item = grid.addWidget(opcoes);
    var elCorpo = item.querySelector('.meupainel-cartao-corpo');
    renderizarGrafico(elCorpo, indicador);
    item.querySelector('.meupainel-remover').addEventListener('click', function () {
      grid.removeWidget(item);
      atualizarVazio();
    });
    atualizarVazio();
  }

  // ------------------------------------------------------------------
  // Carregar / salvar o layout em paineis_customizados (1 painel por conta
  // nesta primeira versão — sem nome/múltiplos painéis ainda).
  // ------------------------------------------------------------------
  function carregarPainelSalvo() {
    return P.sb.from('paineis_customizados').select('id, layout').eq('usuario_id', usuarioId).order('atualizado_em', { ascending: false }).limit(1).maybeSingle()
      .then(function (r) {
        if (r.error) throw r.error;
        if (!r.data) return;
        painelIdSalvo = r.data.id;
        (r.data.layout || []).forEach(function (item) {
          var indicador = indicadoresPorId[item.id];
          if (!indicador) return; // indicador removido do catálogo desde o último salvamento — pula, não quebra
          adicionarCartao(indicador, { x: item.x, y: item.y, w: item.w, h: item.h });
        });
      });
  }

  function salvarPainel() {
    var layout = grid.save(false).map(function (n) {
      return { id: n.id, x: n.x, y: n.y, w: n.w, h: n.h };
    });
    var linha = { usuario_id: usuarioId, layout: layout, atualizado_em: new Date().toISOString() };
    if (painelIdSalvo) linha.id = painelIdSalvo;

    return P.sb.from('paineis_customizados').upsert(linha).select('id').single().then(function (r) {
      if (r.error) throw r.error;
      painelIdSalvo = r.data.id;
      mostrarStatus('Painel salvo.', '');
    }).catch(function (erro) {
      mostrarStatus(P.mensagemErro(erro), 'demo');
    });
  }

  // ------------------------------------------------------------------
  function montarSeletor(indicadores) {
    var select = document.getElementById('meupainel-seletor');
    var porDimensao = {};
    indicadores.forEach(function (i) { (porDimensao[i.dimensao] = porDimensao[i.dimensao] || []).push(i); });
    var html = '<option value="">+ Adicionar indicador…</option>';
    Object.keys(D.DIMENSOES).forEach(function (chave) {
      var itens = porDimensao[chave];
      if (!itens || !itens.length) return;
      html += '<optgroup label="' + esc(D.DIMENSOES[chave].nome) + '">' +
        itens.map(function (i) { return '<option value="' + esc(i.id) + '">' + esc(i.nome) + '</option>'; }).join('') +
        '</optgroup>';
    });
    select.innerHTML = html;
    select.addEventListener('change', function () {
      if (!select.value) return;
      adicionarCartao(indicadoresPorId[select.value]);
      select.value = '';
    });
  }

  function iniciar(contexto) {
    usuarioId = contexto.user.id;
    grid = GridStack.init({ cellHeight: 90, margin: 8, float: true, animate: true });

    D.carregarIndicadores().then(function (indicadores) {
      indicadores.forEach(function (i) { indicadoresPorId[i.id] = i; });
      montarSeletor(indicadores);
      return carregarPainelSalvo();
    }).then(function () {
      atualizarVazio();
    }).catch(function (erro) {
      mostrarStatus(P.mensagemErro(erro), 'demo');
    });

    document.getElementById('meupainel-salvar').addEventListener('click', salvarPainel);
  }

  P.exigirSessao().then(function (contexto) { iniciar(contexto); });
})();
