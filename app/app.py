"""Simulateur d'impôt sur le revenu (IRPP, Tunisie) — interface Shiny.

Aucun calcul fiscal ici : la situation du foyer est envoyée à OpenFisca-Tunisia,
qui renvoie l'IRPP, la CSS et la décomposition. L'app ajoute des calculs dérivés
(taux marginal, simulation inverse, comparateur de barèmes) et des graphiques.

Lancer :
    openfisca serve -c openfisca_tunisia -p 5000
    shiny run app/app.py
"""

from __future__ import annotations

import httpx
from shiny import App, reactive, render, ui

from openfisca_client import (
    CATEGORIES_REVENUS,
    CATEGORIES_RNG,
    DEDUCTIONS_ANNUELLES,
    REVENUS_AVANCE,
    REVENUS_DETAILLE,
    REVENUS_RAPIDE,
    api_disponible,
    calculer_forfaitaire,
    calculer_irpp,
    calculer_plus_value_immobiliere,
    comparer_baremes,
    construire_situation,
    inverser_salaire,
    regularisation,
    taux_marginal,
)
from baremes import bareme_pour, cle_bareme
from graphs import figure_taux, figure_tranches
from i18n import (
    LANGUES,
    LIBELLES_CATEGORIES_RNG,
    LIBELLES_DEDUCTIONS,
    LIBELLES_REVENUS,
    t,
)

ANNEES = [str(a) for a in range(2020, 2026)]

BAREMES_AFFICHAGE = {
    "2017-2024": [
        ("0 → 5 000", "0 %"), ("5 000 → 20 000", "26 %"), ("20 000 → 30 000", "28 %"),
        ("30 000 → 50 000", "32 %"), ("> 50 000", "35 %"),
    ],
    "2025": [
        ("0 → 5 000", "0 %"), ("5 000 → 10 000", "15 %"), ("10 000 → 20 000", "25 %"),
        ("20 000 → 30 000", "30 %"), ("30 000 → 40 000", "33 %"), ("40 000 → 50 000", "36 %"),
        ("50 000 → 70 000", "38 %"), ("> 70 000", "40 %"),
    ],
}


# Revenus révélés progressivement : la case du groupe commande l'apparition du
# champ de montant correspondant (parcours en entonnoir).
REVENUS_AUTRES = {**REVENUS_DETAILLE, **REVENUS_AVANCE}


def _rev_cond(v, groupe):
    """Champ de montant pour `v`, visible seulement si `v` est coché dans `groupe`."""
    cond = f"input.{groupe} && input.{groupe}.indexOf('{v}') > -1"
    return ui.panel_conditional(
        cond,
        ui.input_numeric(f"rev_{v}", LIBELLES_REVENUS[v]["fr"], 0, min=0, step=500),
    )


