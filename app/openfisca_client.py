"""Client de calcul OpenFisca-Tunisia pour le simulateur d'impôt (IRPP).

L'app Shiny ne contient aucune logique fiscale : elle construit une situation
(un foyer fiscal avec ses revenus catégoriels, sa situation de famille et ses
déductions) et demande l'IRPP annuel à OpenFisca-Tunisia. OpenFisca reste le
seul moteur de calcul.

Deux modes, selon la variable d'environnement OPENFISCA_MODE :
- "api" (défaut) : poste la situation à l'API web (openfisca serve). Pratique en
  développement local (API séparée sur OPENFISCA_API_URL).
- "local" : calcule en direct, dans le même process, via
  CountryTaxBenefitSystem. Utilisé en déploiement (shinyapps.io) où un seul
  service tourne : pas d'API HTTP séparée.

Les deux modes consomment le MÊME format de situation JSON ; SimulationBuilder
sait le lire directement.

En local (mode api), lancer l'API avec :
    openfisca serve -c openfisca_tunisia -p 5000
"""

from __future__ import annotations

import os

import httpx

# URL de l'API OpenFisca (mode "api"). Surchargée par OPENFISCA_API_URL.
API_URL = os.environ.get("OPENFISCA_API_URL", "http://localhost:5000")

# Mode de calcul : "api" (HTTP) ou "local" (moteur in-process).
MODE = os.environ.get("OPENFISCA_MODE", "api").lower()

# TaxBenefitSystem chargé paresseusement en mode local (coûteux à l'import).
_TBS = None


def _get_tbs():
    global _TBS
    if _TBS is None:
        from openfisca_tunisia import CountryTaxBenefitSystem

        _TBS = CountryTaxBenefitSystem()
    return _TBS


def _calculate_local(situation: dict) -> dict:
    """Calcule en direct via SimulationBuilder et renvoie le résultat au format API.

    Toutes les variables à `None` dans la situation sont calculées et remplies,
    pour chaque période demandée ; on imite la structure de réponse de l'API.
    """
    from openfisca_core.simulations import SimulationBuilder

    tbs = _get_tbs()
    builder = SimulationBuilder()
    simulation = builder.build_from_entities(tbs, situation)

    resultat = {k: {} for k in situation}
    for collection, entites in situation.items():
        for ident, variables in entites.items():
            resultat[collection][ident] = {}
            for variable, periodes in variables.items():
                if not isinstance(periodes, dict):
                    # champ non temporel (ex. liste de rôles) : recopié tel quel
                    resultat[collection][ident][variable] = periodes
                    continue
                resultat[collection][ident][variable] = {}
                for periode, valeur in periodes.items():
                    if valeur is None:
                        calcule = simulation.calculate(variable, periode)
                        valeur = float(calcule[0])
                    resultat[collection][ident][variable][periode] = valeur
    return resultat


def _calculate(situation: dict, *, timeout: float = 30.0) -> dict:
    """Route le calcul vers l'API HTTP ou le moteur local selon OPENFISCA_MODE."""
    if MODE == "local":
        return _calculate_local(situation)
    reponse = httpx.post(f"{API_URL}/calculate", json=situation, timeout=timeout)
    reponse.raise_for_status()
    return reponse.json()


# --- Catégories de revenus de l'IRPP tunisien -----------------------------
#
# Variable d'entrée (input) qui alimente chaque catégorie, l'entité porteuse et
# un libellé. Toutes sont saisies ANNUELLEMENT par l'utilisateur ; les variables
# mensuelles (salaire, pension) sont réparties sur l'année par OpenFisca
# (set_input_divide_by_period). Chaque catégorie agrège dans le revenu net
# global `rng` du foyer fiscal.
#
# Vérifié par le calcul (openfisca_tunisia, barème 2024/2025) : chaque variable
# ci-dessous, renseignée seule, fait bien varier `irpp`.
CATEGORIES_REVENUS = {
    "salaire_imposable": "Traitements et salaires (net imposable)",
    "pension_de_retraite": "Pensions et rentes viagères",
    "bic_reel_res": "Bénéfices industriels et commerciaux (BIC)",
    "bnc_reel_res_fiscal": "Bénéfices des professions non commerciales (BNC)",
    "beap_reel_res_fiscal": "Bénéfices agricoles et de pêche (BEAP)",
    "foncier_forfaitaire_batis_recettes": "Revenus fonciers (bâtis)",
    "capm_banq": "Revenus de capitaux mobiliers (intérêts)",
    "salaire_etranger": "Revenus de source étrangère (salaire)",
}

