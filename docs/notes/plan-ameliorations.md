# Plan d'améliorations approfondi — simulateur d'impôt (IRPP) Tunisie

> Document de travail. Issu de trois volets de recherche (ce qui est déjà
> modélisé dans OpenFisca-Tunisia mais non exposé ; le droit fiscal tunisien ;
> l'état de l'art des simulateurs d'impôt dans le monde), **chiffres vérifiés
> par le calcul** sur `openfisca-tunisia/.venv`. Les priorités reflètent un
> arbitrage utilité / effort ; à ajuster.

## État d'avancement

**Réalisé (axes A, B, D)** — IRPP + **CSS**, décomposition pas-à-pas et par
catégorie, **minimum d'impôt** (affiché seulement s'il mord), catégories et
déductions avancées, **taux marginal + moyen**, **graphiques** (par tranche,
courbes de taux), **comparateur barème 2024/2025**, **simulation inverse**,
**régime forfaitaire BIC**, **régularisation** (solde), **plus-value
immobilière** (D1 : variables ajoutées à `openfisca_tunisia` + test). Modes
rapide / détaillé / avancé.

**Reste** — Axe C (mode réforme éditable, distributif), export PDF / partage par
URL (B8), parcours en étapes mobile (B9), minimum de perception D3, et la
**publication d'openfisca-tunisia** incluant les plus-values (sinon le module
est indisponible en production). Détail par item ci-dessous.

## État actuel (rappel)

Déclaration annuelle d'un **foyer fiscal à un déclarant**. Entrées : 8 catégories
de revenus (salaire imposable, pension, BIC, BNC, BEAP, foncier bâti, capitaux
mobiliers, source étrangère), situation de famille (chef de famille, enfants,
étudiants, enfants handicapés, parents), 6 déductions. Sorties : RNG → revenu net
imposable → IRPP + taux moyen + barème de l'année. Bilingue FR/AR, modes
api/local, déployé sur shinyapps.io.

## Encadré — chiffres de référence vérifiés (droit 2024)

| Cas | RNG | Imposable | IRPP | CSS | Taux marginal |
|---|---|---|---|---|---|
| Salarié célibataire, salaire imposable 30 000 | 28 000 | 28 000 | 6 140 | 140 | ≈ 28 % |
| Mix 20 000 salaire + 10 000 BIC + 5 000 capitaux, chef + 2 enfants | 33 000 | 32 500 | 7 500 | 162,5 | — |
| Salarié 4 000 (sous seuil) | 4 000 | 4 000 | 0 | 0 (exonéré) | 0 % |

Toutes les variables citées plus bas existent et sont calculables par le moteur
(`contribution_sociale_solidarite`, `minimum_impot`, `tspr/bic/bnc/beap/
revenus_fonciers/rvcm/revenus_source_etrangere`, `deduction_famille`,
`deductions_base`, `deductions_investissement`, `assiette_avant_avantages`,
`impot_avant_avantages`, `impot_revenu_brut`, `impot_total_du`). Le **taux
marginal** s'obtient par dérivée numérique (IRPP(R+1) − IRPP(R)).

---

## Axe A — Fidélité fiscale : exposer ce qui est DÉJÀ modélisé

Gains à fort impact et effort faible : le moteur calcule déjà, il suffit de
l'afficher.

### A1. Contribution sociale de solidarité (CSS) — **PRIORITÉ 1**
- **Quoi** : afficher « IRPP » + « CSS » + « Total prélevé ». Variable
  `contribution_sociale_solidarite` (foyer). L'exonération des revenus
  salaires/pensions ≤ 5 000 DT (LF 2020, art. 39) est gérée par le moteur
  (vérifié : CSS = 0 à 4 000 DT).
- **Pourquoi** : prélèvement obligatoire distinct, visible sur la fiche de paie ;
  les calculateurs tunisiens l'affichent. Base légale : art. 53 LF 2018.
- **Effort** : faible. **Impact** : fort.

