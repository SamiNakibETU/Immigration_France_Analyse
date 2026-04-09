"""
Analyses Terra Nova (rangs UE, ratio asile/solde, quadri grandes économies).
Lit / écrit dans charts/output/ — appelé depuis plot_publication.main().
"""

from __future__ import annotations

import csv
import statistics
from pathlib import Path

from eurostat_migration import load_or_fetch
from migration_csv import EU27_GEO_CODES

DISPLAY = {
    "FR": "France",
    "DE": "Allemagne",
    "IT": "Italie",
    "ES": "Espagne",
    "SE": "Suède",
    "NL": "Pays-Bas",
    "DK": "Danemark",
}

EU27 = sorted(EU27_GEO_CODES)


def _get_year(series: list[tuple[int, float | None]], year: int) -> float | None:
    for y, v in series:
        if y == year and v is not None:
            return float(v)
    return None


def run_rank_france(panel: dict[str, list[tuple[int, float | None]]], out_csv: Path) -> list[dict]:
    """Rang de la France (1 = plus fort solde net) parmi les pays UE-27 avec donnée."""
    rows_out: list[dict] = []
    years = range(2005, 2025)
    for year in years:
        vals: list[tuple[str, float]] = []
        for geo in EU27:
            if geo not in panel:
                continue
            v = _get_year(panel[geo], year)
            if v is not None:
                vals.append((geo, v))
        if not vals:
            continue
        vals.sort(key=lambda x: -x[1])
        if not any(g == "FR" for g, _ in vals):
            continue
        rank_fr = next((i + 1 for i, (g, _) in enumerate(vals) if g == "FR"), None)
        fr_v = next((v for g, v in vals if g == "FR"), None)
        med = statistics.median([v for _, v in vals])
        rows_out.append(
            {
                "annee": year,
                "rang_france": rank_fr or "",
                "nb_pays": len(vals),
                "valeur_fr": round(fr_v, 4) if fr_v is not None else "",
                "mediane_ue27": round(med, 4),
            }
        )
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    with out_csv.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(
            f,
            fieldnames=["annee", "rang_france", "nb_pays", "valeur_fr", "mediane_ue27"],
        )
        w.writeheader()
        w.writerows(rows_out)
    return rows_out


def read_wide(path: Path) -> list[dict]:
    if not path.exists():
        return []
    rows: list[dict] = []
    with path.open(encoding="utf-8", newline="") as f:
        r = csv.DictReader(f)
        for row in r:
            y = int(row["year"])
            d: dict = {"year": y}
            for k, v in row.items():
                if k == "year":
                    continue
                s = (v or "").strip()
                if not s:
                    d[k] = None
                else:
                    try:
                        d[k] = float(s.replace(",", "."))
                    except ValueError:
                        d[k] = None
            rows.append(d)
    return rows


def run_ratio_asile_solde(
    mig_rows: list[dict],
    asy_rows: list[dict],
    out_csv: Path,
) -> list[dict]:
    """Ratio premières demandes d’asile / solde net (même année), par pays — séries temporelles."""
    codes = ["FR", "DE", "IT", "ES", "SE", "NL", "DK"]
    by_year_mig = {r["year"]: r for r in mig_rows}
    by_year_asy = {r["year"]: r for r in asy_rows}
    years = sorted(set(by_year_mig) & set(by_year_asy))
    rows_out: list[dict] = []
    for year in years:
        if year < 2008:
            continue
        rm, ra = by_year_mig[year], by_year_asy[year]
        for code in codes:
            net = rm.get(code)
            asy = ra.get(code)
            if net is None or asy is None:
                continue
            if net > 0.05:
                ratio = asy / net
            else:
                ratio = None
            rows_out.append(
                {
                    "annee": year,
                    "code": code,
                    "libelle": DISPLAY.get(code, code),
                    "solde_net": round(net, 4),
                    "asile_premieres": round(asy, 4),
                    "ratio_asile_sur_solde": "" if ratio is None else round(ratio, 4),
                    "note": "solde net ≤ 0 → ratio omis" if ratio is None else "",
                }
            )
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    with out_csv.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(
            f,
            fieldnames=[
                "annee",
                "code",
                "libelle",
                "solde_net",
                "asile_premieres",
                "ratio_asile_sur_solde",
                "note",
            ],
        )
        w.writeheader()
        w.writerows(rows_out)
    return rows_out


