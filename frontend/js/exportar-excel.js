// DIEESE 360 — exporta a série (já filtrada pelo período escolhido) como
// .xlsx, usando a mesma biblioteca já vendorizada em painel_saude_mental
// (SheetJS, js/vendor/xlsx.mini.min.js). Gerado inteiramente no navegador —
// nenhum dado passa por um servidor para virar a planilha.
(function () {
  'use strict';

  function exportarSerieExcel(indicador, serieAsc) {
    if (!window.XLSX) {
      window.Painel.aviso('Não foi possível carregar o gerador de planilhas.', 'erro');
      return;
    }
    var linhas = serieAsc.map(function (p) {
      return {
        Indicador: indicador.nome,
        'Data de referência': p.data_referencia,
        Valor: p.valor,
        Unidade: indicador.unidade,
        Fonte: indicador.fonte
      };
    });
    var planilha = XLSX.utils.json_to_sheet(linhas);
    planilha['!cols'] = [{ wch: 32 }, { wch: 16 }, { wch: 14 }, { wch: 22 }, { wch: 28 }];
    var livro = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(livro, planilha, 'Série histórica');
    var nomeArquivo = 'dieese360_' + indicador.id + '_' + new Date().toISOString().slice(0, 10) + '.xlsx';
    XLSX.writeFile(livro, nomeArquivo);
  }

  window.DIEESE360 = window.DIEESE360 || {};
  window.DIEESE360.exportarSerieExcel = exportarSerieExcel;
})();
