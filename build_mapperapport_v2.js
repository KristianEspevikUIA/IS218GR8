/**
 * build_mapperapport_v2.js
 *
 * Byggjer den OPPDATERTE samla mapperapporten i tråd med presiseringa frå
 * faglærar (Frank Hovet) etter Oppgåve 2/3-retting:
 *
 *   "Mappen skal bestå av:
 *    - Samlet rapport for mappeinnleveringen (~2 sider)
 *    - Lag en halv side oppsummering per oppgave
 *    - Sett sammen disse til en PDF-fil
 *
 *    Innleveringen i Inspera består av 2 PDF-filer:
 *    - Samlet rapport for mappeinnlevering (2 sider)
 *    - Rapport for semesterprosjekt (max 10 sider + vedlegg)"
 *
 * Resultatet (mapperapport.docx) skal vere ein KORT, sjølvstendig PDF.
 * Semesterrapporten leverast som EIGEN PDF i Inspera.
 */
const fs = require('fs');
const path = require('path');
const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
  Header, Footer, AlignmentType, LevelFormat, HeadingLevel,
  BorderStyle, WidthType, ShadingType, PageNumber, PageBreak,
  ExternalHyperlink,
} = require('/sessions/optimistic-gallant-faraday/mnt/outputs/node_pkgs/node_modules/docx');

const OUT = path.join(__dirname, 'mapperapport.docx');
const REPO = 'https://github.com/KristianEspevikUIA/IS218GR8';
const ACCENT = '2E75B6';
const DARK   = '1F2937';
const MUTED  = '7F7F7F';

const BORDER  = { style: BorderStyle.SINGLE, size: 4, color: 'BBBBBB' };
const BORDERS = { top: BORDER, bottom: BORDER, left: BORDER, right: BORDER };

// ─── HJELPARAR ───────────────────────────────────────────────────────────
const p = (text, opts = {}) => new Paragraph({
  spacing: { before: 40, after: 80, line: 280 },
  alignment: AlignmentType.JUSTIFIED,
  ...opts,
  children: Array.isArray(text) ? text : [new TextRun({ text })],
});

const h1 = (text) => new Paragraph({
  heading: HeadingLevel.HEADING_1,
  spacing: { before: 240, after: 120 },
  children: [new TextRun({ text, bold: true, size: 30, color: DARK })],
});

const h2 = (text) => new Paragraph({
  heading: HeadingLevel.HEADING_2,
  spacing: { before: 180, after: 60 },
  children: [new TextRun({ text, bold: true, size: 24, color: ACCENT })],
});

const h3 = (text) => new Paragraph({
  heading: HeadingLevel.HEADING_3,
  spacing: { before: 100, after: 40 },
  children: [new TextRun({ text, bold: true, size: 20, color: DARK })],
});

const bullet = (text) => new Paragraph({
  numbering: { reference: 'bullets', level: 0 },
  spacing: { after: 40 },
  children: [new TextRun({ text, size: 20 })],
});

const link = (url, label) => new ExternalHyperlink({
  link: url,
  children: [new TextRun({ text: label || url, style: 'Hyperlink', size: 20 })],
});

const cell = (text, opts = {}) => new TableCell({
  borders: BORDERS,
  width: { size: opts.width, type: WidthType.DXA },
  shading: opts.header
    ? { fill: ACCENT, type: ShadingType.CLEAR, color: 'auto' }
    : undefined,
  margins: { top: 60, bottom: 60, left: 100, right: 100 },
  children: [new Paragraph({
    children: [new TextRun({
      text, bold: !!opts.header,
      color: opts.header ? 'FFFFFF' : undefined,
      size: 18,
    })],
  })],
});

const tbl = (header, rows, widths) => {
  const total = widths.reduce((a, b) => a + b, 0);
  return new Table({
    width: { size: total, type: WidthType.DXA },
    columnWidths: widths,
    rows: [
      new TableRow({
        tableHeader: true,
        children: header.map((h, i) => cell(h, { header: true, width: widths[i] })),
      }),
      ...rows.map(r => new TableRow({
        children: r.map((c, i) => cell(String(c), { width: widths[i] })),
      })),
    ],
  });
};

// ─── INNHALD ─────────────────────────────────────────────────────────────
const CH = [];

