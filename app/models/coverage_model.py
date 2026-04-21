"""
CoverageModel.py — Semesterprosjekt (Oppgave 4)

Dekningsgap-analyse for beredskapsressurser i Kristiansand.

Kjernefunksjonalitet:
    - service_areas(...)       : Buffer (gangavstand) rundt AED/brannstasjon/sjukehus
    - coverage_gaps(...)       : Befolka område som ligg UTANFOR service areas (difference)
    - risk_grid(...)           : 250m rutenett med populasjons-veka risikoscore
    - recommend_aed_sites(...) : Grådig algoritme som foreslår N nye AED-plasseringar
                                 som maksimerer befolkningsdekning innanfor 400m

Heile modulen nyttar GeoPandas + Shapely og projiserer til UTM 32N (EPSG:25832)
for korrekte meter-baserte avstandsutrekningar.
"""
from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import geopandas as gpd
import numpy as np
import pandas as pd
from shapely.geometry import MultiPolygon, Point, Polygon, box, mapping, shape
from shapely.ops import unary_union

# ─── Konstantar ──────────────────────────────────────────────────────────
WGS84 = "EPSG:4326"
UTM32N = "EPSG:25832"          # Norsk standardprojeksjon (meter)

# Standard service-radiusar (meter, gangveg)
DEFAULT_RADII = {
    "aed":             400,    # 4-5 min løpe/gange for å hente hjertestartar
    "brannstasjon":    1500,   # 3-4 min utrykning til område
    "sjukehus":        3000,   # 5-7 min kjøretid
    "legevakt":        2000,
    "amk":             5000,   # kan dekke heile byen
    "politi":          2000,
    "sivilforsvar":    3000,
}

# Risikoscore-parameter
DEFAULT_CELL_SIZE_M = 250      # Grid-oppløysing
CRITICAL_RADIUS_M   = 400      # AED må finnast innanfor denne radiusen

# ══════════════════════════════════════════════════════════════════════════
#  Hjelpefunksjonar: I/O
# ══════════════════════════════════════════════════════════════════════════
def _load_geojson(path: str | Path) -> gpd.GeoDataFrame:
    """Last GeoJSON frå fil til GeoDataFrame (WGS84)."""
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    gdf = gpd.GeoDataFrame.from_features(data.get("features", []), crs=WGS84)
    return gdf


def _to_gdf(features: List[Dict]) -> gpd.GeoDataFrame:
    """Konverter ei liste med GeoJSON-features til GeoDataFrame."""
    if not features:
        return gpd.GeoDataFrame(geometry=[], crs=WGS84)
    return gpd.GeoDataFrame.from_features(features, crs=WGS84)


def _to_geojson(gdf: gpd.GeoDataFrame) -> Dict:
    """Konverter GeoDataFrame tilbake til GeoJSON-dict."""
    if len(gdf) == 0:
        return {"type": "FeatureCollection", "features": []}
    # Sikre WGS84 ved serialisering
    gdf = gdf.to_crs(WGS84) if gdf.crs != WGS84 else gdf
    return json.loads(gdf.to_json())


# ══════════════════════════════════════════════════════════════════════════
#  1. Service areas — Buffer rundt beredskapsressursar
# ══════════════════════════════════════════════════════════════════════════
def service_areas(
    resources: gpd.GeoDataFrame,
    radii_m: Dict[str, float] = None,
    category_col: str = "category",
    default_radius_m: float = 500,
) -> gpd.GeoDataFrame:
    """
    Bereknar buffersone (service area) rundt kvar ressurs.

    Parameters
    ----------
    resources : GeoDataFrame med Point-geometri og kategori-kolonne
    radii_m   : dict som kartlegg kategori → radius i meter
    category_col : namn på kategori-kolonne (standard: 'category')
    default_radius_m : radius for kategoriar som ikkje ligg i radii_m

    Returns
    -------
    GeoDataFrame i UTM32N med Polygon-geometri og kolonnen 'radius_m',
    'resource_type', 'resource_name'.
    """
    if len(resources) == 0:
        return gpd.GeoDataFrame(columns=["resource_type", "radius_m", "geometry"], crs=UTM32N)

    radii_m = radii_m or DEFAULT_RADII
    gdf = resources.to_crs(UTM32N).copy()

    rows = []
    for idx, row in gdf.iterrows():
        cat = str(row.get(category_col, "")).lower().strip()
        # Normaliser kategorinamn
        norm_cat = _normalize_category(cat)
        radius = radii_m.get(norm_cat, default_radius_m)

        buffered = row.geometry.buffer(radius)
        rows.append({
            "resource_type": norm_cat or "annet",
            "resource_name": row.get("name") or row.get("site_name") or row.get("brannstasjon") or "ukjent",
            "radius_m": radius,
            "geometry": buffered,
        })

    return gpd.GeoDataFrame(rows, crs=UTM32N)


