"""Client de calcul OpenFisca-Tunisia pour le simulateur d'impôt (IRPP).

L'app Shiny ne contient aucune logique fiscale : elle construit une situation de
foyer fiscal et demande à OpenFisca-Tunisia l'IRPP, la CSS, la décomposition du
calcul, et des calculs dérivés (taux marginal, simulation inverse, comparateur
de barèmes, régime forfaitaire, plus-value immobilière). OpenFisca reste le seul
moteur de calcul.

Deux modes (variable d'environnement OPENFISCA_MODE) :
- "api" (défaut) : poste la situation à l'API web (openfisca serve).
- "local" : calcule en direct via CountryTaxBenefitSystem (déploiement).
"""

from __future__ import annotations

import os

import httpx

API_URL = os.environ.get("OPENFISCA_API_URL", "http://localhost:5000")
MODE = os.environ.get("OPENFISCA_MODE", "api").lower()

_TBS = None


def _get_tbs():
    global _TBS
    if _TBS is None:
        from openfisca_tunisia import CountryTaxBenefitSystem

        _TBS = CountryTaxBenefitSystem()
    return _TBS


# --- Catégories de revenus (entrée individu, saisies annuellement) ----------
# Trois niveaux : rapide (grand public), détaillé, avancé. Toutes agrègent dans
# le revenu net global `rng` du foyer fiscal. Vérifiées par le calcul.
REVENUS_RAPIDE = {
    "salaire_imposable": "Traitements et salaires (net imposable)",
    "pension_de_retraite": "Pensions et rentes viagères",
}
REVENUS_DETAILLE = {
    "bic_reel_res": "Bénéfices industriels et commerciaux (BIC, réel)",
    "bnc_reel_res_fiscal": "Bénéfices non commerciaux (BNC, réel)",
    "beap_reel_res_fiscal": "Bénéfices agricoles et de pêche",
    "foncier_forfaitaire_batis_recettes": "Revenus fonciers (bâtis)",
    "capm_banq": "Capitaux mobiliers — intérêts bancaires",
    "salaire_etranger": "Revenus de source étrangère (salaire)",
}
REVENUS_AVANCE = {
    "capm_part": "Capitaux mobiliers — dividendes",
    "capm_oblig": "Capitaux mobiliers — obligations",
    "foncier_forfaitaire_non_batis_recettes": "Revenus fonciers (non bâtis)",
    "bnc_forfaitaire_recettes_brutes": "BNC — forfait d'assiette (recettes)",
    "pension_etranger_transferee": "Pension étrangère transférée en Tunisie",
    "pension_etranger_non_transferee": "Pension étrangère non transférée",
    "autres_revenus_etranger": "Autres revenus de source étrangère",
}
CATEGORIES_REVENUS = {**REVENUS_RAPIDE, **REVENUS_DETAILLE, **REVENUS_AVANCE}

# Déductions communes (entrée individu, annuelles). Seules celles dont l'effet
# est vérifié de façon générale sont exposées (les déductions conditionnelles —
# comptes spéciaux d'épargne, emprunts obligataires, rente — sont écartées).
DEDUCTIONS_ANNUELLES = {
    "prime_assurance_vie": "Primes d'assurance-vie",
    "interets_acquisition_logement": "Intérêts crédit logement (habitation principale)",
    "compte_epargne_en_actions": "Compte épargne en actions (CEA)",
    "compte_epargne_investissement": "Compte épargne investissement (CEI)",
    "pret_universitaire": "Remboursement de prêts universitaires",
    "dons": "Dons (fonds de solidarité, etc.)",
}

# Revenus par catégorie (sorties intermédiaires, foyer) pour la décomposition.
CATEGORIES_RNG = {
    "tspr": "Traitements, salaires, pensions et rentes",
    "bic": "Bénéfices industriels et commerciaux",
    "bnc": "Bénéfices non commerciaux",
    "beap": "Bénéfices agricoles et de pêche",
    "revenus_fonciers": "Revenus fonciers",
    "rvcm": "Revenus de capitaux mobiliers",
    "revenus_source_etrangere": "Revenus de source étrangère",
}

# Toutes les sorties demandées au moteur (niveau foyer fiscal).
VARIABLES_SORTIE = [
    "rng",
    "deduction_famille",
    "deductions_base",
    "deductions_investissement",
    "revenu_net_imposable",
    "assiette_avant_avantages",
    "impot_avant_avantages",
    "impot_revenu_brut",
    "minimum_impot",
    "irpp",
    "contribution_sociale_solidarite",
] + list(CATEGORIES_RNG)


