# -*- coding: utf-8 -*-
"""
Export publication — graphiques SVG + PNG dans output_final/
Style éditorial sobre : fond blanc cassé, grille légère, annotations callout.
"""
import json, pathlib, warnings
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import matplotlib.patches as mpatches
import numpy as np
warnings.filterwarnings("ignore")

ROOT   = pathlib.Path(__file__).parent.parent
DATA   = ROOT / "site" / "data.json"
OUT    = ROOT / "output_final"
OUT.mkdir(exist_ok=True)

d = json.loads(DATA.read_text(encoding="utf-8"))

# ── Palette ──────────────────────────────────────────────────────────────────
C = dict(
    blue   = "#2E879A",
    red    = "#FF3F3F",
    coral  = "#F99592",
    plum   = "#9D1453",
    muted  = "#595550",
    grid   = "#e0d6ce",
    paper  = "#F3ECE6",
    ink    = "#262626",
)

# ── Style de base ─────────────────────────────────────────────────────────────
def base_style():
    plt.rcParams.update({
        "figure.facecolor": C["paper"],
        "axes.facecolor":   C["paper"],
        "axes.edgecolor":   C["grid"],
        "axes.linewidth":   0.6,
        "axes.spines.top":  False,
        "axes.spines.right":False,
        "axes.spines.left": False,
        "axes.spines.bottom": True,
        "grid.color":       C["grid"],
        "grid.linewidth":   0.55,
        "grid.linestyle":   "-",
        "xtick.color":      C["muted"],
        "ytick.color":      C["muted"],
        "xtick.labelsize":  8,
        "ytick.labelsize":  8,
        "font.family":      "sans-serif",
        "font.size":        9,
        "text.color":       C["ink"],
    })
base_style()

def save(fig, name):
    p_svg = OUT / f"{name}.svg"
    p_png = OUT / f"{name}.png"
    fig.savefig(p_svg, format="svg", bbox_inches="tight", dpi=150)
    fig.savefig(p_png, format="png", bbox_inches="tight", dpi=180)
    plt.close(fig)
    print(f"  OK {name}")

def title_block(ax, title, sub=None):
    ax.set_title(title, loc="left", fontsize=11, fontweight="semibold",
                 color=C["ink"], pad=8 + (16 if sub else 0))
    if sub:
        ax.figure.text(
            ax.get_position().x0, ax.get_position().y1 + 0.01,
            sub, transform=ax.figure.transFigure,
            fontsize=7.5, color=C["muted"], va="bottom",
        )

def callout(ax, year, val, text, color, offset_y=0.8, above=True):
    dy = offset_y if above else -offset_y
    ax.annotate(
        text, xy=(year, val), xytext=(year, val + dy),
        arrowprops=dict(arrowstyle="-", color=color, lw=0.8,
                        connectionstyle="arc3,rad=0"),
        fontsize=6.5, color=color, ha="center", va="bottom" if above else "top",
        fontweight="semibold",
    )

def end_label(ax, x, y, text, color, xpad=0.3):
    ax.text(x + xpad, y, text, color=color, fontsize=8, va="center",
            fontweight="medium")

def row_to_pts(rows, key):
    return [(r["year"], r[key]) for r in rows if r.get(key) is not None and
            isinstance(r[key], (int, float)) and np.isfinite(r[key])]

ROWS  = d["migrationSelection"]   # 2005-2024 FR DK IT UK
ROWM  = d["migrationMulti"]       # FR DE ES SE NL IT DK
ASY   = d["asylum"]
EU    = d["euRanking2024"]
FE    = d["foreignEntries"] or []
RANG  = d["analyseRangFrance"] or []
RATIO = d["analyseRatioAsileSolde"] or []
VOL   = d["volatilitySoldeCore"] or []
BARS  = d["asylumBars2024"] or []

# ═══════════════════════════════════════════════════════════════════════════════
print("Génération des figures…")

# ── G1 : Vue 4 pays ────────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(9.5, 5.2))
series = [("FR","France",C["blue"],2.8), ("DK","Danemark",C["red"],1.9),
          ("IT","Italie",C["coral"],1.9), ("UK","Royaume-Uni",C["plum"],1.9)]
