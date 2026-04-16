"""
Téléchargement des données nationales officielles pour les graphiques N1/N2/N3.

Sources :
- Danemark : Statistics Denmark API (VANDR - immigration/emigration étrangers par citoyenneté)
- Italie    : Istat demo.istat.it (bilancio demografico stranieri)
- Royaume-Uni : ONS LTIM (immigration, émigration, solde net par nationalité UE/non-UE)

Sortie : charts/output/
  - dk_etrangers_solde.csv
  - it_etrangers_solde.csv
  - uk_etrangers_solde.csv
  - uk_by_origin.csv
"""

import urllib.request
import json
import csv
import io
import zipfile
import os
from pathlib import Path

OUT = Path(__file__).parent.parent / "charts" / "output"
OUT.mkdir(parents=True, exist_ok=True)


# ─────────────────────────────────────────────────────────────────────────────
# DANEMARK — Statistics Denmark API
# Table VANDR : immigration et émigration par citoyenneté (danois / étrangers)
# ─────────────────────────────────────────────────────────────────────────────

def fetch_dk():
    print("=== Danemark (Statistics Denmark API) ===")

    # Population DK pour normaliser (en milliers)
    # Source: Statistics Denmark FOLK1A (population au 1er janvier)
    # On utilise l'API pour récupérer la population
    pop_req = {
        "table": "FOLK1A",
        "format": "JSON",
        "lang": "en",
        "variables": [
            {"code": "område", "values": ["000"]},   # tout le Danemark
            {"code": "køn",    "values": ["TOT"]},
            {"code": "alder",  "values": ["IALT"]},
            {"code": "Tid",    "values": ["*"]},
        ]
    }
    resp = _dst_query(pop_req)
    pop_by_year = {}
    for obs in resp.get("data", []):
        key = obs["key"][-1]          # ex: "2013K1"
        if key.endswith("K1"):        # Q1 = 1er janvier
            yr = int(key[:4])
            pop_by_year[yr] = int(obs["values"][0]) / 1000  # en milliers

    # Immigration étrangers
    imm_req = {
        "table": "VANDR",
        "format": "JSON",
        "lang": "en",
        "variables": [
            {"code": "IE",         "values": ["I"]},      # immigration
            {"code": "STATSB",     "values": ["5"]},      # étrangers (5 = non-danois)
            {"code": "BEVAE",      "values": ["TOT"]},
            {"code": "Tid",        "values": ["*"]},
        ]
    }
    emi_req = {
        "table": "VANDR",
        "format": "JSON",
        "lang": "en",
        "variables": [
            {"code": "IE",         "values": ["E"]},      # emigration
            {"code": "STATSB",     "values": ["5"]},
            {"code": "BEVAE",      "values": ["TOT"]},
            {"code": "Tid",        "values": ["*"]},
        ]
    }

    imm_resp = _dst_query(imm_req)
    emi_resp = _dst_query(emi_req)

    def parse_vandr(resp):
        by_year = {}
        for obs in resp.get("data", []):
            yr = int(obs["key"][-1])
            by_year[yr] = int(obs["values"][0])
        return by_year

    imm = parse_vandr(imm_resp)
    emi = parse_vandr(emi_resp)

    years = sorted(set(imm) & set(emi))
    rows = []
    for yr in years:
        if yr < 2013:
            continue
        solde = imm[yr] - emi[yr]
        pop = pop_by_year.get(yr) or pop_by_year.get(yr + 1)
        taux = round(solde / pop * 1000, 2) if pop else None
        rows.append({"year": yr, "immigration": imm[yr], "emigration": emi[yr],
                     "solde": solde, "pop_k": round(pop, 0) if pop else None,
                     "taux_permil": taux})
        print(f"  {yr}: imm={imm[yr]}, emi={emi[yr]}, solde={solde}, pop={pop:.0f}k => {taux}‰")

    out_path = OUT / "dk_etrangers_solde.csv"
    _write_csv(out_path, ["year", "immigration", "emigration", "solde", "pop_k", "taux_permil"], rows)
    print(f"  → {out_path}\n")
    return rows


def _dst_query(payload):
    req = urllib.request.Request(
        "https://api.statbank.dk/v1/data",
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())


