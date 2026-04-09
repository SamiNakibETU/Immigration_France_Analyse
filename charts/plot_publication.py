"""
Figures publication — Eurostat + CSV utilisateur + ONS (UK) · titres datajournalisme.
Charte couleurs type La Grande Conversation (#F3ECE6, #262626, #FF3F3F, #2E879A).

Exécution : python plot_publication.py
"""

from __future__ import annotations

from pathlib import Path
from datetime import datetime

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as mticker
import numpy as np

import data_spec as DS
from design_tokens import (
    COLOR_SERIES,
    FONT_SERIF,
    FIG_PAD_LEFT,
    FIG_WIDTH_IN,
    TN_BAR_MUTED,
    TN_BAR_OTHERS,
    TN_BLUE,
    TN_GRID,
    TN_INK,
    TN_MUTED,
    TN_PAPER,
    TN_PLUM,
    TN_RED,
    apply_matplotlib_style,
    header_top_margin,
    wrap_academic,
)
from eurostat_api import load_or_fetch_dataset, parse_geo_time, per_1000_hab
from eurostat_migration import load_or_fetch, series_to_csv, write_eu27_cnmigratrt_2024_csv
from migration_csv import apply_user_csv_overrides, default_user_csv_paths, load_eu_panel_2024
from ons_fetch import refresh_ons_ltim
from uk_ons_series import UK_SOURCE_FOOTNOTE, uk_rate_per_1000_series

ANNOTATIONS: dict[str, list[tuple[int, str, str]]] = {
    "DK": [(2015, "Pic UE (asile)", "peer"), (2022, "Ukraine", "peer")],
    "IT": [(2015, "Pic UE (asile)", "peer"), (2022, "Ukraine", "peer")],
    "UK": [
        (2014, "Asile", "peer"),
        (2015, "Brexit", "peer"),
        (2020, "Covid", "peer"),
        (2022, "Ukraine", "peer"),
    ],
}

# Figure Italie : cible explicite FR / FX / IT
ANNOTATIONS_IT_TRIPLE: list[tuple[int, str, str]] = [
    (2015, "Crise de l’asile", "IT"),
    (2022, "Ukraine", "IT"),
    (2023, "Meloni", "IT"),
]

DISPLAY_NAMES = {
    "FR": "France (entière)",
    "FX": "France métropolitaine",
    "DK": "Danemark",
    "IT": "Italie",
    "UK": "Royaume-Uni",
    "DE": "Allemagne",
    "ES": "Espagne",
    "SE": "Suède",
    "NL": "Pays-Bas",
    "AT": "Autriche",
    "BE": "Belgique",
    "EL": "Grèce",
    "PL": "Pologne",
    "PT": "Portugal",
    "RO": "Roumanie",
    "BG": "Bulgarie",
    "HR": "Croatie",
    "CY": "Chypre",
    "CZ": "Tchéquie",
    "HU": "Hongrie",
    "IE": "Irlande",
    "LT": "Lituanie",
    "LU": "Luxembourg",
    "LV": "Lettonie",
    "MT": "Malte",
    "SI": "Slovénie",
    "SK": "Slovaquie",
    "EE": "Estonie",
    "FI": "Finlande",
}


def _peer_name(code: str) -> str:
    return DISPLAY_NAMES.get(code, code)


def _years_to_dates(years: list[int]) -> list[datetime]:
    return [datetime(y, 1, 1) for y in years]


def _figure_heading(fig: plt.Figure, lead: str, academic_sub: str) -> float:
    """Titre « punch » (serif) + bloc académique (sans serif, césure). Retourne top pour subplots_adjust."""
    sub = wrap_academic(academic_sub)
    fig.text(
        FIG_PAD_LEFT,
        0.985,
        lead,
        transform=fig.transFigure,
        fontsize=17,
        fontweight="700",
        color=TN_INK,
        ha="left",
        va="top",
        family=FONT_SERIF[0],
    )
    nlines = sub.count("\n") + 1
    y_sub = 0.94 - 0.006 * max(0, nlines - 2)
    fig.text(
        FIG_PAD_LEFT,
        y_sub,
        sub,
        transform=fig.transFigure,
        fontsize=9.15,
        color=TN_MUTED,
        ha="left",
        va="top",
        linespacing=1.38,
    )
    return header_top_margin(academic_sub)


def _add_source_fig(fig: plt.Figure, text: str, y: float = 0.02) -> None:
    fig.text(
        FIG_PAD_LEFT,
        y,
        text,
        transform=fig.transFigure,
        fontsize=8.4,
        color=TN_MUTED,
        ha="left",
        va="bottom",
    )


def _style_axes_area(ax: plt.Axes) -> None:
    ax.grid(True, axis="y", color=TN_GRID, linewidth=0.55, zorder=0)
    ax.grid(False, axis="x")


def _source_under_ax(fig: plt.Figure, ax: plt.Axes, text: str) -> None:
    bb = ax.get_position()
    fig.text(
        bb.x0,
        bb.y0 - 0.03,
        text,
        transform=fig.transFigure,
        fontsize=8.2,
        color=TN_MUTED,
        va="top",
        ha="left",
    )


def _end_label_line(
    ax: plt.Axes,
    dates: list[datetime],
    vals: list[float],
    label: str,
    color: str,
    y_off_pt: float = 0.0,
) -> None:
    if not dates or not vals:
        return
    ax.annotate(
        label,
        xy=(dates[-1], vals[-1]),
        xytext=(8, y_off_pt),
        textcoords="offset points",
        fontsize=9,
        color=color,
        fontweight="600",
        va="center",
        ha="left",
        clip_on=False,
    )


