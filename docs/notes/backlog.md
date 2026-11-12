# Backlog — simulateur d'impôt (IRPP)

Reports durables. Rien d'important ne doit vivre uniquement dans une
conversation d'agent ou une liste de session.

## Fonctionnel

- **Foyer à deux déclarants** : aujourd'hui un seul déclarant. Ajouter le
  conjoint (déclaration commune vs séparée) et répartir les revenus.
- **Réductions d'impôt** : seules les déductions sur le revenu sont exposées.
  Ajouter les réductions/crédits d'impôt éventuels (crédit d'impôt étranger,
  etc.) une fois leur modélisation OpenFisca confirmée.
- **Plafonds de déduction** : afficher les plafonds effectifs appliqués par le
  moteur (assurance-vie, CEA/CEI…) pour expliquer les écarts à l'utilisateur.
- **Minimum d'impôt** : documenter et, si utile, exposer le minimum d'impôt
  (1,5 % du revenu) appliqué par le moteur.
- **Export PDF** et **comparateur multi-années**, comme le simulateur de paie.

## Revenus catégoriels

- Les variables d'entrée retenues sont une par catégorie (la plus courante). Le
  modèle OpenFisca en expose d'autres (BNC forfaitaire, foncier non bâti,
  dividendes `capm_part`, obligations `capm_oblig`, pension étrangère…) : les
  ajouter si le besoin se confirme.
- **Revenus agricoles** et **régimes spéciaux** (forfaitaire, microentreprises) :
  modélisation OpenFisca partielle, à vérifier avant exposition.

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
- **BLOQUÉ — quota shinyapps.io.** Repo GitHub créé
  (`benjello/tunisie-simulateur-impot`), secrets `SHINYAPPS_*` posés, CI verte,
  workflow `deploy.yml` fonctionnel (authentification shinyapps OK, bundle
  assemblé). Le déploiement échoue sur :
  `You have reached the maximum number of applications allowed for your account`
  — le plan gratuit limite le nombre d'applications et les slots sont déjà
  pris (paie, pension…). **Pour débloquer** : supprimer/archiver une app
  shinyapps existante, ou passer à un plan supérieur, puis relancer
  *Actions → Deploy to shinyapps.io → Run workflow*.
- Mutualiser l'API OpenFisca entre les trois simulateurs (paie, pension, impôt)
  plutôt que trois déploiements séparés (réduirait aussi le nombre d'apps
  shinyapps).