app_ui = ui.page_sidebar(
    ui.sidebar(
        ui.input_select("lang", "Langue / اللغة", LANGUES, selected="fr"),
        ui.input_select("annee", "Année des revenus", ANNEES, selected="2024"),
        ui.hr(),
        # 1. Revenus : on coche ses sources, les montants apparaissent.
        ui.input_checkbox_group(
            "rev_courants", "Quels revenus avez-vous perçus ?",
            {v: LIBELLES_REVENUS[v]["fr"] for v in REVENUS_RAPIDE},
            selected=["salaire_imposable"],
        ),
        *[_rev_cond(v, "rev_courants") for v in REVENUS_RAPIDE],
        ui.input_checkbox("montrer_autres", "J'ai d'autres revenus…", False),
        ui.panel_conditional(
            "input.montrer_autres",
            ui.input_checkbox_group(
                "rev_autres", None,
                {v: LIBELLES_REVENUS[v]["fr"] for v in REVENUS_AUTRES},
            ),
            *[_rev_cond(v, "rev_autres") for v in REVENUS_AUTRES],
        ),
        ui.output_ui("aide_revenus_ui"),
        ui.hr(),
        # 2. Famille : chef de famille (toujours), personnes à charge (à la demande).
        ui.input_checkbox("chef_de_famille", "Chef de famille", False),
        ui.output_ui("aide_chef_ui"),
        ui.input_checkbox("a_enfants", "J'ai des personnes à charge", False),
        ui.panel_conditional(
            "input.a_enfants",
            ui.input_numeric("nb_enf", "Enfants à charge (≤ 4)", 0, min=0, max=10, step=1),
            ui.input_numeric("nb_enf_sup", "Étudiants sans bourse", 0, min=0, max=10, step=1),
            ui.input_numeric("nb_infirme", "Enfants handicapés", 0, min=0, max=10, step=1),
            ui.input_numeric("nb_parents", "Parents à charge", 0, min=0, max=4, step=1),
        ),
        ui.hr(),
        # 3. Déductions (à la demande).
        ui.input_checkbox("a_deductions", "J'ai des déductions à déclarer", False),
        ui.panel_conditional(
            "input.a_deductions",
            *[ui.input_numeric(f"ded_{v}", LIBELLES_DEDUCTIONS[v]["fr"], 0, min=0, step=100)
              for v in DEDUCTIONS_ANNUELLES],
        ),
        ui.hr(),
        # 4. Régularisation (à la demande).
        ui.input_checkbox("montrer_regul", "Calculer le solde (montant déjà prélevé)", False),
        ui.panel_conditional(
            "input.montrer_regul",
            ui.input_numeric("deja_preleve", "Déjà prélevé / acomptes (DT)", 0, min=0, step=100),
        ),
        ui.input_action_button("calculer", "Calculer l'impôt", class_="btn-primary"),
        width=360,
    ),
    ui.output_ui("statut_api"),
    ui.navset_tab(
        ui.nav_panel("Impôt dû · الضريبة", ui.output_ui("resultat_ui"), ui.output_ui("note"), value="impot"),
        ui.nav_panel("Graphiques · الرسوم", ui.output_ui("graphiques_ui"), value="graphiques"),
        ui.nav_panel("Comparateur · مقارنة", ui.output_ui("comparateur_ui"), value="comparateur"),
        ui.nav_panel("Autres calculs · أخرى", ui.output_ui("autres_ui"), value="autres"),
        ui.nav_panel("Barème · الجدول", ui.output_ui("bareme_ui"), value="bareme"),
        id="onglets",
    ),
    title="Simulateur d'impôt (IRPP) Tunisie",
)


def _fmt(montant) -> str:
    if montant is None:
        return "—"
    return f"{montant:,.3f} DT".replace(",", " ")


def _pct(x) -> str:
    return "—" if x is None else f"{x * 100:.2f} %"


def _ligne(libelle: str, valeur: str, *, fort: bool = False) -> ui.Tag:
    style = "font-weight:700;" if fort else ""
    return ui.tags.tr(
        ui.tags.td(libelle, style=style),
        # dir="ltr" : les nombres restent de gauche à droite même en mode arabe.
        ui.tags.td(valeur, dir="ltr", style=f"text-align:right;{style}"),
    )


def _message_erreur(err: Exception, lang: str) -> str:
    if isinstance(err, (httpx.TimeoutException, httpx.ConnectError)):
        return t("err_api", lang)
    return f"Erreur de calcul : {err}"


