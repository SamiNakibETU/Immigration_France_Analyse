# -*- coding: utf-8 -*-
"""Patch les annotations dans build_data.py et drawMarkerLabels dans app.js."""
import pathlib, re

ROOT = pathlib.Path(__file__).parent.parent

# ── 1. build_data.py : remplace les blocs ANNOTATIONS_* ──────────────────────
BP = ROOT / "site" / "build_data.py"
content = BP.read_text(encoding="utf-8")

NEW_ANN = '''ANNOTATIONS_FR = [
    {"year": 2015, "text": "Pic de l'asile", "target": "FR"},
    {"year": 2020, "text": "Covid-19", "target": "FR"},
]

ANNOTATIONS = {
    "DK": [
        {"year": 2015, "text": "Pic de l'asile", "target": "peer"},
        {"year": 2019, "text": "Frederiksen PM", "target": "peer"},
        {"year": 2022, "text": "Ukraine", "target": "peer"},
    ],
    "UK": [
        {"year": 2015, "text": "Pic de l'asile", "target": "peer"},
        {"year": 2016, "text": "Brexit", "target": "peer"},
        {"year": 2021, "text": "Fin libre circ.", "target": "peer"},
        {"year": 2022, "text": "Ukraine", "target": "peer"},
    ],
}

ANNOTATIONS_IT = [
    {"year": 2015, "text": "Pic de l'asile", "target": "IT"},
    {"year": 2018, "text": "Salvini ministre", "target": "IT"},
    {"year": 2020, "text": "Covid-19", "target": "IT"},
    {"year": 2022, "text": "G. Meloni PM", "target": "IT"},
]'''

# Replace from ANNOTATIONS_FR to closing ] of ANNOTATIONS_IT
start = content.find("ANNOTATIONS_FR = [")
# find the end of ANNOTATIONS_IT block
it_start = content.find("ANNOTATIONS_IT = [", start)
it_end = content.find("\n]", it_start) + 2  # include the closing ]\n
assert start != -1 and it_end > it_start
content = content[:start] + NEW_ANN + content[it_end:]
BP.write_text(content, encoding="utf-8")
print("build_data.py patched")

# ── 2. app.js : remplace drawMarkerLabels + ajoute clipPath ──────────────────
APP = ROOT / "site" / "js" / "app.js"
js = APP.read_text(encoding="utf-8")

NEW_MARKERS = r'''/**
 * Annotations éditoriales : style callout épuré (NYT/WSJ).
 * – Tige verticale depuis le point de la courbe
 * – Petit disque plein sur le point
 * – Label texte small-caps sans icône, sans rect flou
 * – Placement alterné haut/bas selon la position verticale du point
 */
function drawMarkerLabels(svg, items, innerH) {
  if (!items.length) return;
  const layer = svg.append("g").attr("class", "annotation-markers");
  const MID = innerH != null ? innerH / 2 : 200;

  items.forEach((item) => {
    const { sx, sy, text, color } = item;

    // Placement haut ou bas selon que le point est dans la moitié basse ou haute
    const goUp = sy > MID * 0.55;
    const STEM = 34;
    const ty = goUp ? sy - STEM : sy + STEM;
    const anchor = "middle";

    // Tige
    layer.append("line")
      .attr("x1", sx).attr("y1", goUp ? sy - 5 : sy + 5)
      .attr("x2", sx).attr("y2", ty + (goUp ? 10 : -10))
      .attr("stroke", color)
      .attr("stroke-width", 0.75)
      .attr("opacity", 0.6);

    // Disque sur la courbe
    layer.append("circle")
      .attr("cx", sx).attr("cy", sy)
      .attr("r", 3)
      .attr("fill", color)
      .attr("opacity", 0.85);

    // Texte (déjà en small-caps via CSS)
    const words = text.split(" ");
    // groupes de max 2 mots par ligne
    const lines = [];
    for (let i = 0; i < words.length; i += 2) {
      lines.push(words.slice(i, i + 2).join(" "));
    }
    const lineH = 8.5;
    const totalH = lines.length * lineH;
    const yStart = goUp ? ty - totalH + lineH * 0.8 : ty + lineH * 0.8;

    lines.forEach((line, li) => {
      layer.append("text")
        .attr("class", "ann-label")
        .attr("x", sx)
        .attr("y", yStart + li * lineH)
        .attr("text-anchor", anchor)
        .attr("fill", color)
        .text(line);
    });
  });
}'''

# Replace old drawMarkerLabels function
start_m = js.find("/**\n * Événements : pictogramme")
if start_m == -1:
    start_m = js.find("/**\n * Annotations")
end_m = js.find("\nfunction makeTooltip", start_m)
assert start_m != -1 and end_m != -1, f"markers block not found s={start_m} e={end_m}"
js = js[:start_m] + NEW_MARKERS + "\n" + js[end_m:]
print("drawMarkerLabels replaced")

APP.write_text(js, encoding="utf-8")
print("app.js patched - markers done")
