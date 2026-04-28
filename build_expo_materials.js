/**
 * build_expo_materials.js
 *
 * Genererer tre filer for Expo 28.04.2026:
 *   1. expo_handout.docx       — A4 utdeling med QR-kode og statistikk
 *   2. expo_poster.docx        — A3 liggande bord-poster (stor tagline)
 *   3. expo_demo_kort.docx     — A4 scenariokort (sjuks-skår, til standen)
 *
 * Køyr: node build_expo_materials.js
 */
const fs = require('fs');
const path = require('path');
const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell, ImageRun,
  Header, Footer, AlignmentType, PageOrientation, LevelFormat, HeadingLevel,
  BorderStyle, WidthType, ShadingType, PageNumber, PageBreak, ExternalHyperlink,
} = require('/sessions/optimistic-gallant-faraday/mnt/outputs/node_pkgs/node_modules/docx');

const ROOT = __dirname;
const QR   = path.join(ROOT, 'qr_repo.png');

const ACCENT  = '2E75B6';
const DARK    = '1F2937';
const ALERT   = 'DC2626';
const WARN    = 'F59E0B';
const MUTED   = '6B7280';
const LIGHTBG = 'F3F4F6';

const BORDER  = { style: BorderStyle.SINGLE, size: 4, color: 'BBBBBB' };
const NO_BORDER = { style: BorderStyle.NONE, size: 0, color: 'auto' };
const BORDERS_ALL = { top: BORDER, bottom: BORDER, left: BORDER, right: BORDER };
const BORDERS_NONE = { top: NO_BORDER, bottom: NO_BORDER, left: NO_BORDER, right: NO_BORDER };

const tr = (text, opts = {}) => new TextRun({ text, ...opts });

const para = (children, opts = {}) => new Paragraph({
  spacing: { before: 60, after: 60, line: 280 },
  ...opts,
  children: Array.isArray(children) ? children : [tr(children, opts.run || {})],
});

const cell = (children, opts = {}) => new TableCell({
  borders: opts.bordered ? BORDERS_ALL : BORDERS_NONE,
  width: { size: opts.width || 4680, type: WidthType.DXA },
  shading: opts.shading ? { fill: opts.shading, type: ShadingType.CLEAR, color: 'auto' } : undefined,
  margins: { top: opts.padTop || 80, bottom: opts.padBot || 80, left: 120, right: 120 },
  verticalAlign: opts.valign || undefined,
  children: Array.isArray(children) ? children : [children],
});

