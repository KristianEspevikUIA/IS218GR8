"""
generate_figures.py

Genererer statiske figurar for semesterrapporten frå dekningsgap-analysen.

Output:
    static/figures/01_oversikt_ressursar.png        — alle beredskapsressursar
    static/figures/02_befolkning_250m.png            — befolkningsrutenett
    static/figures/03_service_areas.png              — buffersoner / dekning
    static/figures/04_coverage_gaps.png              — dekningsgap
    static/figures/05_risk_grid.png                  — koroplettkart risikoscore
    static/figures/06_recommendations.png            — anbefalte AED-plasseringar
    static/figures/07_before_after.png               — dekningssamanlikning
"""
from __future__ import annotations

import json
from pathlib import Path

import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from matplotlib.colors import ListedColormap

BASE = Path(__file__).parent
DATA_DIR = BASE / "app" / "data"
COV_DIR = DATA_DIR / "coverage"
OUT_DIR = BASE / "static" / "figures"
OUT_DIR.mkdir(parents=True, exist_ok=True)

WGS84 = "EPSG:4326"
UTM32N = "EPSG:25832"

# Felles stil — mørkt tema som speglar web-UI
plt.rcParams.update({
    "figure.facecolor":  "#1a1a2e",
    "axes.facecolor":    "#16213e",
    "axes.edgecolor":    "#eeeeee",
    "axes.labelcolor":   "#eeeeee",
    "xtick.color":       "#bbbbbb",
    "ytick.color":       "#bbbbbb",
    "text.color":        "#eeeeee",
    "axes.titlecolor":   "#e94560",
    "axes.titlesize":    14,
    "axes.titleweight":  "bold",
    "font.family":       "DejaVu Sans",
    "savefig.facecolor": "#1a1a2e",
    "savefig.dpi":       140,
})

RISK_COLORS = {
    "ingen":   "#d0d0d0",
    "låg":     "#fee08b",
    "moderat": "#fdae61",
    "høg":     "#f46d43",
    "kritisk": "#a50026",
}


def _load(name: str) -> gpd.GeoDataFrame:
    fp = COV_DIR / f"{name}.geojson"
    with open(fp, encoding="utf-8") as f:
        gj = json.load(f)
    if not gj.get("features"):
        return gpd.GeoDataFrame(geometry=[], crs=WGS84)
    return gpd.GeoDataFrame.from_features(gj["features"], crs=WGS84)


def _load_boundary() -> gpd.GeoDataFrame:
    fp = DATA_DIR / "kristiansand_kommune.geojson"
    with open(fp, encoding="utf-8") as f:
        gj = json.load(f)
    return gpd.GeoDataFrame.from_features(gj["features"], crs=WGS84)


def _load_resources():
    with open(DATA_DIR / "norwegian_landmarks.geojson", encoding="utf-8") as f:
        lm = gpd.GeoDataFrame.from_features(json.load(f)["features"], crs=WGS84)
    # Hent AED-ar frå cache eller coverage/service_areas sine senterpunkt
    aed_cache = DATA_DIR / "aeds_cache.geojson"
    if aed_cache.exists():
        with open(aed_cache, encoding="utf-8") as f:
            aeds = gpd.GeoDataFrame.from_features(json.load(f)["features"], crs=WGS84)
    else:
        aeds = gpd.GeoDataFrame(geometry=[], crs=WGS84)
    # Brannstasjoner fra cache hvis tilgjengelig
    brann_cache = DATA_DIR / "brannstasjoner_cache.geojson"
    if brann_cache.exists():
        with open(brann_cache, encoding="utf-8") as f:
            brann = gpd.GeoDataFrame.from_features(json.load(f)["features"], crs=WGS84)
    else:
        brann = gpd.GeoDataFrame(geometry=[], crs=WGS84)
    return lm, aeds, brann


def _add_basemap_frame(ax, boundary):
    """Tegn kommuneomriss og legg inn tittelstriper."""
    if len(boundary):
        boundary.to_crs(UTM32N).plot(
            ax=ax, facecolor="none", edgecolor="#ffffff",
            linewidth=1.2, alpha=0.5,
        )
    ax.set_aspect("equal")
    ax.set_xlabel("East (m, UTM 32N)")
    ax.set_ylabel("North (m, UTM 32N)")


def fig_01_oversikt(boundary, lm, aeds, brann):
    fig, ax = plt.subplots(figsize=(9, 7))
    _add_basemap_frame(ax, boundary)
    b = boundary.to_crs(UTM32N)
    b.plot(ax=ax, facecolor="#0f3460", alpha=0.3, edgecolor="#fff", linewidth=0.8)

    if len(lm):
        lm.to_crs(UTM32N).plot(ax=ax, color="#3388ff", markersize=40,
                                edgecolor="white", label="Beredskapsressurs")
    if len(brann):
        brann.to_crs(UTM32N).plot(ax=ax, color="#ff8c00", markersize=80, marker="^",
                                   edgecolor="white", label="Brannstasjon")
    if len(aeds):
        aeds_utm = aeds.to_crs(UTM32N)
        aeds_utm.plot(ax=ax, color="#27ae60", markersize=20,
                      edgecolor="white", alpha=0.8, label=f"AED ({len(aeds_utm)})")

    ax.set_title("Beredskapsressursar i Kristiansand — inngangsdata")
    ax.legend(loc="upper left", frameon=True, facecolor="#1a1a2e",
              edgecolor="#e94560", labelcolor="#eee")
    plt.tight_layout()
    out = OUT_DIR / "01_oversikt_ressursar.png"
    plt.savefig(out)
    plt.close()
    print(f"✓ {out}")


