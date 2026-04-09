"""
Exporte un CSV par figure web (1–9) pour reprise dans Figma.
Format : UTF-8 avec BOM (Excel), virgule, schéma stable.

Exécution :
  python charts/export_figma_csv.py
"""

from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CHARTS_OUT = ROOT / "charts" / "output"
FIGMA_DIR = ROOT / "figma_csv"

C = {
    "ink": "#262626",
    "red": "#FF3F3F",
    "blue": "#2E879A",
    "plum": "#9D1453",
    "coral": "#F99592",
    "teal": "#1A4D5C",
    "peer_gray": "#B8B8B8",
    "bar_others": "#2E879A",  # remplissage barres fig. 7 (comme le site)
    "bar_muted": "#6B8F96",  # UE hors FR fig. 9
}

PEER_COLORS = [C["red"], C["blue"], C["plum"], C["coral"], C["teal"], C["ink"]]

DISPLAY = {
    "FR": "France (entière)",
    "FX": "France métropolitaine",
    "DK": "Danemark",
    "IT": "Italie",
    "UK": "Royaume-Uni",
    "DE": "Allemagne",
    "ES": "Espagne",
    "SE": "Suède",
    "NL": "Pays-Bas",
    "AT": "Autriche",
    "BE": "Belgique",
    "EL": "Grèce",
    "PL": "Pologne",
    "PT": "Portugal",
    "RO": "Roumanie",
    "BG": "Bulgarie",
    "HR": "Croatie",
    "CY": "Chypre",
    "CZ": "Tchéquie",
    "HU": "Hongrie",
    "IE": "Irlande",
    "LT": "Lituanie",
    "LU": "Luxembourg",
    "LV": "Lettonie",
    "MT": "Malte",
    "SI": "Slovénie",
    "SK": "Slovaquie",
    "EE": "Estonie",
    "FI": "Finlande",
}

ANNOTATIONS = {
    "DK": [(2015, "Pic UE (asile)", "peer"), (2022, "Ukraine", "peer")],
    "IT": [(2015, "Crise de l’asile", "IT"), (2022, "Ukraine", "IT"), (2023, "Meloni", "IT")],
    "UK": [(2014, "Asile", "peer"), (2015, "Brexit", "peer"), (2020, "Covid", "peer"), (2022, "Ukraine", "peer")],
}

POINT_FIELDS = [
    "ligne_type",
    "figure",
    "panneau",
    "code_serie",
    "libelle_legende",
    "annee",
    "valeur",
    "unite",
    "couleur_hex",
    "epaisseur_pt",
    "style_trait",
    "ordre_trace",
    "texte_annotation",
]


def _float(s: str | None) -> float | None:
    if s is None or not str(s).strip():
        return None
    try:
        return float(str(s).replace(",", "."))
    except ValueError:
        return None


def read_wide_year_cols(path: Path) -> list[dict]:
    if not path.exists():
        return []
    rows: list[dict] = []
    with path.open(encoding="utf-8", newline="") as f:
        r = csv.DictReader(f)
        for row in r:
            y = int(row["year"])
            d: dict = {"year": y}
            for k, v in row.items():
                if k == "year":
                    continue
                d[k] = _float(str(v) if v is not None else "")
            rows.append(d)
    return rows


def write_rows(path: Path, rows: list[dict]) -> None:
    FIGMA_DIR.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=POINT_FIELDS, extrasaction="ignore")
        w.writeheader()
        for row in rows:
            w.writerow(row)


def point_row(
    figure: str,
    panneau: str,
    code: str,
    label: str,
    year: int,
    value: float,
    unite: str,
    color: str,
    width: float,
    style: str,
    ordre: int,
) -> dict:
    return {
        "ligne_type": "point",
        "figure": figure,
        "panneau": panneau,
        "code_serie": code,
        "libelle_legende": label,
        "annee": year,
        "valeur": f"{value:.6g}".replace(",", "."),
        "unite": unite,
        "couleur_hex": color,
        "epaisseur_pt": str(width),
        "style_trait": style,
        "ordre_trace": str(ordre),
        "texte_annotation": "",
    }


