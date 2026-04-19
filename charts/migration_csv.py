"""
Lecture des exports SDMX-CSV Eurostat (demo_gind, CNMIGRATRT) déposés à la racine du dépôt Migrations/.
Fusion avec les séries API : les valeurs du CSV l’emportent sur le cache pour les années présentes.

`python charts/refresh_and_publish.py` définit TERRA_PURE_API=1 : aucune fusion, séries = API Eurostat
(+ UK = ONS comme dans plot_publication). Pour forcer la fusion CSV : lancer plot_publication sans cette variable.
"""

from __future__ import annotations

import csv
from pathlib import Path

def _parse_float(s: str) -> float | None:
    s = (s or "").strip()
    if not s:
        return None
    try:
        return float(s.replace(",", "."))
    except ValueError:
        return None


def load_cnmigratrt_csv(path: Path) -> dict[str, dict[int, float | None]]:
    """Retourne geo -> {année: valeur}."""
    out: dict[str, dict[int, float | None]] = {}
    with path.open(encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            geo = (row.get("geo") or "").strip()
            if not geo:
                continue
            try:
                year = int(str(row.get("TIME_PERIOD", "")).strip())
            except ValueError:
                continue
            val = _parse_float(str(row.get("OBS_VALUE", "")))
            out.setdefault(geo, {})[year] = val
    return out


def dict_to_sorted_series(d: dict[int, float | None]) -> list[tuple[int, float | None]]:
    return sorted(d.items(), key=lambda x: x[0])


def overlay_csv_on_series(
    base: list[tuple[int, float | None]],
    overlay: dict[int, float | None],
    year_from: int,
    year_to: int,
) -> list[tuple[int, float | None]]:
    """Remplace les années présentes dans overlay ; conserve le reste de base."""
    by_y = dict(base)
    for y, v in overlay.items():
        if year_from <= y <= year_to:
            by_y[y] = v
    years = sorted(by_y.keys())
    return [(y, by_y[y]) for y in years if year_from <= y <= year_to]


def apply_user_csv_overrides(
    series_by_geo: dict[str, list[tuple[int, float | None]]],
    year_from: int,
    year_to: int,
    paths: list[tuple[str, Path]],
) -> None:
    """Modifie series_by_geo en place. paths = (libellé log, chemin)."""
    for _label, p in paths:
        if not p.exists():
            continue
        parsed = load_cnmigratrt_csv(p)
        for geo, yd in parsed.items():
            if geo not in series_by_geo:
                empty = [(y, None) for y in range(year_from, year_to + 1)]
                series_by_geo[geo] = overlay_csv_on_series(empty, yd, year_from, year_to)
            else:
                series_by_geo[geo] = overlay_csv_on_series(series_by_geo[geo], yd, year_from, year_to)


def default_user_csv_paths(repo_root: Path) -> list[tuple[str, Path]]:
    return [
        ("principal FR/DK/IT", repo_root / "estat_demo_gind_filtered_en.csv"),
        ("FX partiel ou complet", repo_root / "estat_demo_gind_filtered_en (2).csv"),
        ("UK Eurostat historique", repo_root / "estat_demo_gind_filtered_en (3).csv"),
        ("UK Eurostat (doublon)", repo_root / "estat_demo_gind_filtered_en (4).csv"),
    ]


# UE-27 (codes Eurostat)
EU27_GEO_CODES: frozenset[str] = frozenset(
    {
        "AT",
        "BE",
        "BG",
        "HR",
        "CY",
        "CZ",
        "DK",
        "EE",
        "FI",
        "FR",
        "DE",
        "EL",
        "HU",
        "IE",
        "IT",
        "LV",
        "LT",
        "LU",
        "MT",
        "NL",
        "PL",
        "PT",
        "RO",
        "SK",
        "SI",
        "ES",
        "SE",
    }
)


def load_eu_panel_2024(path: Path) -> list[tuple[str, float]]:
    """Lit le CSV multi-pays ; retourne (code_geo, valeur) pour 2024, UE-27 uniquement, valeurs non nulles."""
    if not path.exists():
        return []
    parsed = load_cnmigratrt_csv(path)
    rows: list[tuple[str, float]] = []
    for geo, yd in parsed.items():
        if geo not in EU27_GEO_CODES:
            continue
        v = yd.get(2024)
        if v is not None:
            rows.append((geo, float(v)))
    rows.sort(key=lambda x: x[1])
    return rows
