/**
 * build_mapperapport.js
 *
 * Byggjer forsida + endringslogg for den samla mapperapporten.
 * Resultatet (mapperapport_forside.docx) vert etterpå slått saman med
 * semesterrapport.pdf til mapperapport_samlet.pdf.
 */
const fs = require('fs');
const path = require('path');
const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
  Header, Footer, AlignmentType, LevelFormat, HeadingLevel,
  BorderStyle, WidthType, ShadingType, PageNumber, PageBreak,
  ExternalHyperlink,
} = require('docx');

const OUT = path.join(__dirname, 'mapperapport_forside.docx');
const ACCENT = '2E75B6';
const DARK   = '1F2937';
const BORDER = { style: BorderStyle.SINGLE, size: 4, color: 'BBBBBB' };
const BORDERS = { top: BORDER, bottom: BORDER, left: BORDER, right: BORDER };

const p = (text, opts = {}) => new Paragraph({
  spacing: { before: 60, after: 120, line: 300 },
  alignment: AlignmentType.JUSTIFIED,
  ...opts,
  children: Array.isArray(text) ? text : [new TextRun({ text })],
});

const h1 = (text) => new Paragraph({
  heading: HeadingLevel.HEADING_1,
  spacing: { before: 360, after: 180 },
  children: [new TextRun({ text, bold: true, size: 32, color: DARK })],
});
const h2 = (text) => new Paragraph({
  heading: HeadingLevel.HEADING_2,
  spacing: { before: 240, after: 120 },
  children: [new TextRun({ text, bold: true, size: 26, color: DARK })],
});
const h3 = (text) => new Paragraph({
  heading: HeadingLevel.HEADING_3,
  spacing: { before: 180, after: 80 },
  children: [new TextRun({ text, bold: true, size: 22, color: ACCENT })],
});
const bullet = (text) => new Paragraph({
  numbering: { reference: 'bullets', level: 0 },
  spacing: { after: 80 },
  children: [new TextRun({ text })],
});

const cell = (text, opts = {}) => new TableCell({
  borders: BORDERS,
  width: { size: opts.width || 4680, type: WidthType.DXA },
  shading: opts.header
    ? { fill: ACCENT, type: ShadingType.CLEAR, color: 'auto' }
    : undefined,
  margins: { top: 80, bottom: 80, left: 120, right: 120 },
  children: [new Paragraph({
    children: [new TextRun({
      text, bold: opts.header || false,
      color: opts.header ? 'FFFFFF' : undefined,
      size: 20,
    })],
  })],
});
const makeTable = (header, rows, colWidths) => {
  const totalW = colWidths.reduce((a,b)=>a+b,0);
  return new Table({
    width: { size: totalW, type: WidthType.DXA },
    columnWidths: colWidths,
    rows: [
      new TableRow({ tableHeader: true,
        children: header.map((h,i) => cell(h, { header: true, width: colWidths[i] })) }),
      ...rows.map(r => new TableRow({
        children: r.map((c,i) => cell(String(c), { width: colWidths[i] })) })),
    ],
  });
};

const CH = [];

// ─── FORSIDE ────────────────────────────────────────────────────────────
CH.push(new Paragraph({ alignment: AlignmentType.CENTER,
  spacing: { before: 1600, after: 240 },
  children: [new TextRun({
    text: 'Mapperapport IS-218',
    bold: true, size: 56, color: DARK,
  })] }));
CH.push(new Paragraph({ alignment: AlignmentType.CENTER,
  spacing: { after: 600 },
  children: [new TextRun({
    text: 'Geografiske informasjonssystem · Vår 2026',
    size: 28, color: ACCENT,
  })] }));
CH.push(new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 80 },
  children: [new TextRun({ text: 'Gruppe 8', bold: true, size: 26 })] }));
CH.push(new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 80 },
  children: [new TextRun({
    text: 'Kristian Espevik · Victor · Nicolai · Brage · Amged · Youcef',
    size: 22,
  })] }));
CH.push(new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 80 },
  children: [new TextRun({ text: 'Universitetet i Agder', size: 22 })] }));
CH.push(new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 1200 },
  children: [new TextRun({ text: 'Innleveringsfrist: 5. mai 2026', size: 22, italics: true })] }));

CH.push(new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 240 },
  border: {
    top:    { style: BorderStyle.SINGLE, size: 6, color: ACCENT, space: 10 },
    bottom: { style: BorderStyle.SINGLE, size: 6, color: ACCENT, space: 10 },
  },
  children: [new TextRun({ text: 'Tema: Totalforsvaret 2025–2026',
    bold: true, size: 24, color: ACCENT })] }));

