# HAI716-Projet-Agent

# Projet Le robot de réconfort

Code de départ du projet de semestre. Un robot à perception locale traverse
un appartement, consulte un dictionnaire pour lire l'émotion d'un message,
fouille une armoire et rapporte l'objet au résident.

**L'énoncé complet est dans [`ENONCE.pdf`](ENONCE.pdf). Lisez-le d'abord.**

## Récupérer le code

```
git clone <URL du dépôt>
cd robot-reconfort
python base_fournie/demo.py \
    base_fournie/cartes/appartement_01.json \
    base_fournie/cartes/scenario_01.json \
    base_fournie/donnees \
    sortie.json
```

La démo ne résout rien : elle charge les quatre fichiers et écrit une trace
où toutes les demandes échouent. C'est le squelette à remplir.

Python 3.9 ou plus, aucune dépendance externe. Vous pouvez travailler dans
un autre langage : seul le contrat d'appel (section 2 de l'énoncé) est
imposé.

## Contenu

| | |
|---|---|
| `ENONCE.pdf` | l'énoncé, projet 1 et projet 2 |
| `base_fournie/reconfort_io.py` | lecture des fichiers d'entrée, écriture de la trace |
| `base_fournie/demo.py` | exemple d'utilisation |
| `base_fournie/donnees/` | dictionnaire et armoire |
| `base_fournie/cartes/` | cinq appartements et leurs scénarios |
| `base_fournie/rendu.json` | modèle à compléter pour le rendu |
| `base_fournie/MODELE_README.md` | squelette du README de votre dépôt |


## Travailler

Ne travaillez pas dans ce dépôt. Créez le vôtre, et copiez-y `base_fournie/`.

Rappel: votre historique Git fait partie du rendu. 

## Deux interdits

Votre agent n'a le droit de lire **ni le champ `grille`** de la carte, **ni
le champ `objet`** des casiers. Il découvre les murs case par case à travers
ses perceptions, et le contenu des casiers en se plaçant devant. Sections
3.2 et 3.3 de l'énoncé ; c'est vérifié à la correction.

## Si l'algorithmique des graphes vous est nouvelle

Lisez les annexes de l'énoncé avant d'écrire quoi que ce soit : parcours en
largeur, exemple déroulé, pseudo-code et replanification. Tout y est.