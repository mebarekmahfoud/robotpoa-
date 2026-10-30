from reconfort_io import ErreurFichier


def _verifier_pos(pos, hauteur, largeur, nom_champ):
    if (
        not isinstance(pos, list)
        or len(pos) != 2
        or not all(isinstance(x, int) and not isinstance(x, bool) for x in pos)
    ):
        raise ErreurFichier(f"Position invalide pour {nom_champ}")
    l, c = pos
    if not (0 <= l < hauteur and 0 <= c < largeur):
        raise ErreurFichier(f"Position {pos} hors de la grille pour {nom_champ}")
    return l, c


def valider_donnees(carte, dico, armoire, scenario):
    # 1. Validation de la carte
    for champ in ("nom", "dimensions", "grille", "depart_robot", "armoire", "dictionnaire", "residents"):
        if champ not in carte:
            raise ErreurFichier(f"Champ '{champ}' manquant dans la carte")

    if not isinstance(carte["nom"], str) or not isinstance(carte["dimensions"], dict):
        raise ErreurFichier("Type invalide dans l'en-tête de la carte")

    h = carte["dimensions"].get("hauteur")
    w = carte["dimensions"].get("largeur")
    if not isinstance(h, int) or not isinstance(w, int) or h < 3 or w < 3:
        raise ErreurFichier("Dimensions de grille invalides")

    grille = carte["grille"]
    if not isinstance(grille, list) or len(grille) != h:
        raise ErreurFichier("Hauteur de grille incohérente avec les dimensions")

    for l, ligne in enumerate(grille):
        if not isinstance(ligne, str) or len(ligne) != w:
            raise ErreurFichier("Grille non rectangulaire ou largeur incohérente")
        for c, ch in enumerate(ligne):
            if ch not in ("#", ".", "R", "A", "D", "P"):
                raise ErreurFichier(f"Symbole inconnu '{ch}' dans la grille")
            if (l == 0 or l == h - 1 or c == 0 or c == w - 1) and ch != "#":
                raise ErreurFichier("Le bord de la grille doit être constitué de murs '#'")

    rl, rc = _verifier_pos(carte["depart_robot"], h, w, "depart_robot")
    if grille[rl][rc] != "R":
        raise ErreurFichier("depart_robot ne correspond pas à 'R' dans la grille")

    if not isinstance(carte["armoire"], dict) or "position" not in carte["armoire"]:
        raise ErreurFichier("Champ armoire.position manquant")
    al, ac = _verifier_pos(carte["armoire"]["position"], h, w, "armoire")
    if grille[al][ac] != "A":
        raise ErreurFichier("La position de l'armoire ne correspond pas à 'A'")

    if not isinstance(carte["dictionnaire"], dict) or "position" not in carte["dictionnaire"]:
        raise ErreurFichier("Champ dictionnaire.position manquant")
    dl, dc = _verifier_pos(carte["dictionnaire"]["position"], h, w, "dictionnaire")
    if grille[dl][dc] != "D":
        raise ErreurFichier("La position du dictionnaire ne correspond pas à 'D'")

    if not isinstance(carte["residents"], list) or len(carte["residents"]) == 0:
        raise ErreurFichier("Liste des résidents invalide")

    ids_residents = set()
    for res in carte["residents"]:
        if not isinstance(res, dict) or "id" not in res or "nom" not in res or "position" not in res:
            raise ErreurFichier("Résident mal formé")
        if not isinstance(res["id"], str) or not isinstance(res["nom"], str):
            raise ErreurFichier("Identifiant ou nom de résident invalide")
        if res["id"] in ids_residents:
            raise ErreurFichier(f"Résident en double : {res['id']}")
        ids_residents.add(res["id"])
        pl, pc = _verifier_pos(res["position"], h, w, f"resident {res['id']}")
        if grille[pl][pc] != "P":
            raise ErreurFichier(f"Le résident {res['id']} n'est pas sur une case 'P'")

    # 2. Validation du dictionnaire
    for champ in ("nom", "emotions", "intensites", "entrees"):
        if champ not in dico:
            raise ErreurFichier(f"Champ '{champ}' manquant dans le dictionnaire")

    emotions_ref = dico["emotions"]
    intensites_ref = dico["intensites"]
    if (
        not isinstance(emotions_ref, list)
        or len(emotions_ref) != 8
        or not isinstance(intensites_ref, list)
        or len(intensites_ref) != 3
        or not isinstance(dico["entrees"], list)
    ):
        raise ErreurFichier("Structure du dictionnaire invalide")

    mots_vus = set()
    for entree in dico["entrees"]:
        if not isinstance(entree, dict):
            raise ErreurFichier("Entrée de dictionnaire invalide")
        formes = entree.get("formes")
        emo = entree.get("emotion")
        inten = entree.get("intensite")
        if not isinstance(formes, list) or not formes:
            raise ErreurFichier("Champ 'formes' invalide dans le dictionnaire")
        if emo not in emotions_ref or inten not in intensites_ref:
            raise ErreurFichier(f"Émotion '{emo}' ou intensité '{inten}' inconnue")
        for mot in formes:
            if not isinstance(mot, str) or not mot:
                raise ErreurFichier("Mot invalide dans le dictionnaire")
            if mot in mots_vus:
                raise ErreurFichier(f"Mot '{mot}' présent dans plusieurs entrées")
            mots_vus.add(mot)

    # 3. Validation de l'armoire
    for champ in ("nom", "emotions", "intensites", "casier_depart", "casiers"):
        if champ not in armoire:
            raise ErreurFichier(f"Champ '{champ}' manquant dans l'armoire")

    if armoire["emotions"] != emotions_ref or armoire["intensites"] != intensites_ref:
        raise ErreurFichier("Émotions ou intensités de l'armoire incohérentes avec le dictionnaire")

    _verifier_pos(armoire["casier_depart"], 3, 8, "casier_depart")

    if not isinstance(armoire["casiers"], list):
        raise ErreurFichier("Champ 'casiers' invalide")

    casiers_vus = set()
    for casier in armoire["casiers"]:
        if not isinstance(casier, dict):
            raise ErreurFichier("Casier mal formé")
        for ch in ("ligne", "colonne", "emotion", "intensite", "objet"):
            if ch not in casier:
                raise ErreurFichier(f"Champ '{ch}' manquant dans un casier")
        cl, cc = _verifier_pos([casier["ligne"], casier["colonne"]], 3, 8, "casier")
        if (cl, cc) in casiers_vus:
            raise ErreurFichier(f"Casier {(cl, cc)} en double dans l'armoire")
        casiers_vus.add((cl, cc))
        if casier["intensite"] != intensites_ref[cl] or casier["emotion"] != emotions_ref[cc]:
            raise ErreurFichier(f"Étiquette emotion/intensite incohérente pour le casier {(cl, cc)}")
        if casier["objet"] is not None and not isinstance(casier["objet"], str):
            raise ErreurFichier("Le champ 'objet' d'un casier doit être une chaîne ou null")

    # 4. Validation du scénario
    for champ in ("nom", "carte", "armoire", "demandes"):
        if champ not in scenario:
            raise ErreurFichier(f"Champ '{champ}' manquant dans le scénario")

    if scenario["carte"] != carte["nom"]:
        raise ErreurFichier(f"Scénario prévu pour la carte '{scenario['carte']}', pas '{carte['nom']}'")

    if not isinstance(scenario["demandes"], list):
        raise ErreurFichier("Liste des demandes invalide dans le scénario")

    for dem in scenario["demandes"]:
        if not isinstance(dem, dict):
            raise ErreurFichier("Demande mal formée")
        if "numero" not in dem or "resident" not in dem or "message" not in dem:
            raise ErreurFichier("Champ obligatoire manquant dans une demande")
        if not isinstance(dem["numero"], int) or not isinstance(dem["message"], str):
            raise ErreurFichier("Type invalide dans une demande")
        if dem["resident"] not in ids_residents:
            raise ErreurFichier(f"Résident '{dem['resident']}' absent de la carte")