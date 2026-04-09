"""
Entrées de ressortissants étrangers + apatrides (Eurostat migr_imm1ctz, citizen=FOR_STLS),
rapportées à la population au 1er janvier (demo_pjan). FR, DK, IT (UK : Eurostat seulement jusqu’à 2019).

Exécution : python fetch_entrees_etrangers.py (depuis charts/)
"""

from __future__ import annotations

import csv
import json
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "output" / "entrees_etrangers_pour_1000.csv"

GEOS = ["FR", "DK", "IT", "UK"]
YEAR_LO, YEAR_HI = 2016, 2024
EUROSTAT = "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data"


def fetch_table(dataset: str, params: list[tuple[str, str]]) -> dict:
    q = [("format", "JSON"), ("lang", "en")] + params
    url = f"{EUROSTAT}/{dataset}?{urlencode(q)}"
    with urlopen(url, timeout=120) as resp:
        return json.loads(resp.read())


def parse_geo_time(payload: dict) -> dict[str, list[tuple[int, float | None]]]:
    from eurostat_api import parse_geo_time as pgt

    return pgt(payload)


def main() -> None:
    imm_q = [
        ("citizen", "FOR_STLS"),
        ("sex", "T"),
        ("age", "TOTAL"),
        ("agedef", "COMPLET"),
        ("unit", "NR"),
    ]
    for g in GEOS:
        imm_q.append(("geo", g))
    for y in range(YEAR_LO, YEAR_HI + 1):
        imm_q.append(("time", str(y)))
    pop_q = [("sex", "T"), ("age", "TOTAL"), ("unit", "NR")]
    for g in GEOS:
        pop_q.append(("geo", g))
    for y in range(YEAR_LO, YEAR_HI + 1):
        pop_q.append(("time", str(y)))

    imm = parse_geo_time(fetch_table("migr_imm1ctz", imm_q))
    pop = parse_geo_time(fetch_table("demo_pjan", pop_q))

    rows: list[dict[str, float | int | None]] = []
    for year in range(YEAR_LO, YEAR_HI + 1):
        row: dict[str, float | int | None] = {"year": year}
        for g in GEOS:
            im = {y: v for y, v in imm.get(g, [])}
            pp = {y: v for y, v in pop.get(g, [])}
            a, b = im.get(year), pp.get(year)
            if a is not None and b is not None and b != 0:
                row[g] = round(float(a) / float(b) * 1000.0, 4)
            else:
                row[g] = None
        rows.append(row)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["year", "FR", "DK", "IT", "UK"])
        w.writeheader()
        w.writerows(rows)
    print(f"Écrit {OUT}")


if __name__ == "__main__":
    main()
