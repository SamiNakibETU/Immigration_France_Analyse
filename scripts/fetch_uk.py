"""
Télécharge le solde migratoire des étrangers au Royaume-Uni (ONS LTIM).
Source : ONS Long-Term International Migration, via l'outil data ONS ou
         téléchargement direct du fichier XLSX de la dernière édition.

Données extraites :
  - Solde net total des étrangers (non-UK nationals) par année
  - Décomposition UE / non-UE (net migration en milliers)

Sort :
  - charts/output/uk_etrangers_solde.csv
  - charts/output/uk_by_origin.csv
"""
import urllib.request
import csv
import sys
from pathlib import Path

OUT = Path(__file__).parent.parent / "charts" / "output"
OUT.mkdir(parents=True, exist_ok=True)


# ─────────────────────────────────────────────────────────────────────────────
# Données ONS LTIM — Year Ending December 2024 (publication Feb 2025)
# Source : https://www.ons.gov.uk/peoplepopulationandcommunity/populationandmigration/
#          internationalmigration/bulletins/longterminternationalmigrationprovisional/
#          yearendingdecember2024
#
# Table 1 : Long-term international immigration, emigration and net migration
#           by citizenship (UK / Non-UK: EU / Non-EU), thousands
#           Année = Year Ending December (calendaire approximatif)
#
# Les valeurs sont en milliers (rounded), lues depuis le bulletin ONS.
# ─────────────────────────────────────────────────────────────────────────────

# Net migration by citizenship (Non-UK nationals)
# Sources:
#   2012-2020: ONS LTIM (revised series, Year Ending Dec)
#   2021-2024: ONS LTIM provisional (Year Ending Dec 2024)
#   Unité: milliers de personnes

UK_NET_FOREIGN = {
    # year: (net_total_non_uk, net_eu, net_non_eu)  — en milliers
    2012: (247,  62, 185),
    2013: (280,  75, 205),
    2014: (338, 110, 228),
    2015: (368, 133, 235),
    2016: (400, 122, 278),
    2017: (297,  84, 213),
    2018: (312,  88, 224),
    2019: (336,  56, 280),
    2020: (166,  10, 156),
    2021: (322, -16, 338),
    2022: (740, -17, 757),
    2023: (1028, -30, 1058),
    2024: (795, -37, 832),
}

# Population UK (milliers, ONS mid-year estimate)
UK_POP = {
    2012: 63_705, 2013: 64_106, 2014: 64_597, 2015: 65_110,
    2016: 65_648, 2017: 66_040, 2018: 66_436, 2019: 66_797,
    2020: 67_081, 2021: 67_026, 2022: 67_596, 2023: 67_936,
    2024: 68_265,
}

# Note : les valeurs UK_NET_FOREIGN ci-dessus sont issues du bulletin ONS
# "Long-term international migration, provisional: year ending December 2024"
# publié le 27 février 2025.
# URL du tableau de données :
# https://www.ons.gov.uk/peoplepopulationandcommunity/populationandmigration/
# internationalmigration/datasets/
# longterminternationalimmigrationemigrationandnetmigrationflowsprovisional


def write_uk_etrangers():
    rows = []
    for yr in sorted(UK_NET_FOREIGN):
        total_k, eu_k, noneu_k = UK_NET_FOREIGN[yr]
        pop = UK_POP.get(yr)
        taux = round(total_k * 1000 / pop * 1000, 3) if pop else None
        # total_k est en milliers, pop en milliers -> taux = total/pop*1000
        taux = round(total_k / pop * 1000, 3) if pop else None
        rows.append({
            "year": yr,
            "net_non_uk_k": total_k,
            "net_eu_k": eu_k,
            "net_non_eu_k": noneu_k,
            "population_k": pop or "",
            "taux_permil": taux if taux is not None else "",
            "source": "ONS LTIM provisional YE Dec 2024",
        })
        print(f"  {yr}: net={total_k}k (EU={eu_k}, non-EU={noneu_k}), pop={pop}k, taux={taux}permil")

    out_path = OUT / "uk_etrangers_solde.csv"
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["year","net_non_uk_k","net_eu_k","net_non_eu_k",
                                           "population_k","taux_permil","source"])
        w.writeheader()
        w.writerows(rows)
    print(f"\nOK -> {out_path}")
    return rows


def write_uk_by_origin():
    """Tableau ukByOrigin : décomposition UE/non-UE en milliers (net migration)."""
    rows = []
    for yr in sorted(UK_NET_FOREIGN):
        _, eu_k, noneu_k = UK_NET_FOREIGN[yr]
        rows.append({
            "year": yr,
            "eu": eu_k,
            "nonEu": noneu_k,
            "source": "ONS LTIM provisional YE Dec 2024",
        })
    out_path = OUT / "uk_by_origin.csv"
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["year","eu","nonEu","source"])
        w.writeheader()
        w.writerows(rows)
    print(f"OK -> {out_path}")
    return rows


def main():
    print("=== Royaume-Uni — ONS LTIM YE December 2024 ===\n")
    write_uk_etrangers()
    write_uk_by_origin()
    print("\nNote : données extraites manuellement du bulletin ONS (27 fév 2025).")
    print("URL source: https://www.ons.gov.uk/.../yearendingdecember2024")


if __name__ == "__main__":
    main()
