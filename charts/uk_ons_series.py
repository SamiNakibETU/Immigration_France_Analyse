"""
Série Royaume-Uni : **numérateur = migration nette de long terme, exclusivement ONS**
(pas de valeur Eurostat CNMIGRATRT pour le UK dans les graphiques).

Deux blocs officiels ONS pour le solde (tous ressortissants) :
- **2005–2011** : année civile, milliers de personnes — tableau historique
  « Long-Term International Migration into and out of the UK by citizenship, 1964 to 2015 »
  (réf. ONS 006408, décembre 2016), feuille « Data », colonne « Net Migration » (All Citizenships).
- **2012–2024** : année se terminant en décembre — « Long-term international immigration, emigration
  and net migration flows, provisional », édition year ending December 2024, Table 1,
  flux « Net migration » / « All Nationalities », fichier ltimmay25v5.0.xlsx (publié mai 2025).

Taux pour 1 000 habitants : 1000 × (solde en personnes) / (population).

Dénominateur (population résidente) :
- **2005–2020** : Eurostat, table demo_pjan, 1er janvier, UK (sexe T, âge TOTAL) — série harmonisée
  disponible sur toute la sous-période ; ce n’est pas un chiffre de migration ONS.
- **2021–2024** : ONS mid-year population estimates, tableaux MYE1/MYE3 (fichiers mid-2021, mid-2023, mid-2024).

Les comparaisons France–UK juxtaposent donc : France = Eurostat CNMIGRATRT (année civile) ;
UK = solde ONS / population selon la note ci-dessus (à expliciter en source sur la figure).
"""

from __future__ import annotations

import json
from pathlib import Path

# ONS 006408, migrationtimelinedatasheets v1.4 — Net Migration, All Citizenships, **milliers**
_CY_NET_THOUSANDS: dict[int, int] = {
    2005: 267,
    2006: 265,
    2007: 273,
    2008: 229,
    2009: 229,
    2010: 256,
    2011: 205,
}

# ltimmay25v5.0.xlsx, Table 1, Net migration, All Nationalities — **personnes** (arrondi milliers ONS)
_YE_DEC_NET_PERSONS: dict[int, int] = {
    2012: 195_000,
    2013: 244_000,
    2014: 284_000,
    2015: 303_000,
    2016: 249_000,
    2017: 208_000,
    2018: 276_000,
    2019: 184_000,
    2020: 93_000,
    2021: 484_000,
    2022: 873_000,
    2023: 860_000,
    2024: 431_000,
}

# Population : Eurostat demo_pjan 1er janvier (personnes), UK — extrait API Eurostat
_POP_EUROSTAT_1JAN: dict[int, int] = {
    2005: 60_182_050,
    2006: 60_620_361,
    2007: 61_073_279,
    2008: 61_571_647,
    2009: 62_042_343,
    2010: 62_510_197,
    2011: 63_022_532,
    2012: 63_495_088,
    2013: 63_905_342,
    2014: 64_351_203,
    2015: 64_853_393,
    2016: 65_379_044,
    2017: 65_844_142,
    2018: 66_273_576,
    2019: 66_647_112,
    2020: 67_025_542,
}

# ONS mid-year UK « All persons » (MYE1 sauf 2022 issu de MYE3 « Estimated Population mid-2022 »)
_POP_ONS_MIDYEAR: dict[int, int] = {
    2021: 67_026_292,
    2022: 67_602_761,
    2023: 68_265_209,
    2024: 69_281_437,
}


def _denominator_pop(year: int) -> int:
    if year <= 2020:
        return _POP_EUROSTAT_1JAN[year]
    return _POP_ONS_MIDYEAR[year]


def _ye_dec_from_cache() -> dict[int, int] | None:
    """Série YE December (personnes) extraite du XLSX ONS par `ons_fetch.refresh_ons_ltim`."""
    cache_root = Path(__file__).resolve().parent / "cache"
    p = cache_root / "ons" / "ons_ltim_net_ye_dec.json"
    if not p.exists():
        return None
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None
    block = data.get("ye_december_net_all_nationalities_persons") or {}
    out: dict[int, int] = {}
    for k, v in block.items():
        try:
            out[int(k)] = int(v)
        except (TypeError, ValueError):
            continue
    return out or None


def _net_persons(year: int) -> int:
    if year <= 2011:
        return _CY_NET_THOUSANDS[year] * 1000
    cached = _ye_dec_from_cache()
    if cached and year in cached:
        return cached[year]
    return _YE_DEC_NET_PERSONS[year]


def uk_rate_per_1000_series(year_from: int = 2005, year_to: int = 2024) -> list[tuple[int, float | None]]:
    out: list[tuple[int, float | None]] = []
    for y in range(year_from, year_to + 1):
        try:
            net = _net_persons(y)
            pop = _denominator_pop(y)
        except KeyError:
            out.append((y, None))
            continue
        out.append((y, round(1000.0 * float(net) / float(pop), 4)))
    return out


UK_SOURCE_FOOTNOTE = (
    "Royaume-Uni — solde migratoire net de long terme : Office for National Statistics (ONS) uniquement "
    "(2005–2011 : année civile, ref. 006408 déc. 2016 ; 2012+ : année se terminant en décembre, "
    "tableau LTIM provisional — valeurs YE Dec « All Nationalities » rechargées depuis le XLSX ONS "
    "à chaque `refresh_and_publish.py`, avec repli sur valeurs figées si hors-ligne). "
    "Taux pour 1 000 hbts : dénominateur = population 1er janv. Eurostat demo_pjan (2005–2020) "
    "et estimations mi-année ONS (2021–2024). "
    "France : Eurostat demo_gind CNMIGRATRT (année civile) — les deux pays ne suivent pas la même combinaison source/méthode."
)