CH.push(new Paragraph({ children: [new PageBreak()] }));

// ─── INNHALD ────────────────────────────────────────────────────────────
CH.push(h1('Innhald'));
CH.push(p('Denne samla mapperapporten inneheld alle fire innleveringar i IS-218, Vår 2026:'));
CH.push(makeTable(
  ['#', 'Innlevering', 'Tema', 'Dokument'],
  [
    ['1', 'Oppgåve 1', 'Webutvikling / GIS / kartografi',         'README + kildekode i repoet'],
    ['2', 'Oppgåve 2', 'GIScience / KI · Jupyter-notebook',        'analyse_beredskap.ipynb'],
    ['3', 'Oppgåve 3', 'Prosjektskisse',                           'prosjektskisse.md'],
    ['4', 'Oppgåve 4', 'Semesterprosjekt — Dekningsgap-analyse',    'semesterrapport.pdf (vedlagt)'],
  ],
  [700, 1700, 3700, 3260],
));
CH.push(p('Repo: ' , { }));
CH.push(p([
  new ExternalHyperlink({
    link: 'https://github.com/KristianEspevikUIA/IS218GR8',
    children: [new TextRun({
      text: 'https://github.com/KristianEspevikUIA/IS218GR8',
      style: 'Hyperlink',
    })],
  }),
]));

CH.push(new Paragraph({ children: [new PageBreak()] }));

// ─── ENDRINGSLOGG ───────────────────────────────────────────────────────
CH.push(h1('Endringslogg per innlevering'));
CH.push(p(
  'Alle endringar som er gjort etter innlevering av kvar delinnlevering. ' +
  'Oppgåvene vart levert løpande gjennom semesteret; her listar vi kva som ' +
  'er oppdatert eller utvida før samla innlevering.'
));

CH.push(h2('Oppgåve 1 — Webkart for beredskapsressursar'));
CH.push(h3('Opphavleg innlevering'));
CH.push(p(
  'Flask-basert webkart med Leaflet-frontend og MVC-arkitektur. ' +
  'Inkluderte AED-ar frå Hjertestarterregisteret (OAuth 2.0 API), brannstasjonar ' +
  'frå GeoNorge WFS 2.0, lokale beredskapsressursar som GeoJSON og Supabase-' +
  'baserte stader. Rutenavigering via OSRM gangveg, popup-interaksjon og ' +
  'radiussøk.'
));
CH.push(h3('Endringar etter opphavleg innlevering'));
CH.push(bullet('Utvida Flask-backend med sju nye coverage-endepunkt (/api/coverage/*).'));
CH.push(bullet('Lagt til dynamisk Leaflet-frontend med fire nye kartlag (risk-grid, gaps, service-areas, recommendations).'));
CH.push(bullet('Lagt til sidepanel "📊 Dekningsgap-analyse (Oppg. 4)" med live-oppdatert statistikk frå /api/coverage/summary.'));
CH.push(bullet('Ny styling for risikokoroplett og numererte anbefalingsmarkørar.'));
CH.push(bullet('Separert analyse-modul (`app/models/coverage_model.py`) for gjenbruk i notebook og Flask.'));
CH.push(bullet('Lagt til caching av AED- og brannstasjon-data (`aeds_cache.geojson`, `brannstasjoner_cache.geojson`) for offline demonstrasjon.'));

CH.push(h2('Oppgåve 2 — GIScience / Jupyter-notebook'));
CH.push(h3('Opphavleg innlevering'));
CH.push(p(
  'Notebook `analyse_beredskap.ipynb` med romleg analyse (nærmaste-AED, ' +
  'tetthetskart med kernel density estimation, Folium-visualisering, ' +
  'PostGIS-spørjingar mot Supabase). Kombinerte data frå fleire kjelder og ' +
  'viste interaktive kart og tabellar.'
));
CH.push(h3('Endringar etter opphavleg innlevering'));
CH.push(bullet('Produsert ein ny, fullstendig notebook `dekningsgap_analyse.ipynb` (semesterprosjekt).'));
CH.push(bullet('Notebooken er automatisk generert av `build_notebook.py` og køyrt til full fullføring — alle 17 kodeceller produserer output.'));
CH.push(bullet('Innfører DuckDB SQL-analyse som eit nytt SQL-verktøy i tillegg til PostGIS og geopandas.'));
CH.push(bullet('Vektoranalyse (buffer, overlay-difference, spatial join, aggregering) er no demonstrert i full pipeline.'));
CH.push(bullet('Koplar notebook direkte til webløysinga: eksporterte GeoJSON frå notebook kan serverast av Flask utan endring.'));

