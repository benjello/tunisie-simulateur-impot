"""Graphiques pédagogiques (matplotlib) pour le simulateur d'impôt.

Deux visualisations inspirées des meilleurs simulateurs internationaux :
- décomposition du revenu imposable par tranche du barème (barres) ;
- courbes du taux marginal et du taux moyen en fonction du revenu.

Illustratif : calculé depuis le barème numérique (app/baremes.py). Le montant
d'IRPP qui fait foi reste celui du moteur OpenFisca.
"""

from __future__ import annotations

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from baremes import impot_par_tranche, taux_marginal_bareme  # noqa: E402


def figure_tranches(revenu_imposable: float, bareme: list, *, titre: str, lang: str = "fr"):
    """Barres : part du revenu imposable dans chaque tranche et impôt associé."""
    lignes = impot_par_tranche(revenu_imposable, bareme)
    fig, ax = plt.subplots(figsize=(7, 3.6))
    if not lignes:
        ax.text(0.5, 0.5, "—", ha="center", va="center")
        ax.axis("off")
        return fig
    labels = [lig[0] for lig in lignes]
    revenus = [lig[1] for lig in lignes]
    impots = [lig[3] for lig in lignes]
    y = range(len(labels))
    ax.barh(y, revenus, color="#9ecae1", label="Revenu dans la tranche")
    ax.barh(y, impots, color="#08519c", label="Impôt de la tranche")
    ax.set_yticks(list(y))
    ax.set_yticklabels([f"{lab}  ({lig[2]*100:.0f}%)" for lab, lig in zip(labels, lignes)])
    ax.invert_yaxis()
    ax.set_xlabel("Dinars (DT)")
    ax.set_title(titre)
    ax.legend(loc="lower right", fontsize=8)
    for i, (rev, imp) in enumerate(zip(revenus, impots)):
        ax.text(rev, i, f" {rev:,.0f}".replace(",", " "), va="center", fontsize=7)
    fig.tight_layout()
    return fig


def figure_taux(revenu_imposable: float, bareme: list, *, titre: str,
                lbl_marginal: str, lbl_moyen: str, lbl_vous: str):
    """Courbes du taux marginal (en escalier) et du taux moyen vs revenu."""
    borne = bareme[-1][0]  # début de la dernière tranche
    revenu_max = max(revenu_imposable * 1.3, borne * 1.4, 60000)
    xs = [i for i in range(0, int(revenu_max) + 1, max(1, int(revenu_max // 200)))]
    marginal, moyen = [], []
    for x in xs:
        marginal.append(taux_marginal_bareme(x, bareme) * 100)
        impot = sum(lig[3] for lig in impot_par_tranche(x, bareme))
        moyen.append((impot / x * 100) if x > 0 else 0.0)
    fig, ax = plt.subplots(figsize=(7, 3.6))
    ax.plot(xs, marginal, color="#d94801", drawstyle="steps-post", label=lbl_marginal)
    ax.plot(xs, moyen, color="#08519c", label=lbl_moyen)
    if revenu_imposable > 0:
        ax.axvline(revenu_imposable, color="#555", linestyle="--", linewidth=1)
        taux_m = taux_marginal_bareme(revenu_imposable, bareme) * 100
        ax.annotate(f"{lbl_vous}\n{revenu_imposable:,.0f} DT".replace(",", " "),
                    xy=(revenu_imposable, taux_m), fontsize=8,
                    xytext=(6, -10), textcoords="offset points")
    ax.set_xlabel("Revenu imposable (DT)")
    ax.set_ylabel("Taux (%)")
    ax.set_title(titre)
    ax.legend(loc="lower right", fontsize=8)
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    return fig
