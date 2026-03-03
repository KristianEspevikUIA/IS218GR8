# Beredskapskart Kristiansand — Interaktivt webkart

### TLDR
Eit interaktivt beredskapskart for Kristiansand-regionen knytt til **Totalforsvaret 2025–2026**. Kartet viser hjertestartarar (AED), brannstasjonar, sjukehus, naudnummer-sentralar og andre beredskapsressursar — samla på éit kart med sanntidsdata frå fleire kjelder. Prosjektet kombinerer lokal GeoJSON, eksternt API (Hjertestarterregisteret), OGC WFS (GeoNorge brannstasjonar) og Supabase PostGIS med romleg filtrering, rutenavigering og PostGIS-baserte spørjingar.

**Live:** `http://localhost:3000`

### Demo

> *Video/GIF kjem her*

---

## Funksjonar

- **263 AED-ar** frå Hjertestarterregister API med fargekoding (grøn = åpen, raud = stengt)
- **Brannstasjonar frå OGC WFS** — henta live frå GeoNorge (WFS 2.0, GML-parsing)
- **10+ beredskapsressursar** — sjukehus, legevakt, AMK, sivilforsvar, politi, Røde Kors, flyplass m.m.
- **Rutenavigering** — finn nærmaste åpne AED frå din posisjon (OSRM gangveg-ruting)
- **PostGIS romleg spørjing** — `ST_DWithin` for å finne AED-ar innan radius (server-side)
- **Detaljerte popups** — adresse, etasje, beskrivelse, tilgang, åpningstider, serienummer
- **Romleg søk** — klikk på kartet og søk innan radius
- **Dynamisk kart** — Leaflet.js hentar ferske data kvar gong sida lastast
- **MVC-arkitektur** — Flask-backend med rein separasjon av modell, syn og kontroller
- **Supabase-integrasjon** — stader og (valfritt) AED-data via PostGIS
- **Totalforsvar-tema** — mørkt beredskapstema med relevante datakategoriar
- **Responsivt design** — fungerer på mobil og desktop

---

## Teknisk stabel

| Komponent | Versjon | Formål |
|-----------|---------|--------|
| **Python** | 3.11+ | Backend runtime |
| **Flask** | 3.0.0 | Nettrammeverk (MVC-ruter) |
| **Leaflet.js** | 1.9.4 | Dynamisk kartrammeverk (klientside) |
| **Leaflet.markercluster** | 1.5.3 | Klyngegruppering av markørar |
| **httpx** | 0.25.2 | Supabase REST-klient (HTTP/2) |
| **requests** | 2.31.0 | HTTP-klient for OGC/API-kall |
| **geopy** | 2.4.0 | Haversine avstandsutrekningar |
| **python-dotenv** | 1.0.0 | Miljøvariabel-lasting (.env) |
| **OSRM** | Hosted | Ruteberegning gangveg (gratis, ingen nøkkel) |
| **Supabase PostGIS** | Hosted | Romleg database for stader |
| **Hjertestarterregister API** | v1 | AED-kjeldedata (OAuth 2.0) |
| **GeoNorge WFS** | 2.0.0 | Brannstasjonar (OGC WFS, GML 3.2) |
| **OpenStreetMap** | CDN | Bakgrunnskart (rasterfliser) |

---

## Datakatalog

| Datasett | Kilde | Format | Bearbeiding |
|----------|-------|--------|-------------|
| AED-hjertestartarar (263 stk) | Hjertestarterregister API v1 | JSON → GeoJSON | OAuth 2.0-autentisering, koordinattransformasjon til GeoJSON, IS_OPEN-fargekoding, Haversine-avstand frå sentrum |
| Brannstasjonar (~10 stk) | GeoNorge WFS 2.0 (`wfs.brannstasjoner`) | GML 3.2 → GeoJSON | OGC WFS GetFeature med BBOX-filter, XML/GML-parsing til GeoJSON, eigenskapar: brannstasjon, brannvesen, stasjonstype, kasernert |
| Beredskapsressursar (11 stk) | OpenStreetMap, DSB, Helse Sør-Øst, Avinor m.fl. | GeoJSON (Point, LineString) | Utvunne frå opne kjelder, kuratert og lagra som `norwegian_landmarks.geojson` — sjukehus, legevakt, AMK, politi, sivilforsvar, Røde Kors, evakueringsstad, hamn, flyplass |
| Stader (Supabase) | Supabase PostGIS (`places`-tabell) | JSON via REST | Henta med httpx, konvertert til GeoJSON-features, romleg spørjing med `ST_DWithin` |
| AED-romleg søk (PostGIS) | Supabase PostGIS (`hjertestartere`-tabell) | JSON via RPC | `nearby_hjertestartere()`-funksjon med `ST_DWithin` for server-side romleg filtrering |
| Bakgrunnskart | OpenStreetMap (Mapnik) | XYZ rasterfliser | Levert via CDN, ingen bearbeiding |

