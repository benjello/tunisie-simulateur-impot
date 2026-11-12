# Registre des désaccords — IRPP

Chaque divergence entre un simulateur d'impôt en ligne (ou un calcul manuel) et
le moteur OpenFisca-Tunisia est consignée ici, puis tranchée par le texte légal.

Format d'une entrée :

- **Cas** : description chiffrée (revenus, famille, année).
- **Écart** : valeur simulateur vs valeur OpenFisca.
- **Texte de référence** : article du Code IRPP/IS ou loi de finances + date
  d'effet.
- **Décision** : qui a raison et pourquoi ; impact sur le cas de test.

## Points vérifiés (référence)

- **Barème 2024 (régime 2017)** : tranches 0–5 000 à 0 %, 5 000–20 000 à 26 %,
  20 000–30 000 à 28 %, 30 000–50 000 à 32 %, > 50 000 à 35 %.
  Vérifié : salarié célibataire à 30 000 DT de salaire imposable → abattement
  10 % (plafonné 3 000) → RNG 28 000 → IRPP **6 140 DT**.
- **Barème 2025 (loi de finances 2025)** : nouvelles tranches, taux de 15 % à
  40 % (voir `openfisca_tunisia/parameters/impot_revenu/bareme.yaml`).

## Désaccords ouverts

_(aucun pour l'instant)_
