from analyseur import AnalyseurLinguistique
import unicodedata
import re
from analyseur import AnalyseurLinguistique
from gestion_armoire import GestionnaireArmoire


class Robot:
    def __init__(self, donnees_carte):
        # BLOC 1 : Extraction des données du JSON
        self.position = donnees_carte["depart_robot"]
        self.hauteur = donnees_carte["dimensions"]["hauteur"]
        self.largeur = donnees_carte["dimensions"]["largeur"]
        self.position_armoire = donnees_carte["armoire"]["position"]

        self.vraie_grille_secrete = donnees_carte["grille"]

        self.position_dictionnaire = donnees_carte["dictionnaire"]["position"]
        # On crée un dictionnaire pratique pour retrouver la position d'un résident grâce à son ID (ex: "R1")
        self.residents = {r["id"]: r["position"] for r in donnees_carte["residents"]}
        
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


    def aller_vers(self, destination):
        # On calcule les 4 cases adjacentes à la cible
        cases_cibles = self.obtenir_voisins(destination)
        
        # Tant que le robot n'est pas SUR l'une de ces 4 cases adjacentes
        while self.position not in cases_cibles:
            
            # On calcule le chemin vers le centre de la cible
            chemin = self.calculer_chemin(self.position, destination)
            prochaine_case = chemin[1] 
            
            resultat = self.simuler_un_pas(prochaine_case)
            
            if resultat == "mur":
                self.memoire_robot[str(prochaine_case)] = "mur"
                print(f"Aïe ! Mur découvert en {prochaine_case}, recalcul...")
                continue
            else:
                self.position = prochaine_case
                print(f"Le robot avance sur la case {self.position}")
                
        print(f"Arrivé à côté de la cible {destination}, prêt à interagir !")


    def simuler_un_pas(self, prochaine_case):
            ligne = prochaine_case[0]
            colonne = prochaine_case[1]
        
        # On vérifie la vraie nature de la case dans la grille secrète
            contenu_case = self.vraie_grille_secrete[ligne][colonne]
        
            if contenu_case == "#":
                return "mur"
            else:
                return "ok"

if __name__ == "__main__":
    import sys
    import json
    import os
    
    # --- EXPLICATION : Vérification des arguments du terminal ---
    # Le programme exige exactement 4 arguments (script, carte, scenario, dossier_donnees, sortie)
    if len(sys.argv) < 5:
        sys.exit(1)
        
    dossier_donnees = sys.argv[3]
    chemin_dico = os.path.join(dossier_donnees, "dictionnaire.json")
        
    # --- EXPLICATION : Chargement sécurisé des fichiers de configuration JSON ---
    with open(sys.argv[1], "r", encoding="utf-8") as f:
        donnees_carte = json.load(f)
    with open(sys.argv[2], "r", encoding="utf-8") as f:
        donnees_scenario = json.load(f)
    with open(chemin_dico, "r", encoding="utf-8") as f:
        donnees_dico = json.load(f)

    # --- EXPLICATION : Récupération dynamique du meuble de stockage ---
    # Le nom de l'armoire change selon les scénarios, on le lit directement dans le fichier scénario
    nom_armoire = donnees_scenario["armoire"] 
    chemin_armoire = os.path.join(dossier_donnees, f"{nom_armoire}.json")
    with open(chemin_armoire, "r", encoding="utf-8") as f:
        donnees_armoire = json.load(f)

    # --- EXPLICATION : Instanciation des trois composants de l'architecture ---
    # Le Robot gère le déplacement, l'Analyseur traite le texte, et le Gestionnaire gère l'armoire
    wall_e = Robot(donnees_carte)
    analyseur = AnalyseurLinguistique(donnees_dico)
    armoire = GestionnaireArmoire(donnees_armoire)

    # --- EXPLICATION : Boucle principale d'exécution des missions du scénario ---
    for demande in donnees_scenario["demandes"]:
        id_resident = demande["resident"]
        
        print(f"\n=== Demande {demande['numero']} pour {id_resident} ===")
        
        # Étape 1 : Le robot navigue jusqu'au dictionnaire pour lire la détresse du résident
        wall_e.aller_vers(wall_e.position_dictionnaire)
        
        # L'analyseur externe traduit le message textuel en une émotion et une intensité normalisées
        emotion, intensite = analyseur.trouver_emotion(demande["message"])
        print(f"-> Analyse : Émotion = {emotion}, Intensité = {intensite}")
        
        # Étape 2 : Le robot se déplace ensuite physiquement devant l'armoire de stockage
        wall_e.aller_vers(wall_e.position_armoire)
        
        if emotion != "emotion indeterminee":
            # On interroge le gestionnaire d'armoire pour obtenir la liste ordonnée des casiers prioritaires (Roue de Plutchik)
            tiroirs_a_verifier = armoire.trier_candidats(emotion, intensite)
            
            # On sélectionne le meilleur casier (le premier de la liste de priorité)
            meilleur_tiroir = tiroirs_a_verifier[0]
            
            # On calcule la trajectoire géométrique du bras mécanique (avec bouclage toroïdal horizontal)
            mouvements = armoire.calculer_deplacements(armoire.position_selecteur, meilleur_tiroir)
            print(f"-> Fouille : Le bras se déplace vers {meilleur_tiroir} avec les mouvements {mouvements}")
            
            # On met à jour la position actuelle du sélecteur pour qu'il s'en souvienne lors de la prochaine demande
            armoire.position_selecteur = meilleur_tiroir
        else:
            print("-> Fouille : Impossible, émotion indéterminée.")
        
        # Étape 3 : Enfin, le robot quitte l'armoire pour aller livrer l'objet de réconfort au résident concerné
        wall_e.aller_vers(wall_e.residents[id_resident])