def fig_02_population(boundary):
    pop = _load("population")
    fig, ax = plt.subplots(figsize=(9, 7))
    _add_basemap_frame(ax, boundary)
    pop_utm = pop.to_crs(UTM32N)
    # Filter ut celler med 0 innbyggjarar
    viz = pop_utm[pop_utm["population"] > 0.1].copy()
    viz.plot(ax=ax, column="population", cmap="YlOrRd", legend=True,
             edgecolor="none", alpha=0.85,
             legend_kwds={"label": "Befolkning per 250m-celle", "shrink": 0.6})
    ax.set_title(f"Befolkningsrutenett (250m) — {int(viz['population'].sum()):,} innbyggjarar")
    plt.tight_layout()
    out = OUT_DIR / "02_befolkning_250m.png"
    plt.savefig(out)
    plt.close()
    print(f"✓ {out}")


def fig_03_service_areas(boundary, aeds):
    sa = _load("service_areas")
    fig, ax = plt.subplots(figsize=(9, 7))
    _add_basemap_frame(ax, boundary)
    b = boundary.to_crs(UTM32N)
    b.plot(ax=ax, facecolor="#0f3460", alpha=0.2, edgecolor="#fff")

    # Separer typar
    for rtype, color in [
        ("brannstasjon", "#ff8c00"),
        ("aed",          "#27ae60"),
    ]:
        subset = sa[sa["resource_type"] == rtype]
        if len(subset):
            subset.plot(ax=ax, color=color, alpha=0.25, edgecolor=color,
                        linewidth=0.7, label=f"{rtype} buffer")

    if len(aeds):
        aeds.to_crs(UTM32N).plot(ax=ax, color="white", markersize=12, edgecolor="#27ae60")

    ax.set_title("Service areas — buffersoner (AED 400m · brannstasjon 1500m)")
    ax.legend(loc="upper left", frameon=True, facecolor="#1a1a2e",
              edgecolor="#e94560", labelcolor="#eee")
    plt.tight_layout()
    out = OUT_DIR / "03_service_areas.png"
    plt.savefig(out)
    plt.close()
    print(f"✓ {out}")


def fig_04_gaps(boundary, aeds):
    gaps = _load("coverage_gaps")
    fig, ax = plt.subplots(figsize=(9, 7))
    _add_basemap_frame(ax, boundary)
    b = boundary.to_crs(UTM32N)
    b.plot(ax=ax, facecolor="#0f3460", alpha=0.3, edgecolor="#fff", linewidth=0.7)
    if len(gaps):
        gaps_utm = gaps.to_crs(UTM32N)
        gaps_utm.plot(ax=ax, facecolor="#e74c3c", alpha=0.45, edgecolor="#e74c3c",
                      linewidth=0.5, label=f"Dekningsgap ({len(gaps_utm)} polygon)")
    if len(aeds):
        aeds.to_crs(UTM32N).plot(ax=ax, color="#27ae60", markersize=25,
                                  edgecolor="white", label="Eksisterande AED")
    ax.set_title("Dekningsgap — område utan AED innan 400m")
    ax.legend(loc="upper left", frameon=True, facecolor="#1a1a2e",
              edgecolor="#e94560", labelcolor="#eee")
    plt.tight_layout()
    out = OUT_DIR / "04_coverage_gaps.png"
    plt.savefig(out)
    plt.close()
    print(f"✓ {out}")


def fig_05_risk_grid(boundary):
    risk = _load("risk_grid")
    fig, ax = plt.subplots(figsize=(9, 7))
    _add_basemap_frame(ax, boundary)
    b = boundary.to_crs(UTM32N)
    b.plot(ax=ax, facecolor="#0f3460", alpha=0.2, edgecolor="#fff", linewidth=0.6)

    r_utm = risk.to_crs(UTM32N)
    # Berre visa celler som har risiko (skip 'ingen')
    viz = r_utm[r_utm["risk_class"] != "ingen"].copy()
    # Tildel farge pr klasse
    viz["_color"] = viz["risk_class"].map(RISK_COLORS).fillna("#888")
    viz.plot(ax=ax, color=viz["_color"], alpha=0.75, edgecolor="none")

    # Legende
    handles = [
        mpatches.Patch(color=c, label=k)
        for k, c in RISK_COLORS.items() if k != "ingen"
    ]
    ax.legend(handles=handles, loc="upper left", title="Risikoklasse",
              frameon=True, facecolor="#1a1a2e", edgecolor="#e94560",
              labelcolor="#eee", title_fontsize=11)
    ax.set_title("Risikoscore per 250m-celle (befolkning × 1-dekningsgrad)")
    plt.tight_layout()
    out = OUT_DIR / "05_risk_grid.png"
    plt.savefig(out)
    plt.close()
    print(f"✓ {out}")


