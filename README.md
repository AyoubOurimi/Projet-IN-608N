# Projet-IN-608N

# Introduction

Othello, aussi connu sous le nom de Reversi, est un jeu de société de
stratégie à deux joueurs sur un plateau de 8 × 8 cases. Dans le cadre du
projet IN608, nous avons développé une application Python permettant de
jouer à Othello, incluant un mode joueur contre joueur et un mode joueur
contre une intelligence artificielle (IA) basée sur l’algorithme
*Minmax* avec élagage *alpha-bêta*. Le jeu est doté d’une interface
graphique réalisée avec la bibliothèque Tkinter.

Nous commencerons par rappeler brièvement les règles du jeu Othello.
Ensuite, nous décrirons la structure des données utilisées pour
modéliser le plateau et les pions. La section suivante détaillera
l’architecture du code en séparant la logique du jeu, l’interface
graphique et l’IA. Nous expliquerons ensuite les fonctions principales
et les choix de conception réalisés. L’algorithme Minmax et son
amélioration par l’élagage alpha-bêta seront également présentés, de
même que la fonction d’évaluation heuristique en soulignant les critères
pris en compte (coins, cases dangereuses, mobilité, stabilité, etc...)

# Règles du jeu Othello

Le jeu se déroule sur un plateau de 64 cases (8x8) appelé *othellier*.
Au début de la partie, le plateau commence avec 4 pions disposés au
centre : deux pions noirs et deux pions blancs placés en diagonale
(configuration initiale classique).

Noir joue toujours en premier, puis les joueurs alternent les tours. Un
coup consiste à placer un pion de sa couleur sur une case vide adjacente
à un pion adverse, de manière à *encadrer* un ou plusieurs pions
adverses entre le pion que l’on pose et un autre pion de sa couleur déjà
présent sur le plateau. Tous les pions adverses ainsi encadrés
(horizontalement, verticalement ou diagonalement) sont retournés et
changent donc de couleur pour devenir de la couleur du joueur qui a joué
le coup.

Si un joueur ne peut effectuer aucun mouvement légal (aucune possibilité
d’encadrement), il doit passer son tour et laisser l’adversaire jouer.
La partie s’achève lorsque plus aucun joueur ne peut jouer (généralement
lorsque toutes les cases sont occupées ou qu’aucun coup n’est possible).
Le gagnant est celui qui possède le plus de pions de sa couleur sur le
plateau à la fin de la partie. En cas d’égalité en nombre de pions, on
peut déclarer un match nul.  
**Remarque :** Les règles officielles complètes du jeu Othello sont
disponibles sur le site de la Fédération Française d’Othello:
 <https://www.ffothello.org/othello/regles-du-jeu/>

# Structures de données et représentation du jeu

Afin de faciliter l’implémentation, nous avons opté pour une
représentation simple du plateau et des pions. Le plateau de jeu est
modélisé par une matrice 8 × 8 (une liste de listes en Python) dans
laquelle chaque élément représente une case. Au début de la partie,
cette matrice est initialisée avec des valeurs indiquant des cases vides
partout, sauf au centre où se trouvent les 4 pions initiaux (2 noirs et
2 blancs).

Pour représenter l’état d’une case, nous utilisons une codification
spécifique : une case vide vaut `None`, un pion noir est codé par `N` et
un pion blanc par `B`. Ce choix de valeurs permet de manipuler
facilement les pions lors des changements de couleur : retourner un pion
revient à changer la valeur (un `N` devient `B` et vice-versa).
Alternativement, on aurait pu utiliser des valeur numériques par exemple
`1`, `-1`, `0`) Le principe reste identique, mais pour améliorer la
lisibilité du code on a utilisé `N`, `B`, `None`.

Les coordonnées des cases du plateau sont gérées en repérant les indices
de ligne et de colonne (dans notre implémentation, nous utilisons des
indices de 0 à 7 correspondant respectivement aux lignes 1 à 8 et
colonnes A à H d’un othellier classique). Un coup possible est
simplement représenté par un couple de coordonnées (*i*, *j*) indiquant
la case où un pion peut être placé. Par exemple, le coin supérieur
gauche du plateau correspondra aux coordonnées (0, 0) et le coin
inférieur droit à (7, 7).

