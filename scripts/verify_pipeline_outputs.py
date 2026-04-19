"""
Contrôle post-pipeline : compare les CSV charts/output aux API Eurostat / cache ONS.
Usage (depuis la racine Migrations) : python scripts/verify_pipeline_outputs.py
"""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CHARTS = ROOT / "charts"
OUT = CHARTS / "output"
CACHE_ONS = CHARTS / "cache" / "ons" / "ons_ltim_net_ye_dec.json"

# Import après ajout du chemin charts (même layout que refresh_and_publish)
sys.path.insert(0, str(CHARTS))
from eurostat_api import fetch_dataset, parse_geo_time, per_1000_hab  # noqa: E402
from eurostat_migration import fetch_cnmigratrt, parse_to_series, write_eu27_cnmigratrt_2024_csv  # noqa: E402
from uk_ons_series import uk_rate_per_1000_series  # noqa: E402


def _read_selection(path: Path) -> list[dict]:
    with path.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def _f(x: str) -> float | None:
    s = (x or "").strip()
    if not s:
        return None
    try:
        return float(s.replace(",", "."))
    except ValueError:
        return None


def _near(a: float, b: float, eps: float = 0.06) -> bool:
    return abs(a - b) <= eps


def main() -> int:
    sel_path = OUT / "cnmigratrt_2005_2024_selection.csv"
    eu_path = OUT / "eu27_cnmigratrt_2024_from_api.csv"
    errors: list[str] = []

    if not sel_path.exists():
        print("ERREUR :", sel_path, "manquant — lancer python charts/refresh_and_publish.py")
        return 2

    rows = _read_selection(sel_path)
    last = rows[-1]
    year = int(last["year"])
    if year != 2024:
        errors.append(f"Dernière année attendue 2024, trouvé {year}")

    geos_check = ["FR", "DK", "IT"]
    print("Contrôle CNMIGRATRT (API Eurostat vs", sel_path.name, ")…")
    payload = fetch_cnmigratrt(geos_check, list(range(2020, 2025)))
    api = parse_to_series(payload)
    for g in geos_check:
        api_by_y = {y: v for y, v in api[g] if v is not None}
        for y in (2022, 2023, 2024):
            csv_v = _f(last[g] if y == 2024 else next(r for r in rows if int(r["year"]) == y)[g])
            api_v = api_by_y.get(y)
            if api_v is None:
                errors.append(f"{g} {y} : pas de valeur API")
                continue
            if csv_v is None:
                errors.append(f"{g} {y} : pas de valeur CSV")
                continue
            if not _near(csv_v, api_v):
                errors.append(f"{g} {y} : CSV={csv_v} API={api_v} (écart > 0.06)")

    # UK = ONS (pas Eurostat dans la sélection)
    uk_csv = _f(last["UK"])
    uk_expected = uk_rate_per_1000_series(2024, 2024)[0][1]
    if uk_csv is None or uk_expected is None:
        errors.append("UK 2024 : valeur manquante")
    elif not _near(uk_csv, uk_expected, eps=0.02):
        errors.append(f"UK 2024 : CSV={uk_csv} attendu (ONS/repli)={uk_expected}")

    print("Contrôle EU27 2024 (régénération API vs fichier)…")
    tmp = OUT / "_verify_eu27_2024.csv"
    if write_eu27_cnmigratrt_2024_csv(tmp, year=2024):
        def load_eu(p: Path) -> dict[str, float]:
            out: dict[str, float] = {}
            with p.open(encoding="utf-8", newline="") as f:
                r = csv.DictReader(f)
                for row in r:
                    g = (row.get("geo") or "").strip()
                    v = _f(row.get("OBS_VALUE", ""))
                    if g and v is not None:
                        out[g] = v
            return out

        disk = load_eu(eu_path) if eu_path.exists() else {}
        fresh = load_eu(tmp)
        for geo, v in fresh.items():
            d = disk.get(geo)
            if d is None:
                errors.append(f"EU27 fichier : {geo} manquant")
            elif not _near(d, v, eps=0.05):
                errors.append(f"EU27 {geo} 2024 : fichier={d} API={v}")
        tmp.unlink(missing_ok=True)
    else:
        errors.append("Échec téléchargement EU27 2024")

    if CACHE_ONS.exists():
        meta = json.loads(CACHE_ONS.read_text(encoding="utf-8"))
        print("ONS cache :", meta.get("xlsx_file") or meta.get("source_url", "(métadonnées)"))
    else:
        print("Avertissement : pas de cache ONS — UK non vérifié contre XLSX")

    asy_path = OUT / "asile_premieres_demandes_pour_1000.csv"
    if asy_path.exists():
        print("Contrôle asile 2024 (migr_asyappctza + demo_pjan vs", asy_path.name, ")…")
        geos = ["FR", "DE", "IT"]
        asylum_p = [
            ("freq", "A"),
            ("citizen", "TOTAL"),
            ("applicant", "FRST"),
            ("sex", "T"),
            ("unit", "PER"),
            ("age", "TOTAL"),
        ]
        for g in geos:
            asylum_p.append(("geo", g))
        asylum_p.append(("time", "2024"))
        pop_p = [("freq", "A"), ("age", "TOTAL"), ("sex", "T")]
        for g in geos:
            pop_p.append(("geo", g))
        pop_p.append(("time", "2024"))
        try:
            counts = parse_geo_time(fetch_dataset("migr_asyappctza", asylum_p))
            pops = parse_geo_time(fetch_dataset("demo_pjan", pop_p))
            rates = per_1000_hab(counts, pops)
            with asy_path.open(encoding="utf-8", newline="") as f:
                rows_asy = list(csv.DictReader(f))
            last_asy = next((r for r in rows_asy if int(r["year"]) == 2024), None)
            if not last_asy:
                errors.append("Asile : pas de ligne 2024 dans le CSV")
            else:
                for g in geos:
                    api_v = next((v for y, v in rates.get(g, []) if y == 2024), None)
                    csv_v = _f(last_asy.get(g, ""))
                    if api_v is None or csv_v is None:
                        errors.append(f"Asile {g} 2024 : valeur manquante")
                    elif not _near(csv_v, api_v, eps=0.08):
                        errors.append(f"Asile {g} 2024 : CSV={csv_v} API={api_v}")
        except OSError as exc:
            errors.append(f"Asile : requête Eurostat impossible ({exc})")

    ent_path = OUT / "entrees_etrangers_pour_1000.csv"
    if ent_path.exists():
        print("Contrôle entrées étrangers 2024 (migr_imm1ctz + demo_pjan vs", ent_path.name, ")…")
        ge = ["FR", "DK", "IT"]
        imm_q = [
            ("citizen", "FOR_STLS"),
            ("sex", "T"),
            ("age", "TOTAL"),
            ("agedef", "COMPLET"),
            ("unit", "NR"),
        ]
        for g in ge:
            imm_q.append(("geo", g))
        imm_q.append(("time", "2024"))
        pop_q = [("sex", "T"), ("age", "TOTAL"), ("unit", "NR")]
        for g in ge:
            pop_q.append(("geo", g))
        pop_q.append(("time", "2024"))
        try:
            imm = parse_geo_time(fetch_dataset("migr_imm1ctz", imm_q))
            pop = parse_geo_time(fetch_dataset("demo_pjan", pop_q))
            rates = per_1000_hab(imm, pop)
            with ent_path.open(encoding="utf-8", newline="") as f:
                rows_e = list(csv.DictReader(f))
            last_e = next((r for r in rows_e if int(r["year"]) == 2024), None)
            if not last_e:
                errors.append("Entrées : pas de ligne 2024 dans le CSV")
            else:
                for g in ge:
                    api_v = next((v for y, v in rates.get(g, []) if y == 2024), None)
                    csv_v = _f(last_e.get(g, ""))
                    if api_v is None:
                        errors.append(f"Entrées {g} 2024 : pas de valeur API")
                    elif csv_v is None:
                        errors.append(f"Entrées {g} 2024 : pas de valeur CSV")
                    elif not _near(csv_v, api_v, eps=0.1):
                        errors.append(f"Entrées {g} 2024 : CSV={csv_v} API={api_v}")
        except OSError as exc:
            errors.append(f"Entrées : requête Eurostat impossible ({exc})")

    if errors:
        print("\nÉCHEC —", len(errors), "écart(s) :")
        for e in errors:
            print(" ·", e)
        return 1
    print(
        "\nOK — CNMIGRATRT, UK, EU27 2024, asile et entrées étrangers (FR/DK/IT) alignés sur les sources en direct.",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