def _normalize_category(cat: str) -> str:
    """Mapp ulike skrivemåtar til standard kategorinøklar i DEFAULT_RADII."""
    c = cat.lower().strip()
    if "aed" in c or "hjertestartar" in c or "hjertestarter" in c:
        return "aed"
    if "brann" in c:
        return "brannstasjon"
    if "sjukehus" in c or "sykehus" in c or "hospital" in c:
        return "sjukehus"
    if "legevakt" in c:
        return "legevakt"
    if "amk" in c or "naudsentral" in c or "naudmeld" in c:
        return "amk"
    if "politi" in c:
        return "politi"
    if "sivilforsvar" in c:
        return "sivilforsvar"
    return c


# ══════════════════════════════════════════════════════════════════════════
#  2. Coverage gaps — Befolka areal UTAN AED-dekning
# ══════════════════════════════════════════════════════════════════════════
def coverage_gaps(
    populated_area: gpd.GeoDataFrame,
    service_area_gdf: gpd.GeoDataFrame,
    resource_types: Optional[List[str]] = None,
) -> gpd.GeoDataFrame:
    """
    Finn befolka område som ligg utanfor alle service-soner.

    Overlay-operasjon: difference(populated, union(service_areas))

    Parameters
    ----------
    populated_area : GeoDataFrame med polygon(ar) som viser befolka areal
                     (f.eks. kommunegrense eller områder med bygg)
    service_area_gdf : GeoDataFrame frå service_areas()
    resource_types : liste over kategoriar som skal reknast som "dekning"
                     (default: ['aed'])

    Returns
    -------
    GeoDataFrame med dekningsgap-polygonar i UTM32N.
    """
    resource_types = resource_types or ["aed"]
    sa = service_area_gdf[service_area_gdf["resource_type"].isin(resource_types)]

    if len(populated_area) == 0:
        return gpd.GeoDataFrame(columns=["geometry"], crs=UTM32N)

    pop_utm = populated_area.to_crs(UTM32N)
    pop_union = unary_union(pop_utm.geometry.values)

    if len(sa) == 0:
        # Ingen service-soner → heile populated_area er eit gap
        gap = pop_union
    else:
        sa_union = unary_union(sa.geometry.values)
        gap = pop_union.difference(sa_union)

    # Eksploder til einskilde polygonar og fjern tynne artefakt (< 100 m²)
    gaps = []
    if gap.is_empty:
        return gpd.GeoDataFrame(columns=["area_m2", "geometry"], crs=UTM32N)
    if gap.geom_type == "Polygon":
        geoms = [gap]
    else:
        geoms = list(gap.geoms)

    for g in geoms:
        if g.area < 100:
            continue
        gaps.append({"area_m2": g.area, "geometry": g})

    return gpd.GeoDataFrame(gaps, crs=UTM32N)


# ══════════════════════════════════════════════════════════════════════════
#  3. Risk grid — 250m rutenett med risikoscore
# ══════════════════════════════════════════════════════════════════════════
def build_grid(
    boundary: gpd.GeoDataFrame,
    cell_size_m: float = DEFAULT_CELL_SIZE_M,
) -> gpd.GeoDataFrame:
    """
    Lag rektangulært rutenett som dekkjer boundary-polygonen.
    Returnerer berre celler som overlappar med boundary.
    """
    b = boundary.to_crs(UTM32N)
    minx, miny, maxx, maxy = b.total_bounds

    # Juster til næraste cellegrense
    minx = math.floor(minx / cell_size_m) * cell_size_m
    miny = math.floor(miny / cell_size_m) * cell_size_m
    maxx = math.ceil(maxx / cell_size_m) * cell_size_m
    maxy = math.ceil(maxy / cell_size_m) * cell_size_m

    cells = []
    boundary_union = unary_union(b.geometry.values)
    x = minx
    while x < maxx:
        y = miny
        while y < maxy:
            cell = box(x, y, x + cell_size_m, y + cell_size_m)
            if cell.intersects(boundary_union):
                cells.append({
                    "cell_id": f"{int(x)}_{int(y)}",
                    "cx": x + cell_size_m / 2,
                    "cy": y + cell_size_m / 2,
                    "geometry": cell,
                })
            y += cell_size_m
        x += cell_size_m

    return gpd.GeoDataFrame(cells, crs=UTM32N)


