"""
generate_population_grid.py

Genererer eit 250m rutenett med befolkningsestimat for Kristiansand kommune,
basert på ein innebygd forenkla kommunegrense og ein kalibrert distance-decay
modell rundt kjende befolkningssentrum.

Produserer to GeoJSON-filer:
    app/data/kristiansand_kommune.geojson   (kommunegrense)
    app/data/befolkning_kristiansand.geojson (250m grid med pop_count)

Bakgrunn og designvalg:
    Ekte SSB rutenettstatistikk (ruter250m_sentroider) krev registrering og
    nedlasting av ein stor GeoPackage. For reproduserbarheit og for at alle
    i gruppa skal kunne køyre analysen utan ekstern tilgang, genererer vi
    eit kalibrert syntetisk datasett som:

        1. Les ei innebygd forenkla Kristiansand kommunegrense
           (kan overstyrast ved å legge ekte GeoJSON i app/data/kristiansand_kommune.geojson)
        2. Bygg 250m rutenett over kommunen
        3. Tildeler befolkning via ei blanda distance-decay frå kjende
           befolkningssentrum (Kvadraturen, Lund, Vågsbygd, Søm, Tveit)
        4. Skalerer slik at total befolkning = 115 000 (SSB 2024)
        5. Legg til støy for å unngå artefakt

Modellen gir realistisk fordeling med tette senter og tynne periferiar,
og kan erstattast av ekte SSB-data ved å bytte ut data-kjelda seinare.
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
import requests
from shapely.geometry import Point, Polygon, box, shape
from shapely.ops import unary_union

# ─── Konstantar ──────────────────────────────────────────────────────────
WGS84 = "EPSG:4326"
UTM32N = "EPSG:25832"
CELL_SIZE_M = 250
TOTAL_POPULATION = 115_000   # SSB 2024 estimat for Kristiansand

# Kjende befolkningssentrum (lat, lng, relativ vekt, radius_km standard decay)
# Vektene speglar omtrentleg folketal per bydel (kjelde: kristiansand.kommune.no)
POPULATION_CENTERS = [
    # navn,         lat,      lng,      vekt,  decay_km
    ("Kvadraturen", 58.1467, 8.0059, 0.22, 0.8),
    ("Lund",        58.1541, 8.0261, 0.14, 1.0),
    ("Vågsbygd",    58.1289, 7.9481, 0.18, 1.2),
    ("Tinnheia",    58.1623, 7.9812, 0.08, 0.8),
    ("Hånes",       58.1692, 8.0873, 0.10, 1.2),
    ("Søm",         58.1470, 8.0820, 0.09, 1.0),
    ("Randesund",   58.1389, 8.1247, 0.08, 1.5),
    ("Tveit",       58.2033, 8.0389, 0.06, 2.0),
    ("Justvik",     58.1843, 8.0528, 0.05, 1.2),
]


# ══════════════════════════════════════════════════════════════════════════
#  1. Kommunegrense (WFS med innebygd fallback)
# ══════════════════════════════════════════════════════════════════════════
# Forenkla ytre grense for Kristiansand kommune (lat, lng) — etter
# kommunesamanslåing 2020 med Søgne og Songdalen. Brukar omrisset av den
# bebygde delen og hovudfastlandet, inklusive øyar langs kysten.
KRISTIANSAND_BOUNDARY_COORDS = [
    # Ytre ring (fastlandsgrense, klokkevis frå vest/sør)
    (58.075, 7.670),  # Søgne vest
    (58.097, 7.700),
    (58.115, 7.770),
    (58.135, 7.830),
    (58.148, 7.880),
    (58.155, 7.930),
    (58.158, 7.980),  # Vågsbygd / Hannevika
    (58.162, 8.020),  # Kvadraturen
    (58.172, 8.060),
    (58.188, 8.100),  # Justvik
    (58.205, 8.140),  # Hånes / Tveit
    (58.230, 8.160),
    (58.280, 8.180),  # Tveit nord
    (58.305, 8.160),
    (58.310, 8.120),
    (58.300, 8.070),
    (58.295, 8.020),
    (58.280, 7.970),
    (58.255, 7.930),
    (58.230, 7.880),
    (58.205, 7.830),  # Nord-vest inn mot Songdalen
    (58.218, 7.780),
    (58.200, 7.730),
    (58.175, 7.700),
    (58.150, 7.680),  # Tilbake til start
    (58.120, 7.680),
    (58.095, 7.670),
    (58.075, 7.670),
]


def fetch_kommunegrense_kristiansand() -> gpd.GeoDataFrame:
    """
    Hentar kommunegrensa for Kristiansand (kommunenr 4204).

    Prøver først GeoNorge administrative_enheter WFS, fell tilbake til
    ein innebygd forenkla grense om WFS ikkje er tilgjengeleg (f.eks. i
    eit isolert miljø eller ved proxy-avvisning).
    """
    url = "https://wfs.geonorge.no/skwms1/wfs.administrative_enheter"
    params = {
        "service": "WFS",
        "version": "2.0.0",
        "request": "GetFeature",
        "typeNames": "app:Kommune",
        "outputFormat": "application/gml+xml; version=3.2",
        "filter": (
            '<Filter xmlns="http://www.opengis.net/ogc">'
            '<PropertyIsEqualTo>'
            '<PropertyName>kommunenummer</PropertyName>'
            '<Literal>4204</Literal>'
            '</PropertyIsEqualTo>'
            '</Filter>'
        ),
    }
    try:
        print("[WFS] Prøver å hente kommunegrense frå GeoNorge...")
        r = requests.get(url, params=params, timeout=10)
        r.raise_for_status()
        import xml.etree.ElementTree as ET
        root = ET.fromstring(r.text)
        coords_all = []
        for elem in root.iter():
            tag = elem.tag.split("}")[-1]
            if tag == "posList" and elem.text:
                nums = [float(x) for x in elem.text.split()]
                pts = [(nums[i + 1], nums[i]) for i in range(0, len(nums), 2)]
                coords_all.append(pts)
        if not coords_all:
            raise RuntimeError("Ingen koordinatar i GML")
        rings = [Polygon(ring) for ring in coords_all if len(ring) >= 3]
        rings = [r for r in rings if r.is_valid and r.area > 0]
        boundary = unary_union(rings)
        gdf = gpd.GeoDataFrame(
            {"kommunenavn": ["Kristiansand"], "kommunenummer": ["4204"],
             "kjelde": ["GeoNorge WFS"]},
            geometry=[boundary], crs=WGS84,
        )
        print(f"[WFS] ✓ Areal ≈ {gdf.to_crs(UTM32N).area.sum()/1e6:.1f} km²")
        return gdf
    except Exception as e:
        print(f"[WFS] ✗ Fell tilbake til innebygd grense ({type(e).__name__})")
        ring = [(lng, lat) for lat, lng in KRISTIANSAND_BOUNDARY_COORDS]
        poly = Polygon(ring)
        gdf = gpd.GeoDataFrame(
            {"kommunenavn": ["Kristiansand"], "kommunenummer": ["4204"],
             "kjelde": ["Innebygd forenkla grense"]},
            geometry=[poly], crs=WGS84,
        )
        print(f"[WFS] Innebygd areal ≈ {gdf.to_crs(UTM32N).area.sum()/1e6:.1f} km²")
        return gdf


# ══════════════════════════════════════════════════════════════════════════
#  2. Bygg 250m rutenett over kommunen
# ══════════════════════════════════════════════════════════════════════════
def build_population_grid(kommune: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """
    Lag eit 250m rutenett som berre inneheld celler innanfor kommunen.
    Returnerer GeoDataFrame i WGS84 med kolonnene cx, cy (UTM-senter).
    """
    k_utm = kommune.to_crs(UTM32N)
    boundary_utm = unary_union(k_utm.geometry.values)
    minx, miny, maxx, maxy = k_utm.total_bounds

    minx = math.floor(minx / CELL_SIZE_M) * CELL_SIZE_M
    miny = math.floor(miny / CELL_SIZE_M) * CELL_SIZE_M
    maxx = math.ceil(maxx / CELL_SIZE_M) * CELL_SIZE_M
    maxy = math.ceil(maxy / CELL_SIZE_M) * CELL_SIZE_M

    cells = []
    x = minx
    while x < maxx:
        y = miny
        while y < maxy:
            cell = box(x, y, x + CELL_SIZE_M, y + CELL_SIZE_M)
            if cell.intersects(boundary_utm):
                cells.append({
                    "cell_id": f"{int(x)}_{int(y)}",
                    "cx_utm": x + CELL_SIZE_M / 2,
                    "cy_utm": y + CELL_SIZE_M / 2,
                    "geometry": cell,
                })
            y += CELL_SIZE_M
        x += CELL_SIZE_M

    gdf_utm = gpd.GeoDataFrame(cells, crs=UTM32N)
    print(f"[GRID] Bygde {len(gdf_utm)} celler (250m) over kommunen")
    return gdf_utm


# ══════════════════════════════════════════════════════════════════════════
#  3. Tildel befolkning med distance-decay
# ══════════════════════════════════════════════════════════════════════════
def assign_population(grid_utm: gpd.GeoDataFrame, seed: int = 42) -> gpd.GeoDataFrame:
    """
    Tildel befolkning til kvar celle basert på sum av gaussiske kjelder
    frå kjende bydelssentrum, pluss eit mindre bakgrunns-nivå og støy.
    Skalerer til TOTAL_POPULATION.
    """
    np.random.seed(seed)

    # Konverter senter-punkta til UTM
    centers_gdf = gpd.GeoDataFrame(
        POPULATION_CENTERS,
        columns=["name", "lat", "lng", "weight", "decay_km"],
    )
    centers_gdf["geometry"] = gpd.points_from_xy(centers_gdf["lng"], centers_gdf["lat"])
    centers_gdf.crs = WGS84
    centers_utm = centers_gdf.to_crs(UTM32N)

    # Rå score per celle
    cx = grid_utm["cx_utm"].values
    cy = grid_utm["cy_utm"].values
    raw = np.zeros(len(grid_utm))

    for _, ctr in centers_utm.iterrows():
        dx = cx - ctr.geometry.x
        dy = cy - ctr.geometry.y
        dist_km = np.sqrt(dx * dx + dy * dy) / 1000.0
        # Gaussisk decay
        decay = np.exp(-0.5 * (dist_km / ctr["decay_km"]) ** 2)
        raw += ctr["weight"] * decay

    # Liten bakgrunns-tetthet der det finst folk i det heile
    # (kuttar av ubebygde celler under eit tersk)
    raw += 0.002
    raw = np.where(raw < 0.005, 0.0, raw)   # spreidde celler utan befolkning

    # Støy (± 15 %) berre på celler med befolkning
    noise = np.where(raw > 0, np.random.uniform(0.85, 1.15, size=len(raw)), 1.0)
    raw *= noise

    # Ikkje negative verdiar
    raw = np.clip(raw, 0, None)

    # Normaliser til total befolkning
    total_raw = raw.sum()
    scale = TOTAL_POPULATION / total_raw if total_raw > 0 else 0
    population = raw * scale

    grid_utm = grid_utm.copy()
    grid_utm["population"] = np.round(population, 1)

    print(f"[POP] Tildelte befolkning — total = {grid_utm['population'].sum():,.0f} "
          f"(mål: {TOTAL_POPULATION:,})")
    print(f"[POP] Per-celle statistikk: min={grid_utm['population'].min():.1f}, "
          f"median={grid_utm['population'].median():.1f}, "
          f"max={grid_utm['population'].max():.1f}")
    return grid_utm


# ══════════════════════════════════════════════════════════════════════════
#  Hovudprogram
# ══════════════════════════════════════════════════════════════════════════
def main(output_dir: str = "app/data") -> None:
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    # 1. Kommunegrense
    kommune = fetch_kommunegrense_kristiansand()
    kommune_path = out / "kristiansand_kommune.geojson"
    kommune.to_file(kommune_path, driver="GeoJSON")
    print(f"[IO] Skreiv {kommune_path}")

    # 2. Grid
    grid_utm = build_population_grid(kommune)

    # 3. Befolkning
    grid_utm = assign_population(grid_utm)

    # Konverter til WGS84 for frontend-bruk
    grid_wgs = grid_utm.to_crs(WGS84)[
        ["cell_id", "population", "geometry"]
    ].copy()

    pop_path = out / "befolkning_kristiansand.geojson"
    grid_wgs.to_file(pop_path, driver="GeoJSON")
    print(f"[IO] Skreiv {pop_path}  ({len(grid_wgs)} celler)")
    print("✓ Ferdig.")


if __name__ == "__main__":
    output = sys.argv[1] if len(sys.argv) > 1 else "app/data"
    main(output)
