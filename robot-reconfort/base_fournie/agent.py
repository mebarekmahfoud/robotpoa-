class Robot:
    def __init__(self, donnees_carte):
        # BLOC 1 : Extraction des données du JSON
        self.position = donnees_carte["depart_robot"]
        self.hauteur = donnees_carte["dimensions"]["hauteur"]
        self.largeur = donnees_carte["dimensions"]["largeur"]
        self.position_armoire = donnees_carte["armoire"]["position"]

        self.vraie_grille_secrete = donnees_carte["grille"]
        
        # BLOC 2 : Création de la carte mentale (cerveau vierge)
        self.memoire_robot = {}

    # BLOC 3 : Obtenir voisin de position 
    def obtenir_voisins(self, position_actuelle):
        ligne = position_actuelle[0]
        colonne = position_actuelle[1]
        
        voisins = [
            [ligne - 1, colonne], # Nord
            [ligne + 1, colonne], # Sud
            [ligne, colonne + 1], # Est
            [ligne, colonne - 1]  # Ouest
        ]
        return voisins
    




    def calculer_chemin(self, depart, destination):
        # 1. On met la case de départ dans la file d'attente
        
        a_visiter = [depart] 
        
        # 2. On note que le départ n'a pas de parent (c'est l'origine)
        # On utilise str() pour transformer la liste en texte, car les dictionnaires préfèrent le texte
        parents = {str(depart): None} 
        
        # La boucle d'exploration arrivera ici...

        # Tant qu'il reste des cases à vérifier
        while len(a_visiter) > 0:
            # On prend la première case de la file
            case_en_cours = a_visiter.pop(0)
            
            # Si c'est la destination, on arrête tout !
            if case_en_cours == destination:
                break
                
            # Sinon, on récupère ses 4 voisins
            voisins = self.obtenir_voisins(case_en_cours)
            
            for voisin in voisins:
                voisin_str = str(voisin)
                
                # Règle 1 : Ce n'est pas un mur connu dans notre mémoire
                # La commande self.memoire_robot.get(...) regarde dans le 
                # carnet de notes si un mur a été enregistré à ces coordonnées.
                #  Si c'est le cas, la variable est_un_mur devient True.
                #  Si la case est totalement inconnue, la mémoire ne trouve rien,
                #  l'hypothèse optimiste s'applique, et la variable vaut False.
                est_un_mur = self.memoire_robot.get(voisin_str) == "mur"

                # Règle 2 : On ne l'a pas déjà ajouté à notre historique
                # La vérification in parents regarde si cette case possède déjà un parent.
                #  Si oui, cela signifie que notre algorithme a déjà inondé cette case en venant d'un autre
                #  chemin plus court. L'ignorer empêche le code de tourner en rond à l'infini 
                # ou de revenir en arrière.             
                deja_visite = voisin_str in parents
                
                if not est_un_mur and not deja_visite:
                    a_visiter.append(voisin) # On le met dans la file d'attente
                    parents[voisin_str] = case_en_cours # On mémorise de quelle case on vient



        
        # 3. Reconstruction de l'itinéraire
        chemin = []
        case_actuelle = destination
        
        # On remonte de parent en parent jusqu'au départ (qui a pour parent 'None')
        while case_actuelle is not None:
            chemin.append(case_actuelle)
            case_actuelle = parents.get(str(case_actuelle))
            
        # Comme on est parti de la fin, on inverse la liste pour l'avoir dans le bon sens
        chemin.reverse()
        
        return chemin


    def lancer_mission(self):
        # Tant qu'on n'est pas arrivé à l'armoire
        while self.position != self.position_armoire:
            
            # 1. Le robot calcule son trajet idéal
            chemin = self.calculer_chemin(self.position, self.position_armoire)
            
            # 2. Il repère la case de son tout premier pas
            prochaine_case = chemin[1] 
            
            # 3. Il tente d'avancer via notre maître du jeu interne
            resultat = self.simuler_un_pas(prochaine_case)
            
            # 4. L'apprentissage
            if resultat == "mur":
                self.memoire_robot[str(prochaine_case)] = "mur"
                continue # redemarre la boucle while 
            else:
                self.position = prochaine_case
                print(f"Le robot avance sur la case {self.position}")
                
        print("L'armoire a été trouvée !")



    def simuler_un_pas(self, prochaine_case):
            ligne = prochaine_case[0]
            colonne = prochaine_case[1]
        
        # On vérifie la vraie nature de la case dans la grille secrète
            contenu_case = self.vraie_grille_secrete[ligne][colonne]
        
            if contenu_case == "mur":
                return "mur"
            else:
                return "ok"