def risk_grid(
    grid: gpd.GeoDataFrame,
    population: gpd.GeoDataFrame,
    aed_service_areas: gpd.GeoDataFrame,
    pop_col: str = "population",
) -> gpd.GeoDataFrame:
    """
    Rekn risikoscore per rutenett-celle.

    Score = population × (1 − dekningsgrad)

    - population: summert frå befolkningslag som overlappar cella
    - dekningsgrad: andel av cella som er innanfor AED-service-area

    Robust mot ulike cellegrenser mellom `grid` og `population` — bruker
    arealvekta sjoin i staden for overlay.
    """
    g = grid.to_crs(UTM32N).copy().reset_index(drop=True)
    g["_cell_idx"] = g.index

    # Sikre rett geometrikolonne
    g = gpd.GeoDataFrame(g, geometry="geometry", crs=UTM32N)
    g["cell_area"] = g.geometry.area

    pop = population.to_crs(UTM32N).copy()
    if pop_col not in pop.columns:
        pop[pop_col] = 0.0

    # ── 1. Aggreger befolkning per celle ──────────────────────────
    # Spatial join + arealvekting: kvar pop-polygon sin befolkning vert fordelt
    # på cellene han overlappar, proporsjonalt med overlapp-arealet.
    if len(pop) == 0:
        g["population"] = 0.0
    else:
        pop = pop.reset_index(drop=True)
        pop["_pop_idx"] = pop.index
        pop["_pop_area"] = pop.geometry.area

        joined = gpd.sjoin(
            pop[["_pop_idx", pop_col, "_pop_area", "geometry"]],
            g[["_cell_idx", "geometry"]],
            how="inner",
            predicate="intersects",
        )

        if len(joined) == 0:
            g["population"] = 0.0
        else:
            # Rekn overlapp-areal manuelt (sjoin gir ikkje intersection)
            pop_geoms = pop.set_index("_pop_idx")["geometry"]
            cell_geoms = g.set_index("_cell_idx")["geometry"]

            def _inter_area(row):
                pgeom = pop_geoms[row["_pop_idx"]]
                cgeom = cell_geoms[row["_cell_idx"]]
                try:
                    return pgeom.intersection(cgeom).area
                except Exception:
                    return 0.0

            joined["_inter_area"] = joined.apply(_inter_area, axis=1)
            # Unngå delt-på-null
            joined["_frac"] = joined["_inter_area"] / joined["_pop_area"].replace(0, np.nan)
            joined["_pop_share"] = joined[pop_col].fillna(0) * joined["_frac"].fillna(0)

            pop_by_cell = joined.groupby("_cell_idx")["_pop_share"].sum()
            g["population"] = g["_cell_idx"].map(pop_by_cell).fillna(0).astype(float)

    # ── 2. Dekningsgrad per celle ─────────────────────────────────
    if aed_service_areas is None or len(aed_service_areas) == 0:
        g["coverage_frac"] = 0.0
    else:
        sa = aed_service_areas.to_crs(UTM32N)
        sa_union = unary_union(sa.geometry.values)

        def _cov_frac(cell_geom):
            try:
                inter = cell_geom.intersection(sa_union)
                return min(1.0, max(0.0, inter.area / cell_geom.area))
            except Exception:
                return 0.0

        g["coverage_frac"] = g.geometry.apply(_cov_frac)

    # ── 3. Risikoscore ─────────────────────────────────────────────
    g["risk_score"] = g["population"] * (1 - g["coverage_frac"])
    g["risk_class"] = pd.cut(
        g["risk_score"],
        bins=[-0.01, 0.1, 10, 50, 150, float("inf")],
        labels=["ingen", "låg", "moderat", "høg", "kritisk"],
    ).astype(str)

    # Rydd midlertidige kolonnar
    g = g.drop(columns=[c for c in ("_cell_idx",) if c in g.columns])
    return g


