// Página dedicada "Mercados financeiros" (mercados.html) — layout no padrão
// de painel de bolsa (hero com os 4 índices + tabelas por categoria), bem
// diferente do cartão-padrão do resto da plataforma, a pedido do responsável
// do projeto (2026-10-15): "que a visualização fosse igual aos dos
// principais sites de bolsas de valores". Ver ADR 0010 — esta dimensão não é
// dado produzido pelo DIEESE, por isso fica numa página separada, não
// misturada ao carrossel das outras 6 dimensões.
//
// Fase 1 de ampliação (2026-10-23, ver
// research/notas/INVENTARIO_BENCHMARK_MERCADOS_FINANCEIROS.md, seção 6):
// retorno por janela de tempo exposto direto (sem precisar abrir gráfico,
// inspirado no Yahoo Finance), faixa visual do dia e de 52 semanas
// (inspirado em Yahoo/MarketWatch/Investing.com), volume quando disponível,
// e um selo lembrando que a fonte é um agregador de mercado, não dado
// produzido pelo DIEESE (recomendação 5 do inventário).
(function () {
  'use strict';
  var P = window.Painel;
  var D = window.DIEESE360.dados;
  var esc = P.esc;

  var INDICES = ['ibovespa', 'sp500', 'nasdaq', 'dow_jones'];
  var CRIPTO = ['bitcoin', 'ethereum'];
  // petr4/vale3/itub4 continuam cadastrados como indicadores avulsos (fonte
  // Yahoo, ~1 ano de histórico) — não removidos ainda, mas a tabela de 3
  // ações que os exibia foi substituída pela busca sobre as ~300 ações da
  // B3 (fonte brapi.dev + Yahoo, ver carregarMapaB3/carregarSerieB3 abaixo,
  // 2026-10-26). Decisão de aposentar esses 3 indicadores fica para depois
  // de confirmar que o histórico bate (ver plano aprovado desta sessão).
  var TODOS = INDICES.concat(CRIPTO);

  function diasDesdeInicioDoAno() {
    var hoje = new Date();
    var inicioAno = new Date(hoje.getFullYear(), 0, 1);
    return Math.round((hoje - inicioAno) / 86400000);
  }
  var JANELAS_RETORNO = [
    { dias: 30, rotulo: '1M' },
    { dias: diasDesdeInicioDoAno(), rotulo: 'no ano' },
    { dias: 365, rotulo: '12M' }
  ];

  function formatarVariacaoAbs(indicador, serieAsc) {
    var t = D.calcularTendencia(indicador, serieAsc);
    if (!t) return '<span class="mercados-sem-dado">—</span>';
    var sinal = t.delta > 0 ? '+' : '';
    return '<span class="mercados-variacao ' + t.direcaoMudanca + '">' + t.seta + ' ' + sinal + esc(D.formatarValor(indicador, t.delta)) + '</span>';
  }

  function formatarVariacaoPct(indicador, serieAsc) {
    var v = D.calcularVariacao(indicador, serieAsc);
    if (!v) return '<span class="mercados-sem-dado">—</span>';
    var sinal = v.valor > 0 ? '+' : '';
    return '<span class="mercados-variacao ' + v.direcao + '">' + sinal + D.formatarNumero(v.valor, 2) + '%</span>';
  }

  // Retorno nas 3 janelas (1M/no ano/12M) lado a lado — null quando o
  // histórico ainda não cobre a janela (ex. ticker novo) não quebra o
  // layout, só não mostra aquele badge.
  function montarRetornos(serieAsc) {
    var itens = JANELAS_RETORNO.map(function (j) {
      var r = D.calcularRetornoPeriodo(serieAsc, j.dias);
      if (!r) return '';
      var direcao = r.percentual > 0 ? 'alta' : (r.percentual < 0 ? 'baixa' : 'estavel');
      var sinal = r.percentual > 0 ? '+' : '';
      return '<span class="mercados-retorno"><span class="mercados-retorno-rotulo">' + esc(j.rotulo) + '</span>' +
        '<span class="mercados-variacao ' + direcao + '">' + sinal + D.formatarNumero(r.percentual, 1) + '%</span></span>';
    }).filter(Boolean);
    if (!itens.length) return '';
    return '<div class="mercados-retornos">' + itens.join('') + '</div>';
  }

  // Faixa visual (range bar) com marcador de posição do preço atual dentro
  // de um intervalo [min, max] — mesmo princípio usado por Yahoo/MarketWatch/
  // Investing.com para a variação do dia e a faixa de 52 semanas (ver
  // inventário, padrões recorrentes). min/max vêm do metadata do ponto mais
  // recente (só a "foto do dia" tem esses campos, ver pipeline de
  // transformação) — se ausentes, não desenha nada.
  function montarFaixa(rotulo, valorAtual, min, max, indicador) {
    if (min == null || max == null || max <= min) return '';
    var posicao = Math.max(0, Math.min(100, ((valorAtual - min) / (max - min)) * 100));
    return (
      '<div class="mercados-faixa-bloco">' +
      '<div class="mercados-faixa-rotulo"><span>' + esc(rotulo) + '</span></div>' +
      '<div class="mercados-faixa" title="' + esc(D.formatarValor(indicador, min)) + ' – ' + esc(D.formatarValor(indicador, max)) + '">' +
      '<span class="mercados-faixa-marcador" style="left:' + posicao.toFixed(1) + '%"></span>' +
      '</div>' +
      '<div class="mercados-faixa-extremos"><span>' + esc(D.formatarValor(indicador, min)) + '</span><span>' + esc(D.formatarValor(indicador, max)) + '</span></div>' +
      '</div>'
    );
  }

  function montarFaixas(indicador, atual) {
    var meta = atual.metadata || {};
    var blocos = [
      montarFaixa('Dia', atual.valor, meta.minima_dia, meta.maxima_dia, indicador),
      montarFaixa('52 semanas', atual.valor, meta.minima_52_semanas, meta.maxima_52_semanas, indicador)
    ].filter(Boolean);
    if (!blocos.length) return '';
    return '<div class="mercados-faixas">' + blocos.join('') + '</div>';
  }

  function montarVolume(atual) {
    var volume = (atual.metadata || {}).volume;
    if (volume == null) return '';
    return '<span class="mercados-volume">Volume: ' + esc(D.formatarNumero(volume, 0)) + '</span>';
  }

  // Comparações com métricas padrão de mercado (média móvel, volatilidade,
  // sequência, faixa de 52 semanas) — ver D.montarComparacoesMercado em
  // dados.js. Aqui só a versão compacta, uma linha por ativo; a versão
  // completa, com cada item separado, fica na página do indicador
  // (indicador.html), que tem mais espaço.
  function montarAnaliseCompacta(indicador, serieAsc) {
    var frases = D.montarComparacoesMercado(indicador, serieAsc);
    if (!frases.length) return '';
    return '<span class="mercados-analise-compacta" title="' + esc(frases.join('. ')) + '">' + esc(frases[0]) + '</span>';
  }

  // Selo lembrando que a fonte é um agregador de mercado (Yahoo Finance),
  // não um indicador produzido/validado pelo DIEESE — recomendação 5 do
  // inventário, mesmo padrão visual de badge já usado em .catalogo-classif.
  function montarSeloFonte() {
    return '<span class="mercados-selo-fonte" title="Cotação agregada pela Yahoo Finance, referência de mercado — não é indicador produzido ou validado pelo DIEESE.">fonte: agregador de mercado</span>';
  }

  function montarCardHero(indicador, serieAsc) {
    if (!serieAsc.length) return '';
    var atual = serieAsc[serieAsc.length - 1];
    return (
      '<a class="mercados-hero-card" href="indicador.html?id=' + esc(indicador.id) + '">' +
      '<span class="mercados-hero-nome">' + esc(indicador.nome) + '</span>' +
      '<strong class="mercados-hero-valor">' + esc(D.formatarValor(indicador, atual.valor)) + '</strong>' +
      '<span class="mercados-hero-variacoes">' + formatarVariacaoAbs(indicador, serieAsc) + formatarVariacaoPct(indicador, serieAsc) + '</span>' +
      montarRetornos(serieAsc) +
      D.montarSparkline(serieAsc) +
      montarAnaliseCompacta(indicador, serieAsc) +
      '</a>'
    );
  }

  function montarLinhaTabela(indicador, serieAsc) {
    if (!serieAsc.length) {
      return '<tr><td>' + esc(indicador.nome) + '</td><td colspan="4" class="mercados-sem-dado">Sem dado publicado ainda.</td></tr>';
    }
    var atual = serieAsc[serieAsc.length - 1];
    return (
      '<tr class="mercados-linha" data-id="' + esc(indicador.id) + '" tabindex="0" role="button" aria-label="' + esc(indicador.nome) + ', ver gráfico e metodologia">' +
      '<td class="mercados-col-nome"><strong>' + esc(indicador.nome) + '</strong>' +
      '<span>' + esc(indicador.fonte.replace(/^Yahoo Finance \(ticker /, '').replace(/\)$/, '')) + '</span>' +
      montarSeloFonte() +
      montarVolume(atual) +
      montarAnaliseCompacta(indicador, serieAsc) +
      '</td>' +
      '<td class="mercados-col-grafico">' + D.montarSparkline(serieAsc) + montarRetornos(serieAsc) + '</td>' +
      '<td class="mercados-col-valor">' + esc(D.formatarValor(indicador, atual.valor)) + montarFaixas(indicador, atual) + '</td>' +
      '<td class="mercados-col-variacao">' + formatarVariacaoAbs(indicador, serieAsc) + '</td>' +
      '<td class="mercados-col-variacao">' + formatarVariacaoPct(indicador, serieAsc) + '</td>' +
      '</tr>'
    );
  }

  function montarTabela(idTabela, ids, indicadoresPorId, series) {
    var corpo = document.getElementById(idTabela);
    if (!corpo) return;
    corpo.innerHTML = ids.map(function (id) {
      var indicador = indicadoresPorId[id];
      if (!indicador) return '';
      return montarLinhaTabela(indicador, series[id] || []);
    }).join('');
    corpo.querySelectorAll('.mercados-linha').forEach(function (linha) {
      function abrir() { window.location.href = 'indicador.html?id=' + encodeURIComponent(linha.getAttribute('data-id')); }
      linha.addEventListener('click', abrir);
      linha.addEventListener('keydown', function (e) { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); abrir(); } });
    });
  }

  // ------------------------------------------------------------------
  // Fase 2 (2026-10-26) — mapa de calor de ações da B3, fora do catálogo
  // indicadores/indicadores_serie de propósito (ver migração 0011 e ADR
  // 0010): tabelas próprias mercado_b3_ativos/mercado_b3_serie, fonte
  // brapi.dev. Setor → bloco de setor (squarify), ação → bloco dentro do
  // setor (squarify aninhado), tamanho = capitalização de mercado, cor =
  // variação % do dia. Ao lado, um indicador de amplitude ("X de Y em
  // alta") — recomendação 3 do inventário de benchmark: um mapa ponderado
  // por capitalização pode parecer "tudo verde" por causa de poucas
  // megacaps, mesmo com a maioria das ações em queda; a amplitude mostra
  // isso separadamente, sem depender só da leitura visual do mapa.
  // ------------------------------------------------------------------
  function buscarDataMaisRecenteB3() {
    return P.sb.from('mercado_b3_serie').select('data_referencia')
      .order('data_referencia', { ascending: false }).limit(1).then(function (r) {
        if (r.error) throw r.error;
        return r.data && r.data[0] ? r.data[0].data_referencia : null;
      });
  }

  function carregarMapaB3() {
    return buscarDataMaisRecenteB3().then(function (data) {
      if (!data) return [];
      return P.sb.from('mercado_b3_ativos').select('ticker,nome,setor').then(function (rAtivos) {
        if (rAtivos.error) throw rAtivos.error;
        return P.sb.from('mercado_b3_serie').select('ticker,preco,variacao_pct,market_cap')
          .eq('data_referencia', data).then(function (rSerie) {
            if (rSerie.error) throw rSerie.error;
            var porTicker = {};
            (rSerie.data || []).forEach(function (p) { porTicker[p.ticker] = p; });
            return (rAtivos.data || []).map(function (a) {
              var p = porTicker[a.ticker];
              if (!p || p.market_cap == null) return null;
              return {
                ticker: a.ticker, nome: a.nome, setor: a.setor || 'Outros',
                valor: Number(p.market_cap), preco: p.preco, variacaoPct: p.variacao_pct
              };
            }).filter(Boolean);
          });
      });
    });
  }

  function corPorVariacao(pct) {
    if (pct == null) return 'rgba(154,154,154,.3)';
    var intensidade = Math.min(Math.abs(pct) / 3, 1);
    var alfa = (0.22 + 0.65 * intensidade).toFixed(2);
    var base = pct > 0 ? '12,163,12' : (pct < 0 ? '208,59,59' : '154,154,154');
    return 'rgba(' + base + ',' + alfa + ')';
  }

  function montarAmplitude(ativos) {
    var comVariacao = ativos.filter(function (a) { return a.variacaoPct != null; });
    var emAlta = comVariacao.filter(function (a) { return a.variacaoPct > 0; }).length;
    var pct = comVariacao.length ? Math.round((emAlta / comVariacao.length) * 100) : 0;
    return (
      '<div class="mercados-amplitude">' +
      '<strong>' + emAlta + ' de ' + comVariacao.length + '</strong> ações em alta hoje (' + pct + '%)' +
      '<span class="mercados-amplitude-barra"><span style="width:' + pct + '%"></span></span>' +
      '<span class="mercados-amplitude-nota">O tamanho de cada bloco é a capitalização de mercado — poucas empresas grandes podem dominar a cor do mapa mesmo quando a maioria das ações está em queda (ou vice-versa). Esta barra mostra a amplitude real, ação a ação.</span>' +
      '</div>'
    );
  }

  function montarMapaCalor(ativos) {
    var alvoSvg = document.getElementById('mercados-mapa-svg');
    var alvoAmplitude = document.getElementById('mercados-amplitude-caixa');
    if (!alvoSvg) return;
    if (!ativos.length) {
      alvoSvg.closest('.mercados-mapa-caixa').innerHTML = '<p class="aviso demo">Nenhum dado de ações da B3 publicado ainda.</p>';
      return;
    }
    var T = window.DIEESE360.treemap;
    var LARGURA = 1000, ALTURA = 560;

    var porSetor = {};
    ativos.forEach(function (a) {
      (porSetor[a.setor] = porSetor[a.setor] || []).push(a);
    });
    var setores = Object.keys(porSetor).map(function (nome) {
      var itens = porSetor[nome];
      return { setor: nome, itens: itens, valor: itens.reduce(function (s, a) { return s + a.valor; }, 0) };
    }).sort(function (a, b) { return b.valor - a.valor; });

    T.squarify(setores, 0, 0, LARGURA, ALTURA);

    var svgPartes = [];
    setores.forEach(function (s) {
      var mostrarRotulo = s.largura > 60 && s.altura > 24;
      var reservaRotulo = mostrarRotulo ? 15 : 0;
      var itens = s.itens.slice().sort(function (a, b) { return b.valor - a.valor; });
      T.squarify(itens, s.x + 1, s.y + reservaRotulo + 1, Math.max(s.largura - 2, 0), Math.max(s.altura - reservaRotulo - 2, 0));

      if (mostrarRotulo) {
        svgPartes.push(
          '<text class="mercados-mapa-setor-rotulo" x="' + (s.x + 4).toFixed(1) + '" y="' + (s.y + 11).toFixed(1) + '">' + esc(s.setor) + '</text>'
        );
      }
      itens.forEach(function (it) {
        if (it.largura <= 0 || it.altura <= 0) return;
        var mostrarTexto = it.largura > 30 && it.altura > 16;
        var titulo = it.nome + ' (' + it.ticker + ') — ' + D.formatarValor({ unidade: 'R$' }, it.preco) +
          (it.variacaoPct != null ? ', ' + (it.variacaoPct > 0 ? '+' : '') + D.formatarNumero(it.variacaoPct, 2) + '% no dia' : '');
        svgPartes.push(
          '<g class="mercados-mapa-bloco">' +
          '<rect x="' + it.x.toFixed(1) + '" y="' + it.y.toFixed(1) + '" width="' + it.largura.toFixed(1) + '" height="' + it.altura.toFixed(1) + '" fill="' + corPorVariacao(it.variacaoPct) + '"><title>' + esc(titulo) + '</title></rect>' +
          (mostrarTexto ? '<text x="' + (it.x + it.largura / 2).toFixed(1) + '" y="' + (it.y + it.altura / 2 + 3).toFixed(1) + '" text-anchor="middle">' + esc(it.ticker) + '</text>' : '') +
          '</g>'
        );
      });
    });

    alvoSvg.setAttribute('viewBox', '0 0 ' + LARGURA + ' ' + ALTURA);
    alvoSvg.innerHTML = svgPartes.join('');
    if (alvoAmplitude) alvoAmplitude.innerHTML = montarAmplitude(ativos);
  }

  // ------------------------------------------------------------------
  // Busca + maiores altas/baixas sobre as ~300 ações da B3 (2026-10-26,
  // pedido do responsável do projeto: "eu quero todas as ações... traga
  // um local de busca"). Reaproveita o mesmo `ativos` já carregado por
  // carregarMapaB3 — não faz uma segunda consulta ao banco. Ranking
  // reaproveita o mesmo padrão visual (.resumo-variacoes-linha/.rank-pos)
  // já usado no resumo do dia da home (ver js/inicio.js).
  // ------------------------------------------------------------------
  function montarRankingB3(ativos, direcao, limite) {
    var comVariacao = ativos.filter(function (a) { return a.variacaoPct != null; });
    var filtrados = comVariacao.filter(function (a) { return direcao === 'alta' ? a.variacaoPct > 0 : a.variacaoPct < 0; });
    filtrados.sort(function (a, b) { return Math.abs(b.variacaoPct) - Math.abs(a.variacaoPct); });
    filtrados = filtrados.slice(0, limite);
    if (!filtrados.length) {
      return '<li><span class="nome">Nenhuma variação ' + (direcao === 'alta' ? 'positiva' : 'negativa') + ' publicada hoje.</span></li>';
    }
    return filtrados.map(function (a, idx) {
      var seta = direcao === 'alta' ? '▲ +' : '▼ -';
      return '<li><button type="button" class="resumo-variacoes-linha ' + direcao + '" data-ticker="' + esc(a.ticker) + '">' +
        '<span class="rank-pos rank-' + direcao + '">#' + (idx + 1) + '</span>' +
        '<span class="nome">' + esc(a.nome) + '<span class="vs-periodo">' + esc(a.ticker) + (a.setor ? ' · ' + esc(a.setor) : '') + '</span></span>' +
        '<span class="percentual ' + direcao + '">' + seta + esc(D.formatarNumero(Math.abs(a.variacaoPct), 2)) + '%</span>' +
        '</button></li>';
    }).join('');
  }

  // Busca por nome ou ticker — client-side simples (lista cabe inteira na
  // memória, ~300 itens, não justifica busca no servidor). Mostra até 20
  // resultados para não virar uma lista longa demais na tela.
  function montarResultadosBusca(ativos, termo) {
    var alvo = document.getElementById('mercados-busca-resultados');
    if (!alvo) return;
    var t = termo.trim().toLowerCase();
    if (!t) { alvo.hidden = true; alvo.innerHTML = ''; return; }
    var encontrados = ativos.filter(function (a) {
      return a.nome.toLowerCase().indexOf(t) >= 0 || a.ticker.toLowerCase().indexOf(t) >= 0;
    }).slice(0, 20);
    alvo.hidden = false;
    if (!encontrados.length) {
      alvo.innerHTML = '<p class="mercados-busca-vazio">Nenhuma ação encontrada para "' + esc(termo) + '".</p>';
      return;
    }
    alvo.innerHTML = encontrados.map(function (a) {
      var dir = a.variacaoPct > 0 ? 'alta' : (a.variacaoPct < 0 ? 'baixa' : 'estavel');
      var sinal = a.variacaoPct > 0 ? '+' : '';
      return '<button type="button" class="mercados-busca-item" data-ticker="' + esc(a.ticker) + '">' +
        '<span class="mercados-busca-item-nome">' + esc(a.nome) + '<span class="mercados-busca-item-ticker">' + esc(a.ticker) + '</span></span>' +
        (a.preco != null ? '<span class="mercados-busca-item-preco">' + esc(D.formatarValor({ unidade: 'R$' }, a.preco)) + '</span>' : '') +
        (a.variacaoPct != null ? '<span class="mercados-variacao ' + dir + '">' + sinal + esc(D.formatarNumero(a.variacaoPct, 2)) + '%</span>' : '<span class="mercados-sem-dado">—</span>') +
        '</button>';
    }).join('');
  }

  // Série histórica de uma ação da B3 — mercado_b3_serie, não
  // indicadores_serie (tabelas separadas de propósito, ver migração 0011).
  // Mapeia `preco` para `valor` só para reaproveitar montarGraficoLinha
  // (js/grafico-linha.js), que não sabe nada sobre essa tabela.
  function carregarSerieB3(ticker) {
    return P.sb.from('mercado_b3_serie').select('data_referencia,preco')
      .eq('ticker', ticker).order('data_referencia', { ascending: true })
      .then(function (r) {
        if (r.error) throw r.error;
        return (r.data || []).map(function (p) { return { data_referencia: p.data_referencia, valor: p.preco }; });
      });
  }

  function abrirDetalheAcao(ticker, ativosPorTicker) {
    var alvo = document.getElementById('mercados-acao-detalhe');
    var ativo = ativosPorTicker[ticker];
    if (!alvo || !ativo) return;
    var indicadorFake = { unidade: 'R$', nome: ativo.nome };
    var dir = ativo.variacaoPct > 0 ? 'alta' : (ativo.variacaoPct < 0 ? 'baixa' : 'estavel');
    var sinal = ativo.variacaoPct > 0 ? '+' : '';

    alvo.hidden = false;
    alvo.innerHTML =
      '<div class="mercados-acao-detalhe-topo">' +
      '<div><strong class="mercados-acao-detalhe-nome">' + esc(ativo.nome) + '</strong>' +
      '<span class="mercados-acao-detalhe-ticker">' + esc(ativo.ticker) + (ativo.setor ? ' · ' + esc(ativo.setor) : '') + '</span></div>' +
      '<div class="mercados-acao-detalhe-valores">' +
      '<strong>' + esc(D.formatarValor(indicadorFake, ativo.preco)) + '</strong>' +
      (ativo.variacaoPct != null ? '<span class="mercados-variacao ' + dir + '">' + sinal + esc(D.formatarNumero(ativo.variacaoPct, 2)) + '%</span>' : '') +
      '</div>' +
      '<button type="button" class="mercados-acao-detalhe-fechar" aria-label="Fechar detalhe">×</button>' +
      '</div>' +
      '<div class="grafico-linha-caixa mercados-acao-detalhe-grafico" id="mercados-acao-detalhe-grafico"><p class="aviso demo">Carregando histórico…</p></div>';

    alvo.querySelector('.mercados-acao-detalhe-fechar').addEventListener('click', function () {
      alvo.hidden = true;
      alvo.innerHTML = '';
    });
    alvo.scrollIntoView({ behavior: 'smooth', block: 'nearest' });

    carregarSerieB3(ticker).then(function (serie) {
      var container = document.getElementById('mercados-acao-detalhe-grafico');
      if (!container) return;
      if (serie.length < 2) {
        container.innerHTML = '<p class="aviso demo">Histórico insuficiente ainda para este ativo — vai crescendo a cada coleta diária.</p>';
        return;
      }
      container.innerHTML = '';
      window.DIEESE360.montarGraficoLinha(container, serie, {
        formatarValor: function (v) { return D.formatarValor(indicadorFake, v); },
        formatarData: D.formatarDataCurta
      });
    }).catch(function (erro) {
      var container = document.getElementById('mercados-acao-detalhe-grafico');
      if (container) container.innerHTML = '<p class="aviso demo">' + esc(P.mensagemErro(erro)) + '</p>';
    });
  }

  function iniciar() {
    carregarMapaB3().then(function (ativos) {
      montarMapaCalor(ativos);

      var ativosPorTicker = {};
      ativos.forEach(function (a) { ativosPorTicker[a.ticker] = a; });

      var alvoAltas = document.getElementById('mercados-ranking-altas');
      var alvoBaixas = document.getElementById('mercados-ranking-baixas');
      if (alvoAltas) alvoAltas.innerHTML = montarRankingB3(ativos, 'alta', 5);
      if (alvoBaixas) alvoBaixas.innerHTML = montarRankingB3(ativos, 'baixa', 5);

      var ranking = document.getElementById('mercados-ranking-b3');
      if (ranking) {
        ranking.addEventListener('click', function (e) {
          var botao = e.target.closest('[data-ticker]');
          if (botao) abrirDetalheAcao(botao.getAttribute('data-ticker'), ativosPorTicker);
        });
      }

      var inputBusca = document.getElementById('mercados-busca-acao');
      var resultadosBusca = document.getElementById('mercados-busca-resultados');
      if (inputBusca && resultadosBusca) {
        inputBusca.addEventListener('input', function () { montarResultadosBusca(ativos, inputBusca.value); });
        resultadosBusca.addEventListener('click', function (e) {
          var botao = e.target.closest('[data-ticker]');
          if (!botao) return;
          abrirDetalheAcao(botao.getAttribute('data-ticker'), ativosPorTicker);
          resultadosBusca.hidden = true;
          inputBusca.value = '';
        });
        document.addEventListener('click', function (e) {
          if (!resultadosBusca.hidden && !e.target.closest('.mercados-busca-caixa')) resultadosBusca.hidden = true;
        });
      }
    }).catch(function (erro) {
      var caixa = document.querySelector('.mercados-mapa-caixa');
      if (caixa) caixa.innerHTML = '<p class="aviso demo">' + esc(P.mensagemErro(erro)) + '</p>';
      ['mercados-ranking-altas', 'mercados-ranking-baixas'].forEach(function (id) {
        var el = document.getElementById(id);
        if (el) el.innerHTML = '<li><span class="nome">' + esc(P.mensagemErro(erro)) + '</span></li>';
      });
    });

    D.carregarIndicadores().then(function (indicadores) {
      var porId = {};
      indicadores.forEach(function (i) { porId[i.id] = i; });
      var disponiveis = TODOS.filter(function (id) { return porId[id]; });
      if (!disponiveis.length) {
        document.getElementById('mercados-hero').innerHTML = '<p class="aviso demo">Nenhum dado de mercado publicado ainda.</p>';
        return Promise.resolve();
      }
      return D.carregarSeriesPorIndicadores(disponiveis, 90).then(function (series) {
        document.getElementById('mercados-hero').innerHTML = INDICES.map(function (id) {
          return porId[id] ? montarCardHero(porId[id], series[id] || []) : '';
        }).join('');
        montarTabela('mercados-corpo-cripto', CRIPTO, porId, series);
        document.querySelectorAll('.mercados-atualizado').forEach(function (el) {
          var pontos = series[INDICES[0]] || [];
          if (!pontos.length) return;
          var d = new Date(pontos[pontos.length - 1].data_referencia + 'T00:00:00');
          el.textContent = 'Última atualização: ' + d.toLocaleDateString('pt-BR', { day: '2-digit', month: 'long', year: 'numeric' });
        });
        window.DIEESE360.animarEntrada && window.DIEESE360.animarEntrada(document.body);
      });
    }).catch(function (erro) {
      document.getElementById('mercados-hero').innerHTML = '<p class="aviso demo">' + esc(P.mensagemErro(erro)) + '</p>';
    });
  }

  document.addEventListener('DOMContentLoaded', iniciar);
})();
