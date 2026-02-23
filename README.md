# Interaktivt nettfart - Python Flask + MVC Architecture

## Prosjektoversikt

**InteractiveMap** er eit responsivt Python-basert nettfartprogram som kombinerer statiske geografiske data, eksterne OGC API-ar, og valgfri romleg databasetjenester (PostGIS/Supabase) til ein einaste interaktiv kartografisk opplevnad. Bygd med **Flask**, **Folium**, og **GeoPandas**, demonstrerer denne applikasjonen beste praksis for å handtera geografiske dataflolar, koordinatsystemtransformasjonar, og interaktive kartvisualiseringar ved bruk av **MVC (Model-View-Controller)** arkitektur.

### TLDR
Eit Python Flask nettfart som lastar geografiske data frå fleire kjelder (GeoJSON, OGC API-ar, PostGIS-databasar), visualiserer dei interaktivt med Folium, støttar romleg filtrering etter avstand ved bruk av Haversine-formelen, og skil konsekvent konsern med MVC-arkitektur.

---

## Funksjonar

- ✅ **Flerkildedata-lasting**: GeoJSON-data + OGC API-ar + Supabase PostGIS-støtte
- ✅ **Interaktiv kartgjengiving**: Folium-basert interaktivt kart med Leaflet-backend
- ✅ **Romleg søk**: Filtrer funksjonar innanfor spesifisert avstandsradius
- ✅ **OGC API-integrasjon**: Støtte for WFS og andre OGC-kompatible tenester
- ✅ **Datadriven stilisering**: Tilpass laginaut basert på eigenskapar
- ✅ **MVC-arkitektur**: Ren separasjon av modellar, syn og kontrollsystemar
- ✅ **Responsivt design**: Fungerer på skrivebord og mobilnettlesarar
- ✅ **REST API**: JSON-endepoint for søk og datakjelder

---

## Teknisk stabel

| Komponent | Versjon | Formål |
|-----------|---------|--------|
| **Python** | 3.11+ | Programmeringsspråk |
| **Flask** | 3.0.0 | Nettverkrammeverk |
| **Folium** | 0.14.0 | Interaktiv kartbibliotek (Leaflet-omslag) |
| **GeoPandas** | 0.14.0 | Geografisk dataanalyse |
| **Requests** | 2.31.0 | HTTP API-anrop |
| **Geopy** | 2.4.0 | Geokodering og avstandsutrekningar |

---

## Datakatalog

| Datasett | Kjelde | Format | Prosessering |
|---------|--------|--------|-----------|
| Norske byar og merknader | Innebygd GeoJSON | Point/LineString-funksjonar | Manuelt kuratert frå OSM-data |
| GeoNorge API | Ekstern WFS/WMS | GeoJSON (via henting) | Sanntids HTTP-førespurnader til OGC-tenester |
| PostGIS-database | Supabase | JSON (via API) | SQL-romleg spørjingar med PostGIS-funksjonar |
| OpenStreetMap basiskart | Mapnik-flisematter | XYZ rastermatter | Levert via CDN |

---

## Arkitekturoveverikt

```
┌──────────────────────────────────┐
│      Web Browser (HTML/JS)       │
│    http://localhost:5000         │
└────────────────┬─────────────────┘
                 │
         ┌───────▼────────┐
         │  Flask Routes  │
         │  (app/__init__.py)
         └───────┬────────┘
                 │
    ┌────────────┼────────────┐
    │            │            │
┌───▼──────┐ ┌──▼─────────┐ ┌▼──────────┐
│AppCtrlr  │ │ MapView    │ │ MapModel  │
│(Logic)   │ │(Folium)    │ │(State)    │
└───┬──────┘ └──┬─────────┘ └┬──────────┘
    │           │            │
    └───────────┼────────────┘
                │
    ┌───────────▼────────────────┐
    │        DataModel           │
    │  (Data fetching & spatial  │
    │      query operations)     │
    └───────────┬────────────────┘
                │
    ┌───────────┼───────────┬──────────┐
    │           │           │          │
 ┌──▼──┐  ┌─────▼───┐  ┌────▼────┐  ┌▼─────┐
 │JSON │  │OGC API  │  │Supabase │  │Distance
 │Data │  │(WFS)    │  │(PostGIS)│  │Calc
 └─────┘  └─────────┘  └─────────┘  └──────┘
```

**MVC-komponentar:**

**Modellar** (`app/models/`)
- `DataModel.py`: Datahenting frå fleire kilder, romleg operasjonar (Haversine-avstand)
- `MapModel.py`: Karttilstand, lagstyre, viewport-kontroll

**Syn** (`app/views/`)
- `MapView.py`: Gjengivar interaktive Folium/Leaflet-kart, lagvisualisering