### A2. Décomposition pédagogique du calcul — **PRIORITÉ 1**
- **Quoi** : restituer les étapes nommées plutôt que le seul IRPP final :
  revenu par catégorie (`tspr`, `bic`, `bnc`, `beap`, `revenus_fonciers`,
  `rvcm`, `revenus_source_etrangere`) → RNG → déductions (`deduction_famille`,
  `deductions_base`, `deductions_investissement`) → revenu net imposable →
  impôt barème (`impot_avant_avantages`) → minimum/avantages → IRPP → CSS.
- **Pourquoi** : confiance et pédagogie (modèle impots.gouv.fr « pas-à-pas »).
- **Effort** : faible-moyen (variables déjà là). **Impact** : fort.

### A3. Minimum d'impôt (art. 12 bis) — géré en interne
- **Quoi** : `minimum_impot` = 45 % de l'impôt théorique *avant avantages
  fiscaux*. Il ne **mord que si** des déductions d'investissement
  (assurance-vie, CEA/CEI…) font tomber l'impôt sous ce plancher. Vérifié :
  à 30 000 DT sans déduction, `minimum_impot` = 2 763 < IRPP 6 140 → non
  contraignant.
- **Reco** : calculer en interne, **n'afficher le plancher que lorsqu'il est
  activé** (sinon, afficher `minimum_impot` à côté de l'IRPP induit l'utilisateur
  en erreur — piège repéré). **Effort** : faible.

### A4. Catégories et déductions supplémentaires (mode détaillé)
- **Revenus** aujourd'hui non exposés mais modélisés : dividendes `capm_part`,
  obligations `capm_oblig` (et `capm_cent/caisse/aut`), foncier non bâti
  `foncier_forfaitaire_non_batis_recettes`, BNC forfaitaire
  `bnc_forfaitaire_recettes_brutes`, pension étrangère
  `pension_etranger_transferee/non_transferee`, `autres_revenus_etranger`.
- **Déductions** : `compte_special_epargne_banque/cent`, `emprunt_obligataire`,
  `rente`, `cotisations_non_affilie`, `plus_value_cession_actifs_cotes_bourse`,
  `credit_impot_etranger`.
- **Reco** : les regrouper dans un **mode « détaillé »** (cf. B3) pour ne pas
  alourdir le parcours grand public. **Effort** : faible (ce sont des entrées).

### A5. Régime forfaitaire BIC (« petit commerce ») — très répandu
- **Quoi** : ~400 000 contribuables au forfait (art. 44 bis). Impôt forfaitaire
  **libératoire** sur le CA. Variables `chiffre_affaires_soumis_au_forfait`,
  `impot_regime_forfaitaire_du`, paramètre
  `impot_revenu.regimes_speciaux.forfaitaire.taux_imposition`.
- **Limite** : le BIC forfaitaire **n'alimente pas le RNG** (reste une ligne
  séparée, libératoire) — à traiter comme **module distinct** (« je suis au
  forfait »), pas comme une catégorie de plus.
- **À vérifier** (juriste) : taux et seuils de CA en vigueur (le paramètre
  OpenFisca date de 2014 ; valeurs 2025 à recouper au JORT). **Effort** : moyen.

---

## Axe B — Fonctionnalités de simulation (état de l'art international)

### B1. Taux marginal + taux moyen affichés ensemble — **PRIORITÉ 1**
- **Quoi** : afficher le taux **moyen** (déjà fait) ET le taux **marginal**
  (impôt sur le prochain dinar), via dérivée numérique (vérifié ≈ 28 % à
  30 000 DT). Tooltip explicatif « marginal ≠ moyen ».
- **Pourquoi** : la confusion marginal/moyen est universelle ; #1 des reprises
  internationales (SmartAsset). **Effort** : faible. **Impact** : fort.

### B2. Visualisations du barème — **PRIORITÉ 2**
- Barres empilées « combien de revenu dans chaque tranche / combien d'impôt par
  tranche » ; courbe du taux marginal et du taux moyen en fonction du revenu ;
  option diagramme de flux (Sankey) revenu → déductions → impôt → net
  (cf. Engaging Data, Tax Foundation).
- **Effort** : moyen (matplotlib/plotly en Shiny). **Impact** : fort (rend la
  progressivité intuitive).

