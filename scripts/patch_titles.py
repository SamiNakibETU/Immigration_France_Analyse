# -*- coding: utf-8 -*-
"""Remplace le bloc TITLES+DYADS dans app.js par la version NYT/WSJ."""
import pathlib

APP = pathlib.Path(__file__).parent.parent / "site" / "js" / "app.js"
content = APP.read_text(encoding="utf-8")

NEW_BLOCK = '''/**
 * Titres : thèse éditoriale (ce que le graphique démontre).
 * Sous-titres : variable mesurée + unité, style NYT/WSJ — une ligne max.
 */
const TITLES = {
  1: {
    title: "La France, la plus fermée parmi ses comparateurs",
    sub: "Solde migratoire net pour 1\u202f000 habitants",
  },
  2: {
    title: "La France en queue de peloton parmi ses voisins",
    sub: "Solde migratoire net pour 1\u202f000 habitants",
  },
  3: {
    title: "Sur l\u2019asile, une pression contenue en France",
    sub: "Premières demandes d\u2019asile pour 1\u202f000 habitants",
  },
  4: {
    title: "En 2024, la France dans le bas du classement européen",
    sub: "Solde migratoire net pour 1\u202f000 habitants",
  },
  5: {
    title: "Quatre grandes économies\u00a0: la France stable et discrète",
    sub: "Solde migratoire net pour 1\u202f000 habitants",
  },
  6: {
    title: "La France glisse vers les dernières places de l\u2019UE",
    sub: "Rang parmi les 27 États membres (1\u00a0= solde le plus élevé)",
  },
  7: {
    title: "L\u2019asile représente une part variable selon les pays",
    sub: "Premières demandes d\u2019asile rapportées au solde migratoire net",
  },
  asylumBars: {
    title: "Demandes d\u2019asile\u00a0: la France dans la fourchette basse",
    sub: "Premières demandes pour 1\u202f000 habitants, dernière année",
  },
  entrees: {
    title: "En entrées brutes, la France toujours en retrait",
    sub: "Ressortissants étrangers entrants pour 1\u202f000 habitants",
  },
  dual: {
    title: "Deux mesures, le même constat\u00a0: la France accueille peu",
    sub: "Pour 1\u202f000 habitants, dernière année disponible",
  },
  volatility: {
    title: "La France, trajectoire la plus stable parmi les quatre",
    sub: "Écart-type du solde annuel — amplitude des variations",
  },
};

const DYADS = [
  {
    peerKey: "DK",
    peerLabel: "Danemark",
    title: "Le Danemark de Frederiksen reste plus ouvert que la France",
    sub: "Solde migratoire net pour 1\u202f000 habitants, 2013-2024",
    colorPeer: COL.red,
  },
  {
    peerKey: "IT",
    peerLabel: "Italie",
    title: "L\u2019Italie de Meloni accueille davantage que la France",
    sub: "Solde migratoire net pour 1\u202f000 habitants, 2013-2024",
    colorPeer: COL.coral,
  },
  {
    peerKey: "UK",
    peerLabel: "Royaume-Uni",
    title: "Le Brexit n\u2019a pas fermé le Royaume-Uni à l\u2019immigration",
    sub: "Solde migratoire net pour 1\u202f000 habitants, 2013-2024",
    colorPeer: COL.plum,
  },
];'''

START_MARKER = "/**\n * Titres : angle"
DYADS_MARKER = "const DYADS = ["
END_MARKER = "];"

start = content.find(START_MARKER)
dyads_pos = content.find(DYADS_MARKER, start)
end = content.find(END_MARKER, dyads_pos) + len(END_MARKER)

assert start != -1, "TITLES block not found"
assert dyads_pos != -1, "DYADS block not found"

new_content = content[:start] + NEW_BLOCK + content[end:]
APP.write_text(new_content, encoding="utf-8")
print(f"OK - remplace [{start}:{end}] - {len(NEW_BLOCK)} car.")
