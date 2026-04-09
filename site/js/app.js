/**
 * D3, style atlas. Grille légère, typo Book / Medium. Annotations : data.annotations.
 */
/* global d3 */

const COL = {
  ink: "#141414",
  red: "#b83838",
  blue: "#256070",
  plum: "#6b3050",
  coral: "#c47872",
  teal: "#1a4d5c",
  grid: "#ecebe8",
  muted: "#5a5a58",
  barMuted: "#a8b4b8",
  barOthers: "#4a7a86",
  peerGray: "#b8b8b6",
};

const PEER_COLORS = [COL.red, COL.blue, COL.plum, COL.coral, COL.teal, COL.ink];

/**
 * Titres : thèse éditoriale (ce que le graphique démontre).
 * Sous-titres : variable mesurée + unité, style NYT/WSJ, une ligne max.
 */
const TITLES = {
  1: {
    title: "La France, la plus fermée parmi ses comparateurs",
    sub: "Solde migratoire net pour 1 000 habitants",
  },
  2: {
    title: "La France en queue de peloton parmi ses voisins",
    sub: "Solde migratoire net pour 1 000 habitants",
  },
  3: {
    title: "Sur l’asile, une pression contenue en France",
    sub: "Premières demandes d’asile pour 1 000 habitants",
  },
  4: {
    title: "En 2024, la France dans le bas du classement européen",
    sub: "Solde migratoire net pour 1 000 habitants",
  },
  5: {
    title: "Quatre grandes économies : la France stable et discrète",
    sub: "Solde migratoire net pour 1 000 habitants",
  },
  6: {
    title: "La France glisse vers les dernières places de l’UE",
    sub: "Rang parmi les 27 États membres (1 = solde le plus élevé)",
  },
  7: {
    title: "L’asile représente une part variable selon les pays",
    sub: "Premières demandes d’asile rapportées au solde migratoire net",
  },
  asylumBars: {
    title: "Demandes d’asile : la France dans la fourchette basse",
    sub: "Premières demandes pour 1 000 habitants, dernière année",
  },
  entrees: {
    title: "En entrées brutes, la France toujours en retrait",
    sub: "Ressortissants étrangers entrants pour 1 000 habitants",
  },
  dual: {
    title: "Deux mesures, le même constat : la France accueille peu",
    sub: "Pour 1 000 habitants, dernière année disponible",
  },
  volatility: {
    title: "La France, trajectoire la plus stable parmi les quatre",
    sub: "Écart-type du solde annuel, mesure des fluctuations d'une année à l'autre",
  },
};

