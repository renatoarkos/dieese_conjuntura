// Página "Dimensão Política" (politica.html) — não é uma dimensão nova no
// catálogo (os indicadores aqui já pertencem a macroeconomia/mercado_trabalho/
// monetario_credito/inflação, ver dados.js#DIMENSOES): é uma lente nova sobre
// indicadores que já existem, com uma janela de tempo fixa (desde o início do
// Plano Real, 01/07/1994, confirmado com o responsável do projeto em
// 2026-10-26) e marcadores de período de governo (D.GOVERNOS).
//
// Salvaguarda editorial (ver research/notas/VIABILIDADE_DIMENSAO_POLITICA.md,
// seção 5): nenhuma cor, nota ou ordenação por governo — só o dado segmentado
// visualmente, em ordem cronológica. A média por período é informativa, não
// um ranking.
(function () {
  'use strict';
  var P = window.Painel;
  var D = window.DIEESE360.dados;
  var esc = P.esc;

  var JANELA_INICIO = '1994-07-01'; // início do Plano Real — mesma data de GOVERNOS[0].inicio

  // Indicadores com histórico real suficiente para cruzar vários governos
  // (ver levantamento de viabilidade, seção 3.1) — não é a lista inteira do
  // catálogo: os que têm só 1-9 pontos (porque o pipeline recomeçou em
  // 15/10/2026) ou limite genuíno de fonte (ex. Novo CAGED, só desde 2020)
  // ficam de fora até acumularem histórico de verdade.
  var ELEGIVEIS = [
    'ipca', 'inpc',
    'pib_brasil', 'taxa_investimento', 'pim_producao_industrial', 'pmc_volume_vendas', 'pms_volume_servicos',
    'commodities_geral', 'commodities_agropecuaria', 'commodities_metal', 'commodities_energia',
    'cambio_dolar', 'selic', 'igpm', 'nfsp_setor_publico_consolidado',
    'juros_pf_cheque_especial', 'juros_pf_credito_pessoal', 'juros_pj_cartao_rotativo', 'juros_pj_veiculos',
    'saldo_credito_sfn_total', 'saldo_credito_sfn_pf', 'saldo_credito_sfn_pj',
    'saldo_credito_sfn_recursos_livres', 'saldo_credito_sfn_recursos_direcionados', 'saldo_credito_sfn_livres_pf',
    'endividamento_familias_acumulado_12m', 'endividamento_familias_sem_imovel',
    'comprometimento_renda_com_ajuste', 'comprometimento_renda_sem_ajuste', 'comprometimento_renda_sem_imovel',
    'taxa_desocupacao', 'populacao_ocupada', 'rendimento_medio_real', 'taxa_participacao'
  ];

  function montarSeletor(indicadores) {
    var seletor = document.getElementById('politica-seletor');
    var porDimensao = {};
    indicadores.forEach(function (ind) {
      var chave = D.dimensaoEfetiva(ind.dimensao);
      (porDimensao[chave] = porDimensao[chave] || []).push(ind);
    });
    var html = '';
    Object.keys(porDimensao).forEach(function (dim) {
      var rotuloDim = (D.DIMENSOES[dim] || {}).nome || dim;
      html += '<optgroup label="' + esc(rotuloDim) + '">';
      porDimensao[dim].forEach(function (ind) {
        html += '<option value="' + esc(ind.id) + '">' + esc(ind.nome) + '</option>';
      });
      html += '</optgroup>';
    });
    seletor.innerHTML = html;
  }

  function mediaPorGoverno(serieAsc) {
    return D.GOVERNOS.map(function (g) {
      var fimComparar = g.fim || '9999-12-31';
      var pontos = serieAsc.filter(function (p) { return p.data_referencia >= g.inicio && p.data_referencia < fimComparar; });
      if (!pontos.length) return null;
      var soma = pontos.reduce(function (s, p) { return s + p.valor; }, 0);
      return { nome: g.nome, media: soma / pontos.length, pontos: pontos.length };
    }).filter(Boolean);
  }

  function montarResumoGovernos(indicador, medias) {
    if (!medias.length) return '';
    return (
      '<div class="politica-resumo">' +
      '<h3>Média por período de governo</h3>' +
      '<div class="politica-resumo-grade">' +
      medias.map(function (m) {
        return '<div class="politica-resumo-item">' +
          '<span class="politica-resumo-governo">' + esc(m.nome) + '</span>' +
          '<strong class="politica-resumo-valor">' + esc(D.formatarValor(indicador, m.media)) + '</strong>' +
          '<span class="politica-resumo-n">' + m.pontos + ' ponto' + (m.pontos === 1 ? '' : 's') + '</span>' +
          '</div>';
      }).join('') +
      '</div>' +
      '<p class="politica-resumo-nota">Média simples dos pontos publicados em cada período — não corrige sazonalidade nem isola o efeito de uma política específica. Ver aviso metodológico no topo da página.</p>' +
      '</div>'
    );
  }

  function carregarEDesenhar(indicador) {
    var corpo = document.getElementById('politica-corpo');
    corpo.innerHTML = '<p class="aviso demo">Carregando série completa…</p>';
    D.carregarSerie(indicador.id, 100000).then(function (serieCompleta) {
      var serieAsc = serieCompleta.filter(function (p) { return p.data_referencia >= JANELA_INICIO; });
      if (serieAsc.length < 2) {
        corpo.innerHTML = '<p class="aviso demo">Ainda não há pontos suficientes para este indicador desde ' + JANELA_INICIO.split('-').reverse().join('/') + '.</p>';
        return;
      }
      corpo.innerHTML =
        '<div class="politica-cabecalho-indicador"><h2>' + esc(indicador.nome) + '</h2>' +
        '<p>' + esc(indicador.unidade) + ' · ' + esc(indicador.fonte) + '</p>' +
        (indicador.metodologia_md ? '<p class="politica-cabecalho-metodologia">' + esc(indicador.metodologia_md) + '</p>' : '') +
        '</div>' +
        '<div class="grafico-linha-caixa politica-grafico" id="politica-grafico"></div>' +
        montarResumoGovernos(indicador, mediaPorGoverno(serieAsc));
      window.DIEESE360.montarGraficoLinha(document.getElementById('politica-grafico'), serieAsc, {
        formatarValor: function (v) { return D.formatarValor(indicador, v); },
        formatarData: D.formatarDataCurta,
        marcadores: D.GOVERNOS.map(function (g) { return { data: g.inicio, rotulo: g.nome }; })
      });
    }).catch(function (erro) {
      corpo.innerHTML = '<p class="aviso demo">' + esc(P.mensagemErro(erro)) + '</p>';
    });
  }

  function iniciar() {
    D.carregarIndicadores().then(function (indicadores) {
      var porId = {};
      indicadores.forEach(function (i) { porId[i.id] = i; });
      var elegiveisDisponiveis = ELEGIVEIS.map(function (id) { return porId[id]; }).filter(Boolean);
      if (!elegiveisDisponiveis.length) {
        document.getElementById('politica-corpo').innerHTML = '<p class="aviso demo">Nenhum indicador elegível publicado ainda.</p>';
        return;
      }
      montarSeletor(elegiveisDisponiveis);
      var seletor = document.getElementById('politica-seletor');
      seletor.addEventListener('change', function () {
        var ind = porId[seletor.value];
        if (ind) carregarEDesenhar(ind);
      });
      carregarEDesenhar(elegiveisDisponiveis[0]);
    }).catch(function (erro) {
      document.getElementById('politica-corpo').innerHTML = '<p class="aviso demo">' + esc(P.mensagemErro(erro)) + '</p>';
    });
  }

  document.addEventListener('DOMContentLoaded', iniciar);
})();
