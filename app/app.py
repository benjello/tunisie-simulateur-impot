"""Simulateur d'impôt sur le revenu des personnes physiques (IRPP, Tunisie).

Interface Shiny for Python. Aucun calcul n'est fait ici : la situation du foyer
fiscal (revenus catégoriels, situation de famille, déductions) est envoyée à
OpenFisca-Tunisia, qui renvoie l'IRPP annuel dû.

Lancer l'API puis l'app, en local :
    openfisca serve -c openfisca_tunisia -p 5000
    shiny run app/app.py
"""

from __future__ import annotations

import httpx
from shiny import App, reactive, render, ui

from openfisca_client import (
    CATEGORIES_REVENUS,
    DEDUCTIONS_ANNUELLES,
    api_disponible,
    calculer_irpp,
    construire_situation,
)
from i18n import LANGUES, LIBELLES_DEDUCTIONS, LIBELLES_REVENUS, t

ANNEES = [str(a) for a in range(2020, 2026)]

# Barèmes IRPP par année des revenus (pour l'onglet pédagogique « Barème »).
# Source : loi de finances correspondante ; mêmes valeurs que
# openfisca_tunisia/parameters/impot_revenu/bareme.yaml.
BAREMES = {
    "2017-2024": [
        ("0 → 5 000", "0 %"),
        ("5 000 → 20 000", "26 %"),
        ("20 000 → 30 000", "28 %"),
        ("30 000 → 50 000", "32 %"),
        ("> 50 000", "35 %"),
    ],
    "2025": [
        ("0 → 5 000", "0 %"),
        ("5 000 → 10 000", "15 %"),
        ("10 000 → 20 000", "25 %"),
        ("20 000 → 30 000", "30 %"),
        ("30 000 → 40 000", "33 %"),
        ("40 000 → 50 000", "36 %"),
        ("50 000 → 70 000", "38 %"),
        ("> 70 000", "40 %"),
    ],
}


app_ui = ui.page_sidebar(
    ui.sidebar(
        ui.input_select("lang", "Langue / اللغة", LANGUES, selected="fr"),
        ui.input_select("annee", "Année des revenus", ANNEES, selected="2024"),
        ui.hr(),
        ui.h6("Revenus annuels (DT/an)", id="hdr_revenus"),
        *[
            ui.input_numeric(f"rev_{var}", libelle, 0, min=0, step=500)
            for var, libelle in CATEGORIES_REVENUS.items()
        ],
        ui.hr(),
        ui.h6("Situation familiale", id="hdr_famille"),
        ui.input_checkbox("chef_de_famille", "Chef de famille", False),
        ui.input_numeric("nb_enf", "Enfants à charge (≤ 4)", 0, min=0, max=10, step=1),
        ui.input_numeric("nb_enf_sup", "Étudiants sans bourse", 0, min=0, max=10, step=1),
        ui.input_numeric("nb_infirme", "Enfants handicapés", 0, min=0, max=10, step=1),
        ui.input_numeric("nb_parents", "Parents à charge", 0, min=0, max=4, step=1),
        ui.hr(),
        ui.h6("Déductions (DT/an)", id="hdr_deductions"),
        *[
            ui.input_numeric(f"ded_{var}", libelle, 0, min=0, step=100)
            for var, libelle in DEDUCTIONS_ANNUELLES.items()
        ],
        ui.input_action_button("calculer", "Calculer l'impôt", class_="btn-primary"),
        width=360,
    ),
    ui.output_ui("statut_api"),
    ui.navset_tab(
        ui.nav_panel(
            "Impôt dû",
            ui.output_ui("resultat_ui"),
            ui.output_ui("note"),
            value="tab_resultat",
        ),
        ui.nav_panel(
            "Barème appliqué",
            ui.output_ui("bareme_ui"),
            value="tab_bareme",
        ),
        id="onglets",
    ),
    title="Simulateur d'impôt (IRPP) Tunisie",
)


def _message_erreur(erreur: Exception, lang: str) -> str:
    if isinstance(erreur, (httpx.TimeoutException, httpx.ConnectError)):
        return t("err_api", lang)
    return f"Erreur de calcul : {erreur}"


def _fmt(montant) -> str:
    if montant is None:
        return "—"
    return f"{montant:,.3f} DT".replace(",", " ")


def _ligne(libelle: str, valeur: str, *, fort: bool = False) -> ui.Tag:
    style = "font-weight:700;" if fort else ""
    return ui.tags.tr(
        ui.tags.td(libelle, style=style),
        ui.tags.td(valeur, style=f"text-align:right;{style}"),
    )