### B3. Mode « rapide » vs « détaillé »
- Parcours court grand public (salaire/pension + famille) vs mode avancé
  (BIC/BNC, foncier, toutes déductions — A4). Modèle impots.gouv.fr.
- **Effort** : faible-moyen (branching UI). **Impact** : fort (accessibilité).

### B4. Simulation inverse (revenu net cible → imposable/brut)
- Bissection sur le moteur (déjà éprouvée dans le simulateur de paie). Public
  qui raisonne en net désiré. **Effort** : moyen. **Impact** : moyen-fort.

### B5. Comparateur de scénarios côte à côte
- Deux (ou N) situations en parallèle : célibataire vs marié, avec/sans
  déduction, 2024 vs 2025. **Effort** : moyen. **Impact** : fort (aide à la
  décision).

### B6. Comparateur barème 2024 vs 2025 — **PRIORITÉ 1 (TN)**
- « Gain/perte avec la LF 2025 » (barème passé de 5 à 8 tranches, art. 36
  LF 2025). Deux calculs du moteur, un delta. Très demandé en Tunisie.
- **Effort** : faible. **Impact** : fort.

### B7. Calcul pas-à-pas affiché
- Consomme A2 : chaque étape dépliable avec son montant intermédiaire.
- **Effort** : moyen. **Impact** : fort.

### B8. Export PDF + partage par URL
- Garder une trace, partager un cas (bookmarking Shiny / query params).
- **Effort** : faible. **Impact** : moyen.

### B9. Parcours en étapes, mobile, finition RTL arabe
- Formulaire progressif (mes-aides.gouv.fr), responsive, vérifier l'affichage
  arabe complet (le correctif « nombres en LTR » est fait ; reste labels et sens
  de lecture). **Effort** : moyen.

---

## Axe C — Mode « réforme » (type LexImpact)

### C1. Barème éditable → impact sur un cas type
- L'utilisateur modifie taux/seuils du barème et voit l'effet sur un ménage
  représentatif (graphe avant/après). OpenFisca gère nativement les `Reform`.
- **Pourquoi** : pédagogie citoyenne, débat public. **Effort** : moyen.
  **Impact** : fort / différenciant.

### C2. Impact budgétaire et redistributif national (long terme)
- Coût pour le budget, effet par décile. **Nécessite des micro-données
  représentatives** (INS/DGI) non publiques à ce jour. **Hors portée court
  terme** ; piste via `tunisia-data` / `ceq-tunisie` / `openfisca-survey-manager`
  si un échantillon anonymisé devient disponible.

---

## Axe D — Nouveaux modules fiscaux (à construire d'abord dans OpenFisca)

Ces besoins exigent d'étendre le **country-package** `openfisca_tunisia` avant de
toucher l'app.

### D1. Plus-values immobilières — forte demande, non modélisé
- Droit : art. 27-28 code IRPP, LF 2021 : **15 %** si détention < 5 ans, **10 %**
  au-delà ; majoration du prix de revient de 10 %/an ; exonération résidence
  principale ; retenue 2,5 % (notaire) imputable.
- **État OpenFisca** : aucune variable (seulement des commentaires). À
  implémenter (entrées : prix/année d'achat et de vente, travaux). **Effort** :
  élevé (modèle + tests). **Impact** : fort.

### D2. Régularisation retenue à la source / acomptes → solde
- Entrée « déjà prélevé / acomptes versés » → sortie « solde à payer /
  excédent à restituer ». Le simulateur de paie expose déjà `irpp_net_a_payer`.
- **Effort** : moyen. **Impact** : fort (salariés à revenus complémentaires).

### D3. Minimum de perception (0,2 % du CA, min. 300 DT) — BIC/BNC réel
- Art. 44 § II. **Distinct** du minimum 12 bis (A3). À vérifier s'il est
  modélisé ; sinon à ajouter pour un mode BIC/BNC réel. **Effort** : moyen.
  **Impact** : moyen (marginal grand public).

---

## Axe E — Qualité, confiance, écosystème

- **E1. API publique / MCP** : exposer le moteur indépendamment de l'UI (déjà
  `openfisca serve` ; cf. `mcp-socio-fiscal-tunisie`). Réutilisation chercheurs,
  médias. **Effort** : moyen.