def annotation_row(
    figure: str,
    panneau: str,
    code_cible: str,
    annee: int,
    texte: str,
    couleur: str,
) -> dict:
    return {
        "ligne_type": "annotation",
        "figure": figure,
        "panneau": panneau,
        "code_serie": code_cible,
        "libelle_legende": "",
        "annee": annee,
        "valeur": "",
        "unite": "",
        "couleur_hex": couleur,
        "epaisseur_pt": "",
        "style_trait": "",
        "ordre_trace": "",
        "texte_annotation": texte,
    }


def latest(rowlist: list[dict], key: str) -> tuple[int, float] | None:
    for row in reversed(rowlist):
        v = row.get(key)
        if v is not None:
            return (row["year"], float(v))
    return None


def export_fig1(sel: list[dict]) -> None:
    fig = "01_france_danemark"
    unite = "solde_net_pour_1000_hab_CNMIGRATRT"
    rows: list[dict] = []
    for row in sel:
        y = row["year"]
        for code, pan, col, sty, w, ordre in [
            ("FR", "haut_france", C["ink"], "solid", 3.0, 1),
            ("FX", "haut_france", C["blue"], "dashed", 2.25, 2),
            ("DK", "bas_danemark", C["red"], "solid", 2.55, 1),
        ]:
            v = row.get(code)
            if v is None:
                continue
            rows.append(point_row(fig, pan, code, DISPLAY[code], y, float(v), unite, col, w, sty, ordre))
    for y, txt, _ in ANNOTATIONS["DK"]:
        rows.append(annotation_row(fig, "bas_danemark", "DK", y, txt, C["red"]))
    write_rows(FIGMA_DIR / f"figure_{fig}.csv", rows)


def export_fig2(sel: list[dict]) -> None:
    fig = "02_france_italie"
    unite = "solde_net_pour_1000_hab_CNMIGRATRT"
    rows: list[dict] = []
    spec = [
        ("FR", "unique", C["ink"], "solid", 2.85, 1),
        ("FX", "unique", C["blue"], "dashed", 2.25, 2),
        ("IT", "unique", C["red"], "solid", 2.5, 3),
    ]
    for row in sel:
        y = row["year"]
        for code, pan, col, sty, w, ordre in spec:
            v = row.get(code)
            if v is None:
                continue
            rows.append(point_row(fig, pan, code, DISPLAY[code], y, float(v), unite, col, w, sty, ordre))
    for y, txt, _tgt in ANNOTATIONS["IT"]:
        rows.append(annotation_row(fig, "unique", "IT", y, txt, C["red"]))
    write_rows(FIGMA_DIR / f"figure_{fig}.csv", rows)


def export_fig3(sel: list[dict]) -> None:
    fig = "03_france_royaume_uni"
    unite = "solde_net_pour_1000_hab_FR_FX_Eurostat_UK_ONS"
    rows: list[dict] = []
    for row in sel:
        if row["year"] < 2008:
            continue
        y = row["year"]
        for code, pan, col, sty, w, ordre in [
            ("FR", "haut_france", C["ink"], "solid", 3.0, 1),
            ("FX", "haut_france", C["blue"], "dashed", 2.25, 2),
            ("UK", "bas_royaume_uni", C["red"], "solid", 2.55, 1),
        ]:
            v = row.get(code)
            if v is None:
                continue
            label = "Royaume-Uni (ONS)" if code == "UK" else DISPLAY[code]
            rows.append(point_row(fig, pan, code, label, y, float(v), unite, col, w, sty, ordre))
    for y, txt, _ in ANNOTATIONS["UK"]:
        rows.append(annotation_row(fig, "bas_royaume_uni", "UK", y, txt, C["red"]))
    write_rows(FIGMA_DIR / f"figure_{fig}.csv", rows)