# ─────────────────────────────────────────────────────────────────────────────
# ITALIE — Istat (Eurostat CNMIGRATRT foreigners via demo.istat.it)
# On utilise Eurostat car Istat n'a pas d'API simple.
# L'indicateur "solde étrangers" d'Istat = iscrizioni - cancellazioni stranieri.
# Source : Eurostat migr_pop1ctz (population étrangère) n'est pas le bon.
# On télécharge directement le fichier Istat via demo.istat.it zip CSV.
# ─────────────────────────────────────────────────────────────────────────────

def fetch_it():
    print("=== Italie (Istat demo.istat.it) ===")

    # Population Italie (milliers, Istat)
    pop_it = {
        2014: 60_782, 2015: 60_665, 2016: 60_589, 2017: 60_483,
        2018: 60_359, 2019: 59_641, 2020: 59_258, 2021: 59_030,
        2022: 58_997, 2023: 58_926,
    }

    # Télécharger les données Istat par année via demo.istat.it
    # URL de download du CSV national agrégé
    rows = []
    for year in range(2014, 2024):
        url = f"https://demo.istat.it/app/api/P03?anno={year}&tipoArea=N&area=0"
        try:
            req = urllib.request.Request(url, headers={"Accept": "application/json",
                                                        "User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=20) as r:
                data = json.loads(r.read())
            # Chercher iscrizioni et cancellazioni
            iscrizioni = None
            cancellazioni = None
            for item in data:
                if isinstance(item, dict):
                    nome = str(item.get("nome", "")).lower()
                    if "iscriz" in nome and iscrizioni is None:
                        iscrizioni = item.get("valore")
                    if "cancel" in nome and cancellazioni is None:
                        cancellazioni = item.get("valore")
            if iscrizioni is not None and cancellazioni is not None:
                solde = int(iscrizioni) - int(cancellazioni)
                pop = pop_it.get(year)
                taux = round(solde / pop * 1000, 2) if pop else None
                rows.append({"year": year, "iscrizioni": iscrizioni,
                             "cancellazioni": cancellazioni, "solde": solde,
                             "pop_k": pop, "taux_permil": taux})
                print(f"  {year}: isc={iscrizioni}, can={cancellazioni}, solde={solde} => {taux}‰")
        except Exception as e:
            print(f"  {year}: erreur API Istat — {e}")

    if rows:
        out_path = OUT / "it_etrangers_solde.csv"
        _write_csv(out_path, ["year", "iscrizioni", "cancellazioni", "solde", "pop_k", "taux_permil"], rows)
        print(f"  → {out_path}\n")
    return rows


# ─────────────────────────────────────────────────────────────────────────────
# ROYAUME-UNI — ONS LTIM
# ─────────────────────────────────────────────────────────────────────────────

def fetch_uk():
    print("=== Royaume-Uni (ONS LTIM) ===")

    url = (
        "https://www.ons.gov.uk/generator?format=csv&uri=/peoplepopulationandcommunity"
        "/populationandmigration/internationalmigration/datasets"
        "/longterminternationalimmigrationemigrationandnetmigrationflowsprovisional"
        "/yearendingdecember2024"
    )

    # Télécharger le xlsx ONS
    xlsx_url = (
        "https://www.ons.gov.uk/file?uri=/peoplepopulationandcommunity"
        "/populationandmigration/internationalmigration/datasets"
        "/longterminternationalimmigrationemigrationandnetmigrationflowsprovisional"
        "/yearendingdecember2024/ltim2024decprovisional.xlsx"
    )

    local_xlsx = OUT / "uk_ons_ltim_dec2024.xlsx"
    print(f"  Téléchargement {xlsx_url}")
    try:
        req = urllib.request.Request(xlsx_url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=60) as r:
            content = r.read()
        local_xlsx.write_bytes(content)
        print(f"  Téléchargé : {len(content)} bytes")
        return str(local_xlsx)
    except Exception as e:
        print(f"  Erreur : {e}")
        return None


def _write_csv(path, fieldnames, rows):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)


if __name__ == "__main__":
    fetch_dk()
    fetch_it()
    fetch_uk()
    print("Terminé.")
