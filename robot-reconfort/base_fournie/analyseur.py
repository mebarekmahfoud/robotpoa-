import unicodedata
import re

class AnalyseurLinguistique:
    def __init__(self, donnees_dico):
        self.donnees_dico = donnees_dico

    def trouver_emotion(self, message):
        texte = message.lower() # tout en miniscule 

        # unicodedata.normalize retire les accents. Elle décompose chaque lettre accentuée
        #  (comme "é") en deux caractères (la lettre "e" + l'accent), 
        # puis le filtre if unicodedata.category(c) != 'Mn' supprime toutes les marques 
        # d'accentuation pour ne garder que les lettres de base.
        texte = ''.join(c for c in unicodedata.normalize('NFD', texte) if unicodedata.category(c) != 'Mn')

        # La fonction re.split(r'[^a-z]+', texte) utilise les expressions régulières pour cibler
        #  tout ce qui n'est pas une lettre (espaces, apostrophes, virgules, points)
        #  et s'en sert comme ciseaux pour découper la phrase. La ligne suivante 
        # [m for m in mots if m] nettoie la liste obtenue en supprimant les cases vides qui
        #  apparaissent souvent quand une phrase se termine par un poin
        mots = re.split(r'[^a-z]+', texte)
        mots = [m for m in mots if m]
        
        for mot in mots:
            for entree in self.donnees_dico["entrees"]:
                if mot in entree["formes"]:
                    return entree["emotion"], entree["intensite"]
                    
        return "emotion indeterminee", None