// FORSIDE-BLOKK (kompakt — ikkje eigen side)
CH.push(new Paragraph({
  alignment: AlignmentType.CENTER,
  spacing: { before: 0, after: 80 },
  children: [new TextRun({ text: 'Mapperapport IS-218', bold: true, size: 40, color: DARK })],
}));
CH.push(new Paragraph({
  alignment: AlignmentType.CENTER,
  spacing: { after: 60 },
  children: [new TextRun({
    text: 'Geografiske informasjonssystem · Vår 2026 · Tema: Totalforsvaret 2025–2026',
    size: 22, color: ACCENT,
  })],
}));
CH.push(new Paragraph({
  alignment: AlignmentType.CENTER,
  spacing: { after: 40 },
  children: [new TextRun({
    text: 'Gruppe 8 — Kristian Espevik · Victor Ziadpour · Nicolai Stephansen · Brage Kristoffersen · Amged Mohammed · Youcef Youcef',
    size: 18,
  })],
}));
CH.push(new Paragraph({
  alignment: AlignmentType.CENTER,
  spacing: { after: 200 },
  children: [
    new TextRun({ text: 'Repo: ', size: 18 }),
    link(REPO, REPO),
  ],
}));

// INNLEDNING
CH.push(p([new TextRun({
  text: 'Denne samla mapperapporten gjev ein kort oversikt over dei tre delinnleveringane i ' +
        'IS-218 (Oppgåve 1, 2 og 3). For kvar oppgåve oppsummerer vi opphavleg leveranse, ' +
        'eventuelle endringar etter retting i Canvas, og lenke til relevant kjeldekode. ' +
        'Semesterprosjektet (Oppgåve 4) leverast som eigen PDF i tråd med presiseringa frå faglærar.',
  size: 20,
})]));

// ─── OPPGÅVE 1 ───────────────────────────────────────────────────────────
CH.push(h2('Oppgåve 1 — Webutvikling, GIS og kartografi'));
CH.push(p([
  new TextRun({ text: 'Innlevert: ', bold: true, size: 20 }),
  new TextRun({ text: '24. feb. 2026 — godkjent.   ', size: 20 }),
  new TextRun({ text: 'Repo: ', bold: true, size: 20 }),
  link(REPO + '/tree/main', 'IS218GR8/main'),
]));
CH.push(h3('Opphavleg leveranse'));
CH.push(p([new TextRun({
  text: 'Flask-basert webkart med MVC-arkitektur og Leaflet.js-frontend. Visualiserer ' +
        '263 hjertestartarar (Hjertestarterregister-API med OAuth 2.0), brannstasjonar frå ' +
        'GeoNorge OGC WFS 2.0 (GML 3.2 → GeoJSON), 11 lokale beredskapsressursar og stader ' +
        'frå Supabase PostGIS. Interaksjon: popup-attributtar, datadrevet fargekoding ' +
        '(IS_OPEN), togglebare kartlag, OSRM-rutenavigering til nærmaste åpne AED, og ' +
        'PostGIS-romleg søk via ST_DWithin.',
  size: 20,
})]));
CH.push(h3('Endringar etter Canvas-innlevering'));
CH.push(bullet('Lagt til klikkbar "PostGIS-modus" i frontenden — koordinatar sendes til Supabase RPC nearby_hjertestartere() med ST_DWithin, og resultata utheves med kvit kant.'));
CH.push(bullet('Cache av AED- og brannstasjonsdata (aeds_cache.geojson, brannstasjoner_cache.geojson) for offline demonstrasjon og raskare frontend-loading.'));
CH.push(bullet('Sju nye coverage-endepunkt (/api/coverage/*) som koplar oppgåve 1-frontenden til semesterprosjektet sin analyse.'));
CH.push(bullet('Sidepanel "Dekningsgap-analyse" med live statistikk frå /api/coverage/summary.'));

