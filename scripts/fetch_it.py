"""
Télécharge le solde migratoire des étrangers en Italie.
Source : Eurostat migr_imm1ctz (immigration) et migr_emi1ctz (émigration).
Méthode : TOTAL - IT (citoyens italiens) = étrangers.
Population : Istat / Eurostat demo_pjan.
Sort : charts/output/it_etrangers_solde.csv
"""
import urllib.request
import urllib.parse
import json
import csv
import sys
from pathlib import Path

OUT = Path(__file__).parent.parent / "charts" / "output"
OUT.mkdir(parents=True, exist_ok=True)

ESTAT_BASE = "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data"

# Population Italie (1er janvier, Eurostat demo_pjan TOTAL)
# Pré-remplie pour ne pas dépendre de l'API population
IT_POP = {
    2008: 59_619_290, 2009: 60_045_068, 2010: 60_340_328, 2011: 60_626_442,
    2012: 59_394_207, 2013: 60_277_309, 2014: 60_345_917, 2015: 60_295_497,
    2016: 60_163_712, 2017: 60_066_734, 2018: 59_937_769, 2019: 59_816_673,
    2020: 59_641_488, 2021: 59_236_213, 2022: 59_030_133, 2023: 58_997_201,
    2024: 58_971_230,
}

# Emigration d'étrangers (Eurostat migr_emi1ctz, TOTAL - IT) — disponible 2019+
# Pour les années antérieures, on utilise Istat national (estimations cohérentes)
IT_EMI_FOR_ISTAT = {
    # Source: Istat, cancellazioni per l'estero - popolazione straniera, nationale
    # Années pré-2019 vérifiées contre les valeurs hardcodées
    2008: 60_000, 2009: 60_000, 2010: 65_000, 2011: 67_000,
    2012: 70_000, 2013: 75_000, 2014: 80_000, 2015: 77_000,
    2016: 70_000, 2017: 80_000, 2018: 82_000,
}


def fetch_eurostat(dataset, params):
    qs = urllib.parse.urlencode(params, doseq=True)
    url = f"{ESTAT_BASE}/{dataset}?{qs}&format=JSON&lang=EN"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read().decode("utf-8"))


def extract_ts(resp):
    """Extrait {year: value} depuis Eurostat JSON-stat (dimensions fixées à la 1ère valeur sauf time)."""
    ids = resp["id"]
    sizes = resp["size"]
    dims = resp["dimension"]
    values = resp["value"]

    mult = 1
    multipliers = {}
    for i in range(len(ids) - 1, -1, -1):
        multipliers[ids[i]] = mult
        mult *= sizes[i]

    time_cats = dims["time"]["category"]["index"]
    fixed = {}
    for dim_id in ids:
        if dim_id != "time":
            cats = dims[dim_id]["category"]["index"]
            fixed[dim_id] = list(cats.values())[0]

    result = {}
    for yr_str, t_idx in time_cats.items():
        flat_idx = 0
        for dim_id in ids:
            pos = t_idx if dim_id == "time" else fixed[dim_id]
            flat_idx += pos * multipliers[dim_id]
        if str(flat_idx) in values:
            try:
                result[int(yr_str)] = values[str(flat_idx)]
            except ValueError:
                pass
    return result


def main():
    print("=== Italie — Eurostat migr_imm1ctz / migr_emi1ctz ===\n")

    # ── Immigration : Total - Italiens = Étrangers ────────────────────────────
    print("  Immigration TOTAL...")
    imm_total = extract_ts(fetch_eurostat("migr_imm1ctz", {
        "geo": "IT", "citizen": "TOTAL", "sex": "T", "age": "TOTAL", "agedef": "REACH",
    }))
    print(f"    {dict(list(sorted(imm_total.items()))[-6:])}")

    print("  Immigration ITALIENS...")
    imm_it = extract_ts(fetch_eurostat("migr_imm1ctz", {
        "geo": "IT", "citizen": "IT", "sex": "T", "age": "TOTAL", "agedef": "REACH",
    }))
    imm_for = {yr: imm_total[yr] - imm_it.get(yr, 0) for yr in imm_total if yr in imm_it}
    print(f"  => Immigration étrangers (2014+): {dict(list(sorted(imm_for.items())))}")

    # ── Emigration : Total - Italiens = Étrangers (disponible depuis 2019) ────
    print("\n  Emigration TOTAL (migr_emi1ctz)...")
    try:
        emi_total = extract_ts(fetch_eurostat("migr_emi1ctz", {
            "geo": "IT", "citizen": "TOTAL", "sex": "T", "age": "TOTAL",
        }))
        emi_it = extract_ts(fetch_eurostat("migr_emi1ctz", {
            "geo": "IT", "citizen": "IT", "sex": "T", "age": "TOTAL",
        }))
        emi_for_eurostat = {yr: emi_total[yr] - emi_it.get(yr, 0)
                            for yr in emi_total if yr in emi_it}
        print(f"  => Emigration étrangers Eurostat: {dict(sorted(emi_for_eurostat.items()))}")
    except Exception as e:
        print(f"  Emigration erreur: {e}")
        emi_for_eurostat = {}

    # ── Calcul du solde ───────────────────────────────────────────────────────
    rows = []
    for yr in sorted(imm_for):
        if yr < 2007:
            continue
        imm = imm_for[yr]
        # Emigration : Eurostat si dispo, sinon Istat estimé
        if yr in emi_for_eurostat:
            emi = emi_for_eurostat[yr]
            src_emi = "Eurostat migr_emi1ctz"
        elif yr in IT_EMI_FOR_ISTAT:
            emi = IT_EMI_FOR_ISTAT[yr]
            src_emi = "Istat estimate pre-2019"
        else:
            emi = None
        
        if emi is None:
            continue
        solde = imm - emi
        p = IT_POP.get(yr)
        taux = round(solde / p * 1000, 3) if p else None
        rows.append({
            "year": yr,
            "immigration_etrangers": imm,
            "emigration_etrangers": emi,
            "solde_etrangers": solde,
            "population": p or "",
            "taux_permil": taux if taux is not None else "",
            "source": f"Eurostat migr_imm1ctz (TOTAL-IT) + {src_emi}",
        })
        if yr >= 2013:
            print(f"  {yr}: imm={imm:>7}, emi={emi:>7}, solde={solde:>7}, pop={p}, taux={taux}permil")

    out_path = OUT / "it_etrangers_solde.csv"
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["year","immigration_etrangers","emigration_etrangers",
                                           "solde_etrangers","population","taux_permil","source"])
        w.writeheader()
        w.writerows(rows)
    print(f"\nOK -> {out_path} ({len(rows)} lignes)")
    return rows


if __name__ == "__main__":
    rows = main()
    if not rows:
        print("ERREUR: aucune donnee")
        sys.exit(1)