def _plot_pair(
    fig: plt.Figure,
    ax: plt.Axes,
    fr: list[tuple[int, float | None]],
    peer: list[tuple[int, float | None]],
    peer_label: str,
    source: str,
    annotations: list[tuple[int, str, str]] | None,
) -> None:
    years_fr = [y for y, v in fr if v is not None]
    vals_fr = [v for _, v in fr if v is not None]
    years_p = [y for y, v in peer if v is not None]
    vals_p = [v for _, v in peer if v is not None]
    d_fr = _years_to_dates(years_fr)
    d_p = _years_to_dates(years_p)

    ax.plot(d_fr, vals_fr, color=TN_INK, linewidth=2.65, solid_capstyle="round", zorder=3)
    ax.plot(d_p, vals_p, color=TN_RED, linewidth=2.45, solid_capstyle="round", zorder=3)

    _end_label_line(ax, d_fr, vals_fr, "France", TN_INK, 0)
    _end_label_line(ax, d_p, vals_p, peer_label, TN_RED, 9)

    y_all = vals_fr + vals_p
    if y_all:
        lo, hi = min(y_all), max(y_all)
        pad = max((hi - lo) * 0.08, 0.35)
        ax.set_ylim(lo - pad, hi + pad)

    if years_fr or years_p:
        y_end = max(years_fr[-1] if years_fr else 0, years_p[-1] if years_p else 0)
        ax.set_xlim(datetime(2004, 7, 1), datetime(y_end + 1, 6, 30))

    ax.xaxis.set_major_locator(mdates.YearLocator(2))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    ax.set_ylabel("Pour 1 000 habitants", color=TN_MUTED, fontsize=10)
    ax.tick_params(axis="both", length=3, width=0.5, colors=TN_INK)
    _style_axes_area(ax)

    if annotations:
        for year, text, target in annotations:
            ys = vals_fr if target == "FR" else vals_p
            xs = years_fr if target == "FR" else years_p
            c = TN_INK if target == "FR" else TN_RED
            if year not in xs:
                continue
            yi = xs.index(year)
            vy = ys[yi]
            ax.annotate(
                text,
                xy=(datetime(year, 6, 1), vy),
                xytext=(8, 12 if target == "peer" else -16),
                textcoords="offset points",
                fontsize=7.8,
                color=c,
                arrowprops=dict(arrowstyle="-", color=c, lw=0.55, shrinkB=2),
            )

    _source_under_ax(fig, ax, source)


def _ylim_pad(vals: list[float], *, min_pad: float = 0.28, frac: float = 0.1) -> tuple[float, float]:
    if not vals:
        return -1.0, 3.5
    lo, hi = min(vals), max(vals)
    pad = max((hi - lo) * frac, min_pad)
    return lo - pad, hi + pad


def _plot_fr_fx_peer_stacked(
    ax_fr: plt.Axes,
    ax_peer: plt.Axes,
    fr: list[tuple[int, float | None]],
    fx: list[tuple[int, float | None]],
    peer: list[tuple[int, float | None]],
    peer_display: str,
    annotations: list[tuple[int, str, str]] | None,
    *,
    min_year: int | None = None,
    peer_color: str = TN_RED,
) -> None:
    """France (FR+FX) en haut à son échelle ; pays comparé en bas. Même axe X."""
    fr = _trim_from_year(fr, min_year)
    fx = _trim_from_year(fx, min_year)
    peer = _trim_from_year(peer, min_year)

    y_fr, v_fr, d_fr = _series_xy(fr)
    y_fx, v_fx, d_fx = _series_xy(fx)
    y_p, v_p, d_p = _series_xy(peer)
    peer_by_year = dict(zip(y_p, v_p))

    ax_fr.plot(d_fr, v_fr, color=TN_INK, linewidth=2.75, solid_capstyle="round", zorder=4)
    if d_fx:
        ax_fr.plot(
            d_fx,
            v_fx,
            color=TN_BLUE,
            linewidth=2.35,
            linestyle=(0, (4, 3)),
            solid_capstyle="round",
            zorder=3,
        )
    ax_peer.plot(d_p, v_p, color=peer_color, linewidth=2.55, solid_capstyle="round", zorder=3)

    _end_label_line(ax_fr, d_fr, v_fr, "France (FR)", TN_INK, 0)
    if d_fx:
        _end_label_line(ax_fr, d_fx, v_fx, "Métropole (FX)", TN_BLUE, -10)
    _end_label_line(ax_peer, d_p, v_p, peer_display, peer_color, 8)

    lo0, hi0 = _ylim_pad(v_fr + v_fx, min_pad=0.22, frac=0.11)
    ax_fr.set_ylim(lo0, hi0)
    lo1, hi1 = _ylim_pad(v_p, min_pad=0.45, frac=0.08)
    ax_peer.set_ylim(lo1, hi1)

    y_end = max(y_fr[-1] if y_fr else 0, y_fx[-1] if y_fx else 0, y_p[-1] if y_p else 0)
    x0 = datetime((min_year or 2004) - 1, 7, 1) if min_year else datetime(2004, 7, 1)
    x1 = datetime(y_end + 1, 6, 30)
    ax_fr.set_xlim(x0, x1)
    ax_peer.set_xlim(x0, x1)

    fmt = mticker.StrMethodFormatter("{x:.1f}")
    ax_fr.yaxis.set_major_formatter(fmt)
    ax_peer.yaxis.set_major_formatter(fmt)

    for ax in (ax_fr, ax_peer):
        ax.xaxis.set_major_locator(mdates.YearLocator(2))
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
        ax.set_ylabel("Pour 1 000 habitants", color=TN_MUTED, fontsize=10)
        ax.tick_params(axis="both", length=3, width=0.5, colors=TN_INK)
        _style_axes_area(ax)

    ax_fr.tick_params(axis="x", labelbottom=False)

    if annotations:
        for year, text, target in annotations:
            if target != "peer" or year not in peer_by_year:
                continue
            vy = peer_by_year[year]
            ax_peer.annotate(
                text,
                xy=(datetime(year, 6, 1), vy),
                xytext=(0, 12),
                textcoords="offset points",
                fontsize=8.5,
                color=peer_color,
                fontweight="600",
                ha="center",
                va="bottom",
            )