# --- Moteur -----------------------------------------------------------------

def _calculate_local(situation: dict) -> dict:
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
                    resultat[collection][ident][variable] = periodes
                    continue
                resultat[collection][ident][variable] = {}
                for periode, valeur in periodes.items():
                    if valeur is None:
                        valeur = float(simulation.calculate(variable, periode)[0])
                    resultat[collection][ident][variable][periode] = valeur
    return resultat


def _calculate(situation: dict, *, timeout: float = 30.0) -> dict:
    if MODE == "local":
        return _calculate_local(situation)
    reponse = httpx.post(f"{API_URL}/calculate", json=situation, timeout=timeout)
    reponse.raise_for_status()
    return reponse.json()


def moteur_supporte(variable: str) -> bool:
    """Indique si le moteur connaît `variable` (mode local uniquement).

    En mode api, on ne peut pas l'introspecter simplement : on renvoie True et le
    calcul échouera proprement si la variable manque.
    """
    if MODE != "local":
        return True
    return variable in _get_tbs().variables


# --- Construction de situation + calcul IRPP --------------------------------

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
    sorties: list | None = None,
) -> dict:
    an = str(annee)
    revenus = revenus or {}
    deductions = deductions or {}
    sorties = sorties or VARIABLES_SORTIE

    individu: dict = {}
    for variable, montant in {**revenus, **deductions}.items():
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
    for variable in sorties:
        foyer[variable] = {an: None}

    return {
        "individus": {"ind0": individu},
        "menages": {"m0": {"personne_de_reference": ["ind0"]}},
        "foyers_fiscaux": {"f0": foyer},
    }


def calculer_irpp(situation: dict, *, annee: int, timeout: float = 30.0) -> dict:
    """Renvoie la décomposition complète : revenus par catégorie, déductions,
    assiette, impôt barème, minimum, IRPP, CSS, total, taux moyen.
    """
    an = str(annee)
    data = _calculate(situation, timeout=timeout)
    foyer = data["foyers_fiscaux"]["f0"]
    res = {var: foyer.get(var, {}).get(an) for var in VARIABLES_SORTIE}

    irpp = res.get("irpp") or 0.0
    css = res.get("contribution_sociale_solidarite") or 0.0
    rng = res.get("rng") or 0.0
    res["total_irpp_css"] = irpp + css
    res["taux_moyen"] = (irpp / rng) if rng > 0 else 0.0
    res["taux_moyen_avec_css"] = ((irpp + css) / rng) if rng > 0 else 0.0
    # Le minimum d'impôt (art. 12 bis) ne « mord » que s'il dépasse l'impôt
    # barème après avantages : on signale alors qu'il est contraignant.
    res["minimum_contraignant"] = (res.get("minimum_impot") or 0.0) > (irpp + 0.01)
    return res


def _irpp_simple(revenus, famille, annee):
    """IRPP (seul) pour un jeu de revenus — utilitaire pour marginal/inverse."""
    situation = construire_situation(
        annee=annee, revenus=revenus, deductions={}, sorties=["irpp", "rng"], **famille
    )
    an = str(annee)
    data = _calculate(situation)
    foyer = data["foyers_fiscaux"]["f0"]
    return (foyer.get("irpp", {}).get(an) or 0.0, foyer.get("rng", {}).get(an) or 0.0)


def taux_marginal(revenus: dict, famille: dict, annee: int, *, pas: float = 100.0) -> float:
    """Taux marginal d'imposition : ΔIRPP / ΔRNG pour un supplément de revenu.

    On augmente le premier revenu non nul (à défaut le salaire) de `pas` dinars
    et on mesure la variation d'IRPP rapportée à la variation de RNG, ce qui
    donne le taux de la tranche marginale indépendamment des abattements.
    """
    revenus = {k: v for k, v in revenus.items() if v}
    cible = next(iter(revenus), "salaire_imposable")
    base_irpp, base_rng = _irpp_simple(revenus, famille, annee)
    hausse = dict(revenus)
    hausse[cible] = (hausse.get(cible) or 0.0) + pas
    haut_irpp, haut_rng = _irpp_simple(hausse, famille, annee)
    d_rng = haut_rng - base_rng
    return (haut_irpp - base_irpp) / d_rng if d_rng > 0 else 0.0