**Kontrollsystemar** (`app/controllers/`)
- `AppController.py`: Orkesterar initialisering, hendingehandtering, datalastingslogikk

**Flask-app** (`app/__init__.py`)
- REST API-endepoint for søk, OGC API-henting, karteksport

---

## Installasjon og oppsett

### Føresetnadar
- **Python 3.11+** (last ned frå https://www.python.org/)
- **pip** (inkludert med Python)
- **Visual Studio Code** (valfritt men tilrådd)
- Moderni nettlesar (Chrome, Firefox, Safari, Edge)

**⚠️ Merk:** Prosjektet er no berre konfigurert og testt på Mac. Det er ikkje i ein ønskeleg tilstand.

### Rask start - Mac

1. **Klon og gå inn i mappa**
```bash
git clone https://github.com/KristianEspevikUIA/IS218GR8.git
cd IS218GR8
```

2. **Opprett virtuelt miljø** (tilrådd)
```bash
python3 -m venv venv
source venv/bin/activate
```

3. **Installer avhengigheiter**
```bash
pip install -r requirements.txt
```

4. **Køyr serveren**
```bash
python3 run.py
```

5. **Opne i nettlesar**
Naviger til `http://localhost:5000`

**Med VS Code (anbefalt):**
- Opne prosjektet: `code .`
- Installer Python-utvidinga (Ctrl+Shift+X)
- Køyr med Cmd+Shift+B
- Vel "Run Flask Web Map"

---

## VS Code hurtigreferanse

### Tastatursnarvegar

| Handling | Mac |
|--------|-----|
| **Køyr Flask-server** | Cmd+Shift+B |
| **Debug Flask (F5)** | F5 |
| **Opne terminal** | Ctrl+` |
| **Køyr oppgåve** | Cmd+Shift+B |

### Steg-for-steg: Kjøring frå VS Code

**1. Opne arbeidsflata**
```
File > Open Folder > IS218GR8
```

**2. Installer Python-utvidinga** (viss ikkje allereie installert)
```
Cmd+Shift+X > Søk "Python" > Installer
```

**3. Vel Python-tolkar** (valfritt men tilrådd)
```
Cmd+Shift+P > "Python: Select Interpreter" > Vel 3.11 eller høgare
```

**4. Start serveren med Cmd+Shift+B**
```
Cmd+Shift+B
↓
Vel "Run Flask Web Map"
↓
Avhengigheiter installera automatisk
↓
Server startar på http://localhost:5000
↓
Flask skriver ut: "Running on http://127.0.0.1:5000"
```

**5. Opne nettlesar og naviger til**
```
http://localhost:5000
```

### Debugging i VS Code

Trykk **F5** for å starta Flask med feilsøkjar:
```
F5
↓
Server startar i feilsøkingsmodus
↓
Set bruddpunkt ved å klikka på venstre marg i kode
↓
Feilsøkjar stoppar på bruddpunkt når koden køyrer
↓
Steg gjennom kode med F10 (steg over) eller F11 (steg inn)
```

---

## Bruksrettleiing

### Grunnleggjande kartinteraksjon
- **Flytt**: Klikk og drag kartet
- **Zoom**: Rullehjulet eller bruk zoom-kontrollane
- **Vis detaljar**: Klikk på ein funksjon for å sjå popup

### Romleg søk
1. **Klikk på kartet** for å setja søksenterpunktet
2. Skriv inn ein **radius (km)** i høgre panel
3. Klikk **"Search by Distance"**
4. Resultat lyser opp i raudt med søkradiusvisualisering

### OGC API-integrasjon
Kall `/api/ogc-api`-endepoint:
```bash
curl -X POST http://localhost:5000/api/ogc-api \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://www.geonorge.no/wfs",
    "params": {
      "service": "WFS",
      "request": "GetFeature",
      "typeName": "municipality"
    }
  }'
```

### Romleg søk via API
```bash
curl -X POST http://localhost:5000/api/search \
  -H "Content-Type: application/json" \
  -d '{
    "lat": 59.9139,
    "lng": 10.7339,
    "radius_km": 50
  }'