def _trim_from_year(
    s: list[tuple[int, float | None]], min_year: int | None
) -> list[tuple[int, float | None]]:
    if min_year is None:
        return s
    return [(y, v) for y, v in s if y >= min_year]


def _plot_fr_fx_peer(
    fig: plt.Figure,
    ax: plt.Axes,
    fr: list[tuple[int, float | None]],
    fx: list[tuple[int, float | None]],
    peer: list[tuple[int, float | None]],
    peer_display: str,
    source: str,
    annotations: list[tuple[int, str, str]] | None,
    *,
    min_year: int | None = None,
) -> None:
    fr = _trim_from_year(fr, min_year)
    fx = _trim_from_year(fx, min_year)
    peer = _trim_from_year(peer, min_year)

    y_fr, v_fr, d_fr = _series_xy(fr)
    y_fx, v_fx, d_fx = _series_xy(fx)
    y_p, v_p, d_p = _series_xy(peer)

    ax.plot(d_fr, v_fr, color=TN_INK, linewidth=2.75, solid_capstyle="round", zorder=4)
    ax.plot(
        d_fx,
        v_fx,
        color=TN_BLUE,
        linewidth=2.35,
        linestyle=(0, (4, 3)),
        solid_capstyle="round",
        zorder=3,
    )
    ax.plot(d_p, v_p, color=TN_RED, linewidth=2.5, solid_capstyle="round", zorder=3)

    _end_label_line(ax, d_fr, v_fr, "France (FR)", TN_INK, 0)
    _end_label_line(ax, d_fx, v_fx, "Métropole (FX)", TN_BLUE, -11)
    _end_label_line(ax, d_p, v_p, peer_display, TN_RED, 11)

    y_all = v_fr + v_fx + v_p
    if y_all:
        lo, hi = min(y_all), max(y_all)
        pad = max((hi - lo) * 0.08, 0.35)
        ax.set_ylim(lo - pad, hi + pad)

    y_end = max(
        y_fr[-1] if y_fr else 0,
        y_fx[-1] if y_fx else 0,
        y_p[-1] if y_p else 0,
    )
    x0 = datetime((min_year or 2004) - 1, 7, 1) if min_year else datetime(2004, 7, 1)
    ax.set_xlim(x0, datetime(y_end + 1, 6, 30))
    ax.xaxis.set_major_locator(mdates.YearLocator(2))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    ax.set_ylabel("Pour 1 000 habitants", color=TN_MUTED, fontsize=10)
    ax.tick_params(axis="both", length=3, width=0.5, colors=TN_INK)
    _style_axes_area(ax)

    series_map = {
        "FR": (y_fr, v_fr, TN_INK),
        "FX": (y_fx, v_fx, TN_BLUE),
        "peer": (y_p, v_p, TN_RED),
    }
    if annotations:
        for year, text, target in annotations:
            if target not in series_map:
                continue
            xs, ys, c = series_map[target]
            if year not in xs:
                continue
            yi = xs.index(year)
            vy = ys[yi]
            ax.annotate(
                text,
                xy=(datetime(year, 6, 1), vy),
                xytext=(8, 12 if target == "peer" else -14),
                textcoords="offset points",
                fontsize=7.8,
                color=c,
                arrowprops=dict(arrowstyle="-", color=c, lw=0.55, shrinkB=2),
            )

    _source_under_ax(fig, ax, source)


def _series_xy(
    s: list[tuple[int, float | None]],
) -> tuple[list[int], list[float], list[datetime]]:
    years = [y for y, v in s if v is not None]
    vals = [float(v) for _, v in s if v is not None]
    dates = _years_to_dates(years)
    return years, vals, dates


def _plot_fr_fx_it(
    fig: plt.Figure,
    ax: plt.Axes,
    fr: list[tuple[int, float | None]],
    fx: list[tuple[int, float | None]],
    it: list[tuple[int, float | None]],
    source: str,
    annotations: list[tuple[int, str, str]] | None,
) -> None:
    y_fr, v_fr, d_fr = _series_xy(fr)
    y_fx, v_fx, d_fx = _series_xy(fx)
    y_it, v_it, d_it = _series_xy(it)

    ax.plot(d_fr, v_fr, color=TN_INK, linewidth=2.75, solid_capstyle="round", zorder=4, label=DISPLAY_NAMES["FR"])
    ax.plot(
        d_fx,
        v_fx,
        color=TN_BLUE,
        linewidth=2.35,
        linestyle=(0, (4, 3)),
        solid_capstyle="round",
        zorder=3,
        label=DISPLAY_NAMES["FX"],
    )
    ax.plot(d_it, v_it, color=TN_RED, linewidth=2.5, solid_capstyle="round", zorder=3, label=DISPLAY_NAMES["IT"])

    _end_label_line(ax, d_fr, v_fr, "France (FR)", TN_INK, 0)
    _end_label_line(ax, d_fx, v_fx, "Métropole (FX)", TN_BLUE, -11)
    _end_label_line(ax, d_it, v_it, "Italie", TN_RED, 10)

    y_all = v_fr + v_fx + v_it
    if y_all:
        lo, hi = min(y_all), max(y_all)
        pad = max((hi - lo) * 0.08, 0.35)
        ax.set_ylim(lo - pad, hi + pad)

    y_end = max(
        y_fr[-1] if y_fr else 0,
        y_fx[-1] if y_fx else 0,
        y_it[-1] if y_it else 0,
    )
    ax.set_xlim(datetime(2004, 7, 1), datetime(y_end + 1, 6, 30))
    ax.xaxis.set_major_locator(mdates.YearLocator(2))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    ax.set_ylabel("Pour 1 000 habitants", color=TN_MUTED, fontsize=10)
    ax.tick_params(axis="both", length=3, width=0.5, colors=TN_INK)
    _style_axes_area(ax)

    series_map = {
        "FR": (y_fr, v_fr, TN_INK),
        "FX": (y_fx, v_fx, TN_BLUE),
        "IT": (y_it, v_it, TN_RED),
    }
    if annotations:
        for year, text, target in annotations:
            if target not in series_map:
                continue
            xs, ys, c = series_map[target]
            if year not in xs:
                continue
            yi = xs.index(year)
            vy = ys[yi]
            ax.annotate(
                text,
                xy=(datetime(year, 6, 1), vy),
                xytext=(8, 12 if target == "IT" else -14),
                textcoords="offset points",
                fontsize=7.8,
                color=c,
                arrowprops=dict(arrowstyle="-", color=c, lw=0.55, shrinkB=2),
            )

    _source_under_ax(fig, ax, source)