CH.push(h2('Oppgåve 3 — Prosjektskisse'));
CH.push(h3('Opphavleg innlevering'));
CH.push(p(
  'Kort prosjektskisse (`prosjektskisse.md`) med problemstilling, datasett, ' +
  'teknologi og forventa resultat for semesterprosjektet. Hovudfokus på ' +
  'å identifisere sårbare område i beredskapsdekning i eit totalforsvars' +
  '-scenario.'
));
CH.push(h3('Endringar etter opphavleg innlevering'));
CH.push(bullet('Ingen strukturelle endringar — problemstillinga er halden konsistent gjennom heile prosjektet.'));
CH.push(bullet('Problemstillinga vidareført ordrett i semesterrapporten (seksjon 1.2) og i notebooken (seksjon "Problemstilling").'));
CH.push(bullet('Datasettval og teknologistabel frå skissa følgjer prosjektet 1:1, med ein justering: SSB sitt offisielle 250m rutenett er erstatta av ein kalibrert syntetisk modell for reproduserbarheit i sandboxa (begrunna i semesterrapport seksjon 2.3 og 6.2).'));

CH.push(h2('Oppgåve 4 — Semesterprosjekt'));
CH.push(h3('Kort oppsummering'));
CH.push(p(
  'Ny innlevering: dekningsgap-analyse for beredskap i Kristiansand, ' +
  'fullstendig dokumentert i `semesterrapport.pdf` (vedlagt som del 2 av denne mapperapporten). ' +
  'Leveransen består av:'
));
CH.push(bullet('`dekningsgap_analyse.ipynb` — Jupyter-notebook med full analyse og visualisering (32 celler, 17 kodeceller køyrd ende-til-ende).'));
CH.push(bullet('`app/models/coverage_model.py` — modulær analyse-pipeline gjenbrukt i både notebook og Flask.'));
CH.push(bullet('`app/__init__.py` — sju nye REST-endepunkt som serverer coverage-lag.'));
CH.push(bullet('`templates/index.html` — utvida frontend med fire nye kartlag og sidepanel.'));
CH.push(bullet('`static/figures/` — sju PNG-figurar brukt i rapporten.'));
CH.push(bullet('`semesterrapport.pdf` — 12-sides rapport med metodikk, figurar, resultat, diskusjon, kjelder.'));

// ─── VEILEDNING TIL SENSOR ──────────────────────────────────────────────
CH.push(new Paragraph({ children: [new PageBreak()] }));
CH.push(h1('Veiledning til sensor'));
CH.push(h2('Korleis køyre løysinga'));
CH.push(p([new TextRun({ text: '1. Klon repoet og installer avhengigheiter:', bold: true })]));
CH.push(p([new TextRun({
  text: 'git clone https://github.com/KristianEspevikUIA/IS218GR8.git\n' +
        'cd IS218GR8 && pip install -r requirements.txt',
  font: 'Consolas', size: 20,
})]));
CH.push(p([new TextRun({ text: '2. Bygg coverage-lag (éin gong):', bold: true })]));
CH.push(p([new TextRun({
  text: 'python generate_population_grid.py\n' +
        'python run_coverage_analysis.py',
  font: 'Consolas', size: 20,
})]));
CH.push(p([new TextRun({ text: '3. Start Flask-serveren:', bold: true })]));
CH.push(p([new TextRun({
  text: 'python run.py  →  http://localhost:3000',
  font: 'Consolas', size: 20,
})]));
CH.push(p([new TextRun({ text: '4. Køyr notebook:', bold: true })]));
CH.push(p([new TextRun({
  text: 'jupyter notebook dekningsgap_analyse.ipynb',
  font: 'Consolas', size: 20,
})]));