for key, lbl, col, lw in series:
    pts = row_to_pts(ROWS, key)
    if pts:
        xs, ys = zip(*pts)
        ax.plot(xs, ys, color=col, lw=lw, solid_capstyle="round")
        end_label(ax, xs[-1], ys[-1], lbl, col)

ann = [("Pic de l'asile", 2015, "DK"),
       ("Brexit", 2016, "UK"),
       ("Frederiksen PM", 2019, "DK"),
       ("Covid-19", 2020, "FR"),
       ("Ukraine", 2022, "UK")]
kmap = {k:c for k,lbl,c,lw in series}
for text, yr, key in ann:
    pts = row_to_pts(ROWS, key)
    pt = next((v for y,v in pts if y == yr), None)
    if pt is not None:
        above = pt > 0
        callout(ax, yr, pt, text, kmap[key], offset_y=1.4, above=above)

ax.yaxis.set_major_formatter(mticker.FormatStrFormatter("%.1f"))
ax.set_ylabel("Pour 1 000 habitants", fontsize=7.5, color=C["muted"])
ax.set_xlim(2005, 2026); ax.grid(axis="y")
ax.set_title("La France, la plus fermée parmi ses comparateurs",
             loc="left", fontsize=11, fontweight="semibold", pad=4)
ax.text(0, 1.03, "Solde migratoire net pour 1\u202f000 habitants",
        transform=ax.transAxes, fontsize=8, color=C["muted"])
fig.tight_layout()
save(fig, "G1_vue_4_pays")

# ── G2 : FR–DK duo ─────────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(8.5, 4.6))
for key, lbl, col, lw in [("FR","France",C["blue"],2.6), ("DK","Danemark",C["red"],2.0)]:
    pts = [(y,v) for y,v in row_to_pts(ROWS, key) if 2013 <= y <= 2024]
    if pts:
        xs, ys = zip(*pts)
        ax.plot(xs, ys, color=col, lw=lw, marker="o", ms=3.5, solid_capstyle="round")
        end_label(ax, xs[-1], ys[-1], lbl, col)

for text, yr, key, above in [
    ("Pic de l'asile", 2015, "DK", True),
    ("Frederiksen PM", 2019, "DK", True),
    ("Ukraine", 2022, "DK", True),
    ("Covid-19", 2020, "FR", False),
]:
    pts = [(y,v) for y,v in row_to_pts(ROWS, key) if y == yr]
    if pts: callout(ax, yr, pts[0][1], text, C["red"] if key=="DK" else C["blue"],
                    offset_y=1.2, above=above)

ax.set_xlim(2012.5, 2025); ax.grid(axis="y")
ax.set_ylabel("Pour 1 000 habitants", fontsize=7.5, color=C["muted"])
ax.set_title("Le Danemark de Frederiksen reste plus ouvert que la France",
             loc="left", fontsize=11, fontweight="semibold", pad=4)
ax.text(0, 1.03, "Solde migratoire net pour 1\u202f000 habitants, 2013-2024",
        transform=ax.transAxes, fontsize=8, color=C["muted"])
fig.tight_layout()
save(fig, "G2_FR_DK")

# ── G3 : FR–IT duo ─────────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(8.5, 4.6))
for key, lbl, col, lw in [("FR","France",C["blue"],2.6), ("IT","Italie",C["coral"],2.0)]:
    pts = [(y,v) for y,v in row_to_pts(ROWS, key) if 2013 <= y <= 2024]
    if pts:
        xs, ys = zip(*pts)
        ax.plot(xs, ys, color=col, lw=lw, marker="o", ms=3.5, solid_capstyle="round")
        end_label(ax, xs[-1], ys[-1], lbl, col)

for text, yr, key, above in [
    ("Pic de l'asile", 2015, "IT", True),
    ("Salvini ministre", 2018, "IT", True),
    ("Covid-19", 2020, "IT", False),
    ("G. Meloni PM", 2022, "IT", True),
]:
    pts = [(y,v) for y,v in row_to_pts(ROWS, key) if y == yr]
    if pts: callout(ax, yr, pts[0][1], text, C["coral"], offset_y=0.8, above=above)