def _build_asylum_and_pop_params(geos: list[str], years: list[int]) -> tuple[list[tuple[str, str]], list[tuple[str, str]]]:
    asylum_p: list[tuple[str, str]] = [
        ("freq", "A"),
        ("citizen", "TOTAL"),
        ("applicant", "FRST"),
        ("sex", "T"),
        ("unit", "PER"),
        ("age", "TOTAL"),
    ]
    for g in geos:
        asylum_p.append(("geo", g))
    for y in years:
        asylum_p.append(("time", str(y)))

    pop_p: list[tuple[str, str]] = [("freq", "A"), ("age", "TOTAL"), ("sex", "T")]
    for g in geos:
        pop_p.append(("geo", g))
    for y in years:
        pop_p.append(("time", str(y)))
    return asylum_p, pop_p


def _latest_value(series: list[tuple[int, float | None]]) -> tuple[int, float] | None:
    for y, v in reversed(series):
        if v is not None:
            return (y, v)
    return None


def plot_asylum_lines(
    out: Path,
    rates: dict[str, list[tuple[int, float | None]]],
    highlight: list[str],
) -> None:
    fig, ax = plt.subplots(figsize=(FIG_WIDTH_IN, 6.2))
    ax.set_facecolor(TN_PAPER)
    fig.patch.set_facecolor(TN_PAPER)

    lead, sub = DS.TITLE_ASYLUM_LINES
    top_m = _figure_heading(fig, lead, sub)

    order = ["FR"] + [c for c in highlight if c != "FR" and c in rates]
    peer_idx = 0
    label_offsets = [0, 10, -9, 14, -13, 8]

    for idx, code in enumerate(order):
        if code not in rates:
            continue
        pts = rates[code]
        xs = [datetime(y, 1, 1) for y, v in pts if v is not None]
        ys = [v for _, v in pts if v is not None]
        if not xs:
            continue
        if code == "FR":
            col = TN_INK
            lw = 3.0
        else:
            col = COLOR_SERIES[peer_idx % len(COLOR_SERIES)]
            peer_idx += 1
            lw = 2.05
        ax.plot(xs, ys, color=col, linewidth=lw, solid_capstyle="round", zorder=3)
        off = label_offsets[idx % len(label_offsets)]
        _end_label_line(ax, xs, ys, DISPLAY_NAMES.get(code, code), col, off)

    ax.set_ylabel("Premières demandes pour 1 000 habitants", color=TN_MUTED, fontsize=10)
    ax.xaxis.set_major_locator(mdates.YearLocator(2))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    ax.tick_params(axis="both", length=3, width=0.5)
    _style_axes_area(ax)
    ax.set_xlim(datetime(2007, 6, 1), datetime(2025, 6, 30))

    _add_source_fig(fig, DS.ASYLUM_FOOTER_SHORT + " Détail méthodo : voir METHODOLOGIE_SERIES.txt.", y=0.018)
    fig.subplots_adjust(top=top_m, bottom=0.12, left=FIG_PAD_LEFT, right=0.97)
    fig.savefig(out / "figure_5_asile_premieres_demandes_pour_1000.png")
    plt.close(fig)