Pour le calcul des coups et des retournements de pions, nous avons
également défini un ensemble de directions. Il existe 8 directions
possibles à partir d’une case (horizontal, vertical et les deux
diagonales). Celles-ci peuvent être représentées par des vecteurs de
déplacement, par exemple *Δ* = (−1, 0) pour aller vers la gauche, (1, 1)
pour aller en haut à droite, etc. Nous stockons ces 8 déplacements
directionnels dans une liste afin de pouvoir parcourir systématiquement
toutes les directions lors de la recherche des pions à retourner ou des
coups valides.

# Architecture du programme

Le code du projet est organisé de manière modulaire afin de séparer les
responsabilités entre l’interface utilisateur, la logique du jeu et
l’intelligence artificielle. Cette séparation rend le code plus lisible,
facilite les tests et permet de faire évoluer chaque composant
indépendamment.  Nous utilisons une classe Othello qui permet de gérer
la logique globale du jeu que nous expliquerons dans la partie suivante
 Nous utilisons également une classe IAOthello qui nous permet de gérer
tous les aspects de l’intelligence artificielle.

## Logique du jeu (Classe Othello)

La *classe Othello* regroupe toutes les fonctionnalités liées aux règles
et à l’état du plateau. Cela inclut la gestion du plateau
(initialisation, mise à jour après chaque coup), la détermination des
coups valides pour un joueur donné, l’application d’un coup (avec
retournement des pions adverses) et la vérification des conditions de
fin de partie. Concrètement, on implémente ces fonctionnalités sous
forme de fonctions indépendantes au sein de notre classe qui permettent
le maintient de l’état courant du jeu.

Une fonction importante de la logique est
`coups_valides(plateau, joueur)` qui parcourt toutes les cases vides du
plateau et vérifie pour chacune si un pion du joueur peut y être placé
en retournant au moins un pion adverse. Cette vérification utilise les
directions pré-définies : pour chaque direction, on regarde s’il y a une
succession immédiate de pions adverses suivie d’un pion du joueur actuel
; si oui, la case est un coup valide. De même, la fonction qui applique
un coup, appelée `jouer_coup(plateau, coup, joueur)`, pose le pion du
joueur sur la case choisie et parcourt à nouveau toutes les directions
pour retourner les pions adverses.

Après chaque modification du plateau, on vérifie s’il reste des coups
possibles pour le joueur suivant. Si le joueur suivant ne possède aucun
coup valide, la logique du jeu gère ce cas en lui faisant passer son
tour (sans rejouer le même joueur deux fois de suite, sauf si
l’adversaire n’a vraiment aucun coup). Si plus aucun des deux joueurs ne
peut jouer, la partie est terminée : la logique peut alors compter les
pions de chaque couleur et déterminer le vainqueur.

## Interface graphique (Tkinter)

L’*interface graphique* de notre jeu a été réalisée avec la bibliothèque
`Tkinter` de Python. Elle permet d’afficher le plateau de jeu, de
représenter les pions, et d’assurer l’interaction avec le joueur.
Concrètement, nous avons créé une fenêtre principale (`Tk`) contenant un
`canvas` qui sert de surface d’affichage pour les 64 cases du plateau.

Afin d’améliorer l’esthétique de l’interface, nous avons conçu une image
de fond du plateau et des pions personnalisés (noirs, blancs, gris,
etc.) à l’aide de `Photoshop`. Les cases ne sont pas dessinées
explicitement mais délimitées en fonction de cette image de fond : nous
superposons des pions sur les coordonnées précises de chaque case, ce
qui nous permet de conserver une précision fonctionnelle tout en
maintenant une apparence visuelle agréable.

L’affichage est mis à jour dynamiquement après chaque action : ajout
d’un pion, retournement des pions adverses, changement de tour, etc.
L’utilisateur est ainsi visuellement guidé tout au long de la partie.

Nous avons également intégré des effets sonores en utilisant la
bibliothèque `simpleaudio`. Un son est joué à chaque placement de pion
afin de renforcer le retour utilisateur. Pour utiliser cette
bibliothèque, il est nécessaire d’exécuter la commande
`pip install simpleaudio`. À noter que cette bibliothèque peut présenter
des problèmes de compatibilité avec certaines versions de Python :
d’après nos tests, la version `3.11.9` fonctionne parfaitement.