// ─── OPPGÅVE 2 ───────────────────────────────────────────────────────────
CH.push(h2('Oppgåve 2 — GIScience og romleg analyse'));
CH.push(p([
  new TextRun({ text: 'Innlevert: ', bold: true, size: 20 }),
  new TextRun({ text: '10. mars 2026 — godkjent.   ', size: 20 }),
  new TextRun({ text: 'Notebook: ', bold: true, size: 20 }),
  link(REPO + '/blob/main/analyse_beredskap.ipynb', 'analyse_beredskap.ipynb'),
]));
CH.push(h3('Opphavleg leveranse'));
CH.push(p([new TextRun({
  text: 'Notebook med tre datasett (lokal GeoJSON, Hjertestarterregister-API, GeoNorge WFS), ' +
        'attributt- og romleg filtrering (sjoin), Folium-visualisering, DuckDB SQL-aggregering, ' +
        'vektoranalyse (500 m buffer, overlay intersection/difference), romleg aggregering ' +
        '(1 km grid, postnummer-groupby, næraste-nabo) og rasteranalyse (DEM, slope > 30°, ' +
        'polygonize, to hillshade-variantar). Del B utvidar webkartet med dynamisk PostGIS-' +
        'spørjing (ST_DWithin via Supabase RPC).',
  size: 20,
})]));
CH.push(h3('Endringar etter Canvas-innlevering (svar på sensor-tilbakemelding)'));
CH.push(p([new TextRun({
  text: 'Sensor: «Dokumentasjon er delvis tilfredstillende … forklarer ikke alt på cellenivå … ' +
        'i liten grad hvordan metodene fungerer og hvorfor de er valgt.»',
  italics: true, size: 20, color: MUTED,
})]));
CH.push(bullet('Markdown-cellene for vektor- og rasteranalyse er omarbeidd med eit "HVA → HVORDAN → KVIFOR → TOLKING"-mønster. Kvar celle forklarer no algoritmen (t.d. Horn-formel for slope, GEOS overlay-graf, STR-tre for sjoin) og grunngjev parameterval (kvifor 500 m buffer, kvifor UTM 32N, kvifor 30°-terskel, kvifor azimuth 315°).'));
CH.push(bullet('Lagt til kjelder (Brooks et al. 2017, Horn 1981, NRR 2022) for å støtte tekniske val.'));
CH.push(bullet('Utvida oppsummering (seksjon 9) som eksplisitt mappar krav i oppgåvebeskrivelsen mot leverte celler.'));

// ─── OPPGÅVE 3 ───────────────────────────────────────────────────────────
CH.push(h2('Oppgåve 3 — Prosjektskisse'));
CH.push(p([
  new TextRun({ text: 'Innlevert: ', bold: true, size: 20 }),
  new TextRun({ text: '10. mars 2026 — godkjent.   ', size: 20 }),
  new TextRun({ text: 'Skisse: ', bold: true, size: 20 }),
  link(REPO + '/blob/main/prosjektskisse.md', 'prosjektskisse.md'),
]));
CH.push(h3('Opphavleg leveranse'));
CH.push(p([new TextRun({
  text: 'Éi A4-side med problemstilling, kort beskrivelse, fire datasett (AED, brannstasjon, ' +
        '250 m befolkningsrutenett, dekningsgap som avleidd datasett), teknologistabel ' +
        '(Flask + GeoPandas + Supabase PostGIS + Leaflet) og forventa resultat (interaktivt ' +
        'webkart, dekningsgap-datasett, anbefalingar for nye plasseringar).',
  size: 20,
})]));
CH.push(h3('Endringar etter Canvas-innlevering'));
CH.push(bullet('Ingen strukturelle endringar — sensor karakteriserte skissa som «særdeles relevant» og «på et høyt nivå». Problemstillinga er vidareført ordrett i semesterrapport seksjon 1.2 og i notebooken dekningsgap_analyse.ipynb.'));
CH.push(bullet('Éin justering frå skissa: SSB sitt offisielle 250 m-rutenett er erstatta av ein kalibrert syntetisk modell (begrunna i semesterrapport seksjon 2.3) for at notebooken skal vere reproduserbar utan registrert SSB-tilgang.'));