def server(input, output, session):

    # --- Traductions des libellés ------------------------------------------
    @reactive.effect
    def _langue():
        lang = str(input.lang())
        direction = "rtl" if lang == "ar" else "ltr"
        ui.insert_ui(
            ui.tags.script(
                f"document.documentElement.setAttribute('dir','{direction}');"
                f"document.documentElement.setAttribute('lang','{lang}');"
            ),
            selector="body", where="beforeEnd", immediate=True,
        )
        ui.update_select("annee", label=t("annee", lang))
        ui.update_checkbox_group(
            "rev_courants", label=t("q_revenus", lang),
            choices={v: LIBELLES_REVENUS[v][lang] for v in REVENUS_RAPIDE},
            selected=list(input.rev_courants() or []),
        )
        ui.update_checkbox_group(
            "rev_autres",
            choices={v: LIBELLES_REVENUS[v][lang] for v in REVENUS_AUTRES},
            selected=list(input.rev_autres() or []),
        )
        ui.update_checkbox("montrer_autres", label=t("q_autres_revenus", lang))
        for v in CATEGORIES_REVENUS:
            ui.update_numeric(f"rev_{v}", label=LIBELLES_REVENUS[v][lang])
        ui.update_checkbox("chef_de_famille", label=t("chef_famille", lang))
        ui.update_checkbox("a_enfants", label=t("q_enfants", lang))
        ui.update_numeric("nb_enf", label=t("nb_enf", lang))
        ui.update_numeric("nb_enf_sup", label=t("nb_enf_sup", lang))
        ui.update_numeric("nb_infirme", label=t("nb_infirme", lang))
        ui.update_numeric("nb_parents", label=t("nb_parents", lang))
        ui.update_checkbox("a_deductions", label=t("q_deductions", lang))
        for v in DEDUCTIONS_ANNUELLES:
            ui.update_numeric(f"ded_{v}", label=LIBELLES_DEDUCTIONS[v][lang])
        ui.update_checkbox("montrer_regul", label=t("q_regul", lang))
        ui.update_numeric("deja_preleve", label=t("deja_preleve", lang))
        ui.update_action_button("calculer", label=t("calculer", lang))

    @render.ui
    def aide_revenus_ui():
        return ui.tags.small(t("aide_revenus", str(input.lang())), class_="text-muted")

    @render.ui
    def aide_chef_ui():
        return ui.tags.small(t("aide_chef", str(input.lang())), class_="text-muted")

    @render.ui
    def statut_api():
        if api_disponible():
            return ui.TagList()
        return ui.div(ui.markdown("⚠️ " + t("err_api", str(input.lang()))), class_="alert alert-warning")

    # --- Entrées communes ---------------------------------------------------
    def _revenus():
        selected = set(input.rev_courants() or [])
        if input.montrer_autres():
            selected |= set(input.rev_autres() or [])
        return {v: (float(input[f"rev_{v}"]() or 0) if v in selected else 0.0)
                for v in CATEGORIES_REVENUS}

    def _famille():
        a_enf = bool(input.a_enfants())
        return dict(
            chef_de_famille=bool(input.chef_de_famille()),
            nb_enf=int(input.nb_enf() or 0) if a_enf else 0,
            nb_enf_sup=int(input.nb_enf_sup() or 0) if a_enf else 0,
            nb_infirme=int(input.nb_infirme() or 0) if a_enf else 0,
            nb_parents=int(input.nb_parents() or 0) if a_enf else 0,
        )

    def _deductions():
        if not input.a_deductions():
            return {}
        return {v: float(input[f"ded_{v}"]() or 0) for v in DEDUCTIONS_ANNUELLES}

    # --- Calcul principal ---------------------------------------------------
    @reactive.calc
    @reactive.event(input.calculer, ignore_none=False)
    def resultat():
        lang = str(input.lang())
        annee = int(input.annee())
        revenus = _revenus()
        if sum(revenus.values()) <= 0:
            return ("invalide", t("err_aucun_revenu", lang))
        famille = _famille()
        deductions = _deductions()
        situation = construire_situation(annee=annee, revenus=revenus, deductions=deductions, **famille)
        try:
            detail = calculer_irpp(situation, annee=annee)
            detail["taux_marginal"] = taux_marginal(revenus, famille, annee)
        except httpx.HTTPError as err:
            return ("erreur", _message_erreur(err, lang))
        detail["_annee"] = annee
        return ("ok", detail)

    @render.ui
    def resultat_ui():
        lang = str(input.lang())
        statut, c = resultat()
        if statut == "invalide":
            return ui.div(ui.markdown(f"⚠️ {c}"), class_="alert alert-warning")
        if statut == "erreur":
            return ui.div(ui.markdown(f"**{c}**"), class_="alert alert-danger")

        irpp, css = c.get("irpp"), c.get("contribution_sociale_solidarite")
        # Table principale
        principale = ui.tags.table(ui.tags.tbody(
            _ligne(t("rng", lang), _fmt(c.get("rng"))),
            _ligne(t("revenu_net_imposable", lang), _fmt(c.get("revenu_net_imposable"))),
            _ligne(t("irpp", lang), _fmt(irpp), fort=True),
            _ligne(t("css", lang), _fmt(css)),
            _ligne(t("total_du", lang), _fmt(c.get("total_irpp_css")), fort=True),
            _ligne(t("taux_moyen", lang), _pct(c.get("taux_moyen"))),
            _ligne(t("taux_marginal", lang), _pct(c.get("taux_marginal"))),
        ), class_="table")

        # Décomposition dépliable
        lignes_cat = [
            _ligne(" " + LIBELLES_CATEGORIES_RNG[cat][lang], _fmt(c.get(cat)))
            for cat in CATEGORIES_RNG if (c.get(cat) or 0) > 0
        ]
        decompo = ui.tags.details(
            ui.tags.summary(t("titre_decompo", lang)),
            ui.tags.table(ui.tags.tbody(
                ui.tags.tr(ui.tags.td(ui.tags.b(t("revenus_categoriels", lang)), colspan="2")),
                *lignes_cat,
                _ligne(t("deduction_famille", lang), _fmt(c.get("deduction_famille"))),
                _ligne(t("deductions_investissement", lang), _fmt(c.get("deductions_investissement"))),
                _ligne(t("impot_barème", lang), _fmt(c.get("impot_avant_avantages"))),
                _ligne(t("minimum_impot", lang), _fmt(c.get("minimum_impot"))),
            ), class_="table table-sm"),
        )
        minimum_alerte = (
            ui.div(ui.markdown("ℹ️ " + t("minimum_actif", lang)), class_="alert alert-info")
            if c.get("minimum_contraignant") else ui.TagList()
        )

        # Régularisation
        regul = ui.TagList()
        deja = float(input.deja_preleve() or 0) if input.montrer_regul() else 0.0
        if deja > 0:
            r = regularisation(c.get("total_irpp_css"), deja)
            if r["a_restituer"] > 0:
                regul = ui.div(ui.h5(t("titre_regul", lang)),
                               ui.markdown(f"**{t('solde_a_restituer', lang)} : "
                                           f"{_fmt(r['a_restituer'])}**"), class_="alert alert-success")
            else:
                regul = ui.div(ui.h5(t("titre_regul", lang)),
                               ui.markdown(f"**{t('solde_a_payer', lang)} : "
                                           f"{_fmt(r['a_payer'])}**"), class_="alert alert-warning")

        return ui.TagList(
            ui.h4(t("titre_resultat", lang)), principale,
            ui.tags.small(t("aide_marginal", lang)),
            minimum_alerte, decompo, regul,
        )

    @render.ui
    def note():
        lang = str(input.lang())
        return ui.TagList(ui.markdown(t("note_salaire_imposable", lang)),
                          ui.markdown(t("note_moteur", lang)))

    # --- Graphiques ---------------------------------------------------------
    @render.ui
    def graphiques_ui():
        lang = str(input.lang())
        statut, _ = resultat()
        if statut != "ok":
            return ui.div(ui.markdown("ℹ️ " + t("err_aucun_revenu", lang)), class_="alert alert-info")
        return ui.TagList(
            ui.h4(t("titre_graphiques", lang)),
            ui.output_plot("plot_tranches", height="330px"),
            ui.output_plot("plot_taux", height="330px"),
            ui.markdown(t("note_moteur", lang)),
        )

    @render.plot
    def plot_tranches():
        lang = str(input.lang())
        statut, c = resultat()
        if statut != "ok":
            return None
        rni = c.get("revenu_net_imposable") or 0
        return figure_tranches(rni, bareme_pour(c["_annee"]), titre=t("graph_tranches", lang), lang=lang)

    @render.plot
    def plot_taux():
        lang = str(input.lang())
        statut, c = resultat()
        if statut != "ok":
            return None
        rni = c.get("revenu_net_imposable") or 0
        return figure_taux(rni, bareme_pour(c["_annee"]), titre=t("graph_taux", lang),
                           lbl_marginal=t("lbl_marginal", lang), lbl_moyen=t("lbl_moyen", lang),
                           lbl_vous=t("lbl_vous", lang))

    # --- Comparateur de barèmes --------------------------------------------
    @render.ui
    def comparateur_ui():
        lang = str(input.lang())
        revenus = _revenus()
        if sum(revenus.values()) <= 0:
            return ui.div(ui.markdown("ℹ️ " + t("err_aucun_revenu", lang)), class_="alert alert-info")
        try:
            comp = comparer_baremes(revenus=revenus, famille=_famille(), deductions=_deductions())
        except httpx.HTTPError as err:
            return ui.div(ui.markdown(f"**{_message_erreur(err, lang)}**"), class_="alert alert-danger")
        a24, a25 = comp[2024], comp[2025]
        delta = (a25.get("total_irpp_css") or 0) - (a24.get("total_irpp_css") or 0)
        entete = ui.tags.thead(ui.tags.tr(
            ui.tags.th(""), ui.tags.th("2024", style="text-align:right;"),
            ui.tags.th("2025", style="text-align:right;"),
            ui.tags.th(t("variation", lang), style="text-align:right;"),
        ))
        def row(lib, k):
            v24, v25 = a24.get(k) or 0, a25.get(k) or 0
            return ui.tags.tr(
                ui.tags.td(lib),
                ui.tags.td(_fmt(v24), dir="ltr", style="text-align:right;"),
                ui.tags.td(_fmt(v25), dir="ltr", style="text-align:right;"),
                ui.tags.td(_fmt(v25 - v24), dir="ltr", style="text-align:right;"),
            )
        return ui.TagList(
            ui.h4(t("titre_comparateur", lang)),
            ui.markdown(t("intro_comparateur", lang)),
            ui.tags.table(entete, ui.tags.tbody(
                row(t("irpp", lang), "irpp"),
                row(t("css", lang), "contribution_sociale_solidarite"),
                row(t("total_du", lang), "total_irpp_css"),
            ), class_="table"),
            ui.div(ui.markdown(
                ("🟢 " if delta < 0 else "🔴 ") +
                f"**{t('variation', lang)} : {_fmt(delta)}**"),
                class_="alert " + ("alert-success" if delta < 0 else "alert-warning")),
        )

    # --- Autres calculs : forfaitaire, plus-value, inverse -----------------
    @render.ui
    def autres_ui():
        lang = str(input.lang())
        pv_inputs = ui.TagList(
            ui.input_numeric("pv_cession", t("pv_cession", lang), 0, min=0, step=5000),
            ui.input_numeric("pv_acquisition", t("pv_acquisition", lang), 0, min=0, step=5000),
            ui.input_numeric("pv_frais", t("pv_frais", lang), 0, min=0, step=1000),
            ui.input_numeric("pv_duree", t("pv_duree", lang), 1, min=0, max=60, step=1),
            ui.input_checkbox("pv_exoneree", t("pv_exoneree", lang), False),
            ui.input_action_button("calc_pv", t("calculer_pv", lang), class_="btn-primary"),
            ui.output_ui("pv_resultat"),
        )
        forf = ui.TagList(
            ui.input_numeric("ca_forfait", t("chiffre_affaires", lang), 0, min=0, step=5000),
            ui.input_action_button("calc_forf", t("calculer_forf", lang), class_="btn-primary"),
            ui.output_ui("forf_resultat"),
        )
        inv = ui.TagList(
            ui.input_numeric("net_cible", t("net_cible", lang), 24000, min=0, step=1000),
            ui.input_action_button("calc_inv", t("calculer_inverse", lang), class_="btn-primary"),
            ui.output_ui("inv_resultat"),
        )
        return ui.TagList(
            ui.card(ui.card_header(t("titre_forfaitaire", lang)), ui.markdown(t("intro_forfaitaire", lang)), forf),
            ui.card(ui.card_header(t("titre_plus_value", lang)), ui.markdown(t("intro_plus_value", lang)), pv_inputs),
            ui.card(ui.card_header(t("titre_inverse", lang)), ui.markdown(t("intro_inverse", lang)), inv),
        )

    @reactive.calc
    @reactive.event(input.calc_forf)
    def _forf():
        try:
            return ("ok", calculer_forfaitaire(float(input.ca_forfait() or 0), annee=int(input.annee())))
        except httpx.HTTPError as err:
            return ("erreur", _message_erreur(err, str(input.lang())))

    @render.ui
    def forf_resultat():
        lang = str(input.lang())
        statut, c = _forf()
        if statut != "ok":
            return ui.div(ui.markdown(f"**{c}**"), class_="alert alert-danger")
        return ui.tags.table(ui.tags.tbody(
            _ligne(t("impot_forfaitaire", lang), _fmt(c["impot_forfaitaire"]), fort=True),
        ), class_="table")

    @reactive.calc
    @reactive.event(input.calc_pv)
    def _pv():
        try:
            return ("ok", calculer_plus_value_immobiliere(
                prix_cession=float(input.pv_cession() or 0),
                prix_acquisition=float(input.pv_acquisition() or 0),
                frais=float(input.pv_frais() or 0),
                duree_detention=int(input.pv_duree() or 0),
                exoneree=bool(input.pv_exoneree()),
                annee=int(input.annee()),
            ))
        except httpx.HTTPError as err:
            return ("erreur", _message_erreur(err, str(input.lang())))

    @render.ui
    def pv_resultat():
        lang = str(input.lang())
        statut, c = _pv()
        if statut != "ok":
            return ui.div(ui.markdown(f"**{c}**"), class_="alert alert-danger")
        if c is None:
            return ui.div(ui.markdown("ℹ️ " + t("pv_indispo", lang)), class_="alert alert-info")
        return ui.tags.table(ui.tags.tbody(
            _ligne(t("pv_imposable", lang), _fmt(c["plus_value_imposable"])),
            _ligne(t("pv_impot", lang), _fmt(c["impot"]), fort=True),
        ), class_="table")

    @reactive.calc
    @reactive.event(input.calc_inv)
    def _inv():
        try:
            return ("ok", inverser_salaire(float(input.net_cible() or 0),
                                           annee=int(input.annee()), famille=_famille()))
        except httpx.HTTPError as err:
            return ("erreur", _message_erreur(err, str(input.lang())))

    @render.ui
    def inv_resultat():
        lang = str(input.lang())
        statut, c = _inv()
        if statut != "ok":
            return ui.div(ui.markdown(f"**{c}**"), class_="alert alert-danger")
        return ui.tags.table(ui.tags.tbody(
            _ligne(t("salaire_imposable_trouve", lang), _fmt(c.get("salaire_imposable")), fort=True),
            _ligne(t("irpp", lang), _fmt(c.get("irpp"))),
            _ligne(t("total_du", lang), _fmt(c.get("total_irpp_css"))),
        ), class_="table")

    # --- Barème -------------------------------------------------------------
    @render.ui
    def bareme_ui():
        lang = str(input.lang())
        annee = int(input.annee())
        cle = cle_bareme(annee)
        lignes = [ui.tags.tr(ui.tags.td(tr, dir="ltr"),
                             ui.tags.td(taux, dir="ltr", style="text-align:right;"))
                  for tr, taux in BAREMES_AFFICHAGE[cle]]
        entete = ui.tags.thead(ui.tags.tr(
            ui.tags.th(t("col_tranche", lang)), ui.tags.th(t("col_taux", lang), style="text-align:right;")))
        return ui.TagList(
            ui.h4(f"{t('titre_bareme', lang)} — {annee}"),
            ui.tags.table(entete, ui.tags.tbody(*lignes), class_="table"),
            ui.markdown(t("note_moteur", lang)),
        )


app = App(app_ui, server)
