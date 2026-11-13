"""Traductions français / arabe pour le simulateur d'impôt (IRPP).

Dictionnaire plat clé -> {"fr": ..., "ar": ...}. `t(cle, lang)` renvoie la
traduction (repli sur le français). Les montants ne sont pas traduits.
"""

from __future__ import annotations

LANGUES = {"fr": "Français", "ar": "العربية"}


def _b(fr, ar):
    return {"fr": fr, "ar": ar}


TRADUCTIONS = {
    "titre": _b("Simulateur d'impôt (IRPP) Tunisie", "محاكي الضريبة على الدخل تونس"),
    # Onglets
    "onglet_impot": _b("Impôt dû", "الضريبة المستحقة"),
    "onglet_graphiques": _b("Graphiques", "الرسوم البيانية"),
    "onglet_comparateur": _b("Comparateur de barèmes", "مقارنة الجداول"),
    "onglet_autres": _b("Autres calculs", "حسابات أخرى"),
    "onglet_bareme": _b("Barème", "الجدول"),
    # Panneau latéral
    "annee": _b("Année des revenus", "سنة المداخيل"),
    "mode": _b("Niveau de détail", "مستوى التفصيل"),
    "mode_rapide": _b("Rapide", "سريع"),
    "mode_detaille": _b("Détaillé", "مفصّل"),
    "mode_avance": _b("Avancé", "متقدّم"),
    "revenus": _b("Revenus annuels (DT/an)", "المداخيل السنوية (د.ت/سنة)"),
    # Parcours en entonnoir (divulgation progressive)
    "q_revenus": _b("Quels revenus avez-vous perçus ?", "ما هي المداخيل التي حصّلتها ؟"),
    "aide_revenus": _b(
        "Cochez vos sources de revenu ; un champ de montant apparaîtra pour chacune (montants annuels nets imposables).",
        "اختر مصادر دخلك ؛ سيظهر حقل مبلغ لكل واحد (مبالغ سنوية صافية خاضعة).",
    ),
    "q_autres_revenus": _b(
        "J'ai d'autres revenus (commerce, profession, agricole, foncier, capitaux, étranger…)",
        "لديّ مداخيل أخرى (تجارة، مهنة، فلاحة، عقار، رؤوس أموال، أجنبي…)",
    ),
    "q_enfants": _b("J'ai des personnes à charge", "لديّ أشخاص مكفولون"),
    "q_deductions": _b("J'ai des déductions à déclarer", "لديّ طروحات للتصريح بها"),
    "q_regul": _b("Calculer le solde (montant déjà prélevé)", "حساب الرصيد (المبلغ المقتطع مسبقا)"),
    "aide_chef": _b(
        "Époux ; personne divorcée ou veuve ayant des enfants à charge. L'épouse peut l'être si le mari est sans revenu.",
        "الزوج ؛ المطلّق أو الأرمل الذي له أطفال مكفولون. يمكن أن تكون الزوجة كذلك إذا كان الزوج دون دخل.",
    ),
    "situation_familiale": _b("Situation familiale", "الحالة العائلية"),
    "chef_famille": _b("Chef de famille", "رب الأسرة"),
    "nb_enf": _b("Enfants à charge (≤ 4)", "الأطفال المكفولون (≤ 4)"),
    "nb_enf_sup": _b("Étudiants sans bourse", "طلبة بدون منحة"),
    "nb_infirme": _b("Enfants handicapés", "أطفال ذوو إعاقة"),
    "nb_parents": _b("Parents à charge", "الوالدون المكفولون"),
    "deductions": _b("Déductions (DT/an)", "الطروحات (د.ت/سنة)"),
    "regularisation": _b("Régularisation", "التسوية"),
    "deja_preleve": _b("Déjà prélevé / acomptes (DT)", "المقتطع مسبقا / التسبقات (د.ت)"),
    "calculer": _b("Calculer l'impôt", "احسب الضريبة"),
    # Résultat principal
    "titre_resultat": _b("Impôt sur le revenu — foyer fiscal", "الضريبة على الدخل — المطرح الجبائي"),
    "irpp": _b("IRPP dû", "الضريبة المستحقة"),
    "css": _b("Contribution sociale de solidarité (CSS)", "المساهمة الاجتماعية التضامنية"),
    "total_du": _b("Total dû (IRPP + CSS)", "المجموع المستحق (ضريبة + مساهمة)"),
    "taux_moyen": _b("Taux moyen (IRPP)", "النسبة المتوسطة (الضريبة)"),
    "taux_moyen_total": _b("Taux moyen (IRPP + CSS)", "النسبة المتوسطة (ضريبة + مساهمة)"),
    "taux_marginal": _b("Taux marginal", "النسبة الحدّية"),
    "aide_marginal": _b(
        "Le taux marginal est l'impôt sur le prochain dinar gagné ; le taux moyen est l'impôt rapporté à l'ensemble du revenu.",
        "النسبة الحدّية هي الضريبة على الدينار الإضافي ؛ النسبة المتوسطة هي الضريبة على كامل الدخل.",
    ),
    # Décomposition
    "titre_decompo": _b("Détail du calcul", "تفصيل الحساب"),
    "revenus_categoriels": _b("Revenus par catégorie", "المداخيل حسب الصنف"),
    "rng": _b("Revenu net global (RNG)", "الدخل الصافي الجملي"),
    "deduction_famille": _b("Déduction pour charges de famille", "طرح الأعباء العائلية"),
    "deductions_investissement": _b("Déductions investissement/épargne", "طروحات الاستثمار/الادخار"),
    "revenu_net_imposable": _b("Revenu net imposable", "الدخل الصافي الخاضع للضريبة"),
    "impot_barème": _b("Impôt selon le barème", "الضريبة حسب الجدول"),
    "minimum_impot": _b("Minimum d'impôt (art. 12 bis)", "الضريبة الدنيا (الفصل 12 مكرّر)"),
    "minimum_actif": _b(
        "Le minimum d'impôt s'applique (vos déductions d'investissement sont plafonnées à 45 % de l'impôt théorique).",
        "تُطبَّق الضريبة الدنيا (طروحات الاستثمار محدودة بـ45٪ من الضريبة النظرية).",
    ),
    # Régularisation
    "titre_regul": _b("Régularisation annuelle", "التسوية السنوية"),
    "solde_a_payer": _b("Solde à payer", "الرصيد المستحق للدفع"),
    "solde_a_restituer": _b("Excédent à restituer", "الفائض المسترجع"),
    # Graphiques
    "titre_graphiques": _b("Visualisation du barème", "تمثيل الجدول"),
    "graph_tranches": _b("Revenu et impôt par tranche", "الدخل والضريبة حسب الشريحة"),
    "graph_taux": _b("Taux marginal et taux moyen", "النسبة الحدّية والمتوسطة"),
    "lbl_marginal": _b("Taux marginal", "النسبة الحدّية"),
    "lbl_moyen": _b("Taux moyen", "النسبة المتوسطة"),
    "lbl_vous": _b("Votre revenu", "دخلك"),
    # Comparateur
    "titre_comparateur": _b("Impact de la loi de finances 2025", "أثر قانون المالية 2025"),
    "intro_comparateur": _b(
        "Même foyer, deux barèmes : revenus de 2024 (ancien barème, 5 tranches) vs 2025 (nouveau barème, 8 tranches).",
        "نفس المطرح، جدولان : مداخيل 2024 (الجدول القديم، 5 شرائح) مقابل 2025 (الجدول الجديد، 8 شرائح).",
    ),
    "col_annee": _b("Barème", "الجدول"),
    "variation": _b("Variation", "الفارق"),
    # Autres calculs
    "titre_forfaitaire": _b("Régime forfaitaire BIC (petit commerce)", "النظام التقديري (التجارة الصغرى)"),
    "intro_forfaitaire": _b(
        "Impôt forfaitaire libératoire sur le chiffre d'affaires (art. 44 bis). Remplace l'IRPP ; aucune déduction.",
        "ضريبة تقديرية مبرئة على رقم المعاملات (الفصل 44 مكرّر). تعوّض الضريبة ؛ دون طروحات.",
    ),
    "chiffre_affaires": _b("Chiffre d'affaires annuel (DT)", "رقم المعاملات السنوي (د.ت)"),
    "impot_forfaitaire": _b("Impôt forfaitaire", "الضريبة التقديرية"),
    "titre_plus_value": _b("Plus-value immobilière", "القيمة الزائدة العقارية"),
    "intro_plus_value": _b(
        "Impôt libératoire (art. 27-28) : 15 % si détention < 5 ans, 10 % au-delà ; prix de revient majoré de 10 %/an.",
        "ضريبة مبرئة (الفصلان 27-28) : 15٪ إذا كانت المدة < 5 سنوات، 10٪ بعدها ؛ ثمن التكلفة يُرفع بـ10٪/سنة.",
    ),
    "pv_cession": _b("Prix de cession (DT)", "ثمن التفويت (د.ت)"),
    "pv_acquisition": _b("Prix d'acquisition (DT)", "ثمن الاقتناء (د.ت)"),
    "pv_frais": _b("Frais et travaux justifiés (DT)", "المصاريف والأشغال المبرَّرة (د.ت)"),
    "pv_duree": _b("Durée de détention (années)", "مدة الامتلاك (سنوات)"),
    "pv_exoneree": _b("Cession exonérée (résidence principale)", "تفويت معفى (السكن الرئيسي)"),
    "pv_imposable": _b("Plus-value imposable", "القيمة الزائدة الخاضعة"),
    "pv_impot": _b("Impôt sur la plus-value", "الضريبة على القيمة الزائدة"),
    "titre_inverse": _b("Simulation inverse (revenu net cible)", "محاكاة عكسية (الدخل الصافي المطلوب)"),
    "intro_inverse": _b(
        "À partir d'un revenu net souhaité (après IRPP et CSS), retrouve le salaire imposable correspondant.",
        "انطلاقا من دخل صافٍ مرغوب (بعد الضريبة والمساهمة)، يستخرج الأجر الخاضع المقابل.",
    ),
    "net_cible": _b("Revenu net souhaité (DT/an)", "الدخل الصافي المطلوب (د.ت/سنة)"),
    "salaire_imposable_trouve": _b("Salaire imposable correspondant", "الأجر الخاضع المقابل"),
    "calculer_inverse": _b("Trouver le revenu", "استخرج الدخل"),
    "calculer_pv": _b("Calculer la plus-value", "احسب القيمة الزائدة"),
    "calculer_forf": _b("Calculer le forfait", "احسب التقدير"),
    # Barème
    "titre_bareme": _b("Barème progressif de l'IRPP", "الجدول التصاعدي للضريبة"),
    "col_tranche": _b("Tranche de revenu (DT)", "شريحة الدخل (د.ت)"),
    "col_taux": _b("Taux", "النسبة"),
    # Divers
    "note_moteur": _b(
        "Calculé par le moteur **OpenFisca-Tunisia**. Barème des revenus de l'année choisie (loi de finances correspondante).",
        "محسوب بواسطة محرك **OpenFisca-Tunisia**. جدول مداخيل السنة المختارة (وفق قانون المالية المقابل).",
    ),
    "note_salaire_imposable": _b(
        "Le « net imposable » des salaires = salaire après cotisations sociales et abattement de 10 % (plafonné). Pour partir du brut, utilisez le simulateur de paie.",
        "« الصافي الخاضع » للأجور = الأجر بعد المساهمات والطرح بنسبة 10٪ (بسقف). للانطلاق من الأجر الخام استعمل محاكي الأجور.",
    ),
    "err_api": _b(
        "Impossible de joindre le moteur de calcul. Démarrez l'API ou utilisez le mode local.",
        "تعذّر الاتصال بمحرك الحساب. شغّل الواجهة البرمجية أو استعمل الوضع المحلي.",
    ),
    "err_aucun_revenu": _b(
        "Saisissez au moins un revenu pour calculer l'impôt.",
        "أدخل مدخولاً واحداً على الأقل لحساب الضريبة.",
    ),
    "pv_indispo": _b(
        "Le module plus-value nécessite une version récente d'openfisca-tunisia (non disponible sur ce moteur).",
        "وحدة القيمة الزائدة تتطلب نسخة حديثة من openfisca-tunisia (غير متوفرة على هذا المحرك).",
    ),
}

