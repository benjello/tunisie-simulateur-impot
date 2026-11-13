"""Barèmes IRPP numériques (pour l'affichage et les graphiques pédagogiques).

Source : openfisca_tunisia/parameters/impot_revenu/bareme.yaml. Le barème sert
UNIQUEMENT à la décomposition illustrative par tranche et aux courbes de taux ;
le montant d'IRPP qui fait foi reste celui calculé par le moteur OpenFisca.

Chaque barème est une liste de tranches (seuil_bas, seuil_haut, taux) ; le
dernier seuil_haut vaut None (tranche supérieure ouverte).
"""

from __future__ import annotations

BAREMES_NUM = {
    # Barème « régime 2017 », applicable aux revenus 2017 à 2024.
    "2017-2024": [
        (0, 5000, 0.0),
        (5000, 20000, 0.26),
        (20000, 30000, 0.28),
        (30000, 50000, 0.32),
        (50000, None, 0.35),
    ],
    # Barème de la loi de finances 2025 (revenus 2025 et suivants).
    "2025": [
        (0, 5000, 0.0),
        (5000, 10000, 0.15),
        (10000, 20000, 0.25),
        (20000, 30000, 0.30),
        (30000, 40000, 0.33),
        (40000, 50000, 0.36),
        (50000, 70000, 0.38),
        (70000, None, 0.40),
    ],
}


def cle_bareme(annee: int) -> str:
    return "2025" if annee >= 2025 else "2017-2024"


def bareme_pour(annee: int) -> list:
    return BAREMES_NUM[cle_bareme(annee)]


def impot_par_tranche(revenu_imposable: float, bareme: list) -> list:
    """Décompose un revenu imposable : (libellé tranche, revenu dans la tranche,
    taux, impôt de la tranche) pour chaque tranche atteinte.
    """
    lignes = []
    for bas, haut, taux in bareme:
        if revenu_imposable <= bas:
            break
        plafond = revenu_imposable if haut is None else min(revenu_imposable, haut)
        assiette = max(0.0, plafond - bas)
        if assiette <= 0:
            continue
        borne = "∞" if haut is None else f"{haut:,.0f}".replace(",", " ")
        libelle = f"{bas:,.0f} – {borne}".replace(",", " ")
        lignes.append((libelle, assiette, taux, assiette * taux))
    return lignes


def taux_marginal_bareme(revenu_imposable: float, bareme: list) -> float:
    for bas, haut, taux in bareme:
        if haut is None or revenu_imposable <= haut:
            return taux
    return bareme[-1][2]
