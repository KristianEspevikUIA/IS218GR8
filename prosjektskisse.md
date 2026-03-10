# Prosjektskisse — Hovedprosjekt IS-218

## Problemstilling
*Korleis kan vi identifisere og visualisere sårbare område i Kristiansand med mangelfull beredskapsdekning (AED, brannstasjon, sjukehus) i eit totalforsvarsscenario, og foreslå optimale plasseringar for nye beredskapsressursar?*

## Kort prosjektbeskriving
Prosjektet byggjer vidare på beredskapskart-løysinga frå oppgåve 1–2. Vi utviklar eit romleg analysesystem som kombinerer sanntids beredskapsdata med befolkningsdata for å avdekke dekningshol — område der befolkninga ikkje har tilgang til kritiske ressursar innan akseptabel tid. Systemet bereknar tenesteområde (service areas), identifiserer risikoområde og foreslår nye plasseringar basert på romleg optimering. Resultata vert visualisert i eit interaktivt webkart med kartografiske metodar (koroplettkart, varmekart, isokronar).

## Datasett og datakjelder (4 stk — 1 avleidd)

| # | Datasett | Kjelde | Format |
|---|----------|--------|--------|
| 1 | AED-hjertestartarar (264 stk) | Hjertestarterregister API (OAuth 2.0) | JSON → PostGIS |
| 2 | Brannstasjonar | GeoNorge WFS 2.0 | GML 3.2 → GeoJSON |
| 3 | Befolkning på rutenett (250m) | SSB Befolkning på grunnkretsnivå / rutenettstatistikk | CSV + GeoJSON |
| 4 | **Dekningsgap-analyse** *(avleidd)* | Skapt via buffer, overlay og romleg aggregering | GeoJSON / PostGIS |

Datasett 4 vert produsert ved å bufre beredskapsressursar (5 min gangavstand ≈ 400m), køyre overlay (difference) mot befolka område, og aggregere til rutenett — dette gir eit nytt geografisk datasett over sårbare soner.

## Teknologi og verktøy

| Komponent | Verktøy |
|-----------|---------|
| Backend | Python 3.11, Flask 3.0 |
| Romleg database | Supabase PostGIS (ST_DWithin, ST_Buffer, ST_Intersection) |
| Frontend-kart | Leaflet.js med MarkerCluster, heatmap, isokron-lag |
| Vektoranalyse | GeoPandas (buffer, overlay, sjoin, dissolve) |
| SQL-analyse | DuckDB + PostGIS RPC-funksjonar |
| Rasteranalyse | Rasterio (DEM, slope for tilgjenge-vurdering) |
| Kartografi | Folium (koroplettkart), Matplotlib, Leaflet-choropleth |
| Datainnhenting | httpx (Supabase), requests (WFS/API), OAuth 2.0 |

## Vektoranalysar
- **Buffer**: Tenesteområde rundt kvar AED/brannstasjon (400m, 800m, 1500m)
- **Overlay (difference)**: Befolka område *utan* beredskapsdekning
- **Spatial join**: Befolkningstal per dekningssone
- **Romleg aggregering**: Risikoscore per rutenett-celle (250×250m)
- **Nærmaste-analyse**: PostGIS `ST_DWithin` for dynamiske radiussøk

## Forventa resultat
1. **Interaktivt webkart** som viser beredskapsdekning med koroplett-/varmekart over risikonivå
2. **Dekningsgap-datasett** — polygonlag over sårbare område utan tilstrekkeleg dekning
3. **Anbefalte plasseringar** for nye AED-ar basert på befolkningstettleik og dekningshol
4. **Jupyter Notebook** med fullstendig romleg analyse og visualiseringar
5. **Dashboard** der brukarar kan klikke og sjå beredskapsdekning for sitt nabolag

---
*Gruppe 8: Kristian, Victor, Nicolai, Brage, Amged, Youcef — IS-218 Vår 2026*
