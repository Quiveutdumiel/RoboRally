#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Apr  5 19:11:06 2017

@author: Alexandre Corazza
"""
import os
import sys
from PyQt4 import QtGui, QtCore
from interface import Ui_interface_ihm
#import Joueur
#import Plateau
#import Cartes
#import Robot as rob
import Jeu
import time
import plateau1 #contient un plateau de jeu 'jouable'

class IHM(QtGui.QMainWindow):
    def __init__(self):
        print('init')
        super().__init__()
        # Configuration de l'interface utilisateur.
        self.ui = Ui_interface_ihm()
        self.ui.setupUi(self)
        self.plateau = plateau1.plateau
        self.pioche = plateau1.listeCartes
        self.jeu = Jeu.Jeu(self.plateau, self.pioche)
        self.timer = QtCore.QTimer()
        
        #Mise en place de l'arrière plan
        palette = QtGui.QPalette()
        pixmap = QtGui.QPixmap("images/background.jpg")
        palette.setBrush(QtGui.QPalette.Background,QtGui.QBrush(pixmap))
        self.setPalette(palette)

        
        self.faireAffichageDesCartes = False
        

        
        ######################################################################
        #partie liée à la fsm qui DOIT se trouver dans init

        #liste des états admissibles:
        self.states = ["initialize","pick","play"]
        
        #état dans lequel se situe la fsm
        self.current_state = "initialize"
        
        #transition à effectuer au prochain appel de 'fsm': fonction et nouvel état
        self.transition = None
        
        #dictionnaire des transitions
        self.dict_tr = {
                        ("initialize",None):"initialize",("pick","play"):"play",
                        ("initialize","pick"):"pick",("pick","pick"):"pick",("play","play"):"play",
                        ("play","pick"):"pick"
                        }
        
        #dictionnaire des actions à effectuer lors de la transition
        self.dict_ac = {
                        None: (lambda *args: None), "play": self.play,
                        "pick": self.FaireAffichageDesCartes                      
                        }
        
        #On lie le timeout à la fsm
        self.timer.start(500)
        self.timer.timeout.connect(self.fsm)
        ######################################################################
        

        #Connecte les boutons aux fonctions définies en dessous

        self.ui.bouton_partie.clicked.connect(self.nvellepartie)
        self.ui.bouton_distrib.clicked.connect(self.distrib)
        self.ui.bouton_instru.clicked.connect(self.chooseCard)



##############################################      FSM - FSM - FSM       ######################################################
        
        #Partie liée à la fsm
        #la fsm sert à faire l'affichage correctement, étape par étape: pratique puisque l'on doit pouvoir revenir en arrière



    def fsm(self):
        """
        fonction appelée à chaque timeout pour l'affichage du jeu
        il s'agit d'une 'finite state machine', qui change l'état en fonction de la transition et affiche ensuite le nouvel état
        la transition est gérée par les boutons de l'ihm
        Paramètres
        ----------
        aucun, à rajouter si l'on a besoin de réinitialiser la fsm pour X raison
        """
    
        try:
            new_state = self.dict_tr[(self.current_state,self.transition)]
            if new_state in self.states:
                if new_state != self.current_state:
                    print("{} -> {}".format(self.current_state,new_state))
                self.dict_ac[self.transition]()
                self.current_state = new_state
#                self.transition = None
        except KeyError as erreur:
            print ("transition ou état non définit dans le dictionnaire respectif", erreur)
        except Victoire as VouD: #Victoire ou Défaite
            print ("C'est la {} Mamène".format(VouD))
            exit()
        
#        time.sleep(1) #juste pour débugger tranquillement
        self.affichage()


################################################################################################################################




    def nvellepartie(self):
        """Cette fonction n'est pas encore prête"""
        nbjoueur = self.ui.nbjoueur.value()
        print(nbjoueur)
        
        
    def distrib(self):
        self.jeu.prepareTour()
        self.transition = "pick"
#        self.ui.tapiscarte.update()
        
    def chooseCard(self):
        listeChoix = []
        # Le joueur choisit ses cartes tout en etant limite par la vie de son robot
        valeurs = self.ui.choixcarte.toPlainText()
        valeurs = valeurs.split(' ')
        print(len(valeurs),self.jeu.listeJoueurs[0].robot.pv - 4)
        
        #Tant qu on ne choisi pas des cartes differentes et le choix de la carte n est pas entre 0 et 8
        var = False
        for carte in valeurs:
            if int(carte) > 8 or int(carte) < 0:
                var = True
                
        
        if (not(uniqueness(valeurs)) or (len(valeurs) != self.jeu.listeJoueurs[0].robot.pv - 4) or var):
            print("Veuillez choisir {} cartes distinctes entre 0 et 8".format(self.jeu.listeJoueurs[0].robot.pv - 4) )
