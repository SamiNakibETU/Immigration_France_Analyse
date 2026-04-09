"""
Design tokens — charte proche La Grande Conversation / Terra Nova publication.
Encre #262626, fond dossier #F3ECE6, rouge #FF3F3F, bleu #2E879A, grille discrète.
"""

from __future__ import annotations

import textwrap

# --- La Grande Conversation (publication data) ---
TN_INK = "#262626"
TN_RED = "#FF3F3F"
TN_BLUE = "#2E879A"
TN_BLUE_LIGHT = "#3A9DB0"
TN_MUTED = "#5c5c5c"
TN_GRID = "#e8dfd6"
TN_PAPER = "#F3ECE6"
TN_WHITE = "#FFFFFF"
TN_PLUM = "#9D1453"
TN_CORAL = "#F99592"
TN_BAR_OTHERS = "#2E879A"
TN_BAR_MUTED = "#6b8f96"

COLOR_NOIR = TN_INK
COLOR_BLANC = TN_WHITE
COLOR_GRIS_CLAIR = TN_PAPER
COLOR_ACCENT = TN_RED
COLOR_RESIDENTS = TN_INK
COLOR_GRID = TN_GRID
COLOR_SOURCE = TN_MUTED

# Courbes comparaison (lisibles sur fond beige)
COLOR_SERIES: list[str] = [
    TN_RED,
    TN_BLUE,
    TN_PLUM,
    TN_CORAL,
    "#1a4d5c",
    TN_INK,
]

DPI = 120
FIG_WIDTH_PX = 1080
FIG_WIDTH_IN = FIG_WIDTH_PX / DPI
FIG_PAD_LEFT = 0.09

FONT_SERIF = ["Georgia", "Times New Roman", "DejaVu Serif", "Source Serif 4"]
FONT_SANS = ["Helvetica Neue", "Helvetica", "Arial", "DejaVu Sans", "Source Sans 3", "Inter"]


def apply_matplotlib_style(plt) -> None:
    from cycler import cycler
    import matplotlib as mpl

    plt.rcParams.update(
        {
            "figure.dpi": DPI,
            "savefig.dpi": DPI,
            "font.family": "sans-serif",
            "font.sans-serif": FONT_SANS,
            "font.serif": FONT_SERIF,
            "font.size": 10,
            "axes.titlesize": 12,
            "axes.titleweight": "600",
            "axes.labelsize": 10,
            "axes.labelcolor": TN_INK,
            "axes.edgecolor": TN_INK,
            "axes.linewidth": 0.55,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "axes.grid": True,
            "axes.grid.axis": "y",
            "grid.color": TN_GRID,
            "grid.linewidth": 0.55,
            "grid.alpha": 1.0,
            "xtick.color": TN_INK,
            "ytick.color": TN_INK,
            "text.color": TN_INK,
            "figure.facecolor": TN_PAPER,
            "axes.facecolor": TN_PAPER,
            "savefig.facecolor": TN_PAPER,
            "savefig.edgecolor": TN_PAPER,
            "savefig.bbox": "tight",
            "legend.frameon": False,
        }
    )
    mpl.rcParams["axes.prop_cycle"] = cycler(color=COLOR_SERIES)


def wrap_academic(text: str, width: int = 82) -> str:
    return "\n".join(textwrap.wrap(text, width=width, break_long_words=False, break_on_hyphens=False))


def header_top_margin(academic_sub: str, width: int = 82) -> float:
    n = max(1, len(textwrap.wrap(academic_sub, width=width)))
    return min(0.62, 0.78 - 0.021 * n)


def source_line(dataset: str, indicator: str, extra: str = "") -> str:
    base = f"Source : Eurostat — {dataset}, {indicator}."
    return f"{base} {extra}".strip()
