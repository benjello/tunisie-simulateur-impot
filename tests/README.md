# Tests

Deux niveaux de validation.

## Cas YAML OpenFisca (`tests/irpp/`)

Cas chiffrés exécutés directement par le moteur. Les valeurs attendues sont
celles d'OpenFisca-Tunisia pour l'année des revenus indiquée.

```bash
uv run openfisca test tests/irpp/ -c openfisca_tunisia
```

## Tests du client (`tests/test_client.py`)

Vérifient que `app/openfisca_client.py` (construction de situation + appel du
moteur) reproduit les mêmes chiffres, en **mode local** (moteur in-process, sans
API HTTP).

```bash
OPENFISCA_MODE=local uv run python -m pytest tests/ -q
```

## Confidentialité

Les cas sont anonymisés. La correspondance « cas ↔ simulateur en ligne » est
tenue dans `sources_locales/` (gitignoré) et ne doit jamais être poussée.
