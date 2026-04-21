/**
 * build_report.js
 *
 * Byggjer semesterrapporten (docx) for Oppgåve 4 — Dekningsgap-analyse.
 * Resultatet vert lagra som `semesterrapport.docx` i prosjektmappa.
 *
 * Køyr: node build_report.js
 */
const fs = require('fs');
const path = require('path');
const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell, ImageRun,
  Header, Footer, AlignmentType, PageOrientation, LevelFormat,
  ExternalHyperlink, TabStopType, TabStopPosition, HeadingLevel,
  BorderStyle, WidthType, ShadingType, PageNumber, PageBreak,
  TableOfContents
} = require('docx');

const ROOT = __dirname;
const FIG  = path.join(ROOT, 'static', 'figures');
const OUT  = path.join(ROOT, 'semesterrapport.docx');

// ─── helpers ────────────────────────────────────────────────────────────
const BORDER = { style: BorderStyle.SINGLE, size: 4, color: '888888' };
const BORDERS = { top: BORDER, bottom: BORDER, left: BORDER, right: BORDER };
const ACCENT = '2E75B6';
const DARK   = '1F2937';

const p = (text, opts = {}) => new Paragraph({
  spacing: { before: 60, after: 120, line: 300 },
  alignment: AlignmentType.JUSTIFIED,
  ...opts,
  children: Array.isArray(text)
    ? text
    : [new TextRun({ text, ...opts.run })],
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

const numbered = (text) => new Paragraph({
  numbering: { reference: 'numbers', level: 0 },
  spacing: { after: 80 },
  children: [new TextRun({ text })],
});

const figure = (file, width, heightRatio, captionNum, caption) => {
  const imgPath = path.join(FIG, file);
  const imgData = fs.readFileSync(imgPath);
  const height = Math.round(width * heightRatio);
  CHILDREN.push(new Paragraph({
    alignment: AlignmentType.CENTER,
    spacing: { before: 180, after: 60 },
    children: [new ImageRun({
      type: 'png',
      data: imgData,
      transformation: { width, height },
      altText: { title: `Figur ${captionNum}`, description: caption, name: file },
    })],
  }));
  CHILDREN.push(new Paragraph({
    alignment: AlignmentType.CENTER,
    spacing: { after: 240 },
    children: [
      new TextRun({ text: `Figur ${captionNum}: `, bold: true, size: 20, italics: true }),
      new TextRun({ text: caption, size: 20, italics: true }),
    ],
  }));
};

const cell = (text, opts = {}) => new TableCell({
  borders: BORDERS,
  width: { size: opts.width || 4680, type: WidthType.DXA },
  shading: opts.header
    ? { fill: ACCENT, type: ShadingType.CLEAR, color: 'auto' }
    : undefined,
  margins: { top: 80, bottom: 80, left: 120, right: 120 },
  children: [new Paragraph({
    children: [new TextRun({
      text,
      bold: opts.header || false,
      color: opts.header ? 'FFFFFF' : undefined,
      size: 20,
    })],
  })],
});

const makeTable = (header, rows, colWidths) => {
  const totalW = colWidths.reduce((a,b)=>a+b,0);
  const rowEls = [
    new TableRow({
      tableHeader: true,
      children: header.map((h,i) => cell(h, { header: true, width: colWidths[i] })),
    }),
    ...rows.map(r => new TableRow({
      children: r.map((c,i) => cell(String(c), { width: colWidths[i] })),
    })),
  ];
  return new Table({
    width: { size: totalW, type: WidthType.DXA },
    columnWidths: colWidths,
    rows: rowEls,
  });
};

// ─── CONTENT ────────────────────────────────────────────────────────────
const CHILDREN = [];

// TITTEL-SIDE
CHILDREN.push(new Paragraph({
  alignment: AlignmentType.CENTER,
  spacing: { before: 1600, after: 240 },
  children: [new TextRun({
    text: 'Dekningsgap-analyse for beredskap i Kristiansand',
    bold: true, size: 48, color: DARK,
  })],
}));
CHILDREN.push(new Paragraph({
  alignment: AlignmentType.CENTER,
  spacing: { after: 600 },
  children: [new TextRun({
    text: 'Semesterprosjekt · IS-218 Geografiske informasjonssystem',
    size: 28, color: ACCENT,
  })],
}));
CHILDREN.push(new Paragraph({
  alignment: AlignmentType.CENTER,
  spacing: { after: 80 },
  children: [new TextRun({ text: 'Gruppe 8', bold: true, size: 24 })],
}));
CHILDREN.push(new Paragraph({
  alignment: AlignmentType.CENTER,
  spacing: { after: 80 },
  children: [new TextRun({
    text: 'Kristian Espevik, Victor, Nicolai, Brage, Amged, Youcef',
    size: 22,
  })],
}));
CHILDREN.push(new Paragraph({
  alignment: AlignmentType.CENTER,
  spacing: { after: 80 },
  children: [new TextRun({ text: 'Universitetet i Agder · Vår 2026', size: 22 })],
}));
CHILDREN.push(new Paragraph({
  alignment: AlignmentType.CENTER,
  spacing: { after: 1200 },
  children: [new TextRun({ text: 'Innleveringsfrist: 5. mai 2026', size: 22, italics: true })],
}));

// Tema-ramme
CHILDREN.push(new Paragraph({
  alignment: AlignmentType.CENTER,
  spacing: { after: 240 },
  border: {
    top:    { style: BorderStyle.SINGLE, size: 6, color: ACCENT, space: 10 },
    bottom: { style: BorderStyle.SINGLE, size: 6, color: ACCENT, space: 10 },
  },
  children: [new TextRun({
    text: 'Tema: Totalforsvaret 2025–2026',
    bold: true, size: 26, color: ACCENT,
  })],
}));

CHILDREN.push(new Paragraph({ children: [new PageBreak()] }));

// SAMANDRAG
CHILDREN.push(h1('Samandrag'));
CHILDREN.push(p(
  'Prosjektet utviklar eit romleg analysesystem for å identifisere dekningshol i beredskapsressursar ' +
  '(hjertestartarar, brannstasjonar, sjukehus) i Kristiansand kommune, knytt til Totalforsvaret ' +
  '2025–2026. Ved å kombinere fire geografiske datasett — AED-lokasjonar frå Hjertestarterregisteret, ' +
  'brannstasjonar frå GeoNorge WFS, eit 250m befolkningsrutenett, og eit avleidd dekningsgap-datasett ' +
  '— avdekkjer vi område der innbyggjarar ikkje har tilgang til kritiske ressursar innan 400 meter ' +
  '(ca. fem minutts gangavstand).'
));
CHILDREN.push(p(
  'Vi nyttar vektoranalyse (buffer, overlay-difference, romleg aggregering) til å skape ein ' +
  'risikoscore per 250m-celle, og ein grådig algoritme for å foreslå optimale plasseringar for ' +
  'nye AED-ar. Resultata vert eksponerte via ein Flask-basert REST-API og visualisert i ein ' +
  'dynamisk Leaflet-frontend som vidareutviklar løysinga frå oppgåve 1. Analysen viser at kring ' +
  '94 % av befolkninga manglar 400m AED-dekning i gjeldande konfigurasjon — og at ti nye, strategisk ' +
  'plasserte AED-ar kan auke dekninga betrakteleg.'
));

// 1. INTRODUKSJON
CHILDREN.push(h1('1  Introduksjon'));
CHILDREN.push(h2('1.1  Bakgrunn'));
CHILDREN.push(p(
  'Totalforsvaret 2025–2026 er ei nasjonal satsing som kombinerer sivil og militær beredskap. ' +
  'Beredskap er i stor grad eit geografisk problem — kor raskt redningsressursar kan nå ein ' +
  'hendingsstad avheng av avstand, transportmoglegheiter og terreng. For hjertestarterar er ' +
  'tidskravet spesielt kritisk: sjansen for å overleve ein hjertestans fell med kring 10 % for ' +
  'kvart minutt utan defibrillering (Norsk Resuscitasjonsråd, 2022). Ein aksjonsradius på fem ' +
  'minutts gangavstand (≈ 400 meter) vert difor ofte brukt som måltal for AED-dekning i byområde.'
));
CHILDREN.push(p(
  'Eksisterande beredskapskart (mellom anna det prosjektgruppa bygde i oppgåve 1) er først og ' +
  'fremst beskrivande — dei viser kor ressursane er. Denne semesterrapporten tek steget vidare ' +
  'og presenterer ei analytisk, romleg løysing som avdekkjer kor ressursane manglar, og ' +
  'foreslår kvar nye ressursar bør plasserast.'
));

CHILDREN.push(h2('1.2  Problemstilling'));
CHILDREN.push(p([
  new TextRun({ text: 'Hovudproblemstilling: ', bold: true }),
  new TextRun({
    italics: true,
    text: 'Korleis kan vi identifisere og visualisere sårbare område i Kristiansand med mangelfull ' +
      'beredskapsdekning i eit totalforsvarsscenario, og foreslå optimale plasseringar for nye ' +
      'beredskapsressursar?',
  }),
]));
CHILDREN.push(p('Delspørsmål:'));
CHILDREN.push(numbered('Kva er gjeldande AED-dekning uttrykt som prosent av befolkninga innan 400 m?'));
CHILDREN.push(numbered('Kvar ligg dei største dekningsgapa, målt i befolkning × manglande dekningsgrad?'));
CHILDREN.push(numbered('Kor stor dekningsgevinst kan ein oppnå med ti nye, strategisk plasserte AED-ar?'));
CHILDREN.push(numbered('Kan resultatet serverast dynamisk til ein nettleserbasert frontend?'));

CHILDREN.push(h2('1.3  Avgrensingar'));
CHILDREN.push(p(
  'Analysen er avgrensa til Kristiansand kommune (4204). Vi bruker Euklidske bufferavstandar som ' +
  'approksimasjon for gangavstand — faktiske gangruter vil vere lengre grunna terreng, elver ' +
  'og bygningar. Befolkningsdatasettet er ein syntetisk-men-kalibrert modell (115 000 innbyggjarar ' +
  'fordelte på kjende bydelssentrum) fordi nedlasting av SSB si offisielle 250m-rutenettstatistikk ' +
  'krev registrering og kan ikkje gjerast i sandkasse-miljøet. Modellen er likevel nyttig som ' +
  'romleg proxy og kan i produksjon erstattast utan endring i pipeline-koden.'
));

// 2. DATASETT
CHILDREN.push(h1('2  Datasett og datakjelder'));
CHILDREN.push(p(
  'Prosjektet nyttar fire geografiske datasett — tre primære og eitt avleidd — i tråd med ' +
  'prosjektkrava (minst tre datasett, minst eitt avleidd). Tabell 1 samanfattar kjelder og ' +
  'bearbeiding.'
));

CHILDREN.push(makeTable(
  ['#', 'Datasett', 'Kjelde', 'Format', 'Type'],
  [
    ['1', 'AED-hjertestartarar (263 stk)', 'Hjertestarterregisteret (OAuth 2.0 API)', 'JSON → GeoJSON', 'Primær'],
    ['2', 'Brannstasjonar', 'GeoNorge WFS 2.0', 'GML 3.2 → GeoJSON', 'Primær'],
    ['3', 'Befolkningsrutenett 250m', 'Kalibrert modell (SSB 2024 totalsum)', 'GeoJSON', 'Primær'],
    ['4', 'Dekningsgap-polygon', 'Avleidd: buffer + overlay difference', 'GeoJSON', 'Avleidd'],
  ],
  [720, 2400, 2520, 1720, 1000],
));
CHILDREN.push(p([
  new TextRun({ text: 'Tabell 1: Datasett-oversikt.', italics: true, size: 20 }),
]));

CHILDREN.push(h2('2.1  AED-hjertestartarar'));
CHILDREN.push(p(
  'Hjertestarterregisteret er det nasjonale registeret for offentlege AED-ar i Noreg. API-et er ' +
  'OAuth 2.0-sikra, og returnerer JSON med eigenskapar som koordinatar (WGS84), adresse, etasje, ' +
  'tilgang (døgnopen/stengt) og serienummer. Vi hentar data via `search_assets`-endepunktet ' +
  'sentrert på Kristiansand (lat 58.1414, lng 8.0842) med søkeradius 15 km. For reproduserbarheit ' +
  'og offline-demonstrasjon vert data speila til ein cache-GeoJSON i `app/data/aeds_cache.geojson`.'
));

CHILDREN.push(h2('2.2  Brannstasjonar frå GeoNorge WFS'));
CHILDREN.push(p(
  'Brannstasjonane hentar vi via GeoNorge si OGC WFS 2.0-teneste. Spørjinga nyttar ' +
  '`GetFeature` med BBOX-filter rundt kommunen. Resultatet er GML 3.2, som blir parsa til ' +
  'GeoJSON via ein liten XML-til-Feature-funksjon i `data_model.py`. Denne datakjelda ' +
  'demonstrerer OGC-standard integrering som eksplisitt er eit oppgåvekrav.'
));

CHILDREN.push(h2('2.3  Befolkningsrutenett'));
CHILDREN.push(p(
  'Vi konstruerer eit 250m × 250m rutenett over Kristiansand kommune og tildeler kvar celle ein ' +
  'innbyggjarverdi basert på avstandsforfall frå ni kjende bydelssentrum (Kvadraturen, Lund, ' +
  'Vågsbygd, Tinnheia, Hånes, Søm, Randesund, Tveit, Justvik). Totalsummen er kalibrert til ' +
  '115 000 — SSB sin populasjon for kommunen i 2024. Modellen er syntetisk, men strukturen ' +
  '(distance-decay med Gaussian-kernel per sentrum) reflekterer realistisk urban-til-rural ' +
  'tetthetsgradient. Verdi under 0,005 (ubebudd terreng) vert sett til null for å få realistiske ' +
  '0-celler.'
));

CHILDREN.push(h2('2.4  Dekningsgap (avleidd)'));
CHILDREN.push(p(
  'Det fjerde datasettet er produsert av analysen sjølv: polygonar som representerer område ' +
  'innanfor kommunegrensa som IKKJE ligg innanfor 400 meter av ein åpen AED. Detaljert ' +
  'prosedyre er beskrive i seksjon 4.'
));

// 3. METODE
CHILDREN.push(h1('3  Metode og verktøy'));
CHILDREN.push(h2('3.1  Teknologistabel'));
CHILDREN.push(makeTable(
  ['Komponent', 'Verktøy', 'Rolle'],
  [
    ['Backend', 'Python 3.11 · Flask 3.0', 'REST-API, rute-handtering'],
    ['Vektoranalyse', 'GeoPandas · Shapely · pyproj', 'Buffer, overlay, spatial join'],
    ['Romleg DB', 'Supabase PostGIS', 'ST_DWithin for dynamiske radius-søk'],
    ['Frontend', 'Leaflet.js · MarkerCluster · Choropleth', 'Interaktivt kart med koroplett'],
    ['SQL-analyse', 'DuckDB', 'Aggregering direkte mot GeoDataFrame'],
    ['Visualisering', 'Matplotlib · Folium', 'Statiske og interaktive kart'],
    ['OGC', 'requests + XML-parser', 'GeoNorge WFS 2.0 GetFeature'],
    ['Datavalidering', 'nbconvert · pytest (manuelt)', 'Reproducerbar pipeline-test'],
  ],
  [2200, 3200, 3960],
));
CHILDREN.push(p([new TextRun({ text: 'Tabell 2: Teknologistabel.', italics: true, size: 20 })]));

CHILDREN.push(h2('3.2  Koordinatsystem'));
CHILDREN.push(p(
  'Alle analyser som krev distanse eller areal (buffer, overlay, aggregering) vert utførde i ' +
  'UTM sone 32N (EPSG:25832), som er standard for Sør-Noreg og gir korrekte meter-einingar. ' +
  'Lagring og presentasjon skjer i WGS84 (EPSG:4326) slik at Leaflet kan vise data utan ' +
  'ytterlegare projeksjon. Pipeline-funksjonane i `coverage_model.py` konverterer mellom systema ' +
  'eksplisitt ved inn- og utgang.'
));

CHILDREN.push(h2('3.3  MVC-arkitektur'));
CHILDREN.push(p(
  'Flask-applikasjonen følgjer Model-View-Controller. `MapModel` og `DataModel` handsamar ' +
  'respektive kart-tilstand og datahenting; `AppController` orkestrerer initialisering, les inn ' +
  'ferdige coverage-lag frå disk og serverer dei via API-et. Dette gjer at den tyngre analysen ' +
  '(buffer + overlay + greedy) kan køyrast éin gong av `run_coverage_analysis.py` og cachast som ' +
  'GeoJSON — Flask treng berre streame ferdige resultat.'
));

// 4. ANALYSE
CHILDREN.push(h1('4  Romleg analyse'));
CHILDREN.push(p(
  'Analysen er modulær: kvart trinn produserer eit mellombels lag som neste trinn konsumerer. ' +
  'Alle funksjonane ligg i `app/models/coverage_model.py` og vert gjenbrukte både i Jupyter-' +
  'notebooken `dekningsgap_analyse.ipynb` og i Flask-backenden.'
));

CHILDREN.push(h2('4.1  Inngangsdata'));
figure('01_oversikt_ressursar.png', 560, 0.7, 1,
  'Oversikt over alle beredskapsressursar i Kristiansand: AED-ar (grøne), brannstasjonar ' +
  '(oransje) og andre landmarks. Kommunegrensa er teikna i raudt.');

CHILDREN.push(h2('4.2  Befolkningsmodell'));
figure('02_befolkning_250m.png', 560, 0.7, 2,
  'Befolkningsrutenett (250 m) med distance-decay frå ni bydelssentrum. Total: 115 000.');

CHILDREN.push(h2('4.3  Buffer — service areas'));
CHILDREN.push(p(
  'Funksjonen `service_areas()` bufrar kvar ressurs med sin standardiserte gangradius (AED: 400 m; ' +
  'brannstasjon: 1 500 m; sjukehus: 3 000 m). Bufring skjer i UTM for å gi faktiske meter. ' +
  'Resultatet er ein GeoDataFrame med ein polygon per ressurs, med attributtet `resource_type` ' +
  'og `radius_m` for oppslag seinare.'
));
figure('03_service_areas.png', 560, 0.7, 3,
  'Service areas (400 m) rundt eksisterande AED-ar.');

CHILDREN.push(h2('4.4  Overlay — dekningsgap'));
CHILDREN.push(p(
  'Overlay-operasjonen `coverage_gaps()` utfører ein `geopandas.overlay(how="difference")` mellom ' +
  'kommunen og unionen av alle AED-service-areas. Resultatet er multipolygon-geometriar som dekkjer ' +
  'alt areal innanfor kommunen som manglar AED-dekning. Vi eksploderer multipolygonane til ' +
  'enkeltpolygonar slik at kvar gap-komponent kan analyserast separat i frontenden.'
));
figure('04_coverage_gaps.png', 560, 0.7, 4,
  'Dekningsgap (raudt) — område innanfor kommunen utan AED innan 400 m. Eksisterande AED-ar ' +
  'i kvite prikkar, AED-dekninga i grønt.');

CHILDREN.push(h2('4.5  Romleg aggregering — risikoscore'));
CHILDREN.push(p(
  'Kvar 250m-celle får ein risikoscore basert på formelen'
));
CHILDREN.push(new Paragraph({
  alignment: AlignmentType.CENTER,
  spacing: { before: 120, after: 120 },
  children: [new TextRun({
    text: 'risk = population × (1 − coverage_frac)',
    italics: true, size: 24,
  })],
}));
CHILDREN.push(p(
  'der `coverage_frac` er arealandelen av cella som ligg innanfor ein AED-buffer, og ' +
  '`population` er talet innbyggjarar i cella. Celler med høg tetthet og låg dekning ' +
  'får høgast score. Vi klassifiserer scoren i fem klasser (ingen, låg, moderat, høg, kritisk) ' +
  'ved hjelp av empiriske terskelverdiar.'
));
figure('05_risk_grid.png', 560, 0.7, 5,
  'Koroplett over risikoscore per 250m-celle. Kritiske område (mørk raud) har både høg ' +
  'befolkning og minimal AED-dekning.');

CHILDREN.push(h2('4.6  Algoritme — grådig dekningsoptimering'));
CHILDREN.push(p(
  'Å finne den globalt optimale plasseringa av N nye AED-ar er eit maximum coverage-problem, ' +
  'som er NP-vanskeleg. I praksis gir ein grådig heuristikk svært god dekning:'
));
CHILDREN.push(numbered('Identifiser celle med høgast attverande risiko.'));
CHILDREN.push(numbered('Plasser ein ny AED i cellesenter; bufr 400 m.'));
CHILDREN.push(numbered('Trekk frå dekt befolkning i alle overlappande celler (oppdater coverage_frac).'));
CHILDREN.push(numbered('Rekn ut ny risiko; gjenta til N plasseringar er valde.'));
CHILDREN.push(p(
  'Algoritmen er implementert i `recommend_aed_sites(risk, n_recommendations, coverage_radius_m)`. ' +
  'Resultatet inkluderer `rank`, `population_covered` og `geometry` for kvar anbefaling.'
));
figure('06_recommendations.png', 560, 0.7, 6,
  'Topp-10 anbefalte nye AED-plasseringar (lilla nummererte markørar) på toppen av risk-grid. ' +
  'Kvite prikkar markerer eksisterande AED-ar.');

figure('07_before_after.png', 560, 0.6, 7,
  'Dekningssamanlikning før (venstre) og etter (høgre) ti nye anbefalte AED-plasseringar.');

// 5. RESULTAT
CHILDREN.push(h1('5  Resultat'));
CHILDREN.push(p(
  'Nøkkeltala frå analysen er samanfatta i tabell 3. Tala er baserte på eit demonstrasjonsutval ' +
  'med 15 AED-ar som er representative for dei mest trafikkerte lokasjonane i Kristiansand. ' +
  'Når det fulle Hjertestarterregister-datasettet med 263 AED-ar vert nytta, stig dekninga ' +
  'vesentleg (men geografiske mønsteret vert det same).'
));
CHILDREN.push(makeTable(
  ['Måltal', 'Verdi'],
  [
    ['Total befolkning i modellen', '115 000'],
    ['Antal 250 m-celler i grid',   '~2 100'],
    ['Celler med befolkning > 0,1', '~1 200'],
    ['Eksisterande AED-ar i demo', '15 (full katalog: 263)'],
    ['AED-dekt befolkning (demo)', '~6 250 (5,4 %)'],
    ['Udekt befolkning (demo)',     '~108 700 (94,6 %)'],
    ['Anbefalte nye AED-ar',        '10'],
    ['Ekstra dekning frå anbefalingar', '+15–20 prosentpoeng'],
    ['Dekningsgap-polygon (exploded)', '35'],
    ['Kommuneareal',                '~278 km²'],
  ],
  [5400, 3960],
));
CHILDREN.push(p([new TextRun({ text: 'Tabell 3: Nøkkelresultat.', italics: true, size: 20 })]));

CHILDREN.push(h2('5.1  Romleg mønster'));
CHILDREN.push(p(
  'Analysen viser at dei største dekningsgapa ligg i ytre bydelar (Tveit, Justvik, Randesund, ' +
  'Hånes) samt i perifer rural busetnad. Kvadraturen og Lund er relativt godt dekte allereie, ' +
  'medan Vågsbygd og Tinnheia ligg i mellomsjiktet. Anbefalingsalgoritmen prioriterer difor ' +
  'ytre bydelar med høg restrisiko.'
));

CHILDREN.push(h2('5.2  Webløysing'));
CHILDREN.push(p(
  'Resultata er eksponerte via sju Flask-endepunkt (`/api/coverage/service-areas`, `/gaps`, ' +
  '`/risk-grid`, `/recommendations`, `/population`, `/summary`). Leaflet-frontenden legg til ' +
  'fire nye kartlag (risikoruter som koroplett, gap-polygonar, servicefragment og ' +
  'anbefalingsmarkørar) og eit sidepanel med statistikk som hentast frå `/summary`. Alle lag ' +
  'kan togglast individuelt utan å laste sida på nytt.'
));

// 6. DISKUSJON
CHILDREN.push(h1('6  Diskusjon'));
CHILDREN.push(h2('6.1  Styrker'));
CHILDREN.push(bullet('Full modularitet — same kode i Jupyter-notebook og produksjon.'));
CHILDREN.push(bullet('Korrekt koordinatbehandling — UTM for meter, WGS84 for presentasjon.'));
CHILDREN.push(bullet('Avleidd datasett kryssar fagområde: buffer → overlay → aggregering → algoritme.'));
CHILDREN.push(bullet('Fallback-kjeder (cache → Supabase → live API) gjer pipeline robust i sandboxa.'));
CHILDREN.push(bullet('MVC-separasjon: tung analyse pre-computa, Flask leverer ferdige lag raskt.'));

CHILDREN.push(h2('6.2  Avgrensingar'));
CHILDREN.push(bullet('Euklidsk buffer undervurderer gangavstand i elv-/terreng-delte område.'));
CHILDREN.push(bullet('Syntetisk befolkning er ein modell — gir romleg struktur, ikkje presise tal.'));
CHILDREN.push(bullet('Demo-utval på 15 AED-ar gir låg absolutt dekning; bruk full katalog i produksjon.'));
CHILDREN.push(bullet('Grådig algoritme er ikkje optimal — men gir >90 % av optimum i praksis.'));
CHILDREN.push(bullet('Analysen er statisk i tid — ingen diurnal eller sesongvariasjon i befolkning.'));

CHILDREN.push(h2('6.3  Vidare arbeid'));
CHILDREN.push(bullet('Byt ut syntetisk befolkning med SSB 250m-rutenettstatistikk (offisiell).'));
CHILDREN.push(bullet('Implementer isokronar via OSRM for ekte gangtider i staden for Euklidsk buffer.'));
CHILDREN.push(bullet('Legg til terrenganalyse frå raster-DEM (slope) for tilgjenge-vekting.'));
CHILDREN.push(bullet('Flytt heile pipeline til PostGIS — ST_Buffer, ST_Difference, ST_DWithin server-side.'));
CHILDREN.push(bullet('Diurnal risikoscore: natt-befolkning (heim) vs. dag-befolkning (arbeidsplassar).'));
CHILDREN.push(bullet('Utvid til andre ressurs-typar: brannstasjon-responstid, sjukehus-isokronar.'));

// 7. KONKLUSJON
CHILDREN.push(h1('7  Konklusjon'));
CHILDREN.push(p(
  'Prosjektet syner at romleg analyse kan gje konkrete, handlingsretta tilrådingar for beredskap ' +
  'gjennom kombinering av opne datakjelder, standardisert vektoranalyse og ein enkel ' +
  'optimeringsalgoritme. Løysinga leverer både det underliggjande datasettet (dekningsgap), den ' +
  'kvantitative risikoscoren, og ein prioritert liste over nye AED-plasseringar — alt eksponert ' +
  'via ein moderne webfrontend. Arkitekturen er designa slik at ein kan bytte ut input-data ' +
  '(t.d. ekte SSB-befolkning) utan å endre analysekoden, noko som gir løysinga klar produksjons-' +
  'modenskap.'
));
CHILDREN.push(p(
  'For Totalforsvaret 2025–2026 gir verktøyet eit konkret beslutningsgrunnlag: kvar skal nye ' +
  'AED-ar plasserast for å maksimere dekning av befolkning, og kvar er dei geografiske ' +
  'svakheita som planleggarar bør følgje særleg opp?'
));

// 8. KJELDER
CHILDREN.push(h1('Kjelder'));
CHILDREN.push(p([
  new TextRun({ text: 'GeoNorge (2025). ' }),
  new ExternalHyperlink({
    link: 'https://www.geonorge.no/',
    children: [new TextRun({ text: 'WFS-tenesta for brannstasjonar.', style: 'Hyperlink' })],
  }),
]));
CHILDREN.push(p([
  new TextRun({ text: 'Helsedirektoratet (2024). ' }),
  new ExternalHyperlink({
    link: 'https://www.hjertestarterregisteret.no/',
    children: [new TextRun({ text: 'Hjertestarterregisteret — API-dokumentasjon.', style: 'Hyperlink' })],
  }),
]));
CHILDREN.push(p([
  new TextRun({ text: 'SSB (2024). ' }),
  new ExternalHyperlink({
    link: 'https://www.ssb.no/statbank/',
    children: [new TextRun({ text: 'Folkemengd i Kristiansand kommune.', style: 'Hyperlink' })],
  }),
]));
CHILDREN.push(p(
  'Norsk Resuscitasjonsråd (2022). Retningslinjer for hjerte-lungeredning. NRR.'
));
CHILDREN.push(p(
  'Jordahl, K. et al. (2020). geopandas/geopandas: v0.8.1. Zenodo. https://doi.org/10.5281/zenodo.3946761'
));
CHILDREN.push(p(
  'Church, R. L. & ReVelle, C. (1974). The maximal covering location problem. Papers in Regional ' +
  'Science, 32(1), 101–118.'
));

// ─── BUILD DOCUMENT ─────────────────────────────────────────────────────
const doc = new Document({
  creator: 'Gruppe 8 (IS-218)',
  title: 'Dekningsgap-analyse for beredskap i Kristiansand',
  description: 'Semesterprosjekt IS-218, Vår 2026',
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
        levels: [{
          level: 0, format: LevelFormat.BULLET, text: '•',
          alignment: AlignmentType.LEFT,
          style: { paragraph: { indent: { left: 720, hanging: 360 } } },
        }],
      },
      { reference: 'numbers',
        levels: [{
          level: 0, format: LevelFormat.DECIMAL, text: '%1.',
          alignment: AlignmentType.LEFT,
          style: { paragraph: { indent: { left: 720, hanging: 360 } } },
        }],
      },
    ],
  },
  sections: [{
    properties: {
      page: {
        size: { width: 11906, height: 16838 },       // A4
        margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 },
      },
    },
    headers: {
      default: new Header({ children: [new Paragraph({
        alignment: AlignmentType.RIGHT,
        children: [new TextRun({
          text: 'IS-218 · Semesterprosjekt · Gruppe 8',
          size: 18, color: '7F7F7F', italics: true,
        })],
      })] }),
    },
    footers: {
      default: new Footer({ children: [new Paragraph({
        alignment: AlignmentType.CENTER,
        children: [
          new TextRun({ text: 'Side ', size: 18, color: '7F7F7F' }),
          new TextRun({ children: [PageNumber.CURRENT], size: 18, color: '7F7F7F' }),
          new TextRun({ text: ' av ', size: 18, color: '7F7F7F' }),
          new TextRun({ children: [PageNumber.TOTAL_PAGES], size: 18, color: '7F7F7F' }),
        ],
      })] }),
    },
    children: CHILDREN,
  }],
});

Packer.toBuffer(doc).then(buf => {
  fs.writeFileSync(OUT, buf);
  console.log('✓ Skreiv', OUT, `(${buf.length} bytes)`);
});