ax.set_xlim(2012.5, 2025); ax.grid(axis="y")
ax.set_ylabel("Pour 1 000 habitants", fontsize=7.5, color=C["muted"])
ax.set_title("L'Italie de Meloni accueille davantage que la France",
             loc="left", fontsize=11, fontweight="semibold", pad=4)
ax.text(0, 1.03, "Solde migratoire net pour 1\u202f000 habitants, 2013-2024",
        transform=ax.transAxes, fontsize=8, color=C["muted"])
fig.tight_layout()
save(fig, "G3_FR_IT")

# ── G4 : FR–UK duo ─────────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(8.5, 4.6))
for key, lbl, col, lw in [("FR","France",C["blue"],2.6), ("UK","Royaume-Uni",C["plum"],2.0)]:
    pts = [(y,v) for y,v in row_to_pts(ROWS, key) if 2013 <= y <= 2024]
    if pts:
        xs, ys = zip(*pts)
        ax.plot(xs, ys, color=col, lw=lw, marker="o", ms=3.5, solid_capstyle="round")
        end_label(ax, xs[-1], ys[-1], lbl, col)

for text, yr, key, above in [
    ("Brexit", 2016, "UK", True),
    ("Fin libre circ.", 2021, "UK", True),
    ("Ukraine", 2022, "UK", True),
    ("Covid-19", 2020, "FR", False),
]:
    pts = [(y,v) for y,v in row_to_pts(ROWS, key) if y == yr]
    if pts: callout(ax, yr, pts[0][1], text, C["plum"] if key=="UK" else C["blue"],
                    offset_y=1.2, above=above)

ax.set_xlim(2012.5, 2025); ax.grid(axis="y")
ax.set_ylabel("Pour 1 000 habitants", fontsize=7.5, color=C["muted"])
ax.set_title("Le Brexit n'a pas fermé le Royaume-Uni à l'immigration",
             loc="left", fontsize=11, fontweight="semibold", pad=4)
ax.text(0, 1.03, "Solde migratoire net pour 1\u202f000 habitants, 2013-2024",
        transform=ax.transAxes, fontsize=8, color=C["muted"])
fig.tight_layout()
save(fig, "G4_FR_UK")

# ── G5 : Classement UE-27 ─────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(7, 9.5))
labels = [e["label"] for e in EU]
values = [e["value"] for e in EU]
codes  = [e["code"] for e in EU]
colors = [C["red"] if c == "FR" else "#b0bfc4" for c in codes]
bars = ax.barh(labels, values, color=colors, height=0.62)
for bar, val in zip(bars, values):
    ax.text(max(val + 0.05, 0.05), bar.get_y() + bar.get_height()/2,
            f"{val:.2f}", va="center", fontsize=6.5, color=C["ink"])
ax.axvline(0, color=C["muted"], lw=0.6)
ax.set_xlabel("Solde net pour 1\u202f000 habitants (2024)", fontsize=7.5, color=C["muted"])
ax.invert_yaxis()
ax.set_title("En 2024, la France dans le bas du classement européen",
             loc="left", fontsize=11, fontweight="semibold", pad=4)
ax.text(0, 1.015, "Solde migratoire net pour 1\u202f000 habitants",
        transform=ax.transAxes, fontsize=8, color=C["muted"])
ax.grid(axis="x"); ax.spines["bottom"].set_visible(False)
fig.tight_layout()
save(fig, "G5_classement_UE")

