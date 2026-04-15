"""
Construit site/data.json à partir des CSV générés par charts/plot_publication.py.
Exécution : python build_data.py (depuis le dossier site/) ou python site/build_data.py depuis Migrations/.
"""

from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CHARTS_OUT = ROOT / "charts" / "output"
SITE = Path(__file__).resolve().parent
EU_CSV_LEGACY = ROOT / "estat_demo_gind_filtered_en (1).csv"
EU_CSV_FROM_API = CHARTS_OUT / "eu27_cnmigratrt_2024_from_api.csv"

EU27 = frozenset(
    "AT BE BG HR CY CZ DK EE FI FR DE EL HU IE IT LV LT LU MT NL PL PT RO SK SI ES SE".split()
)

UK_SOURCE_FOOTNOTE = (
    "UK : solde net long terme (ONS). France : Eurostat CNMIGRATRT. "
    "Dénominateur 1 000 hab. : demo_pjan ou estimations ONS selon la série. "
    "Les deux pays ne suivent pas la même méthode."
)

MIGRATION_FOOTER = "Source : Eurostat, demo_gind, CNMIGRATRT, pour 1 000 habitants."

ASYLUM_FOOTER_SHORT = "Source : Eurostat, migr_asyappctza et demo_pjan."

_MONTHS_FR = (
    "janvier",
    "février",
    "mars",
    "avril",
    "mai",
    "juin",
    "juillet",
    "août",
    "septembre",
    "octobre",
    "novembre",
    "décembre",
)


def _date_fr_utc(iso: str) -> str:
    dt = datetime.fromisoformat(iso.replace("Z", "+00:00"))
    return f"{dt.day} {_MONTHS_FR[dt.month - 1]} {dt.year}"


# Événements calés sur les graphiques du texte Terra Nova (Word) + lecture presse.
ANNOTATIONS_FR = [
    {"year": 2015, "text": "Pic de l'asile", "target": "FR"},
    {"year": 2020, "text": "Covid-19", "target": "FR"},
]

ANNOTATIONS = {
    "DK": [
        {"year": 2015, "text": "Pic de l'asile", "target": "peer"},
        {"year": 2019, "text": "Frederiksen PM", "target": "peer"},
        {"year": 2022, "text": "Ukraine", "target": "peer"},
    ],
    "UK": [
        {"year": 2015, "text": "Pic de l'asile", "target": "peer"},
        {"year": 2016, "text": "Brexit", "target": "peer"},
        {"year": 2021, "text": "Fin libre circ.", "target": "peer"},
        {"year": 2022, "text": "Ukraine", "target": "peer"},
    ],
}

ANNOTATIONS_IT = [
    {"year": 2015, "text": "Pic de l'asile", "target": "IT"},
    {"year": 2018, "text": "Salvini ministre", "target": "IT"},
    {"year": 2020, "text": "Covid-19", "target": "IT"},
    {"year": 2022, "text": "G. Meloni PM", "target": "IT"},
]

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


def _float_cell(s: str | None) -> float | None:
    if s is None or not str(s).strip():
        return None
    try:
        return float(str(s).replace(",", "."))
    except ValueError:
        return None


def read_wide_migration(path: Path) -> list[dict]:
    rows: list[dict] = []
    if not path.exists():
        return rows
    with path.open(encoding="utf-8", newline="") as f:
        r = csv.DictReader(f)
        for row in r:
            y = int(row["year"])
            d: dict = {"year": y}
            for k, v in row.items():
                if k == "year":
                    continue
                d[k] = _float_cell(v)
            rows.append(d)
    return rows


def read_asile(path: Path) -> list[dict]:
    return read_wide_migration(path)


def latest_non_null(rows: list[dict], key: str) -> tuple[int, float] | None:
    for row in reversed(rows):
        v = row.get(key)
        if v is not None:
            return (row["year"], v)
    return None


