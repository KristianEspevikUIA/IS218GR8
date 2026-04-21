"""
run_coverage_analysis.py

Kjør dekningsgap-analysen for Kristiansand ved å kombinere:
    - Lokale AED-data (eller live API / Supabase om mogleg)
    - Brannstasjon-data frå GeoNorge WFS (live om mogleg, eller cache)
    - Beredskapsressursar frå lokal GeoJSON
    - Befolkningsrutenett frå generate_population_grid.py
    - Kommunegrense

Skriv resultat-GeoJSON til app/data/coverage/ for frontend-konsum:
    service_areas.geojson
    coverage_gaps.geojson
    risk_grid.geojson
    recommendations.geojson
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import geopandas as gpd

sys.path.insert(0, str(Path(__file__).parent))

from app.models.coverage_model import run_pipeline   # noqa: E402

BASE = Path(__file__).parent
DATA_DIR = BASE / "app" / "data"
OUT_DIR = DATA_DIR / "coverage"


def load_aeds() -> list:
    """
    Prøv å hente AED-ar i prioritert rekkefølge:
      1. Cache-fil app/data/aeds_cache.geojson (om pipeline er køyrt før)
      2. Supabase hjertestartere-tabell (om .env har credentials)
      3. Live Hjertestarterregister API
      4. Fallback: dummy datasett plassert i sentrum (slik at pipeline kan testast)
    """
    cache = DATA_DIR / "aeds_cache.geojson"
    if cache.exists():
        print(f"[AED] Bruker cache: {cache}")
        with open(cache, encoding="utf-8") as f:
            return json.load(f).get("features", [])

    # Prøv Supabase
    try:
        from app.models.data_model import DataModel
        dm = DataModel()
        data = dm.get_hjertestartere_geojson()
        feats = data.get("features", [])
        if feats:
            print(f"[AED] Henta {len(feats)} frå Supabase")
            return feats
    except Exception as e:
        print(f"[AED] Supabase ikkje tilgjengeleg: {e}")

    # Prøv live API
    try:
        from app.models.hjertestarterregister_api import HjertestarterregisterAPI
        api = HjertestarterregisterAPI()
        if api.client_id and api.client_secret:
            api.authenticate()
            resp = api.search_assets(latitude=58.1414, longitude=8.0842,
                                     distance=15000, max_rows=5000)
            if resp and "ASSETS" in resp:
                gj = api.convert_to_geojson(resp)
                feats = gj.get("features", [])
                for feat in feats:
                    for asset in resp["ASSETS"]:
                        if asset.get("ASSET_ID") == feat["properties"].get("asset_id"):
                            feat["properties"]["is_available"] = asset.get("IS_OPEN") == "Y"
                            feat["properties"]["is_open_status"] = asset.get("IS_OPEN", "N")
                            break
                print(f"[AED] Henta {len(feats)} frå live API")
                # Cache it
                os.makedirs(DATA_DIR, exist_ok=True)
                with open(cache, "w", encoding="utf-8") as f:
                    json.dump({"type": "FeatureCollection", "features": feats}, f)
                return feats
    except Exception as e:
        print(f"[AED] Live API ikkje tilgjengeleg: {e}")

    # Fallback: dummy dataset for testing
    print("[AED] ⚠ Bruker dummy-datasett (få AED-ar, plassert realistisk i sentrum)")
    dummies = [
        # (lat, lng, name)
        (58.1469, 8.0058, "Torvet"),
        (58.1502, 8.0107, "Rådhuset"),
        (58.1549, 8.0234, "Lund senter"),
        (58.1291, 7.9483, "Vågsbygd senter"),
        (58.1435, 8.0020, "Marviksletta"),
        (58.1684, 7.9822, "Tinnheia"),
        (58.1467, 8.0810, "Sørlandssenteret"),
        (58.1395, 8.1240, "Randesund skole"),
        (58.2015, 8.0390, "Tveit sentrum"),
        (58.1843, 8.0530, "Justvik"),
        (58.1607, 8.0198, "Kristiansand stasjon"),
        (58.1540, 8.0150, "Hotel Scandic Bystranda"),
        (58.1488, 7.9990, "UiA Gimlemoen"),
        (58.1595, 8.0305, "Kvadraturen skole"),
        (58.1413, 8.0090, "Odderøya"),
    ]
    feats = []
    for i, (lat, lng, name) in enumerate(dummies):
        feats.append({
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [lng, lat]},
            "properties": {
                "asset_id": 900000 + i,
                "site_name": name,
                "is_available": True,
                "is_open_status": "Y",
                "source": "dummy"
            },
        })
    return feats


def load_brannstasjoner() -> list:
    """Prøv å hente brannstasjonar (cache/live), fallback til tomt."""
    cache = DATA_DIR / "brannstasjoner_cache.geojson"
    if cache.exists():
        print(f"[BRANN] Bruker cache: {cache}")
        with open(cache, encoding="utf-8") as f:
            return json.load(f).get("features", [])
    try:
        from app.models.data_model import DataModel
        dm = DataModel()
        data = dm.fetch_brannstasjoner_wfs()
        feats = data.get("features", [])
        if feats:
            print(f"[BRANN] Henta {len(feats)} frå WFS")
            with open(cache, "w", encoding="utf-8") as f:
                json.dump(data, f)
            return feats
    except Exception as e:
        print(f"[BRANN] WFS ikkje tilgjengeleg: {e}")

    # Fallback: dummy brannstasjonar
    dummies = [
        (58.1489, 8.0012, "Kristiansand hovudstasjon"),
        (58.2015, 8.0379, "Tveit brannstasjon"),
        (58.1299, 7.9464, "Vågsbygd brannstasjon"),
    ]
    print("[BRANN] ⚠ Bruker dummy-datasett")
    return [{
        "type": "Feature",
        "geometry": {"type": "Point", "coordinates": [lng, lat]},
        "properties": {"brannstasjon": name, "category": "brannstasjon"},
    } for lat, lng, name in dummies]


def load_landmarks() -> list:
    """Lokal GeoJSON med beredskapsressursar."""
    fp = DATA_DIR / "norwegian_landmarks.geojson"
    with open(fp, encoding="utf-8") as f:
        return json.load(f).get("features", [])


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    print("━" * 60)
    print("Dekningsgap-analyse — Kristiansand")
    print("━" * 60)

    # ── Last inn alle data ──
    aed_features = load_aeds()
    brann_features = load_brannstasjoner()
    landmarks_features = load_landmarks()

    print(f"\n[INPUT] AED-ar:           {len(aed_features)}")
    print(f"[INPUT] Brannstasjonar:   {len(brann_features)}")
    print(f"[INPUT] Landmarks:        {len(landmarks_features)}")

    # Befolkning + kommune
    pop_path = DATA_DIR / "befolkning_kristiansand.geojson"
    kommune_path = DATA_DIR / "kristiansand_kommune.geojson"
    if not pop_path.exists() or not kommune_path.exists():
        print("[PIPE] ✗ Manglar befolkning/kommunegrense — køyr generate_population_grid.py først.")
        sys.exit(1)

    with open(pop_path, encoding="utf-8") as f:
        pop_gj = json.load(f)
    population_gdf = gpd.GeoDataFrame.from_features(pop_gj["features"], crs="EPSG:4326")

    with open(kommune_path, encoding="utf-8") as f:
        kommune_gj = json.load(f)
    boundary_gdf = gpd.GeoDataFrame.from_features(kommune_gj["features"], crs="EPSG:4326")

    print(f"[INPUT] Befolknings-celler: {len(population_gdf)}")
    print(f"[INPUT] Kommunegrense:      {len(boundary_gdf)} polygon(ar)")

    # ── Køyr pipeline ──
    print("\n[PIPE] Køyrer dekningsgap-pipeline...")
    results = run_pipeline(
        aed_features=aed_features,
        brann_features=brann_features,
        landmarks_features=landmarks_features,
        population_gdf=population_gdf,
        boundary_gdf=boundary_gdf,
        n_recommendations=10,
    )

    # ── Lagre alle output-lag ──
    for key, geojson in results.items():
        n_feat = len(geojson.get("features", []))
        out = OUT_DIR / f"{key}.geojson"
        with open(out, "w", encoding="utf-8") as f:
            json.dump(geojson, f, ensure_ascii=False)
        print(f"[OUT] {out.name:25s} {n_feat:5d} features")

    # ── Oppsummering ──
    print("\n━" * 30)
    print("Oppsummering:")
    risk_feats = results["risk_grid"]["features"]
    if risk_feats:
        populations = [f["properties"]["population"] for f in risk_feats]
        risks = [f["properties"]["risk_score"] for f in risk_feats]
        coverages = [f["properties"]["coverage_frac"] for f in risk_feats]
        total_pop = sum(populations)
        avg_cov = sum(p * c for p, c in zip(populations, coverages)) / total_pop if total_pop else 0
        covered_pop = sum(p * c for p, c in zip(populations, coverages))
        uncovered = total_pop - covered_pop
        print(f"  Total befolkning:       {total_pop:,.0f}")
        print(f"  AED-dekka (befolkn.):   {covered_pop:,.0f} ({100*avg_cov:.1f}%)")
        print(f"  Utan dekning:           {uncovered:,.0f} ({100*(1-avg_cov):.1f}%)")
        classes = {}
        for f in risk_feats:
            classes[f["properties"]["risk_class"]] = classes.get(f["properties"]["risk_class"], 0) + 1
        print(f"  Risikoklassefordeling:  {dict(sorted(classes.items()))}")
    recs = results["recommendations"]["features"]
    if recs:
        print(f"\n  Anbefalte nye AED (top {len(recs)}):")
        for r in recs:
            p = r["properties"]
            print(f"    #{p['rank']:2d}  covers {p['population_covered']:>6.0f} pers  "
                  f"at ({r['geometry']['coordinates'][1]:.4f}, {r['geometry']['coordinates'][0]:.4f})")
    print("━" * 60)


if __name__ == "__main__":
    main()