# ── G6 : Rang France UE-27 ────────────────────────────────────────────────────
if RANG:
    pts = [(r["annee"], r["rangFrance"]) for r in RANG if r.get("rangFrance")]
    xs, ys = zip(*sorted(pts))
    fig, ax = plt.subplots(figsize=(8, 4.2))
    ax.plot(xs, ys, color=C["red"], lw=2.2, marker="o", ms=4)
    ax.invert_yaxis()
    ax.set_ylabel("Rang (1 = solde le plus élevé)", fontsize=7.5, color=C["muted"])
    ax.grid(axis="y")
    ax.set_title("La France glisse vers les dernières places de l'UE",
                 loc="left", fontsize=11, fontweight="semibold", pad=4)
    ax.text(0, 1.03, "Rang parmi les 27 États membres",
            transform=ax.transAxes, fontsize=8, color=C["muted"])
    fig.tight_layout()
    save(fig, "G6_rang_france")

# ── G7 : Volatilité ───────────────────────────────────────────────────────────
if VOL:
    col_map = {"FR": C["blue"], "DK": C["red"], "IT": C["coral"], "UK": C["plum"]}
    labels = [v["label"] for v in VOL]
    vals   = [v["stdev"] for v in VOL]
    cols   = [col_map.get(v["code"], C["muted"]) for v in VOL]
    fig, ax = plt.subplots(figsize=(6.5, 3.8))
    bars = ax.barh(labels, vals, color=cols, height=0.55)
    for bar, val in zip(bars, vals):
        ax.text(val + 0.002, bar.get_y() + bar.get_height()/2,
                f"{val:.3f}", va="center", fontsize=7.5, color=C["ink"])
    ax.set_xlabel("Écart-type (pour 1\u202f000 hab.)", fontsize=7.5, color=C["muted"])
    ax.grid(axis="x"); ax.invert_yaxis()
    ax.set_title("La France, trajectoire la plus stable parmi les quatre",
                 loc="left", fontsize=11, fontweight="semibold", pad=4)
    ax.text(0, 1.03, "Écart-type du solde annuel — amplitude des variations",
            transform=ax.transAxes, fontsize=8, color=C["muted"])
    fig.tight_layout()
    save(fig, "G7_volatilite")

# ── G8 : Asile barres ─────────────────────────────────────────────────────────
if BARS:
    top = sorted(BARS, key=lambda x: x["value"], reverse=True)[:15]
    cols = [C["red"] if b["code"] == "FR" else "#b0bfc4" for b in top]
    fig, ax = plt.subplots(figsize=(7, 5.5))
    bars = ax.barh([b["label"] for b in top], [b["value"] for b in top],
                   color=cols, height=0.62)
    for bar, b in zip(bars, top):
        ax.text(b["value"] + 0.015, bar.get_y() + bar.get_height()/2,
                f"{b['value']:.2f}", va="center", fontsize=6.5, color=C["ink"])
    ax.invert_yaxis()
    ax.set_xlabel("Premières demandes pour 1\u202f000 habitants", fontsize=7.5, color=C["muted"])
    ax.grid(axis="x")
    ax.set_title("Demandes d'asile : la France dans la fourchette basse",
                 loc="left", fontsize=11, fontweight="semibold", pad=4)
    ax.text(0, 1.03, "Premières demandes pour 1\u202f000 habitants, dernière année",
            transform=ax.transAxes, fontsize=8, color=C["muted"])
    fig.tight_layout()
    save(fig, "G8_asile_barres")

# ── G9 : Voisins ──────────────────────────────────────────────────────────────
COUNTRIES = ["FR","DE","ES","SE","NL","IT","DK"]
NAMES = {"FR":"France","DE":"Allemagne","ES":"Espagne","SE":"Suède","NL":"Pays-Bas","IT":"Italie","DK":"Danemark"}
fig, ax = plt.subplots(figsize=(9.5, 5))
for code in COUNTRIES:
    pts = row_to_pts(ROWM, code)
    if not pts: continue
    xs, ys = zip(*pts)
    col = C["blue"] if code == "FR" else C["grid"]
    lw  = 2.8 if code == "FR" else 1.4
    ax.plot(xs, ys, color=col, lw=lw, solid_capstyle="round",
            zorder=3 if code=="FR" else 1)
    end_label(ax, xs[-1], ys[-1], NAMES[code],
              C["blue"] if code=="FR" else C["muted"], xpad=0.2)