---

## Hurtigstart

### 1. Klon og installer

```bash
git clone https://github.com/KristianEspevikUIA/IS218GR8.git
cd IS218GR8
py -m venv .venv
.venv\Scripts\activate      # Windows
pip install -r requirements.txt
```

### 2. Konfigurer miljøvariablar

Opprett `.env` i prosjektmappa:

```env
SUPABASE_URL=https://<prosjekt>.supabase.co
SUPABASE_ANON_KEY=<din-nøkkel>
HJERTESTARTERREGISTER_CLIENT_ID=<din-id>
HJERTESTARTERREGISTER_CLIENT_SECRET=<din-hemmelighet>
```

### 3. Start serveren

```bash
py run.py
```

Opne `http://localhost:3000` i nettlesaren.

**Med VS Code:** Trykk `Ctrl+Shift+B` → vel «Run Flask Web Map».

---

## Kartet

### Markørfargar

| Farge | Type |
|-------|------|
| 🟢 Grøn | AED åpen (IS_OPEN = Y) |
| 🔴 Raud | AED stengt (IS_OPEN = N) |
| � Oransje | Brannstasjon (OGC WFS) |
| 🔵 Blå | Beredskapsressurs (lokal GeoJSON) |
| 🟢 Teal | Supabase-stad (PostGIS) |

### Klikk på ein AED-markør for detaljar

- Namn og adresse
- Postnummer og postområde
- Etasje
- Beskrivelse av plassering
- Tilgangsinformasjon
- Åpningstider
- Serienummer og ID
- Sist oppdatert dato

### Finn nærmaste åpne AED

1. Klikk **«❤️ Finn nærmaste åpne AED»**
2. Tillat posisjonstilgang i nettlesaren
3. Kartet viser gangveg-rute (raud stipla linje)
4. Infopanel viser avstand og estimert gåtid

> Berre *åpne* AED-ar (IS_OPEN = Y) vert vurdert.

---

## Prosjektstruktur

```
IS218GR8/
├── app/
│   ├── __init__.py              # Flask-ruter og API-endepunkt
│   ├── controllers/
│   │   └── app_controller.py    # Orkestrasjon og dataflyt
│   ├── models/
│   │   ├── data_model.py        # Supabase REST-klient (httpx)
│   │   ├── map_model.py         # Karttilstand og lag
│   │   └── hjertestarterregister_api.py  # AED API-klient (OAuth)
│   └── data/
│       └── norwegian_landmarks.geojson
├── templates/
│   └── index.html               # Leaflet.js dynamisk kart
├── run.py                       # Startpunkt (port 3000)
├── requirements.txt             # Python-avhengigheiter
├── supabase_schema.sql          # Database-skjema
├── sync_aeds_to_supabase.py     # Synk AED-data til Supabase
└── .env                         # Miljøvariablar (ikkje i git)
```

---

## API-endepunkt

### Kartdata

| Metode | Endepunkt | Skildring |
|--------|-----------|-----------|
| GET | `/` | Hovudside med kart |
| GET | `/api/map/layers` | Alle kartlag som GeoJSON |
| GET | `/api/data-sources` | Registrerte datakjelder |

### AED

| Metode | Endepunkt | Skildring |
|--------|-----------|-----------|
| GET | `/api/aeds/available` | Tilgjengelege (åpne) AED-ar |
| GET | `/api/aeds/available/count` | Tal på åpne AED-ar |

### Stader (Supabase CRUD)

| Metode | Endepunkt | Skildring |
|--------|-----------|-----------|
| GET | `/api/supabase/places` | Alle stader |
| POST | `/api/supabase/places` | Opprett stad |
| GET | `/api/supabase/places/:id` | Hent ein stad |
| PUT | `/api/supabase/places/:id` | Oppdater stad |
| DELETE | `/api/supabase/places/:id` | Slett stad |
| POST | `/api/supabase/places/nearby` | Stader innan radius |
| GET | `/api/supabase/places/city/:city` | Stader etter by |
| GET | `/api/supabase/places/category/:cat` | Stader etter kategori |

