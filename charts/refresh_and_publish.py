"""
Efface le cache JSON Eurostat local, retélécharge via l’API, régénère PNG/CSV
et met à jour site/data.json.

Usage (depuis la racine du dossier Migrations) :
    python charts/refresh_and_publish.py
"""

from __future__ import annotations

import sys
from pathlib import Path


def _clear_cache(cache_dir: Path) -> int:
    n = 0
    for p in sorted(cache_dir.glob("*.json")):
        p.unlink(missing_ok=True)
        print(f"Cache effacé : {p.name}")
        n += 1
    ons_dir = cache_dir / "ons"
    if ons_dir.is_dir():
        for p in sorted(ons_dir.iterdir()):
            if p.is_file():
                p.unlink(missing_ok=True)
                print(f"Cache effacé : ons/{p.name}")
                n += 1
    return n


def main() -> int:
    root = Path(__file__).resolve().parent
    repo = root.parent
    cache = root / "cache"
    cache.mkdir(parents=True, exist_ok=True)
    cleared = _clear_cache(cache)
    print(f"({cleared} fichier(s) supprimé(s).)\n")

    sys.path.insert(0, str(root))
    import plot_publication

    plot_publication.main()
    print("\nFigures et CSV : charts/output/")

    try:
        import fetch_entrees_etrangers

        fetch_entrees_etrangers.main()
    except OSError as e:
        print(f"Entrées étrangers (Eurostat) : {e}")

    import subprocess

    r = subprocess.run([sys.executable, str(repo / "site" / "build_data.py")], cwd=str(repo))
    if r.returncode != 0:
        return r.returncode
    print("site/data.json à jour.")

    subprocess.run(
        [sys.executable, str(repo / "charts" / "export_xlsx_dataviz.py")],
        cwd=str(repo),
    )
    print("Excel dataviz : charts/output/terra_nova_migrations_dataviz.xlsx")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
