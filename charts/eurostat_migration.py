"""
Données : Eurostat, jeu demo_gind, indicateur CNMIGRATRT
(Taux de solde migratoire plus ajustement statistique pour 1 000 habitants).

Documentation : https://ec.europa.eu/eurostat/cache/metadata/en/demo_gind_esms.htm

Remarques méthodologiques :
- Les révisions Eurostat peuvent différer d’agrégats nationaux (INSEE, ONS, etc.).
- Le Royaume-Uni : pour les figures publication, le taux UK affiché ne reprend pas cette série Eurostat
  mais une construction ONS documentée dans `uk_ons_series.py`.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any
from urllib.parse import urlencode
import time
from urllib.error import URLError
from urllib.request import urlopen

BASE = "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/demo_gind"


def _flat_index(idxs: list[int], size: list[int]) -> int:
    flat = 0
    for i in range(len(size)):
        factor = 1
        for j in range(i + 1, len(size)):
            factor *= size[j]
        flat += idxs[i] * factor
    return flat


def fetch_cnmigratrt(
    geos: list[str],
    years: range | list[int],
    lang: str = "fr",
) -> dict[str, Any]:
    """Récupère CNMIGRATRT pour une liste de codes pays Eurostat et une plage d’années."""
    if isinstance(years, range):
        year_list = list(years)
    else:
        year_list = list(years)

    q: list[tuple[str, str]] = [
        ("format", "JSON"),
        ("lang", lang),
        ("indic_de", "CNMIGRATRT"),
    ]
    for g in geos:
        q.append(("geo", g))
    for y in year_list:
        q.append(("time", str(y)))

    url = f"{BASE}?{urlencode(q)}"
    last_err: Exception | None = None
    for attempt in range(3):
        try:
            with urlopen(url, timeout=120) as resp:
                return json.loads(resp.read())
        except (URLError, OSError, ConnectionResetError) as e:
            last_err = e
            time.sleep(2.0 * (attempt + 1))
    raise last_err  # type: ignore[misc]


def parse_to_series(payload: dict[str, Any]) -> dict[str, list[tuple[int, float | None]]]:
    """Transforme la réponse JSON Eurostat en dictionnaire pays -> [(année, valeur), ...]."""
    ids: list[str] = payload["id"]
    size: list[int] = payload["size"]
    dim = payload["dimension"]
    vals = payload.get("value") or {}

    geo_idx = dim["geo"]["category"]["index"]
    time_idx = dim["time"]["category"]["index"]
    year_by_pos = {pos: int(year) for year, pos in time_idx.items()}

    pos_geo = ids.index("geo")
    pos_time = ids.index("time")
    n_time = size[pos_time]

    out: dict[str, list[tuple[int, float | None]]] = {}
    for gcode, gi in geo_idx.items():
        series: list[tuple[int, float | None]] = []
        for ti in range(n_time):
            idxs = [0] * len(size)
            idxs[pos_geo] = gi
            idxs[pos_time] = ti
            key = str(_flat_index(idxs, size))
            raw = vals.get(key)
            if raw is None or raw == ":":
                v: float | None = None
            else:
                try:
                    v = float(raw)
                except (TypeError, ValueError):
                    v = None
            series.append((year_by_pos[ti], v))
        out[gcode] = sorted(series, key=lambda x: x[0])
    return out


def series_to_csv(path: Path, series: dict[str, list[tuple[int, float | None]]]) -> None:
    """Écrit un CSV large : colonnes year, FR, DK, ..."""
    years_set: set[int] = set()
    for pts in series.values():
        for y, _ in pts:
            years_set.add(y)
    years = sorted(years_set)
    countries = sorted(series.keys())
    lines = ["year," + ",".join(countries)]
    for y in years:
        row = [str(y)]
        for c in countries:
            val = None
            for yy, vv in series[c]:
                if yy == y:
                    val = vv
                    break
            row.append("" if val is None else f"{val:.4f}".rstrip("0").rstrip("."))
        lines.append(",".join(row))
    path.write_text("\n".join(lines), encoding="utf-8")


def write_eu27_cnmigratrt_2024_csv(out_csv: Path, year: int = 2024) -> bool:
    """
    Télécharge CNMIGRATRT pour tous les codes UE-27 (année unique) et écrit un CSV
    compatible avec load_cnmigratrt_csv (colonnes geo, TIME_PERIOD, OBS_VALUE).
    """
    from migration_csv import EU27_GEO_CODES

    geos = sorted(EU27_GEO_CODES)
    try:
        payload = fetch_cnmigratrt(geos, [year])
    except (OSError, TimeoutError, ValueError, KeyError):
        return False
    series = parse_to_series(payload)
    rows = ["geo,TIME_PERIOD,OBS_VALUE"]
    for geo in geos:
        for y, v in series.get(geo, []):
            if y == year and v is not None:
                rows.append(f"{geo},{year},{v}")
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    out_csv.write_text("\n".join(rows), encoding="utf-8")
    return len(rows) > 1


def load_or_fetch(
    geos: list[str],
    year_from: int,
    year_to: int,
    cache_json: Path | None = None,
) -> dict[str, list[tuple[int, float | None]]]:
    years = range(year_from, year_to + 1)
    if cache_json and cache_json.exists():
        payload = json.loads(cache_json.read_text(encoding="utf-8"))
    else:
        payload = fetch_cnmigratrt(geos, years)
        if cache_json:
            cache_json.parent.mkdir(parents=True, exist_ok=True)
            cache_json.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return parse_to_series(payload)
