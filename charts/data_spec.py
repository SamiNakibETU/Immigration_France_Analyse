"""
Spécification figée des séries Eurostat utilisées dans les exports.
Toute figure du dossier output/ doit rester alignée sur ces libellés.

Pourquoi les chiffres peuvent différer d’anciens graphiques Excel / INSEE :
- CNMIGRATRT = solde migratoire total + ajustement statistique (Eurostat), pas le « solde migratoire des seuls immigrés » INSEE.
- Les instituts nationaux publient parfois des millésimes ou définitions voisines mais non identiques.
- Royaume-Uni : les graphiques n’utilisent pas Eurostat pour le solde ; la série UK est construite
  à partir de publications ONS (voir `uk_ons_series.py`) avec dénominateur population documenté.
"""

from __future__ import annotations

# --- Solde migratoire ---
MIGRATION_TABLE = "demo_gind"
MIGRATION_INDICATOR_CODE = "CNMIGRATRT"
MIGRATION_INDICATOR_LABEL = (
    "taux brut de solde migratoire plus ajustement statistique pour 1 000 habitants"
)
MIGRATION_FOOTER = (
    f"Source : Eurostat — table {MIGRATION_TABLE}, indicateur {MIGRATION_INDICATOR_CODE} "
    f"({MIGRATION_INDICATOR_LABEL}). Série harmonisée ; révisions possibles."
)

# Pied de figure court (print & web) — le détail reste dans METHODOLOGIE_SERIES.txt
MIGRATION_SOURCE_SHORT = (
    f"Source : Eurostat — {MIGRATION_TABLE}, {MIGRATION_INDICATOR_CODE} (pour 1 000 hab.)."
)

# --- Asile ---
ASYLUM_TABLE = "migr_asyappctza"
ASYLUM_FOOTER_DETAIL = (
    "Eurostat migr_asyappctza : premières demandes (applicant=FRST, citizen=TOTAL, sex=T, age=TOTAL) ; "
    "dénominateur = population au 1er janvier (demo_pjan, age=TOTAL, sex=T). "
    "Taux annuels ; ne reflète pas les décisions finales."
)
ASYLUM_FOOTER_SHORT = (
    f"Source : Eurostat — {ASYLUM_TABLE} + demo_pjan (population 1er janv.)."
)

# --- Titres éditoriaux (lead) + sous-titres académiques ---
TITLES_PAIR: dict[str, tuple[str, str]] = {
    "DK": (
        "En 2024, le solde migratoire danois est près de deux fois supérieur au français",
        (
            "Solde net pour 1 000 habitants, 2013-2024 · même indicateur Eurostat (CNMIGRATRT) pour les deux pays · "
            "deux panneaux : France (FR + métropole FX) puis Danemark · "
            "FX : Eurostat souvent jusqu’en ~2012 seulement pour cet indicateur."
        ),
    ),
    "IT": (
        "Depuis 2021, l’Italie affiche un solde migratoire supérieur à celui de la France",
        (
            "Solde net pour 1 000 habitants, 2013-2024 · CNMIGRATRT (demo_gind) · "
            "FR = France entière, FX = métropole · Italie harmonisée."
        ),
    ),
    "UK": (
        "En 2022, le solde migratoire britannique a atteint un pic cinq fois supérieur au français",
        (
            "Solde net pour 1 000 habitants, 2013-2024 · France : Eurostat CNMIGRATRT · "
            "Royaume-Uni : ONS (séries non strictement comparables) · échelles Y distinctes."
        ),
    ),
}

TITLE_EU_COMPARE = (
    "En vingt ans, la France est passée sous la trajectoire de ses six principaux voisins européens",
    (
        "Solde migratoire net pour 1 000 habitants, 2005-2024 · Eurostat (CNMIGRATRT) · "
        "haut : France FR + FX · bas : France (bleu) avec DE, ES, SE, NL, IT, DK (gris), même échelle Y."
    ),
)

TITLE_ASYLUM_LINES = (
    "Demandes d’asile : la France se situe dans la moyenne basse (premières demandes / 1 000 hab.)",
    (
        "Premières demandes d’asile pour 1 000 habitants, 2008-2024 · "
        "Eurostat migr_asyappctza (FRST, citizen=TOTAL) · population au 1er janvier (demo_pjan)."
    ),
)

TITLE_ASYLUM_BARS = (
    "Premières demandes d’asile en 2024 : la France derrière l’Allemagne, l’Espagne ou l’Italie",
    (
        "Premières demandes pour 1 000 habitants, 2024 · "
        f"{ASYLUM_TABLE} + demo_pjan."
    ),
)

TITLE_KEY_DUAL = (
    "En 2024, la France combine un solde migratoire et des demandes d’asile inférieurs à beaucoup de voisins",
    (
        "Solde migratoire net et premières demandes d’asile pour 1 000 habitants · "
        "dernière année disponible par pays · demo_gind CNMIGRATRT · migr_asyappctza / demo_pjan."
    ),
)

TITLE_SNAPSHOT_2024 = (
    "2024 : même indicateur, écarts qui structurent le débat",
    (
        "Solde migratoire net pour 1 000 habitants · dernière année disponible par série · "
        "FR et FX (Eurostat) · DK, IT (Eurostat) · UK (ONS, voir méthodo) · "
        "rapports annotés vs France métropolitaine (FX) et vs France entière (FR)."
    ),
)

TITLE_EU_RANK_2024 = (
    "Solde migratoire en 2024 : la France dans le bas du classement (UE-27, CNMIGRATRT)",
    (
        "Solde migratoire net pour 1 000 habitants · 27 États membres, 2024 · "
        "données provisoires possibles (p) · hors Royaume-Uni."
    ),
)
