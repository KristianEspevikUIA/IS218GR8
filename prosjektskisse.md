# Prosjektskisse — Hovedprosjekt IS-218

## Problemstilling
*Hvordan kan vi identifisere og visualisere sårbare områder i Kristiansand med mangelfull beredskapsdekning (AED, brannstasjon, sykehus) i et totalforsvarsscenario, og foreslå optimale plasseringer for nye beredskapsressurser?*

## Kort prosjektbeskrivelse
Prosjektet bygger videre på beredskapskart-løsningen fra oppgave 1–2. Vi utvikler et romlig analysesystem som kombinerer sanntids beredskapsdata med befolkningsdata for å avdekke dekningshull — områder der befolkningen ikke har tilgang til kritiske ressurser innen akseptabel tid. Systemet beregner tjenesteområder (service areas), identifiserer risikoområder og foreslår nye plasseringer basert på romlig optimalisering. Resultatene visualiseres i et interaktivt webkart med kartografiske metoder (koroplettkart, varmekart, isokroner).

## Datasett og datakilder (4 stk — 1 avledet)

| # | Datasett | Kilde | Format |
|---|----------|-------|--------|
| 1 | AED-hjertestartere (264 stk) | Hjertestarterregister API (OAuth 2.0) | JSON → PostGIS |
| 2 | Brannstasjoner | GeoNorge WFS 2.0 | GML 3.2 → GeoJSON |
| 3 | Befolkning på rutenett (250m) | SSB Befolkning på grunnkretsnivå / rutenettstatistikk | CSV + GeoJSON |
| 4 | **Dekningsgap-analyse** *(avledet)* | Skapt via buffer, overlay og romlig aggregering | GeoJSON / PostGIS |

Datasett 4 produseres ved å bufre beredskapsressurser (5 min gangavstand ≈ 400m), kjøre overlay (difference) mot befolkede områder, og aggregere til rutenett — dette gir et nytt geografisk datasett over sårbare soner.

## Teknologi og verktøy

| Komponent | Verktøy |
|-----------|---------|
| Backend | Python 3.11, Flask 3.0 |
| Romlig database | Supabase PostGIS (ST_DWithin, ST_Buffer, ST_Intersection) |
| Frontend-kart | Leaflet.js med MarkerCluster, heatmap, isokron-lag |
| Vektoranalyse | GeoPandas (buffer, overlay, sjoin, dissolve) |
| SQL-analyse | DuckDB + PostGIS RPC-funksjoner |
| Rasteranalyse | Rasterio (DEM, slope for tilgjengelighetsvurdering) |
| Kartografi | Folium (koroplettkart), Matplotlib, Leaflet-choropleth |
| Datainnhenting | httpx (Supabase), requests (WFS/API), OAuth 2.0 |

## Vektoranalyser
- **Buffer**: Tjenesteområder rundt hver AED/brannstasjon (400m, 800m, 1500m)
- **Overlay (difference)**: Befolkede områder *uten* beredskapsdekning
- **Spatial join**: Befolkningstall per dekningssone
- **Romlig aggregering**: Risikoscore per rutenettcelle (250×250m)
- **Nærmeste-analyse**: PostGIS `ST_DWithin` for dynamiske radiussøk

## Forventede resultater
1. **Interaktivt webkart** som viser beredskapsdekning med koroplett-/varmekart over risikonivå
2. **Dekningsgap-datasett** — polygonlag over sårbare områder uten tilstrekkelig dekning
3. **Anbefalte plasseringer** for nye AED-er basert på befolkningstetthet og dekningshull
4. **Jupyter Notebook** med fullstendig romlig analyse og visualiseringer
5. **Dashboard** der brukere kan klikke og se beredskapsdekning for sitt nabolag

---
*Gruppe 8: Kristian, Victor, Nicolai, Brage, Amged, Youcef — IS-218 Våren 2026*