// ────────────────────────────────────────────────────────────────────────────
// 1. EXPO HANDOUT — A4 portrait, ein side
// ────────────────────────────────────────────────────────────────────────────
function buildHandout() {
  const C = [];

  // Header med tittel og gruppe
  C.push(new Table({
    width: { size: 9360, type: WidthType.DXA },
    columnWidths: [6240, 3120],
    rows: [new TableRow({ children: [
      cell([
        para([tr('Beredskapskart Kristiansand', { bold: true, size: 40, color: 'FFFFFF' })]),
        para([tr('Kvar manglar hjertestartarane når sekundene tel?', { size: 22, color: 'FFFFFF' })]),
      ], { width: 6240, shading: ACCENT, padTop: 240, padBot: 240 }),
      cell([
        para([tr('Gruppe 8', { bold: true, size: 28, color: 'FFFFFF' })], { alignment: AlignmentType.RIGHT }),
        para([tr('IS-218 · UiA · Vår 2026', { size: 18, color: 'FFFFFF' })], { alignment: AlignmentType.RIGHT }),
        para([tr('Totalforsvaret 2025–2026', { size: 18, color: 'FFFFFF' })], { alignment: AlignmentType.RIGHT }),
      ], { width: 3120, shading: DARK, padTop: 240, padBot: 240 }),
    ]})],
  }));

  // Why-What-How boks
  C.push(para([], { spacing: { after: 0 } }));
  C.push(new Table({
    width: { size: 9360, type: WidthType.DXA },
    columnWidths: [9360],
    rows: [new TableRow({ children: [
      cell([
        para([
          tr('KVIFOR. ', { bold: true, color: WARN, size: 22 }),
          tr('I ein nødssituasjon er sekundene avgjerande. Folk treng å vite kor dei nærmaste beredskapsressursane er — hjertestartarar, sjukehus, brannstasjonar — utan å måtte leite på fleire nettsider.', {}),
        ]),
        para([
          tr('KVA. ', { bold: true, color: WARN, size: 22 }),
          tr('Vi har bygd eit interaktivt webkart som samlar publikumstilgjengelege beredskapsressursar i Kristiansand i éin felles løysing — med ruting til nærmaste, klikkbare popup-ar og romleg søk.', {}),
        ]),
        para([
          tr('KORLEIS. ', { bold: true, color: WARN, size: 22 }),
          tr('Vi kombinerer Hjertestarterregisteret (live API), GeoNorge OGC WFS, lokale beredskapsdata og Supabase PostGIS — alt rendra i sanntid i nettleseren via Leaflet og Flask.', {}),
        ]),
      ], { shading: 'FEF3C7', padTop: 160, padBot: 160 }),
    ]})],
  }));

  // Tre store nøkkeltal
  C.push(para([], { spacing: { after: 80 } }));
  C.push(new Table({
    width: { size: 9360, type: WidthType.DXA },
    columnWidths: [3080, 3080, 3200],
    rows: [new TableRow({ children: [
      cell([
        para([tr('4', { bold: true, size: 56, color: ACCENT })], { alignment: AlignmentType.CENTER }),
        para([tr('Datakjelder kombinerte (API, WFS, lokal, PostGIS)', { size: 18, color: MUTED })], { alignment: AlignmentType.CENTER }),
      ], { shading: LIGHTBG, padTop: 160, padBot: 160 }),
      cell([
        para([tr('Live', { bold: true, size: 56, color: ACCENT })], { alignment: AlignmentType.CENTER }),
        para([tr('Sanntidsdata henta direkte frå Hjertestarterregisteret', { size: 18, color: MUTED })], { alignment: AlignmentType.CENTER }),
      ], { shading: LIGHTBG, padTop: 160, padBot: 160 }),
      cell([
        para([tr('Klikk', { bold: true, size: 56, color: ACCENT })], { alignment: AlignmentType.CENTER }),
        para([tr('Romleg søk i kartet via PostGIS ST_DWithin', { size: 18, color: MUTED })], { alignment: AlignmentType.CENTER }),
      ], { shading: LIGHTBG, padTop: 160, padBot: 160 }),
    ]})],
  }));

  // Funksjonsoversikt + QR side ved side
  C.push(para([], { spacing: { after: 80 } }));
  C.push(new Table({
    width: { size: 9360, type: WidthType.DXA },
    columnWidths: [6360, 3000],
    rows: [new TableRow({ children: [
      cell([
        para([tr('Kva kartet kan', { bold: true, size: 24, color: ACCENT })]),
        para([
          tr('• ', { bold: true, color: ACCENT }),
          tr('Vise alle publikumstilgjengelege hjertestartarar (AED), brannstasjonar, sjukehus, AMK, politi og sivilforsvar i Kristiansand på éit kart.', { size: 18 }),
        ]),
        para([
          tr('• ', { bold: true, color: ACCENT }),
          tr('Finne nærmaste åpne AED frå din posisjon — med rutevegen teikna inn (OSRM gangveg-ruting).', { size: 18 }),
        ]),
        para([
          tr('• ', { bold: true, color: ACCENT }),
          tr('Klikkbart romleg søk: trykk kvar som helst → få liste over AED-ar innan valt radius (PostGIS ST_DWithin server-side).', { size: 18 }),
        ]),
        para([
          tr('• ', { bold: true, color: ACCENT }),
          tr('Detaljerte popup-ar med adresse, etasje, tilgang, åpningstider og oppdatert status frå Hjertestarterregisteret.', { size: 18 }),
        ]),
        para([
          tr('• ', { bold: true, color: ACCENT }),
          tr('Datadrevet fargekoding: grønn = åpen AED, raud = stengt — så ein kan filtrere bort dei som ikkje er tilgjengelege når du treng dei.', { size: 18 }),
        ]),
      ], { width: 6360, padTop: 80, padBot: 80 }),

      cell([
        para([new ImageRun({
          type: 'png',
          data: fs.readFileSync(QR),
          transformation: { width: 140, height: 140 },
          altText: { title: 'QR repo', description: 'GitHub repo', name: 'qr' },
        })], { alignment: AlignmentType.CENTER }),
        para([tr('Skann for repo', { bold: true, size: 18 })], { alignment: AlignmentType.CENTER }),
        para([tr('github.com/', { size: 14 })], { alignment: AlignmentType.CENTER }),
        para([tr('KristianEspevikUIA/', { size: 14 })], { alignment: AlignmentType.CENTER }),
        para([tr('IS218GR8', { size: 14 })], { alignment: AlignmentType.CENTER }),
      ], { width: 3000, padTop: 80, padBot: 80, valign: 'center' }),
    ]})],
  }));

  // Teknologi-chips
  C.push(para([], { spacing: { after: 80 } }));
  C.push(para([tr('Teknologi', { bold: true, size: 22, color: ACCENT })]));
  C.push(para([
    tr('Python 3.11   ·   ', { size: 18 }),
    tr('Flask MVC   ·   ', { size: 18 }),
    tr('GeoPandas + Shapely   ·   ', { size: 18 }),
    tr('Supabase PostGIS (ST_DWithin)   ·   ', { size: 18 }),
    tr('Leaflet.js   ·   ', { size: 18 }),
    tr('DuckDB   ·   ', { size: 18 }),
    tr('OGC WFS 2.0   ·   ', { size: 18 }),
    tr('OAuth 2.0', { size: 18 }),
  ]));

  // Kva juryen ser
  C.push(para([], { spacing: { after: 60 } }));
  C.push(para([tr('Demo — tre scenarier vi viser', { bold: true, size: 22, color: ACCENT })]));
  [
    ['1.', 'Klikk "Finn nærmaste AED"', '→ OSRM rutenavigering på gangveg, raud stipla linje + estimert gåtid.'],
    ['2.', 'Aktiver PostGIS-modus',     '→ koordinatane går til Supabase, ST_DWithin gjev AED-ar i radius.'],
    ['3.', 'Klikk på AED-markør',       '→ popup med adresse, etasje, tilgang, åpningstider live frå API.'],
  ].forEach(([n, head, tail]) => {
    C.push(para([
      tr(n + '  ', { bold: true, size: 18, color: ACCENT }),
      tr(head, { bold: true, size: 18 }),
      tr('  ' + tail, { size: 18 }),
    ]));
  });

  // Footer
  C.push(para([], { spacing: { after: 80 } }));
  C.push(new Table({
    width: { size: 9360, type: WidthType.DXA },
    columnWidths: [9360],
    rows: [new TableRow({ children: [
      cell([
        para([tr('Kristian Espevik · Victor Ziadpour · Nicolai Stephansen · Brage Kristoffersen · Amged Mohammed · Youcef Youcef', { size: 14, color: MUTED })], { alignment: AlignmentType.CENTER }),
      ], { padTop: 60, padBot: 60 }),
    ]})],
  }));

  return new Document({
    styles: { default: { document: { run: { font: 'Calibri', size: 18 } } } },
    sections: [{
      properties: { page: {
        size: { width: 11906, height: 16838 },
        margin: { top: 720, right: 720, bottom: 720, left: 720 },  // 0.5"
      }},
      children: C,
    }],
  });
}

