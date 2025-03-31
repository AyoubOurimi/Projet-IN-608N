import tkinter as tk
import tkinter.messagebox as messagebox
from tkinter import ttk
import random as random
import time

class Othello:
    def __init__(self, fenetre, mode_ia=False, couleur_ia=None):
        self.fenetre = fenetre
        self.fenetre.title("Othello")

        icone = tk.PhotoImage(file="Othello/Logo_Tkinter.png")
        self.fenetre.iconphoto(False, icone)

        self.image_plateau = tk.PhotoImage(file="Othello/Plateau.png")
        self.size = 8  # Taille du plateau (8x8)
        self.image_size = self.image_plateau.width()  # supposé carré
        self.marge = 17.5  # bordure autour du plateau
        self.cellules_size = (self.image_size - 2 * self.marge) / 8

        self.canvas = tk.Canvas(self.fenetre,width=self.image_plateau.width(),height=self.image_plateau.height())
        self.canvas.pack()
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.image_plateau) #affichage de l'image

        self.pion_noir_img = tk.PhotoImage(file="Othello/pion_noir.png")
        self.pion_blanc_img = tk.PhotoImage(file="Othello/pion_blanc.png")
        self.pion_gris_img = tk.PhotoImage(file="Othello/pion_gris.png")

        self.mode_ia = mode_ia
        self.couleur_ia = couleur_ia
        if self.mode_ia:
            self.ai_player = IAOthello(jeu=self, couleur=self.couleur_ia, profondeur_max=5)

        self.NOIR = "N"
        self.BLANC = "B"

        self.plateau = [[None for _ in range(self.size)] for _ in range(self.size)]
        mid = self.size // 2
        self.plateau[mid - 1][mid - 1] = self.BLANC
        self.plateau[mid - 1][mid]     = self.NOIR
        self.plateau[mid][mid - 1]     = self.NOIR
        self.plateau[mid][mid]         = self.BLANC

        self.canvas.bind("<Button-1>", self.gerer_clic)
        self.joueur_courant = self.NOIR

        self.score_label = tk.Label(self.fenetre, font=("Arial", 14))
        self.score_label.pack(pady=10)
        self.mise_à_jour_scores()
        self.dessiner_plateau()

        self.blink_state = False
        self.clignotement_delay = 1000  # ms
        self.fenetre.after(self.clignotement_delay, self.clignoter)

        if self.mode_ia and self.joueur_courant == self.couleur_ia:
            self.faire_jouer_ia()
            

    def dessiner_plateau(self):
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.image_plateau)

        for lig in range(self.size):
            for col in range(self.size):
                x1 = self.marge + col * self.cellules_size
                y1 = self.marge + lig * self.cellules_size
                x2 = x1 + self.cellules_size
                y2 = y1 + self.cellules_size

                if self.plateau[lig][col] == self.NOIR:
                    self.canvas.create_image((x1 + x2) // 2, (y1 + y2) // 2, image=self.pion_noir_img)
                elif self.plateau[lig][col] == self.BLANC:
                    self.canvas.create_image((x1 + x2) // 2, (y1 + y2) // 2, image=self.pion_blanc_img)

        self.afficher_coups_jouables()

    def gerer_clic(self, event):
        col = int((event.x - self.marge) // self.cellules_size)
        lig = int((event.y - self.marge) // self.cellules_size)

        if 0 <= lig < self.size and 0 <= col < self.size:
            if self.coup_valide(lig, col, self.joueur_courant):
                joueur_actuel = self.joueur_courant

                # on place le pion car valide, et on retourne les pions adverses
                self.plateau[lig][col] = joueur_actuel
                self.retourner_pions(lig, col, joueur_actuel)

                self.mise_à_jour_scores()
                self.dessiner_plateau()

                # on cherche à déterminer le joueur suivant
                prochain = self.BLANC if self.joueur_courant == self.NOIR else self.NOIR

                if not self.peut_jouer(self.joueur_courant) and not self.peut_jouer(prochain):
                    self.verifier_fin_partie()
                    return
                if not self.peut_jouer(prochain):
                    messagebox.showinfo("Passer le tour", f"Le joueur {prochain} ne peut pas jouer. Le tour reste au joueur {self.joueur_courant}.")
                    if self.mode_ia and self.joueur_courant == self.couleur_ia:
                        self.faire_jouer_ia()
                else:
                    self.joueur_courant = prochain
                    if self.mode_ia and self.joueur_courant == self.couleur_ia:
                        self.faire_jouer_ia()
                
                if self.mode_ia:
                    self.test_diff_ia() #test pour verif la diff des pions
                    self.test_coins_ia() #test pour verif les pions des coins 
                    self.test_get_valid_moves() #test pour verif les coup valide sous forme de liste
                    self.test_mobilite() #test pour verif qui a le plus de mobilite entre IA et joueur
                    self.test_stabilite() #test le nbre de pions non retournables
                    self.test_triangles() #test zone triangulaire (dangereux)
                    self.test_cases_dangereuses() #test verif les case dangereuses (bord)
                    self.test_apply_move() #test pour voir le calcul des prochains coups possibles

                if not self.partie_terminee():
                    self.dessiner_plateau()  
                
                #on vérif dès que le changement de joueur est fait
                if self.partie_terminee():
                    self.verifier_fin_partie()
                else:
                    self.mise_à_jour_scores()
            else:
                print("Placement non valide (debug)")

    def retourner_pions(self, ligne, col, joueur):
        """Retourne les pions adverses encadrés par le pion placé."""
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1),
                      (-1, -1), (-1, 1), (1, -1), (1, 1)]
        #tableau des directions, j'ai pas trouvé plus simple pour visualiser le truc mais peut être vous aurez une vision plus opti
        #0,0 c'est le point de départ
        #la première ligne dans le tableau c'est les points à gauche(-1,0), à droite(1,0), en dessous(0,-1), et au dessus(0,1),
        #la deuxieme ligne c'est les points en haut à gauche(-1,-1), en haut à gauche(-1,1), en bas à droite (1,-1) et en haut à droite (1,1)
        #j'espère c clair les frères ptdrr

        adversaire = self.NOIR if joueur == self.BLANC else self.BLANC

        for dx, dy in directions:
            pions_a_retourner = []
            x = ligne + dx
            y = col + dy

            #on récupère les pions adverses dans la direction donnée
            while 0 <= x < self.size and 0 <= y < self.size and self.plateau[x][y] == adversaire:
                pions_a_retourner.append((x, y))
                x += dx
                y += dy

            #si à la fin on retrouve un pion du joueur alors on retourne les pions adverses entre les deux pions
            if pions_a_retourner and 0 <= x < self.size and 0 <= y < self.size and self.plateau[x][y] == joueur:
                for rx, ry in pions_a_retourner:
                    self.plateau[rx][ry] = joueur

    def coup_valide(self, ligne, col, joueur):
        """Vérifie si le coup est valide : la case doit être vide et encadrer au moins un pion adverse."""
        if self.plateau[ligne][col] is not None:
            return False

        directions = [(-1, 0), (1, 0), (0, -1), (0, 1),
                      (-1, -1), (-1, 1), (1, -1), (1, 1)]
        adversaire = self.NOIR if joueur == self.BLANC else self.BLANC

        for dx, dy in directions:
            x = ligne + dx
            y = col + dy
            encadrement = 0

            #on boucle tant que l'on trouve des pions adverses dans la direction donnée
            while 0 <= x < self.size and 0 <= y < self.size and self.plateau[x][y] == adversaire:
                encadrement += 1
                x += dx
                y += dy

            #le coup est considéré valide si on trouve un pion du joueur dans la direction qui encadre des pions adverses
            if encadrement > 0 and 0 <= x < self.size and 0 <= y < self.size and self.plateau[x][y] == joueur:
                return True

        return False
    
    def mise_à_jour_scores(self):
        pions_blanc = sum(row.count(self.BLANC) for row in self.plateau)
        pions_noir = sum(row.count(self.NOIR) for row in self.plateau)
        if self.mode_ia:
            self.score_label.config(text=f"Scores : Noirs: {pions_noir} | Blancs: {pions_blanc} | Couleur Joueur: {self.joueur_courant} | Couleur IA: {self.couleur_ia}")
        else:
            self.score_label.config(text=f"Scores : Noirs: {pions_noir} | Blancs: {pions_blanc} | Tour Actuel: {self.joueur_courant}")

    def peut_jouer(self, joueur):
        """Est ce que le joueur à un coup valide à jouer"""
        for lig in range(self.size):
            for col in range(self.size):
                if self.coup_valide(lig, col, joueur):
                    return True
        return False

    def partie_terminee(self):
        """Partie terminée si aucun des joueurs ne peut jouer ou si le plateau est remplit"""
        if not self.peut_jouer(self.NOIR) and not self.peut_jouer(self.BLANC):
            return True
        for lig in range(self.size):
            for col in range(self.size):
                if self.plateau[lig][col] is None:
                    return False
        return True

    def verifier_fin_partie(self):
        """Detecte la fin de partie et affiche le gagnant"""
        if self.partie_terminee():
            pions_noir = sum(row.count(self.NOIR) for row in self.plateau)
            pions_blanc = sum(row.count(self.BLANC) for row in self.plateau)
            self.dessiner_plateau()
            self.mise_à_jour_scores()
            if pions_noir > pions_blanc:
                resultat = "Le joueur Noir gagne la partie !"
            elif pions_blanc > pions_noir:
                resultat = "Le joueur Blanc gagne la partie !"
            else:
                resultat = "Match nul !"
            messagebox.showinfo("Fin de Partie", f"Score final - Noirs: {pions_noir} | Blancs: {pions_blanc}\n{resultat}")
    
    def afficher_coups_jouables(self):
        if self.joueur_courant != self.couleur_ia:
            for lig in range(self.size):
                for col in range(self.size):
                    if self.coup_valide(lig, col, self.joueur_courant):
                        x1 = self.marge + col * self.cellules_size
                        y1 = self.marge + lig * self.cellules_size
                        x2 = x1 + self.cellules_size
                        y2 = y1 + self.cellules_size
                        cx = (x1 + x2) // 2
                        cy = (y1 + y2) // 2
                        rayon_gris = self.cellules_size // 2 - 10
                        image_id = self.canvas.create_image(cx, cy, image=self.pion_gris_img, tags=("coups_jouables",))

    def clignoter(self):
        if self.joueur_courant != self.couleur_ia:
            self.blink_state = not self.blink_state
            if self.blink_state:
                self.canvas.itemconfigure("coups_jouables", state="normal")
            else:
                self.canvas.itemconfigure("coups_jouables", state="hidden")
            self.fenetre.after(self.clignotement_delay, self.clignoter)

    def clone_plateau(self, plateau):
        """Copie du tableau de jeu, dans un nouveau pour nos calculs"""
        copie = []
        for ligne in plateau:
            copie.append(ligne[:])  #copie de chaque ligne
        return copie

    def faire_jouer_ia(self):
        if self.peut_jouer(self.couleur_ia):
            self.fenetre.update()
            time.sleep(1)
            self.ai_player.jouer_coup(self.plateau)
            self.joueur_courant = self.BLANC if self.couleur_ia == self.NOIR else self.NOIR
            self.mise_à_jour_scores()
            self.dessiner_plateau()
            if not self.peut_jouer(self.joueur_courant):
                messagebox.showinfo("Passer le tour", f"Le joueur {self.joueur_courant} ne peut pas jouer. Le tour reste à l'IA.")
                self.joueur_courant = self.couleur_ia
                if not self.partie_terminee():
                    self.faire_jouer_ia()
        else:
            #si l'ia ne peut pas jouer, c'est encore au joueur de jouer
            messagebox.showinfo("Passer le tour", "L'IA ne peut pas jouer")
            self.joueur_courant = self.BLANC if self.couleur_ia == self.NOIR else self.NOIR

    
    """ ⚠️⚠️ TEST POUR LES FONCTIONS DE L'IA"""
    def test_diff_ia(self):
        diff = self.ai_player.diff_pions(self.plateau)
        print(f"[IA] Différence pions (IA - Adv): {diff}")
    
    def test_coins_ia(self):
        score_coins = self.ai_player.coins(self.plateau)
        print(f"[IA] Score de coins : {score_coins}")

    def test_get_valid_moves(self):
        coups = self.ai_player.get_valid_moves(self.plateau, self.ai_player.couleur)
        print(f"[IA] Coups valides (via Othello.coup_valide) : {coups}")

    def test_mobilite(self):
        mobilite_diff = self.ai_player.mobilite(self.plateau)
        print(f"[IA] Difference de mobilite : {mobilite_diff}")
    
    def test_apply_move(self):
        if self.mode_ia:
            print("[IA]test apply_move()")
            coups = self.ai_player.get_valid_moves(self.plateau, self.ai_player.couleur)
            if coups:
                coup = coups[0]
                print(f"[IA]coup testé : {coup}")
                nouveau_plateau = self.ai_player.apply_move(self.plateau, coup, self.ai_player.couleur)
                print("[IA]plateau après le coup :")
                for ligne in nouveau_plateau:
                    print(" ".join(p if p else "." for p in ligne))
            else:
                print("[IA]aucun coup valide à tester.")

    def test_stabilite(self):
        score_stabilite = self.ai_player.stabilite(self.plateau)
        print(f"[IA] Score de stabilité : {score_stabilite}")

    def test_triangles(self):
        score_triangles = self.ai_player.triangles(self.plateau)
        print(f"[IA] Score de triangles : {score_triangles}")

    def test_cases_dangereuses(self):
        score_danger = self.ai_player.cases_dangereuses(self.plateau)
        print(f"[IA] Score de cases dangereuses : {score_danger}")


class IAOthello:
    def __init__(self, jeu, couleur, profondeur_max):
        """Initialise l'IA avec sa couleur et la profondeur max de recherche."""
        self.jeu = jeu
        self.couleur = couleur
        self.profondeur_max = profondeur_max

    def jouer_coup(self, plateau):
        meilleur_score = float("-inf") #-inf pour maximiser notre coup
        meilleur_coup = None

        for coup in self.get_valid_moves(plateau, self.couleur): #on parcours tous les coups possibles et on prend le meilleur (via min-max)
            nouveau_plateau = self.apply_move(plateau, coup, self.couleur)
            score = self.minmax(nouveau_plateau, self.profondeur_max - 1, float("-inf"), float("inf"), False)

            if score > meilleur_score:
                meilleur_score = score
                meilleur_coup = coup
        if meilleur_coup: #on applique le meilleur coup sur le plateau
            ligne, col = meilleur_coup
            self.jeu.plateau[ligne][col] = self.couleur
            self.jeu.retourner_pions(ligne, col, self.couleur)
        return meilleur_coup

    def minmax(self, plateau, profondeur, alpha, beta, maximisant):
        """Algorithme Min-Max avec élagage alpha-bêta pour choisir un coup."""
        if profondeur == 0 or self.game_over(plateau): #condition d'arrêt de la récursion
            return self.evaluer_plateau(plateau)
        
        joueur = self.couleur if maximisant else ("B" if self.couleur == "N" else "N") #si maxisanr = true c'est le tour de l'IA, sinon c'est l'adversaire
        coups_possibles = self.get_valid_moves(plateau, joueur)

        if not coups_possibles: #aucun coup possible, on passe le tour et on continue la récursivité
            return self.minmax(plateau, profondeur - 1, alpha, beta, not maximisant)

        if maximisant: #l'IA veut le meilleur coup (maximisant)
                max_eval = float("-inf")
                for coup in coups_possibles:
                    nouveau_plateau = self.apply_move(plateau, coup, joueur)
                    evaluation = self.minmax(nouveau_plateau, profondeur - 1, alpha, beta, False) #on cherche le score minimisant pour le prochain coup du joueur
                    max_eval = max(max_eval, evaluation) #on prend le meilleur pour l'IA
                    alpha = max(alpha, evaluation) #alpha prend donc le meilleur score
                    if beta <= alpha: #si l'adversaire de ne prendra pas cette branche on break
                        break  # on applique l'élagage ici
                return max_eval
        else: #cas ou l'adversaire va jouer et essayer de minimiser notre score
            min_eval = float("inf")
            for coup in coups_possibles:
                nouveau_plateau = self.apply_move(plateau, coup, joueur)
                evaluation = self.minmax(nouveau_plateau, profondeur - 1, alpha, beta, True)
                min_eval = min(min_eval, evaluation) #même principe qu'en haut, sauf qu'on garde le pire score pour le joueur
                beta = min(beta, evaluation) #pire score trouvé dans beta
                if beta <= alpha:
                    break  #élagage alpha bete ici
            return min_eval
        
    def evaluer_plateau(self, plateau):
        """Évalue le plateau selon une heuristique avancée."""
        score = 0
        score += 10 * self.diff_pions(plateau)
        score += 20 * self.coins(plateau)
        score += 15 * self.mobilite(plateau)
        score += 10 * self.stabilite(plateau)
        score += 25 * self.triangles(plateau)
        score -= 10 * self.cases_dangereuses(plateau)
        return score

    def diff_pions(self, plateau):
        """Calcule la différence de pions IA - adversaire."""
        def count_pieces(plateau):
            nb_noirs = 0
            nb_blancs = 0
            for ligne in range(8):
                for col in range(8):
                    if plateau[ligne][col] == "N":
                        nb_noirs += 1
                    elif plateau[ligne][col] == "B":
                        nb_blancs += 1
            return nb_noirs, nb_blancs

        nb_noirs, nb_blancs = count_pieces(plateau)

        if self.couleur == "N":
            nb_Ia = nb_noirs
            nb_adv = nb_blancs
        else:
            nb_Ia = nb_blancs
            nb_adv = nb_noirs

        return nb_Ia - nb_adv

    def coins(self, plateau):
        """Compte les coins occupés par l'IA et l'adversaire."""
        coins_pos = [[0,0], [0,7], [7,0], [7,7]]
        score = 0
        adv = "B" if self.couleur == "N" else "N"
        for x,y in coins_pos:
            if plateau[x][y] == self.couleur:
                score += 1
            elif plateau[x][y] == adv:
                score -=1
        return score 

    def get_valid_moves(self, plateau, joueur):
        """Utilise la méthode coup_valide déjà existante dans Othello."""
        coups_valides = []
        for lig in range(8):
            for col in range(8):
                if plateau[lig][col] is None and self.jeu.coup_valide(lig, col, joueur):
                    coups_valides.append((lig, col))
        return coups_valides

    def mobilite(self, plateau):
        """Calcule la mobilité (coups possibles IA - adversaire).""" 
        nb_IA  = len(self.get_valid_moves(plateau, self.couleur))
        adv = "B" if self.couleur == "N" else "N"
        nb_adv = len(self.get_valid_moves(plateau, adv))

        return nb_IA - nb_adv

    def stabilite(self, plateau):
        """Évalue les pions stables (non retournables) de l'IA et de l'adversaire."""
        score = 0
        adv = "B" if self.couleur == "N" else "N"

        def est_sur_bord(x, y):
            return x == 0 or x == 7 or y == 0 or y == 7

        for x in range(8):
            for y in range(8):
                if plateau[x][y] == self.couleur and est_sur_bord(x, y):
                    score += 1
                elif plateau[x][y] == adv and est_sur_bord(x, y):
                    score -= 1
        return score

    def triangles(self, plateau):
        """Détecte les formations en triangle autour des coins."""
        triangles_pos = [[(0,0), (0,1), (1,0)], [(0,7), (0,6), (1,7)], [(7,0), (6,0), (7,1)], [(7,7), (6,7), (7,6)]]
        score = 0
        adv = "B" if self.couleur == "N" else "N"

        for triangle in triangles_pos:
            nb_IA = sum(1 for (x, y) in triangle if plateau[x][y] == self.couleur)
            nb_adv = sum(1 for (x, y) in triangle if plateau[x][y] == adv)

            if nb_IA == 3:
                score += 1
            elif nb_adv == 3:
                score -= 1

        return score

    def cases_dangereuses(self, plateau):
        """Évalue les cases dangereuses adjacentes aux coins."""
        dangereuses_pos = [(0,1), (1,0), (1,1), (0,6), (1,7), (1,6), (6,0), (6,1), (7,1), (6,7), (7,6), (6,6)]
        score = 0
        adv = "B" if self.couleur == "N" else "N"

        for x, y in dangereuses_pos:
            if plateau[x][y] == self.couleur:
                score += 1
            elif plateau[x][y] == adv:
                score -= 1

        return score

    def apply_move(self, plateau, coup, joueur):
        """Simule un certain coup sur le plateau et renvoie une copie du nouveau plateau"""
        lig, col = coup
        nouveau_plateau = self.jeu.clone_plateau(plateau)
        nouveau_plateau[lig][col] = joueur
        adversaire = "B" if joueur == "N" else "N"
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1),
                    (-1, -1), (-1, 1), (1, -1), (1, 1)]
        #même principe que coup valide dans la classe Othello
        for dx, dy in directions:
            x, y = lig + dx, col + dy
            pions_a_retourner = []
            while 0 <= x < 8 and 0 <= y < 8 and nouveau_plateau[x][y] == adversaire:
                pions_a_retourner.append((x, y))
                x += dx
                y += dy
            if pions_a_retourner and 0 <= x < 8 and 0 <= y < 8 and nouveau_plateau[x][y] == joueur:
                for rx, ry in pions_a_retourner:
                    nouveau_plateau[rx][ry] = joueur
        return nouveau_plateau

    def game_over(self, plateau):
        """Retourne True si aucun joueur ne peut encore jouer, sinon False."""
        noir_peut_jouer = bool(self.get_valid_moves(plateau, "N"))
        blanc_peut_jouer = bool(self.get_valid_moves(plateau, "B"))
        return not (noir_peut_jouer or blanc_peut_jouer)