L’interaction utilisateur se fait principalement via la souris : le
joueur peut cliquer sur une case pour jouer un pion. Nous avons associé
à chaque case un gestionnaire d’événement TKinter `<Boutton-1>` qui,
lorsqu’un clic gauche est détecté sur une case, appelle la fonction de
logique du jeu correspondante pour tenter de jouer le coup à cet
emplacement. Si le coup est valide, la logique met à jour le plateau et
renvoie le contrôle à l’interface pour rafraîchir l’affichage. Si le
coup est invalide (par exemple clic sur une case où le joueur ne peut
pas jouer ou en dehors du plateau), l’interface ignore le clic. Dans
notre projet, nous avons choisi de simplement ne rien faire en cas de
coup invalide, afin de ne pas interrompre le flux du jeu, on aurait pu
afficher une erreur ou un message.  
L’interface propose également le choix du mode de jeu au démarrage, via
un écran d’accueil simple : le joueur peut choisir de jouer contre un
autre humain (partie locale à deux) ou contre l’IA. Dans le mode Joueur
contre j-Joueur, l’interface alterne simplement les tours entre les deux
joueurs. Dans le mode Joueur contre IA, dès que le joueur a joué son
coup, l’interface sollicite l’IA pour calculer la réponse de
l’ordinateur.

## Intelligence artificielle (IA)

La classe *IAOthello* contient l’implémentation de l’algorithme de
décision pour le mode joueur contre IA. Il fait appel à la logique du
jeu pour simuler les coups et évaluer les configurations. Dans notre
projet, l’IA utilise l’algorithme Minmax pour explorer les coups
possibles, amélioré par l’optimisation alpha-bêta pour réduire l’espace
de recherche. L’IA dispose d’une fonction d’évaluation heuristique qui
attribue un score à une configuration donnée du plateau (nous la
détaillons plus tard dans le compte-rendu). Connaissant cette fonction
d’évaluation, l’algorithme d’IA tente de choisir le coup qui maximise
les chances de victoire de l’ordinateur.

Concrètement, lorsque c’est au tour de l’IA de jouer, l’interface
graphique appelle une fonction principale de l’IA
`jouer_coup(self, plateau)` qui retourne les coordonnées du coup
considéré comme optimal. Cette fonction va générer récursivement l’arbre
des coups possibles en utilisant Minmax/Alpha-Bêta : pour chaque coup
envisageable du joueur IA, on simule le coup en copiant le plateau
actuel dans une structure temporaire (une copie du tableau de jeu grâce
à la fonction : `clone_plateau(self, plateau)`), puis on regarde la
réponse du joueur adverse, et ainsi de suite, jusqu’à une profondeur
donnée. Une fois le meilleur coup calculé, le module IA le renvoie à
l’interface graphique qui l’applique en appelant la même fonction
`jouer_coup` et met à jour l’affichage.

# Algorithmes d’intelligence artificielle

Pour que l’ordinateur puisse jouer à l’Othello, nous avons implémenté un
algorithme de recherche de coup inspiré de *Minmax*, un classique pour
les jeux à deux joueurs à somme nulle et en jeu à information parfaite.
Étant donné la complexité du jeu (le nombre de configurations possibles
est énorme), nous limitons la profondeur de recherche de Minmax et nous
utilisons une *fonction d’évaluation heuristique* pour estimer la valeur
d’une position. De plus, nous améliorons l’efficacité de la recherche
grâce à l’élagage *alpha-bêta*, qui évite d’explorer des branches
inutiles de l’arbre de jeu sans altérer le résultat final du Minmax.  

Afin d’optimiser la recherche dans l’algorithme Minmax, nous mettons en
place un tri préalable des coups possibles en fonction de leur
pertinence stratégique. Chaque coup est évalué à l’aide d’une fonction
simple qui attribue un score basé sur plusieurs critères :

- **Prise de coin** : les coins sont les positions les plus précieuses,
  car ils ne peuvent plus être repris une fois joués.

- **Positions en bordure** : les cases situées sur les bords sont
  intéressantes car elles offrent une meilleure stabilité que les cases
  centrales.

- **Nombre de pions retournés** : bien que cela soit plus utile en fin
  de partie, retourner plusieurs pions reste un indicateur d’efficacité
  d’un coup.

- **Évitement des cases dangereuses** : certaines positions, comme les
  cases adjacentes aux coins non contrôlés, peuvent offrir des
  opportunités à l’adversaire et doivent être évitées.

