"""Ajoute les footers aux DYADS et les sources a neighborsLineFigure dans app.js."""
from pathlib import Path

APP = Path(__file__).parent.parent / "site" / "js" / "app.js"
content = APP.read_text(encoding="utf-8")

# ── 1. DYAD DK : ajouter footer apres colorPeer: COL.red ──────────────────────
old1 = '    colorPeer: COL.red,\n  },\n  {\n    peerKey: "IT",'
new1 = (
    '    colorPeer: COL.red,\n'
    '    footer: "Sources\u00a0: Eurostat, indicateur CNMIGRATRT (solde migratoire net harmonis\u00e9,'
    ' pour 1\u202f000 habitants). M\u00eames d\u00e9finitions et m\u00eame base d\u00e9mographique'
    ' pour les deux pays. P\u00e9riode 2013-2024.",\n'
    '  },\n  {\n    peerKey: "IT",'
)
assert old1 in content, "DYAD DK pattern not found"
content = content.replace(old1, new1, 1)

# ── 2. DYAD IT ────────────────────────────────────────────────────────────────
old2 = '    colorPeer: COL.coral,\n  },\n  {\n    peerKey: "UK",'
new2 = (
    '    colorPeer: COL.coral,\n'
    '    footer: "Sources\u00a0: Eurostat, indicateur CNMIGRATRT (solde migratoire net harmonis\u00e9,'
    ' pour 1\u202f000 habitants). M\u00eames d\u00e9finitions et m\u00eame base d\u00e9mographique'
    ' pour les deux pays. P\u00e9riode 2013-2024.",\n'
    '  },\n  {\n    peerKey: "UK",'
)
assert old2 in content, "DYAD IT pattern not found"
content = content.replace(old2, new2, 1)

# ── 3. DYAD UK ────────────────────────────────────────────────────────────────
old3 = '    colorPeer: COL.plum,\n  },\n];'
new3 = (
    '    colorPeer: COL.plum,\n'
    '    footer: "Sources\u00a0: Eurostat, CNMIGRATRT (France, 2013-2024, donn\u00e9es harmonis\u00e9es) ;'
    ' Office for National Statistics, Long-Term International Migration (Royaume-Uni, 2013-2024).'
    ' Les deux s\u00e9ries mesurent le solde de longue dur\u00e9e mais avec des m\u00e9thodes'
    ' non strictement identiques\u00a0: la comparaison reste indicative.",\n'
    '  },\n];'
)
assert old3 in content, "DYAD UK pattern not found"
content = content.replace(old3, new3, 1)

# ── 4. dyadLineFigure : utiliser spec.footer pour appendre le pied ────────────
old4 = '    labelGap: 14,\n  });\n}\n\n/**\n * Pictogrammes'
new4 = (
    '    labelGap: 14,\n  });\n'
    '  if (spec.footer) container.append("p").attr("class", "figure-foot").text(spec.footer);\n'
    '}\n\n/**\n * Pictogrammes'
)
assert old4 in content, "dyadLineFigure closing not found"
content = content.replace(old4, new4, 1)

# ── 5. neighborsLineFigure : ajouter le footer a la fin ─────────────────────
old5 = (
    '    height: 440,\n'
    '    margin: { top: 22, right: 148, bottom: 56, left: 64 },\n'
    '    labelGap: 16,\n'
    '  });\n'
    '}\n\n'
    'function barHFigure'
)
new5 = (
    '    height: 440,\n'
    '    margin: { top: 22, right: 148, bottom: 56, left: 64 },\n'
    '    labelGap: 16,\n'
    '  });\n'
    '  container.append("p").attr("class", "figure-foot").text(\n'
    '    "Sources\u00a0: Eurostat, indicateur CNMIGRATRT (solde migratoire net harmonis\u00e9, pour 1\u202f000 habitants). '
    'S\u00e9rie annuelle pour les pays de l\'UE-27 + Royaume-Uni disponibles dans la base Eurostat demo_gind.'
    ' La France est mise en valeur en bleu\u00a0: elle s\'inscrit syst\u00e9matiquement dans la partie basse du spectre europ\u00e9en."\n'
    '  );\n'
    '}\n\n'
    'function barHFigure'
)
assert old5 in content, "neighborsLineFigure closing not found"
content = content.replace(old5, new5, 1)

APP.write_text(content, encoding="utf-8")
print("OK - footers ajoutes aux DYADS et neighborsLineFigure")
