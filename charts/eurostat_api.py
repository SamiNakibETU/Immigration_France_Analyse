"""
Client minimal Eurostat JSON 1.0 : requête, cache, parsing geo × time.
"""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any
from urllib.error import URLError
from urllib.parse import urlencode
from urllib.request import urlopen

EUROSTAT_ROOT = "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data"


def _flat_index(idxs: list[int], size: list[int]) -> int:
    flat = 0
    for i in range(len(size)):
        factor = 1
        for j in range(i + 1, len(size)):
            factor *= size[j]
        flat += idxs[i] * factor
    return flat


def fetch_dataset(
    dataset: str,
    params: list[tuple[str, str]],
    retries: int = 3,
) -> dict[str, Any]:
    """params : liste (clé, valeur) répétable (ex. plusieurs geo)."""
    q = [("format", "JSON"), ("lang", "fr")] + params
    url = f"{EUROSTAT_ROOT}/{dataset}?{urlencode(q)}"
    last_err: Exception | None = None
    for attempt in range(retries):
        try:
            with urlopen(url, timeout=120) as resp:
                return json.loads(resp.read())
        except (URLError, OSError, ConnectionResetError) as e:
            last_err = e
            time.sleep(2.0 * (attempt + 1))
    raise last_err  # type: ignore[misc]


def load_or_fetch_dataset(
    dataset: str,
    params: list[tuple[str, str]],
    cache_path: Path | None,
) -> dict[str, Any]:
    if cache_path and cache_path.exists():
        return json.loads(cache_path.read_text(encoding="utf-8"))
    data = fetch_dataset(dataset, params)
    if cache_path:
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        cache_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return data


def parse_geo_time(payload: dict[str, Any]) -> dict[str, list[tuple[int, float | None]]]:
    """Extrait des séries par code pays lorsque seuls geo et time varient (autres dims = 1)."""
    ids: list[str] = payload["id"]
    size: list[int] = payload["size"]
    dim = payload["dimension"]
    vals = payload.get("value") or {}

    if "geo" not in ids or "time" not in ids:
        raise ValueError("Payload sans dimensions geo/time")

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


def per_1000_hab(
    numerator: dict[str, list[tuple[int, float | None]]],
    population: dict[str, list[tuple[int, float | None]]],
) -> dict[str, list[tuple[int, float | None]]]:
    """Pour chaque pays : numérateur / population × 1 000 (années communes uniquement)."""
    countries = sorted(set(numerator.keys()) & set(population.keys()))
    out: dict[str, list[tuple[int, float | None]]] = {}
    for c in countries:
        num = {y: v for y, v in numerator[c]}
        den = {y: v for y, v in population[c]}
        years = sorted(set(num.keys()) & set(den.keys()))
        merged: list[tuple[int, float | None]] = []
        for y in years:
            va, vb = num[y], den[y]
            if va is not None and vb is not None and vb != 0:
                merged.append((y, float(va) / float(vb) * 1000.0))
            else:
                merged.append((y, None))
        out[c] = merged
    return out
