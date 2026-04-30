/**
 * D3, style atlas. Grille légère, typo Book / Medium. Annotations : data.annotations.
 */
/* global d3 */

/** Palette publication « La Grande Conversation » (+ dérivés grille / barres). */
const COL = {
  paper: "#F3ECE6",
  ink: "#262626",
  /** Couleur dominante publication La Grande Conversation (titres d’épisode, mise en évidence). */
  primary: "#FF6437",
  red: "#FF6437",
  blue: "#2E879A",
  plum: "#9D1453",
  accent: "#FF6437",
  coral: "#F99592",
  /* Teal soutenu pour se distinguer du bleu DK et de l’orange France */
  teal: "#1f6f82",
  grid: "#e0d6ce",
  gridLineH: "#d9cfc5",
  gridLineV: "#e4dbd3",
  muted: "#595550",
  barMuted: "#b8aea8",
  barOthers: "#6a959f",
  peerGray: "#a89f99",
};

/** Libellés à l'intérieur d'une barre : encre si le fond est clair ; papier sinon. */
function fillForBarInterior(fillHex) {
  const u = String(fillHex || "").toUpperCase();
  if (u === COL.primary.toUpperCase()) return COL.paper;
  if ([COL.coral.toUpperCase(), COL.barMuted.toUpperCase()].includes(u)) return COL.ink;
  return COL.paper;
}

/**
 * Une teinte stable par pays sur tous les graphiques (France = couleur marque).
 * DK / IT / UK ne réutilisent pas l’orange réservée à la France.
 */
const SERIE_PAYS = {
  FR: COL.primary,
  DK: COL.blue,
  IT: COL.plum,
  UK: COL.teal,
};

/** Couleurs pour séries « voisins » hors France — jamais COL.primary (réservé à FR). */
const PEER_COLORS = [COL.plum, COL.teal, COL.blue, COL.coral, COL.peerGray, COL.ink];

/**
 * Titres / sous-titres : alignés sur la note v4 (ton factuel, thèse sur le positionnement relatif de la France).
 */
const TITLES = {
  1: {
    title:
      "Solde migratoire : la France accueille 1,9 fois moins que le Danemark et 1,5 fois moins que l’Italie",
    sub:
      "Solde migratoire net pour 1 000 habitants, série annuelle (2005-2024).",
  },
  2: {
    title: "En vingt ans, la France est passée sous la trajectoire de ses six principaux voisins européens",
    sub: "Solde migratoire net pour 1 000 habitants, 2005-2024. Eurostat (CNMIGRATRT).",
  },
  3: {
    title:
      "Demandes d’asile : avec 1,9 demande pour 1 000 habitants, la France se situe dans la moyenne basse",
    sub:
      "Premières demandes d’asile pour 1 000 habitants, 2008-2024. Eurostat (migr_asyappctza, demo_pjan).",
  },
  4: {
    title: "Solde migratoire en 2024 : la France se classe 21e sur 27 dans l’Union européenne",
    sub:
      "Solde migratoire net pour 1 000 habitants, 27 États membres, 2024. Eurostat (CNMIGRATRT).",
  },
  5: {
    title: "Parmi les quatre premières économies de l’UE, la France est la seule sous la médiane européenne",
    sub:
      "Solde migratoire net pour 1 000 habitants, France, Allemagne, Italie, Espagne et médiane UE-27, 2005-2024. Eurostat.",
  },
  6: {
    title: "Classement au sein de l’UE : la France est passée du 11e au 21e rang en vingt ans",
    sub:
      "Place de la France parmi les 27 selon le solde migratoire net par habitant, 2005-2024. 1er = solde le plus élevé. Eurostat.",
  },
  7: {
    title:
      "Demandes d’asile rapportées au solde migratoire : un rapport variable selon les pays, rarement majoritaire",
    sub:
      "Premières demandes d’asile divisées par le solde migratoire net (quand il est positif), 2008-2024. Eurostat.",
  },
  asylumBars: {
    title:
      "Premières demandes d’asile en 2024 : la France reçoit moins de demandes que l’Allemagne, l’Espagne ou l’Italie",
    sub: "Premières demandes pour 1 000 habitants, 2024. Eurostat (migr_asyappctza).",
  },
  entrees: {
    title:
      "Entrées de ressortissants étrangers : le Danemark en accueille trois fois plus que la France, rapporté à sa population",
    sub:
      "Entrées pour 1 000 habitants, 2016-2024. Eurostat (migr_imm1ctz), ONS (LTIM, UK en pointillés, rupture en 2020).",
  },
  dual: {
    title:
      "En 2024, la France combine un solde migratoire et un niveau de demandes d’asile inférieurs à la plupart de ses voisins",
    sub:
      "Solde migratoire net et premières demandes d’asile, pour 1 000 habitants, dernière année disponible. Eurostat.",
  },
  volatility: {
    title: "La France est le pays où le solde migratoire varie le moins d’une année à l’autre",
    sub: "Écart-type des variations annuelles du solde net pour 1 000 habitants, 2010-2024. Eurostat, ONS.",
  },
};

const DYADS = [
  {
    peerKey: "DK",
    peerLabel: "Danemark",
    title: "En 2024, le solde migratoire danois est près de deux fois supérieur au français",
    sub: "Solde net pour 1 000 habitants, 2013-2024. Même indicateur Eurostat (CNMIGRATRT) pour les deux pays.",
    colorPeer: SERIE_PAYS.DK,
    exportSlug: "solde-france-danemark-eurostat",
    footer: "Sources : Eurostat, indicateur CNMIGRATRT (solde migratoire net harmonisé, pour 1 000 habitants). Mêmes définitions et même base démographique pour les deux pays. Période 2013-2024.",
  },
  {
    peerKey: "IT",
    peerLabel: "Italie",
    title: "Depuis 2021, l’Italie affiche un solde migratoire supérieur à celui de la France",
    sub: "Solde net pour 1 000 habitants, 2013-2024. Même indicateur Eurostat (CNMIGRATRT) pour les deux pays.",
    colorPeer: SERIE_PAYS.IT,
    exportSlug: "solde-france-italie-eurostat",
    footer: "Sources : Eurostat, indicateur CNMIGRATRT (solde migratoire net harmonisé, pour 1 000 habitants). Mêmes définitions et même base démographique pour les deux pays. Période 2013-2024.",
  },
  {
    peerKey: "UK",
    peerLabel: "Royaume-Uni",
    title: "En 2022, le solde migratoire britannique a atteint un pic cinq fois supérieur au français",
    sub: "Solde net pour 1 000 habitants, 2013-2024. France : Eurostat. Royaume-Uni : ONS (séries non strictement comparables).",
    colorPeer: SERIE_PAYS.UK,
    exportSlug: "solde-france-royaume-uni-eurostat",
    footer: "Sources : Eurostat, CNMIGRATRT (France, 2013-2024, données harmonisées) ; Office for National Statistics, Long-Term International Migration (Royaume-Uni, 2013-2024). Les deux séries mesurent le solde de longue durée mais avec des méthodes non strictement identiques : la comparaison reste indicative.",
  },
];

const DISPLAY_MULTI = {
  FR: "France",
  DE: "Allemagne",
  ES: "Espagne",
  SE: "Suède",
  NL: "Pays-Bas",
  IT: "Italie",
  DK: "Danemark",
};

function pointsFromRows(rows, key) {
  return rows
    .map((r) => ({ year: r.year, value: r[key] }))
    .filter((p) => p.value != null && Number.isFinite(p.value));
}

function extentYears(seriesPts) {
  const all = seriesPts.flat();
  return d3.extent(all, (d) => d.year);
}

function extentValues(seriesPts) {
  const all = seriesPts.flat();
  const vals = all.map((d) => d.value).filter((v) => v != null && Number.isFinite(v));
  if (!vals.length) return [0, 1];
  const lo = d3.min(vals);
  const hi = d3.max(vals);
  const pad = Math.max((hi - lo) * 0.06, 0.55);
  return [lo - pad, hi + pad];
}

function extentValuesFrom(pts2d, frac = 0.06, minPad = 0.28) {
  const all = pts2d.flat();
  const vals = all.map((d) => d.value).filter((v) => v != null && Number.isFinite(v));
  if (!vals.length) return [0, 1];
  const lo = d3.min(vals);
  const hi = d3.max(vals);
  const pad = Math.max((hi - lo) * frac, minPad);
  return [lo - pad, hi + pad];
}

/** Marge en « années » sur l’axe X : évite que points et grille rognent contre le bord du clip. */
function padLinearXDomain(dom) {
  if (!Array.isArray(dom) || dom.length < 2) return [2010, 2024];
  const lo = Number(dom[0]);
  const hi = Number(dom[1]);
  if (!Number.isFinite(lo) || !Number.isFinite(hi)) return [2010, 2024];
  if (hi <= lo) return [lo - 0.5, hi + 0.5];
  const span = hi - lo;
  const pad = Math.min(0.95, Math.max(span * 0.042, 0.28));
  return [lo - pad, hi + pad];
}

function layoutEndLabels(series, xScale, yScale, innerW, innerH, gap = 15) {
  const items = [];
  for (const s of series) {
    const pts = s.points.filter((p) => p.value != null && Number.isFinite(p.value));
    if (!pts.length) continue;
    const last = pts[pts.length - 1];
    items.push({
      series: s,
      px: xScale(last.year),
      py: yScale(last.value),
      last,
    });
  }
  items.sort((a, b) => a.py - b.py);
  const effGap =
    gap + Math.max(0, items.length - 2) * 2 + (items.length >= 6 ? 4 : items.length >= 4 ? 2 : 0);

  function spreadVertical(group) {
    let ly = group.map((d) => d.py);
    for (let p = 0; p < 22; p++) {
      for (let i = 1; i < ly.length; i++) {
        if (ly[i] - ly[i - 1] < effGap) ly[i] = ly[i - 1] + effGap;
      }
      for (let i = ly.length - 2; i >= 0; i--) {
        if (ly[i + 1] - ly[i] < effGap) ly[i] = ly[i + 1] - effGap;
      }
    }
    ly = ly.map((yy) => Math.min(Math.max(yy, 10), innerH - 10));
    group.forEach((d, i) => {
      d.ly = ly[i];
    });
  }

  if (items.length >= 4) {
    const col0 = items.filter((_, i) => i % 2 === 0);
    const col1 = items.filter((_, i) => i % 2 === 1);
    spreadVertical(col0);
    spreadVertical(col1);
    items.forEach((d, i) => {
      d.col = i % 2;
    });
  } else {
    spreadVertical(items);
    items.forEach((d) => {
      d.col = 0;
    });
  }
  return items;
}

/**
 * Bras de raccord dernier point → colonne libellés : orthogonal (pas de diagonale
 * traversant les autres courbes) ; retourne d pour un path SVG.
 */
function endLabelLeadPath(px, py, lx, ly) {
  const minRight = px + 16;
  const target = px + 30;
  const maxBendBeforeLabel = lx - 14;
  const bx = Math.max(minRight, Math.min(target, maxBendBeforeLabel));
  return `M${px},${py} H${bx} V${ly} H${lx - 8}`;
}

/** Clé « pays comparant » (dernière série hors France). */
function resolvePeerKey(seriesDefs) {
  const peers = seriesDefs.map((d) => d.key).filter((k) => k !== "FR");
  return peers.length ? peers[peers.length - 1] : seriesDefs[1]?.key ?? null;
}

/**
 * Vue 4 pays : annotations dédupliquées par texte+année, placées sur la courbe
 * la plus haute à chaque millésime. Max 1 par tranche de 2 ans pour éviter
 * les chevauchements dans les zones denses (2014-2016, 2019-2022).
 */
function overviewAnnotations(data, rows) {
  const all = [];
  for (const key of ["FR", "DK", "IT", "UK"]) {
    for (const a of data.annotations?.[key] ?? []) {
      all.push({ year: a.year, text: a.text, country: key });
    }
  }
  const seen = new Set();
  const unique = [];
  for (const a of all) {
    const k = `${a.year}|${a.text}`;
    if (!seen.has(k)) { seen.add(k); unique.push(a); }
  }
  const keys = ["FR", "DK", "IT", "UK"];
  const mapped = unique.map((a) => {
    let bestKey = a.country;
    let bestVal = -Infinity;
    const row = rows.find((r) => r.year === a.year);
    if (row) {
      for (const k of keys) {
        if (row[k] != null && Number.isFinite(row[k]) && row[k] > bestVal) {
          bestVal = row[k]; bestKey = k;
        }
      }
    }
    return { year: a.year, text: a.text, target: bestKey };
  });
  mapped.sort((a, b) => a.year - b.year);
  const filtered = [];
  let lastYear = -99;
  for (const a of mapped) {
    if (a.year - lastYear >= 2) { filtered.push(a); lastYear = a.year; }
  }
  return filtered;
}

/** Annotations événementielles pour un seul pays pair (Danemark, Italie ou Royaume-Uni). */
function annotationsForPeer(data, peerKey) {
  const list = data.annotations?.[peerKey] ?? [];
  return list.map((a) => ({
        year: a.year,
        text: a.text,
    target: a.target === "peer" ? peerKey : a.target,
  }));
}

/** Duos France + X : jalons sur la France et sur le pays comparé (comme dans le texte Word). */
function annotationsForDyad(data, peerKey) {
  const fr = (data.annotations?.FR ?? []).map((a) => ({
    year: a.year,
    text: a.text,
    target: a.target === "peer" ? "FR" : a.target,
  }));
  return fr.concat(annotationsForPeer(data, peerKey));
}

