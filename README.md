# AED Kart Kristiansand — Interaktivt webkart

Sanntidskart over hjertestartere (AED) i Kristiansand-regionen. Bygd med Flask, Leaflet.js og Supabase.

**Live:** `http://localhost:3000`

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

| Komponent | Formål |
|-----------|--------|
| **Python 3.11+** | Backend |
| **Flask 3.0.0** | Nettrammeverk |
| **Leaflet.js 1.9.4** | Dynamisk kartrammeverk (klientside) |
| **MarkerCluster** | Gruppering av markørar |
| **httpx** | Supabase REST-klient |
| **OSRM** | Ruteberegning (gangveg, gratis, ingen nøkkel) |
| **Supabase PostGIS** | Stader-database |
| **Hjertestarterregister API** | AED-kjeldedata (OAuth 2.0) |

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
