// DIEESE 360 — mapa coroplético por UF, para indicadores regionalizados (hoje:
// limite fiscal de pessoal). Usa a malha oficial do IBGE, vendorizada em
// frontend/assets/mapas/malha_uf.geojson (baixada de
// https://servicodados.ibge.gov.br/api/v3/malhas/paises/BR?formato=application/vnd.geo+json&qualidade=minima&intrarregiao=UF
// — API de malhas territoriais do próprio IBGE, não um serviço de terceiros).
// Vendorizado em vez de buscado ao vivo a cada carga de página: o arquivo é
// pequeno (~98 KB) e a malha das UFs não muda com frequência.
//
// Projeção: equirretangular simples (sem dependência externa) — adequada aqui
// porque o Brasil fica longe dos polos, a distorção nessa escala é pequena, e
// este mapa não precisa de pan/zoom, só do desenho estático + hover. Cor:
// rampa sequencial de um hue só (azul de marca), clara->escura — ver skill de
// dataviz (references/choosing-a-form.md: "heatmap/choropleth -> sequencial").
(function () {
  'use strict';
  var esc = (window.Painel && window.Painel.esc) || function (s) { return s; };

  // sigla -> código de área do IBGE (mesma tabela usada em
  // pipelines/ingestao/bloco_1_macroeconomia/coleta_limite_fiscal_siconfi.py)
  var CODIGO_UF = {
    RO: '11', AC: '12', AM: '13', RR: '14', PA: '15', AP: '16', TO: '17',
    MA: '21', PI: '22', CE: '23', RN: '24', PB: '25', PE: '26', AL: '27', SE: '28', BA: '29',
    MG: '31', ES: '32', RJ: '33', SP: '35',
    PR: '41', SC: '42', RS: '43',
    MS: '50', MT: '51', GO: '52', DF: '53'
  };
  var NOME_UF = {
    RO: 'Rondônia', AC: 'Acre', AM: 'Amazonas', RR: 'Roraima', PA: 'Pará', AP: 'Amapá', TO: 'Tocantins',
    MA: 'Maranhão', PI: 'Piauí', CE: 'Ceará', RN: 'Rio Grande do Norte', PB: 'Paraíba', PE: 'Pernambuco',
    AL: 'Alagoas', SE: 'Sergipe', BA: 'Bahia', MG: 'Minas Gerais', ES: 'Espírito Santo', RJ: 'Rio de Janeiro',
    SP: 'São Paulo', PR: 'Paraná', SC: 'Santa Catarina', RS: 'Rio Grande do Sul', MS: 'Mato Grosso do Sul',
    MT: 'Mato Grosso', GO: 'Goiás', DF: 'Distrito Federal'
  };
  var CODAREA_PARA_SIGLA = {};
  Object.keys(CODIGO_UF).forEach(function (sigla) { CODAREA_PARA_SIGLA[CODIGO_UF[sigla]] = sigla; });

  // Rampa sequencial — mesmos tokens de marca do CSS (--seq-100..--seq-900),
  // repetidos aqui como hex porque path.setAttribute('fill', ...) precisa de
  // um valor resolvido, não de uma var() condicionada ao elemento.
  var RAMPA = [
    { parada: 0, cor: [238, 240, 251] },   // --seq-100 / --azul-50
    { parada: 0.35, cor: [223, 227, 247] },// --seq-300 / --azul-100
    { parada: 0.65, cor: [141, 147, 214] },// --seq-500 / --azul-300
    { parada: 0.85, cor: [10, 10, 168] },  // --seq-700 / --azul-hover
    { parada: 1, cor: [3, 0, 134] }        // --seq-900 / --azul
  ];

  function corSequencial(t) {
    t = Math.max(0, Math.min(1, t));
    for (var i = 0; i < RAMPA.length - 1; i++) {
      var a = RAMPA[i], b = RAMPA[i + 1];
      if (t >= a.parada && t <= b.parada) {
        var local = (t - a.parada) / (b.parada - a.parada || 1);
        var rgb = a.cor.map(function (v, idx) { return Math.round(v + (b.cor[idx] - v) * local); });
        return 'rgb(' + rgb.join(',') + ')';
      }
    }
    return 'rgb(' + RAMPA[RAMPA.length - 1].cor.join(',') + ')';
  }

  // ------------------------------------------------------------------
  // Projeção equirretangular a partir do bbox real da malha (não um bbox
  // "do Brasil" de tabela — calculado direto das coordenadas do GeoJSON).
  // ------------------------------------------------------------------
  function calcularBbox(geojson) {
    var minLon = Infinity, maxLon = -Infinity, minLat = Infinity, maxLat = -Infinity;
    function varrer(coords, prof) {
      if (prof === 0) {
        var lon = coords[0], lat = coords[1];
        if (lon < minLon) minLon = lon; if (lon > maxLon) maxLon = lon;
        if (lat < minLat) minLat = lat; if (lat > maxLat) maxLat = lat;
        return;
      }
      coords.forEach(function (c) { varrer(c, prof - 1); });
    }
    geojson.features.forEach(function (f) {
      var prof = f.geometry.type === 'Polygon' ? 2 : 3; // Polygon=[anel][ponto], MultiPolygon=[poligono][anel][ponto]
      varrer(f.geometry.coordinates, prof);
    });
    return { minLon: minLon, maxLon: maxLon, minLat: minLat, maxLat: maxLat };
  }

  function montarProjecao(bbox, largura, altura, margem) {
    var w = largura - margem * 2, h = altura - margem * 2;
    var escalaX = w / (bbox.maxLon - bbox.minLon);
    var escalaY = h / (bbox.maxLat - bbox.minLat);
    var escala = Math.min(escalaX, escalaY);
    var deslocX = margem + (w - (bbox.maxLon - bbox.minLon) * escala) / 2;
    var deslocY = margem + (h - (bbox.maxLat - bbox.minLat) * escala) / 2;
    return function (lon, lat) {
      var x = deslocX + (lon - bbox.minLon) * escala;
      var y = deslocY + (bbox.maxLat - lat) * escala; // y cresce para baixo no SVG, latitude cresce para cima
      return [x, y];
    };
  }

  function anelParaPath(anel, projetar) {
    return anel.map(function (ponto, i) {
      var xy = projetar(ponto[0], ponto[1]);
      return (i === 0 ? 'M' : 'L') + xy[0].toFixed(1) + ',' + xy[1].toFixed(1);
    }).join(' ') + ' Z';
  }

  function geometriaParaPath(geometria, projetar) {
    if (geometria.type === 'Polygon') {
      return geometria.coordinates.map(function (anel) { return anelParaPath(anel, projetar); }).join(' ');
    }
    if (geometria.type === 'MultiPolygon') {
      return geometria.coordinates.map(function (poligono) {
        return poligono.map(function (anel) { return anelParaPath(anel, projetar); }).join(' ');
      }).join(' ');
    }
    return '';
  }

  // ------------------------------------------------------------------
  // Tooltip (uma instância compartilhada, reposicionada a cada hover)
  // ------------------------------------------------------------------
  function obterTooltip() {
    var el = document.getElementById('mapa-tooltip');
    if (!el) {
      el = document.createElement('div');
      el.id = 'mapa-tooltip';
      el.className = 'mapa-tooltip';
      el.setAttribute('role', 'status');
      document.body.appendChild(el);
    }
    return el;
  }

  function mostrarTooltip(evento, sigla, valor, unidade, formatarValor) {
    var el = obterTooltip();
    el.innerHTML = '';
    var nome = document.createElement('strong');
    nome.textContent = (NOME_UF[sigla] || sigla) + ' (' + sigla + ')';
    var valorEl = document.createElement('span');
    valorEl.className = 'valor';
    valorEl.textContent = valor == null ? 'sem dado' : formatarValor(valor);
    el.appendChild(nome);
    el.appendChild(valorEl);
    el.style.left = evento.clientX + 'px';
    el.style.top = evento.clientY + 'px';
    el.classList.add('visivel');
  }

  function esconderTooltip() {
    var el = document.getElementById('mapa-tooltip');
    if (el) el.classList.remove('visivel');
  }

  // ------------------------------------------------------------------
  // Monta o mapa dentro de `container` (um elemento vazio) a partir de
  // `porUf` ({SIGLA: valor}) e devolve nada — efeito colateral no DOM.
  // `opcoes.formatarValor(valor)` formata o número do tooltip/legenda.
  // ------------------------------------------------------------------
  function montarMapaUF(container, porUf, opcoes) {
    opcoes = opcoes || {};
    var formatarValor = opcoes.formatarValor || function (v) { return String(v); };

    fetch('assets/mapas/malha_uf.geojson')
      .then(function (r) { return r.json(); })
      .then(function (geojson) {
        var LARGURA = 520, ALTURA = 480, MARGEM = 8;
        var bbox = calcularBbox(geojson);
        var projetar = montarProjecao(bbox, LARGURA, ALTURA, MARGEM);

        var valores = Object.keys(porUf).map(function (k) { return porUf[k]; });
        var min = Math.min.apply(null, valores), max = Math.max.apply(null, valores);
        var amplitude = (max - min) || 1;

        var svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
        svg.setAttribute('viewBox', '0 0 ' + LARGURA + ' ' + ALTURA);
        svg.setAttribute('class', 'mapa-uf');
        svg.setAttribute('role', 'img');
        svg.setAttribute('aria-label', 'Mapa do Brasil por Unidade da Federação');

        geojson.features.forEach(function (f) {
          var sigla = CODAREA_PARA_SIGLA[f.properties.codarea];
          var valor = sigla ? porUf[sigla] : null;
          var d = geometriaParaPath(f.geometry, projetar);
          var path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
          path.setAttribute('d', d);
          path.setAttribute('class', 'uf');
          path.setAttribute('fill', valor == null ? '#eceef5' : corSequencial((valor - min) / amplitude));
          path.setAttribute('tabindex', '0');
          path.setAttribute('aria-label', (NOME_UF[sigla] || sigla) + (valor == null ? ', sem dado' : ', ' + formatarValor(valor)));

          path.addEventListener('pointermove', function (e) { mostrarTooltip(e, sigla, valor, null, formatarValor); });
          path.addEventListener('pointerenter', function () { path.classList.add('realce'); });
          path.addEventListener('pointerleave', function () { path.classList.remove('realce'); esconderTooltip(); });
          path.addEventListener('focus', function (e) {
            path.classList.add('realce');
            var r = path.getBoundingClientRect();
            mostrarTooltip({ clientX: r.left + r.width / 2, clientY: r.top }, sigla, valor, null, formatarValor);
          });
          path.addEventListener('blur', function () { path.classList.remove('realce'); esconderTooltip(); });

          svg.appendChild(path);
        });

        container.innerHTML = '';
        container.appendChild(svg);

        if (opcoes.legenda) {
          var legenda = document.createElement('div');
          legenda.className = 'mapa-legenda';
          legenda.innerHTML = '<span>' + esc(formatarValor(min)) + '</span><div class="rampa"></div><span>' + esc(formatarValor(max)) + '</span>';
          container.parentNode.appendChild(legenda);
        }
      })
      .catch(function (erro) {
        container.innerHTML = '<p class="aviso demo">Não foi possível carregar o mapa (' + esc(String(erro && erro.message || erro)) + ').</p>';
      });
  }

  window.DIEESE360 = window.DIEESE360 || {};
  window.DIEESE360.montarMapaUF = montarMapaUF;
})();