#            valeurs = self.ui.choixcarte.toPlainText()
#            valeurs = valeurs.split(' ')
        
        else:
            removeList = [] #liste des cartes à retirer de la pioche
            for valeur in valeurs:
                listeChoix.append(int(valeur))
                removeList.append(self.jeu.pioche[int(valeur)])
        
                # Une fois le choix effectue, on met les cartes choisies dans la variable joueur
            for i in range(self.jeu.listeJoueurs[0].robot.pv - 4):
                valeurs[i] = self.jeu.listeJoueurs[0].mainJoueur[listeChoix[i]]
                self.jeu.listeJoueurs[0].cartes[i] = self.jeu.listeJoueurs[0].mainJoueur[listeChoix[i]]

                
            self.transition = "play"

    def play(self):
        """
        Lance un tour
        """
        #penser a coder une liste qui retient les joueurs ayant déjà joué
        #penser à coder la priorité pour les cartes les plus rapides
        
        fin_tour = True
        for joueur in self.jeu.listeJoueurs:
#            print(joueur.cartes)
            if joueur.cartes:
                fin_tour = False
        
        if fin_tour:
            self.distrib()              #Si le tour est fini on redistribue
        
        else:
            for joueur in self.jeu.listeJoueurs:
                # On applique l'effet de la carte:
                carte = joueur.cartes.pop(0)
                estimated_state = carte.effet(joueur.robot)
                if True: #vérifier pour les murs etc
#                    joueur.robot.position = (estimated_state[1],estimated_state[2])
#                    joueur.robot.orientation = estimated_state[3]
#                    print(estimated_state)
                    joueur.robot.set_state(estimated_state)
#                    print(joueur.robot)
#                 On applique l'effet de la case:
                for row in self.plateau.cases:
                    for case in row:
                        if case.position == joueur.robot.position:
#                            case.effet(joueur.robot)
                            estimated_state = case.effet(joueur.robot)
                            if True:
                                joueur.robot.set_state(estimated_state)
                
            
            self.transition = "play"                    #Si le tour n'est pas fini, on continue de jouer
        
        
    def FaireAffichageDesCartes(self):
        self.faireAffichageDesCartes = True
        
        
    def affichage(self):
        """
        fonction élémentaire pour lancer toutes fonctions servant à 'refresh' l'affichage du jeu
        """
        self.ui.centralwidget.update()


    #Affichage des robots sur le plateau
    def drawrobot(self, qp):
        for joueur in self.jeu.listeJoueurs:
            joueur.robot.dessin(qp)
            
    def drawboard(self, qp):
        for rangee in self.jeu.plateau.cases:
            for case in rangee:
                case.dessin(qp, case.image)
        for mur in self.jeu.plateau.listeMurs:
            mur.dessin(qp)

    def drawcards(self, qp):
        c=0
        x=[0,0,0,1,1,1,2,2,2]
        for carte in self.jeu.listeJoueurs[0].mainJoueur:
            carte.dessin(qp, carte.image, x[c], c%3)
            c+=1

    def paintEvent(self,e):
        qp = QtGui.QPainter(self)
        self.drawboard(qp)
        self.drawrobot(qp)
        if self.faireAffichageDesCartes:
            self.drawcards(qp)
        qp.end()
     

def uniqueness(l):
    """
    Renvoie true si les éléments de la liste l sont uniques, false sinon
    ----------
    l: liste a vérifier (index dans la pioche des cartes choisies)
    """
    for i in range(len(l)):
        for j in range(i+1, len(l)):
            if l[i] == l[j]:
                return False
    return True

def realState(state1,state2,jeu):
    """
    renvoie l'état réel en tenant compte des murs et autres obstacles
    ----------
    state1: état de départ
    state2: état prévu par les cartes / cases en ignorant les conditions externes
    jeu: le jeu, contient toutes les variables nécessaires à la création de realState
    """
    listeMur = jeu.plateau.listeMur
    pass
    # a finir    
    
    
    
    

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    window = IHM()
    window.setGeometry(100,50,1300,900)
    window.show()
    app.exec_()