def inverser_salaire(
    net_cible: float, *, annee: int, famille: dict, tolerance: float = 0.01, max_iter: int = 60
) -> dict:
    """Trouve le salaire imposable dont le revenu net après IRPP+CSS = net_cible.

    Dichotomie sur le seul salaire imposable (autres revenus supposés nuls).
    """
    def net_pour(salaire: float) -> dict:
        situation = construire_situation(
            annee=annee, revenus={"salaire_imposable": salaire}, **famille
        )
        res = calculer_irpp(situation, annee=annee)
        res["salaire_imposable"] = salaire
        res["net"] = (res.get("rng") or 0.0) - (res.get("total_irpp_css") or 0.0)
        return res

    if net_cible <= 0:
        return net_pour(0.0)
    bas, haut = 0.0, max(net_cible, 1.0) * 1.6
    res_haut = net_pour(haut)
    gardes = 0
    while res_haut["net"] < net_cible and gardes < 40:
        haut *= 1.5
        res_haut = net_pour(haut)
        gardes += 1
    dernier = res_haut
    for _ in range(max_iter):
        milieu = (bas + haut) / 2.0
        dernier = net_pour(milieu)
        if abs(dernier["net"] - net_cible) <= tolerance:
            break
        if dernier["net"] < net_cible:
            bas = milieu
        else:
            haut = milieu
    return dernier


def comparer_baremes(
    *, revenus: dict, famille: dict, deductions: dict, annees: tuple = (2024, 2025)
) -> dict:
    """Compare l'IRPP d'un même foyer sous les barèmes de deux années."""
    sortie = {}
    for annee in annees:
        situation = construire_situation(
            annee=annee, revenus=revenus, deductions=deductions, **famille
        )
        sortie[annee] = calculer_irpp(situation, annee=annee)
    return sortie


def calculer_forfaitaire(chiffre_affaires: float, *, annee: int) -> dict:
    """Impôt du régime forfaitaire BIC (libératoire) pour un chiffre d'affaires."""
    an = str(annee)
    situation = {
        "individus": {"ind0": {}},
        "menages": {"m0": {"personne_de_reference": ["ind0"]}},
        "foyers_fiscaux": {
            "f0": {
                "declarants": ["ind0"],
                "chiffre_affaires_soumis_au_forfait": {an: float(chiffre_affaires)},
                "impot_regime_forfaitaire_du": {an: None},
            }
        },
    }
    data = _calculate(situation)
    impot = data["foyers_fiscaux"]["f0"].get("impot_regime_forfaitaire_du", {}).get(an)
    return {"chiffre_affaires": chiffre_affaires, "impot_forfaitaire": impot}


def calculer_plus_value_immobiliere(
    *, prix_cession: float, prix_acquisition: float, duree_detention: int,
    frais: float = 0.0, exoneree: bool = False, annee: int,
) -> dict | None:
    """Impôt sur la plus-value immobilière (art. 27-28 CIRPP).

    Renvoie None si le moteur ne connaît pas la variable (openfisca-tunisia trop
    ancien : la fonctionnalité nécessite une version incluant les plus-values).
    """
    if not moteur_supporte("impot_plus_value_immobiliere"):
        return None
    an = str(annee)
    foyer = {
        "declarants": ["ind0"],
        "plus_value_immobiliere_prix_cession": {an: float(prix_cession)},
        "plus_value_immobiliere_prix_acquisition": {an: float(prix_acquisition)},
        "plus_value_immobiliere_frais": {an: float(frais)},
        "plus_value_immobiliere_duree_detention": {an: int(duree_detention)},
        "plus_value_immobiliere_exoneree": {an: bool(exoneree)},
        "plus_value_immobiliere_imposable": {an: None},
        "impot_plus_value_immobiliere": {an: None},
    }
    situation = {
        "individus": {"ind0": {}},
        "menages": {"m0": {"personne_de_reference": ["ind0"]}},
        "foyers_fiscaux": {"f0": foyer},
    }
    try:
        data = _calculate(situation)
    except httpx.HTTPError:
        return None
    f = data["foyers_fiscaux"]["f0"]
    return {
        "plus_value_imposable": f.get("plus_value_immobiliere_imposable", {}).get(an),
        "impot": f.get("impot_plus_value_immobiliere", {}).get(an),
    }


def regularisation(total_du: float, deja_preleve: float) -> dict:
    """Solde de régularisation annuelle : total dû (IRPP+CSS) − déjà prélevé."""
    solde = (total_du or 0.0) - (deja_preleve or 0.0)
    return {"solde": solde, "a_payer": max(solde, 0.0), "a_restituer": max(-solde, 0.0)}


def api_disponible(timeout: float = 3.0) -> bool:
    if MODE == "local":
        return True
    try:
        return httpx.get(f"{API_URL}/spec", timeout=timeout).status_code == 200
    except httpx.HTTPError:
        return False