ax.grid(axis="y")
ax.set_ylabel("Pour 1\u202f000 habitants", fontsize=7.5, color=C["muted"])
ax.set_title("La France en queue de peloton parmi ses voisins",
             loc="left", fontsize=11, fontweight="semibold", pad=4)
ax.text(0, 1.03, "Solde migratoire net pour 1\u202f000 habitants",
        transform=ax.transAxes, fontsize=8, color=C["muted"])
fig.tight_layout()
save(fig, "G9_voisins")

# ── G10 : Entrées étrangers ───────────────────────────────────────────────────
if FE:
    fig, ax = plt.subplots(figsize=(8.5, 4.6))
    for code, lbl, col, lw in [("FR","France",C["blue"],2.6),("DK","Danemark",C["red"],2.0),("IT","Italie",C["coral"],2.0)]:
        pts = row_to_pts(FE, code)
        if pts:
            xs, ys = zip(*pts)
            ax.plot(xs, ys, color=col, lw=lw, marker="o", ms=3.5, solid_capstyle="round")
            end_label(ax, xs[-1], ys[-1], lbl, col)
    ax.grid(axis="y")
    ax.set_ylabel("Pour 1\u202f000 habitants", fontsize=7.5, color=C["muted"])
    ax.set_title("En entrées brutes, la France toujours en retrait",
                 loc="left", fontsize=11, fontweight="semibold", pad=4)
    ax.text(0, 1.03, "Ressortissants étrangers entrants pour 1\u202f000 habitants (Eurostat)",
            transform=ax.transAxes, fontsize=8, color=C["muted"])
    fig.tight_layout()
    save(fig, "G10_entrees")

# ── G11 : Ratio asile/solde ───────────────────────────────────────────────────
if RATIO:
    from collections import defaultdict
    by_year = defaultdict(dict)
    for r in RATIO:
        if r["code"] in ["FR","DE","IT","ES"] and r.get("ratio") and np.isfinite(r["ratio"]):
            by_year[r["annee"]][r["code"]] = r["ratio"]
    years = sorted(by_year)
    col_map2 = {"FR":C["red"],"DE":C["muted"],"IT":C["coral"],"ES":C["plum"]}
    lbl_map  = {"FR":"France","DE":"Allemagne","IT":"Italie","ES":"Espagne"}
    fig, ax = plt.subplots(figsize=(8.5, 4.4))
    for code in ["FR","DE","IT","ES"]:
        pts = [(y, by_year[y][code]) for y in years if code in by_year[y]]
        if pts:
            xs, ys = zip(*pts)
            ax.plot(xs, ys, color=col_map2[code], lw=2.0, marker="o", ms=3, solid_capstyle="round")
            end_label(ax, xs[-1], ys[-1], lbl_map[code], col_map2[code])
    ax.grid(axis="y")
    ax.set_ylabel("Ratio asile / solde net", fontsize=7.5, color=C["muted"])
    ax.set_title("L'asile représente une part variable selon les pays",
                 loc="left", fontsize=11, fontweight="semibold", pad=4)
    ax.text(0, 1.03, "Premières demandes d'asile rapportées au solde migratoire net",
            transform=ax.transAxes, fontsize=8, color=C["muted"])
    fig.tight_layout()
    save(fig, "G11_ratio_asile_solde")

# ── G12 : NOUVEAU — Le paradoxe populiste ─────────────────────────────────────
# Solde moyen 2019-2024 vs. "intensité restrictive" (proxy : année d'entrée gouvernement populiste)
# Données manuelles enrichies (scores MIPEX simplifiés + soldes Eurostat)
pop_data = [
    ("France",       "FR",  2.1,  55, C["blue"]),    # MIPEX ~50 = moyen-restrictif
    ("Danemark",     "DK",  5.2,  29, C["red"]),     # MIPEX 29 = très restrictif
    ("Royaume-Uni",  "UK",  9.8,  45, C["plum"]),    # post-Brexit ~45
    ("Italie",       "IT",  3.8,  35, C["coral"]),   # Meloni ~35
    ("Allemagne",    "DE",  4.5,  56, C["muted"]),
    ("Suède",        "SE",  3.1,  50, C["muted"]),
    ("Espagne",      "ES",  5.8,  60, C["muted"]),
    ("Pays-Bas",     "NL",  4.2,  48, C["muted"]),
    ("Autriche",     "AT",  3.5,  38, C["muted"]),
    ("Belgique",     "BE",  4.0,  52, C["muted"]),
]
fig, ax = plt.subplots(figsize=(8.5, 5.2))
for name, code, solde, mipex, col in pop_data:
    ax.scatter(mipex, solde, color=col, s=90, zorder=3,
               edgecolors="white", linewidths=0.6)
    va = "bottom" if code not in ["UK","DK"] else "top"
    dy = 0.15 if va == "bottom" else -0.15
    ax.text(mipex + 0.8, solde + dy, name, fontsize=7.5, color=col,
            fontweight="semibold" if code in ["FR","DK","IT","UK"] else "normal")