# Déductions communes sur le revenu global (variables annuelles, entité Individu).
DEDUCTIONS_ANNUELLES = {
    "prime_assurance_vie": "Primes d'assurance-vie",
    "interets_acquisition_logement": "Intérêts crédit logement (habitation principale)",
    "compte_epargne_en_actions": "Compte épargne en actions (CEA)",
    "compte_epargne_investissement": "Compte épargne investissement (CEI)",
    "pret_universitaire": "Remboursement de prêts universitaires",
    "dons": "Dons (fonds de solidarité, etc.)",
}

# Variables de sortie demandées au moteur (toutes au niveau du foyer fiscal).
VARIABLES_SORTIE = [
    "rng",
    "revenu_net_imposable",
    "irpp",
]


def construire_situation(
    *,
    annee: int,
    revenus: dict | None = None,
    chef_de_famille: bool = False,
    nb_enf: int = 0,
    nb_enf_sup: int = 0,
    nb_infirme: int = 0,
    nb_parents: int = 0,
    deductions: dict | None = None,
) -> dict:
    """Construit la situation JSON OpenFisca d'un foyer fiscal pour l'année donnée.

    `revenus` et `deductions` sont des dicts {variable: montant_annuel}. Les
    charges de famille sont des variables annuelles du foyer fiscal.
    """
    an = str(annee)
    revenus = revenus or {}
    deductions = deductions or {}

    individu: dict = {}
    for variable, montant in revenus.items():
        if montant:
            individu[variable] = {an: float(montant)}
    for variable, montant in deductions.items():
        if montant:
            individu[variable] = {an: float(montant)}

    foyer: dict = {
        "declarants": ["ind0"],
        "chef_de_famille": {an: chef_de_famille},
        "nb_enf": {an: nb_enf},
        "nb_enf_sup": {an: nb_enf_sup},
        "nb_infirme": {an: nb_infirme},
        "nb_parents": {an: nb_parents},
    }
    for variable in VARIABLES_SORTIE:
        foyer[variable] = {an: None}

    return {
        "individus": {"ind0": individu},
        "menages": {"m0": {"personne_de_reference": ["ind0"]}},
        "foyers_fiscaux": {"f0": foyer},
    }


def calculer_irpp(situation: dict, *, annee: int, timeout: float = 30.0) -> dict:
    """Poste la situation à l'API (ou calcule en local) et renvoie le détail IRPP.

    Renvoie un dict plat : rng (revenu net global), revenu_net_imposable, irpp,
    et taux_moyen (irpp / rng). Lève httpx.HTTPError si l'API est injoignable.
    """
    an = str(annee)
    data = _calculate(situation, timeout=timeout)
    foyer = data["foyers_fiscaux"]["f0"]

    resultat = {var: foyer.get(var, {}).get(an) for var in VARIABLES_SORTIE}
    rng = resultat.get("rng") or 0.0
    irpp = resultat.get("irpp") or 0.0
    resultat["taux_moyen"] = (irpp / rng) if rng > 0 else 0.0
    return resultat


def api_disponible(timeout: float = 3.0) -> bool:
    """Indique si le moteur est prêt (pour un message clair dans l'UI).

    En mode local, le moteur est toujours disponible (calcul in-process). En
    mode api, on teste la joignabilité de l'API.
    """
    if MODE == "local":
        return True
    try:
        reponse = httpx.get(f"{API_URL}/spec", timeout=timeout)
        return reponse.status_code == 200
    except httpx.HTTPError:
        return False