- **E2. Corpus de tests élargi** : caler des cas sur des notes communes / exemples
  officiels, tenir `docs/notes/desaccords.md` (écarts avec calculateurs en ligne :
  confusion déduction-revenu/impôt, oubli du plafond d'abattement 10 % à 2 000 DT,
  CSS appliquée à tort sous 5 000 DT). **Effort** : continu.
- **E3. Vie privée** : calcul sans stockage, documenté. **Effort** : faible.
- **E4. Accessibilité / i18n arabe complet / mobile**. **Effort** : moyen.
- **E5. Dette technique de déploiement** : harmoniser les workflows `deploy.yml`
  de paie et pension avec `--app-id` (même bug de doublons `*-tunisie1`). Voir
  `backlog.md`.

---

## Priorisation synthétique (ma recommandation)

**Vague 1 — quick wins (app seule, moteur prêt)**
A1 CSS · B1 taux marginal/moyen · B6 comparateur barème 2024/2025 ·
A2 décomposition · B2 graphes par tranche. → forte valeur, faible effort.

**Vague 2 — UX et profondeur**
B3 mode rapide/détaillé · A4 catégories/déductions avancées · B7 pas-à-pas ·
B4 simulation inverse · B5 comparateur de scénarios · B8 export/partage ·
B9 étapes + mobile + RTL.

**Vague 3 — modules et différenciation**
A5 forfaitaire BIC · D2 régularisation · C1 mode réforme.

**Vague 4 — gros chantiers / country-model**
D1 plus-values immobilières · D3 minimum de perception · C2 distributif national.

## Dépendances et risques

- **Étendre d'abord `openfisca_tunisia`** pour D1 (plus-values) et possiblement
  D3 : ce n'est pas qu'un travail d'app.
- **Ne pas afficher `minimum_impot` comme un dû** quand il n'est pas contraignant
  (A3) — risque de mésinterprétation.
- **Incertitudes à lever (texte/juriste)** : taux et seuil du forfaitaire BIC
  2025 ; montant de la déduction « parents à charge » 2025 ; articulation
  min. 12 bis / min. de perception pour revenus mixtes ; détail des abattements
  TSPR par année. À trancher dans `desaccords.md`.

## Sources

- [impots.gouv.fr — Simulateurs](https://www.impots.gouv.fr/simulateurs) ·
  [IR 2026 simplifié](https://simulateur-ir-ifi.impots.gouv.fr/calcul_impot/2026/simplifie/index.htm)
- [LexImpact](https://leximpact.an.fr/) ·
  [simulateur socio-fiscal](https://socio-fiscal.leximpact.an.fr/accueil) ·
  [fonctionnement](https://socio-fiscal.leximpact.an.fr/fonctionnement)
- [mes-aides.gouv.fr](https://mes-aides.gouv.fr/) ·
  [GitHub mes-aides/simulateur](https://github.com/mes-aides/simulateur)
- [SmartAsset — Income Tax Calculator](https://smartasset.com/taxes/income-taxes) ·
  [Tax Foundation — interactive tax graph](https://interactive.taxfoundation.org/taxgraph/) ·
  [Engaging Data — Tax Brackets](https://engaging-data.com/tax-brackets/)
- [listentotaxman.com](https://listentotaxman.com/) ·
  [MoneySavingExpert — Income tax calculator](https://www.moneysavingexpert.com/tax-calculator/)
- Droit tunisien : art. 53 LF 2018 (CSS) ; art. 39 LF 2020 (exonération CSS
  < 5 000 DT) ; art. 44 code IRPP, art. 14-1 LF 2017, art. 36 LF 2025 (barèmes) ;
  art. 12 bis loi 89-114 et art. 44 § II code (minima) ; art. 5 et 40 (chef de
  famille, déductions) ; art. 27-28 code IRPP + LF 2021 (plus-values immo) ;
  art. 44 bis et art. 22 § II (régimes forfaitaires).