def eu_ranking_2024() -> list[dict]:
    path = EU_CSV_FROM_API if EU_CSV_FROM_API.exists() else EU_CSV_LEGACY
    if not path.exists():
        return []
    by_geo: dict[str, dict[int, float | None]] = {}
    with path.open(encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            geo = (row.get("geo") or "").strip()
            if geo not in EU27:
                continue
            try:
                y = int(row["TIME_PERIOD"])
            except (ValueError, KeyError):
                continue
            v = _float_cell(row.get("OBS_VALUE"))
            by_geo.setdefault(geo, {})[y] = v
    out: list[dict] = []
    for geo, yd in by_geo.items():
        v = yd.get(2024)
        if v is not None:
            out.append(
                {
                    "code": geo,
                    "label": f"{DISPLAY.get(geo, geo)} ({geo})",
                    "value": round(v, 4),
                }
            )
    out.sort(key=lambda x: x["value"])
    return out


def load_analyse_rang_france(path: Path) -> list[dict]:
    """CSV généré par charts/analyses_terra_nova.py."""
    if not path.exists():
        return []
    out: list[dict] = []
    with path.open(encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            try:
                a = int(row["annee"])
            except (KeyError, ValueError):
                continue
            rf = (row.get("rang_france") or "").strip()
            vf = (row.get("valeur_fr") or "").strip()
            nb = (row.get("nb_pays") or "").strip()
            med = (row.get("mediane_ue27") or "").strip()
            out.append(
                {
                    "annee": a,
                    "rangFrance": int(rf) if rf.isdigit() else None,
                    "nbPays": int(nb) if nb.isdigit() else None,
                    "valeurFr": _float_cell(vf),
                    "medianeUe27": _float_cell(med),
                }
            )
    return out


def read_foreign_entries(path: Path) -> list[dict]:
    """Eurostat migr_imm1ctz FOR_STLS / demo_pjan, pour 1 000 hab.
    Complète avec les données ONS pour le Royaume-Uni après 2019 (Eurostat indisponible post-Brexit).
    Source ONS LTIM : immigration de non-UK nationals, estimation cohérente avec la série pré-2020.
    """
    rows = read_wide_migration(path) if path.exists() else []
    # UK ONS entries post-2019 (non-UK nationals / population UK)
    uk_ons = {2020: 9.0, 2021: 12.4, 2022: 17.0, 2023: 18.0, 2024: 13.8}
    for row in rows:
        yr = row.get("year")
        if yr in uk_ons and (row.get("UK") is None):
            row["UK"] = uk_ons[yr]
    return rows


def load_volatility_core(path: Path) -> list[dict]:
    """CSV généré par charts/analyses_terra_nova.run_volatility_core."""
    if not path.exists():
        return []
    out: list[dict] = []
    with path.open(encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            code = (row.get("code") or "").strip()
            if not code:
                continue
            sd = _float_cell(row.get("stdev"))
            if sd is None:
                continue
            ylo = row.get("year_lo") or ""
            yhi = row.get("year_hi") or ""
            out.append(
                {
                    "code": code,
                    "label": (row.get("libelle") or code).strip(),
                    "yearLo": int(ylo) if str(ylo).isdigit() else None,
                    "yearHi": int(yhi) if str(yhi).isdigit() else None,
                    "n": int(row["n"]) if (row.get("n") or "").strip().isdigit() else None,
                    "stdev": round(sd, 4),
                    "mean": _float_cell(row.get("mean")),
                }
            )
    out.sort(key=lambda x: x["stdev"])
    return out


def load_analyse_ratio_asile_solde(path: Path) -> list[dict]:
    if not path.exists():
        return []
    out: list[dict] = []
    with path.open(encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            try:
                a = int(row["annee"])
            except (KeyError, ValueError):
                continue
            ratio_s = (row.get("ratio_asile_sur_solde") or "").strip()
            net_s = (row.get("solde_net") or "").strip()
            asy_s = (row.get("asile_premieres") or "").strip()
            ratio = _float_cell(ratio_s) if ratio_s else None
            out.append(
                {
                    "annee": a,
                    "code": (row.get("code") or "").strip(),
                    "libelle": (row.get("libelle") or "").strip(),
                    "soldeNet": _float_cell(net_s),
                    "asilePremieres": _float_cell(asy_s),
                    "ratio": ratio,
                }
            )
    return out


def snapshot_rows(mig: list[dict]) -> list[dict]:
    codes = ["FR", "DK", "IT", "UK"]
    rows = []
    for c in codes:
        lv = latest_non_null(mig, c)
        if lv:
            name = DISPLAY.get(c, c)
            bar = "ink"
            if c == "FR":
                bar = "ink"
            elif c == "FX":
                bar = "blue"
            elif c == "IT":
                bar = "red"
            elif c == "DK":
                bar = "plum"
            elif c == "UK":
                bar = "teal"
            rows.append(
                {
                    "code": c,
                    "label": name,
                    "year": lv[0],
                    "value": round(lv[1], 4),
                    "barKey": bar,
                    "yLabel": f"{name} ({lv[0]})",
                }
            )
    rows.sort(key=lambda x: x["value"])
    return rows


def snapshot_ratio_line(rows: list[dict]) -> str:
    def by_code(code: str) -> float | None:
        for r in rows:
            if r.get("code") == code:
                return r["value"]
        return None

    fr_v = by_code("FR")
    it_v = by_code("IT")
    dk_v = by_code("DK")
    uk_v = by_code("UK")
    bits: list[str] = []
    if fr_v and fr_v != 0:
        if it_v:
            bits.append(f"IT / FR ×{it_v / fr_v:.2f}")
        if dk_v:
            bits.append(f"DK / FR ×{dk_v / fr_v:.2f}")
        if uk_v:
            bits.append(f"UK / FR ×{uk_v / fr_v:.2f}")
    return " ".join(bits)


def dual_panel_latest(mig: list[dict], asy: list[dict], codes: list[str]) -> tuple[list[dict], list[dict]]:
    net_rows = []
    asy_rows = []
    for c in codes:
        ln = latest_non_null(mig, c)
        la = latest_non_null(asy, c)
        if ln:
            net_rows.append(
                {"code": c, "label": f"{DISPLAY.get(c, c)} ({ln[0]})", "year": ln[0], "value": round(ln[1], 4)}
            )
        if la:
            asy_rows.append(
                {"code": c, "label": f"{DISPLAY.get(c, c)} ({la[0]})", "year": la[0], "value": round(la[1], 4)}
            )
    net_rows.sort(key=lambda x: x["value"])
    asy_rows.sort(key=lambda x: x["value"])
    return net_rows, asy_rows


# ── Données statistiques nationales (hors Eurostat harmonisé) ─────────────────
# Sources :
#   - INSEE : solde migratoire des immigrés (nés étrangers à l'étranger), France métropolitaine.
#     Série officielle disponible jusqu'en 2021 ; 2022-2024 = estimation (94 000 sorties/an).
#   - Statistics Denmark (statistikbanken.dk) : solde migratoire des étrangers (citizenship-based).
#   - Istat (demo.istat.it) : solde migratoire des étrangers, Italie.
#   - ONS Long-Term International Migration (LTIM), Royaume-Uni : solde net global étrangers
#     + décomposition UE / non-UE en valeur absolue (milliers).
# Population de référence : estimations nationales (France 68M, DK 5.9M, IT 59M, UK 67M).
NATIONAL_STATS = {
    # ── Solde immigrés France (INSEE) ──────────────────────────────────────────
    # Taux pour 1 000 habitants. 2022-2024 en italique = estimation.
    "frImmigres": [
        {"year": 2013, "value": 2.94, "estimated": False},
        {"year": 2014, "value": 2.82, "estimated": False},
        {"year": 2015, "value": 2.94, "estimated": False},
        {"year": 2016, "value": 2.97, "estimated": False},
        {"year": 2017, "value": 3.09, "estimated": False},
        {"year": 2018, "value": 3.22, "estimated": False},
        {"year": 2019, "value": 3.35, "estimated": False},
        {"year": 2020, "value": 2.35, "estimated": False},
        {"year": 2021, "value": 3.09, "estimated": False},
        {"year": 2022, "value": 3.82, "estimated": True},
        {"year": 2023, "value": 3.97, "estimated": True},
        {"year": 2024, "value": 3.82, "estimated": True},
    ],
    # ── Solde étrangers Danemark (Statistics Denmark) ──────────────────────────
    "dkEtrangers": [
        {"year": 2013, "value": 4.1},
        {"year": 2014, "value": 5.4},
        {"year": 2015, "value": 7.4},
        {"year": 2016, "value": 1.5},
        {"year": 2017, "value": 3.4},
        {"year": 2018, "value": 3.5},
        {"year": 2019, "value": 1.1},
        {"year": 2020, "value": 1.0},
        {"year": 2021, "value": 2.2},
        {"year": 2022, "value": 10.1},
        {"year": 2023, "value": 5.5},
        {"year": 2024, "value": 5.1},
    ],
    # ── Solde étrangers Italie (Istat) ─────────────────────────────────────────
    "itEtrangers": [
        {"year": 2014, "value": 3.2},
        {"year": 2015, "value": 3.0},
        {"year": 2016, "value": 3.8},
        {"year": 2017, "value": 4.3},
        {"year": 2018, "value": 4.2},
        {"year": 2019, "value": 3.0},
        {"year": 2020, "value": 2.6},
        {"year": 2021, "value": 3.0},
        {"year": 2022, "value": 4.8},
        {"year": 2023, "value": 5.6},
    ],
    # ── Solde étrangers Royaume-Uni (ONS LTIM) ─────────────────────────────────
    "ukEtrangers": [
        {"year": 2014, "value": 5.1},
        {"year": 2015, "value": 5.5},
        {"year": 2016, "value": 6.0},
        {"year": 2017, "value": 4.5},
        {"year": 2018, "value": 4.6},
        {"year": 2019, "value": 4.6},
        {"year": 2020, "value": 3.5},
        {"year": 2021, "value": 5.0},
        {"year": 2022, "value": 11.8},
        {"year": 2023, "value": 14.9},
    ],
    # ── Solde total Italie Eurostat (nationaux inclus) — pour comparaison méthodologique ──
    # Eurostat CNMIGRATRT = total (nationaux + étrangers). Istat = étrangers seulement.
    # L'écart en 2020 (-1.2 Eurostat vs +2.6 Istat) s'explique par la migration des Italiens eux-mêmes.
    "itEurostatNet": [
        {"year": 2014, "value": 0.8},
        {"year": 2015, "value": 0.5},
        {"year": 2016, "value": 0.7},
        {"year": 2017, "value": 1.0},
        {"year": 2018, "value": 1.2},
        {"year": 2019, "value": 0.7},
        {"year": 2020, "value": -1.2},
        {"year": 2021, "value": 1.6},
        {"year": 2022, "value": 4.9},
        {"year": 2023, "value": 4.5},
    ],
    # ── Décomposition UK par origine (ONS LTIM) — milliers, valeurs nettes ─────
    # La substitution UE → non-UE post-Brexit est l'argument central.
    "ukByOrigin": [
        {"year": 2012, "eu": 62,  "nonEu": 185},
        {"year": 2013, "eu": 75,  "nonEu": 205},
        {"year": 2014, "eu": 110, "nonEu": 228},
        {"year": 2015, "eu": 133, "nonEu": 235},
        {"year": 2016, "eu": 122, "nonEu": 278},
        {"year": 2017, "eu": 84,  "nonEu": 213},
        {"year": 2018, "eu": 88,  "nonEu": 224},
        {"year": 2019, "eu": 56,  "nonEu": 280},
        {"year": 2020, "eu": 10,  "nonEu": 156},
        {"year": 2021, "eu": -16, "nonEu": 338},
        {"year": 2022, "eu": -17, "nonEu": 757},
        {"year": 2023, "eu": -30, "nonEu": 1058},
        {"year": 2024, "eu": -37, "nonEu": 832},
        {"year": 2025, "eu": -38, "nonEu": 408},
    ],
    # Premiers titres de séjour par motif (Eurostat migr_resfirst, 2022, pour 1 000 habitants)
    # Source : Eurostat / Home Office UK. Arrondis à une décimale.
    "permitsMotif": [
        {"pays": "France",      "code": "FR", "travail": 1.6, "famille": 2.2, "etudes": 1.4, "protection": 0.5},
        {"pays": "Danemark",    "code": "DK", "travail": 5.3, "famille": 2.3, "etudes": 1.0, "protection": 1.0},
        {"pays": "Italie",      "code": "IT", "travail": 1.4, "famille": 0.5, "etudes": 0.2, "protection": 0.3},
        {"pays": "Royaume-Uni", "code": "UK", "travail": 4.1, "famille": 1.8, "etudes": 7.1, "protection": 1.2},
    ],
    # Taux de reconnaissance asile (EUAA / Eurostat migr_asydcfsta, 2022, %)
    # Décisions positives (Convention de Genève + protection subsidiaire + humanitaire) / total.
    "asileRecognition": [
        {"pays": "Royaume-Uni", "code": "UK", "taux": 67},
        {"pays": "Suède",       "code": "SE", "taux": 54},
        {"pays": "Allemagne",   "code": "DE", "taux": 47},
        {"pays": "France",      "code": "FR", "taux": 37},
        {"pays": "Danemark",    "code": "DK", "taux": 23},
        {"pays": "Italie",      "code": "IT", "taux": 20},
    ],
}


def main() -> None:
    mig_sel = read_wide_migration(CHARTS_OUT / "cnmigratrt_2005_2024_selection.csv")
    mig_all = read_wide_migration(CHARTS_OUT / "cnmigratrt_2005_2024_tous_pays.csv")
    asy = read_asile(CHARTS_OUT / "asile_premieres_demandes_pour_1000.csv")

    fig7_codes = ["FR", "SE", "IT", "DK", "DE", "NL", "ES"]
    net7, asy7 = dual_panel_latest(mig_all if mig_all else mig_sel, asy, fig7_codes)

    asy2024_bars = []
    if asy:
        last = asy[-1]
        y = last["year"]
        for code in ["DK", "SE", "NL", "FR", "AT", "IT", "DE", "BE", "ES"]:
            v = last.get(code)
            if v is not None:
                asy2024_bars.append(
                    {"code": code, "label": f"{DISPLAY.get(code, code)} ({y})", "value": round(v, 4)}
                )
        asy2024_bars.sort(key=lambda x: x["value"])

    snap = snapshot_rows(mig_sel)
    gen_iso = datetime.now(timezone.utc).isoformat()
    date_pub = _date_fr_utc(gen_iso)

    payload = {
        "meta": {
            "generated": gen_iso,
            "indicator": "CNMIGRATRT",
            "unit": "Pour 1 000 habitants",
            "notes": [],
            "datePublicationFr": date_pub,
        },
        "copy": {
            "migrationFooter": MIGRATION_FOOTER,
            "migrationSourceShort": "Source : Eurostat, demo_gind, CNMIGRATRT.",
            "migrationSourceUkShort": "Source : Eurostat ou ONS pour le UK (long terme).",
            "migrationFooterUk": MIGRATION_FOOTER + " " + UK_SOURCE_FOOTNOTE,
            "asylumFooter": (
                f"Sources : Eurostat, statistiques sur les demandeurs d’asile (première demande dans l’année) et "
                f"population au 1er janvier. Taux pour mille habitants ; ce n’est pas le solde migratoire net. "
                f"Détail technique : fichier METHODOLOGIE_SERIES.txt (dossier projet). Données extraites le {date_pub}."
            ),
            "dualFooter": (
                f"Sources : Eurostat (soldes migratoires nets, base démographique harmonisée) et Eurostat "
                f"(premières demandes d’asile, croisée avec la population au 1er janvier). "
                f"Chaque pays est à sa dernière année disponible pour l’indicateur. "
                f"Fichiers agrégés pour cette page le {date_pub}."
            ),
            "euFooter": (
                f"Sources : Eurostat, comptes démographiques harmonisés (solde migratoire net pour mille habitants), "
                f"millésime 2024 pour chaque pays de l’UE à 27 membres ayant transmis une valeur. "
                f"Données extraites le {date_pub}. Plus d’informations : ec.europa.eu/eurostat."
            ),
            "snapshotFooter": MIGRATION_FOOTER + " " + UK_SOURCE_FOOTNOTE
            + (" " + snapshot_ratio_line(snap) if snap else ""),
            "ukFootnote": UK_SOURCE_FOOTNOTE,
            "analyseRangFooter": (
                f"Sources : Eurostat, même indicateur de solde net (pour mille habitants). "
                f"Le rang 1 désigne le pays de l’UE-27 avec le solde le plus élevé pour l’année considérée. "
                f"Calculs à partir des séries téléchargées le {date_pub}."
            ),
            "analyseRatioFooter": (
                f"Sources : Eurostat. Numérateur : premières demandes d’asile (statistiques officielles des pays) ; "
                f"dénominateur : solde migratoire net lorsqu’il est strictement positif. "
                f"Lecture : plus le ratio est haut, plus l’asile représente une part marquée par rapport au solde net. "
                f"Données consolidées le {date_pub}."
            ),
            "analyseQuadriFooter": (
                f"Sources : Eurostat, indicateur harmonisé de solde migratoire net (pour mille habitants), "
                f"pour la France, l’Allemagne, l’Italie et l’Espagne. Extrait le {date_pub}."
            ),
            "volatilityFooter": (
                f"Sources : Eurostat pour la France, le Danemark et l’Italie ; Office for National Statistics (ONS) "
                f"pour le Royaume-Uni (série du solde de longue durée, non strictement identique). "
                f"La hauteur de chaque barre correspond à l’écart-type des taux annuels sur la fenêtre indiquée : "
                f"elle décrit les à-coups, pas le niveau moyen d’immigration. Agrégation le {date_pub}."
            ),
            "entreesFooter": (
                f"Sources : Eurostat, statistiques annuelles d’immigration (ressortissants étrangers et apatrides, "
                f"FOR_STLS) et effectifs de population au 1er janvier. Les taux sont pour mille habitants. "
                f"UK 2020-2024 : ONS Long-Term International Migration (estimation cohérente). Rupture méthodologique UK en 2020. "
                f"Extrait le {date_pub}."
            ),
            "asylumBarsFooter": (
                f"Sources : Eurostat, statistiques sur les demandeurs d’asile (première demande déposée dans l’année), "
                f"rapportées à la population au 1er janvier (démographie). Les pays peuvent réviser leurs chiffres ; "
                f"dernière année présente dans notre fichier : voir l’étiquette de chaque barre. "
                f"Données téléchargées et traitées le {date_pub}."
            ),
            "overviewFooter": (
                f"Sources : Eurostat (soldes migratoires nets harmonisés, pour mille habitants) pour la France, "
                f"le Danemark et l’Italie ; Office for National Statistics pour le Royaume-Uni (migrations internationales "
                f"de longue durée, autre définition). Les courbes ne sont donc pas strictement comparables point à point "
                f"entre la France et le Royaume-Uni. Agrégation pour cette visualisation : {date_pub}. "
                f"Liens utiles : ec.europa.eu/eurostat et ons.gov.uk."
            ),
        },
        "annotations": {
            "FR": ANNOTATIONS_FR,
            "DK": ANNOTATIONS["DK"],
            "UK": ANNOTATIONS["UK"],
            "IT": ANNOTATIONS_IT,
        },
        "asylumLineCodes": ["FR", "DE", "IT", "SE", "DK"],
        "migrationSelection": mig_sel,
        "migrationMulti": mig_all,
        "asylum": asy,
        "euRanking2024": eu_ranking_2024(),
        "snapshot": snap,
        "asylumBars2024": asy2024_bars,
        "dualNetAsylum2024": {"net": net7, "asylum": asy7},
        "analyseRangFrance": load_analyse_rang_france(CHARTS_OUT / "analyse_rang_france_ue27.csv"),
        "analyseRatioAsileSolde": load_analyse_ratio_asile_solde(CHARTS_OUT / "analyse_ratio_asile_solde_net.csv"),
        "volatilitySoldeCore": load_volatility_core(CHARTS_OUT / "analyse_volatility_solde_fr_dk_it_uk.csv"),
        "foreignEntries": read_foreign_entries(CHARTS_OUT / "entrees_etrangers_pour_1000.csv"),
        # Statistiques nationales (hors Eurostat) — sources officielles, granularité supérieure
        "nationalStats": NATIONAL_STATS,
    }

    SITE.mkdir(parents=True, exist_ok=True)
    out_path = SITE / "data.json"
    out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Écrit {out_path} ({len(mig_sel)} années migration, EU={len(payload['euRanking2024'])}).")


if __name__ == "__main__":
    main()
