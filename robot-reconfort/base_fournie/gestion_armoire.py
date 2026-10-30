class GestionnaireArmoire:
    def __init__(self, infos_armoire):
        # 1. On récupère la liste des 8 émotions de la roue de Plutchik
        self.emotions = infos_armoire["emotions"]

        # 2. On récupère la liste des intensités (["faible", "moyenne", "forte"])
        self.intensites = infos_armoire["intensites"]

        # 3. Position actuelle du bras sélecteur dans l'armoire
        self.position_selecteur = list(infos_armoire["casier_depart"])

        # 4. Mémoire des casiers déjà vus par le robot : "(ligne, colonne)" -> objet ou None
        self.memoire_casiers = {}

    def trier_candidats(self, emotion_cible, intensite_cible):
        # 1. On trouve l'indice numérique (0 à 7) de l'émotion et (0 à 2) de l'intensité
        idx_e = self.emotions.index(emotion_cible)
        idx_i = self.intensites.index(intensite_cible)

        candidats = []
        # 2. On parcourt les 3x8 positions possibles sans lire le contenu "objet"
        for l in range(3):
            for c in range(8):
                # --- CRITÈRE 1 : Distance sur la roue (avec bouclage modulo 8) ---
                ecart_brut = abs(c - idx_e)
                dist_roue = min(ecart_brut, 8 - ecart_brut)

                # On ne garde que les émotions à une distance <= 2
                if dist_roue <= 2:
                    # --- CRITÈRE 2 : Écart d'intensité ---
                    ecart_intensite = abs(l - idx_i)

                    # --- CRITÈRE 4 : Sens horaire prioritaire ---
                    sens = (c - idx_e) % 8
                    est_antihoraire = 1 if sens > 4 else 0

                    # Détermination du type de repli pour trace.json (Section 6.2)
                    if dist_roue == 0 and ecart_intensite == 0:
                        repli = "aucun"
                    elif dist_roue == 0:
                        repli = "intensite"
                    elif dist_roue == 1:
                        repli = "voisine_1"
                    else:
                        repli = "voisine_2"

                    # Clé de tri regroupant les 4 critères dans l'ordre exact du sujet
                    cle_tri = (dist_roue, ecart_intensite, l, est_antihoraire)
                    candidats.append((cle_tri, [l, c], repli))

        # Tri automatique par tuple
        candidats.sort(key=lambda x: x[0])

        # Renvoie la liste ordonnée de couples : ([ligne, colonne], repli)
        return [(c[1], c[2]) for c in candidats]

    def calculer_deplacements(self, depart, arrivee):
        mouvements = []
        l_dep, c_dep = depart
        l_arr, c_arr = arrivee

        # 1. Déplacements verticaux (lignes 0 à 2, sans bouclage)
        while l_dep != l_arr:
            if l_dep < l_arr:
                mouvements.append("S")
                l_dep += 1
            else:
                mouvements.append("N")
                l_dep -= 1

        # 2. Déplacements horizontaux avec bouclage toroïdal sur 8 colonnes
        while c_dep != c_arr:
            horaire = (c_arr - c_dep) % 8
            anti_horaire = (c_dep - c_arr) % 8

            if horaire <= anti_horaire:
                mouvements.append("E")
                c_dep = (c_dep + 1) % 8
            else:
                mouvements.append("O")
                c_dep = (c_dep - 1) % 8

        return mouvements