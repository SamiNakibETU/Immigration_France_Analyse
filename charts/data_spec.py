"""
Spécification figée des séries Eurostat utilisées dans les exports.
Toute figure du dossier output/ doit rester alignée sur ces libellés.

Pourquoi les chiffres peuvent différer d’anciens graphiques Excel / INSEE :
- CNMIGRATRT = solde migratoire + ajustement statistique, harmonisé Eurostat ;
  les instituts nationaux publient parfois des millésimes ou définitions voisines mais non identiques.
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
        "Des pics danois, une courbe française étroite",
        (
            "Solde migratoire net pour 1 000 habitants · Eurostat CNMIGRATRT · "
            "deux panneaux : France (FR + métropole FX) à son échelle, puis Danemark · "
            "FX : Eurostat seulement jusqu’en 2012 pour cet indicateur."
        ),
    ),
    "IT": (
        "L’Italie oscille fort ; la France reste dans une bande basse",
        (
            "CNMIGRATRT (demo_gind) · FR = France entière, FX = métropole seule · "
            "Attention : chez Eurostat, la série FX peut s’arrêter vers 2012 pour cet indicateur ; "
            "la courbe pointillée bleue ne couvre alors que le début de période · "
            "Italie harmonisée · France : flags 2014 (b), 2021–24 (p)."
        ),
    ),
    "UK": (
        "Le Royaume-Uni affiche un solde net nettement plus élevé que la France",
        (
            "France : Eurostat CNMIGRATRT · Royaume-Uni : solde net de long terme (ONS) · "
            "deux panneaux, échelles Y distinctes · FX métropole : Eurostat jusqu’en 2012."
        ),
    ),
}

TITLE_EU_COMPARE = (
    "France en bleu, six pays voisins en gris",
    (
        "CNMIGRATRT pour 1 000 habitants · haut : France FR + FX (axe Y adapté) · "
        "bas : France (bleu) avec DE, ES, SE, NL, IT, DK (gris), même échelle Y · Eurostat demo_gind."
    ),
)

TITLE_ASYLUM_LINES = (
    "Les chocs d’asile touchent surtout certains pays du nord ; la France reste modérée",
    (
        "Premières demandes pour 1 000 habitants · Eurostat migr_asyappctza (FRST, citizen=TOTAL, sex=T, age=TOTAL) · "
        "population au 1er janvier (demo_pjan) · séries annuelles (décisions finales non montrées)."
    ),
)

TITLE_ASYLUM_BARS = (
    "Dernière année : la France se situe dans le bas du classement relatif",
    (
        "Premières demandes d’asile pour 1 000 habitants · dernière année disponible par pays · "
        f"{ASYLUM_TABLE} + demo_pjan."
    ),
)

TITLE_KEY_DUAL = (
    "Solde migratoire net vs asile : la France combine un net modéré et un asile dans la moyenne basse",
    (
        "Dernière année disponible par pays pour chaque indicateur · "
        "gauche : demo_gind CNMIGRATRT · droite : migr_asyappctza / demo_pjan · "
        "les millésimes affichés peuvent coïncider (souvent 2024)."
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
    "Dans l’Union européenne, la France reste dans le bas du tableau",
    (
        "CNMIGRATRT 2024 · États membres UE-27 avec valeur publiée · "
        "données provisoires possibles (p) · hors Royaume-Uni."
    ),
)