def fig_06_recommendations(boundary, aeds):
    risk = _load("risk_grid")
    recs = _load("recommendations")

    fig, ax = plt.subplots(figsize=(9, 7))
    _add_basemap_frame(ax, boundary)
    b = boundary.to_crs(UTM32N)
    b.plot(ax=ax, facecolor="#0f3460", alpha=0.2, edgecolor="#fff", linewidth=0.6)

    # Risikokoroplett som bakgrunn
    r_utm = risk.to_crs(UTM32N)
    viz = r_utm[r_utm["risk_class"].isin(["moderat", "høg", "kritisk"])].copy()
    viz["_color"] = viz["risk_class"].map(RISK_COLORS)
    viz.plot(ax=ax, color=viz["_color"], alpha=0.45, edgecolor="none")

    # Eksisterande AED
    if len(aeds):
        aeds.to_crs(UTM32N).plot(ax=ax, color="#27ae60", markersize=16,
                                  edgecolor="white", linewidth=0.6,
                                  label="Eksisterande AED")

    # Anbefalte (nummererte)
    if len(recs):
        r_utm = recs.to_crs(UTM32N)
        r_utm.plot(ax=ax, color="#8e24aa", markersize=200, marker="o",
                   edgecolor="white", linewidth=2, zorder=5,
                   label=f"Anbefalt ny AED (top {len(r_utm)})")
        for _, row in r_utm.iterrows():
            ax.annotate(
                str(int(row["rank"])),
                xy=(row.geometry.x, row.geometry.y),
                ha="center", va="center",
                color="white", fontsize=9, fontweight="bold", zorder=6,
            )

    ax.set_title("Anbefalte nye AED-plasseringar — grådig maksimal dekning")
    ax.legend(loc="upper left", frameon=True, facecolor="#1a1a2e",
              edgecolor="#e94560", labelcolor="#eee")
    plt.tight_layout()
    out = OUT_DIR / "06_recommendations.png"
    plt.savefig(out)
    plt.close()
    print(f"✓ {out}")


def fig_07_before_after():
    """Stolpediagram med dekningsstatistikk før/etter anbefalinger."""
    risk = _load("risk_grid")
    recs = _load("recommendations")

    # Før: totaler frå risk_grid
    total = risk["population"].sum()
    covered_before = (risk["population"] * risk["coverage_frac"]).sum()
    uncovered_before = total - covered_before

    # Etter: legg til dekning frå anbefalingene
    covered_by_recs = recs["population_covered"].sum() if len(recs) else 0
    covered_after = covered_before + covered_by_recs
    uncovered_after = total - covered_after

    fig, ax = plt.subplots(figsize=(9, 5))
    labels = ["I dag", "Med 10 anbefalte AED"]
    covered = [covered_before, covered_after]
    uncovered = [uncovered_before, uncovered_after]

    x = np.arange(len(labels))
    w = 0.5
    ax.bar(x, covered,   w, color="#27ae60", label="Dekka")
    ax.bar(x, uncovered, w, bottom=covered, color="#e74c3c", label="Udekka")

    for i, (c, u) in enumerate(zip(covered, uncovered)):
        pct = 100 * c / (c + u) if (c + u) else 0
        ax.text(i, c / 2, f"{c:,.0f}\n({pct:.1f}%)",
                ha="center", va="center", color="white", fontweight="bold")
        ax.text(i, c + u / 2, f"{u:,.0f}",
                ha="center", va="center", color="white", fontsize=10)

    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=11)
    ax.set_ylabel("Befolkning (personar)")
    ax.set_title("AED-dekning før og etter anbefalingar")
    ax.legend(frameon=True, facecolor="#1a1a2e", edgecolor="#e94560", labelcolor="#eee")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    plt.tight_layout()
    out = OUT_DIR / "07_before_after.png"
    plt.savefig(out)
    plt.close()
    print(f"✓ {out}")


def main():
    print("━" * 60)
    print("Genererer figurar til semesterrapporten")
    print("━" * 60)

    boundary = _load_boundary()
    lm, aeds, brann = _load_resources()

    fig_01_oversikt(boundary, lm, aeds, brann)
    fig_02_population(boundary)
    fig_03_service_areas(boundary, aeds)
    fig_04_gaps(boundary, aeds)
    fig_05_risk_grid(boundary)
    fig_06_recommendations(boundary, aeds)
    fig_07_before_after()

    print("━" * 60)
    print(f"✓ Ferdig. Figurar i {OUT_DIR}")


if __name__ == "__main__":
    main()
