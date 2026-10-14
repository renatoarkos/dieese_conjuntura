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

  var ORDEM_DIMENSOES = ['macroeconomia', 'monetario_credito', 'inflacao', 'mercado_trabalho', 'caged'];

  var ICONES_DIMENSAO = {
    macroeconomia: 'assets/dimensoes/icone-macroeconomia.png',
    monetario_credito: 'assets/dimensoes/icone-monetario-credito.png',
    inflacao: 'assets/dimensoes/icone-inflacao.png',
    mercado_trabalho: 'assets/dimensoes/icone-mercado-trabalho.png',
    caged: 'assets/dimensoes/icone-caged.png'
  };

  // Texto mais completo por dimensão (o que é, o que cobre, por que importa
  // para a leitura de conjuntura) — complementa a descrição de uma linha já
  // usada em D.DIMENSOES (essa continua servindo o resumo rápido da grade).
  var TEXTO_DIMENSAO = {
    macroeconomia: 'Reúne os indicadores que descrevem o ritmo geral da economia brasileira: Produto Interno Bruto, comércio exterior, investimento, preços de commodities e contas públicas. É a base para situar qualquer leitura setorial dentro do ciclo econômico em curso.',
    monetario_credito: 'Cobre a taxa básica de juros, as taxas cobradas ao tomador final, o crédito concedido pelo sistema financeiro e o endividamento das famílias. Mostra como a política monetária se transmite ao custo do dinheiro no dia a dia de empresas e trabalhadores.',
    inflacao: 'Acompanha os principais índices de preços ao consumidor (IPCA, INPC, IGP-M) e itens sensíveis ao orçamento familiar, como combustíveis. É o contraponto necessário para ler qualquer variação nominal de salário ou renda em termos reais.',
    mercado_trabalho: 'Reúne emprego, desocupação, rendimento, sindicalização e negociação coletiva: o núcleo da pauta histórica do DIEESE, onde a pesquisa socioeconômica se conecta diretamente à atuação sindical.',
    caged: 'Admissões e desligamentos formais apurados por microdado todo mês, com granularidade menor que a RAIS anual. Antecipa movimentos do mercado de trabalho formal entre uma apuração anual e outra.'
  };

  // Indicadores que compõem o ticker de topo: um recorte entre dimensões,
  // priorizando os de atualização mais frequente.
  var TICKER = ['selic', 'cambio_dolar', 'ipca', 'commodities_geral', 'balanca_saldo', 'taxa_desocupacao', 'bndes_desembolsos'];
  // Indicadores em destaque no resumo do dia — um recorte entre dimensões,
  // cada um vira um cartão giratório com gráfico completo no carrossel.
  var DESTAQUES = ['cambio_dolar', 'selic', 'ipca', 'taxa_desocupacao'];

  // Frase "vs. <período>" explícita — usada em toda exibição de variação
  // (ticker, lista de maiores variações, destaque), a pedido do responsável
  // do projeto (2026-10-14): "preciso que diga a que se refere cada um,
  // mostrando em que comparação fez a variação".
  function vsPeriodo(indicador, pontoAnterior) {
    return 'vs. ' + D.formatarDataReferencia(pontoAnterior.data_referencia, indicador.periodicidade);
  }

  // Só a casca da grade (ícone + nome) — a árvore de indicadores de cada
  // dimensão é preenchida depois, quando os dados chegam (ver
  // preencherArvoreDimensoes). É <a>, não <div>: cada cartão é um link para
  // a seção detalhada da própria dimensão mais abaixo.
  function montarGradeDimensoes() {
    var alvo = document.getElementById('grade-dimensoes');
    var html = '';
    var i = 1;
    Object.keys(D.DIMENSOES).forEach(function (chave) {
      var dim = D.DIMENSOES[chave];
      var icone = ICONES_DIMENSAO[chave] || '';
      html += '<a class="cartao-dimensao" href="#dimensao-' + esc(chave) + '">' +
        '<div class="cartao-dimensao-topo">' +
        '<span class="num">Dimensão ' + (i++) + '</span>' +
        (icone ? '<img src="' + esc(icone) + '" alt="" class="cartao-dimensao-icone" width="48" height="48" loading="lazy">' : '') +
        '</div>' +
        '<h3>' + esc(dim.nome) + '</h3>' +
        '<ul class="cartao-dimensao-arvore" id="arvore-' + esc(chave) + '"><li>Carregando indicadores…</li></ul>' +
        '</a>';
    });
    alvo.innerHTML = html;
  }

  // Preenche a árvore de cada cartão da grade com até 5 nomes de indicador
  // reais + "e mais N" — nunca repete a descrição de uma linha, que já
  // aparece por extenso na seção detalhada da dimensão (evita mostrar o
  // mesmo texto duas vezes, redundância relatada pelo responsável do
  // projeto, 2026-10-14).
  function preencherArvoreDimensoes(porDimensao) {
    ORDEM_DIMENSOES.forEach(function (chave) {
      var alvo = document.getElementById('arvore-' + chave);
      if (!alvo) return;
      var lista = porDimensao[chave] || [];
      if (!lista.length) { alvo.innerHTML = '<li>Em preparação.</li>'; return; }
      var visiveis = lista.slice(0, 5);
      var html = visiveis.map(function (ind) { return '<li>' + esc(ind.nome) + '</li>'; }).join('');
      if (lista.length > visiveis.length) html += '<li class="mais">+ ' + (lista.length - visiveis.length) + ' indicador(es)</li>';
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

  // Tabela de maiores variações: usa D.calcularVariacao, que compara cada
  // indicador na unidade certa (pontos percentuais para quem já é expresso
  // em %, variação percentual para os demais) — nunca "percentual da
  // percentual", que gerava número sem sentido (ex. IPCA "+356%", achado
  // pelo responsável do projeto, 2026-10-14). Cada linha mostra também
  // "vs. <período>" e é um botão, não um link: clicar abre o cartão
  // giratório em modal (cartao-modal.js) em vez de navegar — mesma regra já
  // fixada para qualquer cartão da plataforma.
  function montarListaVariacoes(indicadores, series, direcao, limite) {
    var linhas = indicadores.map(function (ind) {
      var variacao = D.calcularVariacao(ind, series[ind.id] || []);
      return variacao ? { indicador: ind, variacao: variacao } : null;
    }).filter(Boolean);
    linhas = linhas.filter(function (l) { return direcao === 'alta' ? l.variacao.valor > 0 : l.variacao.valor < 0; });
    linhas.sort(function (a, b) { return Math.abs(b.variacao.valor) - Math.abs(a.variacao.valor); });
    linhas = linhas.slice(0, limite);
    if (!linhas.length) return '<li><span class="nome">Nenhuma variação ' + (direcao === 'alta' ? 'positiva' : 'negativa') + ' no período.</span></li>';
    return linhas.map(function (l) {
      return '<li><button type="button" class="resumo-variacoes-linha" data-id="' + esc(l.indicador.id) + '">' +
        '<span class="nome">' + esc(l.indicador.nome) + '<span class="vs-periodo">' + esc(vsPeriodo(l.indicador, l.variacao.anterior)) + '</span></span>' +
        '<span class="percentual ' + direcao + '">' + (direcao === 'alta' ? '▲' : '▼') + ' ' + Math.abs(l.variacao.valor).toFixed(1) + ' ' + esc(l.variacao.sufixo) + '</span>' +
        '</button></li>';
    }).join('');
  }

  // Monta só a casca do resumo do dia (carrossel de destaque + as duas
  // listas, todos em estado "carregando") — nenhuma rede ainda, roda assim
  // que o DOM existe.
  function montarEstruturaResumoDia() {
    var alvo = document.getElementById('resumo-dia');
    alvo.innerHTML =
      '<div class="resumo-destaque">' +
      '<div class="carrossel-cabecalho"><h3>Indicadores em destaque</h3>' +
      '<div class="carrossel-setas">' +
      '<button type="button" class="carrossel-seta" id="seta-ant-destaque" aria-label="Indicador em destaque anterior">‹</button>' +
      '<button type="button" class="carrossel-seta" id="seta-prox-destaque" aria-label="Próximo indicador em destaque">›</button>' +
      '</div></div>' +
      '<div class="carrossel-trilho" id="carrossel-destaque"><p class="aviso demo">Carregando…</p></div>' +
      '</div>' +
      '<div class="resumo-variacoes">' +
      '<div><h3>Maiores altas</h3><ul class="resumo-variacoes-lista" id="resumo-altas"><li>Carregando…</li></ul></div>' +
      '<div><h3>Maiores baixas</h3><ul class="resumo-variacoes-lista" id="resumo-baixas"><li>Carregando…</li></ul></div>' +
      '</div>';
  }

  // Carrossel de 2-4 indicadores em destaque, cada um um cartão giratório
  // com gráfico completo na frente (não só sparkline) — pedido do
  // responsável do projeto (2026-10-14): "o quadro pode ser um carrossel
  // que vai mostrando esses indicadores com o cartão e o gráfico".
  function preencherDestaque(indicadores, series) {
    var trilho = document.getElementById('carrossel-destaque');
    var indicadoresPorId = {};
    var disponiveis = DESTAQUES.map(function (id) {
      var ind = indicadores.filter(function (i) { return i.id === id; })[0];
      if (ind) indicadoresPorId[id] = ind;
      return ind;
    }).filter(Boolean);
    if (!disponiveis.length) { trilho.innerHTML = '<p class="aviso demo">Nenhum indicador em destaque publicado ainda.</p>'; return; }
    trilho.innerHTML = disponiveis.map(function (ind) {
      return '<div class="carrossel-item destaque-item">' + window.DIEESE360.montarCartaoFlip(ind, series[ind.id] || [], { graficoCompleto: true }) + '</div>';
    }).join('');
    window.DIEESE360.ligarCartoesFlip(trilho);
    window.DIEESE360.preencherGraficosCompletos(trilho, indicadoresPorId, series);
    ligarSetasCarrossel(trilho, document.getElementById('seta-ant-destaque'), document.getElementById('seta-prox-destaque'));
  }

  function preencherVariacoes(indicadores, series) {
    document.getElementById('resumo-altas').innerHTML = montarListaVariacoes(indicadores, series, 'alta', 5);
    document.getElementById('resumo-baixas').innerHTML = montarListaVariacoes(indicadores, series, 'baixa', 5);
    ligarCliquesVariacoes(indicadores);
  }

  // Clique numa linha da tabela de variações busca a série completa (só
  // essa, sob demanda — a lista usa só 2 pontos por indicador) e abre o
  // cartão giratório em modal, sem navegar para outra página.
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

  function ligarSetasCarrossel(trilho, setaAnterior, setaProxima) {
    function atualizarEstado() {
      setaAnterior.disabled = trilho.scrollLeft <= 4;
      setaProxima.disabled = trilho.scrollLeft >= trilho.scrollWidth - trilho.clientWidth - 4;
    }
    function largurapasso() {
      var item = trilho.querySelector('.carrossel-item');
      return item ? item.getBoundingClientRect().width + 16 : trilho.clientWidth;
    }
    setaAnterior.addEventListener('click', function () { trilho.scrollBy({ left: -largurapasso(), behavior: 'smooth' }); });
    setaProxima.addEventListener('click', function () { trilho.scrollBy({ left: largurapasso(), behavior: 'smooth' }); });
    trilho.addEventListener('scroll', atualizarEstado);
    atualizarEstado();
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
        '<div class="carrossel-setas">' +
        '<button type="button" class="carrossel-seta" id="seta-ant-' + esc(chave) + '" aria-label="Indicador anterior de ' + esc(dim.nome) + '">‹</button>' +
        '<button type="button" class="carrossel-seta" id="seta-prox-' + esc(chave) + '" aria-label="Próximo indicador de ' + esc(dim.nome) + '">›</button>' +
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
    trilho.innerHTML = indicadoresDim.map(function (ind) {
      return '<div class="carrossel-item">' + window.DIEESE360.montarCartaoFlip(ind, series[ind.id] || []) + '</div>';
    }).join('');
    window.DIEESE360.ligarCartoesFlip(trilho);
    ligarSetasCarrossel(trilho, document.getElementById('seta-ant-' + chave), document.getElementById('seta-prox-' + chave));
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
