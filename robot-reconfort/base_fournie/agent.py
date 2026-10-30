import sys
from collections import deque
from pathlib import Path

import reconfort_io as rio
from analyseur import AnalyseurLinguistique
from gestion_armoire import GestionnaireArmoire
from simulateur import Simulateur
from validation import valider_donnees


class Robot:
    def __init__(self, donnees_carte):
        # BLOC 1 : Extraction des données publiques du JSON (SANS la grille !)
        self.position = list(donnees_carte["depart_robot"])
        self.hauteur = donnees_carte["dimensions"]["hauteur"]
        self.largeur = donnees_carte["dimensions"]["largeur"]
        self.position_armoire = list(donnees_carte["armoire"]["position"])
        self.position_dictionnaire = list(donnees_carte["dictionnaire"]["position"])

        # On crée un dictionnaire pratique pour retrouver la position d'un résident grâce à son ID (ex: "R1")
        self.residents = {r["id"]: list(r["position"]) for r in donnees_carte["residents"]}

        # BLOC 2 : Création de la carte mentale (cerveau du robot)
        # Dès le départ, le robot sait que l'armoire, le dictionnaire et les résidents
        # sont des cases non traversables (Section 3.1 et 3.2 de l'énoncé).
        self.memoire_robot = {}
        self.memoire_robot[str(self.position_armoire)] = "armoire"
        self.memoire_robot[str(self.position_dictionnaire)] = "dictionnaire"
        for pos_res in self.residents.values():
            self.memoire_robot[str(pos_res)] = "resident"

    # BLOC 3 : Obtenir les 4 voisins orthogonaux d'une position
    def obtenir_voisins(self, position_actuelle):
        ligne = position_actuelle[0]
        colonne = position_actuelle[1]

        voisins = [
            [ligne - 1, colonne],  # Nord
            [ligne + 1, colonne],  # Sud
            [ligne, colonne + 1],  # Est
            [ligne, colonne - 1],  # Ouest
        ]
        return voisins

    # BLOC 4 : PERCEPTION — Mise à jour de la carte mentale avec les capteurs locaux
    def observer_alentours(self, perception, contenu_casier, armoire):
        l, c = self.position
        directions = {
            "N": [l - 1, c],
            "S": [l + 1, c],
            "E": [l, c + 1],
            "O": [l, c - 1],
        }
        # Le robot inscrit le type des 4 cases adjacentes dans sa mémoire
        for dir_code, coord in directions.items():
            self.memoire_robot[str(coord)] = perception[dir_code]

        # S'il est à côté de l'armoire, il mémorise aussi ce qu'il voit dans le casier courant
        if self. position in self.obtenir_voisins(self.position_armoire):
            armoire.memoire_casiers[str(armoire.position_selecteur)] = contenu_casier

    # BLOC 5 : DÉCISION — Calcul du plus court chemin (Parcours en largeur BFS)
    def calculer_chemin(self, depart, destination):
        # Les cases d'arrivée possibles sont les 4 cases adjacentes à la cible
        # qui ne sont pas des obstacles connus.
        cases_cibles = []
        for v in self.obtenir_voisins(destination):
            if 0 <= v[0] < self.hauteur and 0 <= v[1] < self.largeur:
                type_connu = self.memoire_robot.get(str(v), "libre")
                if type_connu == "libre":
                    cases_cibles.append(v)

        if not cases_cibles:
            return None  # Toutes les cases autour de la cible sont bloquées !

        if depart in cases_cibles:
            return [depart]

        # 1. On met la case de départ dans la file d'attente (deque imposée par Annexe B.4)
        a_visiter = deque([depart])

        # 2. On note que le départ n'a pas de parent (c'est l'origine)
        # On utilise str() pour transformer la liste en texte, car les dictionnaires préfèrent le texte
        parents = {str(depart): None}

        case_atteinte = None

        # Tant qu'il reste des cases à vérifier dans la file
        while len(a_visiter) > 0:
            # On retire la case la plus ancienne de la file (popleft = temps constant O(1))
            case_en_cours = a_visiter.popleft()

            # Si on a atteint l'une des cases adjacentes à la destination, on arrête tout !
            if case_en_cours in cases_cibles:
                case_atteinte = case_en_cours
                break

            # Sinon, on récupère ses 4 voisins
            voisins = self.obtenir_voisins(case_en_cours)

            for voisin in voisins:
                # On vérifie que le voisin reste bien dans les limites de la grille
                if not (0 <= voisin[0] < self.hauteur and 0 <= voisin[1] < self.largeur):
                    continue

                voisin_str = str(voisin)

                # Règle 1 : La case est-elle traversable dans notre mémoire ?
                # La commande self.memoire_robot.get(..., "libre") regarde dans le carnet de notes.
                # Si la case est inconnue, l'hypothèse optimiste s'applique : elle est supposée "libre".
                # Si c'est un "mur", "armoire", "dictionnaire" ou "resident", elle n'est pas traversable.
                est_traversable = self.memoire_robot.get(voisin_str, "libre") == "libre"

                # Règle 2 : On ne l'a pas déjà ajouté à notre historique
                # L'ignorer empêche le code de tourner en rond à l'infini ou de revenir en arrière.
                deja_visite = voisin_str in parents

                if est_traversable and not deja_visite:
                    a_visiter.append(voisin)  # On le met dans la file d'attente
                    parents[voisin_str] = case_en_cours  # On mémorise de quelle case on vient

        # Si la file est vide et qu'aucune case cible n'a été atteinte, aucun chemin n'existe !
        if case_atteinte is None:
            return None

        # 3. Reconstruction de l'itinéraire
        chemin = []
        case_actuelle = case_atteinte

        # On remonte de parent en parent jusqu'au départ (qui a pour parent 'None')
        while case_actuelle is not None:
            chemin.append(case_actuelle)
            case_actuelle = parents.get(str(case_actuelle))

        # Comme on est parti de la fin, on inverse la liste pour l'avoir dans le bon sens
        chemin.reverse()

        return chemin

    # Traduit deux coordonnées adjacentes en direction cardinale ("N", "S", "E", "O")
    def trouver_direction(self, depart, arrivee):
        dl = arrivee[0] - depart[0]
        dc = arrivee[1] - depart[1]
        if dl == -1 and dc == 0:
            return "N"
        if dl == 1 and dc == 0:
            return "S"
        if dl == 0 and dc == 1:
            return "E"
        if dl == 0 and dc == -1:
            return "O"
        raise ValueError("Cases non adjacentes")

    # BLOC 6 : ACTION — Déplacement pas à pas avec perception locale à chaque tour
    def aller_vers(self, destination, simulateur, armoire, num_demande):
        cases_cibles = self.obtenir_voisins(destination)

        # Tant que le robot n'est pas SUR l'une des 4 cases adjacentes à la cible
        while self.position not in cases_cibles:
            # 1. Percevoir les 4 cases adjacentes AVANT de décider (Annexe B.5)
            perception, contenu = simulateur.percevoir()
            self.observer_alentours(perception, contenu, armoire)

            # 2. Calculer le plus court chemin sur la carte mentale mise à jour
            chemin = self.calculer_chemin(self.position, destination)
            if chemin is None or len(chemin) < 2:
                # Preuve mathématique qu'aucun chemin n'existe (Annexe B.6)
                return False

            # 3. Faire un seul pas sur ce chemin et l'enregistrer dans la Trace
            prochaine_case = chemin[1]
            direction = self.trouver_direction(self.position, prochaine_case)
            simulateur.executer_action(num_demande, "AVANCER", direction)
            self.position = prochaine_case

        # Mise à jour des capteurs une fois arrivé à côté de la cible
        perception, contenu = simulateur.percevoir()
        self.observer_alentours(perception, contenu, armoire)
        return True

    # BLOC 7 : ACTION — Fouille réelle de l'armoire casier par casier
    def fouiller_armoire(self, emotion, intensite, armoire, simulateur, num_demande):
        candidats = armoire.trier_candidats(emotion, intensite)

        for casier_cible, repli in candidats:
            # Si on est déjà passé devant ce casier et qu'on sait qu'il est vide, on passe au suivant
            if (
                str(casier_cible) in armoire.memoire_casiers
                and armoire.memoire_casiers[str(casier_cible)] is None
            ):
                continue

            # Calcul et exécution des mouvements du sélecteur vers ce casier candidat
            mouvements = armoire.calculer_deplacements(armoire.position_selecteur, casier_cible)
            for mouv in mouvements:
                perception, contenu = simulateur.percevoir()
                self.observer_alentours(perception, contenu, armoire)

                simulateur.executer_action(num_demande, "CHERCHER", mouv)
                l, c = armoire.position_selecteur
                if mouv == "N":
                    armoire.position_selecteur = [l - 1, c]
                elif mouv == "S":
                    armoire.position_selecteur = [l + 1, c]
                elif mouv == "E":
                    armoire.position_selecteur = [l, (c + 1) % 8]
                elif mouv == "O":
                    armoire.position_selecteur = [l, (c - 1) % 8]

            # Une fois devant le casier candidat, le robot regarde son contenu
            perception, contenu_actuel = simulateur.percevoir()
            self.observer_alentours(perception, contenu_actuel, armoire)

            if contenu_actuel is not None:
                # Le casier contient un objet ! Le robot le prend.
                simulateur.executer_action(num_demande, "PRENDRE", contenu_actuel)
                return casier_cible, repli, contenu_actuel

        # Si le dernier casier vérifié est vide, on fait ATTENDRE pour journaliser sa perception vide
        simulateur.executer_action(num_demande, "ATTENDRE")
        return None, "aucun", None


