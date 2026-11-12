"""Tests du client OpenFisca (mode local).

Lancer avec le moteur in-process :
    OPENFISCA_MODE=local uv run python -m pytest tests/ -q

Ces tests vérifient que `construire_situation` + `calculer_irpp` produisent les
mêmes chiffres que ceux calés dans les cas YAML (`tests/irpp/`).
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest

# Force le moteur in-process (pas d'API HTTP pour les tests).
os.environ.setdefault("OPENFISCA_MODE", "local")

# Rendre le package de l'app importable.
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "app"))

from openfisca_client import calculer_irpp, construire_situation  # noqa: E402


def _irpp(annee, revenus, **kwargs):
    situation = construire_situation(annee=annee, revenus=revenus, **kwargs)
    return calculer_irpp(situation, annee=annee)


def test_salarie_celibataire_2024():
    r = _irpp(2024, {"salaire_imposable": 30000})
    assert r["rng"] == pytest.approx(28000, abs=0.01)
    assert r["irpp"] == pytest.approx(6140, abs=0.01)


def test_chef_famille_deux_enfants_2024():
    r = _irpp(2024, {"salaire_imposable": 30000}, chef_de_famille=True, nb_enf=2)
    assert r["revenu_net_imposable"] == pytest.approx(27500, abs=0.01)
    assert r["irpp"] == pytest.approx(6000, abs=0.01)


def test_bic_2024():
    r = _irpp(2024, {"bic_reel_res": 40000})
    assert r["irpp"] == pytest.approx(9900, abs=0.01)


def test_multi_revenus_2025():
    r = _irpp(2025, {"salaire_imposable": 20000, "pension_de_retraite": 10000, "capm_banq": 5000})
    assert r["rng"] == pytest.approx(30500, abs=0.01)
    assert r["irpp"] == pytest.approx(6415, abs=0.01)


def test_aucun_revenu_irpp_nul():
    r = _irpp(2024, {})
    assert (r["irpp"] or 0.0) == pytest.approx(0.0, abs=0.01)
    assert r["taux_moyen"] == 0.0


def test_deduction_reduit_impot():
    sans = _irpp(2024, {"salaire_imposable": 50000}, chef_de_famille=True)
    avec = _irpp(2024, {"salaire_imposable": 50000}, chef_de_famille=True,
                 deductions={"prime_assurance_vie": 2000})
    assert avec["irpp"] < sans["irpp"]