// ─── KOR FINN SENSOR KVA ─────────────────────────────────────────────────
CH.push(h2('Kor finn sensor kva (snarvegar)'));
CH.push(tbl(
  ['Tema', 'Fil / sti', 'Oppgåve'],
  [
    ['Webkart (Leaflet)',          'templates/index.html',                          '1, 2B'],
    ['Flask + MVC',                'app/__init__.py, app/models/, app/controllers/',  '1'],
    ['OGC WFS (brannstasjonar)',   'app/models/data_model.py',                      '1'],
    ['PostGIS ST_DWithin',         'app/models/data_model.py · supabase_schema.sql',  '1, 2B'],
    ['Notebook — vektor + raster', 'analyse_beredskap.ipynb',                        '2A'],
    ['Notebook — semesterprosjekt','dekningsgap_analyse.ipynb',                      '4'],
    ['Vektoranalyse-pipeline',     'app/models/coverage_model.py',                  '4'],
    ['Avleidd dekningsgap (GeoJSON)', 'app/data/coverage/coverage_gaps.geojson',     '3, 4'],
    ['Risiko-koroplett',           'app/data/coverage/risk_grid.geojson',           '4'],
    ['Greedy-anbefalingar',        'coverage_model.recommend_aed_sites()',          '4'],
    ['Semesterrapport (eigen PDF)', 'semesterrapport.pdf',                          '4'],
  ],
  [3000, 4860, 1500],
));

CH.push(p([new TextRun({
  text: 'Korleis køyre løysinga lokalt: ',
  bold: true, size: 20,
})]));
CH.push(new Paragraph({
  spacing: { before: 40, after: 40 },
  children: [new TextRun({
    text: 'git clone ' + REPO + '   →   pip install -r requirements.txt   →   ' +
          'python generate_population_grid.py   →   python run_coverage_analysis.py   →   ' +
          'python run.py   (server på http://localhost:3000)',
    font: 'Consolas', size: 18,
  })],
}));

// ─── BUILD ───────────────────────────────────────────────────────────────
const doc = new Document({
  creator: 'Gruppe 8 (IS-218)',
  title: 'IS-218 Mapperapport — samla oversikt',
  description: 'Kort oversikt over delinnleveringane oppgåve 1–3',
  styles: {
    default: { document: { run: { font: 'Calibri', size: 20 } } },
    paragraphStyles: [
      { id: 'Heading1', name: 'Heading 1', basedOn: 'Normal', next: 'Normal', quickFormat: true,
        run: { size: 30, bold: true, font: 'Calibri', color: DARK },
        paragraph: { spacing: { before: 240, after: 120 }, outlineLevel: 0 } },
      { id: 'Heading2', name: 'Heading 2', basedOn: 'Normal', next: 'Normal', quickFormat: true,
        run: { size: 24, bold: true, font: 'Calibri', color: ACCENT },
        paragraph: { spacing: { before: 180, after: 60 }, outlineLevel: 1 } },
      { id: 'Heading3', name: 'Heading 3', basedOn: 'Normal', next: 'Normal', quickFormat: true,
        run: { size: 20, bold: true, font: 'Calibri', color: DARK },
        paragraph: { spacing: { before: 100, after: 40 }, outlineLevel: 2 } },
    ],
  },
  numbering: {
    config: [
      { reference: 'bullets',
        levels: [{ level: 0, format: LevelFormat.BULLET, text: '•',
          alignment: AlignmentType.LEFT,
          style: { paragraph: { indent: { left: 540, hanging: 270 } } } }] },
    ],
  },
  sections: [{
    properties: {
      page: {
        size: { width: 11906, height: 16838 },                 // A4
        margin: { top: 1080, right: 1080, bottom: 1080, left: 1080 },  // 0.75"
      },
    },
    headers: {
      default: new Header({ children: [new Paragraph({
        alignment: AlignmentType.RIGHT,
        children: [new TextRun({
          text: 'IS-218 · Mapperapport · Gruppe 8 · Vår 2026',
          size: 16, color: MUTED, italics: true,
        })],
      })] }),
    },
    footers: {
      default: new Footer({ children: [new Paragraph({
        alignment: AlignmentType.CENTER,
        children: [
          new TextRun({ text: 'Side ', size: 16, color: MUTED }),
          new TextRun({ children: [PageNumber.CURRENT], size: 16, color: MUTED }),
          new TextRun({ text: ' av ', size: 16, color: MUTED }),
          new TextRun({ children: [PageNumber.TOTAL_PAGES], size: 16, color: MUTED }),
        ],
      })] }),
    },
    children: CH,
  }],
});

Packer.toBuffer(doc).then(buf => {
  fs.writeFileSync(OUT, buf);
  console.log('OK ✓ Skreiv', OUT, '(' + buf.length + ' bytes)');
});