def export_fig4(all_rows: list[dict]) -> None:
    fig = "04_france_vs_six_pays"
    unite = "solde_net_pour_1000_hab_CNMIGRATRT"
    eu_top = ["FR", "FX"]
    others = ["DE", "ES", "SE", "NL", "IT", "DK"]
    rows: list[dict] = []
    for row in all_rows:
        y = row["year"]
        for code in eu_top:
            v = row.get(code)
            if v is None:
                continue
            is_fx = code == "FX"
            rows.append(
                point_row(
                    fig,
                    "haut_france",
                    code,
                    DISPLAY[code],
                    y,
                    float(v),
                    unite,
                    C["blue"] if is_fx else C["ink"],
                    2.2 if is_fx else 3.0,
                    "dashed" if is_fx else "solid",
                    2 if is_fx else 1,
                )
            )
        for i, code in enumerate(others):
            v = row.get(code)
            if v is None:
                continue
            rows.append(
                point_row(
                    fig,
                    "bas_france_bleu_voisins_gris",
                    code,
                    DISPLAY[code],
                    y,
                    float(v),
                    unite,
                    C["peer_gray"],
                    1.85,
                    "solid",
                    i + 1,
                )
            )
        v_fr = row.get("FR")
        if v_fr is not None:
            rows.append(
                point_row(
                    fig,
                    "bas_france_bleu_voisins_gris",
                    "FR",
                    DISPLAY["FR"],
                    y,
                    float(v_fr),
                    unite,
                    C["blue"],
                    3.2,
                    "solid",
                    7,
                )
            )
    write_rows(FIGMA_DIR / f"figure_{fig}.csv", rows)


def export_fig5(asy: list[dict]) -> None:
    fig = "05_asile_lignes"
    unite = "premieres_demandes_asile_pour_1000_hab"
    codes = ["FR", "DE", "IT", "SE", "DK"]
    color_by_code = {"FR": (C["ink"], 3.0, 1)}
    peer_idx = 0
    for c in codes:
        if c == "FR":
            continue
        color_by_code[c] = (PEER_COLORS[peer_idx % len(PEER_COLORS)], 2.1, peer_idx + 2)
        peer_idx += 1
    rows: list[dict] = []
    for row in asy:
        if row["year"] < 2008:
            continue
        y = row["year"]
        for code in codes:
            v = row.get(code)
            if v is None:
                continue
            col, w, ordre = color_by_code[code]
            label = "France (entière)" if code == "FR" else DISPLAY[code]
            rows.append(point_row(fig, "unique", code, label, y, float(v), unite, col, w, "solid", ordre))
    write_rows(FIGMA_DIR / f"figure_{fig}.csv", rows)


def export_fig6(asy: list[dict]) -> None:
    fig = "06_asile_barres_derniere_annee"
    unite = "premieres_demandes_asile_pour_1000_hab"
    codes_ordre = ["DK", "SE", "NL", "FR", "AT", "IT", "DE", "BE", "ES"]
    if not asy:
        write_rows(FIGMA_DIR / f"figure_{fig}.csv", [])
        return
    last = asy[-1]
    y_ref = last["year"]
    tmp: list[tuple[str, float]] = []
    for code in codes_ordre:
        v = last.get(code)
        if v is None:
            continue
        tmp.append((code, float(v)))
    tmp.sort(key=lambda x: x[1])
    rows: list[dict] = []
    for rank, (code, v) in enumerate(tmp, start=1):
        coul = C["red"] if code == "FR" else C["blue"]
        rows.append(
            point_row(
                fig,
                "unique",
                code,
                f"{DISPLAY.get(code, code)} ({y_ref})",
                y_ref,
                v,
                unite,
                coul,
                2.0,
                "solid",
                rank,
            )
        )
    write_rows(FIGMA_DIR / f"figure_{fig}.csv", rows)


def export_fig7(mig_all: list[dict], asy: list[dict]) -> None:
    fig = "07_solde_net_vs_asile_derniere_dispo"
    unite_net = "solde_net_pour_1000_hab_CNMIGRATRT"
    unite_asy = "premieres_demandes_asile_pour_1000_hab"
    codes = ["FR", "SE", "IT", "DK", "DE", "NL", "ES"]
    net_rows: list[tuple[str, int, float]] = []
    asy_rows: list[tuple[str, int, float]] = []
    for code in codes:
        ln = latest(mig_all, code)
        if ln:
            net_rows.append((code, ln[0], float(ln[1])))
        la = latest(asy, code)
        if la:
            asy_rows.append((code, la[0], float(la[1])))
    net_rows.sort(key=lambda x: x[2])
    asy_rows.sort(key=lambda x: x[2])
    rows: list[dict] = []
    for rank, (code, y, v) in enumerate(net_rows, start=1):
        rows.append(
            point_row(
                fig,
                "gauche_solde_net",
                code,
                f"{DISPLAY[code]} ({y})",
                y,
                v,
                unite_net,
                C["bar_others"],
                2.0,
                "solid",
                rank,
            )
        )
    for rank, (code, y, v) in enumerate(asy_rows, start=1):
        rows.append(
            point_row(
                fig,
                "droite_asile",
                code,
                f"{DISPLAY[code]} ({y})",
                y,
                v,
                unite_asy,
                C["bar_others"],
                2.0,
                "solid",
                rank,
            )
        )
    write_rows(FIGMA_DIR / f"figure_{fig}.csv", rows)


