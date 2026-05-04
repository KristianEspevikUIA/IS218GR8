Beredskapskart Kristiansand, interaktivt webkart

TLDR

Et interaktivt beredskapskart for Kristiansand-regionen knyttet til Totalforsvaret 2025–2026. Kartet viser hjertestartere (AED), brannstasjoner, sykehus, nødnummer-sentraler og andre beredskapsressurser samlet på ett kart, med sanntidsdata fra flere kilder. Prosjektet kombinerer lokal GeoJSON, eksternt API (Hjertestarterregisteret), OGC WFS (GeoNorge brannstasjoner) og Supabase PostGIS med romlig filtrering, rutenavigering og PostGIS-baserte spørringer.

Live: http://localhost:3000

Demo

https://youtu.be/Ackwl4m9i5A

⸻

Funksjoner

* 263 AED-er fra Hjertestarterregister-API (grønn = åpen, rød = stengt)
* Brannstasjoner fra GeoNorge (OGC WFS, GML)
* 10+ beredskapsressurser (sykehus, politi, Røde Kors osv.)
* Rutenavigering til nærmeste åpne AED (OSRM)
* PostGIS-spørring med ST_DWithin
* Detaljerte popups med all info
* Romlig søk via kartklikk
* Dynamisk kart (Leaflet.js)
* MVC-arkitektur (Flask)
* Supabase PostGIS-integrasjon
* Responsivt design

⸻

Teknisk stabel

* Python 3.11+
* Flask
* Leaflet.js
* MarkerCluster
* Supabase PostGIS
* OSRM
* GeoNorge WFS
* Hjertestarterregister API
* OpenStreetMap

⸻

Hurtigstart

1. Klon repo

git clone https://github.com/KristianEspevikUIA/IS218GR8.git
cd IS218GR8

2. Opprett virtual environment

py -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt

3. Opprett .env

SUPABASE_URL=https://<prosjekt>.supabase.co
SUPABASE_ANON_KEY=<din-nøkkel>
HJERTESTARTERREGISTER_CLIENT_ID=<din-id>
HJERTESTARTERREGISTER_CLIENT_SECRET=<din-hemmelighet>

4. Start app

py run.py

Åpne i nettleser:
http://localhost:3000

⸻

Kartet

Farger

* 🟢 Grønn: AED åpen
* 🔴 Rød: AED stengt
* 🟠 Oransje: Brannstasjon
* 🔵 Blå: Beredskapsressurs
* 🟢 Teal: Supabase-sted

Funksjon

Klikk på en AED for:

* Adresse
* Etasje
* Åpningstider
* Serienummer

⸻

Arkitektur

Frontend (Leaflet.js) henter GeoJSON fra Flask API.

Backend:

* Flask (MVC)
* AppController styrer dataflyt

Datakilder:

* GeoJSON (lokal)
* GeoNorge (WFS)
* Hjertestarterregister (API)
* Supabase (PostGIS)

⸻

Refleksjon

* GML fra OGC WFS er mer komplisert enn JSON
* PostGIS (ST_DWithin) er raskere enn Haversine
* Mangler autentisering (bør legges til)
* Kan få ytelsesproblemer ved store datasett
* Offline-støtte bør implementeres

⸻

Bidragsytere

* Kristian Espevik
* Victor Ziadpour
* Nicolai Stephansen
* Brage Kristoffersen
* Amged Mohammed
* Youcef Youcef

⸻

Lisens

MIT

⸻

Oppgaver (kort)

* Notebook med romlig analyse (GeoPandas, Rasterio)
* PostGIS-klikk i kart
* Dekningsgap-analyse og anbefalinger

⸻

Sist oppdatert: 4. mai 2026