Ces critères sont combinés pour calculer un score global pour chaque
coup. Une fois cette évaluation effectuée, les coups sont triés par
ordre décroissant de score. Ensuite, seuls les 8 meilleurs coups sont
conservés pour l’exploration dans Minmax. Cette limitation permet de
réduire significativement le temps de calcul sans nuire de manière
notable à la qualité des décisions prises par l’IA.

## Algorithme Minmax

L’algorithme Minmax explore récursivement les différents scénarios de
jeu en alternant entre un niveau où l’IA cherche à maximiser le score
(niveau Max) et un niveau où l’adversaire cherche à minimiser le score
du joueur (niveau Min). Chaque position de jeu se voit attribuer une
valeur (score) du point de vue du joueur IA : une position très
favorable à l’IA aura une valeur élevée, tandis qu’une position
défavorable (avantageuse pour l’adversaire) aura une valeur faible (ou
négative). Le Minmax pur évalue les feuilles de l’arbre (fin de partie)
en fonction du résultat (victoire, défaite ou nul). Dans notre
implémentation, nous ne pouvons pas explorer jusqu’à la fin du jeu sauf
en toute fin de partie, nous arrêtons donc la recherche récursive au
bout d’une certaine profondeur fixe (par exemple, 7 niveaux de coups à
l’avance) et nous utilisons la fonction d’évaluation heuristique pour
estimer le score des positions où l’on coupe la recherche.

Le pseudocode simplifié de l’algorithme Minmax est donné ci-dessous. On
suppose une fonction `get_valid_moves(self, plateau, joueur)` qui
retourne la liste de tous les coups possibles pour `joueur` dans la
`position` courante, ainsi qu’une fonction
`evaluer_plateau(self, plateau)` qui donne le score heuristique pour la
position (du point de vue du joueur IA). La variable `maximisant` est un
booléen indiquant si le niveau actuel correspond au joueur IA (`True`)
ou à son adversaire (`False`) :

    <pre>
    ```python

    fonction Minmax(plateau, profondeur,alpha, beta,  maximisant):
    if profondeur == 0 or position == fin:
        return evaluer_plateau(position)
    if maximisant:
        meilleur_score = -inf
        pour chaque coup dans get_valid_moves(self, plateau, joueur):
            nouvelle_position = position après avoir joué coup
            score = Minmax(nouvelle_position, profondeur-1,alpha, beta False)
            alpha = max(alpha, evaluation)
            if beta <= alpha:
                break
            meilleur_score = max(meilleur_score, score)
        return meilleur_score
    else:
        pire_score = +inf
        pour chaque coup dans get_valid_moves(self, plateau, joueur):
            nouvelle_position = position après avoir joué coup
            score = Minmax(nouvelle_position, depth-1, True)
            beta = min(beta, evaluation)
            if beta <= alpha:
                break 
            pire_score = min(pire_score, score)
        return pire_score
    ```
    </pre>

**À noter :** dans la version finale de notre algorithme Minmax, nous
n’utilisons plus directement la fonction `get_valid_moves` à chaque
niveau de récursion. A la place, nous pré-calculons les coups valides au
début de l’itération, puis nous trions cette liste selon leur score
estimé via une fonction d’évaluation simple (coins, bords, stabilité,
etc.). Cette liste triée est ensuite réutilisée directement dans le
reste du processus de recherche. Cela permet à la fois de réduire le
temps de calcul et d’explorer les coups les plus prometteurs en
priorité, ce qui améliore l’efficacité de l’élagage alpha-bêta.

Ce parcours d’arbre retourne le score évalué optimal pour le joueur IA
en supposant que l’adversaire joue parfaitement pour minimiser ce score.
Pour obtenir le coup à jouer effectivement, on encapsule généralement
cet algorithme dans une fonction qui, au lieu de retourner directement
le score, parcourt les coups initiaux possibles et sélectionne celui
dont le score Minmax est maximal.

## Optimisation alpha-bêta

