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

from time import localtime

from osgeo import ogr    # spatial files
from xlwt import Workbook, Font, XFStyle, easyxf, Formula   # excel library

from modules import InfosOGR

###################################
########### Variables #############
###################################

liste_shapes = []         # list for shapefiles path
today = unicode(localtime()[0]) + u"-" +\
        unicode(localtime()[1]) + u"-" +\
        unicode(localtime()[2])    # date of the day
dico_infos_couche = {}    # dictionary where will be stored informations
dico_champs = {}          # dictionary for fields information
dico_err = {}             # errors list


class DicoShapes:
    def __init__(self):
        u""" Constructeur de la fenêtre principale """
        self.root =Tk()
        self.root.withdraw()
        # determine the folder "target"
        self.cible = doss_cible()
        if self.cible == "":     # if any folder is choosen: stop the program
            self.erreurStop(mess = "Pas de dossier choisi")
        self.cible = path.normpath(self.cible)
        # Listing of shapefiles into the folder
        self.listing_shapes(self.cible)
        if len(liste_shapes) == 0:  # if any shapefiles has been found: stop the program
            self.erreurStop(mess = "Aucun shape compatible rencontré")

        # creation of excel structure
        self.configexcel()

        # getting the info from shapefiles
        self.liste_chps = []
        InfosOGR(liste_shapes[0], dico_infos_couche, dico_champs, self.liste_chps)

        # saving dictionary
        self.savedico(self.book)

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

    def configexcel(self):
        # Basic configurationdu
        self.book = Workbook(encoding = 'utf8')
        self.feuy1 = self.book.add_sheet(u'Shapes', cell_overwrite_ok=True)

        # Some customization: fonts and styles
        # first line style
        self.entete = XFStyle()
        self.font1 = Font()
        self.font1.name = 'Times New Roman'
        self.font1.bold = True
        self.entete.font = self.font1

        # hyperlinks style
        self.url = easyxf(u'font: underline single')
        # errors style
        self.erreur = easyxf(u'font: name Arial, bold 1, colour red')

        # columns name
        self.feuy1.write(0, 0, u'Nom fichier', self.entete)
        self.feuy1.write(0, 1, u'Chemin', self.entete)
        self.feuy1.write(0, 2, u'Thème', self.entete)
        self.feuy1.write(0, 3, u'Type géométrie', self.entete)
        self.feuy1.write(0, 4, u'Emprise', self.entete)
        self.feuy1.write(0, 5, u'Projection', self.entete)
        self.feuy1.write(0, 6, u'EPSG', self.entete)
        self.feuy1.write(0, 7, u'Nombre de champs', self.entete)
        self.feuy1.write(0, 8, u'Nombre d\'objets', self.entete)
        self.feuy1.write(0, 9, u'Date de l\'information', self.entete)
        self.feuy1.write(0, 10, u'Date dernière actualisation', self.entete)
        self.feuy1.write(0, 11, u'Liste des champs', self.entete)

        return self.book

    def savedico(self, excel):
        u""" Save the Excel file """
        # Prompt of folder where save the file
        self.defaultname = "DicoShapes_" + today + "_"+ path.split(self.cible)[1]
        saved = savefic(initialdir= self.cible,
                        defaultextension = '.xls',
                        initialfile = self.defaultname,
                        filetypes = [("Classeurs Excel","*.xls")])
        if path.splitext(saved)[1] != ".xls":
            saved = saved + ".xls"
        self.book.save(saved)

    def erreurStop(self, mess):
        u""" In case of error, close the GUI and stop the program """
        info(title = u'Erreur', message = mess)
        self.root.destroy()
        exit()





if __name__ == '__main__':
    DicoShapes()
    print liste_shapes