def plot_asylum_bars_latest(out: Path, rates: dict[str, list[tuple[int, float | None]]], codes: list[str]) -> None:
    rows: list[tuple[str, int, float]] = []
    for c in codes:
        if c not in rates:
            continue
        lv = _latest_value(rates[c])
        if lv:
            rows.append((DISPLAY_NAMES.get(c, c), lv[0], lv[1]))
    rows.sort(key=lambda x: x[2])
    if not rows:
        return

    fig, ax = plt.subplots(figsize=(FIG_WIDTH_IN, max(4.1, 0.5 * len(rows) + 2.1)))
    ax.set_facecolor(TN_PAPER)
    fig.patch.set_facecolor(TN_PAPER)

    lead, sub = DS.TITLE_ASYLUM_BARS
    top_m = _figure_heading(fig, lead, sub)

    labels = [f"{n} ({y})" for n, y, _ in rows]
    vals = [v for _, _, v in rows]
    y_pos = np.arange(len(rows))
    bar_cols = [TN_RED if n == "France" else TN_BAR_MUTED for n, _, _ in rows]

    ax.barh(y_pos, vals, height=0.62, color=bar_cols, linewidth=0, zorder=2)
    ax.set_yticks(y_pos, labels=labels, fontsize=9.5, color=TN_INK)
    ax.invert_yaxis()
    ax.set_xlabel("Pour 1 000 habitants", color=TN_MUTED, fontsize=10)
    ax.tick_params(axis="x", length=3, width=0.5)
    ax.grid(axis="x", color=TN_GRID, linewidth=0.6, zorder=0)
    ax.set_axisbelow(True)
    xmax = max(vals) * 1.2
    ax.set_xlim(0, xmax)
    for i, v in enumerate(vals):
        ax.text(
            min(v + xmax * 0.012, xmax * 0.97),
            i,
            f"{v:.2f}",
            va="center",
            fontsize=9.5,
            color=TN_RED,
            fontweight="600",
            ha="left",
        )
    _add_source_fig(fig, DS.ASYLUM_FOOTER_SHORT + " " + DS.ASYLUM_TABLE + " + demo_pjan.", y=0.02)
    fig.subplots_adjust(left=0.28, right=0.94, top=top_m, bottom=0.11)
    fig.savefig(out / "figure_6_asile_barres_derniere_annee.png")
    plt.close(fig)


def plot_key_dual_panel(
    out: Path,
    net_series: dict[str, list[tuple[int, float | None]]],
    asylum_rates: dict[str, list[tuple[int, float | None]]],
    codes: list[str],
) -> None:
    net_year_vals: list[tuple[str, int, float]] = []
    asy_year_vals: list[tuple[str, int, float]] = []
    for c in codes:
        if c not in net_series:
            continue
        n = _latest_value(net_series[c])
        a = _latest_value(asylum_rates.get(c, []))
        if n:
            net_year_vals.append((DISPLAY_NAMES.get(c, c), n[0], n[1]))
        if a:
            asy_year_vals.append((DISPLAY_NAMES.get(c, c), a[0], a[1]))

    net_year_vals.sort(key=lambda x: x[2])
    asy_year_vals.sort(key=lambda x: x[2])

    h = max(4.5, 0.42 * max(len(net_year_vals), len(asy_year_vals), 5) + 1.75)
    fig, (ax0, ax1) = plt.subplots(1, 2, figsize=(FIG_WIDTH_IN, h))
    fig.patch.set_facecolor(TN_PAPER)

    lead, sub = DS.TITLE_KEY_DUAL
    top_m = _figure_heading(fig, lead, sub)

    def draw_panel(ax, rows: list[tuple[str, int, float]], xlabel: str) -> None:
        ax.set_facecolor(TN_PAPER)
        labels = [f"{n} ({y})" for n, y, _ in rows]
        vals = [v for _, _, v in rows]
        yp = np.arange(len(rows))
        cols = [TN_RED if n == "France" else TN_BAR_OTHERS for n, _, _ in rows]
        ax.barh(yp, vals, height=0.6, color=cols, linewidth=0)
        ax.set_yticks(yp, labels=labels, fontsize=8.5, color=TN_INK)
        ax.invert_yaxis()
        ax.set_xlabel(xlabel, color=TN_MUTED, fontsize=9.5)
        ax.grid(axis="x", color=TN_GRID, linewidth=0.55)
        ax.set_axisbelow(True)
        topv = max(vals) if vals else 1
        xmax = topv * 1.24
        ax.set_xlim(0, xmax)
        for i, v in enumerate(vals):
            ax.text(
                min(v + xmax * 0.014, xmax * 0.96),
                i,
                f"{v:.2f}",
                va="center",
                fontsize=8.8,
                color=TN_RED,
                fontweight="600",
                ha="left",
            )

    fig.subplots_adjust(left=0.2, right=0.94, top=top_m, bottom=0.2, wspace=0.34)

    draw_panel(ax0, net_year_vals, "Pour 1 000 habitants")
    draw_panel(ax1, asy_year_vals, "Pour 1 000 habitants")

    ax0.set_title("Solde migratoire net", loc="left", fontsize=11.5, fontweight="700", color=TN_INK, pad=12, family=FONT_SERIF[0])
    ax1.set_title("Premières demandes d’asile", loc="left", fontsize=11.5, fontweight="700", color=TN_INK, pad=12, family=FONT_SERIF[0])

    _add_source_fig(
        fig,
        "Source : Eurostat — demo_gind (CNMIGRATRT) et migr_asyappctza + demo_pjan · années = dernière valeur disponible par série.",
        y=0.02,
    )
    fig.savefig(out / "figure_7_chiffres_cles_derniere_annee.png")
    plt.close(fig)