def export_fig8(sel: list[dict]) -> None:
    fig = "08_snapshot_solde_net_derniere_serie"
    unite = "solde_net_pour_1000_hab"
    bar_color = {"ink": C["ink"], "blue": C["blue"], "red": C["red"], "plum": C["plum"], "teal": C["teal"]}
    codes = ["FR", "DK", "IT", "UK"]
    fx_lv = latest(sel, "FX")
    if fx_lv and fx_lv[0] >= 2023:
        codes = ["FR", "FX", "DK", "IT", "UK"]
    rows: list[dict] = []
    snapshots: list[tuple[str, int, float, str]] = []
    for code in codes:
        ln = latest(sel, code)
        if not ln:
            continue
        y, v = ln
        bk = "ink"
        if code == "FX":
            bk = "blue"
        elif code == "IT":
            bk = "red"
        elif code == "DK":
            bk = "plum"
        elif code == "UK":
            bk = "teal"
        snapshots.append((code, y, float(v), bk))
    snapshots.sort(key=lambda x: x[2])
    for rank, (code, y, v, bk) in enumerate(snapshots, start=1):
        label = DISPLAY.get(code, code)
        rows.append(
            point_row(
                fig,
                "unique",
                code,
                f"{label} ({y})",
                y,
                v,
                unite,
                bar_color.get(bk, C["ink"]),
                2.0,
                "solid",
                rank,
            )
        )
    write_rows(FIGMA_DIR / f"figure_{fig}.csv", rows)


def export_fig9() -> None:
    fig = "09_classement_ue27_CNMIGRATRT_2024"
    path = CHARTS_OUT / "eu27_cnmigratrt_2024_from_api.csv"
    if not path.exists():
        write_rows(FIGMA_DIR / f"figure_{fig}.csv", [])
        return
    unite = "solde_net_pour_1000_hab_CNMIGRATRT_2024"
    rows: list[dict] = []
    parsed: list[tuple[str, float]] = []
    with path.open(encoding="utf-8", newline="") as f:
        r = csv.DictReader(f)
        for row in r:
            geo = (row.get("geo") or "").strip()
            if not geo:
                continue
            try:
                v = float(str(row.get("OBS_VALUE", "")).replace(",", "."))
            except ValueError:
                continue
            parsed.append((geo, v))
    parsed.sort(key=lambda x: x[1])
    for rank, (geo, v) in enumerate(parsed, start=1):
        label = f"{DISPLAY.get(geo, geo)} ({geo})"
        col = C["red"] if geo == "FR" else C["bar_muted"]
        rows.append(point_row(fig, "unique", geo, label, 2024, v, unite, col, 2.0, "solid", rank))
    write_rows(FIGMA_DIR / f"figure_{fig}.csv", rows)


def main() -> None:
    sel = read_wide_year_cols(CHARTS_OUT / "cnmigratrt_2005_2024_selection.csv")
    all_mig = read_wide_year_cols(CHARTS_OUT / "cnmigratrt_2005_2024_tous_pays.csv") or sel
    asy = read_wide_year_cols(CHARTS_OUT / "asile_premieres_demandes_pour_1000.csv")

    export_fig1(sel)
    export_fig2(sel)
    export_fig3(sel)
    export_fig4(all_mig)
    export_fig5(asy)
    export_fig6(asy)
    export_fig7(all_mig, asy)
    export_fig8(sel)
    export_fig9()

    print(f"OK — {FIGMA_DIR} : 9 fichiers figure_XX_*.csv (UTF-8 BOM).")


if __name__ == "__main__":
    main()