// ────────────────────────────────────────────────────────────────────────────
// 2. POSTER — A3 liggande, stor tagline
// ────────────────────────────────────────────────────────────────────────────
function buildPoster() {
  const C = [];

  // Massiv tittel midt på
  C.push(para([], { spacing: { before: 1200 } }));
  C.push(para([tr('GRUPPE 8', { bold: true, size: 48, color: ACCENT })], { alignment: AlignmentType.CENTER }));
  C.push(para([], { spacing: { before: 200 } }));
  C.push(para([tr('Beredskapskart Kristiansand', { bold: true, size: 96, color: DARK })], { alignment: AlignmentType.CENTER }));
  C.push(para([], { spacing: { before: 200 } }));
  C.push(para([tr('Finn nærmaste hjertestartar — på sekund.', { italics: true, size: 36, color: MUTED })], { alignment: AlignmentType.CENTER }));

  C.push(para([], { spacing: { before: 600 } }));

  // Tre store stats
  C.push(new Table({
    width: { size: 14400, type: WidthType.DXA },
    columnWidths: [4800, 4800, 4800],
    rows: [new TableRow({ children: [
      cell([
        para([tr('4', { bold: true, size: 96, color: ACCENT })], { alignment: AlignmentType.CENTER }),
        para([tr('datakjelder kombinerte', { size: 24, color: MUTED })], { alignment: AlignmentType.CENTER }),
      ], { shading: LIGHTBG, padTop: 240, padBot: 240, width: 4800 }),
      cell([
        para([tr('Live', { bold: true, size: 96, color: ACCENT })], { alignment: AlignmentType.CENTER }),
        para([tr('AED-data direkte frå registeret', { size: 24, color: MUTED })], { alignment: AlignmentType.CENTER }),
      ], { shading: LIGHTBG, padTop: 240, padBot: 240, width: 4800 }),
      cell([
        para([tr('1 klikk', { bold: true, size: 96, color: ACCENT })], { alignment: AlignmentType.CENTER }),
        para([tr('til nærmaste åpne AED', { size: 24, color: MUTED })], { alignment: AlignmentType.CENTER }),
      ], { shading: LIGHTBG, padTop: 240, padBot: 240, width: 4800 }),
    ]})],
  }));

  C.push(para([], { spacing: { before: 600 } }));

  // QR + invitasjon
  C.push(new Table({
    width: { size: 14400, type: WidthType.DXA },
    columnWidths: [10000, 4400],
    rows: [new TableRow({ children: [
      cell([
        para([tr('Stopp og prøv kartet!', { bold: true, size: 56, color: DARK })]),
        para([tr('Klikk på kvar som helst i Kristiansand →', { size: 28, color: MUTED })]),
        para([tr('sjå AED-ane innan 2 km via PostGIS romleg spørjing.', { size: 28, color: MUTED })]),
        para([], { spacing: { before: 120 } }),
        para([tr('Tema: ', { size: 24 }), tr('Totalforsvaret 2025–2026', { size: 24, italics: true, color: ACCENT })]),
        para([tr('IS-218 · Universitetet i Agder · Vår 2026', { size: 22, color: MUTED })]),
      ], { padTop: 120, padBot: 120, width: 10000, valign: 'center' }),
      cell([
        para([new ImageRun({
          type: 'png',
          data: fs.readFileSync(QR),
          transformation: { width: 200, height: 200 },
          altText: { title: 'QR', description: 'repo', name: 'qr' },
        })], { alignment: AlignmentType.CENTER }),
        para([tr('Repo / kjeldekode', { size: 18, color: MUTED })], { alignment: AlignmentType.CENTER }),
      ], { width: 4400, valign: 'center' }),
    ]})],
  }));

  return new Document({
    styles: { default: { document: { run: { font: 'Calibri', size: 22 } } } },
    sections: [{
      properties: { page: {
        size: { width: 16838, height: 11906, orientation: PageOrientation.LANDSCAPE },  // A3 liggande (men docx-js swap)
        margin: { top: 1080, right: 1080, bottom: 1080, left: 1080 },
      }},
      children: C,
    }],
  });
}