const DYADS = [
  {
    peerKey: "DK",
    peerLabel: "Danemark",
    title: "Le Danemark de Frederiksen reste plus ouvert que la France",
    sub: "Solde migratoire net pour 1 000 habitants, 2013-2024",
    colorPeer: COL.red,
  },
  {
    peerKey: "IT",
    peerLabel: "Italie",
    title: "L’Italie de Meloni accueille davantage que la France",
    sub: "Solde migratoire net pour 1 000 habitants, 2013-2024",
    colorPeer: COL.coral,
  },
  {
    peerKey: "UK",
    peerLabel: "Royaume-Uni",
    title: "Le Brexit n’a pas fermé le Royaume-Uni à l’immigration",
    sub: "Solde migratoire net pour 1 000 habitants, 2013-2024",
    colorPeer: COL.plum,
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

  function spreadVertical(group) {
    let ly = group.map((d) => d.py);
    for (let p = 0; p < 14; p++) {
      for (let i = 1; i < ly.length; i++) {
        if (ly[i] - ly[i - 1] < gap) ly[i] = ly[i - 1] + gap;
      }
      for (let i = ly.length - 2; i >= 0; i--) {
        if (ly[i + 1] - ly[i] < gap) ly[i] = ly[i + 1] - gap;
      }
    }
    ly = ly.map((y) => Math.min(Math.max(y, 8), innerH - 8));
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
  const rows = data.migrationSelection;
  figureHead(container, { title, sub });
  const host = container.append("div").attr("class", "chart-host");
  const frPts = pointsFromRows(rows, "FR");
  const peerPts = pointsFromRows(rows, peerKey);
  const yDom = extentValues([frPts, peerPts]);
  lineChartFigure(host, {
    rows,
    seriesDefs: [
      { key: "FR", label: "France", color: COL.blue, width: 2.9 },
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
        .attr("stroke", "#fafaf9")
        .attr("stroke-width", 0.65)
        .attr("stroke-linejoin", "round");
    },
  },
  {
    id: "sun",
    draw(g, color) {
      const w = 1.35;
      const cap = "round";
      g.append("circle").attr("cx", 12).attr("cy", 12).attr("r", 4).attr("fill", color).attr("stroke", "#fafaf9").attr("stroke-width", 0.5);
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

  const series = seriesDefs.map((d) => ({
    key: d.key,
    label: d.label,
    color: d.color,
    dash: d.dash || null,
    width: d.width ?? 2.2,
    points: pointsFromRows(rows, d.key),
  }));

  const allPts = series.map((s) => s.points);
  const xDom = xDomIn || extentYears(allPts);
  const yDom = yDomIn || extentValues(allPts);

  const w = Math.max(900, container.node().getBoundingClientRect().width || 900);
  const innerW = w - margin.left - margin.right;
  const innerH = height - margin.top - margin.bottom;

  const svg = container
    .append("svg")
    .attr("class", "chart-line-swiss")
    .attr("viewBox", `0 0 ${w} ${height}`)
    .attr("width", w)
    .attr("height", height);

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

  const yTicks = y.ticks(6);
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

    g.selectAll(`.dot-${s.key}`)
      .data(s.points)
      .join("circle")
      .attr("class", `dot-${s.key}`)
      .attr("cx", (d) => x(d.year))
      .attr("cy", (d) => y(d.value))
      .attr("r", 9)
      .attr("fill", "transparent")
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

  const calloutItems = [];
  if (annotations && annotations.length) {
    annotations.forEach((ann) => {
      const tgtKey = ann.target === "peer" ? peerKey : ann.target;
      const s = targetMap[tgtKey];
      if (!s) return;
      const pt = s.points.find((p) => p.year === ann.year);
      if (!pt) return;
      calloutItems.push({
        sx: margin.left + x(pt.year),
        sy: margin.top + y(pt.value),
        text: ann.text,
        color: s.color,
      });
    });
    drawMarkerLabels(svg, calloutItems, margin.top + innerH);
  }

  const labelColW = series.length >= 4 ? 64 : 0;
  const labelXBase = innerW + 10;
  const layouts = layoutEndLabels(series, x, y, innerW, innerH, labelGap);
  const lg = g.append("g").attr("class", "end-labels");
  layouts.forEach((d) => {
    const lx = labelXBase + (d.col || 0) * labelColW;
    lg.append("path")
      .attr("d", `M${d.px},${d.py} L${lx - 6},${d.ly} L${lx - 2},${d.ly}`)
      .attr("fill", "none")
      .attr("stroke", d.series.color)
      .attr("stroke-width", 0.55)
      .attr("opacity", 0.8);
    lg.append("text")
      .attr("x", lx)
      .attr("y", d.ly)
      .attr("dy", "0.35em")
      .attr("fill", d.series.color)
      .attr("font-size", 10.5)
      .attr("font-weight", "500")
      .text(d.series.label);
  });
}

/** Un seul panneau : France (bleu) + pays voisins (gris), sans FX. */
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

/** Grille verticale discrète (repères, sans trait d’axe). */
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

/** Libellés catégories à gauche (sans composant axe D3). */
function appendBarCategoryLabelsY(g, y, fontSize = 9.25) {
  y.domain().forEach((lab) => {
    g.append("text")
      .attr("class", "bar-y-label")
      .attr("x", -6)
      .attr("y", y(lab) + y.bandwidth() / 2)
      .attr("dy", "0.35em")
      .attr("text-anchor", "end")
      .attr("fill", COL.ink)
      .attr("font-size", fontSize)
      .attr("font-weight", "450")
      .text(lab);
  });
}

function neighborsLineFigure(container, data, tooltip) {
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
      color: COL.peerGray,
      width: 1.75,
    })),
    {
      key: "FR",
      label: "France",
      color: COL.blue,
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

  appendBarCategoryLabelsY(g, y);

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

function dualBarRow(container, data, footer) {
  figureHead(container, TITLES.dual);

  const row = container.append("div").attr("class", "row-2");
  const net = data.dualNetAsylum2024.net || [];
  const asy = data.dualNetAsylum2024.asylum || [];

  function mini(host, label, rows) {
    host.append("p").attr("class", "mini-panel-title").text(label);
    const h = host.append("div").attr("class", "chart-host chart-bar-swiss");
    const w = 440;
    const rowH = 34;
    const margin = { top: 8, right: 56, bottom: 36, left: 150 };
    const innerW = w - margin.left - margin.right;
    const innerH = Math.max(rows.length * rowH, 40);
    const height = innerH + margin.top + margin.bottom;
    const svg = h.append("svg").attr("viewBox", `0 0 ${w} ${height}`).attr("width", "100%").attr("height", height);
    const g = svg.append("g").attr("transform", `translate(${margin.left},${margin.top})`);

    const inset = { left: 8, right: 8, top: 6, bottom: 8 };
    const vals = rows.map((r) => r.value);
    const useSigned = vals.some((v) => Number.isFinite(v) && v < 0);
    const maxV = d3.max(vals);
    const xDom = useSigned ? xDomainSignedBars(vals) : [0, Math.max((Number.isFinite(maxV) ? maxV : 0) * 1.12, 1e-6)];
    const x = d3.scaleLinear().domain(xDom).range([inset.left, innerW - inset.right]);
    const y = d3
      .scaleBand()
      .domain(rows.map((r) => r.label))
      .range([inset.top, innerH - inset.bottom])
      .paddingInner(0.35)
      .paddingOuter(0.1);

    const x0 = x(0);

    appendHorizontalBarGrid(g, x, inset, innerH, 5);
    appendBarTickLabelsX(g, x, innerH, 5, 8.25);

    appendBarCategoryLabelsY(g, y, 8.75);

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
      .attr("y", innerH + 26)
      .attr("text-anchor", "middle")
      .attr("fill", COL.muted)
      .attr("font-size", 8.5)
      .attr("font-weight", "500")
      .text("Pour 1 000 habitants");
  }

  mini(row.append("div"), "Solde net", net);
  mini(row.append("div"), "Asile", asy);
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

  /* 1 Vue d’ensemble quatre pays */
  {
    const art = main.append("article").attr("class", "figure");
    figureHead(art, TITLES[1]);
    const host = art.append("div").attr("class", "chart-host");
    const corePts = ["FR", "DK", "IT", "UK"].map((k) => pointsFromRows(rows, k));
    const yDom = extentValues(corePts);
    lineChartFigure(host, {
      rows,
      seriesDefs: [
        { key: "FR", label: "France", color: COL.blue, width: 2.85 },
        { key: "DK", label: "Danemark", color: COL.red, width: 2.15 },
        { key: "IT", label: "Italie", color: COL.coral, width: 2.15 },
        { key: "UK", label: "Royaume-Uni", color: COL.plum, width: 2.15 },
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

  /* 1a–c Duos France / Danemark, Italie, Royaume-Uni */
  for (const d of DYADS) {
    const art = main.append("article").attr("class", "figure");
    dyadLineFigure(art, data, tooltip, d);
  }

  /* Volatilité */
  {
    const vol = data.volatilitySoldeCore || [];
    if (vol.length) {
      const art = main.append("article").attr("class", "figure");
      const y0 = vol[0].yearLo;
      const y1 = vol[0].yearHi;
      figureHead(art, {
        title: TITLES.volatility.title,
        sub: `${TITLES.volatility.sub}, ${y0 ?? "…"}–${y1 ?? "…"}`,
      });
      /* Volatilité : exception à la règle « France rouge / autres gris » — une couleur par pays. */
      const barColor = (d) => {
        if (d.code === "FR") return COL.blue;
        if (d.code === "DK") return COL.red;
        if (d.code === "IT") return COL.coral;
        if (d.code === "UK") return COL.plum;
        return COL.peerGray;
      };
      barHFigure(art, {
        rows: vol.map((d) => ({
          code: d.code,
          label: d.label,
          yLabel: d.label,
          value: d.stdev,
        })),
        xLabel: "Écart-type (pour 1 000 hab.)",
        valueFormat: (v) => v.toFixed(3),
        barColor,
        labelColor: COL.ink,
        rowH: 42,
      });
      const foot = (data.copy && data.copy.volatilityFooter) || "";
      if (foot) art.append("p").attr("class", "figure-foot").text(foot);
    }
  }

  /* 2 Voisins */
  {
    const art = main.append("article").attr("class", "figure");
    neighborsLineFigure(art, data, tooltip);
  }

  /* 3 Asile */
  {
    const art = main.append("article").attr("class", "figure");
    figureHead(art, TITLES[3]);
    const host = art.append("div").attr("class", "chart-host");
    const codes = data.asylumLineCodes || ["FR", "DE", "IT", "SE", "DK"];
    const asyRows = data.asylum || [];
    let peerIdx = 0;
    const defs = codes.map((code) => {
      const isFr = code === "FR";
      const col = isFr ? COL.ink : PEER_COLORS[peerIdx++ % PEER_COLORS.length];
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
      yLabel: "Premières demandes / 1 000 hab.",
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
      const art = main.append("article").attr("class", "figure");
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

  /* 4 Classement UE */
  {
    const art = main.append("article").attr("class", "figure");
    figureHead(art, TITLES[4]);
    const eu = data.euRanking2024 || [];
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

    appendBarCategoryLabelsY(g, y);

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

  /* 5 Quadri */
  {
    const art = main.append("article").attr("class", "figure");
    figureHead(art, TITLES[5]);
    const host = art.append("div").attr("class", "chart-host");
    lineChartFigure(host, {
      rows: data.migrationMulti || [],
      seriesDefs: [
        { key: "FR", label: "France", color: COL.blue, width: 2.85 },
        { key: "DE", label: "Allemagne", color: COL.peerGray, width: 2.05 },
        { key: "IT", label: "Italie", color: COL.plum, width: 2.05 },
        { key: "ES", label: "Espagne", color: COL.coral, width: 2.05 },
      ],
      tooltip,
      height: 438,
    });
    const qf = data.copy?.analyseQuadriFooter;
    if (qf) art.append("p").attr("class", "figure-foot").text(qf);
  }

  /* 6 Rang France */
  {
    const rankRows = (data.analyseRangFrance || [])
      .filter((r) => r.rangFrance != null)
      .map((r) => ({ year: r.annee, rang: r.rangFrance }));
    if (rankRows.length) {
      const art = main.append("article").attr("class", "figure");
      figureHead(art, TITLES[6]);
      const host = art.append("div").attr("class", "chart-host");
      lineChartFigure(host, {
        rows: rankRows,
        seriesDefs: [{ key: "rang", label: "Rang France", color: COL.red, width: 2.75 }],
        tooltip,
        yLabel: "Rang (1 = plus fort)",
        yDomain: [27, 1],
        height: 400,
      });
      const rf = data.copy?.analyseRangFooter;
      if (rf) art.append("p").attr("class", "figure-foot").text(rf);
    }
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
      const art = main.append("article").attr("class", "figure");
      figureHead(art, TITLES[7]);
      const host = art.append("div").attr("class", "chart-host");
      lineChartFigure(host, {
        rows: ratioRows,
        seriesDefs: [
          { key: "FR", label: "France", color: COL.red, width: 2.55 },
          { key: "DE", label: "Allemagne", color: COL.peerGray, width: 2.05 },
          { key: "IT", label: "Italie", color: COL.plum, width: 2.05 },
          { key: "ES", label: "Espagne", color: COL.teal, width: 2.05 },
        ],
        tooltip,
        yLabel: "Ratio asile / solde",
        height: 420,
      });
      const rtf = data.copy?.analyseRatioFooter;
      if (rtf) art.append("p").attr("class", "figure-foot").text(rtf);
    }
  }

  /* 8 Panneau double solde / asile */
  {
    const art = main.append("article").attr("class", "figure");
    dualBarRow(art, data, data.copy?.dualFooter);
  }

  /* 9 Entrées de nationalité étrangère (Eurostat) */
  {
    const fe = data.foreignEntries || [];
    if (fe.length) {
      const art = main.append("article").attr("class", "figure");
      figureHead(art, TITLES.entrees);
      const host = art.append("div").attr("class", "chart-host");
      const frPts = pointsFromRows(fe, "FR");
      const dkPts = pointsFromRows(fe, "DK");
      const itPts = pointsFromRows(fe, "IT");
      const yDom = extentValuesFrom([frPts, dkPts, itPts], 0.08, 0.35);
      lineChartFigure(host, {
        rows: fe,
        seriesDefs: [
          { key: "FR", label: "France", color: COL.blue, width: 2.75 },
          { key: "DK", label: "Danemark", color: COL.red, width: 2.2 },
          { key: "IT", label: "Italie", color: COL.coral, width: 2.2 },
        ],
        annotations: [],
        tooltip,
        yLabel: "Entrées pour 1 000 habitants",
        yDomain: yDom,
        xDomain: [2016, 2024],
        height: 420,
        margin: { top: 20, right: 200, bottom: 52, left: 64 },
      });
      const enf = data.copy?.entreesFooter;
      if (enf) art.append("p").attr("class", "figure-foot").text(enf);
    }
  }

  /* ── GRAPHIQUES STATISTIQUES NATIONALES (INSEE / Statistics DK / Istat / ONS) ── */
  const NS = data.nationalStats || {};

  /* N1 — Danemark (étrangers, Stat DK) vs France (immigrés, INSEE) */
  {
    const dkRows = (NS.dkEtrangers || []).map(r => ({ year: r.year, DK: r.value }));
    const frRows = (NS.frImmigres || []).map(r => ({ year: r.year, FR: r.value, estimated: r.estimated }));
    const merged = {};
    for (const r of dkRows) { merged[r.year] = { year: r.year, DK: r.DK }; }
    for (const r of frRows) { if (!merged[r.year]) merged[r.year] = { year: r.year }; merged[r.year].FR = r.FR; merged[r.year].estimated = r.estimated; }
    const mRows = Object.values(merged).sort((a, b) => a.year - b.year);
    if (mRows.length) {
      const art = main.append("article").attr("class", "figure");
      figureHead(art, {
        title: "Même avec les données nationales, le Danemark reste au-dessus",
        sub: "Solde étrangers au Danemark (Statistics Denmark) vs solde immigrés en France (INSEE)",
      });
      const host = art.append("div").attr("class", "chart-host");
      const frPts = mRows.filter(r => r.FR != null).map(r => ({ year: r.year, value: r.FR }));
      const dkPts = mRows.filter(r => r.DK != null).map(r => ({ year: r.year, value: r.DK }));
      const yDom = extentValues([frPts, dkPts]);
      lineChartFigure(host, {
        rows: mRows,
        seriesDefs: [
          { key: "FR", label: "France (immigrés, INSEE)", color: COL.blue, width: 2.6 },
          { key: "DK", label: "Danemark (étrangers, Stat DK)", color: COL.red, width: 2.1 },
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
        "Sources : Statistics Denmark (solde migratoire des étrangers, citizenship-based) ; INSEE (solde migratoire des immigrés, France métropolitaine). 2022-2024 France = estimation (94 000 sorties/an). Indicateurs non strictement équivalents : l'indicateur danois est un minorant par rapport au français."
      );
    }
  }

  /* N2 — Italie (étrangers, Istat) vs France (immigrés, INSEE) */
  {
    const itRows = (NS.itEtrangers || []).map(r => ({ year: r.year, IT: r.value }));
    const frRows = (NS.frImmigres || []).map(r => ({ year: r.year, FR: r.value }));
    const merged = {};
    for (const r of itRows) { merged[r.year] = { year: r.year, IT: r.IT }; }
    for (const r of frRows) { if (!merged[r.year]) merged[r.year] = { year: r.year }; merged[r.year].FR = r.FR; }
    const mRows = Object.values(merged).sort((a, b) => a.year - b.year);
    if (mRows.length) {
      const art = main.append("article").attr("class", "figure");
      figureHead(art, {
        title: "L'Italie de Meloni accueille toujours plus que la France, en données nationales",
        sub: "Solde étrangers en Italie (Istat) vs solde immigrés en France (INSEE)",
      });
      const host = art.append("div").attr("class", "chart-host");
      const frPts = mRows.filter(r => r.FR != null).map(r => ({ year: r.year, value: r.FR }));
      const itPts = mRows.filter(r => r.IT != null).map(r => ({ year: r.year, value: r.IT }));
      const yDom = extentValues([frPts, itPts]);
      lineChartFigure(host, {
        rows: mRows,
        seriesDefs: [
          { key: "FR", label: "France (immigrés, INSEE)", color: COL.blue, width: 2.6 },
          { key: "IT", label: "Italie (étrangers, Istat)", color: COL.coral, width: 2.1 },
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
        "Sources : Istat (solde migratoire des étrangers, Italie) ; INSEE (solde migratoire des immigrés, France). 2022-2024 France = estimation. Même biais méthodologique que pour le Danemark : l'indicateur Istat est citizenship-based, l'indicateur INSEE est birthplace-based."
      );
    }
  }

  /* N3 — Royaume-Uni (étrangers, ONS) vs France (immigrés, INSEE) */
  {
    const ukRows = (NS.ukEtrangers || []).map(r => ({ year: r.year, UK: r.value }));
    const frRows = (NS.frImmigres || []).map(r => ({ year: r.year, FR: r.value }));
    const merged = {};
    for (const r of ukRows) { merged[r.year] = { year: r.year, UK: r.UK }; }
    for (const r of frRows) { if (!merged[r.year]) merged[r.year] = { year: r.year }; merged[r.year].FR = r.FR; }
    const mRows = Object.values(merged).sort((a, b) => a.year - b.year);
    if (mRows.length) {
      const art = main.append("article").attr("class", "figure");
      figureHead(art, {
        title: "À partir de 2021, le Royaume-Uni s'envole quand la France reste stable",
        sub: "Solde étrangers au Royaume-Uni (ONS LTIM) vs solde immigrés en France (INSEE)",
      });
      const host = art.append("div").attr("class", "chart-host");
      const frPts = mRows.filter(r => r.FR != null).map(r => ({ year: r.year, value: r.FR }));
      const ukPts = mRows.filter(r => r.UK != null).map(r => ({ year: r.year, value: r.UK }));
      const yDom = extentValues([frPts, ukPts]);
      lineChartFigure(host, {
        rows: mRows,
        seriesDefs: [
          { key: "FR", label: "France (immigrés, INSEE)", color: COL.blue, width: 2.6 },
          { key: "UK", label: "Royaume-Uni (étrangers, ONS)", color: COL.plum, width: 2.1 },
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
      const art = main.append("article").attr("class", "figure");
      figureHead(art, {
        title: "Le Brexit a substitué l'immigration non-européenne à l'européenne",
        sub: "Solde migratoire net du Royaume-Uni par origine, en milliers de personnes (ONS LTIM)",
      });
      const wrap = art.append("div").attr("class", "chart-host chart-bar-swiss");

      const w = 900;
      /* Marge droite généreuse pour que les étiquettes des grandes barres restent dans le SVG */
      /* Marge gauche pour les années ; domaine x très étendu vers les nég. + libellés UE collés au zéro, pas à gauche des barres */
      const margin = { top: 16, right: 16, bottom: 60, left: 76 };
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

      /* Grille verticale */
      x.ticks(6).forEach(t => {
        g.append("line").attr("x1", x(t)).attr("x2", x(t)).attr("y1", 0).attr("y2", innerH)
          .attr("stroke", "#e0deda").attr("stroke-width", 0.5);
        g.append("text").attr("x", x(t)).attr("y", innerH + 16).attr("text-anchor", "middle")
          .attr("fill", COL.muted).attr("font-size", 8.5).text(t);
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
          .attr("fill", COL.coral).attr("rx", 2);

        /* Étiquette non-UE : à l'intérieur si la barre est assez longue, sinon après */
        const neuBarEnd = Math.max(x0, x(r.nonEu));
        const neuLabelInside = wNeu > 60;
        g.append("text")
          .attr("x", neuLabelInside ? neuBarEnd - 5 : neuBarEnd + 5)
          .attr("y", ys + half * 0.65)
          .attr("text-anchor", neuLabelInside ? "end" : "start")
          .attr("fill", neuLabelInside ? "#fafaf9" : COL.ink)
          .attr("font-size", 7.5).attr("font-weight", "600")
          .text(`${r.nonEu > 0 ? "+" : ""}${r.nonEu}k`);

        /* Étiquette UE : positifs inchangés ; négatifs : toujours centré sur la barre corail, blanc + contour (lisible sur le saumon) */
        const euIsNeg = r.eu < 0;
        const euLabelInsidePos = !euIsNeg && wEu > 40;
        const yUe = ys + half + 1 + (half - 2) / 2;
        if (euIsNeg) {
          const fs = wEu < 22 ? 7 : 8;
          g.append("text")
            .attr("class", "uk-eu-neg-value")
            .attr("x", xEu + wEu / 2)
            .attr("y", yUe)
            .attr("dy", "0.35em")
            .attr("text-anchor", "middle")
            .attr("fill", "#fafaf9")
            .attr("stroke", "rgba(60, 28, 48, 0.55)")
            .attr("stroke-width", 0.65)
            .attr("paint-order", "stroke fill")
            .attr("font-size", fs)
            .attr("font-weight", "700")
            .attr("font-variant-numeric", "tabular-nums")
            .text(`${r.eu}k`);
        } else {
          const euLabelX = euLabelInsidePos ? x0 + wEu - 5 : x0 + wEu + 5;
          const euAnchor = euLabelInsidePos ? "end" : "start";
          const euFill = euLabelInsidePos ? "#fafaf9" : COL.muted;
          g.append("text")
            .attr("x", euLabelX)
            .attr("y", yUe)
            .attr("dy", "0.35em")
            .attr("text-anchor", euAnchor)
            .attr("fill", euFill)
            .attr("font-size", 7.5).attr("font-weight", "600")
            .text(`${r.eu > 0 ? "+" : ""}${r.eu}k`);
        }

        /* Année : bien à gauche du tracé */
        g.append("text").attr("x", -8).attr("y", ys + bh / 2).attr("dy", "0.35em")
          .attr("text-anchor", "end").attr("fill", COL.ink)
          .attr("font-size", 8.5).attr("font-weight", "450").text(r.year);
      });

      /* Légende */
      const legY = margin.top + innerH + 46;
      const legItems = [
        [COL.plum, "Non-UE"],
        [COL.coral, "UE"],
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
}

fetch("data.json")
  .then((r) => {
    if (!r.ok) throw new Error(`data.json ${r.status}`);
    return r.json();
  })
  .then((data) => {
    render(data);
    const metaEl = document.getElementById("metho-meta");
    if (metaEl && data.meta?.generated) {
      const d = new Date(data.meta.generated);
      metaEl.textContent = `Jeu de données agrégé : ${d.toLocaleString("fr-FR", {
        timeZone: "UTC",
        year: "numeric",
        month: "long",
        day: "numeric",
        hour: "2-digit",
        minute: "2-digit",
      })} UTC.`;
    }
  })
  .catch((e) => {
    document.getElementById("main-figures").innerHTML =
      `<p class="figure-sub">Impossible de charger data.json (${e.message}).</p>`;
  });
