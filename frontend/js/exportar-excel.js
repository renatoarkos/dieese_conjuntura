// DIEESE 360 — exporta a série (já filtrada pelo período escolhido na página)
// como .xlsx, usando xlsx-js-style (js/vendor/xlsx-js-style.js) — fork MIT do
// SheetJS com suporte a escrita de estilo de célula. A build "mini" vendorizada
// de painel_saude_mental não escreve estilo (`.s`) no arquivo gerado, só lê —
// testado e confirmado nesta sessão (cor/negrito silenciosamente ignorados).
// Gerado inteiramente no navegador — nenhum dado passa por um servidor.
//
// A pedido explícito do responsável do projeto: a planilha não é só a tabela
// crua — tem título, cores (cabeçalho em navy/branco, igual à marca do
// DIEESE 360), e um bloco de metadados (fonte, unidade, periodicidade,
// período exportado, data de exportação, metodologia completa) ANTES da
// tabela, para quem baixar conseguir interpretar o número fora da
// plataforma sem precisar voltar aqui. O valor em si fica como número puro
// (não como texto "R$ 1.234,56") para poder ser usado em fórmula/gráfico de
// quem baixou — a unidade fica só no bloco de metadados, não em cada célula.
(function () {
  'use strict';

  var AZUL = '030086';
  var BRANCO = 'FFFFFF';
  var CINZA_CLARO = 'F6F7FC';

  function estiloTitulo() {
    return { font: { bold: true, sz: 14, color: { rgb: BRANCO } }, fill: { patternType: 'solid', fgColor: { rgb: AZUL } }, alignment: { vertical: 'center' } };
  }
  function estiloRotuloMeta() {
    return { font: { bold: true, sz: 10 }, alignment: { vertical: 'top' } };
  }
  function estiloValorMeta(quebraLinha) {
    return { font: { sz: 10 }, alignment: { vertical: 'top', wrapText: !!quebraLinha } };
  }
  function estiloCabecalhoTabela() {
    return { font: { bold: true, sz: 10, color: { rgb: BRANCO } }, fill: { patternType: 'solid', fgColor: { rgb: AZUL } }, alignment: { vertical: 'center' } };
  }
  function estiloLinhaTabela(paridade) {
    return { font: { sz: 10 }, fill: { patternType: 'solid', fgColor: { rgb: paridade === 0 ? BRANCO : CINZA_CLARO } } };
  }

  function definirCelula(planilha, endereco, valor, estilo, numFmt) {
    var celula = { v: valor, t: typeof valor === 'number' ? 'n' : 's' };
    if (estilo) celula.s = estilo;
    if (numFmt) celula.z = numFmt;
    planilha[endereco] = celula;
  }

  function montarBlocoMetadados(planilha, indicador, periodoRotulo, nPontos) {
    var merges = [];
    definirCelula(planilha, 'A1', 'DIEESE 360 — ' + indicador.nome, estiloTitulo());
    merges.push({ s: { r: 0, c: 0 }, e: { r: 0, c: 1 } });

    var linhasMeta = [
      ['Fonte', indicador.fonte],
      ['Unidade', indicador.unidade],
      ['Periodicidade', indicador.periodicidade],
      ['Classificação de automação', indicador.classificacao],
      ['Período exportado', periodoRotulo + ' (' + nPontos + ' pontos)'],
      ['Exportado em', new Date().toLocaleString('pt-BR')]
    ];
    var linha = 2; // zero-indexed: linha 3 da planilha (A1/A2 já usados pelo título)
    linhasMeta.forEach(function (par) {
      definirCelula(planilha, 'A' + (linha + 1), par[0], estiloRotuloMeta());
      definirCelula(planilha, 'B' + (linha + 1), par[1] == null ? '' : String(par[1]), estiloValorMeta());
      linha++;
    });

    linha++; // linha em branco
    definirCelula(planilha, 'A' + (linha + 1), 'Metodologia', estiloRotuloMeta());
    merges.push({ s: { r: linha, c: 0 }, e: { r: linha, c: 1 } });
    linha++;
    definirCelula(planilha, 'A' + (linha + 1), indicador.metodologia_md || 'Sem metodologia registrada.', estiloValorMeta(true));
    merges.push({ s: { r: linha, c: 0 }, e: { r: linha, c: 1 } });
    planilha['!rows'] = planilha['!rows'] || [];
    planilha['!rows'][linha] = { hpt: 60 };
    linha++;

    linha++; // linha em branco antes da tabela
    return { proximaLinha: linha, merges: merges };
  }

  function montarTabela(planilha, linhaInicial, indicador, serieAsc) {
    definirCelula(planilha, 'A' + (linhaInicial + 1), 'Data de referência', estiloCabecalhoTabela());
    definirCelula(planilha, 'B' + (linhaInicial + 1), 'Valor (' + indicador.unidade + ')', estiloCabecalhoTabela());
    var linhasOrdenadas = serieAsc.slice().reverse(); // mais recente primeiro, como na vista de tabela da página
    linhasOrdenadas.forEach(function (p, i) {
      var linha = linhaInicial + 1 + i + 1;
      var estilo = estiloLinhaTabela(i % 2);
      definirCelula(planilha, 'A' + linha, p.data_referencia, estilo);
      definirCelula(planilha, 'B' + linha, p.valor, estilo, '0.00');
    });
    return linhaInicial + 1 + linhasOrdenadas.length;
  }

  function exportarSerieExcel(indicador, serieAsc, periodoRotulo) {
    if (!window.XLSX) {
      window.Painel.aviso('Não foi possível carregar o gerador de planilhas.', 'erro');
      return;
    }
    var planilha = {};
    var bloco = montarBlocoMetadados(planilha, indicador, periodoRotulo || 'Série completa', serieAsc.length);
    var ultimaLinha = montarTabela(planilha, bloco.proximaLinha, indicador, serieAsc);

    planilha['!ref'] = 'A1:B' + ultimaLinha;
    planilha['!cols'] = [{ wch: 26 }, { wch: 46 }];
    planilha['!merges'] = bloco.merges;

    var livro = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(livro, planilha, 'DIEESE 360');
    var nomeArquivo = 'dieese360_' + indicador.id + '_' + new Date().toISOString().slice(0, 10) + '.xlsx';
    XLSX.writeFile(livro, nomeArquivo, { cellStyles: true });
  }

  window.DIEESE360 = window.DIEESE360 || {};
  window.DIEESE360.exportarSerieExcel = exportarSerieExcel;
})();