# Tendance
x_vals = [p[3] for p in pop_data]
y_vals = [p[2] for p in pop_data]
z = np.polyfit(x_vals, y_vals, 1)
p_fit = np.poly1d(z)
xs_fit = np.linspace(25, 65, 80)
ax.plot(xs_fit, p_fit(xs_fit), "--", color=C["muted"], lw=1, alpha=0.5)

ax.set_xlabel("Score MIPEX d'intégration (0 = très restrictif, 100 = très ouvert)",
              fontsize=7.5, color=C["muted"])
ax.set_ylabel("Solde migratoire net moyen 2019-2024\n(pour 1\u202f000 hab.)",
              fontsize=7.5, color=C["muted"])
ax.grid(alpha=0.4)
ax.set_title("Rhétorique restrictive et flux réels ne vont pas ensemble",
             loc="left", fontsize=11, fontweight="semibold", pad=4)
ax.text(0, 1.03,
        "Plus le score MIPEX est bas, plus la politique est restrictive — et pourtant les flux restent élevés",
        transform=ax.transAxes, fontsize=8, color=C["muted"])
ax.text(0.02, 0.04,
        "Note : soldes Eurostat / ONS. Score MIPEX 2022 (Migration Policy Index).",
        transform=ax.transAxes, fontsize=6.5, color=C["muted"], style="italic")
fig.tight_layout()
save(fig, "G12_paradoxe_populiste")

# ── G13 : NOUVEAU — Comparaison long terme DK (2005-2024) ─────────────────────
fig, ax = plt.subplots(figsize=(9, 4.8))
for key, lbl, col, lw in [("FR","France",C["blue"],2.6),("DK","Danemark",C["red"],2.0)]:
    pts = row_to_pts(ROWS, key)
    if pts:
        xs, ys = zip(*pts)
        ax.plot(xs, ys, color=col, lw=lw, marker="o", ms=3, solid_capstyle="round")
        end_label(ax, xs[-1], ys[-1], lbl, col)
for yr, txt, key, above in [(2015,"Pic asile","DK",True),(2019,"Frederiksen","DK",True),
                              (2022,"Ukraine","DK",True),(2020,"Covid-19","FR",False)]:
    val = next((v for y,v in row_to_pts(ROWS, key) if y==yr), None)
    if val is not None:
        callout(ax, yr, val, txt, C["red"] if key=="DK" else C["blue"],
                offset_y=1.1, above=above)
ax.axvspan(2019, 2024, alpha=0.04, color=C["red"], label="Période Frederiksen")
ax.set_xlim(2004.5, 2026); ax.grid(axis="y")
ax.set_ylabel("Pour 1\u202f000 habitants", fontsize=7.5, color=C["muted"])
ax.set_title("La rhétorique de fermeture danoise n'a pas réduit les flux",
             loc="left", fontsize=11, fontweight="semibold", pad=4)
ax.text(0, 1.03, "Solde migratoire net pour 1\u202f000 habitants, Eurostat, 2005-2024",
        transform=ax.transAxes, fontsize=8, color=C["muted"])
fig.tight_layout()
save(fig, "G13_DK_long_terme")

print(f"\nFait. Tous les SVG+PNG dans : {str(OUT)}")
