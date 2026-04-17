"""
Audit complet de toutes les donnees du site.
Compare data.json avec les CSV sources et les valeurs officielles connues.
"""
import json
import csv
from pathlib import Path

ROOT = Path(__file__).parent.parent
DATA = ROOT / "site" / "data.json"
OUT  = ROOT / "charts" / "output"

d = json.load(open(DATA, encoding="utf-8"))
ns = d["nationalStats"]

print("=" * 70)
print("AUDIT DES DONNEES — site/data.json")
print("=" * 70)

# ─── 1. frImmigres (INSEE IP2050) ─────────────────────────────────────────────
print("\n1. frImmigres (INSEE Premiere n2050, mai 2025)")
print("   Source CSV: charts/output/fr_immigres_solde_insee_IP2050.csv")
print(f"   {'Annee':>6}  {'Valeur':>8}  {'Estime':>8}")
for r in ns["frImmigres"]:
    est = r.get("estimated", False)
    print(f"   {r['year']:>6}  {r['value']:>8.2f}  {'[EST]' if est else '':>8}")

# Verifier contre le CSV source
csv_fr = OUT / "fr_immigres_solde_insee_IP2050.csv"
if csv_fr.exists():
    print("   --- Verification contre CSV source ---")
    rows = list(csv.DictReader(open(csv_fr, encoding="utf-8")))
    json_map = {r["year"]: r["value"] for r in ns["frImmigres"]}
    ok = True
    for row in rows:
        yr = int(row["year"])
        if yr < 2013: continue
        tp = row.get("taux_permil", "")
        if not tp: continue
        csv_val = round(float(tp), 2)
        json_val = json_map.get(yr)
        match = abs(csv_val - json_val) < 0.01 if json_val else False
        if not match:
            print(f"   ECART {yr}: CSV={csv_val} vs JSON={json_val}")
            ok = False
    if ok:
        print("   OK: toutes les valeurs correspondent au CSV.")

# ─── 2. dkEtrangers (Statistics Denmark) ─────────────────────────────────────
print("\n2. dkEtrangers (Statistics Denmark INDVAN/UDVAN + BEFOLK1)")
print("   Source CSV: charts/output/dk_etrangers_solde.csv")
print(f"   {'Annee':>6}  {'JSON':>8}  {'CSV':>8}  {'OK':>5}")
csv_dk = OUT / "dk_etrangers_solde.csv"
if csv_dk.exists():
    json_map = {r["year"]: r["value"] for r in ns["dkEtrangers"]}
    rows_dk = list(csv.DictReader(open(csv_dk, encoding="utf-8")))
    for row in rows_dk:
        yr = int(row["year"])
        if yr < 2013: continue
        csv_val = round(float(row["taux_permil"]), 2) if row["taux_permil"] else None
        json_val = json_map.get(yr)
        match = abs(csv_val - json_val) < 0.01 if (csv_val and json_val) else (csv_val is None and json_val is None)
        flag = "OK" if match else "ECART"
        print(f"   {yr:>6}  {json_val or 'NA':>8}  {csv_val or 'NA':>8}  {flag:>5}")

# ─── 3. itEtrangers (Eurostat migr_imm1ctz/emi1ctz) ─────────────────────────
print("\n3. itEtrangers (Eurostat migr_imm1ctz - emi1ctz, TOTAL - IT citizens)")
print("   Source CSV: charts/output/it_etrangers_solde.csv")
print(f"   {'Annee':>6}  {'JSON':>8}  {'CSV':>8}  {'OK':>5}")
csv_it = OUT / "it_etrangers_solde.csv"
if csv_it.exists():
    json_map = {r["year"]: r["value"] for r in ns["itEtrangers"]}
    rows_it = list(csv.DictReader(open(csv_it, encoding="utf-8")))
    for row in rows_it:
        yr = int(row["year"])
        if yr < 2013: continue
        csv_val = round(float(row["taux_permil"]), 2) if row["taux_permil"] else None
        json_val = json_map.get(yr)
        match = abs(csv_val - json_val) < 0.02 if (csv_val and json_val) else (csv_val is None and json_val is None)
        flag = "OK" if match else "ECART"
        print(f"   {yr:>6}  {json_val or 'NA':>8}  {csv_val or 'NA':>8}  {flag:>5}")