def server(input, output, session):
    @reactive.effect
    def _appliquer_langue():
        lang = str(input.lang())
        direction = "rtl" if lang == "ar" else "ltr"
        ui.insert_ui(
            ui.tags.script(
                f"document.documentElement.setAttribute('dir', '{direction}');"
                f"document.documentElement.setAttribute('lang', '{lang}');"
            ),
            selector="body",
            where="beforeEnd",
            immediate=True,
        )
        ui.update_select("annee", label=t("annee", lang))
        for var in CATEGORIES_REVENUS:
            ui.update_numeric(f"rev_{var}", label=LIBELLES_REVENUS[var][lang])
        ui.update_checkbox("chef_de_famille", label=t("chef_famille", lang))
        ui.update_numeric("nb_enf", label=t("nb_enf", lang))
        ui.update_numeric("nb_enf_sup", label=t("nb_enf_sup", lang))
        ui.update_numeric("nb_infirme", label=t("nb_infirme", lang))
        ui.update_numeric("nb_parents", label=t("nb_parents", lang))
        for var in DEDUCTIONS_ANNUELLES:
            ui.update_numeric(f"ded_{var}", label=LIBELLES_DEDUCTIONS[var][lang])
        ui.update_action_button("calculer", label=t("calculer", lang))

    @render.ui
    def statut_api():
        if api_disponible():
            return ui.TagList()
        lang = str(input.lang())
        return ui.div(ui.markdown("⚠️ " + t("err_api", lang)), class_="alert alert-warning")

    @reactive.calc
    @reactive.event(input.calculer, ignore_none=False)
    def resultat():
        lang = str(input.lang())
        annee = int(input.annee())
        revenus = {
            var: float(input[f"rev_{var}"]() or 0) for var in CATEGORIES_REVENUS
        }
        deductions = {
            var: float(input[f"ded_{var}"]() or 0) for var in DEDUCTIONS_ANNUELLES
        }
        if sum(revenus.values()) <= 0:
            return ("invalide", t("err_aucun_revenu", lang))

        situation = construire_situation(
            annee=annee,
            revenus=revenus,
            chef_de_famille=bool(input.chef_de_famille()),
            nb_enf=int(input.nb_enf() or 0),
            nb_enf_sup=int(input.nb_enf_sup() or 0),
            nb_infirme=int(input.nb_infirme() or 0),
            nb_parents=int(input.nb_parents() or 0),
            deductions=deductions,
        )
        try:
            detail = calculer_irpp(situation, annee=annee)
        except httpx.HTTPError as erreur:
            return ("erreur", _message_erreur(erreur, lang))
        return ("ok", {"detail": detail, "revenus": revenus})

    @render.ui
    def resultat_ui():
        lang = str(input.lang())
        statut, contenu = resultat()
        if statut == "invalide":
            return ui.div(ui.markdown(f"⚠️ {contenu}"), class_="alert alert-warning")
        if statut == "erreur":
            return ui.div(ui.markdown(f"**{contenu}**"), class_="alert alert-danger")

        detail = contenu["detail"]
        revenus = contenu["revenus"]

        lignes_rev = [
            _ligne(f" {LIBELLES_REVENUS[var][lang]}", _fmt(montant))
            for var, montant in revenus.items()
            if montant
        ]
        detail_rev = ui.tags.details(
            ui.tags.summary(t("detail_revenus", lang)),
            ui.tags.table(ui.tags.tbody(*lignes_rev), class_="table table-sm"),
        )

        taux = detail.get("taux_moyen") or 0.0
        table = ui.tags.table(
            ui.tags.tbody(
                _ligne(t("rng", lang), _fmt(detail.get("rng"))),
                _ligne(t("revenu_net_imposable", lang), _fmt(detail.get("revenu_net_imposable"))),
                _ligne(t("irpp", lang), _fmt(detail.get("irpp")), fort=True),
                _ligne(t("taux_moyen", lang), f"{taux * 100:.2f} %"),
            ),
            class_="table",
        )
        return ui.TagList(
            ui.h4(t("titre_resultat", lang)),
            table,
            detail_rev,
        )

    @render.ui
    def note():
        lang = str(input.lang())
        return ui.TagList(
            ui.markdown(t("note_salaire_imposable", lang)),
            ui.markdown(t("note_moteur", lang)),
        )

    @render.ui
    def bareme_ui():
        lang = str(input.lang())
        annee = int(input.annee())
        cle = "2025" if annee >= 2025 else "2017-2024"
        lignes = [
            ui.tags.tr(ui.tags.td(tr), ui.tags.td(taux, style="text-align:right;"))
            for tr, taux in BAREMES[cle]
        ]
        entete = ui.tags.thead(
            ui.tags.tr(
                ui.tags.th(t("col_tranche", lang)),
                ui.tags.th(t("col_taux", lang), style="text-align:right;"),
            )
        )
        return ui.TagList(
            ui.h4(f"{t('titre_bareme', lang)} — {annee}"),
            ui.tags.table(entete, ui.tags.tbody(*lignes), class_="table"),
            ui.markdown(t("note_moteur", lang)),
        )


app = App(app_ui, server)