# Libellés des catégories de revenus (clés = variables openfisca).
LIBELLES_REVENUS = {
    "salaire_imposable": _b("Traitements et salaires (net imposable)", "الأجور والمرتبات (صافٍ خاضع)"),
    "pension_de_retraite": _b("Pensions et rentes viagères", "الجرايات والإيرادات العمرية"),
    "bic_reel_res": _b("BIC — régime réel", "الأرباح الصناعية والتجارية (حقيقي)"),
    "bnc_reel_res_fiscal": _b("BNC — régime réel", "الأرباح غير التجارية (حقيقي)"),
    "beap_reel_res_fiscal": _b("Bénéfices agricoles et de pêche", "الأرباح الفلاحية والصيد البحري"),
    "foncier_forfaitaire_batis_recettes": _b("Revenus fonciers (bâtis)", "المداخيل العقارية (المبنية)"),
    "capm_banq": _b("Capitaux mobiliers — intérêts", "رؤوس الأموال المنقولة — فوائد"),
    "salaire_etranger": _b("Revenus de source étrangère (salaire)", "مداخيل من مصدر أجنبي (أجر)"),
    "capm_part": _b("Capitaux mobiliers — dividendes", "رؤوس الأموال المنقولة — أرباح أسهم"),
    "capm_oblig": _b("Capitaux mobiliers — obligations", "رؤوس الأموال المنقولة — سندات"),
    "foncier_forfaitaire_non_batis_recettes": _b("Revenus fonciers (non bâtis)", "المداخيل العقارية (غير المبنية)"),
    "bnc_forfaitaire_recettes_brutes": _b("BNC — forfait d'assiette", "الأرباح غير التجارية (تقدير الوعاء)"),
    "pension_etranger_transferee": _b("Pension étrangère transférée", "جراية أجنبية محوَّلة"),
    "pension_etranger_non_transferee": _b("Pension étrangère non transférée", "جراية أجنبية غير محوَّلة"),
    "autres_revenus_etranger": _b("Autres revenus étrangers", "مداخيل أجنبية أخرى"),
}
LIBELLES_DEDUCTIONS = {
    "prime_assurance_vie": _b("Primes d'assurance-vie", "أقساط التأمين على الحياة"),
    "interets_acquisition_logement": _b("Intérêts crédit logement", "فوائد قرض السكن"),
    "compte_epargne_en_actions": _b("Compte épargne en actions (CEA)", "حساب الادخار في الأسهم"),
    "compte_epargne_investissement": _b("Compte épargne investissement (CEI)", "حساب الادخار للاستثمار"),
    "pret_universitaire": _b("Remboursement de prêts universitaires", "تسديد القروض الجامعية"),
    "dons": _b("Dons", "التبرعات"),
}
LIBELLES_CATEGORIES_RNG = {
    "tspr": _b("Traitements, salaires, pensions", "الأجور والمرتبات والجرايات"),
    "bic": _b("Bénéfices industriels et commerciaux", "الأرباح الصناعية والتجارية"),
    "bnc": _b("Bénéfices non commerciaux", "الأرباح غير التجارية"),
    "beap": _b("Bénéfices agricoles et de pêche", "الأرباح الفلاحية والصيد البحري"),
    "revenus_fonciers": _b("Revenus fonciers", "المداخيل العقارية"),
    "rvcm": _b("Revenus de capitaux mobiliers", "مداخيل رؤوس الأموال المنقولة"),
    "revenus_source_etrangere": _b("Revenus de source étrangère", "مداخيل من مصدر أجنبي"),
}


def t(cle: str, lang: str) -> str:
    entree = TRADUCTIONS.get(cle)
    if entree is None:
        return cle
    return entree.get(lang, entree.get("fr", cle))