def run_volatility_core(
    mig_rows: list[dict],
    out_csv: Path,
    year_lo: int = 2010,
    year_hi: int = 2024,
) -> list[dict]:
    """
    Écart-type du solde migratoire net (pour 1 000 hab.) sur une fenêtre d’années —
    comparaison FR / DK / IT / UK. Lecture data journalisme : variabilité conjoncturelle
    (pics, trous) vs courbe plus étroite.
    """
    codes = ["FR", "DK", "IT", "UK"]
    display = {"FR": "France", "DK": "Danemark", "IT": "Italie", "UK": "Royaume-Uni"}
    buckets: dict[str, list[float]] = {c: [] for c in codes}
    for r in mig_rows:
        y = r["year"]
        if y < year_lo or y > year_hi:
            continue
        for c in codes:
            v = r.get(c)
            if v is not None and isinstance(v, (int, float)):
                buckets[c].append(float(v))
    rows_out: list[dict] = []
    for c in codes:
        vals = sorted(buckets[c])
        if len(vals) < 2:
            continue
        sd = statistics.stdev(vals)
        mu = statistics.mean(vals)
        rows_out.append(
            {
                "code": c,
                "libelle": display.get(c, c),
                "year_lo": year_lo,
                "year_hi": year_hi,
                "n": len(vals),
                "stdev": round(sd, 4),
                "mean": round(mu, 4),
            }
        )
    rows_out.sort(key=lambda x: x["stdev"])
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    with out_csv.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(
            f,
            fieldnames=["code", "libelle", "year_lo", "year_hi", "n", "stdev", "mean"],
        )
        w.writeheader()
        w.writerows(rows_out)
    return rows_out


def run_quadri_wide(mig_rows: list[dict], out_csv: Path) -> list[dict]:
    """Solde net FR, DE, IT, ES — format large pour Figma / D3."""
    rows_out: list[dict] = []
    for r in mig_rows:
        row = {"annee": r["year"]}
        for c in ("FR", "DE", "IT", "ES"):
            v = r.get(c)
            row[c] = "" if v is None else round(v, 4)
        rows_out.append(row)
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    with out_csv.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["annee", "FR", "DE", "IT", "ES"])
        w.writeheader()
        w.writerows(rows_out)
    return rows_out


def main(out_dir: Path | None = None, cache_dir: Path | None = None) -> None:
    root = Path(__file__).resolve().parent
    out = out_dir or (root / "output")
    cache = cache_dir or (root / "cache")
    cache.mkdir(parents=True, exist_ok=True)
    out.mkdir(parents=True, exist_ok=True)

    mig_all = read_wide(out / "cnmigratrt_2005_2024_tous_pays.csv")
    if not mig_all:
        mig_all = read_wide(out / "cnmigratrt_2005_2024_selection.csv")
    mig_sel = read_wide(out / "cnmigratrt_2005_2024_selection.csv")
    if not mig_sel:
        mig_sel = mig_all
    asy = read_wide(out / "asile_premieres_demandes_pour_1000.csv")

    run_volatility_core(mig_sel, out / "analyse_volatility_solde_fr_dk_it_uk.csv")
    try:
        import fetch_entrees_etrangers

        fetch_entrees_etrangers.main()
    except OSError as e:
        print(f"Entrées étrangers : {e}")
    run_ratio_asile_solde(mig_all, asy, out / "analyse_ratio_asile_solde_net.csv")
    run_quadri_wide(mig_all, out / "analyse_quadri_fr_de_it_es.csv")

    cache_json = cache / "cnmigratrt_eu27_panel_rankings.json"
    try:
        panel = load_or_fetch(EU27, 2005, 2024, cache_json=cache_json)
        n = run_rank_france(panel, out / "analyse_rang_france_ue27.csv")
        print(
            f"Analyses Terra Nova : rang France ({len(n)} années), volatilité FR-DK-IT-UK, "
            "ratio asile/solde, quadri FR-DE-IT-ES."
        )
    except OSError as e:
        print(f"Analyses UE-27 (rangs) indisponibles (réseau/cache) : {e}")
        (out / "analyse_rang_france_ue27.csv").write_text(
            "annee,rang_france,nb_pays,valeur_fr,mediane_ue27\n", encoding="utf-8"
        )


if __name__ == "__main__":
    main()
