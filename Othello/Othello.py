import tkinter as tk
import tkinter.messagebox as messagebox
import random as random

class Othello:
    def __init__(self, fenetre):
        self.fenetre = fenetre
        icone = tk.PhotoImage(file="Othello/Logo_Tkinter.png")
        self.fenetre.iconphoto(False, icone)
        self.fenetre.title("Othello")

        self.size = 8   
        self.size_3 = self.size // 2 - 1   
        self.size_4 = self.size // 2

        self.cellules_size = 60   

        self.NOIR = "N"
        self.BLANC = "B"

        self.plateau = [[None for _ in range(self.size)] for _ in range(self.size)]

        self.plateau[self.size_3][self.size_3] = self.BLANC
        self.plateau[self.size_3][self.size_4] = self.NOIR
        self.plateau[self.size_4][self.size_3] = self.NOIR
        self.plateau[self.size_4][self.size_4] = self.BLANC

        # ⚠️ TEMPORAIRE: on créer l'ia vite fait pour les tests
        self.ai_player = IAOthello(jeu=self, couleur=self.NOIR, profondeur_max=3)
        
        self.canvas = tk.Canvas(self.fenetre, width=self.size * self.cellules_size, height=self.size * self.cellules_size, bg="green")
        self.canvas.pack()

        self.canvas.bind("<Button-1>", self.gerer_clic)

        self.joueur_courant = self.NOIR

        self.score_label = tk.Label(self.fenetre, text=f"Scores : Noirs: 2 | Blancs: 2 | Tour Actuel: {self.joueur_courant}", font=("Arial", 14))
        self.score_label.pack(pady=10)

        self.dessiner_plateau()

        self.blink_state = False #allumé éteint
        self.clignotement_delay = 1000  # 1 seconde        
        self.fenetre.after(self.clignotement_delay, self.clignoter)

    def dessiner_plateau(self):
        self.canvas.delete("all")
        for lig in range(self.size):
            for col in range(self.size):
                x1 = col * self.cellules_size
                y1 = lig * self.cellules_size
                x2 = x1 + self.cellules_size
                y2 = y1 + self.cellules_size

                # Dessin des cases du plateau
                self.canvas.create_rectangle(x1, y1, x2, y2, outline="black", fill="green")

                # Dessin des pions
                if self.plateau[lig][col] == self.NOIR:
                    self.canvas.create_oval(x1 + 5, y1 + 5, x2 - 5, y2 - 5, fill="black", outline="white", width=1)
                elif self.plateau[lig][col] == self.BLANC:
                    self.canvas.create_oval(x1 + 5, y1 + 5, x2 - 5, y2 - 5, fill="white", outline="black", width=1)
        
        self.afficher_coups_jouables()

    
    def gerer_clic(self, event):
        col = event.x // self.cellules_size
        lig = event.y // self.cellules_size

        if 0 <= lig < self.size and 0 <= col < self.size:
            if self.coup_valide(lig, col, self.joueur_courant):
                joueur_actuel = self.joueur_courant

                # on place le pion car valide, et on retourne les pions adverses
                self.plateau[lig][col] = joueur_actuel
                self.retourner_pions(lig, col, joueur_actuel)

                self.mise_à_jour_scores()
                self.dessiner_plateau()

                # on cherche à déterminer le joueur suivant
                prochain = self.BLANC if joueur_actuel == self.NOIR else self.NOIR

                if self.peut_jouer(prochain):
                    self.joueur_courant = prochain
                elif self.peut_jouer(joueur_actuel):
                    messagebox.showinfo(
                        "Passer le tour",
                        f"Le joueur {prochain} ne peut pas jouer. Le tour reste au joueur {joueur_actuel}."
                    )
                    self.joueur_courant = joueur_actuel
                else:
                    #les deux ne peuvent pas jouer, alors on verif la fin de partie
                    self.verifier_fin_partie()
                    return
                
                self.test_diff_ia() #test pour verif la diff des pions
                self.test_coins_ia() #test pour verif les pions des coins 
                self.test_get_valid_moves() #test pour verif les coup valide sous forme de liste
                self.test_mobilite() #test pour verif qui a le plus de mobilite entre IA et joueur

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
        """Affiche un petit cercle gris pour les coups dit jouables pour le joueur actuel"""
        for lig in range(self.size):
            for col in range(self.size):
                if self.coup_valide(lig, col, self.joueur_courant):
                    x1 = col * self.cellules_size
                    y1 = lig * self.cellules_size
                    x2 = x1 + self.cellules_size
                    y2 = y1 + self.cellules_size
                    cx, cy = (x1 + x2)//2, (y1 + y2)//2
                    r = 8
                    rayon_gris = self.cellules_size // 2 - 10
                    self.canvas.create_oval(
                        cx - rayon_gris, cy - rayon_gris, cx + rayon_gris, cy + rayon_gris,
                        fill="#A9A9A9",  # gris clair
                        outline="", tags=("coups_jouables",)
                    )

    def clignoter(self):
        """permet de faire clignoter les pions gris"""
        self.blink_state = not self.blink_state
        couleur = "#A9A9A9" if self.blink_state else ""
        self.canvas.itemconfig("coups_jouables", fill=couleur)
        self.fenetre.after(self.clignotement_delay, self.clignoter)

    def clone_plateau(self, plateau):
        """Copie du tableau de jeu, dans un nouveau pour nos calculs"""
        copie = []
        for ligne in plateau:
            copie.append(ligne[:])  #copie de chaque ligne
        return copie
    
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

class IAOthello:
    def __init__(self, jeu, couleur, profondeur_max):
        """Initialise l'IA avec sa couleur et la profondeur max de recherche."""
        self.jeu = jeu  # référence vers l'objet Othello
        self.couleur = couleur
        self.profondeur_max = profondeur_max

    def jouer_coup(self, plateau):
        """Calcule et joue le meilleur coup possible pour l'IA sur le plateau."""
        pass

    def minmax(self, plateau, profondeur, alpha, beta, maximisant):
        """Algorithme Min-Max avec élagage alpha-bêta pour choisir un coup."""
        pass

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
        pass

    def triangles(self, plateau):
        """Détecte les formations en triangle autour des coins."""
        pass

    def cases_dangereuses(self, plateau):
        """Évalue les cases dangereuses adjacentes aux coins."""
        pass

    


    def apply_move(self, plateau, coup, joueur):
        """Applique un coup sur le plateau et retourne le nouvel état."""
        pass

    def game_over(self, plateau):
        """Indique si la partie est terminée (aucun coup valide restant)."""
        pass

def main():
    root = tk.Tk()
    Othello(root)
    root.mainloop()

if __name__ == "__main__":
    main()