CH.push(h2('Kor finn eg kva?'));
CH.push(makeTable(
  ['Område', 'Fil / mappe', 'Vurderingskriterium'],
  [
    ['Webkart (Leaflet)',        'templates/index.html',                'Oppg. 1 — kartografi, interaksjon'],
    ['Flask MVC',                'app/__init__.py, app/models/, app/controllers/', 'Oppg. 1 — arkitektur'],
    ['OGC-integrering',          'app/models/data_model.py (WFS)',      'Oppg. 1 — OGC-krav'],
    ['PostGIS-spørjingar',       'app/models/data_model.py (ST_DWithin)', 'Oppg. 1 + 4 — spatial DB'],
    ['Notebook (GIScience)',     'analyse_beredskap.ipynb + dekningsgap_analyse.ipynb', 'Oppg. 2 + 4'],
    ['Vektoranalyse-kjerne',     'app/models/coverage_model.py',        'Oppg. 4 — buffer/overlay/aggregering'],
    ['Greedy-algoritme',         'coverage_model.recommend_aed_sites()', 'Oppg. 4 — algoritme'],
    ['Dekningsgap (avleidd)',    'app/data/coverage/coverage_gaps.geojson', 'Oppg. 4 — avleidd datasett'],
    ['Risiko-koroplett',         'app/data/coverage/risk_grid.geojson', 'Oppg. 4 — aggregering + kartografi'],
    ['Semesterrapport',          'semesterrapport.pdf',                 'Oppg. 4 — skriftleg'],
    ['Endringslogg',             'denne fila (del 1)',                  'Samla mapperapport'],
    ['Prosjektskisse',           'prosjektskisse.md',                   'Oppg. 3'],
  ],
  [2400, 3300, 3660],
));

CH.push(h2('Direkte lenker til API-endepunkt (når serveren køyrer)'));
CH.push(bullet('GET  /api/map/layers  — alle kartlag (oppg. 1)'));
CH.push(bullet('POST /api/postgis/nearby-aeds  — PostGIS-romleg søk (oppg. 1)'));
CH.push(bullet('GET  /api/coverage/summary  — statistikk for dekningsgap (oppg. 4)'));
CH.push(bullet('GET  /api/coverage/risk-grid  — 250m risiko-koroplett (oppg. 4)'));
CH.push(bullet('GET  /api/coverage/recommendations  — 10 anbefalte AED-plasseringar (oppg. 4)'));
CH.push(bullet('GET  /api/coverage/gaps  — dekningsgap-polygon (avleidd datasett, oppg. 4)'));

// ─── BUILD ──────────────────────────────────────────────────────────────
const doc = new Document({
  creator: 'Gruppe 8 (IS-218)',
  title: 'IS-218 Mapperapport Vår 2026 — Gruppe 8',
  description: 'Samla mapperapport med endringslogg',
  styles: {
    default: { document: { run: { font: 'Calibri', size: 22 } } },
    paragraphStyles: [
      { id: 'Heading1', name: 'Heading 1', basedOn: 'Normal', next: 'Normal', quickFormat: true,
        run: { size: 32, bold: true, font: 'Calibri', color: DARK },
        paragraph: { spacing: { before: 360, after: 180 }, outlineLevel: 0 } },
      { id: 'Heading2', name: 'Heading 2', basedOn: 'Normal', next: 'Normal', quickFormat: true,
        run: { size: 26, bold: true, font: 'Calibri', color: DARK },
        paragraph: { spacing: { before: 240, after: 120 }, outlineLevel: 1 } },
      { id: 'Heading3', name: 'Heading 3', basedOn: 'Normal', next: 'Normal', quickFormat: true,
        run: { size: 22, bold: true, font: 'Calibri', color: ACCENT },
        paragraph: { spacing: { before: 180, after: 80 }, outlineLevel: 2 } },
    ],
  },
  numbering: {
    config: [
      { reference: 'bullets',
        levels: [{ level: 0, format: LevelFormat.BULLET, text: '•',
          alignment: AlignmentType.LEFT,
          style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] },
      { reference: 'numbers',
        levels: [{ level: 0, format: LevelFormat.DECIMAL, text: '%1.',
          alignment: AlignmentType.LEFT,
          style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] },
    ],
  },
  sections: [{
    properties: { page: { size: { width: 11906, height: 16838 },
      margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 } } },
    headers: { default: new Header({ children: [new Paragraph({
      alignment: AlignmentType.RIGHT,
      children: [new TextRun({
        text: 'IS-218 · Mapperapport · Gruppe 8',
        size: 18, color: '7F7F7F', italics: true,
      })],
    })] }) },
    footers: { default: new Footer({ children: [new Paragraph({
      alignment: AlignmentType.CENTER,
      children: [
        new TextRun({ text: 'Del 1 · Side ', size: 18, color: '7F7F7F' }),
        new TextRun({ children: [PageNumber.CURRENT], size: 18, color: '7F7F7F' }),
      ],
    })] }) },
    children: CH,
  }],
});

Packer.toBuffer(doc).then(buf => {
  fs.writeFileSync(OUT, buf);
  console.log('✓ Skreiv', OUT, `(${buf.length} bytes)`);
});