# ══════════════════════════════════════════════════════════════════════════
#  4. Recommend AED sites — Grådig maksimal dekning
# ══════════════════════════════════════════════════════════════════════════
def recommend_aed_sites(
    risk_grid_gdf: gpd.GeoDataFrame,
    n_recommendations: int = 10,
    coverage_radius_m: float = CRITICAL_RADIUS_M,
    min_population: float = 5,
) -> gpd.GeoDataFrame:
    """
    Grådig algoritme: Finn N celler der ein ny AED ville dekke mest uveka befolkning.

    Kvar iterasjon:
      1. Sorter celler etter risikoscore (population × (1-coverage))
      2. Vel cellesenter med høgast score som ikkje alt er plassert
      3. Bufr coverage_radius_m rundt punktet
      4. Trekk frå dekt befolkning i alle overlappande celler
      5. Gjenta

    Returns
    -------
    GeoDataFrame med anbefalte punkt, befolkning dekt, avstand til eksisterande.
    """
    g = risk_grid_gdf.to_crs(UTM32N).copy()
    # Arbeidskopi: remaining uncovered population
    g["remaining"] = g["population"] * (1 - g["coverage_frac"])

    recommendations = []
    for rank in range(1, n_recommendations + 1):
        # Vel cella med høgast attverande risiko
        candidates = g[g["remaining"] > min_population].copy()
        if len(candidates) == 0:
            break

        # Sorter, vel topp
        best = candidates.sort_values("remaining", ascending=False).iloc[0]
        cx, cy = best["cx"], best["cy"]
        point_utm = Point(cx, cy)
        covered_buffer = point_utm.buffer(coverage_radius_m)

        # Rekn ut kor mykje befolkning som vert nydekt
        covered_mask = g.geometry.intersects(covered_buffer)
        pop_covered = 0.0
        for idx in g[covered_mask].index:
            cell = g.loc[idx]
            inter = cell.geometry.intersection(covered_buffer)
            frac = inter.area / cell.geometry.area if cell.geometry.area > 0 else 0
            pop_gained = cell["remaining"] * frac
            pop_covered += pop_gained
            g.at[idx, "remaining"] = cell["remaining"] * (1 - frac)

        # Konverter senterpunkt tilbake til WGS84 for frontend-bruk
        centroid_wgs = (
            gpd.GeoSeries([point_utm], crs=UTM32N)
            .to_crs(WGS84)
            .iloc[0]
        )

        recommendations.append({
            "rank": rank,
            "cell_id": best["cell_id"],
            "population_covered": round(pop_covered, 1),
            "latitude": centroid_wgs.y,
            "longitude": centroid_wgs.x,
            "geometry": point_utm,
        })

    if not recommendations:
        return gpd.GeoDataFrame(columns=["rank", "population_covered", "geometry"], crs=UTM32N)
    return gpd.GeoDataFrame(recommendations, crs=UTM32N)


# ══════════════════════════════════════════════════════════════════════════
#  5. Full pipeline — kall for å produsere alle output-lag
# ══════════════════════════════════════════════════════════════════════════
def run_pipeline(
    aed_features: List[Dict],
    brann_features: List[Dict],
    landmarks_features: List[Dict],
    population_gdf: gpd.GeoDataFrame,
    boundary_gdf: gpd.GeoDataFrame,
    n_recommendations: int = 10,
    cell_size_m: float = DEFAULT_CELL_SIZE_M,
) -> Dict[str, Dict]:
    """
    Køyr heile dekningsgap-analysen og returner alle resultat som GeoJSON-dict.
    Brukast både av notebook og Flask-backend (ved runtime eller pre-computed).
    """
    # Filtrer AED til åpne
    aeds_all = _to_gdf(aed_features)
    if "is_available" in aeds_all.columns:
        aeds = aeds_all[aeds_all["is_available"] == True].copy()
    elif "is_open_status" in aeds_all.columns:
        aeds = aeds_all[aeds_all["is_open_status"] == "Y"].copy()
    else:
        aeds = aeds_all.copy()
    aeds["category"] = "aed"

    brann = _to_gdf(brann_features)
    if len(brann):
        brann["category"] = "brannstasjon"

    landmarks = _to_gdf(landmarks_features)
    # Bruk berre dei relevante kategoriane frå landmarks
    if "category" in landmarks.columns:
        landmarks = landmarks[landmarks.geometry.type == "Point"]

    # Kombiner alle ressursar
    all_resources = pd.concat(
        [g for g in [aeds, brann, landmarks] if len(g) > 0],
        ignore_index=True,
    )
    if len(all_resources) == 0:
        raise ValueError("Ingen beredskapsressursar funne — kan ikkje køyre analyse.")
    all_resources = gpd.GeoDataFrame(all_resources, geometry="geometry", crs=WGS84)

    # 1. Service areas (alle typar)
    sa_all = service_areas(all_resources)

    # 2. Dekningsgap (berre AED-dekning som kriterium)
    gaps = coverage_gaps(boundary_gdf, sa_all, resource_types=["aed"])

    # 3. Risk grid
    grid = build_grid(boundary_gdf, cell_size_m=cell_size_m)
    aed_sa = sa_all[sa_all["resource_type"] == "aed"]
    risk = risk_grid(grid, population_gdf, aed_sa)

    # 4. Anbefalte plasseringar
    recs = recommend_aed_sites(risk, n_recommendations=n_recommendations)

    return {
        "service_areas": _to_geojson(sa_all),
        "coverage_gaps": _to_geojson(gaps),
        "risk_grid":     _to_geojson(risk),
        "recommendations": _to_geojson(recs),
        "population":    _to_geojson(population_gdf),
    }