L’optimisation alpha-bêta consiste à couper des branches entières de
l’arbre de recherche qui ne peuvent de toute façon pas affecter la
décision finale. Deux bornes, notées *α* et *β*, sont maintenues au
cours de la recherche : *α* représente le meilleur score (le plus élevé)
trouvé jusqu’à présent pour le niveau Max (IA), et *β* représente le
meilleur score (le plus bas) trouvé jusqu’à présent pour le niveau Min
(adversaire). Si au cours de l’exploration, l’algorithme découvre qu’une
position mène à un score pire que *α* pour le joueur Max (ou meilleur
que *β* pour le joueur Min), alors il peut arrêter d’explorer les
successeurs de cette position car le joueur adverse choisirait une autre
branche plus favorable pour lui-même. En d’autres termes, si
l’adversaire a une option qui conduit à une valeur inférieure ou égale à
une valeur que Max, alors l’adversaire ne permettra jamais à Max
d’atteindre cette branche.  

Grâce à l’élagage alpha-bêta, le nombre de nœuds évalués est
significativement réduit par rapport à Minmax pur, surtout si les coups
sont bien ordonnés. Dans le meilleur des cas, l’algorithme alpha-bêta
permet de parcourir un arbre de profondeur *d* avec une complexité en
*O*(*b*<sup>*d*/2</sup>) au lieu de *O*(*b*<sup>*d*</sup>) pour Minmax,
où *b* est le facteur de branchement (nombre moyen de coups possibles
par position).

## Fonction d’évaluation heuristique

La fonction d’évaluation est un élément crucial de l’IA : c’est elle qui
attribue une valeur numérique à une position non finale pour estimer les
chances de victoire du joueur IA. Nous avons conçu une fonction prenant
en compte plusieurs critères classiques du jeu Othello, pondérés pour
refléter leur importance au fil de la partie :

- **Parité (différence de pions)** : nombre de pions du joueur IA moins
  nombre de pions de l’adversaire. En fin de partie, maximiser son
  nombre de pions est l’objectif principal. En début de partie, ce
  critère a moins d’importance (avoir trop de pions peut même être
  défavorable), mais il reste utile d’en tenir compte.

- **Mobilité** : nombre de coups valides disponibles. On calcule la
  mobilité du joueur IA et celle de l’adversaire (c’est-à-dire le nombre
  de coups possibles pour chacun depuis la position courante). Une
  mobilité supérieure de l’IA indique qu’il a plus de choix de coups (ce
  qui est bon), tandis qu’une faible mobilité signifie qu’il est à court
  d’options (ce qui est dangereux). L’heuristique intégre la différence
  de mobilités, pour encourager les positions où l’adversaire a peu de
  mouvements possibles et l’IA beaucoup.

- **Coins** : les coins (du plateau) sont des positions stratégiques car
  un pion placé dans un coin ne peut jamais être repris par
  l’adversaire. Notre évaluation attribue donc un bonus important pour
  chaque coin détenu par le joueur IA, et un malus symétrique pour
  chaque Un coin détenu par l’adversaire est désavantageux pour l’IA.
  Nous prenons également en compte si un coin est *sécurisé* ou non : un
  coin est considéré comme sécurisé lorsque les bordures adjacentes à ce
  coin sont aussi contrôlées par l’IA, ce qui renforce sa stabilité.

- **Cases Dangereuses** : les cases dites Dangereuses sont les cases
  adjacentes en diagonale, verticale, horizontale aux coins (par exemple
  B1, B2, A2, par rapport au coin A1). Placer un pion sur une case
  dangereuses est généralement risqué si le coin adjacent est vide, car
  cela offre une opportunité à l’adversaire de s’emparer du coin plus
  tard. Ainsi, notre fonction d’évaluation donne un score négatif
  (malus) pour chaque pion du joueur IA sur une case dangereuse (si le
  coin correspondant n’appartient à personne), et un bonus si c’est
  l’adversaire qui a un pion sur une telle case (puisque c’est
  défavorable pour lui).

- **Stabilité des pions** : on appelle pions stables les pions qui ne
  pourront plus être retournés d’ici la fin de la partie, quels que
  soient les coups à venir (typiquement, les pions dans les coins sont
  stables, de même que certains pions adossés à des coins). Plus un
  joueur a de pions stables, plus sa position est solide. Notre
  heuristique estime le nombre de pions stables pour le joueur IA et
  pour l’adversaire (par exemple en considérant que les pions dans les
  coins et éventuellement certains pions sur les bords adjacents à des
  coins déjà pris sont stables), et ajoute un bonus proportionnel à
  l’écart de pions stables en faveur de l’IA.