// ────────────────────────────────────────────────────────────────────────────
// 3. DEMO-KORT — A4, kort scenariooversikt for å ha i nærleiken på standen
// ────────────────────────────────────────────────────────────────────────────
function buildDemoCard() {
  const C = [];

  C.push(para([tr('STAND-KORT — IS-218 Gruppe 8', { bold: true, size: 24, color: ACCENT })], { alignment: AlignmentType.CENTER }));
  C.push(para([tr('Beredskapskart Kristiansand · Expo 28.04', { size: 18, color: MUTED, italics: true })], { alignment: AlignmentType.CENTER }));
  C.push(para([], { spacing: { after: 120 } }));

  // 90-sek pitch
  C.push(para([tr('🎤 90-sekund pitch (KVIFOR / KVA / KORLEIS)', { bold: true, size: 22, color: ACCENT })]));
  C.push(para([
    tr('"I ein nødssituasjon er sekundene avgjerande. Folk veit sjeldan kor nærmaste hjertestartar er, ', { size: 18 }),
    tr('og sjølv om informasjonen finst i offentlege register, er det spreidd over fleire kjelder. ', { size: 18 }),
    tr('Vi bygde eit interaktivt webkart for Kristiansand som samlar alle publikumstilgjengelege ', { size: 18 }),
    tr('beredskapsressursar — hjertestartarar, sjukehus, brannstasjonar, AMK — på éit kart, og kan ', { size: 18 }),
    tr('ruta deg til den næraste på sekund. Det kombinerer Hjertestarterregisteret (live API), ', { size: 18 }),
    tr('GeoNorge sine OGC WFS-tenester og PostGIS-romleg søk — alt rendra direkte i nettleseren."', { size: 18 }),
  ]));

  C.push(para([], { spacing: { after: 120 } }));

  // 3 demoer
  C.push(para([tr('🖱️ Tre demo-scenarier', { bold: true, size: 22, color: ACCENT })]));

  const demos = [
    {
      title: 'Demo 1 — Finn nærmaste AED',
      knapp: 'Trykk "❤️ Finn nærmaste åpne AED"',
      vis: 'OSRM ruter på gangveg, raud stipla linje + avstand + estimert gåtid',
      seier: 'Bygd inn i appen, fungerer som ein vanleg navigator — men berre dei som er åpne 24/7 vert vurderte.',
    },
    {
      title: 'Demo 2 — Klikk for PostGIS-spørjing',
      knapp: 'Trykk "📍 Aktiver PostGIS-klikk", klikk i kartet',
      vis: 'Markør + sirkel + AED-ar i radius utheva med kvit kant, sortert liste i sidepanel',
      seier: 'Klienten sender koordinatar til Supabase, som køyrer ST_DWithin server-side i PostGIS.',
    },
    {
      title: 'Demo 3 — Klikk på AED for detaljar',
      knapp: 'Klikk på ein grøn (åpen) eller raud (stengt) markør',
      vis: 'Popup med adresse, etasje, beskrivelse, tilgang, åpningstider og serienummer — live frå API.',
      seier: 'All informasjon kjem direkte frå Hjertestarterregisteret. Grøn = åpen, raud = stengt.',
    },
  ];

  demos.forEach(d => {
    C.push(new Table({
      width: { size: 9360, type: WidthType.DXA },
      columnWidths: [9360],
      rows: [new TableRow({ children: [
        cell([
          para([tr(d.title, { bold: true, size: 20, color: DARK })]),
          para([tr('▸ Klikk: ', { bold: true, size: 16, color: MUTED }), tr(d.knapp, { size: 16 })]),
          para([tr('▸ Brukaren ser: ', { bold: true, size: 16, color: MUTED }), tr(d.vis, { size: 16 })]),
          para([tr('▸ Du seier: ', { bold: true, size: 16, color: MUTED }), tr(d.seier, { size: 16, italics: true })]),
        ], { shading: LIGHTBG, padTop: 80, padBot: 80 }),
      ]})],
    }));
    C.push(para([], { spacing: { after: 40 } }));
  });

  // Vanlege spørsmål
  C.push(para([], { spacing: { after: 60 } }));
  C.push(para([tr('❓ Spørsmål du sannsynlegvis får', { bold: true, size: 22, color: ACCENT })]));
  [
    ['Kor mange AED-ar viser kartet?', 'Alle dei publikumstilgjengelege i regionen kjem live frå Hjertestarterregisteret. Talet kan variere med kva som er åpent på det tidspunktet du opnar kartet.'],
    ['Kva er forskjellen på grøn og raud markør?', 'Grøn = åpen for publikum no. Raud = stengt eller utanfor opningstid. Når du finn nærmaste AED, vurderer appen berre dei grøne.'],
    ['Kor kjem dataene frå?', 'Fire kjelder: (1) Hjertestarterregisteret via OAuth 2.0 API, (2) GeoNorge si OGC WFS for brannstasjonar, (3) lokale beredskapsdata (sjukehus, AMK, politi), (4) Supabase PostGIS for romleg søk.'],
    ['Korleis fungerer "Finn nærmaste AED"?', 'Vi tek din GPS-posisjon, finn alle åpne AED-ar, sorterer på Haversine-avstand, og spør OSRM (open routing) om gangrute til den næraste.'],
    ['Kva er PostGIS, og kvifor brukar de det?', 'PostGIS er ein utviding av PostgreSQL for romleg data. Vi brukar funksjonen ST_DWithin server-side — mykje raskare enn å filtrere alle AED-ar i nettlesaren.'],
    ['Kan dette skalerast til heile Noreg?', 'Ja — same pipeline. Berre datasettet treng å utvidast (bytte ut kommunegrense og hente fleire AED-ar via same API).'],
    ['Kvifor laga de dette?', 'Skuleprosjekt i IS-218 ved UiA, knytt til Totalforsvaret 2025–2026 — sivil beredskap krev god informasjonstilgang.'],
  ].forEach(([q, a]) => {
    C.push(para([
      tr('Q: ', { bold: true, color: ACCENT, size: 16 }),
      tr(q, { bold: true, size: 16 }),
    ]));
    C.push(para([
      tr('A: ', { bold: true, color: MUTED, size: 16 }),
      tr(a, { size: 16 }),
    ], { spacing: { after: 80 } }));
  });

  // Backup
  C.push(para([], { spacing: { after: 60 } }));
  C.push(para([tr('🚨 Hvis demo feilar', { bold: true, size: 20, color: ALERT })]));
  C.push(para([tr('1. Sjekk at `python run.py` køyrer (terminal). 2. Reload http://localhost:3000. 3. Worst case: vis YouTube-demo (qr på handout) eller PDF av semesterrapport.', { size: 16 })]));

  return new Document({
    styles: { default: { document: { run: { font: 'Calibri', size: 18 } } } },
    sections: [{
      properties: { page: {
        size: { width: 11906, height: 16838 },
        margin: { top: 720, right: 720, bottom: 720, left: 720 },
      }},
      children: C,
    }],
  });
}

// ────────────────────────────────────────────────────────────────────────────
// BUILD
// ────────────────────────────────────────────────────────────────────────────
async function main() {
  const items = [
    ['expo_handout.docx',   buildHandout()],
    ['expo_poster.docx',    buildPoster()],
    ['expo_demo_kort.docx', buildDemoCard()],
  ];
  for (const [name, doc] of items) {
    const buf = await Packer.toBuffer(doc);
    fs.writeFileSync(path.join(ROOT, name), buf);
    console.log(`OK ${name} (${buf.length} bytes)`);
  }
}
main().catch(e => { console.error(e); process.exit(1); });
