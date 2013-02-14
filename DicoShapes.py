# -*- coding: UTF-8 -*-
#!/usr/bin/env python
#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      Utilisateur
#
# Created:     14/02/2013
# Copyright:   (c) Utilisateur 2013
# Licence:     <your licence>
#-------------------------------------------------------------------------------

###################################
########### Libraries #############
###################################

from Tkinter import Tk      # GUI
from tkFileDialog import askdirectory as doss_cible
from tkFileDialog import asksaveasfilename as savefic
from tkMessageBox import showinfo as info

from sys import exit
from os import walk, path       # files and folder managing

###################################
########### Variables #############
###################################

liste_shapes = []         # list for shapefiles path

class DicoShapes:
    def __init__(self):
        u""" Constructeur de la fenêtre principale """
        self.root =Tk()
        self.root.withdraw()
        # determine the folder "target"
        cible = doss_cible()
        if cible == "":     # if any folder is choosen: stop the program
            self.erreurStop(mess = "Pas de dossier choisi")
        # Listing of shapefiles into the folder
        self.listing_shapes(cible)
        if len(liste_shapes) == 0:  # if any shapefiles has been found: stop the program
            self.erreurStop(mess = "Aucun shape compatible rencontré")

    def listing_shapes(self, folderpath):
        u""" List shapefiles contained in the folder and its subfolders """
        global liste_shapes
        for root, dirs, files in walk(folderpath):
            for i in files:
                if path.splitext(path.join(root, i))[1] == u'.shp' and \
                path.isfile(path.join(root, i)[:-4] + u'.dbf') and \
                path.isfile(path.join(root, i)[:-4] + u'.shx') and \
                path.isfile(path.join(root, i)[:-4] + u'.prj'):
                    liste_shapes.append(path.join(root, i))
        # end of function
        return liste_shapes



    def erreurStop(self, mess):
        u""" In case of error, close the GUI and stop the program """
        info(title = u'Erreur', message = mess)
        self.root.destroy()
        exit()





if __name__ == '__main__':
    DicoShapes()
    print liste_shapes
