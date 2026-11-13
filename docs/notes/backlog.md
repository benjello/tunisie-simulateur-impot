# Backlog — simulateur d'impôt (IRPP)

Reports durables. Rien d'important ne doit vivre uniquement dans une
conversation d'agent ou une liste de session.

## Relais de session — 2026-11-13 (état complet, à ne pas perdre)

**✅ Committé et poussé** (branche `main`) : CI verte, déploiement shinyapps
réussi, app **en ligne HTTP 200** (https://benjello.shinyapps.io/simulateur-impot-tunisie/).
Fichiers : `app/app.py`, `app/openfisca_client.py`, `app/i18n.py`,
`app/baremes.py`, `app/graphs.py`, `README.md`, `.github/workflows/deploy.yml`,
`deploy/shinyapps/push.sh`, `pyproject.toml`, `deploy/shinyapps/requirements.txt`,
`tests/test_client.py`, `docs/notes/plan-ameliorations.md`, `docs/notes/backlog.md`.
NB déploiement : le bundle shinyapps doit inclure **tous** les modules de `app/`
(baremes.py et graphs.py avaient été oubliés → HTTP 500, corrigé).

**Reste non committé (autre dépôt)** : les fichiers plus-value dans
`openfisca-tunisia` (paramètres + variable + test YAML), à faire relire,
committer et **publier en release** pour activer la plus-value en production.

### Livré et testé cette session (app en ligne : https://benjello.shinyapps.io/simulateur-impot-tunisie/)
- **Axe A** : CSS (IRPP+CSS+total), décomposition par catégorie + pas-à-pas,
  minimum d'impôt (affiché seulement s'il mord), catégories & déductions
  avancées (mode avancé), régime forfaitaire BIC.
- **Axe B** : taux marginal + moyen, graphiques (par tranche + courbes de taux,
  `app/graphs.py` + `app/baremes.py`), comparateur barème 2024/2025, simulation
  inverse (net cible → salaire), modes rapide/détaillé/avancé.
- **Axe D** : D1 plus-values immobilières (voir § dépendance PyPI), D2
  régularisation (solde à payer/restituer).
- Correctif RTL antérieur (nombres en `dir="ltr"`) conservé.
- Tests : **5 YAML + 10 pytest verts, 1 skip** (plus-value, absente de PyPI).
- Dépendance : **openfisca-tunisia pris sur PyPI** (0.165) pour dev/CI/deploy.

### UX "entonnoir" (divulgation progressive) — FAIT
Objectif : ne montrer un champ que si l'utilisateur dit qu'il est concerné.
**Réalisé** dans `app/app.py` + `app/i18n.py` :
- Le radio rapide/détaillé/avancé est **remplacé** par des questions-portes :
  `input_checkbox_group` "Quels revenus avez-vous perçus ?" (courants :
  salaire/pension) + case "J'ai d'autres revenus" révélant un 2e groupe
  (`REVENUS_AUTRES` = détaillé + avancé). Chaque montant apparaît via
  `ui.panel_conditional` testé sur l'appartenance au groupe (`_rev_cond`).
- Case "J'ai des personnes à charge" → révèle nb_enf/enf_sup/infirme/parents ;
  case "J'ai des déductions" → révèle les 6 déductions ; case "Calculer le
  solde" → révèle `deja_preleve`. Aide contextuelle (`aide_revenus_ui`,
  `aide_chef_ui`) rendue en `@render.ui` (traduite).
- `_revenus()` ne compte que les types cochés ; `_famille()`/`_deductions()`/
  `deja_preleve` renvoient 0/vide si la case est décochée ; `_langue()` met à
  jour les libellés et les `update_checkbox_group` (choices traduits, `selected`
  conservé).
- **Vérifié** : import OK, `shiny run` HTTP 200 avec toutes les questions,
  5 YAML + 10 pytest verts (1 skip plus-value). Logique de calcul inchangée.

> Pistes UX de suite (non bloquantes) : indicateur d'étapes/progression,
> résumé de la saisie avant calcul, et parcours une-question-à-la-fois sur
> mobile (B9).

> **Plan d'améliorations avancées** (CSS, taux marginal, comparateur de barèmes,
> décomposition pédagogique, mode réforme, plus-values immobilières, etc.,
> priorisés et vérifiés) : voir [`plan-ameliorations.md`](plan-ameliorations.md).
> Les entrées ci-dessous restent le backlog opérationnel à court terme.

> **Fait (axes A, B, D)** — voir `plan-ameliorations.md` § État d'avancement :
> CSS, décomposition, minimum d'impôt, catégories/déductions avancées, taux
> marginal/moyen, graphiques, comparateur barèmes, inverse, forfaitaire BIC,
> régularisation, plus-value immobilière. Ci-dessous : ce qui reste.

## Dépendance bloquante — plus-value immobilière en production

- **Décision : le projet dépend d'openfisca-tunisia depuis PyPI** (actuellement
  0.165) — dev, CI et shinyapps utilisent la même source, pas d'install
  éditable local.
