# tunisie-simulateur-impot

Simulateur d'**impôt sur le revenu des personnes physiques (IRPP)** pour la
Tunisie, construit sur le moteur de micro-simulation
[OpenFisca-Tunisia](https://github.com/openfisca/openfisca-tunisia), avec une
interface [Shiny for Python](https://shiny.posit.co/py/).

**🚀 Application en ligne : https://benjello.shinyapps.io/simulateur-impot-tunisie/**

Dépôt frère de [`tunisie-simulateur-paie`](https://github.com/benjello/tunisie-simulateur-paie)
(fiche de paie) et [`tunisie-simulateur-pension`](https://github.com/benjello/tunisie-simulateur-pension)
(retraite). Même architecture, même moteur.

## Architecture

L'application **ne calcule rien elle-même** : elle envoie la situation d'un
foyer fiscal (revenus par catégorie, situation de famille, déductions) à
l'**API web d'OpenFisca-Tunisia** et affiche l'IRPP annuel renvoyé. OpenFisca
reste le moteur unique ; l'app est une couche de présentation.

```
Shiny (app/)  ──HTTP──▶  API OpenFisca-Tunisia  ──▶  moteur de calcul
```

En local, deux processus (voir [`app/README.md`](app/README.md)) :

```bash
uv run openfisca serve -c openfisca_tunisia -p 5000   # l'API
uv run shiny run app/app.py --port 8102               # l'app
```

## Périmètre de la v1

Déclaration annuelle de l'IRPP au niveau du **foyer fiscal** (un déclarant).

- **Entrées — revenus par catégorie** (annuels, en DT) : traitements et
  salaires (net imposable), pensions et rentes viagères, BIC, BNC, bénéfices
  agricoles et de pêche (BEAP), revenus fonciers, revenus de capitaux
  mobiliers, revenus de source étrangère.
- **Entrées — situation familiale** : chef de famille, enfants à charge,
  étudiants sans bourse, enfants handicapés, parents à charge.
- **Entrées — déductions communes** : assurance-vie, intérêts de crédit
  logement, compte épargne en actions (CEA), compte épargne investissement
  (CEI), prêts universitaires, dons.
- **Sorties** : revenu net global (RNG), revenu net imposable, **IRPP + CSS**
  (contribution sociale de solidarité), total dû, **taux moyen et taux
  marginal**, et la décomposition pas-à-pas du calcul.

### Fonctionnalités avancées

- **Modes rapide / détaillé / avancé** : du grand public (salaire + famille) aux
  cas complexes (toutes catégories, dividendes, obligations, pensions
  étrangères…).
- **Décomposition pédagogique** : revenus par catégorie, déductions, assiette,
  impôt par tranche ; **graphiques** (revenu/impôt par tranche, courbes des taux
  marginal et moyen).
- **Comparateur de barèmes 2024 vs 2025** (impact de la loi de finances 2025).
- **Régularisation** : solde à payer / à restituer à partir du déjà prélevé.
- **Autres calculs** : régime forfaitaire BIC (petit commerce), **plus-value
  immobilière** (art. 27-28), **simulation inverse** (revenu net souhaité →
  salaire imposable).

> Le simulateur part du **salaire net imposable** (après cotisations sociales et
> abattement de 10 %). Pour partir du salaire brut, utilisez le simulateur de
> paie.

> **Plus-value immobilière** : repose sur des variables ajoutées à
> `openfisca_tunisia` (paramètres + `impot_plus_value_immobiliere`). Le module
> nécessite une version d'openfisca-tunisia incluant cette fonctionnalité ; sinon
> l'app l'affiche comme indisponible (dégradation propre).

## Convention de millésime

Le **barème IRPP** appliqué est celui des **revenus de l'année choisie** (fixé
par la loi de finances correspondante). Barèmes disponibles dans OpenFisca :
régime 2017 (valable 2017-2024) et régime 2025.

## Principe de validation

Le **droit fait référence** (Code de l'IRPP et de l'IS, lois de finances). Les
simulateurs d'impôt en ligne servent de **points de comparaison** : chaque cas
chiffré devient un test YAML OpenFisca (`tests/irpp/`). Chaque divergence est
documentée dans [`docs/notes/desaccords.md`](docs/notes/desaccords.md) et
tranchée par le texte légal.

> Les noms des simulateurs testés ne figurent pas dans le dépôt public. La
> correspondance « cas de test ↔ source » est tenue dans `sources_locales/`
> (dossier gitignoré).

## Structure

```
app/               Application Shiny (client OpenFisca + interface)
tests/irpp/        Tests YAML OpenFisca (publics)
sources_locales/   Correspondance cas ↔ simulateur (GITIGNORÉ)
docs/notes/        Backlog et registre des désaccords
deploy/            Déploiement (shinyapps.io)
```

## Déploiement

App déployée sur **shinyapps.io** en mode local (OpenFisca calculé dans le
process, sans API séparée). Déploiement manuel via `deploy/shinyapps/push.sh` ou
automatique via GitHub Actions (`.github/workflows/deploy.yml`, sur push `main`).
Les 3 secrets `SHINYAPPS_*` se définissent une fois dans un `.env` local
(gitignoré, voir `.env.example`) puis se poussent avec
`scripts/set_shinyapps_secrets.sh`. Détails : [`deploy/shinyapps/README.md`](deploy/shinyapps/README.md).

## Lancer les tests

```bash
uv run openfisca test tests/irpp/ -c openfisca_tunisia   # cas YAML
OPENFISCA_MODE=local uv run python -m pytest tests/ -q    # client en local
```
