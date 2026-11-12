# Déploiement sur shinyapps.io

Hébergement gratuit de l'app Shiny (compte shinyapps.io, sans carte bancaire ;
plan gratuit = 25 h actives/mois, 1 Go RAM). L'app calcule OpenFisca **en
direct** dans le process (`OPENFISCA_MODE=local`) : pas d'API HTTP séparée.

## Prérequis (une seule fois)

1. **Compte** sur https://www.shinyapps.io (Google/GitHub, sans carte).
2. **rsconnect-python** : déjà installé dans le venv du projet (`uv sync --group dev`).
3. **Autoriser le compte** — contient ton SECRET, à lancer dans TON terminal
   (depuis Account → Tokens sur shinyapps.io, bouton « Copy to clipboard ») :

   ```bash
   .venv/bin/rsconnect add --account <compte> --name <compte> \
     --token <TOKEN> --secret <SECRET>
   ```

   > Le token/secret donnent accès à ton compte : ne les commite jamais. Tu peux
   > les révoquer/régénérer à tout moment depuis la page Tokens.

## Déployer (manuel)

```bash
deploy/shinyapps/push.sh <compte> [nom-app]
# ex :
deploy/shinyapps/push.sh benjello simulateur-impot-tunisie
```

Le script assemble un bundle propre (point d'entrée `app.py` qui force le mode
local + `app_main.py` + `openfisca_client.py` + `i18n.py` + `requirements.txt`)
et lance `rsconnect deploy shiny`. L'URL publique s'affiche à la fin.

## Fichiers

- `app.py` — point d'entrée déploiement (force `OPENFISCA_MODE=local`).
- `requirements.txt` — dépendances (shiny, openfisca-tunisia, httpx).
- `push.sh` — assemble le bundle et déploie.

## Déploiement automatique (GitHub Actions)

Le workflow `.github/workflows/deploy.yml` déploie l'app à chaque push sur
`main` touchant `app/` ou `deploy/shinyapps/` (et manuellement via
*Actions → Deploy to shinyapps.io → Run workflow*).

**Configuration unique — définir 3 secrets GitHub** (Settings → Secrets and
variables → Actions → New repository secret) :

| Secret | Valeur |
|--------|--------|
| `SHINYAPPS_ACCOUNT` | ton compte, ex. `benjello` |
| `SHINYAPPS_TOKEN`   | le token (Account → Tokens sur shinyapps.io) |
| `SHINYAPPS_SECRET`  | le secret associé |

Ces valeurs sont chiffrées par GitHub et ne sont jamais exposées dans les logs.
Tant qu'elles ne sont pas définies, le job échoue proprement (rien n'est
déployé). Pour les changer : régénère le token sur shinyapps.io et mets à jour
le secret.

### Pousser les secrets sans les ressaisir dans l'interface

Les secrets GitHub ne se copient pas d'un repo à l'autre automatiquement.
Renseigne-les une fois dans un `.env` local (gitignoré, voir `.env.example` à la
racine) puis lance `scripts/set_shinyapps_secrets.sh` (il lit `.env` et pousse
les secrets via `gh`) :

```bash
cp .env.example .env && chmod 600 .env   # puis éditer .env
scripts/set_shinyapps_secrets.sh benjello/tunisie-simulateur-impot
```

Le `.env` peut être partagé entre les simulateurs (paie, pension, impôt) : le
script cible le repo passé en argument. Ne commite jamais `.env`.

> **Alternative pour beaucoup de repos** : les déplacer dans une **organisation
> GitHub** et définir les secrets `SHINYAPPS_*` **une seule fois** au niveau de
> l'org (accessibles à tous ses repos). Surdimensionné pour 2-3 repos.

## Limite du plan gratuit

25 h actives/mois. Au-delà, l'app est suspendue jusqu'au mois suivant. Pour un
usage soutenu : plan payant shinyapps.io, ou un VPS.