- La plus-value (D1) repose sur des variables **ajoutées au dépôt
  `openfisca-tunisia`** (paramètres `impot_revenu/plus_value_immobiliere/*`,
  variable `impot_plus_value_immobiliere`, test
  `tests/formulas/impot_revenu/plus_value_immobiliere.yaml`) mais **pas encore
  publiées sur PyPI**. Tant que la release ne les inclut pas, l'app affiche le
  module comme indisponible (dégradation propre) et le test
  `test_plus_value_immobiliere` est `skip`.
- **À faire pour activer la plus-value en prod** : faire relire/committer les
  fichiers plus-value dans openfisca-tunisia, **publier une release**, puis
  remonter la contrainte `openfisca-tunisia>=<version>` dans `pyproject.toml` et
  `deploy/shinyapps/requirements.txt`. Tout le code app côté impot est déjà
  prêt (il détecte automatiquement le support du moteur).

## Fonctionnel (reste à faire)

- **Foyer à deux déclarants** : conjoint (déclaration commune vs séparée) et
  répartition des revenus.
- **Plafonds de déduction** : afficher les plafonds effectifs (assurance-vie,
  CEA/CEI…) pour expliquer les écarts.
- **Export PDF** et **partage par URL** du résultat (B8).
- **Parcours en étapes / mobile** (B9) et finition de l'affichage arabe.
- **Mode réforme éditable** (axe C) et minimum de perception 0,2 % CA (D3).
- **Déductions avancées conditionnelles** (comptes spéciaux d'épargne, emprunt
  obligataire, rente, cotisations non affilié) : vérifié qu'elles n'ont aucun
  effet hors contexte adéquat → non exposées ; à traiter avec leurs conditions
  si le besoin se confirme.
- **Taux/seuils forfaitaire BIC 2025** : paramètre OpenFisca à 10 % (datant de
  2014) à recouper au JORT.

## Revenus catégoriels

- Exposés en mode avancé : dividendes `capm_part`, obligations `capm_oblig`,
  foncier non bâti, BNC forfaitaire, pensions étrangères. **Revenus agricoles**
  et **régimes spéciaux** restent à approfondir (modélisation partielle).

## Validation / tests

- Monter le jeu de cas `tests/irpp/*.yaml` à partir de simulateurs en ligne
  (correspondance tenue dans `sources_locales/`, gitignoré).
- Documenter chaque divergence dans `docs/notes/desaccords.md`.

## Déploiement

- Déploiement `shinyapps.io` en mode local : **câblé** — `deploy/shinyapps/`
  (bundle + `push.sh` manuel) et `.github/workflows/deploy.yml` (auto sur push
  `main`). Secrets GitHub `SHINYAPPS_*` poussés via
  `scripts/set_shinyapps_secrets.sh` (lit `.env`, gitignoré). Reste à **créer le
  repo GitHub `benjello/tunisie-simulateur-impot`, pousser les secrets et
  valider un premier déploiement**.
- **DÉPLOYÉ** ✅ — app en ligne : https://benjello.shinyapps.io/simulateur-impot-tunisie/
  (HTTP 200). Repo `benjello/tunisie-simulateur-impot`, secrets `SHINYAPPS_*`
  posés, CI verte, workflow `deploy.yml` opérationnel.
- Le quota du plan gratuit (5 apps) était atteint : deux apps parasites avec
  suffixe `1` (doublons d'un double déploiement) occupaient des slots
  (`simulateur-paie-tunisie1`, `simulateur-pension-tunisie1`). J'ai **terminé**
  `simulateur-paie-tunisie1` (status `terminated`, ne compte plus dans la limite
  active) ce qui a libéré le déploiement.
- **Cause racine des doublons `*-tunisie1` identifiée** : le workflow deploy
  (et `push.sh`) déployait par `--title` sans `--app-id`. Depuis un checkout
  neuf (CI) rsconnect ne trouve aucun enregistrement de déploiement et **crée
  une nouvelle app** à chaque run. Corrigé dans `deploy.yml` (ajout
  `--app-id 18430435`, l'app canonique). **⚠ Les dépôts paie et pension ont le
  même bug** — à corriger pareillement (sinon chaque déploiement auto ajoute un
  doublon et sature le quota).
- **À nettoyer** (dashboard shinyapps.io → Archive/Delete, l'API refuse la
  suppression hors du bon statut) : les apps terminées `simulateur-paie-tunisie1`,
  `simulateur-pension-tunisie1`, `simulateur-impot-tunisie1`. Terminées =
  hors quota actif ; juste du ménage définitif.
- **RTL (arabe)** : correctif appliqué — les montants et le barème sont rendus
  en `dir="ltr"` pour que les nombres ne soient pas réordonnés. Déployé en
  direct via rsconnect (`--app-id`). Au prochain passage : vérifier d'un œil
  l'affichage arabe complet (labels, sens de lecture).
- Mutualiser l'API OpenFisca entre les trois simulateurs (paie, pension, impôt)
  plutôt que trois déploiements séparés (réduirait aussi le nombre d'apps
  shinyapps).