/** Graphique ligne à deux pays (France + un comparateur), axe X resserré. */
function dyadLineFigure(container, data, tooltip, spec) {
  const { peerKey, peerLabel, title, sub, colorPeer } = spec;
  if (spec.exportSlug) container.attr("data-export-slug", spec.exportSlug);
  const rows = data.migrationSelection;
  figureHead(container, { title, sub });
  const host = container.append("div").attr("class", "chart-host");
  const frPts = pointsFromRows(rows, "FR");
  const peerPts = pointsFromRows(rows, peerKey);
  const yDom = extentValues([frPts, peerPts]);
  lineChartFigure(host, {
    rows,
    seriesDefs: [
      { key: "FR", label: "France", color: SERIE_PAYS.FR, width: 2.9 },
      { key: peerKey, label: peerLabel, color: colorPeer, width: 2.35 },
    ],
    annotations: annotationsForDyad(data, peerKey),
    tooltip,
    yDomain: yDom,
    xDomain: [2013, 2024],
    height: 420,
    margin: { top: 20, right: 188, bottom: 52, left: 64 },
    labelGap: 14,
  });
  if (spec.footer) container.append("p").attr("class", "figure-foot").text(spec.footer);
}

/**
 * Pictogrammes 24×24 : étoile, soleil, globe.
 * Inspirés des conventions d’icônes outline (Lucide-like), rendus en SVG natif.
 */
const EVENT_MARKER_ICONS = [
  {
    id: "star",
    draw(g, color) {
      g.append("path")
        .attr("d", "M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z")
        .attr("fill", color)
        .attr("stroke", COL.paper)
        .attr("stroke-width", 0.65)
        .attr("stroke-linejoin", "round");
    },
  },
  {
    id: "sun",
    draw(g, color) {
      const w = 1.35;
      const cap = "round";
      g.append("circle").attr("cx", 12).attr("cy", 12).attr("r", 4).attr("fill", color).attr("stroke", COL.paper).attr("stroke-width", 0.5);
      const rays =
        "M12 2v2.5M12 19.5V22M4.2 4.2l1.8 1.8M18 18l1.8 1.8M2 12h2.5M19.5 12H22M4.2 19.8l1.8-1.8M18 6l1.8-1.8";
      g.append("path").attr("d", rays).attr("fill", "none").attr("stroke", color).attr("stroke-width", w).attr("stroke-linecap", cap);
    },
  },
  {
    id: "globe",
    draw(g, color) {
      const w = 1.25;
      g.append("circle").attr("cx", 12).attr("cy", 12).attr("r", 9).attr("fill", "none").attr("stroke", color).attr("stroke-width", w);
      g.append("path").attr("d", "M2 12h20").attr("fill", "none").attr("stroke", color).attr("stroke-width", w * 0.9);
      g.append("ellipse").attr("cx", 12).attr("cy", 12).attr("rx", 9).attr("ry", 3.6).attr("fill", "none").attr("stroke", color).attr("stroke-width", w * 0.85);
      g.append("path").attr("d", "M5 8.5c2.2 2.8 4.8 4.2 7 4.2s4.8-1.4 7-4.2M5 15.5c2.2-2.8 4.8-4.2 7-4.2s4.8 1.4 7 4.2").attr("fill", "none").attr("stroke", color).attr("stroke-width", w * 0.75).attr("stroke-linecap", "round");
    },
  },
];

/** 0 étoile, 1 soleil, 2 globe (selon le texte de l’événement). */
function pickEventIconIndex(text, seqIndex) {
  const t = (text || "").toLowerCase();
  if (t.includes("ukraine") || t.includes("guerre")) return 1;
  if (t.includes("brexit") || t.includes("libre circ") || t.includes("populiste")) return 2;
  if (t.includes("frederiksen") || t.includes("meloni")) return 2;
  if (t.includes("pic") || t.includes("crise") || t.includes("covid") || t.includes("asile")) return 0;
  return seqIndex % EVENT_MARKER_ICONS.length;
}

/**
 * Annotations éditoriales : style callout épuré (NYT/WSJ).
 * - Tige verticale depuis le point de la courbe
 * - Petit disque plein sur le point
 * - Label texte small-caps sans icône, sans rect flou
 * - Placement alterné haut/bas selon la position verticale du point
 */
function closestPointByYear(points, year) {
  const withVal = points.filter((p) => p.value != null && Number.isFinite(p.value));
  if (!withVal.length) return null;
  let best = withVal[0];
  let bestD = Math.abs(best.year - year);
  for (const p of withVal) {
    const d = Math.abs(p.year - year);
    if (d < bestD) {
      bestD = d;
      best = p;
    }
  }
  return best;
}

/**
 * Valeur Y sur la courbe : tige + disque + libellé chiffré (sans petites capitales).
 * plotMidY : coordonnée Y absolue SVG du milieu vertical de la zone de tracé.
 */
function drawPointValueLabels(svg, items, plotMidY) {
  if (!items.length) return;
  const layer = svg.append("g").attr("class", "annotation-point-values").attr("pointer-events", "none");

  items.forEach((item) => {
    const { sx, sy, text, color } = item;
    const goUp = sy > plotMidY;
    const STEM = 38;
    const ty = goUp ? sy - STEM : sy + STEM;

    layer
      .append("line")
      .attr("x1", sx)
      .attr("y1", goUp ? sy - 5 : sy + 5)
      .attr("x2", sx)
      .attr("y2", ty + (goUp ? 9 : -9))
      .attr("stroke", color)
      .attr("stroke-width", 0.75)
      .attr("opacity", 0.6);

    layer
      .append("circle")
      .attr("cx", sx)
      .attr("cy", sy)
      .attr("r", 3.2)
      .attr("fill", color)
      .attr("opacity", 0.9);

    const lineH = 11;
    const yStart = goUp ? ty - lineH + 3 : ty + lineH - 2;

    layer
      .append("text")
      .attr("class", "ann-point-value")
      .attr("x", sx)
      .attr("y", yStart)
      .attr("text-anchor", "middle")
      .attr("fill", color)
      .attr("font-size", 10.75)
      .attr("font-weight", "600")
      .attr("letter-spacing", "0.02em")
      .text(text);
  });
}