- **Motifs (patterns)** : Enfin, l’évaluation peut prendre en compte
  certains motifs spécifiques de pions sur le plateau. Par exemple, des
  configurations particulières près des coins, comme le triangle — un
  arrangement de trois pions formant un triangle dans l’angle d’un coin
  — peuvent être un signe de bonne position, car cette structure est
  souvent irrécupérable par l’adversaire. D’autres motifs stratégiques
  pourront être ajoutés ultérieurement pour affiner encore
  l’heuristique.

  
La fonction d’évaluation combine ces critères linéairement pour produire
un score final, en tenant compte du contexte de la partie (début, milieu
ou fin) ainsi que du style de jeu choisi pour l’IA. Chaque critère
(différence de pions, prise de coins, mobilité, stabilité des pions,
motifs triangulaires, et présence sur des cases dangereuses) est associé
à un poids numérique qui reflète son importance relative dans la
stratégie globale.

Ces poids ne sont pas constants tout au long de la partie : ils sont
ajustés dynamiquement en fonction du nombre total de pions présents sur
le plateau. Ainsi :

- En **début de partie** (moins de 20 pions), l’accent est mis sur la
  mobilité et les motifs prés du bord, tandis que la stabilité des pions
  est encore peu significative.

- En **milieu de partie** (entre 20 et 50 pions), tous les critères sont
  pris en compte de manière plus équilibrée, avec une importance
  croissante pour la stabilité et la différence de pions.

- En **fin de partie** (plus de 50 pions), la stabilité et la différence
  de pions deviennent primordiales, car ils conditionnent directement le
  score final. La mobilité, quant à elle, devient moins déterminante.

De plus, le style de jeu de l’IA influence les pondérations attribuées
aux critères. Par exemple, un style offensif augmente l’importance de la
différence de pions et de la mobilité, tandis qu’un style défensif
renforce le poids de la stabilité et pénalise davantage les cases
dangereuses. Le style stratégique valorise la prise de coins et
l’utilisation intelligente des motifs comme les triangles.

Finalement, le score global de la position est calculé en multipliant
chaque critère par son poids associé, puis en additionnant les
résultats. Ce score est utilisé par l’algorithme Minmax pour comparer
les différentes positions possibles et choisir le coup optimal.

  
Cette fonction d’évaluation permet à l’IA d’estimer la qualité d’une
position sans avoir à jouer tous les coups jusqu’à la fin. Elle n’est
pas parfaite, mais combine des connaissances stratégiques connues
d’Othello pour guider l’algorithme de recherche. Nous avons testé et
ajusté ses pondérations afin que l’IA joue de manière équilibrée (par
exemple, éviter qu’elle ne prenne un coin trop tôt en jouant une case
dangereuse, ou qu’elle ne cherche pas systématiquement à maximiser le
nombre de pions au détriment de la position).

# Conclusion

Ce projet Othello a permis de mettre en œuvre de nombreux aspects de la
programmation informatique : développement d’une interface graphique
interactive, implémentation rigoureuse des règles d’un jeu de société,
et utilisation d’algorithmes d’intelligence artificielle pour créer un
adversaire automatisé. Le résultat final est un jeu fonctionnel où deux
joueurs peuvent s’affronter, ou où un joueur peut mesurer ses talents
face à une IA capable de décisions stratégiques basées sur un algorithme
Minmax et une heuristique élaborée.

Nous avons veillé à produire un code clair et bien structuré, en
séparant les composants et en commentant les parties délicates. Les
tests effectués garantissent une expérience de jeu fluide et conforme
aux règles officielles. L’IA offre un niveau de jeu correct pour un
programme de ce type : elle sait profiter des opportunités (par exemple
capturer les coins) tout en évitant les pièges évidents (comme jouer
dans les cases dangereuses trop tôt dans la partie).

En perspective, il serait possible d’améliorer encore l’IA en augmentant
la profondeur de recherche si les performances le permettent, ou en
implémentant des techniques d’optimisation supplémentaires (table de
transposition pour garder en mémoire les cuops, etc.). On pourrait
également affiner la fonction d’évaluation ou la faire évoluer en la
calibrant à l’aide de méthodes d’apprentissage. Néanmoins, telles
quelles, ces améliorations sortent du cadre de ce projet.

Pour conclure, ce projet nous a non seulement permis de réaliser un jeu
Othello complet et ludique, mais il nous a également fait approfondir
des concepts importants comme la gestion d’interface en Tkinter et la
programmation d’une IA.