def main(argv):
    # --- EXPLICATION : Vérification des arguments du terminal ---
    if len(argv) != 5:
        print(
            "Usage: python agent.py <carte> <scenario> <dossier_donnees> <sortie>",
            file=sys.stderr,
        )
        return 2

    chemin_carte, chemin_scenario = Path(argv[1]), Path(argv[2])
    dossier_donnees, chemin_sortie = Path(argv[3]), Path(argv[4])

    # --- EXPLICATION : Chargement et validation stricte des 4 fichiers JSON (Section 5.6) ---
    try:
        donnees_carte = rio.charger_carte(chemin_carte)
        donnees_scenario = rio.charger_scenario(chemin_scenario)
        donnees_dico = rio.charger_dictionnaire(dossier_donnees / "dictionnaire.json")
        nom_armoire = donnees_scenario.get("armoire")
        if not isinstance(nom_armoire, str):
            raise rio.ErreurFichier("Champ 'armoire' manquant ou invalide dans le scénario")
        donnees_armoire = rio.charger_armoire(dossier_donnees / f"{nom_armoire}.json")

        # Vérifie la cohérence complète (grille rectangulaire, bornes, doublons, etc.)
        valider_donnees(donnees_carte, donnees_dico, donnees_armoire, donnees_scenario)
    except rio.ErreurFichier as err:
        print(f"Erreur de fichier : {err}", file=sys.stderr)
        return 1

    # --- EXPLICATION : Instanciation des composants de l'architecture ---
    simulateur = Simulateur(
        donnees_carte=donnees_carte,
        donnees_armoire=donnees_armoire,
        donnees_scenario=donnees_scenario,
        equipe=["MEBAREK Mahfoud Rabah", "CHEGHOUB Aymen"],
    )

    # Le robot et le gestionnaire d'armoire ne reçoivent QUE les données publiques !
    wall_e = Robot(simulateur.carte_publique)
    analyseur = AnalyseurLinguistique(donnees_dico)
    armoire = GestionnaireArmoire(simulateur.armoire_publique)

    # --- EXPLICATION : Boucle principale d'exécution des missions du scénario ---
    for demande in donnees_scenario["demandes"]:
        num = demande["numero"]
        id_resident = demande["resident"]

        # Étape 1 : Aller au dictionnaire
        if not wall_e.aller_vers(wall_e.position_dictionnaire, simulateur, armoire, num):
            simulateur.trace.ajouter_livraison(
                demande=num, resident=id_resident, emotion=None, intensite=None,
                casier_choisi=None, repli="aucun", objet=None,
                succes=False, motif_echec="resident inaccessible",
            )
            continue

        # Étape 2 : Consulter le dictionnaire et analyser le message
        simulateur.executer_action(num, "CONSULTER")
        emotion, intensite = analyseur.trouver_emotion(demande["message"])
        if emotion == "emotion indeterminee":
            simulateur.trace.ajouter_livraison(
                demande=num, resident=id_resident, emotion=None, intensite=None,
                casier_choisi=None, repli="aucun", objet=None,
                succes=False, motif_echec="emotion indeterminee",
            )
            continue

        # Étape 3 : Aller à l'armoire
        if not wall_e.aller_vers(wall_e.position_armoire, simulateur, armoire, num):
            simulateur.trace.ajouter_livraison(
                demande=num, resident=id_resident, emotion=emotion, intensite=intensite,
                casier_choisi=None, repli="aucun", objet=None,
                succes=False, motif_echec="resident inaccessible",
            )
            continue

        # Étape 4 : Fouiller l'armoire et prendre l'objet
        casier_choisi, repli, objet = wall_e.fouiller_armoire(
            emotion, intensite, armoire, simulateur, num
        )
        if objet is None:
            simulateur.trace.ajouter_livraison(
                demande=num, resident=id_resident, emotion=emotion, intensite=intensite,
                casier_choisi=None, repli="aucun", objet=None,
                succes=False, motif_echec="armoire vide",
            )
            continue

        # Étape 5 : Aller livrer l'objet au résident
        if not wall_e.aller_vers(wall_e.residents[id_resident], simulateur, armoire, num):
            simulateur.trace.ajouter_livraison(
                demande=num, resident=id_resident, emotion=emotion, intensite=intensite,
                casier_choisi=casier_choisi, repli=repli, objet=objet,
                succes=False, motif_echec="resident inaccessible",
            )
            continue

        simulateur.executer_action(num, "DONNER", objet)
        simulateur.trace.ajouter_livraison(
            demande=num, resident=id_resident, emotion=emotion, intensite=intensite,
            casier_choisi=casier_choisi, repli=repli, objet=objet,
            succes=True, motif_echec=None,
        )

    # Écriture finale du fichier sortie.json
    simulateur.trace.ecrire(chemin_sortie)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))