import tkinter as tk

class Othello:
    def __init__(self, fenetre):
        self.fenetre = fenetre
        icone = tk.PhotoImage(file="Logo_Tkinter.png")
        self.fenetre.iconphoto(False, icone)
        self.fenetre.title("Othello")

        # dims
        self.size = 8   
        self.size_3 = self.size//2 - 1   
        self.size_4 = self.size//2

        self.cellules_size = 60   

        self.NOIR = "N"
        self.BLANC = "B"

        # creation de la structure de plateau --> la ou on va manipuler quand le joueur va gerer l'etats des cellues (quelle pions est ou)
        self.plateau = [[None for _ in range(self.size)] for _ in range(self.size)]

        # pions initiaux au centre
        self.plateau[self.size_3][self.size_3] = self.BLANC
        self.plateau[self.size_3][self.size_4] = self.NOIR
        self.plateau[self.size_4][self.size_3] = self.NOIR
        self.plateau[self.size_4][self.size_4] = self.BLANC

        self.canvas = tk.Canvas(self.fenetre, width=self.size * self.cellules_size, height=self.size * self.cellules_size, bg="green")
        self.canvas.pack()

        #permet de gérer le clic
        self.canvas.bind("<Button-1>", self.gerer_clic)

        self.joueur_courant = self.NOIR

        self.score_label = tk.Label(self.fenetre, text=f"Scores : Noirs: {2} | Blancs: {2} | Tour Actuel: {self.joueur_courant}", font=("Arial", 14))
        self.score_label.pack(pady=10)

        

        self.dessiner_plateau()

    def dessiner_plateau(self):
        self.canvas.delete("all")
        for lig in range(self.size):
            for col in range(self.size):
                x1 = col * self.cellules_size
                y1 = lig * self.cellules_size
                x2 = x1 + self.cellules_size
                y2 = y1 + self.cellules_size

                #dessin des cases pour le plateau 
                self.canvas.create_rectangle(x1, y1, x2, y2, outline="black", fill="green")

                #dessin des pions
                if self.plateau[lig][col] == self.NOIR:
                    self.canvas.create_oval(x1+5, y1+5, x2-5, y2-5, fill="black")
                elif self.plateau[lig][col] == self.BLANC:
                    self.canvas.create_oval(x1+5, y1+5, x2-5, y2-5, fill="white")
    
    def gerer_clic(self, event):
        """verifie si le coup du joueur est valide, place le pion si oui et retourne les pions adverses"""
        col = event.x // self.cellules_size
        lig = event.y // self.cellules_size

        if 0 <= lig < self.size and 0 <= col < self.size:
            if self.coup_valide(lig, col, self.joueur_courant):

                #on place le pion du joueur après les vérifications
                self.plateau[lig][col] = self.joueur_courant

                # on retourne les pions ennmies entourés
                self.retourner_pions(lig, col, self.joueur_courant)

                #on change le joueur courant
                self.joueur_courant = self.NOIR if self.joueur_courant == self.BLANC else self.BLANC
                self.mise_à_jour_scores()
                self.dessiner_plateau()
            else:
                print("Placement non valide (debug)") #à supprimer dans la version finale c'est juste pour mieux comprendre comment ça fonctionne pour le debug

    def retourner_pions(self, ligne, col, joueur):
        """retourne les pions adverses (noir ou blanc en fonction du joueur actuel)"""
        directions = [
            (-1, 0), (1, 0), (0, -1), (0, 1),
            (-1, -1), (-1, 1), (1, -1), (1, 1)]
        adversaire = self.NOIR if joueur == self.BLANC else self.BLANC

        for dx, dy in directions:
            pions_a_retourner = []
            x, y = ligne + dx, col + dy

            #on prend la position des pions adverses
            while 0 <= x < self.size and 0 <= y < self.size and self.plateau[x][y] == adversaire:
                pions_a_retourner.append((x, y))
                x += dx
                y += dy

            #si le dernier pion est le joueur actuel, on retourne tous les pions entre
            if pions_a_retourner and 0 <= x < self.size and 0 <= y < self.size and self.plateau[x][y] == joueur:
                for rx, ry in pions_a_retourner:
                    self.plateau[rx][ry] = joueur
    

    def coup_valide(self, ligne, col, joueur):
        """Vérifie si le coup est valide. Coup valide si la case est vide et s'il encadre au moins un pion adverse entre le pion placé et un pion déjà placé ennemie"""
        if self.plateau[ligne][col] is not None:
            return False

        #tableau des directions, j'ai pas trouvé plus simple pour visualiser le truc mais peut être vous aurez une vision plus opti
        #0,0 c'est le point de départ
        #la première ligne dans le tableau c'est les points à gauche(-1,0), à droite(1,0), en dessous(0,-1), et au dessus(0,1),
        #la deuxieme ligne c'est les points en haut à gauche(-1,-1), en haut à gauche(-1,1), en bas à droite (1,-1) et en haut à droite (1,1)
        #j'espère c clair les frères ptdrr
        directions = [
            (-1, 0), (1, 0), (0, -1), (0, 1),
            (-1, -1), (-1, 1), (1, -1), (1, 1)]

        adversaire = self.NOIR if joueur == self.BLANC else self.BLANC

        for dx, dy in directions:
            x, y = ligne + dx, col + dy
            nb_adversaires_encadres = 0

            #while dans le plateau et qu'on voit toujours des pions ennemie
            while 0 <= x < self.size and 0 <= y < self.size and self.plateau[x][y] == adversaire:
                x += dx
                y += dy
                nb_adversaires_encadres += 1

            #on sort de cette boucle soit parce qu'on est hors du plateau soit parce qu'on est tombé sur une case qui n'est pas un pion adverse.

            #pour que ça soit valide faut:
            #1) au moins un pion adverse (nb_adversaires_encadres > 0)
            #2) un pion du joueur en bout de chemin pour pouvoir encadré
            if nb_adversaires_encadres > 0 and 0 <= x < self.size and 0 <= y < self.size:
                if self.plateau[x][y] == joueur:
                    return True

        return False
    
    def mise_à_jour_scores(self):
        pions_blanc = sum (row.count(self.BLANC) for row in self.plateau)
        pions_noir = sum(row.count(self.NOIR) for row in self.plateau)
        
        self.score_label.config(text=f"Scores : Noirs: {pions_noir} | Blancs: {pions_blanc} | Tour Actuel: {self.joueur_courant}")
    
        

def main():
    root = tk.Tk()
    Othello(root)
    root.mainloop()

if __name__ == "__main__":
    main()