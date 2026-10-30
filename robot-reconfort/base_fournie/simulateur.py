import reconfort_io as rio


class Simulateur:
    """Gère le monde réel, calcule les perceptions locales et enregistre la trace."""

    TRADUCTION_CASE = {
        "#": "mur",
        ".": "libre",
        "R": "libre",
        "A": "armoire",
        "D": "dictionnaire",
        "P": "resident",
    }

    DELTAS = {
        "N": (-1, 0),
        "S": (1, 0),
        "E": (0, 1),
        "O": (0, -1),
    }

    def __init__(self, donnees_carte, donnees_armoire, donnees_scenario, equipe):
        self._grille = donnees_carte["grille"]
        self._casiers_reels = {
            (c["ligne"], c["colonne"]): c["objet"]
            for c in donnees_armoire["casiers"]
        }
        self.pos_robot = list(donnees_carte["depart_robot"])
        self.pos_armoire = list(donnees_carte["armoire"]["position"])
        self.pos_selecteur = list(donnees_armoire["casier_depart"])

        # Données filtrées transmises au Robot (SANS "grille" ni "objet")
        self.carte_publique = {
            "dimensions": donnees_carte["dimensions"],
            "depart_robot": list(donnees_carte["depart_robot"]),
            "armoire": {"position": list(donnees_carte["armoire"]["position"])},
            "dictionnaire": {"position": list(donnees_carte["dictionnaire"]["position"])},
            "residents": [
                {"id": r["id"], "nom": r["nom"], "position": list(r["position"])}
                for r in donnees_carte["residents"]
            ],
        }
        self.armoire_publique = {
            "emotions": list(donnees_armoire["emotions"]),
            "intensites": list(donnees_armoire["intensites"]),
            "casier_depart": list(donnees_armoire["casier_depart"]),
        }

        self.trace = rio.Trace(
            nom_carte=donnees_carte["nom"],
            nom_scenario=donnees_scenario["nom"],
            equipe=equipe,
        )

    def est_adjacent(self, pos1, pos2):
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1]) == 1

    def percevoir(self):
        """Renvoie les 4 cases adjacentes (N, S, E, O) et le contenu du casier courant."""
        l, c = self.pos_robot
        perception = {}
        for direction, (dl, dc) in self.DELTAS.items():
            symbole = self._grille[l + dl][c + dc]
            perception[direction] = self.TRADUCTION_CASE[symbole]

        contenu_casier = None
        if self.est_adjacent(self.pos_robot, self.pos_armoire):
            contenu_casier = self._casiers_reels.get(tuple(self.pos_selecteur))

        return perception, contenu_casier

    def executer_action(self, num_demande, action, argument=None, commentaire=None):
        """Journalise le pas AVANT l'action dans Trace, puis met à jour le monde."""
        perception, contenu_casier = self.percevoir()

        self.trace.ajouter_pas(
            demande=num_demande,
            position=self.pos_robot,
            casier=self.pos_selecteur,
            action=action,
            argument=argument,
            perception=perception,
            contenu_casier=contenu_casier,
            commentaire=commentaire,
        )

        if action == "AVANCER":
            dl, dc = self.DELTAS[argument]
            self.pos_robot = [self.pos_robot[0] + dl, self.pos_robot[1] + dc]
        elif action == "CHERCHER":
            l, c = self.pos_selecteur
            if argument == "N":
                self.pos_selecteur = [l - 1, c]
            elif argument == "S":
                self.pos_selecteur = [l + 1, c]
            elif argument == "E":
                self.pos_selecteur = [l, (c + 1) % 8]
            elif argument == "O":
                self.pos_selecteur = [l, (c - 1) % 8]