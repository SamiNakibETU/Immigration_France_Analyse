"""
Télécharge le solde migratoire des étrangers au Danemark depuis Statistics Denmark.
Tables :
  - INDVAN : immigrations d'étrangers (STATSB=UDLAND)
  - UDVAN  : émigrations d'étrangers (STATSB=UDLAND)
  - BEFOLK1 : population au 1er janvier
Sort : charts/output/dk_etrangers_solde.csv
"""
import urllib.request
import urllib.parse
import csv
import io
import sys
from pathlib import Path

OUT = Path(__file__).parent.parent / "charts" / "output"
OUT.mkdir(parents=True, exist_ok=True)

BASE = "https://api.statbank.dk/v1"
YEARS = list(map(str, range(2007, 2026)))


def dst_get_csv(table, params):
    qs = urllib.parse.urlencode(params, doseq=True)
    url = f"{BASE}/data/{table}/CSV?{qs}&lang=en&delimiter=Semicolon"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8-sig")


def parse_yearly(content):
    """Parse CSV DST → {year: value}, en sommant si plusieurs lignes par année."""
    reader = csv.DictReader(io.StringIO(content), delimiter=";")
    by_year = {}
    for row in reader:
        yr_key = "TID" if "TID" in row else "Tid"
        try:
            yr = int(row[yr_key].strip())
        except ValueError:
            continue
        val_col = [k for k in row.keys() if k not in (yr_key,) and "STATSB" not in k
                   and "KN" not in k and "K\xd8N" not in k][-1]
        raw = row[val_col].strip().replace("\xa0", "").replace(" ", "")
        v = int(raw) if raw not in ("", ".", "..") else 0
        by_year[yr] = by_year.get(yr, 0) + v
    return by_year


def main():
    print("=== Danemark — Statistics Denmark ===\n")

    # ── Immigration étrangers ─────────────────────────────────────────────────
    print("  Téléchargement INDVAN (immigration)...")
    imm_content = dst_get_csv("INDVAN", {"STATSB": "UDLAND", "Tid": YEARS})
    imm = parse_yearly(imm_content)

    # ── Emigration étrangers ──────────────────────────────────────────────────
    print("  Téléchargement UDVAN (emigration)...")
    emi_content = dst_get_csv("UDVAN", {"STATSB": "UDLAND", "Tid": YEARS})
    emi = parse_yearly(emi_content)

    # ── Population 1er janvier ────────────────────────────────────────────────
    print("  Téléchargement BEFOLK1 (population)...")
    pop_content = dst_get_csv("BEFOLK1", {"Tid": YEARS})
    pop = parse_yearly(pop_content)

    # ── Calcul du solde par mille ─────────────────────────────────────────────
    rows = []
    for yr in sorted(set(imm) & set(emi)):
        if yr < 2007:
            continue
        i = imm[yr]
        e = emi[yr]
        solde = i - e
        p = pop.get(yr)
        taux = round(solde / p * 1000, 3) if p else None
        rows.append({
            "year": yr,
            "immigration_etrangers": i,
            "emigration_etrangers": e,
            "solde_etrangers": solde,
            "population": p or "",
            "taux_permil": taux if taux is not None else "",
        })
        if yr >= 2013:
            print(f"  {yr}: imm={i:>7}, emi={e:>7}, solde={solde:>7}, pop={p}, taux={taux}permil")

    out_path = OUT / "dk_etrangers_solde.csv"
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["year","immigration_etrangers","emigration_etrangers",
                                           "solde_etrangers","population","taux_permil"])
        w.writeheader()
        w.writerows(rows)
    print(f"\nOK -> {out_path} ({len(rows)} lignes)")
    return rows


if __name__ == "__main__":
    rows = main()
    if not rows:
        print("ERREUR: aucune donnee")
        sys.exit(1)
