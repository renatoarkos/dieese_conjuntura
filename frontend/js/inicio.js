// Orquestração da página inicial pública (index.html): ticker de topo,
// resumo do dia (indicador em destaque + maiores variações) e um carrossel
// por dimensão com todos os indicadores publicados. Não exige sessão — os
// números são públicos (ver ADR 0005); só a navegação completa fica atrás
// do login.
(function () {
  'use strict';
  var P = window.Painel;
  var D = window.DIEESE360.dados;
  var esc = P.esc;

  // 'mercados' fica fora do carrossel genérico de propósito (ver ADR 0010):
  // tem página e diagramação próprias (mercados.html), no padrão de painel
  // de bolsa pedido pelo responsável do projeto, em vez do cartão-padrão das
  // outras 5 dimensões socioeconômicas.
  var ORDEM_DIMENSOES = ['macroeconomia', 'monetario_credito', 'inflacao', 'mercado_trabalho', 'caged'];

  var ICONES_DIMENSAO = {
    macroeconomia: 'assets/dimensoes/icone-macroeconomia.png',
    monetario_credito: 'assets/dimensoes/icone-monetario-credito.png',
    inflacao: 'assets/dimensoes/icone-inflacao.png',
    mercado_trabalho: 'assets/dimensoes/icone-mercado-trabalho.png',
    caged: 'assets/dimensoes/icone-caged.png'
    // 'mercados' ainda sem ícone próprio gerado (ver frontend/img-prompts.json
    // para o padrão visual a seguir) — ICONES_DIMENSAO[chave] || '' já trata
    // a ausência sem quebrar o layout, só não mostra a imagem por enquanto.
  };

  // Texto mais completo por dimensão (o que é, o que cobre, por que importa
  // para a leitura de conjuntura) — complementa a descrição de uma linha já
  // usada em D.DIMENSOES (essa continua servindo o resumo rápido da grade).
  var TEXTO_DIMENSAO = {
    macroeconomia: 'Reúne os indicadores que descrevem o ritmo geral da economia brasileira: Produto Interno Bruto, comércio exterior, investimento, preços de commodities e contas públicas. É a base para situar qualquer leitura setorial dentro do ciclo econômico em curso.',
    monetario_credito: 'Cobre a taxa básica de juros, as taxas cobradas ao tomador final, o crédito concedido pelo sistema financeiro e o endividamento das famílias. Mostra como a política monetária se transmite ao custo do dinheiro no dia a dia de empresas e trabalhadores.',
    inflacao: 'Acompanha os principais índices de preços ao consumidor (IPCA, INPC, IGP-M) e itens sensíveis ao orçamento familiar, como combustíveis. É o contraponto necessário para ler qualquer variação nominal de salário ou renda em termos reais.',
    mercado_trabalho: 'Reúne emprego, desocupação, rendimento, sindicalização e negociação coletiva: o núcleo da pauta histórica do DIEESE, onde a pesquisa socioeconômica se conecta diretamente à atuação sindical.',
    caged: 'Admissões e desligamentos formais apurados por microdado todo mês, com granularidade menor que a RAIS anual. Antecipa movimentos do mercado de trabalho formal entre uma apuração anual e outra.',
    mercados: 'Índices das principais bolsas de valores, criptoativos de maior volume e algumas das ações mais negociadas da B3, com fechamento diário. Dimensão separada do restante da plataforma: é referência de mercado, não um indicador socioeconômico produzido ou validado pelo DIEESE, e não deve ser lida como recomendação de investimento.'
  };

  // Prévia compacta da dimensão "mercados" na home (não entra no fetch geral
  // de TICKER/DESTAQUES porque é uma dimensão à parte, ver ADR 0010) — um
  // índice nacional, um global, um criptoativo e uma ação B3, representando
  // as 3 categorias da página própria (mercados.html).
  var PREVIEW_MERCADOS = ['ibovespa', 'sp500', 'bitcoin', 'petr4'];

  var TICKER = ['selic', 'cambio_dolar', 'ipca', 'commodities_geral', 'balanca_saldo', 'taxa_desocupacao', 'bndes_desembolsos'];
  // Indicadores em destaque no resumo do dia: 8 séries chave distribuídas em grid completo
  var DESTAQUES = [
    'cambio_dolar',
    'selic',
    'ipca',
    'taxa_desocupacao',
    'balanca_saldo',
    'rendimento_medio_real',
    'reajustes_acima_inpc_pct',
    'commodities_geral'
  ];

  // Frase "vs. <período>" explícita — usada em toda exibição de variação
  // (ticker, lista de maiores variações, destaque), a pedido do responsável
  // do projeto (2026-10-14): "preciso que diga a que se refere cada um,
  // mostrando em que comparação fez a variação".
  function vsPeriodo(indicador, pontoAnterior) {
    return 'vs. ' + D.formatarDataReferencia(pontoAnterior.data_referencia, indicador.periodicidade);
  }

  // Montagem moderna e comercial dos cartões de dimensão (SaaS intelligence grid)
  function montarGradeDimensoes() {
    var alvo = document.getElementById('grade-dimensoes');
    var html = '';
    var i = 1;
    ORDEM_DIMENSOES.forEach(function (chave) {
      var dim = D.DIMENSOES[chave];
      var icone = ICONES_DIMENSAO[chave] || '';
      var numFmt = i < 10 ? '0' + i : i;
      html += '<a class="cartao-dimensao" href="#dimensao-' + esc(chave) + '">' +
        '<div class="cartao-dimensao-topo">' +
        '<div class="cartao-dimensao-kicker-grupo">' +
        '<span class="num">Dimensão ' + numFmt + '</span>' +
        '<span class="cartao-dimensao-qtd" id="qtd-' + esc(chave) + '">...</span>' +
        '</div>' +
        (icone ? '<div class="cartao-dimensao-icone-moldura"><img src="' + esc(icone) + '" alt="" class="cartao-dimensao-icone" width="52" height="52" loading="lazy"></div>' : '') +
        '</div>' +
        '<h3 class="cartao-dimensao-titulo">' + esc(dim.nome) + '</h3>' +
        '<p class="cartao-dimensao-desc">' + esc(dim.descricao) + '</p>' +
        '<div class="cartao-dimensao-indicadores-wrapper">' +
        '<span class="cartao-dimensao-subtitulo">Indicadores monitorados:</span>' +
        '<div class="cartao-dimensao-tags" id="arvore-' + esc(chave) + '"><span class="cartao-dimensao-carregando">Carregando indicadores…</span></div>' +
        '</div>' +
        '<div class="cartao-dimensao-rodape">' +
        '<span>Explorar dimensão</span>' +
        '<svg class="cartao-dimensao-seta" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14M12 5l7 7-7 7"/></svg>' +
        '</div>' +
        '</a>';
      i++;
    });
    alvo.innerHTML = html;
  }

  // Preenche as tags com nomes reais dos indicadores + badge "+ N indicadores"
  function preencherArvoreDimensoes(porDimensao) {
    ORDEM_DIMENSOES.forEach(function (chave) {
      var alvo = document.getElementById('arvore-' + chave);
      var badgeQtd = document.getElementById('qtd-' + chave);
      if (!alvo) return;
      var lista = porDimensao[chave] || [];
      if (badgeQtd) {
        badgeQtd.textContent = lista.length + (lista.length === 1 ? ' série' : ' séries');
      }
      if (!lista.length) { alvo.innerHTML = '<span class="tag-ind vazia">Em preparação</span>'; return; }
      var visiveis = lista.slice(0, 4);
      var html = visiveis.map(function (ind) {
        return '<span class="tag-ind" title="' + esc(ind.nome) + '">' + esc(ind.nome) + '</span>';
      }).join('');
      if (lista.length > visiveis.length) {
        html += '<span class="tag-ind mais">+ ' + (lista.length - visiveis.length) + ' indicadores</span>';
      }
      alvo.innerHTML = html;
    });
  }

  function montarTicker(indicadores, series) {
    var alvo = document.getElementById('ticker-trilho');
    var itens = TICKER.map(function (id) {
      var indicador = indicadores.filter(function (i) { return i.id === id; })[0];
      return indicador ? D.montarItemTicker(indicador, series[id] || []) : '';
    }).filter(Boolean);
    if (!itens.length) { alvo.innerHTML = '<span class="ticker-topo-item">Sem indicadores publicados ainda.</span>'; return; }
    // Duplica a lista para o loop de rolagem ficar contínuo (ver @keyframes ticker-rola, translateX(-50%)).
    alvo.innerHTML = itens.join('') + itens.join('');
  }

  // Tabela de maiores variações com ranking #1, #2... e duas colunas diagramadas
  function montarListaVariacoes(indicadores, series, direcao, limite) {
    var linhas = indicadores.map(function (ind) {
      var variacao = D.calcularVariacao(ind, series[ind.id] || []);
      return variacao ? { indicador: ind, variacao: variacao } : null;
    }).filter(Boolean);
    linhas = linhas.filter(function (l) { return direcao === 'alta' ? l.variacao.valor > 0 : l.variacao.valor < 0; });
    linhas.sort(function (a, b) { return Math.abs(b.variacao.valor) - Math.abs(a.variacao.valor); });
    linhas = linhas.slice(0, limite);
    if (!linhas.length) return '<li><span class="nome">Nenhuma variação ' + (direcao === 'alta' ? 'positiva' : 'negativa') + ' no período.</span></li>';
    return linhas.map(function (l, idx) {
      var pos = idx + 1;
      return '<li><button type="button" class="resumo-variacoes-linha ' + direcao + '" data-id="' + esc(l.indicador.id) + '" title="' + esc(l.indicador.nome) + '">' +
        '<span class="rank-pos rank-' + direcao + '">#' + pos + '</span>' +
        '<span class="nome">' + esc(l.indicador.nome) + '<span class="vs-periodo">' + esc(vsPeriodo(l.indicador, l.variacao.anterior)) + '</span></span>' +
        '<span class="percentual ' + direcao + '">' + (direcao === 'alta' ? '▲ +' : '▼ -') + Math.abs(l.variacao.valor).toFixed(1) + ' ' + esc(l.variacao.sufixo) + '</span>' +
        '</button></li>';
    }).join('');
  }

  // Monta a estrutura do resumo do dia:
  // - Lado esquerdo: painel com grid completo de gráficos cobrindo todo o quadro
  // - Lado direito: DUAS colunas lado a lado (Maiores Altas e Maiores Baixas) com títulos customizados
  function montarEstruturaResumoDia() {
    var alvo = document.getElementById('resumo-dia');
    alvo.innerHTML =
      '<div class="resumo-destaque">' +
      '<div class="destaque-topo-bloco">' +
      '<span class="secao-kicker">Termômetro da conjuntura</span>' +
      '<h3>Indicadores em destaque</h3>' +
      '<p class="destaque-subtitulo">Clique em qualquer cartão para ver o gráfico ampliado e as notas metodológicas.</p>' +
      '</div>' +
      '<div class="destaque-grade" id="carrossel-destaque"><p class="aviso demo">Carregando indicadores…</p></div>' +
      '</div>' +
      '<div class="resumo-variacoes">' +
      '<div class="variacoes-coluna-bloco altas">' +
      '<div class="variacoes-cabecalho">' +
      '<div class="variacoes-tag-topo tag-alta">▲ Aumentos</div>' +
      '<h4>Maiores Altas</h4>' +
      '<span class="variacoes-desc">Maiores variações positivas</span>' +
      '</div>' +
      '<ul class="resumo-variacoes-lista" id="resumo-altas"><li>Carregando…</li></ul>' +
      '</div>' +
      '<div class="variacoes-coluna-bloco baixas">' +
      '<div class="variacoes-cabecalho">' +
      '<div class="variacoes-tag-topo tag-baixa">▼ Reduções</div>' +
      '<h4>Maiores Baixas</h4>' +
      '<span class="variacoes-desc">Maiores reduções e quedas</span>' +
      '</div>' +
      '<ul class="resumo-variacoes-lista" id="resumo-baixas"><li>Carregando…</li></ul>' +
      '</div>' +
      '</div>';
  }

  // Preenche a grade completa de indicadores em destaque (8 cartões com gráficos completos)
  function preencherDestaque(indicadores, series) {
    var grade = document.getElementById('carrossel-destaque');
    var indicadoresPorId = {};
    var disponiveis = [];
    DESTAQUES.forEach(function (id) {
      var ind = indicadores.filter(function (i) { return i.id === id; })[0];
      if (ind && series[ind.id] && series[ind.id].length >= 2) {
        disponiveis.push(ind);
        indicadoresPorId[ind.id] = ind;
      }
    });
    // Se faltar para 8, preenche com os outros indicadores que têm séries publicadas
    if (disponiveis.length < 8) {
      indicadores.forEach(function (ind) {
        if (disponiveis.indexOf(ind) === -1 && series[ind.id] && series[ind.id].length >= 2) {
          disponiveis.push(ind);
          indicadoresPorId[ind.id] = ind;
        }
      });
    }
    disponiveis = disponiveis.slice(0, 8);
    if (!disponiveis.length) { grade.innerHTML = '<p class="aviso demo">Nenhum indicador em destaque publicado ainda.</p>'; return; }
    
    grade.innerHTML = disponiveis.map(function (ind) {
      return '<div class="destaque-card-wrapper" data-id="' + esc(ind.id) + '">' +
        window.DIEESE360.montarCartaoFlip(ind, series[ind.id] || [], { graficoCompleto: true, classeExtra: 'destaque-cartao-flip' }) +
        '</div>';
    }).join('');
    
    window.DIEESE360.ligarCartoesFlip(grade);
    window.DIEESE360.preencherGraficosCompletos(grade, indicadoresPorId, series);
    
    // Ao clicar em cada cartão da grade, abre o cartão ampliado em modal com rotação e metodologia
    grade.querySelectorAll('.destaque-card-wrapper').forEach(function (wrapper) {
      wrapper.addEventListener('click', function (e) {
        // Se clicou no link de página completa do verso, deixa navegar
        if (e.target.closest('a')) return;
        var id = wrapper.getAttribute('data-id');
        var ind = indicadoresPorId[id];
        if (ind) {
          D.carregarSerie(id, 24).then(function (serie) {
            window.DIEESE360.abrirCartaoModal(ind, serie);
          });
        }
      });
    });
  }

  function preencherVariacoes(indicadores, series) {
    document.getElementById('resumo-altas').innerHTML = montarListaVariacoes(indicadores, series, 'alta', 5);
    document.getElementById('resumo-baixas').innerHTML = montarListaVariacoes(indicadores, series, 'baixa', 5);
    ligarCliquesVariacoes(indicadores);
  }

  // Clique numa linha da tabela de variações busca a série completa e abre o cartão giratório em modal
  function ligarCliquesVariacoes(indicadores) {
    document.querySelectorAll('.resumo-variacoes-linha').forEach(function (botao) {
      botao.addEventListener('click', function () {
        var id = botao.getAttribute('data-id');
        var indicador = indicadores.filter(function (i) { return i.id === id; })[0];
        if (!indicador) return;
        D.carregarSerie(id, 24).then(function (serie) {
          window.DIEESE360.abrirCartaoModal(indicador, serie);
        });
      });
    });
  }

  // Só a casca das 5 seções (título, texto, trilho vazio em "carregando") —
  // nenhuma rede ainda. O carrossel de cada dimensão é preenchido depois,
  // de forma independente (ver preencherCarrossel), para a seção aparecer
  // na hora e os cartões surgirem assim que a própria consulta terminar,
  // sem travar esperando as outras 4 dimensões.
  function montarEstruturaSecoesDimensao() {
    var raiz = document.getElementById('secoes-dimensao-home');
    raiz.innerHTML = ORDEM_DIMENSOES.map(function (chave) {
      var dim = D.DIMENSOES[chave];
      var icone = ICONES_DIMENSAO[chave] || '';
      return (
        '<section class="secao carrossel-dimensao" id="dimensao-' + esc(chave) + '">' +
        '<div class="container">' +
        '<div class="carrossel-cabecalho">' +
        '<div>' +
        '<div class="secao-dimensao-topo">' +
        (icone ? '<img src="' + esc(icone) + '" alt="" class="secao-dimensao-icone" width="40" height="40" loading="lazy">' : '') +
        '<h2>' + esc(dim.nome) + '</h2>' +
        '</div>' +
        '<p class="lead">' + esc(TEXTO_DIMENSAO[chave] || dim.descricao) + '</p>' +
        '</div>' +
        '</div>' +
        '<div class="carrossel-trilho" id="carrossel-' + esc(chave) + '"><p class="aviso demo">Carregando indicadores…</p></div>' +
        '</div>' +
        '</section>'
      );
    }).join('');
  }

  function preencherCarrossel(chave, indicadoresDim, series) {
    var trilho = document.getElementById('carrossel-' + chave);
    if (!indicadoresDim.length) { trilho.innerHTML = D.montarCartaoDimensaoPendente(chave); return; }
    var indicadoresPorId = {};
    var itensHtml = indicadoresDim.map(function (ind) {
      indicadoresPorId[ind.id] = ind;
      return '<div class="carrossel-item" data-id="' + esc(ind.id) + '" role="button" tabindex="0" ' +
        'aria-label="' + esc(ind.nome) + ', clique para ver gráfico ampliado e metodologia">' +
        window.DIEESE360.montarCartaoFlip(ind, series[ind.id] || []) + '</div>';
    }).join('');
    // Carrossel contínuo (igual ao ticker do topo): pista duplicada, animação
    // translateX(-50%) em loop, pausa ao passar o mouse/focar (para dar tempo
    // de clicar). A cópia (2ª metade) fica fora da navegação por teclado
    // (aria-hidden/tabindex -1) e some com prefers-reduced-motion, sobrando
    // só a lista real, com rolagem nativa (ver CSS).
    var itensCopia = indicadoresDim.map(function (ind) {
      return '<div class="carrossel-item carrossel-item-copia" data-id="' + esc(ind.id) + '" aria-hidden="true" tabindex="-1">' +
        window.DIEESE360.montarCartaoFlip(ind, series[ind.id] || []) + '</div>';
    }).join('');
    trilho.innerHTML = '<div class="carrossel-pista">' + itensHtml + itensCopia + '</div>';
    trilho.querySelectorAll('.carrossel-item').forEach(function (item) {
      function abrirModal() {
        var id = item.getAttribute('data-id');
        var ind = indicadoresPorId[id];
        if (!ind) return;
        D.carregarSerie(id, 36).then(function (serie) {
          window.DIEESE360.abrirCartaoModal(ind, serie);
        });
      }
      item.addEventListener('click', function (e) {
        if (e.target.closest('a')) return;
        abrirModal();
      });
      item.addEventListener('keydown', function (e) {
        if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); abrirModal(); }
      });
    });
  }

  // Prévia da dimensão "mercados" na home: cartões compactos (valor +
  // variação + sparkline), cada um já linkando para a página própria
  // (mercados.html) — pedido explícito do responsável do projeto (2026-10-23):
  // a seção da home não pode ser só texto estático, precisa mostrar um
  // resumo real de indicadores antes de levar para a página interna.
  function preencherPreviewMercados(indicadores, series) {
    var grade = document.getElementById('mercados-teaser-grade');
    if (!grade) return;
    var porId = {};
    indicadores.forEach(function (i) { porId[i.id] = i; });
    var cartoes = PREVIEW_MERCADOS.map(function (id) {
      var indicador = porId[id];
      var serieAsc = series[id] || [];
      if (!indicador || !serieAsc.length) return '';
      var atual = serieAsc[serieAsc.length - 1];
      var variacao = D.calcularVariacao(indicador, serieAsc);
      var chip = variacao
        ? '<span class="chip-tendencia ' + (variacao.valor > 0 ? 'boa' : (variacao.valor < 0 ? 'ruim' : 'neutra')) + '">' +
          (variacao.valor > 0 ? '▲' : (variacao.valor < 0 ? '▼' : '—')) + ' ' + esc(D.formatarNumero(Math.abs(variacao.valor), 2)) + '%</span>'
        : '';
      return (
        '<a class="mercados-teaser-card" href="mercados.html">' +
        '<span class="mercados-teaser-card-nome">' + esc(indicador.nome) + '</span>' +
        '<strong class="mercados-teaser-card-valor">' + esc(D.formatarValor(indicador, atual.valor)) + '</strong>' +
        chip +
        D.montarSparkline(serieAsc) +
        '</a>'
      );
    }).filter(Boolean);
    grade.innerHTML = cartoes.length
      ? cartoes.join('')
      : '<p class="aviso demo">Nenhum dado de mercado publicado ainda.</p>';
  }

  function iniciar() {
    montarGradeDimensoes();
    montarEstruturaResumoDia();
    montarEstruturaSecoesDimensao();
    if (!P.sb) {
      document.getElementById('resumo-dia').innerHTML = '<p class="aviso demo">Não foi possível conectar ao Supabase. Confira js/config.js.</p>';
      return;
    }
    D.carregarIndicadores().then(function (indicadores) {
      var idsTickerDestaque = TICKER.concat(DESTAQUES).filter(function (id, i, arr) { return arr.indexOf(id) === i; });
      var todosIds = indicadores.map(function (i) { return i.id; });
      var porDimensao = {};
      ORDEM_DIMENSOES.forEach(function (c) { porDimensao[c] = []; });
      indicadores.forEach(function (i) { if (porDimensao[i.dimensao]) porDimensao[i.dimensao].push(i); });
      preencherArvoreDimensoes(porDimensao);

      // Rápido: só o ticker e os indicadores em destaque (poucos ids) —
      // aparece primeiro, sem esperar o resto.
      D.carregarSeriesPorIndicadores(idsTickerDestaque, 24).then(function (series) {
        montarTicker(indicadores, series);
        preencherDestaque(indicadores, series);
        window.DIEESE360.animarEntrada(document.getElementById('resumo-dia'));
      });

      // Em paralelo, mas independente: a tabela de maiores variações precisa
      // só dos 2 últimos pontos de cada um dos 55 indicadores (consulta leve,
      // uma só chamada), preenchida assim que voltar.
      D.carregarSeriesPorIndicadores(todosIds, 2).then(function (series) {
        preencherVariacoes(indicadores, series);
      });

      // Prévia de mercados: fetch independente e leve (só 4 ids), preenche
      // assim que chegar, sem depender do resto da home.
      D.carregarSeriesPorIndicadores(PREVIEW_MERCADOS, 24).then(function (series) {
        preencherPreviewMercados(indicadores, series);
      });

      // Cada dimensão busca sua própria série (uma chamada por dimensão, não
      // uma por indicador) e preenche o próprio carrossel assim que chegar.
      ORDEM_DIMENSOES.forEach(function (chave) {
        var idsDim = porDimensao[chave].map(function (i) { return i.id; });
        if (!idsDim.length) { preencherCarrossel(chave, [], {}); return; }
        D.carregarSeriesPorIndicadores(idsDim, 24).then(function (series) {
          preencherCarrossel(chave, porDimensao[chave], series);
        });
      });
    }).catch(function (erro) {
      document.getElementById('resumo-dia').innerHTML = '<p class="aviso demo">' + esc(P.mensagemErro(erro)) + '</p>';
    });
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', iniciar); else iniciar();
})();
