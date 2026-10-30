from reconfort_io import normaliser


class AnalyseurLinguistique:
    def __init__(self, donnees_dico):
        self.entrees = donnees_dico["entrees"]

    def trouver_emotion(self, message):
        # 1. Minuscules, retrait des accents et découpage via reconfort_io
        mots = normaliser(message)

        # 2. Parcours de gauche à droite : arrêt au premier mot reconnu
        for mot in mots:
            for entree in self.entrees:
                if mot in entree["formes"]:
                    return entree["emotion"], entree["intensite"]

        # 3. Aucun mot reconnu
        return "emotion indeterminee", None