def plot_snapshot_latest(
    out: Path,
    series: dict[str, list[tuple[int, float | None]]],
    codes_order: list[str],
) -> None:
    rows: list[tuple[str, int, float]] = []
    for c in codes_order:
        if c not in series:
            continue
        lv = _latest_value(series[c])
        if lv:
            rows.append((DISPLAY_NAMES.get(c, c), lv[0], lv[1]))
    if len(rows) < 2:
        return

    rows.sort(key=lambda x: x[2])
    fig, ax = plt.subplots(figsize=(FIG_WIDTH_IN, max(4.2, 0.55 * len(rows) + 2.4)))
    ax.set_facecolor(TN_PAPER)
    fig.patch.set_facecolor(TN_PAPER)

    lead, sub = DS.TITLE_SNAPSHOT_2024
    top_m = _figure_heading(fig, lead, sub)

    labels = [f"{n} ({y})" for n, y, _ in rows]
    vals = [v for _, _, v in rows]
    y_pos = np.arange(len(rows))

    def bar_color(name: str) -> str:
        if "entière" in name:
            return TN_INK
        if "métropolitaine" in name.lower():
            return TN_BLUE
        if name == "Italie":
            return TN_RED
        if name == "Danemark":
            return TN_PLUM
        return TN_BAR_OTHERS

    cols = [bar_color(rows[i][0]) for i in range(len(rows))]

    ax.barh(y_pos, vals, height=0.58, color=cols, linewidth=0, zorder=2)
    ax.set_yticks(y_pos, labels=labels, fontsize=9.5, color=TN_INK)
    ax.invert_yaxis()
    ax.set_xlabel("Pour 1 000 habitants", color=TN_MUTED, fontsize=10)
    ax.tick_params(axis="x", length=3, width=0.5)
    ax.grid(axis="x", color=TN_GRID, linewidth=0.6, zorder=0)
    ax.set_axisbelow(True)
    xmax = max(vals) * 1.22
    ax.set_xlim(0, xmax)
    for i, v in enumerate(vals):
        ax.text(
            min(v + xmax * 0.01, xmax * 0.97),
            i,
            f"{v:.2f}",
            va="center",
            fontsize=9.5,
            color=TN_INK,
            fontweight="600",
            ha="left",
        )

    # Rapports vs FX et FR (Textes Terra Nova)
    def _val_for(sub: str) -> float | None:
        for n, _, vv in rows:
            if sub in n:
                return vv
        return None

    fr_v = _val_for("entière")
    fx_v = _val_for("métropolitaine")
    it_v = next((r[2] for r in rows if r[0] == "Italie"), None)
    dk_v = next((r[2] for r in rows if r[0] == "Danemark"), None)
    uk_v = next((r[2] for r in rows if r[0] == "Royaume-Uni"), None)
    ratio_bits: list[str] = []
    if fx_v and fx_v != 0:
        if it_v:
            ratio_bits.append(f"IT / FX ×{it_v / fx_v:.2f}")
        if dk_v:
            ratio_bits.append(f"DK / FX ×{dk_v / fx_v:.2f}")
        if uk_v:
            ratio_bits.append(f"UK / FX ×{uk_v / fx_v:.2f}")
    if fr_v and fr_v != 0:
        if it_v:
            ratio_bits.append(f"IT / FR ×{it_v / fr_v:.2f}")
        if dk_v:
            ratio_bits.append(f"DK / FR ×{dk_v / fr_v:.2f}")
        if uk_v:
            ratio_bits.append(f"UK / FR ×{uk_v / fr_v:.2f}")
    ratio_line = " · ".join(ratio_bits) if ratio_bits else ""

    _add_source_fig(
        fig,
        DS.MIGRATION_FOOTER + " " + UK_SOURCE_FOOTNOTE + (" · " + ratio_line if ratio_line else ""),
        y=0.018,
    )
    fig.subplots_adjust(left=0.32, right=0.94, top=top_m, bottom=0.12)
    fig.savefig(out / "figure_8_snapshot_derniere_annee.png")
    plt.close(fig)


def plot_eu_ranking_2024(out: Path, repo_root: Path) -> None:
    api_csv = out / "eu27_cnmigratrt_2024_from_api.csv"
    legacy_csv = repo_root / "estat_demo_gind_filtered_en (1).csv"
    eu_csv = api_csv if api_csv.exists() else legacy_csv
    panel = load_eu_panel_2024(eu_csv)
    if len(panel) < 5:
        return

    fig, ax = plt.subplots(figsize=(FIG_WIDTH_IN, max(5.5, 0.38 * len(panel) + 2.0)))
    ax.set_facecolor(TN_PAPER)
    fig.patch.set_facecolor(TN_PAPER)

    lead, sub = DS.TITLE_EU_RANK_2024
    top_m = _figure_heading(fig, lead, sub)

    labels = [f"{DISPLAY_NAMES.get(code, code)} ({code})" for code, _ in panel]
    vals = [v for _, v in panel]
    y_pos = np.arange(len(panel))
    bar_cols = [TN_RED if code == "FR" else TN_BAR_MUTED for code, _ in panel]

    ax.barh(y_pos, vals, height=0.55, color=bar_cols, linewidth=0, zorder=2)
    ax.set_yticks(y_pos, labels=labels, fontsize=8.2, color=TN_INK)
    ax.invert_yaxis()
    ax.set_xlabel("Solde migratoire net pour 1 000 habitants (2024)", color=TN_MUTED, fontsize=10)
    ax.tick_params(axis="x", length=3, width=0.5)
    ax.grid(axis="x", color=TN_GRID, linewidth=0.55, zorder=0)
    ax.set_axisbelow(True)
    xmax = max(vals) * 1.15 if vals else 1
    ax.set_xlim(0, xmax)
    for i, v in enumerate(vals):
        ax.text(
            min(v + xmax * 0.008, xmax * 0.98),
            i,
            f"{v:.2f}",
            va="center",
            fontsize=8.5,
            color=TN_INK,
            fontweight="600",
            ha="left",
        )

    src_note = (
        " API Eurostat (CNMIGRATRT, 2024), export automatique."
        if api_csv.exists()
        else " Fichier Eurostat multi-pays (export manuel), millésime 2024."
    )
    _add_source_fig(fig, DS.MIGRATION_FOOTER + src_note, y=0.02)
    fig.subplots_adjust(left=0.26, right=0.94, top=top_m, bottom=0.11)
    fig.savefig(out / "figure_9_classement_ue27_2024.png")
    plt.close(fig)


