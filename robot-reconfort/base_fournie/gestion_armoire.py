class GestionnaireArmoire:
    def __init__(self, donnees_armoire):
        # 1. On récupère la liste des 8 émotions de la roue de Plutchik
        self.emotions = donnees_armoire["emotions"]
        
        # 2. On récupère la liste des intensités (ex: ["faible", "moyenne", "forte"])
        self.intensites = donnees_armoire["intensites"]
        
        # 3. On transforme la liste des casiers en un dictionnaire intelligent.
        # Clé = un tuple (ligne, colonne), Valeur = le contenu du casier.
        # Cela permet d'accéder instantanément à un casier par ses coordonnées.
        self.casiers = { (c["ligne"], c["colonne"]): c for c in donnees_armoire["casiers"] }
        
        # 4. On enregistre la position de départ du bras sélecteur dans l'armoire
        self.position_selecteur = donnees_armoire["casier_depart"]


    def trier_candidats(self, emotion_cible, intensite_cible):
        # 1. On trouve l'indice numérique (de 0 à 7) de l'émotion recherchée sur la roue
        idx_e = self.emotions.index(emotion_cible)
        
        # 2. On trouve l'indice numérique (de 0 à 2) de l'intensité recherchée
        idx_i = self.intensites.index(intensite_cible)
        
        candidats = []
        # 3. On boucle sur TOUS les casiers de l'armoire un par un ((l, c) = ligne, colonne)
        for (l, c), contenu in self.casiers.items():
            
            # --- CRITÈRE 1 : La distance sur la roue (avec bouclage) ---
            ecart_brut = abs(c - idx_e)
            # Puisque la roue est un cercle de 8 émotions (le cas 7 est voisin du cas 0),
            # on calcule le plus court chemin sur le cercle : min(écart direct, 8 - écart direct).
            dist_roue = min(ecart_brut, 8 - ecart_brut)
            
            # L'énoncé exige qu'on ne garde que les émotions situées à une distance <= 2 sur la roue
            if dist_roue <= 2:
                
                # --- CRITÈRE 2 : L'écart d'intensité (différence de lignes) ---
                ecart_intensite = abs(l - idx_i)
                
                # --- CRITÈRE 4 : Le sens horaire prioritaire ---
                sens = (c - idx_e) % 8
                # Si le sens dépasse 4, c'est qu'on tourne dans le sens anti-horaire (on met la valeur 1, sinon 0)
                est_antihoraire = 1 if sens > 4 else 0
                
                # --- LA CLÉ DE TRI UNIQUE (Le secret de Python) ---
                # Python sait trier naturellement les tuples de gauche à droite.
                # Il va classer d'abord par dist_roue (le plus petit), 
                # puis par ecart_intensite, puis par la ligne 'l', puis par sens horaire.
                cle_tri = (dist_roue, ecart_intensite, l, est_antihoraire)
                
                # On ajoute ce casier et sa clé de tri dans notre liste de candidats
                candidats.append((cle_tri, (l, c)))
        
        # 4. On trie automatiquement tous les casiers grâce à la clé de tri calculée
        candidats.sort(key=lambda x: x[0])
        
        # 5. On extrait et renvoie uniquement les coordonnées (l, c) ordonnées du meilleur au pire casier
        return [c[1] for c in candidats]


    def calculer_deplacements(self, depart, arrivee):
        mouvements = []
        l_dep, c_dep = depart
        l_arr, c_arr = arrivee
        
        # 1. Déplacements verticaux (lignes de 0 à 2)
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