# Immigration France — Analyse comparative

Visualisations interactives accompagnant la note Terra Nova
*« La France est-elle vraiment le pays le plus ouvert à l'immigration ? »*

## Ce que montre ce site

Dix-sept graphiques comparant la France au Danemark, à l'Italie et au Royaume-Uni sur le solde migratoire net, les premières demandes d'asile, les entrées brutes d'étrangers et la décomposition des flux britanniques post-Brexit. Sources : Eurostat, ONS (UK), Statistics Denmark, Istat, INSEE.

## Lancer en local

```bash
python site/build_data.py   # génère site/data.json
cd site && python -m http.server 8765
# ouvrir http://localhost:8765
```

## Structure

```
site/           → HTML + JS + CSS + data.json (généré)
charts/         → Scripts de collecte Eurostat
scripts/        → Outils : export SVG/PNG, patches
output_final/   → Figures SVG + PNG exportées
```

## Sources de données

| Indicateur | Source |
|---|---|
| Solde migratoire net harmonisé | Eurostat `demo_gind` CNMIGRATRT |
| Premières demandes d'asile | Eurostat `migr_asyappctza` |
| Entrées étrangers | Eurostat `migr_imm1ctz` |
| Solde net long terme UK | ONS Long-Term International Migration |
| Solde étrangers Danemark | Statistics Denmark |
| Solde étrangers Italie | Istat |
| Solde immigrés France | INSEE |

## Déploiement Vercel

Importer le repo sur [vercel.com](https://vercel.com), définir **Root Directory = `site`**, laisser Build Command vide.