def main() -> None:
    apply_matplotlib_style(plt)
    root = Path(__file__).resolve().parent
    repo_root = root.parent
    out = root / "output"
    out.mkdir(exist_ok=True)
    cache = root / "cache"

    import sys as _sys

    _ons_json = cache / "ons" / "ons_ltim_net_ye_dec.json"
    if "--refresh" in _sys.argv or not _ons_json.exists():
        try:
            _ons_meta = refresh_ons_ltim(cache)
            print(
                f"ONS LTIM : {_ons_meta['years_parsed']} années « YE Dec » (All Nationalities) "
                f"téléchargées — {_ons_meta.get('xlsx_file', '')}."
            )
        except Exception as exc:
            print(f"Avertissement ONS (série UK 2012+ : repli sur valeurs embarquées) : {exc}")

    all_geos = sorted(set(["FR", "FX", "DK", "IT", "UK", "DE", "ES", "SE", "NL"]))
    # Cache versionné : inclut FX (métropole) ; renommer si les géographies changent pour forcer un re-téléchargement.
    full_series = load_or_fetch(all_geos, 2005, 2024, cache_json=cache / "demo_gind_cnmigratrt_full_v2_fx.json")
    apply_user_csv_overrides(full_series, 2005, 2024, default_user_csv_paths(repo_root))
    # Royaume-Uni : ONS uniquement pour les figures (pas les séries Eurostat UK du CSV).
    full_series["UK"] = uk_rate_per_1000_series(2005, 2024)

    series = {k: full_series[k] for k in ["FR", "FX", "DK", "IT", "UK"] if k in full_series}
    series_to_csv(out / "cnmigratrt_2005_2024_selection.csv", series)
    series_to_csv(out / "cnmigratrt_2005_2024_tous_pays.csv", full_series)

    (out / "METHODOLOGIE_SERIES.txt").write_text(
        f"{DS.MIGRATION_FOOTER}\n\n"
        f"France : FR (entière) et FX (métropole) — figure Italie. "
        f"Eurostat ne diffuse souvent plus FX pour CNMIGRATRT après ~2012 ; compléter avec un export national si besoin.\n"
        f"Fusion des CSV estat_demo_gind_filtered_en*.csv à la racine Migrations/ lorsqu’ils sont présents.\n\n"
        f"{UK_SOURCE_FOOTNOTE}\n\n{DS.ASYLUM_FOOTER_DETAIL}\n",
        encoding="utf-8",
    )

    # Figures 1 & 3 : FR + FX + pays pair (même logique que le site D3)
    triple_pairs: list[tuple[str, str, int | None]] = [
        ("DK", "figure_1_france_danemark.png", None),
        ("UK", "figure_3_france_royaume_uni.png", 2008),
    ]
    for peer_code, fname, min_y in triple_pairs:
        fr = series["FR"]
        fx = series["FX"]
        peer = series[peer_code]
        fig, (ax_top, ax_bot) = plt.subplots(
            2,
            1,
            figsize=(FIG_WIDTH_IN, 7.15),
            sharex=True,
            sharey=False,
            height_ratios=[1.02, 1.0],
        )
        ax_top.set_facecolor(TN_PAPER)
        ax_bot.set_facecolor(TN_PAPER)
        fig.patch.set_facecolor(TN_PAPER)
        lead, academic = DS.TITLES_PAIR[peer_code]
        top_m = _figure_heading(fig, lead, academic)
        _plot_fr_fx_peer_stacked(
            ax_top,
            ax_bot,
            fr,
            fx,
            peer,
            _peer_name(peer_code),
            ANNOTATIONS.get(peer_code),
            min_year=min_y,
            peer_color=TN_RED,
        )
        src_line = DS.MIGRATION_SOURCE_SHORT
        if peer_code == "UK":
            src_line += " · UK (solde long terme) : ONS."
        _add_source_fig(fig, src_line, y=0.018)
        fig.subplots_adjust(bottom=0.12, left=FIG_PAD_LEFT, right=0.97, top=top_m, hspace=0.16)
        fig.savefig(out / fname)
        plt.close(fig)

    # Figure 2 : Italie — FR + FX + Italie
    fig, ax = plt.subplots(figsize=(FIG_WIDTH_IN, 5.85))
    ax.set_facecolor(TN_PAPER)
    fig.patch.set_facecolor(TN_PAPER)
    lead, academic = DS.TITLES_PAIR["IT"]
    top_m = _figure_heading(fig, lead, academic)
    src_it = DS.MIGRATION_FOOTER + " Deux séries France : FR (entière) et FX (métropolitaine)."
    _plot_fr_fx_it(fig, ax, series["FR"], series["FX"], series["IT"], src_it, ANNOTATIONS_IT_TRIPLE)
    fig.subplots_adjust(bottom=0.2, left=FIG_PAD_LEFT, right=0.97, top=top_m)
    fig.savefig(out / "figure_2_france_italie.png")
    plt.close(fig)

    snap_codes = ["FR", "DK", "IT", "UK"]
    fx_lv = _latest_value(series.get("FX", []))
    if fx_lv and fx_lv[0] >= 2023:
        snap_codes = ["FR", "FX", "DK", "IT", "UK"]
    plot_snapshot_latest(out, series, snap_codes)
    write_eu27_cnmigratrt_2024_csv(out / "eu27_cnmigratrt_2024_from_api.csv", year=2024)
    plot_eu_ranking_2024(out, repo_root)

    eu_geos = ["FR", "DE", "ES", "SE", "NL", "IT", "DK"]
    payload_series = {k: full_series[k] for k in eu_geos if k in full_series}
    fig, axes = plt.subplots(2, 1, figsize=(FIG_WIDTH_IN, 7.6), sharex=True, sharey=False)
    fig.patch.set_facecolor(TN_PAPER)
    others = [g for g in eu_geos if g != "FR"]
    ax0, ax1 = axes
    ax0.set_facecolor(TN_PAPER)
    ax1.set_facecolor(TN_PAPER)

    lead, academic = DS.TITLE_EU_COMPARE
    top_m = _figure_heading(fig, lead, academic)

    fr_pts = payload_series["FR"]
    yf = [v for _, v in fr_pts if v is not None]
    xf = [datetime(y, 1, 1) for y, v in fr_pts if v is not None]
    ax0.plot(xf, yf, color=TN_INK, linewidth=3.0, zorder=4)
    _end_label_line(ax0, xf, yf, "France (FR)", TN_INK, 0)
    fx_full = full_series.get("FX", [])
    vals_top: list[float] = []
    for _, v in fr_pts:
        if v is not None:
            vals_top.append(float(v))
    y_fx, v_fx, d_fx = _series_xy(fx_full)
    for v in v_fx:
        vals_top.append(float(v))
    lo0, hi0 = _ylim_pad(vals_top, min_pad=0.3, frac=0.09)
    ax0.set_ylim(lo0, hi0)
    ax0.yaxis.set_major_formatter(mticker.StrMethodFormatter("{x:.1f}"))

    if d_fx:
        ax0.plot(
            d_fx,
            v_fx,
            color=TN_BLUE,
            linewidth=2.35,
            linestyle=(0, (4, 3)),
            solid_capstyle="round",
            zorder=3,
        )
        _end_label_line(ax0, d_fx, v_fx, "Métropole (FX)", TN_BLUE, -10)
    ax0.set_title(
        "France : FR et métropole (FX)",
        loc="left",
        fontsize=11.5,
        fontweight="700",
        color=TN_INK,
        pad=10,
        family=FONT_SERIF[0],
    )

    vals_bot: list[float] = []
    for _, v in fr_pts:
        if v is not None:
            vals_bot.append(float(v))
    for g in others:
        for _, v in payload_series[g]:
            if v is not None:
                vals_bot.append(float(v))
    lo1, hi1 = _ylim_pad(vals_bot, min_pad=0.5, frac=0.06)
    ax1.set_ylim(lo1, hi1)
    ax1.yaxis.set_major_formatter(mticker.StrMethodFormatter("{x:.1f}"))

    GRAY_PEER = "#B8B8B8"
    for g in others:
        pts = payload_series[g]
        x = [datetime(y, 1, 1) for y, v in pts if v is not None]
        y = [v for _, v in pts if v is not None]
        ax1.plot(x, y, linewidth=1.85, color=GRAY_PEER, zorder=2, solid_capstyle="round")

    xf_fr = [datetime(y, 1, 1) for y, v in fr_pts if v is not None]
    yf_fr = [v for _, v in fr_pts if v is not None]
    ax1.plot(xf_fr, yf_fr, linewidth=3.2, color=TN_BLUE, zorder=5, solid_capstyle="round")
    _end_label_line(ax1, xf_fr, yf_fr, "France (FR)", TN_BLUE, 0)

    ax1.set_title(
        "France (bleu) et six pays (gris), même échelle",
        loc="left",
        fontsize=11.5,
        fontweight="700",
        color=TN_INK,
        pad=10,
        family=FONT_SERIF[0],
    )

    ax0.tick_params(axis="x", labelbottom=False)
    for ax in axes:
        ax.set_ylabel("Pour 1 000 habitants", color=TN_MUTED, fontsize=10)
        ax.tick_params(axis="both", length=3, width=0.5)
        _style_axes_area(ax)

    ax1.xaxis.set_major_locator(mdates.YearLocator(2))
    ax1.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))

    _add_source_fig(fig, DS.MIGRATION_SOURCE_SHORT, y=0.022)
    fig.subplots_adjust(bottom=0.14, top=top_m, hspace=0.38, left=FIG_PAD_LEFT, right=0.97)
    fig.savefig(out / "figure_4_petit_multiple_ue.png")
    plt.close(fig)

    years_asy = list(range(2008, 2025))
    geos_asy = sorted(set(["FR", "DK", "IT", "DE", "ES", "SE", "NL", "AT", "BE"]))
    asylum_p, pop_p = _build_asylum_and_pop_params(geos_asy, years_asy)
    try:
        raw_asy = load_or_fetch_dataset("migr_asyappctza", asylum_p, cache / "migr_asyappctza.json")
        raw_pop = load_or_fetch_dataset("demo_pjan", pop_p, cache / "demo_pjan_asylum_geos.json")
        counts = parse_geo_time(raw_asy)
        pops = parse_geo_time(raw_pop)
        rates = per_1000_hab(counts, pops)
        series_to_csv(out / "asile_premieres_demandes_pour_1000.csv", rates)
        plot_asylum_lines(out, rates, highlight=["DE", "IT", "SE", "DK"])
        plot_asylum_bars_latest(out, rates, geos_asy)
        plot_key_dual_panel(out, full_series, rates, geos_asy)
    except Exception as exc:
        (out / "asile_erreur.txt").write_text(
            f"Import asile/population non généré : {exc!s}\nRelancer avec réseau pour remplir le cache.\n",
            encoding="utf-8",
        )

    try:
        import analyses_terra_nova

        analyses_terra_nova.main(out_dir=out, cache_dir=cache)
    except Exception as exc:
        print(f"Analyses Terra Nova : {exc}")


if __name__ == "__main__":
    import sys

    if "--refresh" in sys.argv:
        _root = Path(__file__).resolve().parent
        _cache = _root / "cache"
        for _p in sorted(_cache.glob("*.json")):
            _p.unlink(missing_ok=True)
            print("Cache effacé :", _p.name)
    main()
