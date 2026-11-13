"""Tests du client OpenFisca (mode local).

Lancer :
    OPENFISCA_MODE=local uv run python -m pytest tests/ -q

Vérifie que `openfisca_client` reproduit les chiffres du moteur et que les
calculs dérivés (marginal, inverse, comparateur, forfaitaire, plus-value,
régularisation) sont cohérents.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest

os.environ.setdefault("OPENFISCA_MODE", "local")
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "app"))

import openfisca_client as oc  # noqa: E402
import baremes  # noqa: E402

FAM0 = dict(chef_de_famille=False, nb_enf=0, nb_enf_sup=0, nb_infirme=0, nb_parents=0)


def _irpp(annee, revenus, deductions=None, **fam):
    f = {**FAM0, **fam}
    s = oc.construire_situation(annee=annee, revenus=revenus, deductions=deductions or {}, **f)
    return oc.calculer_irpp(s, annee=annee)


def test_decomposition_et_css_2024():
    r = _irpp(2024, {"salaire_imposable": 30000})
    assert r["rng"] == pytest.approx(28000, abs=0.01)
    assert r["tspr"] == pytest.approx(28000, abs=0.01)
    assert r["irpp"] == pytest.approx(6140, abs=0.01)
    assert r["contribution_sociale_solidarite"] == pytest.approx(140, abs=0.01)
    assert r["total_irpp_css"] == pytest.approx(6280, abs=0.01)


def test_css_exoneree_sous_seuil():
    r = _irpp(2024, {"salaire_imposable": 4000})
    assert (r["irpp"] or 0) == pytest.approx(0, abs=0.01)
    assert (r["contribution_sociale_solidarite"] or 0) == pytest.approx(0, abs=0.01)


def test_minimum_non_contraignant_sans_investissement():
    r = _irpp(2024, {"salaire_imposable": 30000})
    assert r["minimum_contraignant"] is False


def test_multi_categories_decomposition():
    r = _irpp(2024, {"salaire_imposable": 20000, "bic_reel_res": 10000, "capm_banq": 5000},
              chef_de_famille=True, nb_enf=2)
    assert r["bic"] == pytest.approx(10000, abs=0.01)
    assert r["rvcm"] == pytest.approx(5000, abs=0.01)
    assert r["deduction_famille"] == pytest.approx(500, abs=0.01)
    assert r["irpp"] == pytest.approx(7500, abs=0.01)


def test_taux_marginal_tranche_32():
    tm = oc.taux_marginal({"salaire_imposable": 40000}, FAM0, 2024)
    assert tm == pytest.approx(0.32, abs=0.005)


def test_inverse_salaire():
    r = oc.inverser_salaire(25000, annee=2024, famille=FAM0)
    assert r["net"] == pytest.approx(25000, abs=1.0)
    # vérifie la cohérence : net = rng - total dû
    assert (r["rng"] - r["total_irpp_css"]) == pytest.approx(25000, abs=1.0)


def test_comparateur_baremes():
    comp = oc.comparer_baremes(revenus={"salaire_imposable": 40000}, famille=FAM0, deductions={})
    assert comp[2024]["irpp"] == pytest.approx(9260, abs=0.01)
    assert comp[2025]["irpp"] == pytest.approx(8890, abs=0.01)


def test_forfaitaire_bic():
    r = oc.calculer_forfaitaire(60000, annee=2024)
    assert r["impot_forfaitaire"] == pytest.approx(6000, abs=0.01)


@pytest.mark.skipif(
    not oc.moteur_supporte("impot_plus_value_immobiliere"),
    reason="plus-values absentes de cette version d'openfisca-tunisia (nécessite une release incluant la fonctionnalité)",
)
def test_plus_value_immobiliere():
    r = oc.calculer_plus_value_immobiliere(
        prix_cession=300000, prix_acquisition=200000, duree_detention=3, annee=2024)
    assert r is not None
    assert r["plus_value_imposable"] == pytest.approx(40000, abs=0.01)
    assert r["impot"] == pytest.approx(6000, abs=0.01)


def test_regularisation():
    r = oc.regularisation(6000, 4000)
    assert r["a_payer"] == pytest.approx(2000, abs=0.01)
    assert r["a_restituer"] == 0.0


def test_bareme_par_tranche_somme_a_irpp():
    # La décomposition par tranche (illustrative) doit sommer à l'IRPP moteur.
    total = sum(l[3] for l in baremes.impot_par_tranche(28000, baremes.bareme_pour(2024)))
    assert total == pytest.approx(6140, abs=0.01)