# ─── 4. ukEtrangers + ukByOrigin (ONS LTIM) ──────────────────────────────────
print("\n4. ukEtrangers (ONS LTIM YE December 2024)")
print("   Source CSV: charts/output/uk_etrangers_solde.csv")
print(f"   {'Annee':>6}  {'JSON':>8}  {'CSV':>8}  {'OK':>5}")
csv_uk = OUT / "uk_etrangers_solde.csv"
if csv_uk.exists():
    json_map = {r["year"]: r["value"] for r in ns["ukEtrangers"]}
    rows_uk = list(csv.DictReader(open(csv_uk, encoding="utf-8")))
    for row in rows_uk:
        yr = int(row["year"])
        if yr < 2013: continue
        csv_val = round(float(row["taux_permil"]), 2) if row["taux_permil"] else None
        json_val = json_map.get(yr)
        match = abs(csv_val - json_val) < 0.02 if (csv_val and json_val) else (csv_val is None and json_val is None)
        flag = "OK" if match else ("ABSENT" if not json_val else "ECART")
        print(f"   {yr:>6}  {json_val or 'NA':>8}  {csv_val or 'NA':>8}  {flag:>5}")

print("\n4b. ukByOrigin (ONS LTIM)")
print("   Source CSV: charts/output/uk_by_origin.csv")
print(f"   {'Annee':>6}  {'EU_json':>9}  {'EU_csv':>9}  {'NEU_json':>10}  {'NEU_csv':>10}  OK")
csv_ukor = OUT / "uk_by_origin.csv"
if csv_ukor.exists():
    json_map = {r["year"]: r for r in ns["ukByOrigin"]}
    for row in csv.DictReader(open(csv_ukor, encoding="utf-8")):
        yr = int(row["year"])
        if yr < 2012: continue
        j = json_map.get(yr)
        eu_csv = int(row["eu"])
        neu_csv = int(row["nonEu"])
        eu_ok = j and j["eu"] == eu_csv
        neu_ok = j and j["nonEu"] == neu_csv
        flag = "OK" if (eu_ok and neu_ok) else "ECART"
        eu_j = j["eu"] if j else "NA"
        neu_j = j["nonEu"] if j else "NA"
        print(f"   {yr:>6}  {eu_j:>9}  {eu_csv:>9}  {neu_j:>10}  {neu_csv:>10}  {flag}")

# ─── 5. itEurostatNet ────────────────────────────────────────────────────────
print("\n5. itEurostatNet (Eurostat CNMIGRATRT, IT total - nationaux inclus)")
print("   Valeurs hardcodees - a verifier manuellement contre Eurostat:")
for r in ns["itEurostatNet"]:
    print(f"   {r['year']}: {r['value']} permil")

# ─── 6. Eurostat principal (migrationSelection) ───────────────────────────────
print("\n6. Serie principale Eurostat CNMIGRATRT (migrationSelection)")
print("   Derniers points par pays (annee, valeur):")
rows_main = d.get("migrationSelection", [])
keys = ["FR", "DK", "IT", "UK"]
if rows_main:
    last_row = rows_main[-1]
    print(f"   Derniere annee: {last_row.get('year')}")
    for k in keys:
        v = last_row.get(k)
        if v is not None:
            print(f"     {k}: {v:.3f} permil")
    print("   Quelques annees cles (FR, DK, IT, UK):")
    for row in rows_main:
        yr = row.get("year")
        if yr in [2013, 2015, 2019, 2020, 2022, 2024]:
            vals = " | ".join(f"{k}:{row.get(k, 'NA'):.2f}" if isinstance(row.get(k), float) else f"{k}:NA" for k in keys)
            print(f"   {yr}: {vals}")

# ─── 7. permitsMotif ─────────────────────────────────────────────────────────
print("\n7. permitsMotif (Eurostat migr_resfirst, 2022, pour 1000 hab.)")
for r in ns.get("permitsMotif", []):
    aut = r.get("autres", r.get("protection", 0))
    tot = r["travail"] + r["famille"] + r["etudes"] + aut
    print(f"   {r['pays']:>12}: travail={r['travail']} famille={r['famille']} etudes={r['etudes']} autres={aut} TOTAL={tot:.2f}")

# ─── 8. asileRecognition ─────────────────────────────────────────────────────
print("\n8. asileRecognition (EUAA/Eurostat migr_asydcfsta, 2022)")
for r in ns.get("asileRecognition", []):
    print(f"   {r['pays']:>12} ({r['code']}): {r['taux']}%")

print("\n" + "=" * 70)
print("FIN AUDIT")
print("=" * 70)