### Søk

| Metode | Endepunkt | Skildring |
|--------|-----------|-----------|
| POST | `/api/search` | Filtrer etter avstand (Haversine) |
| POST | `/api/ogc-api` | Hent data frå OGC API |
| POST | `/api/postgis/nearby-aeds` | Finn AED-ar innan radius (PostGIS `ST_DWithin`) |

---

## Arkitektur

```
┌─────────────────────────────────────────────┐
│          Nettlesar (Leaflet.js)             │
│  Dynamisk kart — hentar /api/map/layers     │
│  kvar gong sida lastast (cache: off)        │
│  Lag: AED · Brannstasjonar · Beredskap · DB │
└────────────────┬────────────────────────────┘
                 │  fetch JSON
         ┌───────▼────────┐
         │  Flask Ruter    │
         │  app/__init__.py│
         └───────┬────────┘
                 │
         ┌───────▼────────┐
         │ AppController   │   ← orkestrasjon
         └──┬──┬──┬──┬───┘
            │  │  │  │
   ┌────────┘  │  │  └────────┐
   ▼           ▼  ▼           ▼
 Lokal      GeoNorge  Supabase   Hjertestart.
 GeoJSON    WFS/GML   REST/httpx  API (OAuth)
(beredskap) (brann)   (PostGIS)   (AED-data)
```

Klienten (Leaflet.js) er heilt frikopla frå backend. Alle data kjem som GeoJSON via REST. Brannstasjonar vert henta live frå GeoNorge OGC WFS og konverterte frå GML 3.2 til GeoJSON server-side.

---

## Supabase (valfritt)

Om `hjertestartere`-tabellen ikkje finst i Supabase, fallback-ar systemet automatisk til direkte API-henting.

For å aktivere Supabase-synkronisering:

1. Køyr SQL frå `supabase_schema.sql` i Supabase Dashboard → SQL Editor
2. Køyr `py sync_aeds_to_supabase.py` for å synkronisere AED-data

---

## Refleksjon

1. **OGC WFS og GML-parsing:** Brannstasjonsdata kjem frå GeoNorge som GML 3.2 — eit XML-basert format som krev manuell parsing med `xml.etree.ElementTree`. Dette var meir krevjande enn forventa samanlikna med JSON-baserte API-ar, men viser korleis OGC-standardar fungerer i praksis. BBOX-filtrering gjer at berre relevante stasjonar vert henta.

2. **PostGIS vs. Haversine:** Opphavleg brukte vi berre Python-basert Haversine for avstandsfiltrering. No nyttar vi `ST_DWithin` i Supabase for server-side romleg spørjing — mykje meir effektivt for store datasett og korrekt for sfærisk geometri. Den PyTHon-baserte Haversine er framleis fallback.

3. **Autentisering og sikkerheit:** Applikasjonen har ikkje noko brukarautentisering. Supabase anon-nøkkel og API-credentials ligg i `.env`, men for ein produksjonsversjon bør ein leggje til Flask-Login eller JWT-basert tilgangskontroll slik at sensitive endepunkt ikkje er opne.

4. **Yting ved mange markørar:** Med 263 AED-ar + ~10 brannstasjonar + 11 beredskapsressursar fungerer MarkerCluster bra, men dersom ein utvider til heile Noreg (>10 000 AED-ar) vil klientside-rendering bli treg. Ei forbetring er å implementere server-side klynging eller vektorfliser.

5. **Offline-støtte og PWA:** I ein beredskapssituasjon kan internett vere nede. Ei framtidig forbetring er å cache AED-data i Service Worker / localStorage slik at kartet fungerer offline med siste kjende data — særleg relevant for Totalforsvar-scenariet.

---

## Bidragarar

- **Kristian Espevik** — Arkitektur, Flask, MVC
- **Victor Ziadpour** — OGC API, Supabase-integrasjon
- **Nicolai Stephansen** — Datahenting og spørjingar
- **Brage Kristoffersen** — Frontend og interaksjon
- **Amged Mohammed** — Testing og dokumentasjon
- **Youcef Youcef** — Kartvisualisering og design

---

## Lisens

MIT — sjå [LICENSE](LICENSE)

---

**Sist oppdatert:** Mars 3, 2026