```

---

## Prosjektstruktur

```
IS218GR8/
├── app/
│   ├── __init__.py                # Flask-appinitialisering & ruter
│   ├── models/
│   │   ├── __init__.py
│   │   ├── data_model.py          # Datahenting & romleg operasjonar
│   │   └── map_model.py           # Karttilstandsstyring
│   ├── views/
│   │   ├── __init__.py
│   │   └── map_view.py            # Folium-kartgjengiving
│   └── controllers/
│       ├── __init__.py
│       └── app_controller.py      # Applikasjon-orkestrasjon & logikk
├── templates/
│   └── index.html                 # Jinja2-mal for web-UI
├── .vscode/
│   ├── tasks.json                 # VS Code byggjeopgåver (kryssplattform)
│   └── launch.json                # VS Code Python-feilsøkjar-konfigurasjon
├── run.py                         # Flask startpunkt
├── requirements.txt               # Python-avhengigheiter
├── .gitignore                     # Git-ignoreradarregler
├── README.md                      # Denne fila
└── LICENSE                        # MIT-lisens
```

---

## API-endepoint

### GET `/`
Gjengivar hovudfartinterface med datakatalog

### POST `/api/search`
Romleg søk etter avstand
- **Førespurnad**: `{"lat": float, "lng": float, "radius_km": float}`
- **Svar**: `{"status": "success", "count": int, "features": [], "search_point": {}, "radius_km": float}`

### POST `/api/ogc-api`
Hent data frå OGC API-ar
- **Førespurnad**: `{"url": "string", "params": {}}`
- **Svar**: `{"status": "success", "message": "string"}`

### GET `/api/data-sources`
List registrerte datakilder
- **Svar**: `[{"id": "string", "name": "string", "type": "string", "visible": bool}]`

### GET `/api/export-map`
Eksporter kart som HTML-fil
- **Svar**: `{"status": "success", "filepath": "string", "message": "string"}`

---

## Konfigurasjon

### Miljøvariabler (valfritt)
Opprett `.env`-fil i `python_app/`-mappa:
```env
FLASK_ENV=development
FLASK_DEBUG=True
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key
```

Last inn med:
```python
from dotenv import load_dotenv
load_dotenv()
```

---

## Utviding av applikasjonen

### Legg til ein nye datakjelde
```python
# I AppController.setup_data_sources()
self.data_model.register_source('my-source', {
    'type': 'ogc_api',
    'name': 'My OGC Service'
})
```

### Legg til tilpassa stilisering
```python
# I MapView.add_geojson_layer()
self.map_view.add_geojson_layer(
    layer_id='custom',
    features=features,
    color='#ff0000'  # Red
)
```

### Spørr PostGIS
```python
# I AppController
results = self.data_model.query_supabase(
    supabase_client,
    'places',
    filters={'city': 'Oslo'}
)
```

---

## Nettlesarstøtte

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

---

## Refleksjon og forbetringer

### Nåværande styrkar
- Ren MVC-arkitektur mogeld testabilitet og vedlikehaldslyst
- Haversine-formelen gir nøyaktig geodetisk avstandsutrekningar
- Folium genererer interaktive kart utan kompleks oppsett
- Responsivt design fungerer på tversplattform
- REST API tillater eksterne integrasjonar

### Område for forbetring

1. **Autentisering & sikkerheit**: No har ingen autentiseringslag. For produksjon, legg til Flask-Login og sikra API-endepoint med JWT-token. Supabase API-nøklar må aldri eksporneras i klientkode.

2. **Prestasjonar**: Store funksjonsamlingar (>10.000) kan forårsaka seint gjengifing. Implementer serverside-klynging, romleg indeksering, eller flisbasert gjengiving ved bruk av MapLibre GL i stad for Folium.

3. **Advanced Spatial Analysis**: Nåværande avstandsfiltrering er grunnleggjande. Forbetra med polygon-skjæring, buffer-operasjonar, og topologi-analyse ved bruk av Shapely eller PostGIS SQL-spørjingar direkte.

4. **Feilhandtering & logaritme**: Legg til omfattande prøva-fang-blokker, førespurnadvalidering, og logaritme til fil for feilsøking av produksjonsproblem.

5. **Testande & CI/CD**: Implementer einingsetest for modellar, integrasjonstestar for kontrollsystemar, og automatisert distribusjonspipeline ved bruk av GitHub Actions.

---

## Lisens

MIT-lisens - Sjå [LICENSE](LICENSE)-fila for detaljar

---

## Bidragarar

- **Kristian Espevik** - MVC-arkitektur implementering med Python Flask & Folium
- **Victor Ziadpour** - OGC API & Supabase integrasjon
- **Nicolai Stephansen** - Datahenting og spørjingar
- **Brage Kristoffersen** - Frontend og interaksjon
- **Amged Mohammed** - Testing og dokumentasjon
- **Youcef Youcef** - Kartvisualisering og design

---

## Kontakt og støtte

For problema, spørsmål eller bidrag, opne ein issue på [GitHub-arkivet](https://github.com/KristianEspevikUIA/IS218GR8).

---

**Sist oppdatert**: Februar 23, 2026
**Språk**: Python 3.11+ med Flask 3.0.0
**Status**: Ikkje i ønskjeleg tilstand - fungerer berre på Mac
