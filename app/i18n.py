"""Traductions français / arabe pour le simulateur d'impôt (IRPP).

Un dictionnaire plat clé -> {"fr": ..., "ar": ...}. La fonction `t(cle, lang)`
renvoie la chaîne traduite. Les nombres (montants) ne sont pas traduits.
"""

from __future__ import annotations

LANGUES = {"fr": "Français", "ar": "العربية"}

TRADUCTIONS: dict[str, dict[str, str]] = {
    # Titre et navigation
    "titre": {"fr": "Simulateur d'impôt (IRPP) Tunisie", "ar": "محاكي الضريبة على الدخل تونس"},
    "onglet_resultat": {"fr": "Impôt dû", "ar": "الضريبة المستحقة"},
    "onglet_bareme": {"fr": "Barème appliqué", "ar": "الجدول المطبق"},
    # Panneau latéral
    "langue": {"fr": "Langue / اللغة", "ar": "اللغة / Langue"},
    "annee": {"fr": "Année des revenus", "ar": "سنة المداخيل"},
    "revenus": {"fr": "Revenus annuels (DT/an)", "ar": "المداخيل السنوية (د.ت/سنة)"},
    "situation_familiale": {"fr": "Situation familiale", "ar": "الحالة العائلية"},
    "chef_famille": {"fr": "Chef de famille", "ar": "رب الأسرة"},
    "nb_enf": {"fr": "Enfants à charge (≤ 4)", "ar": "الأطفال المكفولون (≤ 4)"},
    "nb_enf_sup": {"fr": "Étudiants sans bourse", "ar": "طلبة بدون منحة"},
    "nb_infirme": {"fr": "Enfants handicapés", "ar": "أطفال ذوو إعاقة"},
    "nb_parents": {"fr": "Parents à charge", "ar": "الوالدون المكفولون"},
    "deductions": {"fr": "Déductions (DT/an)", "ar": "الطروحات (د.ت/سنة)"},
    "calculer": {"fr": "Calculer l'impôt", "ar": "احسب الضريبة"},
    # Résultats
    "titre_resultat": {"fr": "Impôt sur le revenu — foyer fiscal", "ar": "الضريبة على الدخل — المطرح الجبائي"},
    "rng": {"fr": "Revenu net global", "ar": "الدخل الصافي الجملي"},
    "revenu_net_imposable": {"fr": "Revenu net imposable", "ar": "الدخل الصافي الخاضع للضريبة"},
    "irpp": {"fr": "IRPP dû", "ar": "الضريبة المستحقة"},
    "taux_moyen": {"fr": "Taux moyen d'imposition", "ar": "نسبة الضريبة المتوسطة"},
    "detail_revenus": {"fr": "Détail des revenus saisis", "ar": "تفصيل المداخيل المدخلة"},
    # Barème
    "titre_bareme": {"fr": "Barème progressif de l'IRPP", "ar": "الجدول التصاعدي للضريبة"},
    "col_tranche": {"fr": "Tranche de revenu (DT)", "ar": "شريحة الدخل (د.ت)"},
    "col_taux": {"fr": "Taux", "ar": "النسبة"},
    # Messages
    "note_moteur": {
        "fr": "Calculé par le moteur **OpenFisca-Tunisia**. Le barème appliqué "
        "est celui des revenus de l'année choisie (loi de finances correspondante).",
        "ar": "محسوب بواسطة محرك **OpenFisca-Tunisia**. الجدول المطبق هو جدول "
        "مداخيل السنة المختارة (وفق قانون المالية المقابل).",
    },
    "note_salaire_imposable": {
        "fr": "Le « net imposable » des salaires = salaire après cotisations "
        "sociales et abattement de 10 % (plafonné). Pour partir du brut, utilisez "
        "le simulateur de paie.",
        "ar": "« الصافي الخاضع للضريبة » للأجور = الأجر بعد المساهمات الاجتماعية "
        "والطرح بنسبة 10٪ (بسقف). للانطلاق من الأجر الخام استعمل محاكي الأجور.",
    },
    "err_api": {
        "fr": "Impossible de joindre le moteur de calcul (API injoignable). "
        "Démarrez l'API ou utilisez le mode local (OPENFISCA_MODE=local).",
        "ar": "تعذّر الاتصال بمحرك الحساب. شغّل الواجهة البرمجية أو استعمل الوضع المحلي.",
    },
    "err_aucun_revenu": {
        "fr": "Saisissez au moins un revenu pour calculer l'impôt.",
        "ar": "أدخل مدخولاً واحداً على الأقل لحساب الضريبة.",
    },
}

# Libellés bilingues des catégories de revenus et déductions (clés = variables
# openfisca). Repris côté app pour traduire les champs de saisie.
LIBELLES_REVENUS = {
    "salaire_imposable": {"fr": "Traitements et salaires (net imposable)", "ar": "الأجور والمرتبات (صافٍ خاضع)"},
    "pension_de_retraite": {"fr": "Pensions et rentes viagères", "ar": "الجرايات والإيرادات العمرية"},
    "bic_reel_res": {"fr": "Bénéfices industriels et commerciaux (BIC)", "ar": "الأرباح الصناعية والتجارية"},
    "bnc_reel_res_fiscal": {"fr": "Bénéfices non commerciaux (BNC)", "ar": "الأرباح غير التجارية"},
    "beap_reel_res_fiscal": {"fr": "Bénéfices agricoles et de pêche", "ar": "الأرباح الفلاحية والصيد البحري"},
    "foncier_forfaitaire_batis_recettes": {"fr": "Revenus fonciers (bâtis)", "ar": "المداخيل العقارية (المبنية)"},
    "capm_banq": {"fr": "Revenus de capitaux mobiliers (intérêts)", "ar": "مداخيل رؤوس الأموال المنقولة (فوائد)"},
    "salaire_etranger": {"fr": "Revenus de source étrangère", "ar": "مداخيل من مصدر أجنبي"},
}
LIBELLES_DEDUCTIONS = {
    "prime_assurance_vie": {"fr": "Primes d'assurance-vie", "ar": "أقساط التأمين على الحياة"},
    "interets_acquisition_logement": {"fr": "Intérêts crédit logement", "ar": "فوائد قرض السكن"},
    "compte_epargne_en_actions": {"fr": "Compte épargne en actions (CEA)", "ar": "حساب الادخار في الأسهم"},
    "compte_epargne_investissement": {"fr": "Compte épargne investissement (CEI)", "ar": "حساب الادخار للاستثمار"},
    "pret_universitaire": {"fr": "Remboursement de prêts universitaires", "ar": "تسديد القروض الجامعية"},
    "dons": {"fr": "Dons", "ar": "التبرعات"},
}


def t(cle: str, lang: str) -> str:
    """Renvoie la traduction de `cle` dans la langue `lang` (repli sur le fr)."""
    entree = TRADUCTIONS.get(cle)
    if entree is None:
        return cle
    return entree.get(lang, entree.get("fr", cle))