def menu_accueil():
    """Menu d'accueil du jeu Othello."""
    root = tk.Tk()
    root.title("Othello - Menu")
    window_width = 1004
    window_height = 1004
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x_coord = (screen_width // 2) - (window_width // 2)
    y_coord = (screen_height // 2) - (window_height // 2)
    root.geometry(f"{window_width}x{window_height}+{x_coord}+{y_coord}")
    root.configure(bg="#2c2c2c")
    style = ttk.Style(root)
    style.theme_use('clam')
    style.configure("Custom.TFrame", background="#3a3a3a")
    frame = ttk.Frame(root, style="Custom.TFrame")
    frame.place(relx=0.5, rely=0.5, anchor="center", width=600, height=400)
    style.configure("Custom.TLabel", background="#3a3a3a", foreground="white", font=("Helvetica", 28, "bold"))
    label_title = ttk.Label(frame, text="Bienvenue dans Othello", style="Custom.TLabel")
    label_title.pack(pady=(40, 20))
    style.configure("Custom.TButton", font=("Helvetica", 20), padding=(20, 10))
    def lancer_pvp():
        frame.destroy()
        Othello(root)
    
    def lancer_ia_menu():
        """Lance le menu pour choisir le style de jeu de l'IA."""
        frame.destroy()
        menu_ia_options(root)
    
    btn_pvp = ttk.Button(frame, text="Joueur contre Joueur", command=lancer_pvp, style="Custom.TButton")
    btn_pvp.pack(pady=20, fill="x", padx=40)
    btn_ia = ttk.Button(frame, text="Joueur contre IA", command=lancer_ia_menu, style="Custom.TButton")
    btn_ia.pack(pady=30, fill="x", padx=40)
    
    root.mainloop()

def menu_ia_options(root):
    """Menu pour choisir le style de jeu de l'IA"""
    style = ttk.Style(root)
    style.theme_use('clam')
    #on configure le style de tous les widgets que l'on va utiliser
    style.configure("Custom.TFrame", background="#3a3a3a", borderwidth=3, relief="raised")
    style.configure("Custom.TLabel", background="#3a3a3a", foreground="white", font=("Helvetica", 28, "bold"))
    style.configure("Custom.TRadiobutton", background="#3a3a3a", foreground="white", font=("Helvetica", 20))
    style.configure("Custom.TButton", font=("Helvetica", 20), padding=(20, 10))
    style.map("Custom.TRadiobutton",background=[("active", "#3a3a3a")],foreground=[("active", "white")])
    ia_frame = ttk.Frame(root, style="Custom.TFrame")
    ia_frame.place(relx=0.5, rely=0.5, anchor="center", width=600, height=400)
    label = ttk.Label(ia_frame, text="Choisissez le mode IA", style="Custom.TLabel")
    label.pack(pady=(40, 20))
    mode_var = tk.StringVar(value="offensif") #notre variable pour le style de jeu de l'IA
    modes = [("Offensif", "offensif"), ("Défensif", "defensif"), ("Stratégique", "strategique")]
    for text, mode in modes:
        rb = ttk.Radiobutton(ia_frame,text=text,variable=mode_var,value=mode,style="Custom.TRadiobutton")
        rb.pack(pady=5)

    def confirmer_ia():
        """Confirme le choix du style de jeu de l'IA et lance le jeu."""
        ia_mode = mode_var.get()
        print(f"[INFO] Mode IA sélectionné : {ia_mode}")
        ia_frame.destroy()
        couleur_ia = random.choice(["N", "B"])
        print(f"[INFO] L'IA joue en {couleur_ia}")
        Othello(root, mode_ia=True, couleur_ia=couleur_ia)

    btn_confirmer = ttk.Button(ia_frame, text="Lancer l'IA", command=confirmer_ia, style="Custom.TButton")
    btn_confirmer.pack(pady=20, fill="x", padx=40)

if __name__ == "__main__":
    menu_accueil()