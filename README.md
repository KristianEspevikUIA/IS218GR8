# AED Kart Kristiansand — Interaktivt webkart

### TLDR
Eit interaktivt webkart som viser alle hjertestartere (AED) i Kristiansand-regionen med sanntidsdata frå Hjertestarterregisteret. Prosjektet er knytt til **Totalforsvarets år 2025–2026** — hjertestartarar er ein kritisk del av sivilberedskapen, og rask tilgang til nærmaste *åpne* AED kan redde liv i akutte situasjonar. Kartet kombinerer lokal GeoJSON, eksternt API og Supabase PostGIS med romleg filtrering og rutenavigering.

**Live:** `http://localhost:3000`

### Demo

> *Video/GIF kjem her*

---

## Funksjonar

- **263 AED-ar** frå Hjertestarterregister API med fargekoding (grøn = åpen, raud = stengt)
- **Rutenavigering** — finn nærmaste åpne AED frå din posisjon (OSRM gangveg-ruting)
- **Detaljerte popups** — adresse, etasje, beskrivelse, tilgang, åpningstider, serienummer
- **Romleg søk** — klikk på kartet og søk innan radius
- **Dynamisk kart** — Leaflet.js hentar ferske data kvar gong sida lastast
- **MVC-arkitektur** — Flask-backend med rein separasjon av modell, syn og kontroller
- **Supabase-integrasjon** — stader og (valfritt) AED-data via PostGIS
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
| **OpenStreetMap** | CDN | Bakgrunnskart (rasterfliser) |

---

## Datakatalog

| Datasett | Kilde | Format | Bearbeiding |
|----------|-------|--------|-------------|
| Norske landemerke og byar | Lokalt kuratert frå OpenStreetMap | GeoJSON (Point, LineString) | Manuelt utvald, lagra som `norwegian_landmarks.geojson` |
| AED-hjertestartarar (263 stk) | Hjertestarterregister API v1 | JSON → GeoJSON | OAuth 2.0-autentisering, koordinattransformasjon til GeoJSON, IS_OPEN-fargekoding, Haversine-avstand frå sentrum |
| Stader (Supabase) | Supabase PostGIS (`places`-tabell) | JSON via REST | Henta med httpx, konvertert til GeoJSON-features med lat/lng |
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
| 🔵 Blå | Landemerke (lokal GeoJSON) |
| 🟢 Teal | Supabase-stad |

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
│   ├── views/
│   │   └── map_view.py          # (Legacy Folium — ikkje i bruk)
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

---

## Arkitektur

```
┌────────────────────────────────────────┐
│         Nettlesar (Leaflet.js)         │
│  Dynamisk kart — hentar /api/map/layers│
│  kvar gong sida lastast (cache: off)   │
└──────────────┬─────────────────────────┘
               │  fetch JSON
       ┌───────▼────────┐
       │  Flask Ruter    │
       │  app/__init__.py│
       └───────┬────────┘
               │
       ┌───────▼────────┐
       │ AppController   │   ← orkestrasjon
       └───┬───┬───┬────┘
           │   │   │
    ┌──────┘   │   └──────┐
    ▼          ▼          ▼
 Lokal     Supabase    Hjertestart.
 GeoJSON   REST/httpx  API (OAuth)
```

Klienten (Leaflet.js) er heilt frikopla frå backend. Alle data kjem som GeoJSON via REST.

---

## Supabase (valfritt)

Om `hjertestartere`-tabellen ikkje finst i Supabase, fallback-ar systemet automatisk til direkte API-henting.

For å aktivere Supabase-synkronisering:

1. Køyr SQL frå `supabase_schema.sql` i Supabase Dashboard → SQL Editor
2. Køyr `py sync_aeds_to_supabase.py` for å synkronisere AED-data

---

## Refleksjon

1. **Autentisering og sikkerheit:** Applikasjonen har ikkje noko brukarautentisering. Supabase anon-nøkkel og API-credentials ligg i `.env`, men for ein produksjonsversjon bør ein leggje til Flask-Login eller JWT-basert tilgangskontroll slik at sensitive endepunkt ikkje er opne.

2. **Yting ved mange markørar:** Med 263 AED-ar fungerer MarkerCluster bra, men dersom ein utvider til heile Noreg (>10 000 AED-ar) vil klientside-rendering bli treg. Ei forbetring er å implementere server-side klynging eller vektorfliser (t.d. MapLibre GL JS med Protobuf-tiles).

3. **Supabase-tabellen `hjertestartere`:** Tabellen må opprettast manuelt i Supabase Dashboard. Ideelt sett burde appen auto-migrere skjemaet ved oppstart, eller ein CI/CD-pipeline kunne køyre migrasjonen automatisk.

4. **Berre éin romleg spørjetype:** Noverande romleg filtrering brukar Haversine-avstand (sirkelradius). For meir avansert analyse kunne ein nytta PostGIS-funksjonar som `ST_Within`, `ST_Intersects` eller polygon-basert filtrering direkte i databasen.

5. **Offline-støtte og PWA:** I ein beredskapssituasjon kan internett vere nede. Ei framtidig forbetring er å cache AED-data i Service Worker / localStorage slik at kartet fungerer offline med siste kjende data.

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