function drawMarkerLabels(svg, items, plotMidY, plotTop) {
  if (!items.length) return;
  const layer = svg.append("g").attr("class", "annotation-markers");
  /* Bande haute (~22 % depuis le haut du tracé) : évite les étiquettes rognées en tête du SVG */
  const topBand =
    plotTop != null && plotMidY != null ? plotTop + (plotMidY - plotTop) * 0.22 : null;

  items.forEach((item) => {
    const { sx, sy, text, color } = item;
    const tLower = String(text || "").toLowerCase();
    const forceBelow =
      /\bukraine\b/.test(tLower) || (topBand != null && sy <= topBand);
    const goUp = !forceBelow && sy > plotMidY;
    const STEM = forceBelow ? 58 : 42;
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
    const lineH = 10;
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
}

function makeTooltip(el) {
  return {
    show(html, x, y) {
      el.innerHTML = html;
      el.classList.add("visible");
      el.style.left = `${x + 12}px`;
      el.style.top = `${y + 12}px`;
    },
    hide() {
      el.classList.remove("visible");
    },
  };
}

function lineChartFigure(container, opts) {
  const {
    rows,
    seriesDefs,
    annotations,
    yDomain: yDomIn,
    xDomain: xDomIn,
    tooltip,
    yLabel = "Pour 1 000 habitants",
    height = 400,
    margin: marginOverride,
    labelGap = 17,
    curve = d3.curveLinear,
  } = opts;

  const margin = { top: 18, right: 142, bottom: 52, left: 62, ...marginOverride };
  const hasCallout =
    annotations?.some((a) => {
      if (a == null || String(a.text || "").trim() === "") return false;
      return a.calloutStyle !== "pointValue";
    }) ?? false;
  if (hasCallout) margin.top += 14;

  const series = seriesDefs.map((d) => ({
    key: d.key,
    label: d.label,
    color: d.color,
    dash: d.dash || null,
    width: d.width ?? 2.2,
    points: pointsFromRows(rows, d.key),
  }));

  const allPts = series.map((s) => s.points);
  let xDom = xDomIn ? [Number(xDomIn[0]), Number(xDomIn[1])] : extentYears(allPts);
  xDom = padLinearXDomain(xDom);
  const yDom = yDomIn || extentValues(allPts);

  const nSer = series.length;
  if (nSer >= 7) margin.right += 28;
  else if (nSer >= 5) margin.right += 16;

  /* Largeur nominale fixe (900) : alignée sur .figure-sub / export ; le rendu suit le conteneur via CSS (width 100%). */
  const w = 900;
  const innerW = w - margin.left - margin.right;
  const innerH = height - margin.top - margin.bottom;

  const svg = container
    .append("svg")
    .attr("class", "chart-line-swiss")
    .attr("viewBox", `0 0 ${w} ${height}`)
    .attr("width", "100%")
    .attr("preserveAspectRatio", "xMinYMin meet");

  const lx = margin.left * 0.36;
  const ly = margin.top + innerH / 2;
  svg
    .append("g")
    .attr("class", "y-axis-label")
    .attr("transform", `translate(${lx},${ly}) rotate(-90)`)
    .append("text")
    .attr("text-anchor", "middle")
    .attr("fill", COL.muted)
    .attr("font-size", yLabel.length > 42 ? 8.5 : 9.5)
    .attr("font-weight", "500")
    .text(yLabel);

  const clipId = `clip-${Math.random().toString(36).slice(2, 8)}`;
  svg.append("defs").append("clipPath").attr("id", clipId)
    .append("rect").attr("x", 0).attr("y", -8).attr("width", innerW + 2).attr("height", innerH + 16);

  const g = svg.append("g").attr("transform", `translate(${margin.left},${margin.top})`);

  const x = d3.scaleLinear().domain(xDom).range([0, innerW]);
  const y = d3.scaleLinear().domain(yDom).range([innerH, 0]);
  const yMax = yDom[1];

  /* Grille verticale puis horizontale (repères de lecture, pas le filet export titre/graphique). */
  const xGridTicks = Math.min(12, Math.max(6, Math.floor((xDom[1] - xDom[0]) / 2)));
  g.append("g")
    .attr("class", "chart-grid-v")
    .selectAll("line")
    .data(x.ticks(xGridTicks))
    .join("line")
    .attr("class", "chart-grid-line-v")
    .attr("x1", (d) => x(d))
    .attr("x2", (d) => x(d))
    .attr("y1", 0)
    .attr("y2", innerH);

  const yTicks = y.ticks(6).filter((d) => d < yMax - 1e-9);
  g.append("g")
    .attr("class", "chart-grid-h")
    .selectAll("line")
    .data(yTicks)
    .join("line")
    .attr("class", "chart-grid-line")
    .attr("x1", 0)
    .attr("x2", innerW)
    .attr("y1", (d) => y(d))
    .attr("y2", (d) => y(d));

  const yAxisG = g.append("g").call(
    d3.axisLeft(y).ticks(6).tickFormat(d3.format(".1f")).tickSize(0).tickPadding(9),
  );
  yAxisG.select(".domain").remove();
  yAxisG.selectAll(".tick line").remove();
  yAxisG.selectAll(".tick text").attr("fill", COL.ink).attr("font-size", 9.5).attr("font-weight", "450");

  const line = d3.line().x((d) => x(d.year)).y((d) => y(d.value)).curve(curve).defined((d) => d.value != null);

  const targetMap = Object.fromEntries(series.map((s) => [s.key, s]));
  const peerKey = resolvePeerKey(seriesDefs);

  const linesG = g.append("g").attr("clip-path", `url(#${clipId})`);
  series.forEach((s) => {
    if (!s.points.length) return;
    const path = linesG
      .append("path")
      .datum(s.points)
      .attr("fill", "none")
      .attr("stroke", s.color)
      .attr("stroke-width", s.width)
      .attr("stroke-linejoin", "round")
      .attr("stroke-linecap", "round")
      .attr("d", line);
    if (s.dash) path.attr("stroke-dasharray", s.dash);

    /* Points visibles sur la courbe - minimalistes, sans halo */
    linesG.selectAll(`.vis-dot-${s.key}`)
      .data(s.points.filter((d) => d.value != null))
      .join("circle")
      .attr("class", `vis-dot-${s.key}`)
      .attr("cx", (d) => x(d.year))
      .attr("cy", (d) => y(d.value))
      .attr("r", 2.5)
      .attr("fill", s.color)
      .attr("pointer-events", "none");

    /* Zones de survol invisibles (plus grandes pour faciliter le tooltip) */
    g.selectAll(`.dot-${s.key}`)
      .data(s.points)
      .join("circle")
      .attr("class", `dot-${s.key}`)
      .attr("cx", (d) => x(d.year))
      .attr("cy", (d) => y(d.value))
      .attr("r", 9)
      .attr("fill", "none")
      .attr("pointer-events", "all")
      .on("mouseenter", (ev, d) => {
        const frSeries = series.find((ss) => ss.key === "FR");
        const frPt = s.key !== "FR" && frSeries ? frSeries.points.find((p) => p.year === d.year) : null;
        const swatch = `<span class="tt-swatch" style="background:${s.color}"></span>`;
        let html = `<div class="tt-head">${swatch}<strong>${s.label}</strong></div>`;
        html += `<div class="tt-row"><span class="tt-yr">${d.year}</span><span class="tt-val">${d.value.toFixed(2)}\u202f‰</span></div>`;
        if (frPt) {
          const diff = (d.value - frPt.value);
          const sign = diff >= 0 ? "+" : "";
          html += `<div class="tt-compare">France\u00a0: ${frPt.value.toFixed(2)}\u202f‰ <span class="tt-diff">(${sign}${diff.toFixed(2)})</span></div>`;
        }
        tooltip._html = html;
        tooltip.show(html, ev.clientX, ev.clientY);
      })
      .on("mousemove", (ev) => {
        if (tooltip._html) tooltip.show(tooltip._html, ev.clientX, ev.clientY);
      })
      .on("mouseleave", () => tooltip.hide());
  });

  const yearSpan = xDom[1] - xDom[0];
  const xTickCount = Math.min(12, Math.max(6, Math.floor(yearSpan / 2)));
  const xAxisG = g
    .append("g")
    .attr("transform", `translate(0,${innerH})`)
    .call(d3.axisBottom(x).ticks(xTickCount).tickFormat(d3.format("d")).tickSize(0).tickPadding(8));
  xAxisG.select(".domain").remove();
  xAxisG.selectAll(".tick line").remove();
  xAxisG.selectAll(".tick text").attr("fill", COL.ink).attr("font-size", 9.5).attr("font-weight", "450").attr("dy", "0.9em");

  g.append("text")
    .attr("x", innerW / 2)
    .attr("y", innerH + 38)
    .attr("text-anchor", "middle")
    .attr("fill", COL.muted)
    .attr("font-size", 9)
    .attr("font-weight", "500")
    .text("Année");

  const labelColW = series.length >= 4 ? 70 : 0;
  const labelXBase = innerW + 14;
  const labelGapUse = Math.max(labelGap, 12 + Math.max(0, series.length - 2) * 2.8);
  const layouts = layoutEndLabels(series, x, y, innerW, innerH, labelGapUse);
  const lg = g.append("g").attr("class", "end-labels").attr("pointer-events", "none");
  const lgLines = lg.append("g").attr("class", "end-label-lines").attr("pointer-events", "none");
  layouts.forEach((d) => {
    const lx = labelXBase + (d.col || 0) * labelColW;
    lgLines.append("path")
      .attr("d", endLabelLeadPath(d.px, d.py, lx, d.ly))
      .attr("fill", "none")
      .attr("stroke", d.series.color)
      .attr("stroke-width", 0.65)
      .attr("stroke-linejoin", "round")
      .attr("opacity", 0.82);
  });

  const calloutItems = [];
  const pointValueItems = [];
  if (annotations && annotations.length) {
    annotations.forEach((ann) => {
      const tgtKey = ann.target === "peer" ? peerKey : ann.target;
      const s = targetMap[tgtKey];
      if (!s) return;
      const pt =
        s.points.find((p) => p.year === ann.year) || closestPointByYear(s.points, ann.year);
      if (!pt || pt.value == null) return;
      const sx = margin.left + x(pt.year);
      const sy = margin.top + y(pt.value);
      const color = ann.color || s.color;
      if (ann.calloutStyle === "pointValue") {
        const v = pt.value;
        const text =
          ann.text != null && String(ann.text).trim() !== ""
            ? ann.text
            : String(Number.isInteger(v) ? v : Math.round(Number(v)));
        pointValueItems.push({ sx, sy, text, color });
      } else {
        if (ann.text == null || String(ann.text).trim() === "") return;
        calloutItems.push({ sx, sy, text: ann.text, color });
      }
    });
    const plotMidY = margin.top + innerH / 2;
    drawMarkerLabels(svg, calloutItems, plotMidY, margin.top);
    drawPointValueLabels(svg, pointValueItems, plotMidY);
  }

  const lgTexts = lg.append("g").attr("class", "end-label-texts").attr("pointer-events", "none");
  layouts.forEach((d) => {
    const lx = labelXBase + (d.col || 0) * labelColW;
    lgTexts
      .append("text")
      .attr("x", lx)
      .attr("y", d.ly)
      .attr("dy", "0.35em")
      .attr("fill", d.series.color)
      .attr("font-size", 10.25)
      .attr("font-weight", "600")
      .attr("paint-order", "normal")
      .attr("stroke", "none")
      .text(d.series.label);
  });
}

/** Un seul panneau : France (couleur marque) + pays voisins, sans FX. */
/** Domaine X avec valeurs négatives possibles (0 toujours visible si min &lt; 0 &lt; max). */
function xDomainSignedBars(values) {
  const nums = values.map(Number).filter((v) => Number.isFinite(v));
  if (!nums.length) return [0, 1];
  const minV = d3.min(nums);
  const maxV = d3.max(nums);
  const lo = Math.min(0, minV);
  const hi = Math.max(0, maxV);
  const span = Math.max(hi - lo, 1e-6);
  const pad = Math.max(span * 0.08, 0.12);
  return [lo - pad, hi + pad];
}

/** Barre horizontale signée : origine x(0), largeur vers la valeur. */
function layoutSignedHBar(value, xScale, x0) {
  const xv = xScale(value);
  if (value >= 0) {
    const left = Math.min(x0, xv);
    return {
      rectX: left,
      rectW: Math.max(0, Math.abs(xv - x0)),
      labelX: Math.max(x0, xv) + 6,
      anchor: "start",
    };
  }
  const left = xv;
  const w = Math.max(0, x0 - xv);
  if (w < 16) {
    return {
      rectX: left,
      rectW: w,
      labelX: x0 + 6,
      anchor: "start",
    };
  }
  return {
    rectX: left,
    rectW: w,
    labelX: left + w / 2,
    anchor: "middle",
  };
}

/** Grille verticale discrète sur barres horizontales (repères, sans trait d’axe). */
function appendHorizontalBarGrid(g, x, inset, innerH, tickCount) {
  const ticks = x.ticks(tickCount);
  g.append("g")
    .attr("class", "bar-plot-grid")
    .selectAll("line")
    .data(ticks)
    .join("line")
    .attr("class", "bar-grid-line")
    .attr("x1", (d) => x(d))
    .attr("x2", (d) => x(d))
    .attr("y1", inset.top)
    .attr("y2", innerH - inset.bottom);
}

/** Graduations en chiffres sous le graphique (sans composant axe D3). */
function appendBarTickLabelsX(g, x, innerH, tickCount, fontSize = 8.75) {
  const ticks = x.ticks(tickCount);
  const fmt = d3.format(".2f");
  ticks.forEach((t) => {
    g.append("text")
      .attr("class", "bar-tick-label")
      .attr("x", x(t))
      .attr("y", innerH + 18)
      .attr("text-anchor", "middle")
      .attr("fill", COL.muted)
      .attr("font-size", fontSize)
      .attr("font-weight", "450")
      .text(fmt(t));
  });
}

/** Libellés catégories à gauche (sans composant axe D3). fillForLabel(lab) peut surcharger la couleur. */
function appendBarCategoryLabelsY(g, y, fontSize = 9.25, fillForLabel = null) {
  y.domain().forEach((lab) => {
    const fill =
      typeof fillForLabel === "function"
        ? fillForLabel(lab) || COL.ink
        : COL.ink;
    g.append("text")
      .attr("class", "bar-y-label")
      .attr("x", -6)
      .attr("y", y(lab) + y.bandwidth() / 2)
      .attr("dy", "0.35em")
      .attr("text-anchor", "end")
      .attr("fill", fill)
      .attr("font-size", fontSize)
      .attr("font-weight", fill !== COL.ink ? "600" : "450")
      .text(lab);
  });
}

function neighborsLineFigure(container, data, tooltip) {
  container.attr("data-export-slug", "voisins-six-pays-et-la-france");
  const rows = data.migrationMulti;
  const eu = ["FR", "DE", "ES", "SE", "NL", "IT", "DK"];
  const frPts = pointsFromRows(rows, "FR");
  const others = eu.filter((c) => c !== "FR");
  const botSeriesPts = others.map((code) => pointsFromRows(rows, code));
  const yDom = extentValuesFrom([frPts, ...botSeriesPts], 0.06, 0.32);
  const xDom = extentYears([frPts, ...botSeriesPts]);

  figureHead(container, TITLES[2]);

  const host = container.append("div").attr("class", "chart-host");
  const seriesDefs = [
    ...others.map((code) => ({
      key: code,
      label: DISPLAY_MULTI[code] || code,
      color: code === "IT" ? SERIE_PAYS.IT : COL.peerGray,
      width: 1.75,
    })),
    {
      key: "FR",
      label: "France",
      color: SERIE_PAYS.FR,
      width: 3,
    },
  ];

  lineChartFigure(host, {
    rows,
    seriesDefs,
    annotations: [],
    tooltip,
    yDomain: yDom,
    xDomain: xDom,
    height: 440,
    margin: { top: 22, right: 148, bottom: 56, left: 64 },
    labelGap: 16,
  });
  container.append("p").attr("class", "figure-foot").text(
    "Sources : Eurostat, indicateur CNMIGRATRT (solde migratoire net harmonisé, pour 1 000 habitants). Série annuelle pour les pays de l'UE-27 + Royaume-Uni disponibles dans la base Eurostat demo_gind. La France est mise en valeur en orange, l’Italie en bordeaux, les autres pays voisins en gris : la France s’inscrit systématiquement dans la partie basse du spectre européen."
  );
}

function barHFigure(container, opts) {
  const {
    rows,
    title,
    sub,
    xLabel,
    valueFormat = (v) => v.toFixed(2),
    barColor,
    labelColor,
    rowH = 38,
    bandPadding = 0.32,
    /** Couleur du libellé Y : (lab) => couleur. Défaut : France en rouge si barre « classique », sinon encre. */
    categoryLabelFill = null,
  } = opts;

  if (title) container.append("h2").attr("class", "figure-title").text(title);
  if (sub) container.append("p").attr("class", "figure-sub").text(sub);

  const wrap = container.append("div").attr("class", "chart-host chart-bar-swiss");
  const w = 900;
  const margin = { top: 12, right: 72, bottom: 40, left: 168 };
  const innerW = w - margin.left - margin.right;
  const innerH = rows.length * rowH;
  const height = Math.max(innerH, 80) + margin.top + margin.bottom;

  const svg = wrap
    .append("svg")
    .attr("viewBox", `0 0 ${w} ${height}`)
    .attr("width", "100%")
    .attr("height", height);

  const g = svg.append("g").attr("transform", `translate(${margin.left},${margin.top})`);

  const inset = { left: 10, right: 10, top: 8, bottom: 10 };
  const vals = rows.map((d) => d.value);
  const useSigned = vals.some((v) => Number.isFinite(v) && v < 0);
  const maxV = d3.max(vals);
  const xDom = useSigned ? xDomainSignedBars(vals) : [0, (Number.isFinite(maxV) ? maxV : 0) * 1.14 || 1];
  const x = d3.scaleLinear().domain(xDom).range([inset.left, innerW - inset.right]);

  const y = d3
    .scaleBand()
    .domain(rows.map((d) => d.yLabel || d.label))
    .range([inset.top, innerH - inset.bottom])
    .paddingInner(bandPadding)
    .paddingOuter(0.12);

  const x0 = x(0);

  appendHorizontalBarGrid(g, x, inset, innerH, 7);
  appendBarTickLabelsX(g, x, innerH, 7);

  g.append("text")
    .attr("x", innerW / 2)
    .attr("y", innerH + 32)
    .attr("text-anchor", "middle")
    .attr("fill", COL.muted)
    .attr("font-size", 9)
    .attr("font-weight", "500")
    .text(xLabel);

  appendBarCategoryLabelsY(
    g,
    y,
    9.25,
    categoryLabelFill ??
      ((lab) => {
        const row = rows.find((d) => (d.yLabel || d.label) === lab);
        return row?.code === "FR" ? COL.red : COL.ink;
      })
  );

  rows.forEach((d) => {
    const yy = y(d.yLabel || d.label);
    const lay = layoutSignedHBar(d.value, x, x0);
    const c = typeof barColor === "function" ? barColor(d) : barColor;
    g.append("rect")
      .attr("class", "bar-fill")
      .attr("x", lay.rectX)
      .attr("y", yy)
      .attr("width", lay.rectW)
      .attr("height", y.bandwidth())
      .attr("fill", c)
      .attr("rx", 2)
      .attr("ry", 2);

    const lc = typeof labelColor === "function" ? labelColor(d) : labelColor;
    g.append("text")
      .attr("x", lay.labelX)
      .attr("y", yy + y.bandwidth() / 2)
      .attr("dy", "0.35em")
      .attr("text-anchor", lay.anchor)
      .attr("fill", lc)
      .attr("font-size", 9.25)
      .attr("font-weight", "600")
      .text(valueFormat(d.value));
  });
}

/** Slug fichier à partir du titre de figure (export Word). */
function slugifyTitle(s) {
  const ascii = String(s || "figure")
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .replace(/[^a-zA-Z0-9]+/g, "-")
    .replace(/^-|-$/g, "");
  return (ascii || "figure").toLowerCase().slice(0, 55);
}

function parseSvgPixelSize(svgEl) {
  const vb = svgEl.getAttribute("viewBox");
  if (vb) {
    const parts = vb.trim().split(/[\s,]+/);
    if (parts.length >= 4) {
      const w = Number.parseFloat(parts[2]);
      const h = Number.parseFloat(parts[3]);
      if (Number.isFinite(w) && Number.isFinite(h) && w > 0 && h > 0) return { w, h };
    }
  }
  const w = Number.parseFloat(svgEl.getAttribute("width")) || 900;
  const h = Number.parseFloat(svgEl.getAttribute("height")) || 460;
  return { w, h };
}

const SVG_NS = "http://www.w3.org/2000/svg";

/** Retours à la ligne pour titres / sous-titres dans l’export (largeur ~ largeur SVG). Les \n imposent une coupure (paragraphes sources). */
function wrapTextToLines(text, maxChars) {
  if (!text) return [];
  const blocks = String(text).split("\n");
  const lines = [];
  for (const block of blocks) {
    if (!block.trim()) {
      lines.push("\u00a0");
      continue;
    }
    const words = block.trim().split(/\s+/).filter(Boolean);
    let cur = "";
    for (const w of words) {
      const trial = cur ? `${cur} ${w}` : w;
      if (trial.length > maxChars && cur) {
        lines.push(cur);
        cur = w;
      } else cur = trial;
    }
    if (cur) lines.push(cur);
  }
  return lines;
}

/**
 * Césure export : ~7 px / car. pour titre 16px, ~5,8 pour sous-titre 11px (évite les lignes qui
 * dépassent la viewBox et sont rognées dans Word / Figma).
 */
function exportWrapLimits(chartWidthPx) {
  const usable = Math.max(280, chartWidthPx - 56);
  return {
    title: Math.max(32, Math.floor(usable / 7.1)),
    sub: Math.max(44, Math.floor(usable / 5.85)),
    panel: Math.max(40, Math.floor(usable / 6.2)),
    /* Pied : comme le sous-titre (même colonne que la zone tracé, pas de lignes trop longues). */
    foot: Math.max(44, Math.floor(usable / 5.9)),
  };
}

/**
 * Styles critiques inlinés dans le SVG exporté (Word n’applique pas main.css).
 * Couleurs et pile typo alignées sur :root / .figure-* dans main.css.
 */
const EXPORT_SVG_STYLES = `
svg { background-color: ${COL.paper}; }
text, tspan {
  font-family: "Overused Grotesk", "Helvetica Neue", Helvetica, system-ui, sans-serif !important;
}
.chart-line-swiss .end-label-lines path {
  stroke-linejoin: round; stroke-linecap: round;
  vector-effect: non-scaling-stroke;
}
.chart-line-swiss .end-label-texts text {
  stroke: none; paint-order: normal; shape-rendering: optimizeLegibility;
}
.chart-line-swiss .chart-grid-line {
  stroke: ${COL.gridLineH}; stroke-width: 0.85px; opacity: 0.95;
  vector-effect: non-scaling-stroke; shape-rendering: crispEdges;
}
.chart-line-swiss .chart-grid-line-v {
  stroke: ${COL.gridLineV}; stroke-width: 0.5px; opacity: 0.7;
  vector-effect: non-scaling-stroke; shape-rendering: crispEdges;
}
.chart-line-swiss .end-label-lines path { stroke-width: 0.65px; opacity: 0.82; }
.chart-line-swiss .y-axis-label text { fill: ${COL.muted}; }
g.tick text { fill: ${COL.ink}; font-size: 9.5px; font-weight: 450; }
.annotation-markers line {
  stroke: currentColor; stroke-width: 0.75px; stroke-dasharray: 2.5 2; opacity: 0.6;
}
.annotation-markers .ann-label {
  font-size: 9px; font-weight: 600; letter-spacing: 0.045em; text-transform: uppercase;
  stroke: none; paint-order: normal;
}
.annotation-point-values .ann-point-value {
  font-family: "Overused Grotesk", "Helvetica Neue", Helvetica, system-ui, sans-serif;
  text-transform: none;
  stroke: none; paint-order: normal;
}
.chart-bar-swiss .bar-plot-grid .bar-grid-line {
  stroke: ${COL.grid}; stroke-width: 0.5px; opacity: 0.42;
  vector-effect: non-scaling-stroke;
}
.chart-bar-swiss .bar-fill { vector-effect: non-scaling-stroke; }
`;

/** Typo export SVG : calée sur .figure-title / .figure-sub / .figure-foot (main.css). */
const EXPORT_TITLE_LH = 21;
const EXPORT_SUB_LH = 19;
const EXPORT_FOOT_LH = 15;

/** Tiret ASCII seul (pas d’en dash ni d’em dash) pour export et cohérence. */
function normalizeTypographyHyphens(s) {
  return String(s || "")
    .replace(/\u2011/g, "-")
    .replace(/\u2013/g, "-")
    .replace(/\u2014/g, "-");
}

/**
 * SVG autonome : bandeau titre + sous-titre (+ panneau optionnel), styles inline,
 * graphique décalé sous le bandeau (comme sur la page).
 * Textes toujours lus depuis le DOM (.figure-title, .figure-sub, .figure-foot) - pas de variante export.
 */
function buildExportRootSvg(chartSvg, articleEl) {
  const { w: cw, h: ch } = parseSvgPixelSize(chartSvg);
  /* Largeur document = largeur du SVG graphique : titre, sources et tracé partagent la même colonne. */
  const totalW = cw;
  const padChartX = 0;
  const textX = 28;
  const lim = exportWrapLimits(cw);
  const title = normalizeTypographyHyphens(
    articleEl?.querySelector(".figure-title")?.textContent?.trim() || "Figure",
  );
  const sub = normalizeTypographyHyphens(articleEl?.querySelector(".figure-sub")?.textContent?.trim() || "");
  const footText = normalizeTypographyHyphens(
    articleEl?.querySelector(".figure-foot")?.textContent?.trim() || "",
  );
  const titleLines = wrapTextToLines(title, lim.title);
  const subLines = wrapTextToLines(sub, lim.sub);
  const panelLines = [];
  const footLines = footText ? wrapTextToLines(footText, lim.foot) : [];

  let ty = 26;
  titleLines.forEach(() => {
    ty += EXPORT_TITLE_LH;
  });
  if (titleLines.length && subLines.length) ty += 8;
  else if (titleLines.length) ty += 6;
  subLines.forEach(() => {
    ty += EXPORT_SUB_LH;
  });
  const headerH = Math.min(300, Math.max(70, ty + 18));

  const footerH = footLines.length ? 10 + footLines.length * EXPORT_FOOT_LH + 10 : 0;

  const totalH = ch + headerH + footerH;

  const root = document.createElementNS(SVG_NS, "svg");
  root.setAttribute("xmlns", SVG_NS);
  root.setAttribute("xmlns:xlink", "http://www.w3.org/1999/xlink");
  root.setAttribute("viewBox", `0 0 ${totalW} ${totalH}`);
  root.setAttribute("width", String(totalW));
  root.setAttribute("height", String(totalH));
  root.setAttribute("overflow", "hidden");

  const styleEl = document.createElementNS(SVG_NS, "style");
  styleEl.textContent = EXPORT_SVG_STYLES;
  root.appendChild(styleEl);

  const headBg = document.createElementNS(SVG_NS, "rect");
  headBg.setAttribute("x", "0");
  headBg.setAttribute("y", "0");
  headBg.setAttribute("width", String(totalW));
  headBg.setAttribute("height", String(headerH));
  headBg.setAttribute("fill", COL.paper);
  root.appendChild(headBg);

  /* Fond papier explicite sous le tracé (Word ne peint pas toujours le fond du svg) */
  const plotBg = document.createElementNS(SVG_NS, "rect");
  plotBg.setAttribute("x", "0");
  plotBg.setAttribute("y", String(headerH));
  plotBg.setAttribute("width", String(totalW));
  plotBg.setAttribute("height", String(totalH - headerH));
  plotBg.setAttribute("fill", COL.paper);
  root.appendChild(plotBg);

  ty = 26;
  titleLines.forEach((line) => {
    const t = document.createElementNS(SVG_NS, "text");
    t.setAttribute("x", String(textX));
    t.setAttribute("y", String(ty));
    t.setAttribute("fill", COL.ink);
    t.setAttribute("font-size", "17");
    t.setAttribute("font-weight", "600");
    t.setAttribute("letter-spacing", "-0.028em");
    t.textContent = line;
    root.appendChild(t);
    ty += EXPORT_TITLE_LH;
  });
  if (titleLines.length && subLines.length) ty += 8;
  else if (titleLines.length) ty += 6;
  subLines.forEach((line) => {
    const t = document.createElementNS(SVG_NS, "text");
    t.setAttribute("x", String(textX));
    t.setAttribute("y", String(ty));
    t.setAttribute("fill", COL.muted);
    t.setAttribute("font-size", "13");
    t.setAttribute("font-weight", "450");
    t.setAttribute("letter-spacing", "0.01em");
    t.textContent = line;
    root.appendChild(t);
    ty += EXPORT_SUB_LH;
  });
  panelLines.forEach((line) => {
    const t = document.createElementNS(SVG_NS, "text");
    t.setAttribute("x", String(textX));
    t.setAttribute("y", String(ty));
    t.setAttribute("fill", COL.muted);
    t.setAttribute("font-size", "10.5");
    t.setAttribute("font-weight", "600");
    t.setAttribute("letter-spacing", "0.06em");
    t.setAttribute("text-transform", "uppercase");
    t.textContent = line;
    root.appendChild(t);
    ty += 15;
  });

  const chartLayer = document.createElementNS(SVG_NS, "g");
  const host = chartSvg.closest(".chart-host");
  const layerClasses = ["export-chart-shift"];
  const svgClass = chartSvg.getAttribute("class");
  if (svgClass) layerClasses.push(svgClass);
  if (host && host.classList.contains("chart-bar-swiss")) layerClasses.push("chart-bar-swiss");
  chartLayer.setAttribute("class", layerClasses.join(" ").trim());
  chartLayer.setAttribute("transform", `translate(${padChartX},${headerH})`);
  const innerClone = chartSvg.cloneNode(true);
  /* Retirer les cercles de survol (fill="none" ou anciennement "transparent")
   * qui s'affichent en noir dans Word / Illustrator car SVG standalone
   * n'applique pas pointer-events et interprète fill vide comme #000. */
  innerClone.querySelectorAll("circle").forEach((el) => {
    const f = el.getAttribute("fill");
    if (f === "none" || f === "transparent" || f === "") {
      const r = parseFloat(el.getAttribute("r") || "0");
      if (r >= 6) el.remove();
    }
  });
  while (innerClone.firstChild) chartLayer.appendChild(innerClone.firstChild);
  root.appendChild(chartLayer);

  /* Footer : texte source/méthodo sous le graphique */
  if (footLines.length) {
    /* Fond papier de la zone footer */
    const footBg = document.createElementNS(SVG_NS, "rect");
    footBg.setAttribute("x", "0");
    footBg.setAttribute("y", String(headerH + ch));
    footBg.setAttribute("width", String(totalW));
    footBg.setAttribute("height", String(footerH));
    footBg.setAttribute("fill", COL.paper);
    root.appendChild(footBg);

    let fy = headerH + ch + 10;
    footLines.forEach((line) => {
      const ft = document.createElementNS(SVG_NS, "text");
      ft.setAttribute("x", String(textX));
      ft.setAttribute("y", String(fy));
      ft.setAttribute("fill", COL.muted);
      ft.setAttribute("font-size", "11");
      ft.setAttribute("font-weight", "450");
      ft.setAttribute("letter-spacing", "0.01em");
      ft.textContent = line;
      root.appendChild(ft);
      fy += EXPORT_FOOT_LH;
    });
  }

  return root;
}

function downloadBlob(blob, filename) {
  const a = document.createElement("a");
  a.href = URL.createObjectURL(blob);
  a.download = filename;
  a.rel = "noopener";
  document.body.appendChild(a);
  a.click();
  a.remove();
  setTimeout(() => URL.revokeObjectURL(a.href), 2500);
}

function exportFigureSvg(svgEl, filenameBase, articleEl) {
  const root = buildExportRootSvg(svgEl, articleEl);
  const xml = new XMLSerializer().serializeToString(root);
  const out = `<?xml version="1.0" encoding="UTF-8"?>\n${xml}`;
  downloadBlob(new Blob([out], { type: "image/svg+xml;charset=utf-8" }), `${filenameBase}.svg`);
}

function exportFigurePng(svgEl, filenameBase, scale, articleEl) {
  const root = buildExportRootSvg(svgEl, articleEl);
  const { w, h } = parseSvgPixelSize(root);
  const outW = Math.round(w * scale);
  const outH = Math.round(h * scale);
  /* Largeur/hauteur en pixels pilotent la résolution raster du SVG (évite un flou d’agrandissement). */
  root.setAttribute("width", String(outW));
  root.setAttribute("height", String(outH));
  const str = new XMLSerializer().serializeToString(root);
  const blob = new Blob([str], { type: "image/svg+xml;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const img = new Image();
  img.decoding = "async";
  img.onload = () => {
    try {
      const canvas = document.createElement("canvas");
      canvas.width = outW;
      canvas.height = outH;
      const ctx = canvas.getContext("2d");
      if (!ctx) return;
      ctx.imageSmoothingEnabled = true;
      ctx.imageSmoothingQuality = "high";
      ctx.fillStyle = COL.paper;
      ctx.fillRect(0, 0, canvas.width, canvas.height);
      ctx.drawImage(img, 0, 0, outW, outH);
      canvas.toBlob((pngBlob) => {
        if (pngBlob) downloadBlob(pngBlob, `${filenameBase}-${scale}x.png`);
      }, "image/png");
    } finally {
      URL.revokeObjectURL(url);
    }
  };
  img.onerror = () => URL.revokeObjectURL(url);
  img.src = url;
}

/**
 * Ajoute les boutons d'export sur chaque article.figure (après rendu D3).
 * Plusieurs SVG dans un même article : un groupe d’export par tracé (même titres / notes que l’article).
 */
function attachFigureExports() {
  const root = document.getElementById("main-figures");
  if (!root) return;
  root.querySelectorAll("article.figure").forEach((article, figIndex) => {
    if (article.querySelector(".figure-export")) return;
    const titleEl = article.querySelector(".figure-title");
    const slug = article.dataset.exportSlug || slugifyTitle(titleEl?.textContent || "figure");
    const baseTitle = `figure_${figIndex + 1}_${slug}`;
    const svgs = [...article.querySelectorAll(".chart-host svg")];
    if (!svgs.length) return;
    const miniTitles = [...article.querySelectorAll(".mini-panel-title")].map((el) =>
      slugifyTitle(el.textContent || "")
    );

    const bar = document.createElement("div");
    bar.className = "figure-export";
    bar.setAttribute("role", "group");
    bar.setAttribute("aria-label", "Exporter la figure");

    const label = document.createElement("span");
    label.className = "figure-export-kicker";
    label.textContent = "Export (Word, haute qualité)";
    bar.appendChild(label);

    svgs.forEach((svgEl, i) => {
      const suffix = svgs.length > 1 ? `-${miniTitles[i] || `partie-${i + 1}`}` : "";
      const base = `${baseTitle}${suffix}`;

      const grp = document.createElement("span");
      grp.className = "figure-export-group";

      const mkBtn = (text, titleAttr, onClick) => {
        const b = document.createElement("button");
        b.type = "button";
        b.className = "figure-export-btn";
        b.textContent = text;
        b.title = titleAttr;
        b.addEventListener("click", () => {
          try {
            b.disabled = true;
            onClick();
          } finally {
            setTimeout(() => {
              b.disabled = false;
            }, 800);
          }
        });
        return b;
      };

      grp.appendChild(
        mkBtn("SVG", "Fichier vectoriel avec titre et styles (Word)", () =>
          exportFigureSvg(svgEl, base, article)
        )
      );
      grp.appendChild(
        mkBtn("PNG 4× HD", "Image publication (largeur nominale ×4, raster net, fond LGC)", () =>
          exportFigurePng(svgEl, base, 4, article)
        )
      );
      grp.appendChild(
        mkBtn("PNG 2×", "Version plus légère (×2)", () => exportFigurePng(svgEl, base, 2, article))
      );
      bar.appendChild(grp);
    });

    const firstHost = article.querySelector(".chart-host");
    if (firstHost) firstHost.insertAdjacentElement("beforebegin", bar);
    else article.prepend(bar);
  });
}

/** Un seul SVG : solde net puis asile (export unique SVG/PNG). */
function dualBarRow(container, data, footer) {
  container.classed("figure-dual-net-asylum", true);
  container.attr("data-export-slug", "double-panneau-solde-et-asile-2024");
  figureHead(container, TITLES.dual);

  const net = data.dualNetAsylum2024?.net || [];
  const asy = data.dualNetAsylum2024?.asylum || [];
  const wrap = container.append("div").attr("class", "chart-host chart-bar-swiss");

  const w = 900;
    const rowH = 34;
  const margin = { top: 8, right: 72, bottom: 34, left: 168 };
  const inset = { left: 8, right: 8, top: 6, bottom: 8 };
    const innerW = w - margin.left - margin.right;
  const kickerH = 15;
  const gapPanels = 28;

  function panelBlockHeight(rows) {
    const innerH = Math.max(rows.length * rowH, 40);
    return kickerH + margin.top + innerH + margin.bottom;
  }

  const totalH = panelBlockHeight(net) + gapPanels + panelBlockHeight(asy);
  const svg = wrap
    .append("svg")
    .attr("viewBox", `0 0 ${w} ${totalH}`)
    .attr("width", "100%")
    .attr("height", totalH);

  function drawPanelAt(yBase, kickerLabel, rows) {
    const innerH = Math.max(rows.length * rowH, 40);
    const gBlock = svg.append("g").attr("transform", `translate(0,${yBase})`);
    gBlock
      .append("text")
      .attr("x", 28)
      .attr("y", 11)
      .attr("fill", COL.muted)
      .attr("font-size", 9.25)
      .attr("font-weight", "600")
      .attr("letter-spacing", "0.11em")
      .text(kickerLabel);
    const g = gBlock.append("g").attr("transform", `translate(${margin.left},${kickerH + margin.top})`);

    const vals = rows.map((r) => r.value).filter((v) => Number.isFinite(v));
    const useSigned = vals.some((v) => v < 0);
    const maxV = vals.length ? d3.max(vals) : 0;
    const x = d3.scaleLinear().range([inset.left, innerW - inset.right]);
    if (useSigned) {
      x.domain(xDomainSignedBars(vals));
    } else {
      const hi = Math.max((Number.isFinite(maxV) ? maxV : 0) * 1.22, 0.35);
      x.domain([0, hi]).nice();
    }
    const y = d3
      .scaleBand()
      .domain(rows.map((r) => r.label))
      .range([inset.top, innerH - inset.bottom])
      .paddingInner(0.35)
      .paddingOuter(0.1);
    const x0 = x(0);

    appendHorizontalBarGrid(g, x, inset, innerH, 5);
    appendBarTickLabelsX(g, x, innerH, 5, 8.25);
    appendBarCategoryLabelsY(g, y, 8.75, (lab) => {
      const r = rows.find((x) => x.label === lab);
      return r?.code === "FR" ? COL.red : COL.ink;
    });

    rows.forEach((r) => {
      const yy = y(r.label);
      const lay = layoutSignedHBar(r.value, x, x0);
      const isFr = r.code === "FR";
      g.append("rect")
        .attr("class", "bar-fill")
        .attr("x", lay.rectX)
        .attr("y", yy)
        .attr("width", lay.rectW)
        .attr("height", y.bandwidth())
        .attr("fill", isFr ? COL.red : COL.barMuted)
        .attr("rx", 2)
        .attr("ry", 2);
      g.append("text")
        .attr("x", lay.labelX)
        .attr("y", yy + y.bandwidth() / 2)
        .attr("dy", "0.35em")
        .attr("text-anchor", lay.anchor)
        .attr("fill", COL.ink)
        .attr("font-weight", "600")
        .attr("font-size", 8.75)
        .text(r.value.toFixed(2));
    });

    g.append("text")
      .attr("x", innerW / 2)
      .attr("y", innerH + 24)
      .attr("text-anchor", "middle")
      .attr("fill", COL.muted)
      .attr("font-size", 8.5)
      .attr("font-weight", "500")
      .text("Pour 1 000 habitants");

    return kickerH + margin.top + innerH + margin.bottom;
  }

  let y = 0;
  y += drawPanelAt(y, "SOLDE NET - CNMIGRATRT", net);
  y += gapPanels;
  drawPanelAt(y, "PREMIÈRES DEMANDES D’ASILE", asy);

  if (footer) container.append("p").attr("class", "figure-foot").text(footer);
}

function figureHead(art, spec) {
  art.append("h2").attr("class", "figure-title").text(spec.title);
  if (spec.sub) art.append("p").attr("class", "figure-sub").text(spec.sub);
}

function render(data) {
  const main = d3.select("#main-figures");
  const tipEl = document.getElementById("tooltip");
  const tooltip = makeTooltip(tipEl);

  const rows = data.migrationSelection;


  /* 1a-c Duos France / Danemark, Italie, Royaume-Uni */
  for (const d of DYADS) {
    const art = main.append("article").attr("class", "figure");
    dyadLineFigure(art, data, tooltip, d);
  }


  /* GRAPHIQUES STATISTIQUES NATIONALES (INSEE / Statistics DK / Istat / ONS) */
  const NS = data.nationalStats || {};

  /* N1 - Danemark (étrangers, Stat DK) vs France (immigrés, INSEE) */
  {
    const dkRows = (NS.dkEtrangers || []).map(r => ({ year: r.year, DK: r.value }));
    const frRows = (NS.frImmigres || []).map(r => ({ year: r.year, FR: r.value, estimated: r.estimated }));
    const merged = {};
    for (const r of dkRows) { merged[r.year] = { year: r.year, DK: r.DK }; }
    for (const r of frRows) { if (!merged[r.year]) merged[r.year] = { year: r.year }; merged[r.year].FR = r.FR; merged[r.year].estimated = r.estimated; }
    const mRows = Object.values(merged).sort((a, b) => a.year - b.year);
    if (mRows.length) {
      const art = main.append("article").attr("class", "figure").attr("data-export-slug", "danemark-france-instituts-nationaux");
      figureHead(art, {
        title:
          "Solde migratoire selon les instituts nationaux : le Danemark reste au-dessus de la France depuis 2015",
        sub:
          "Danemark : étrangers (Statistics DK). France : immigrés (INSEE Première n°2050). Pour 1 000 habitants, 2013-2024. Indicateurs non strictement équivalents.",
      });
      const host = art.append("div").attr("class", "chart-host");
      const frPts = mRows.filter(r => r.FR != null).map(r => ({ year: r.year, value: r.FR }));
      const dkPts = mRows.filter(r => r.DK != null).map(r => ({ year: r.year, value: r.DK }));
      const yDom = extentValues([frPts, dkPts]);
      lineChartFigure(host, {
        rows: mRows,
        seriesDefs: [
          { key: "FR", label: "France (immigrés, INSEE)", color: SERIE_PAYS.FR, width: 2.6 },
          { key: "DK", label: "Danemark (étrangers, Stat DK)", color: SERIE_PAYS.DK, width: 2.1 },
        ],
        annotations: [
          { year: 2015, text: "Pic de l'asile", target: "DK" },
          { year: 2019, text: "Frederiksen PM", target: "DK" },
          { year: 2022, text: "Ukraine", target: "DK" },
        ],
        tooltip,
        yDomain: yDom,
        xDomain: [2013, 2024],
        height: 430,
        margin: { top: 20, right: 240, bottom: 52, left: 64 },
      });
      art.append("p").attr("class", "figure-foot").text(
        "Sources : Statistics Denmark (solde migratoire des étrangers, citizenship-based) ; INSEE (solde migratoire des immigrés, France métropolitaine). 2022-2023 France = estimation (entrées réelles INSEE EAR 2024 : 375k en 2022, 347k en 2023 ; sorties estimées à 94 000/an, moyenne 2012-2021). Source : INSEE Première n°2050, mai 2025. Indicateurs non strictement équivalents : l'indicateur danois est un minorant par rapport au français."
      );
    }
  }

  /* N2 - Italie (étrangers, Istat) vs France (immigrés, INSEE) */
  {
    const itRows = (NS.itEtrangers || []).map(r => ({ year: r.year, IT: r.value }));
    const frRows = (NS.frImmigres || []).map(r => ({ year: r.year, FR: r.value }));
    const merged = {};
    for (const r of itRows) { merged[r.year] = { year: r.year, IT: r.IT }; }
    for (const r of frRows) { if (!merged[r.year]) merged[r.year] = { year: r.year }; merged[r.year].FR = r.FR; }
    const mRows = Object.values(merged).sort((a, b) => a.year - b.year);
    if (mRows.length) {
      const art = main.append("article").attr("class", "figure").attr("data-export-slug", "italie-france-instituts-nationaux");
      figureHead(art, {
        title:
          "Mesurées par leurs propres instituts, l’Italie et la France suivent des trajectoires comparables mais distinctes",
        sub:
          "Italie : étrangers (Istat). France : immigrés (INSEE). Pour 1 000 habitants, 2014-2023. Indicateurs non strictement équivalents.",
      });
      const host = art.append("div").attr("class", "chart-host");
      const frPts = mRows.filter(r => r.FR != null).map(r => ({ year: r.year, value: r.FR }));
      const itPts = mRows.filter(r => r.IT != null).map(r => ({ year: r.year, value: r.IT }));
      const yDom = extentValues([frPts, itPts]);
      lineChartFigure(host, {
        rows: mRows,
        seriesDefs: [
          { key: "FR", label: "France (immigrés, INSEE)", color: SERIE_PAYS.FR, width: 2.6 },
          { key: "IT", label: "Italie (étrangers, Istat)", color: SERIE_PAYS.IT, width: 2.1 },
        ],
        annotations: [
          { year: 2018, text: "Salvini ministre", target: "IT" },
          { year: 2022, text: "G. Meloni PM", target: "IT" },
        ],
        tooltip,
        yDomain: yDom,
        xDomain: [2014, 2023],
        height: 430,
        margin: { top: 20, right: 240, bottom: 52, left: 64 },
      });
      art.append("p").attr("class", "figure-foot").text(
        "Sources : Istat (solde migratoire des étrangers, Italie) ; INSEE (solde migratoire des immigrés, France). 2022-2023 France = estimation (entrées réelles INSEE, sorties ~94 000/an). Source : INSEE Première n°2050, mai 2025. Même biais méthodologique que pour le Danemark : l'indicateur Istat est citizenship-based, l'indicateur INSEE est birthplace-based."
      );
    }
  }

  /* N2b - Italie : écart Eurostat (total) vs Istat (étrangers seulement) - explication 2020 */
  {
    const itNat = (NS.itEtrangers || []);
    const itEur = (NS.itEurostatNet || []);
    if (itNat.length && itEur.length) {
      const art = main.append("article").attr("class", "figure").attr("data-export-slug", "italie-ecart-eurostat-istat");
      figureHead(art, {
        title: "Eurostat (solde total) et Istat (étrangers seuls) : l’écart s’explique surtout par les nationaux Italiens en 2020",
        sub:
          "Solde migratoire pour 1 000 habitants. Eurostat : nationaux inclus. Istat : étrangers uniquement. L’écart s’explique par les Italiens restés à l’étranger pendant le Covid.",
      });
      const host = art.append("div").attr("class", "chart-host");

      /* Fusion des deux séries sur les années communes */
      const allYears = Array.from(new Set([...itNat.map(r => r.year), ...itEur.map(r => r.year)])).sort();
      const natByYear = Object.fromEntries(itNat.map(r => [r.year, r.value]));
      const eurByYear = Object.fromEntries(itEur.map(r => [r.year, r.value]));
      const rows = allYears.map(yr => ({ year: yr, ISTAT: natByYear[yr] ?? null, EUROSTAT: eurByYear[yr] ?? null }));

      const natPts = rows.filter(r => r.ISTAT != null).map(r => ({ year: r.year, value: r.ISTAT }));
      const eurPts = rows.filter(r => r.EUROSTAT != null).map(r => ({ year: r.year, value: r.EUROSTAT }));

      lineChartFigure(host, {
        rows,
        seriesDefs: [
          { key: "ISTAT",    label: "Istat - étrangers uniquement",  color: COL.plum, width: 2.6 },
          { key: "EUROSTAT", label: "Eurostat - solde total (nationaux inclus)", color: COL.muted, width: 1.8, dash: "5 3" },
        ],
        annotations: [
          { year: 2020, text: "Italiens restés à l'étranger (Covid)", target: "EUROSTAT" },
        ],
        tooltip,
        yDomain: [d3.min([...natPts, ...eurPts].map(p => p.value)) - 0.5,
                  d3.max([...natPts, ...eurPts].map(p => p.value)) + 0.5],
        xDomain: [2014, 2023],
        height: 400,
        margin: { top: 20, right: 260, bottom: 52, left: 64 },
      });
      art.append("p").attr("class", "figure-foot").text(
        "Sources : Istat (solde migratoire des étrangers, Italie) ; Eurostat CNMIGRATRT (solde migratoire total, nationaux inclus). En 2020, l'écart atteint 3,8 ‰ : Eurostat affiche -1,2 ‰ tandis qu'Istat enregistre +2,6 ‰ pour les seuls étrangers. La différence (3,8 ‰) correspond à la migration nette des Italiens eux-mêmes, qui ont massivement choisi de rester à l'étranger durant la pandémie plutôt que de rentrer, faisant chuter le solde total en territoire négatif."
      );
    }
  }

  /* N3 - Royaume-Uni (étrangers, ONS) vs France (immigrés, INSEE) */
  {
    const ukRows = (NS.ukEtrangers || []).map(r => ({ year: r.year, UK: r.value }));
    const frRows = (NS.frImmigres || []).map(r => ({ year: r.year, FR: r.value }));
    const merged = {};
    for (const r of ukRows) { merged[r.year] = { year: r.year, UK: r.UK }; }
    for (const r of frRows) { if (!merged[r.year]) merged[r.year] = { year: r.year }; merged[r.year].FR = r.FR; }
    const mRows = Object.values(merged).sort((a, b) => a.year - b.year);
    if (mRows.length) {
      const art = main.append("article").attr("class", "figure").attr("data-export-slug", "royaume-uni-france-instituts-nationaux");
      figureHead(art, {
        title:
          "Le solde migratoire britannique a été multiplié par cinq entre 2019 et 2022, celui de la France est resté stable",
        sub:
          "R.-U. : étrangers (ONS). France : immigrés (INSEE). Pour 1 000 habitants, 2014-2023. Indicateurs non strictement comparables.",
      });
      const host = art.append("div").attr("class", "chart-host");
      const frPts = mRows.filter(r => r.FR != null).map(r => ({ year: r.year, value: r.FR }));
      const ukPts = mRows.filter(r => r.UK != null).map(r => ({ year: r.year, value: r.UK }));
      const yDom = extentValues([frPts, ukPts]);
      lineChartFigure(host, {
        rows: mRows,
        seriesDefs: [
          { key: "FR", label: "France (immigrés, INSEE)", color: SERIE_PAYS.FR, width: 2.6 },
          { key: "UK", label: "Royaume-Uni (étrangers, ONS)", color: SERIE_PAYS.UK, width: 2.1 },
        ],
        annotations: [
          { year: 2016, text: "Brexit", target: "UK" },
          { year: 2021, text: "Fin libre circ.", target: "UK" },
          { year: 2022, text: "Ukraine", target: "UK" },
        ],
        tooltip,
        yDomain: yDom,
        xDomain: [2014, 2023],
        height: 430,
        margin: { top: 20, right: 240, bottom: 52, left: 64 },
      });
      art.append("p").attr("class", "figure-foot").text(
        "Sources : ONS Long-Term International Migration (LTIM), Royaume-Uni ; INSEE (immigrés, France métropolitaine). Les deux indicateurs ne sont pas strictement comparables (citizenship-based vs birthplace-based)."
      );
    }
  }

  /* N4 - UK par origine : UE vs non-UE, l'argument Brexit */
  {
    const ukOrigin = NS.ukByOrigin || [];
    if (ukOrigin.length) {
      const art = main.append("article").attr("class", "figure").attr("data-export-slug", "brexit-arrivees-nettes-ue-non-ue");
      figureHead(art, {
        title:
          "Depuis le Brexit, le solde UE est devenu négatif au Royaume-Uni tandis que les arrivées non-UE ont triplé",
        sub: "Arrivées nettes en milliers, par nationalité UE et non-UE. ONS (LTIM). Données provisoires pour 2024-2025.",
      });
      const wrap = art.append("div").attr("class", "chart-host chart-bar-swiss");

      const w = 900;
      /* Droite : marge pour libellés hors barre (barres courtes) ; gauche : années */
      const margin = { top: 16, right: 36, bottom: 60, left: 76 };
      const innerW = w - margin.left - margin.right;
      const rowH = 32;
      const years = ukOrigin.map(r => r.year);
      const innerH = years.length * rowH;
      const height = innerH + margin.top + margin.bottom;

      const svg = wrap.append("svg")
        .attr("viewBox", `0 0 ${w} ${height}`)
        .attr("width", "100%")
        .attr("height", height);

      /* Clip-path : les barres ne débordent pas du cadre */
      const clipIdUk = "clip-uk-origin";
      svg.append("defs").append("clipPath").attr("id", clipIdUk)
        .append("rect").attr("x", 0).attr("y", 0).attr("width", innerW).attr("height", innerH);

      const g = svg.append("g").attr("transform", `translate(${margin.left},${margin.top})`);
      const barsG = g.append("g").attr("clip-path", `url(#${clipIdUk})`);

      const allVals = ukOrigin.flatMap(r => [r.eu, r.nonEu]);
      const xMax = d3.max(allVals.filter((v) => v > 0));
      const xMinNeg = d3.min(allVals.filter((v) => v < 0));
      /*
       * Large marge négative sur l'axe : la ligne zéro est bien à droite, loin des libellés d'années.
       * Les valeurs UE négatives sont petites (-40 à 0) : sans ça, l'échelle serait trop serrée à gauche.
       */
      const domainHi = xMax * 1.02;
      const domainLo = Number.isFinite(xMinNeg)
        ? Math.min(xMinNeg - 45, -240)
        : 0;
      const x = d3.scaleLinear().domain([domainLo, domainHi]).range([0, innerW]);
      const y = d3.scaleBand().domain(years.map(String)).range([0, innerH]).paddingInner(0.25).paddingOuter(0.06);
      const x0 = x(0);

      x.ticks(6).forEach((t) => {
        g.append("line")
          .attr("x1", x(t))
          .attr("x2", x(t))
          .attr("y1", 0)
          .attr("y2", innerH)
          .attr("stroke", COL.grid)
          .attr("stroke-width", 0.5);
        g.append("text")
          .attr("x", x(t))
          .attr("y", innerH + 16)
          .attr("text-anchor", "middle")
          .attr("fill", COL.muted)
          .attr("font-size", 8.5)
          .text(t);
      });
      g.append("text").attr("x", innerW / 2).attr("y", innerH + 36).attr("text-anchor", "middle")
        .attr("fill", COL.muted).attr("font-size", 9).attr("font-weight", "500").text("Milliers de personnes (net)");

      /* Ligne zéro */
      g.append("line").attr("x1", x0).attr("x2", x0).attr("y1", 0).attr("y2", innerH)
        .attr("stroke", COL.ink).attr("stroke-width", 0.8).attr("opacity", 0.35);

      /* Barres et étiquettes */
      ukOrigin.forEach(r => {
        const ys = y(String(r.year));
        const bh = y.bandwidth();
        const half = bh / 2;

        /* Non-UE */
        const xNeu = Math.min(x0, x(r.nonEu));
        const wNeu = Math.abs(x(r.nonEu) - x0);
        barsG.append("rect").attr("x", xNeu).attr("y", ys).attr("width", wNeu).attr("height", half - 1)
          .attr("fill", COL.plum).attr("rx", 2);

        /* UE */
        const xEu = r.eu >= 0 ? x0 : x(r.eu);
        const wEu = Math.abs(x(r.eu) - x0);
        barsG.append("rect").attr("x", xEu).attr("y", ys + half + 1).attr("width", wEu).attr("height", half - 1)
          .attr("fill", COL.teal).attr("rx", 2);

        /* Libellés : centré blanc dans la barre si ≥ 45 px, sinon à droite (positif) ou à gauche (négatif) en encre foncée */
        const yNeuCenter = ys + (half - 1) / 2;
        const yUeCenter  = ys + half + 1 + (half - 2) / 2;
        const MIN_INSIDE = 45;
        const FS = 8;

        function barLabel(grp, xPx, yPx, w, isNeg, txt, segmentFill) {
          const inside = w >= MIN_INSIDE;
          const xPos = inside
            ? xPx + w / 2
            : isNeg ? xPx - 5 : xPx + w + 5;
          grp.append("text")
            .attr("x", xPos)
            .attr("y", yPx)
            .attr("dy", "0.35em")
            .attr("text-anchor", inside ? "middle" : isNeg ? "end" : "start")
            .attr("fill", inside ? fillForBarInterior(segmentFill) : COL.ink)
            .attr("font-size", FS)
            .attr("font-weight", "700")
            .attr("font-variant-numeric", "tabular-nums")
            .text(txt);
        }

        barLabel(g, xNeu, yNeuCenter, wNeu, false, `${r.nonEu > 0 ? "+" : ""}${r.nonEu}k`, COL.plum);
        barLabel(g, xEu,  yUeCenter,  wEu,  r.eu < 0, `${r.eu > 0 ? "+" : ""}${r.eu}k`, COL.teal);

        /* Année : bien à gauche du tracé */
        g.append("text").attr("x", -8).attr("y", ys + bh / 2).attr("dy", "0.35em")
          .attr("text-anchor", "end").attr("fill", COL.ink)
          .attr("font-size", 8.5).attr("font-weight", "450").text(r.year);
      });

      /* Légende */
      const legY = margin.top + innerH + 46;
      const legItems = [
        [COL.plum, "Non-UE"],
        [COL.teal, "UE"],
      ];
      legItems.forEach(([col, lbl], i) => {
        svg.append("rect").attr("x", margin.left + i * 120).attr("y", legY).attr("width", 10).attr("height", 10).attr("fill", col).attr("rx", 1);
        svg.append("text").attr("x", margin.left + i * 120 + 15).attr("y", legY + 8).attr("fill", COL.ink).attr("font-size", 8.5).text(lbl);
      });

      art.append("p").attr("class", "figure-foot").text(
        "Source : ONS Long-Term International Migration (LTIM). Données provisoires pour 2024-2025. Le solde UE devient négatif à partir de 2021 : les ressortissants européens repartent plus qu'ils n'arrivent. Le Brexit visait à réduire l'immigration ; il en a seulement changé la composition, en remplaçant une immigration européenne par une immigration non-européenne bien plus volumineuse."
      );
    }
  }


  /* 9 Entrées de nationalité étrangère (Eurostat) */
  {
    const fe = data.foreignEntries || [];
    if (fe.length) {
      const art = main.append("article").attr("class", "figure").attr("data-export-slug", "entrees-etrangers-quatre-pays");
      const host = art.append("div").attr("class", "chart-host");
      const frPts = pointsFromRows(fe, "FR");
      const dkPts = pointsFromRows(fe, "DK");
      const itPts = pointsFromRows(fe, "IT");
      const ukPtsE = pointsFromRows(fe, "UK");
      const yDom = extentValuesFrom([frPts, dkPts, itPts, ukPtsE], 0.08, 0.35);
      lineChartFigure(host, {
        rows: fe,
        seriesDefs: [
          { key: "FR", label: "France", color: SERIE_PAYS.FR, width: 2.75 },
          { key: "DK", label: "Danemark", color: SERIE_PAYS.DK, width: 2.2 },
          { key: "IT", label: "Italie", color: SERIE_PAYS.IT, width: 2.2 },
          { key: "UK", label: "Royaume-Uni", color: SERIE_PAYS.UK, width: 2.2, dash: "4 2" },
        ],
        annotations: [
          { year: 2021, text: "Fin libre circ. RU", target: "UK" },
        ],
        tooltip,
        yLabel: "Entrées pour 1 000 habitants",
        yDomain: yDom,
        xDomain: [2016, 2024],
        height: 420,
        margin: { top: 20, right: 210, bottom: 52, left: 64 },
      });
      art.append("p").attr("class", "figure-foot").text(
        "Sources : Eurostat migr_imm1ctz (FR, DK, IT, UK 2016-2019) ; ONS Long-Term International Migration (UK 2020-2024, estimation cohérente). Rupture méthodologique UK en 2020 : données Eurostat indisponibles après Brexit, données ONS utilisées. Lecture : le Royaume-Uni, en pointillés, connaît une explosion post-Brexit que les autres pays n'ont pas."
      );
    }
  }


  /* 6 Rang France */
  {
    const rankRows = (data.analyseRangFrance || [])
      .filter((r) => r.rangFrance != null)
      .map((r) => ({ year: r.annee, rang: r.rangFrance }));
    if (rankRows.length) {
      const art = main.append("article").attr("class", "figure").attr("data-export-slug", "classement-france-dans-lue-sur-le-temps");
      const rA = rankRows[0];
      const rZ = rankRows[rankRows.length - 1];
      const title6 = `Classement au sein de l’UE : la France est passée du ${rA.rang}e au ${rZ.rang}e rang (${rA.year}-${rZ.year})`;
      figureHead(art, { title: title6, sub: TITLES[6].sub });
      const host = art.append("div").attr("class", "chart-host");
      lineChartFigure(host, {
        rows: rankRows,
        seriesDefs: [{ key: "rang", label: "Rang France", color: COL.red, width: 2.75 }],
        annotations: [
          { year: rA.year, text: `${rA.rang}e`, target: "rang", calloutStyle: "pointValue", color: COL.red },
          { year: rZ.year, text: `${rZ.rang}e`, target: "rang", calloutStyle: "pointValue", color: COL.red },
        ],
        tooltip,
        yLabel: "Place au classement (1er = solde net le plus élevé)",
        yDomain: [27, 1],
        height: 400,
      });
      const rf = data.copy?.analyseRangFooter;
      if (rf) art.append("p").attr("class", "figure-foot").text(rf);
    }
  }


  /* 4 Classement UE */
  {
    const eu = data.euRanking2024 || [];
    if (!eu.length) {
      /* Données absentes du JSON : ne pas rendre la figure. */
    } else {
      const art = main.append("article").attr("class", "figure").attr("data-export-slug", "solde-net-classement-ue27-en-2024");
      const frIdx = eu.findIndex((d) => d.code === "FR");
      const nEu = eu.length;
      const frRank = frIdx >= 0 && nEu > 0 ? nEu - frIdx : null;
      const title4 =
        frRank != null
          ? `Solde migratoire en 2024 : la France se classe ${frRank}e sur ${nEu} dans l'Union européenne`
          : TITLES[4].title;
      figureHead(art, { title: title4, sub: TITLES[4].sub });
      const wrap = art.append("div").attr("class", "chart-host chart-bar-swiss");
      const w = 900;
      const rowH = 26;
      const margin = { top: 16, right: 52, bottom: 44, left: 200 };
      const innerW = w - margin.left - margin.right;
      const innerH = Math.max(eu.length * rowH, 200);
      const height = innerH + margin.top + margin.bottom;

      const svg = wrap.append("svg").attr("viewBox", `0 0 ${w} ${height}`).attr("width", "100%").attr("height", height);
      const g = svg.append("g").attr("transform", `translate(${margin.left},${margin.top})`);

      const inset = { left: 10, right: 10, top: 8, bottom: 10 };
      const euVals = eu.map((d) => d.value);
      const xDom = xDomainSignedBars(euVals);
      const x = d3.scaleLinear().domain(xDom).range([inset.left, innerW - inset.right]);
      const y = d3
        .scaleBand()
        .domain(eu.map((d) => d.label))
        .range([inset.top, innerH - inset.bottom])
        .paddingInner(0.28)
        .paddingOuter(0.08);

      const x0 = x(0);

      appendHorizontalBarGrid(g, x, inset, innerH, 7);
      appendBarTickLabelsX(g, x, innerH, 7);

      g.append("text")
        .attr("x", innerW / 2)
        .attr("y", innerH + 34)
        .attr("text-anchor", "middle")
        .attr("fill", COL.muted)
        .attr("font-size", 8.75)
        .attr("font-weight", "500")
        .text("Solde net pour 1 000 habitants (2024)");

      appendBarCategoryLabelsY(g, y, 9.25, (lab) => {
        const row = eu.find((e) => e.label === lab);
        return row?.code === "FR" ? COL.red : COL.ink;
      });

      eu.forEach((d) => {
        const yy = y(d.label);
        const lay = layoutSignedHBar(d.value, x, x0);
        const isFr = d.code === "FR";
        g.append("rect")
          .attr("class", "bar-fill")
          .attr("x", lay.rectX)
          .attr("y", yy)
          .attr("width", lay.rectW)
          .attr("height", y.bandwidth())
          .attr("fill", isFr ? COL.red : COL.barMuted)
          .attr("rx", 2)
          .attr("ry", 2);
        g.append("text")
          .attr("x", lay.labelX)
          .attr("y", yy + y.bandwidth() / 2)
          .attr("dy", "0.35em")
          .attr("text-anchor", lay.anchor)
          .attr("fill", COL.ink)
          .attr("font-weight", "600")
          .attr("font-size", 9.25)
          .text(d.value.toFixed(2));
      });
      const ef = data.copy?.euFooter;
      if (ef) art.append("p").attr("class", "figure-foot").text(ef);
    }
  }


  /* Volatilité */
  {
    const vol = data.volatilitySoldeCore || [];
    if (vol.length) {
      const art = main.append("article").attr("class", "figure").attr("data-export-slug", "volatilite-solde-quatre-pays");
      /* Volatilité : une couleur par pays, alignée sur SERIE_PAYS. */
      const barColor = (d) => {
        if (d.code === "FR") return SERIE_PAYS.FR;
        if (d.code === "DK") return SERIE_PAYS.DK;
        if (d.code === "IT") return SERIE_PAYS.IT;
        if (d.code === "UK") return SERIE_PAYS.UK;
        return COL.peerGray;
      };
      /* Libellés Y = même couleur que les barres. */
      const volRows = vol.map((d) => ({
        code: d.code,
        label: d.label,
        yLabel: d.label,
        value: d.stdev,
      }));
      barHFigure(art, {
        rows: volRows,
        title: TITLES.volatility.title,
        sub: TITLES.volatility.sub,
        xLabel: "Écart-type (pour 1 000 hab.)",
        valueFormat: (v) => v.toFixed(3),
        barColor,
        labelColor: COL.ink,
        rowH: 42,
        categoryLabelFill(lab) {
          const row = volRows.find((d) => (d.yLabel || d.label) === lab);
          return row ? barColor(row) : COL.ink;
        },
      });
      const foot = (data.copy && data.copy.volatilityFooter) || "";
      if (foot) art.append("p").attr("class", "figure-foot").text(foot);
    }
  }


  /* 1 Vue d’ensemble quatre pays */
  {
    const art = main.append("article").attr("class", "figure").attr("data-export-slug", "solde-net-quatre-pays-vue-densemble");
    figureHead(art, TITLES[1]);
    const host = art.append("div").attr("class", "chart-host");
    const corePts = ["FR", "DK", "IT", "UK"].map((k) => pointsFromRows(rows, k));
    const yDom = extentValues(corePts);
    lineChartFigure(host, {
      rows,
      seriesDefs: [
        { key: "FR", label: "France", color: SERIE_PAYS.FR, width: 2.85 },
        { key: "DK", label: "Danemark", color: SERIE_PAYS.DK, width: 2.15 },
        { key: "IT", label: "Italie", color: SERIE_PAYS.IT, width: 2.15 },
        { key: "UK", label: "Royaume-Uni", color: SERIE_PAYS.UK, width: 2.15 },
      ],
      annotations: overviewAnnotations(data, rows),
      tooltip,
      yDomain: yDom,
      xDomain: [2005, 2024],
      height: 460,
      margin: { top: 20, right: 248, bottom: 52, left: 64 },
      labelGap: 18,
    });
    const of = data.copy?.overviewFooter;
    if (of) art.append("p").attr("class", "figure-foot").text(of);
  }


  /* 2 Voisins */
  {
    const art = main.append("article").attr("class", "figure");
    neighborsLineFigure(art, data, tooltip);
  }


  /* 3 Asile */
  {
    const art = main.append("article").attr("class", "figure").attr("data-export-slug", "demandes-asile-series-multipays");
    const asyRows = data.asylum || [];
    const lastFrAsy = [...asyRows].reverse().find((r) => r.FR != null && Number.isFinite(r.FR));
    const frAsyVal = lastFrAsy ? lastFrAsy.FR : null;
    const frAsyStr =
      frAsyVal != null
        ? frAsyVal.toLocaleString("fr-FR", { minimumFractionDigits: 1, maximumFractionDigits: 1 })
        : null;
    const title3 =
      frAsyStr != null
        ? `Demandes d’asile : avec ${frAsyStr} demande pour 1 000 habitants, la France se situe dans la moyenne basse`
        : TITLES[3].title;
    figureHead(art, { title: title3, sub: TITLES[3].sub });
    const host = art.append("div").attr("class", "chart-host");
    const codes = data.asylumLineCodes || ["FR", "DE", "IT", "SE", "DK"];
    let peerIdx = 0;
    const defs = codes.map((code) => {
      const isFr = code === "FR";
      const fixed = !isFr && Object.prototype.hasOwnProperty.call(SERIE_PAYS, code) ? SERIE_PAYS[code] : null;
      const col = isFr ? SERIE_PAYS.FR : fixed ?? PEER_COLORS[peerIdx++ % PEER_COLORS.length];
      return {
        key: code,
        label: isFr ? "France" : DISPLAY_MULTI[code] || code,
        color: col,
        width: isFr ? 3 : 2.05,
      };
    });
    const allAsyPts = codes.flatMap((c) => pointsFromRows(asyRows, c));
    let hi = d3.max(allAsyPts, (d) => d.value);
    if (hi == null || !Number.isFinite(hi)) hi = 16;
    const yHi = Math.ceil(hi * 1.08 * 10) / 10;
    lineChartFigure(host, {
      rows: asyRows,
      seriesDefs: defs,
      tooltip,
      yLabel: "Premières demandes pour 1 000 habitants",
      height: 472,
      margin: { top: 20, right: 210, bottom: 56, left: 64 },
      yDomain: [0, Math.max(yHi, hi + 0.5)],
      xDomain: [2008, 2024],
      labelGap: 14,
    });
    const asf = data.copy?.asylumFooter;
    if (asf) art.append("p").attr("class", "figure-foot").text(asf);
  }


  /* 3b Premières demandes d’asile (barres, dernière année) */
  {
    const bars = data.asylumBars2024 || [];
    if (bars.length) {
      const art = main.append("article").attr("class", "figure").attr("data-export-slug", "demandes-asile-barres-2024");
      figureHead(art, TITLES.asylumBars);
      barHFigure(art, {
        rows: bars.map((d) => ({
          code: d.code,
          label: d.label,
          yLabel: d.label,
          value: d.value,
        })),
        xLabel: "Premières demandes pour 1 000 habitants",
        valueFormat: (v) => v.toFixed(2),
        barColor: (d) => (d.code === "FR" ? COL.red : COL.barMuted),
        labelColor: COL.ink,
        rowH: 36,
      });
      const af = data.copy?.asylumBarsFooter;
      if (af) art.append("p").attr("class", "figure-foot").text(af);
    }
  }


  /* 8 Panneau double solde / asile */
  {
    const art = main.append("article").attr("class", "figure");
    dualBarRow(art, data, data.copy?.dualFooter);
  }


  /* 7 Ratio asile / solde */
  {
    const ratioList = data.analyseRatioAsileSolde || [];
    const byYear = new Map();
    for (const r of ratioList) {
      if (!["FR", "DE", "IT", "ES"].includes(r.code) || r.ratio == null || !Number.isFinite(r.ratio)) continue;
      if (!byYear.has(r.annee)) byYear.set(r.annee, { year: r.annee });
      byYear.get(r.annee)[r.code] = r.ratio;
    }
    const ratioRows = [...byYear.values()].sort((a, b) => a.year - b.year);
    if (ratioRows.length) {
      const art = main.append("article").attr("class", "figure").attr("data-export-slug", "ratio-asile-sur-solde-migratoire");
      figureHead(art, TITLES[7]);
      const host = art.append("div").attr("class", "chart-host");
      lineChartFigure(host, {
        rows: ratioRows,
        seriesDefs: [
          { key: "FR", label: "France", color: SERIE_PAYS.FR, width: 2.55 },
          { key: "DE", label: "Allemagne", color: COL.peerGray, width: 2.05 },
          { key: "IT", label: "Italie", color: SERIE_PAYS.IT, width: 2.05 },
          { key: "ES", label: "Espagne", color: COL.teal, width: 2.05 },
        ],
        tooltip,
        yLabel: "Demandes d’asile ÷ solde migratoire net",
        height: 420,
      });
      const rtf = data.copy?.analyseRatioFooter;
      if (rtf) art.append("p").attr("class", "figure-foot").text(rtf);
    }
  }


  /* 5 Quadri */
  {
    const art = main.append("article").attr("class", "figure").attr("data-export-slug", "quatre-grandes-economies-ue");
    figureHead(art, TITLES[5]);
    const host = art.append("div").attr("class", "chart-host");
    lineChartFigure(host, {
      rows: data.migrationMulti || [],
      seriesDefs: [
        { key: "FR", label: "France", color: SERIE_PAYS.FR, width: 2.85 },
        { key: "DE", label: "Allemagne", color: COL.peerGray, width: 2.05 },
        { key: "IT", label: "Italie", color: SERIE_PAYS.IT, width: 2.05 },
        { key: "ES", label: "Espagne", color: COL.coral, width: 2.05 },
      ],
      tooltip,
      height: 438,
    });
    const qf = data.copy?.analyseQuadriFooter;
    if (qf) art.append("p").attr("class", "figure-foot").text(qf);
  }


  /* Angle 1 : Tendance longue 2005-2024 avec mandats présidentiels */
  {
    const rows = data.migrationSelection || [];
    if (rows.length) {
      const art = main.append("article").attr("class", "figure").attr("data-export-slug", "mandats-presidentiels-france-danemark");
      figureHead(art, {
        title:
          "Vingt ans de solde migratoire : la France reste systématiquement sous le Danemark, quel que soit le président français",
        sub:
          "Solde migratoire net pour 1 000 habitants, 2005-2024. Les bandes indiquent les mandats présidentiels français. Eurostat (CNMIGRATRT).",
      });
      const host = art.append("div").attr("class", "chart-host");
      const w = 900;
      const margin = { top: 28, right: 220, bottom: 52, left: 64 };
      const innerW = w - margin.left - margin.right;
      const h = 420;
      const innerH = h - margin.top - margin.bottom;

      const svg = host.append("svg").attr("viewBox", `0 0 ${w} ${h}`).attr("width", "100%").attr("height", h);
      const g = svg.append("g").attr("transform", `translate(${margin.left},${margin.top})`);

      const keys = ["FR", "DK"];
      const pts = keys.map((k) => pointsFromRows(rows, k));
      const allY = pts.flat().map((p) => p.value);
      const yLo = d3.min(allY) - 0.5;
      const yHi = d3.max(allY) + 0.5;
      const xDomM = padLinearXDomain([2005, 2024]);
      const x = d3.scaleLinear().domain(xDomM).range([0, innerW]);
      const y = d3.scaleLinear().domain([yLo, yHi]).range([innerH, 0]);

      /* Bandes mandats présidentiels / PM français */
      const mandatsFR = [
        { lo: 2005, hi: 2007, label: "Chirac",   color: "#e5ddd4" },
        { lo: 2007, hi: 2012, label: "Sarkozy",  color: "#efe8e0" },
        { lo: 2012, hi: 2017, label: "Hollande", color: "#e5ddd4" },
        { lo: 2017, hi: 2024, label: "Macron",   color: "#efe8e0" },
      ];
      mandatsFR.forEach(({ lo, hi, label, color }) => {
        const x1 = x(lo);
        const x2 = Math.min(x(hi), innerW);
        g.append("rect").attr("x", x1).attr("y", 0).attr("width", x2 - x1).attr("height", innerH)
          .attr("fill", color).attr("opacity", 0.7);
        g.append("text").attr("x", (x1 + x2) / 2).attr("y", -10)
          .attr("text-anchor", "middle").attr("fill", COL.muted)
          .attr("font-size", 8).attr("font-weight", "500").text(label);
      });

      y.ticks(5)
        .filter((t) => t < yHi - 1e-9)
        .forEach((t) => {
          g.append("line")
            .attr("x1", 0)
            .attr("x2", innerW)
            .attr("y1", y(t))
            .attr("y2", y(t))
            .attr("stroke", COL.grid)
            .attr("stroke-width", 0.6);
        });
      y.ticks(5).forEach((t) => {
        g.append("text").attr("x", -8).attr("y", y(t)).attr("dy", "0.35em")
          .attr("text-anchor", "end").attr("fill", COL.muted).attr("font-size", 8.5).text(t);
      });
      /* Axe X */
      [2005, 2008, 2011, 2014, 2017, 2020, 2024].forEach((yr) => {
        g.append("text").attr("x", x(yr)).attr("y", innerH + 16).attr("text-anchor", "middle")
          .attr("fill", COL.muted).attr("font-size", 8.5).text(yr);
      });
      g.append("text").attr("x", innerW / 2).attr("y", innerH + 38).attr("text-anchor", "middle")
        .attr("fill", COL.muted).attr("font-size", 9).attr("font-weight", "500").text("Année");

      /* Ligne zéro */
      if (yLo < 0) {
        g.append("line").attr("x1", 0).attr("x2", innerW).attr("y1", y(0)).attr("y2", y(0))
          .attr("stroke", COL.muted).attr("stroke-width", 0.5).attr("stroke-dasharray", "3,3");
      }

      /* Courbes */
      const serDefs = [
        { key: "FR", label: "France", color: SERIE_PAYS.FR, w: 2.8 },
        { key: "DK", label: "Danemark", color: SERIE_PAYS.DK, w: 2.2 },
      ];
      const clipIdLT = "clip-lt";
      svg.append("defs").append("clipPath").attr("id", clipIdLT)
        .append("rect").attr("x", 0).attr("y", -8).attr("width", innerW + 2).attr("height", innerH + 16);
      const linesG = g.append("g").attr("clip-path", `url(#${clipIdLT})`);

      const line = d3.line().x((d) => x(d.year)).y((d) => y(d.value)).curve(d3.curveLinear);
      serDefs.forEach(({ key, label, color, w: lw }) => {
        const serPts = pointsFromRows(rows, key).filter((p) => p.year >= 2005 && p.year <= 2024);
        linesG.append("path").datum(serPts).attr("fill", "none")
          .attr("stroke", color).attr("stroke-width", lw).attr("d", line);
        /* Étiquette fin de courbe */
        const last = serPts[serPts.length - 1];
        if (last) {
          g.append("text").attr("x", innerW + 10).attr("y", y(last.value)).attr("dy", "0.35em")
            .attr("fill", color).attr("font-size", 9.5).attr("font-weight", "700").text(label);
          g.append("text").attr("x", innerW + 10).attr("y", y(last.value) + 13).attr("dy", "0.35em")
            .attr("fill", color).attr("font-size", 8).text(`${last.value.toFixed(1)}\u202f‰ (${last.year})`);
        }
      });

      art.append("p").attr("class", "figure-foot").text(
        "Sources : Eurostat, solde migratoire net harmonisé (CNMIGRATRT), pour 1 000 habitants. Les bandes de couleur indiquent les mandats présidentiels français. Lecture : quel que soit le gouvernement en place, la France est restée en dessous du Danemark sur l'ensemble de la période, y compris sous Sarkozy et Hollande."
      );
    }
  }


  /* Angle 2 : Premiers titres de séjour par motif (2022, pour 1 000 hab.) */
  {
    const permits = (data.nationalStats || {}).permitsMotif || [];
    if (permits.length) {
      const motifs = ["travail", "famille", "etudes", "autres"];
      const totalPerm = (d) => motifs.reduce((s, m) => s + (d[m] || 0), 0);
      const frP = permits.find((p) => p.code === "FR");
      const ukP = permits.find((p) => p.code === "UK");
      const fmtPerm = (x) => x.toFixed(1).replace(".", ",");
      const titlePerm =
        frP && ukP
          ? `Premiers titres de séjour en 2022 : la France en délivre ${fmtPerm(totalPerm(frP))} pour 1 000 habitants, contre ${fmtPerm(totalPerm(ukP))} au Royaume-Uni`
          : "Premiers titres de séjour en 2022 : la France et le Royaume-Uni comparés pour 1 000 habitants";

      const art = main.append("article").attr("class", "figure").attr("data-export-slug", "permis-sejour-motifs-2022-fr-uk");
      figureHead(art, {
        title: titlePerm,
        sub:
          "Premiers titres de séjour de longue durée (12 mois ou plus), par motif, pour 1 000 habitants, 2022. Eurostat (migr_resfirst), Home Office (UK).",
      });
      const wrap = art.append("div").attr("class", "chart-host chart-bar-swiss");

      const w = 900;
      const margin = { top: 20, right: 20, bottom: 72, left: 116 };
      const innerW = w - margin.left - margin.right;
      const rowH = 44;
      const innerH = permits.length * rowH;
      const h = innerH + margin.top + margin.bottom;
      const svg = wrap.append("svg").attr("viewBox", `0 0 ${w} ${h}`).attr("width", "100%").attr("height", h);
      const g = svg.append("g").attr("transform", `translate(${margin.left},${margin.top})`);

      const colors = { travail: COL.plum, famille: COL.teal, etudes: COL.blue, autres: COL.coral };
      const labels = { travail: "Travail", famille: "Famille", etudes: "Études", autres: "Autres / protection" };

      const xMax = d3.max(permits, (d) => motifs.reduce((s, m) => s + d[m], 0));
      const x = d3.scaleLinear().domain([0, xMax * 1.08]).range([0, innerW]);
      const y = d3.scaleBand().domain(permits.map((d) => d.pays)).range([0, innerH]).paddingInner(0.25).paddingOuter(0.1);

      x.ticks(6).forEach((t) => {
        g.append("line")
          .attr("x1", x(t))
          .attr("x2", x(t))
          .attr("y1", 0)
          .attr("y2", innerH)
          .attr("stroke", COL.grid)
          .attr("stroke-width", 0.5);
        g.append("text")
          .attr("x", x(t))
          .attr("y", innerH + 14)
          .attr("text-anchor", "middle")
          .attr("fill", COL.muted)
          .attr("font-size", 8.5)
          .text(t);
      });
      g.append("text").attr("x", innerW / 2).attr("y", innerH + 32).attr("text-anchor", "middle")
        .attr("fill", COL.muted).attr("font-size", 9).attr("font-weight", "500").text("Pour 1 000 habitants");

      permits.forEach((d) => {
        const ys = y(d.pays);
        const bh = y.bandwidth();
        let xCursor = 0;
        motifs.forEach((m) => {
          const bw = x(d[m]);
          g.append("rect").attr("x", xCursor).attr("y", ys).attr("width", bw).attr("height", bh)
            .attr("fill", colors[m]).attr("rx", 2);
          if (bw > 26) {
            g.append("text").attr("x", xCursor + bw / 2).attr("y", ys + bh / 2).attr("dy", "0.35em")
              .attr("text-anchor", "middle").attr("fill", fillForBarInterior(colors[m]))
              .attr("font-size", 7.5).attr("font-weight", "700")
              .text(d[m].toFixed(1));
          }
          xCursor += bw;
        });
        /* Total */
        const total = motifs.reduce((s, m) => s + d[m], 0);
        g.append("text").attr("x", xCursor + 6).attr("y", ys + bh / 2).attr("dy", "0.35em")
          .attr("text-anchor", "start").attr("fill", COL.ink)
          .attr("font-size", 8.5).attr("font-weight", "700")
          .text(`${total.toFixed(1)}\u202f‰`);
        /* Pays label */
        const isFR = d.code === "FR";
        g.append("text").attr("x", -8).attr("y", ys + bh / 2).attr("dy", "0.35em")
          .attr("text-anchor", "end").attr("fill", isFR ? SERIE_PAYS.FR : COL.ink)
          .attr("font-size", 9.5).attr("font-weight", isFR ? "700" : "450")
          .text(d.pays);
      });

      /* Légende */
      const legY = margin.top + innerH + 46;
      motifs.forEach((m, i) => {
        svg.append("rect").attr("x", margin.left + i * 165).attr("y", legY).attr("width", 10).attr("height", 10)
          .attr("fill", colors[m]).attr("rx", 1);
        svg.append("text").attr("x", margin.left + i * 165 + 15).attr("y", legY + 8)
          .attr("fill", COL.ink).attr("font-size", 8.5).text(labels[m]);
      });

      art.append("p").attr("class", "figure-foot").text(
        "Source : Eurostat, table migr_resfirst (premiers permis de séjour de longue durée, >= 12 mois, citizen=TOTAL, 2022). Pour le Royaume-Uni : Home Office Immigration Statistics, year ending December 2022. Population : Eurostat au 1er janvier 2022. La catégorie « Autres / protection » regroupe les titres humanitaires, subsidiaires, et résidualiers (Eurostat ne les isole pas dans migr_resfirst)."
      );
    }
  }


  /* Angle 3 : Taux de reconnaissance asile (2022) */
  {
    const reconn = (data.nationalStats || {}).asileRecognition || [];
    if (reconn.length) {
      const art = main.append("article").attr("class", "figure").attr("data-export-slug", "taux-reconnaissance-asile-2022");
      figureHead(art, {
        title: "Taux de reconnaissance de l’asile en 2022 : des écarts importants d’un pays à l’autre",
        sub:
          "Part des décisions favorables en première instance sur l’ensemble des décisions rendues, 2022. Eurostat (migr_asydcfsta), Home Office (UK).",
      });
      const wrap = art.append("div").attr("class", "chart-host chart-bar-swiss");

      const w = 900;
      const margin = { top: 16, right: 64, bottom: 48, left: 116 };
      const innerW = w - margin.left - margin.right;
      const rowH = 36;
      const innerH = reconn.length * rowH;
      const h = innerH + margin.top + margin.bottom;
      const svg = wrap.append("svg").attr("viewBox", `0 0 ${w} ${h}`).attr("width", "100%").attr("height", h);
      const g = svg.append("g").attr("transform", `translate(${margin.left},${margin.top})`);

      const x = d3.scaleLinear().domain([0, 100]).range([0, innerW]);
      const y = d3.scaleBand().domain(reconn.map((d) => d.pays)).range([0, innerH]).paddingInner(0.3).paddingOuter(0.1);

      [0, 25, 50, 75, 100].forEach((t) => {
        g.append("line")
          .attr("x1", x(t))
          .attr("x2", x(t))
          .attr("y1", 0)
          .attr("y2", innerH)
          .attr("stroke", COL.grid)
          .attr("stroke-width", 0.5);
        g.append("text")
          .attr("x", x(t))
          .attr("y", innerH + 14)
          .attr("text-anchor", "middle")
          .attr("fill", COL.muted)
          .attr("font-size", 8.5)
          .text(`${t}\u202f%`);
      });

      /* Ligne France */
      const frRow = reconn.find((d) => d.code === "FR");
      if (frRow) {
        g.append("line").attr("x1", x(frRow.taux)).attr("x2", x(frRow.taux))
          .attr("y1", 0).attr("y2", innerH)
          .attr("stroke", COL.primary).attr("stroke-width", 1).attr("stroke-dasharray", "4,3").attr("opacity", 0.6);
      }

      reconn.forEach((d) => {
        const ys = y(d.pays);
        const bh = y.bandwidth();
        const bw = x(d.taux);
        const isFR = d.code === "FR";
        g.append("rect").attr("x", 0).attr("y", ys).attr("width", bw).attr("height", bh)
          .attr("fill", isFR ? COL.primary : COL.barMuted).attr("rx", 2).attr("opacity", isFR ? 1 : 0.75);
        /* Étiquette valeur */
        const inside = bw > 55;
        g.append("text")
          .attr("x", inside ? bw - 6 : bw + 6)
          .attr("y", ys + bh / 2).attr("dy", "0.35em")
          .attr("text-anchor", inside ? "end" : "start")
          .attr("fill", inside ? fillForBarInterior(isFR ? COL.primary : COL.barMuted) : COL.ink)
          .attr("font-size", 9).attr("font-weight", "700")
          .text(`${d.taux}\u202f%`);
        /* Pays */
        g.append("text").attr("x", -8).attr("y", ys + bh / 2).attr("dy", "0.35em")
          .attr("text-anchor", "end").attr("fill", isFR ? COL.primary : COL.ink)
          .attr("font-size", 9.5).attr("font-weight", isFR ? "700" : "450")
          .text(d.pays);
      });

      art.append("p").attr("class", "figure-foot").text(
        "Source : Eurostat, table migr_asydcfsta (décisions en première instance), 2022, age=TOTAL, sex=T, citizen=TOTAL. Pour le Royaume-Uni : Home Office Asylum Statistics year ending December 2022 (initial decisions). Lecture : le taux reflète à la fois la politique d'octroi et la composition des demandeurs (nationalités à fort ou faible taux de reconnaissance varient selon les pays) ; il ne doit pas être lu comme un indice de sévérité isolé."
      );
    }
  }

  attachFigureExports();
}

fetch("data.json")
  .then((r) => {
    if (!r.ok) throw new Error(`data.json ${r.status}`);
    return r.json();
  })
  .then((data) => {
    render(data);
    const metaEl = document.getElementById("metho-meta");
    if (metaEl && data.meta) {
      const bits = [];
      if (data.meta.datePublicationFr) {
        bits.push(`Données consolidées (libellé projet) : ${data.meta.datePublicationFr}.`);
      }
      if (data.meta.generated) {
      const d = new Date(data.meta.generated);
        bits.push(
          `Horodatage technique (UTC) : ${d.toLocaleString("fr-FR", {
        timeZone: "UTC",
        year: "numeric",
        month: "long",
        day: "numeric",
        hour: "2-digit",
        minute: "2-digit",
          })}.`,
        );
      }
      if (data.meta.pipeline) {
        bits.push(`Chaîne : ${data.meta.pipeline}`);
      }
      metaEl.textContent = bits.join(" ");
    }
  })
  .catch((e) => {
    document.getElementById("main-figures").innerHTML =
      `<p class="figure-sub">Impossible de charger data.json (${e.message}).</p>`;
  });

