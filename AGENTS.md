# AGENTS.md

Instructions et profils d'agents pour ce dépôt, lisibles par n'importe quel
opérateur d'agent (Claude Code, opencode, Cursor, pi…).

## Le projet

Simulateur d'**impôt sur le revenu des personnes physiques (IRPP)** pour la
Tunisie, construit sur le moteur [OpenFisca-Tunisia](https://github.com/openfisca/openfisca-tunisia)
et une interface [Shiny for Python](https://shiny.posit.co/py/). Dépôt frère de
`tunisie-simulateur-paie` et `tunisie-simulateur-pension`.

**L'application ne calcule rien elle-même** : elle poste la situation d'un foyer
fiscal (revenus par catégorie, situation de famille, déductions) à l'API web
d'OpenFisca-Tunisia et affiche l'IRPP dû. OpenFisca est le moteur unique.

## Règles de travail

- **Le droit fait référence** (Code de l'IRPP et de l'IS, lois de finances). Les
  simulateurs d'impôt en ligne sont des points de comparaison, pas la vérité.
- Chaque divergence est **identifiée, documentée et tranchée par le texte** dans
  `docs/notes/desaccords.md`. Un simulateur peut n'être exact que pour certaines
  années : le cas de test est alors calé sur l'année où sa règle est valide.
- **Convention de millésime** : le barème IRPP appliqué est celui des **revenus
  de l'année choisie** (loi de finances correspondante).
- **Confidentialité des sources** : les noms des simulateurs testés ne figurent
  pas dans le dépôt public. La correspondance « cas ↔ source » est tenue dans
  `sources_locales/` (gitignoré).
- Les tests YAML (`tests/irpp/`) sont exécutés par le moteur :
  `openfisca test tests/irpp/ -c openfisca_tunisia`.
- **Backlog durable** : tout report va dans `docs/notes/backlog.md`, jamais
  seulement dans la conversation.

## Profils d'agents disponibles

**Source unique** : `.pi/agents/*.md` (frontmatter name/description/tools/model).
Les autres formats sont **générés** par `scripts/deploy_agents.sh` :

```bash
scripts/deploy_agents.sh           # régénère .claude/agents/ et .opencode/agent/
scripts/deploy_agents.sh --global  # + déploie en user
scripts/deploy_agents.sh --check   # vérifie la synchro (CI), sans écrire
```

N'éditez que `.pi/agents/*.md`, puis relancez le script.

### `analyste-openfisca` — analyse du modèle (lecture seule, économe)

Répond à des questions précises sur le code et les paramètres d'OpenFisca-Tunisia
(`/home/benjello/projets/openfisca-tunisia`) — variables de revenus catégoriels,
barème, enchaînement du calcul de l'IRPP. **Vérifie les chiffres par le calcul**
via le venv `openfisca-tunisia/.venv`. Modèle conseillé : petit/rapide (Haiku).

### `juriste-fiscal-tn` — droit fiscal tunisien de l'IRPP

Établit ce que dit la loi (Code IRPP/IS, lois de finances) pour trancher les
écarts de calcul, en partant des textes primaires. Lecture seule + recherche
web. Modèle conseillé : intermédiaire (Sonnet).

## Entités et variables OpenFisca (mémo)

- Foyer fiscal `foyers_fiscaux` (rôle `declarants`) : variables annuelles
  `chef_de_famille`, `nb_enf`, `nb_enf_sup`, `nb_infirme`, `nb_parents`.
  Sorties : `rng`, `revenu_net_imposable`, `irpp`.
- Individu dans `individus` : revenus catégoriels — `salaire_imposable`,
  `pension_de_retraite`, `bic_reel_res`, `bnc_reel_res_fiscal`,
  `beap_reel_res_fiscal`, `foncier_forfaitaire_batis_recettes`, `capm_banq`,
  `salaire_etranger` ; déductions — `prime_assurance_vie`,
  `interets_acquisition_logement`, `compte_epargne_en_actions`,
  `compte_epargne_investissement`, `pret_universitaire`, `dons`.
- Ménage `menages` (rôle `personne_de_reference`).
- Barème : `openfisca_tunisia/parameters/impot_revenu/bareme.yaml`
  (régimes 1990, 2017, 2025).
