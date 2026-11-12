# Application — impôt sur le revenu (IRPP)

Interface [Shiny for Python](https://shiny.posit.co/py/) pour le simulateur
d'IRPP. **Tout le calcul est fait par OpenFisca-Tunisia** : l'app construit la
situation d'un foyer fiscal, la poste à l'API (ou calcule en local), et affiche
l'impôt dû.

## Lancer en local

Deux processus. Dans un premier terminal, l'API OpenFisca :

```bash
uv run openfisca serve -c openfisca_tunisia -p 5000
```

Dans un second, l'app Shiny :

```bash
uv run shiny run app/app.py --port 8102
```

Puis ouvrir http://localhost:8102.

Pour calculer sans API séparée (moteur in-process), utilisez le mode local :

```bash
OPENFISCA_MODE=local uv run shiny run app/app.py --port 8102
```

Pour pointer vers une API hébergée ailleurs, définir `OPENFISCA_API_URL` :

```bash
OPENFISCA_API_URL=https://mon-api-openfisca.example uv run shiny run app/app.py
```

## Fichiers

- `openfisca_client.py` — construction de la situation (foyer fiscal) et appel
  `/calculate` ; modes `api` (HTTP) et `local` (in-process).
- `app.py` — interface Shiny (entrées : revenus par catégorie, situation
  familiale, déductions ; sorties : RNG, revenu imposable, IRPP, taux moyen).
- `i18n.py` — traductions FR / AR.

## Périmètre actuel

Déclaration annuelle d'un foyer fiscal à un déclarant. Le conjoint déclarant
séparé, le détail par bénéficiaire et les réductions d'impôt spécifiques sont au
backlog (voir `docs/notes/backlog.md`).
