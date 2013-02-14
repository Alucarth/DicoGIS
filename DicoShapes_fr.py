# -*- coding: UTF-8 -*-
#!/usr/bin/env python
#--------------------------------
# Name:         dicoshapes.py
# Purpose:      make an Excel file about shapefiles present in a databse files
#               structured, gathering basic informations. The output file could
#               be used as a database dictionary.
# Author:       Julien Moura (https://github.com/Guts)
# Created:      06/10/2011
# Last update:  09/02/2013
# Python version:  2.7.3
# Language: French (fr-fr)
#--------------------------------

###################################
########### Libraries #############
###################################

from Tkinter import Tk      # GUI
from tkFileDialog import askdirectory as doss_cible
from tkFileDialog import asksaveasfilename as savefic
from tkMessageBox import showinfo as info

from os import walk, path       # files and folder managing
from os import startfile        # open a file in Windows system

from time import localtime

from osgeo import ogr    # spatial files
from xlwt import Workbook, Font, XFStyle, easyxf, Formula   # excel library

from pickle import dump
from sys import exit

###################################
############ Functions ############
###################################

def listing_shapes(folderpath):
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

def infos_ogr(shapepath):
    u""" Uses gdal/ogr functions to extract basic informations about shapefile
    given as parameter and store into the corresponding dictionary. """
    global dico_infos_couche, dico_champs, liste_chps
    source = ogr.Open(shapepath, 0)     # OGR driver
    couche = source.GetLayer()          # get the layer
    objet = couche.GetFeature(0)        # get the first object (index 0)
    geom = objet.GetGeometryRef()       # get the geometry
    def_couche = couche.GetLayerDefn()  # get the layer definitions
    srs = couche.GetSpatialRef()        # get spatial system reference
    srs.AutoIdentifyEPSG()              # try to determine the EPSG code
    # Storing into the dictionary
    dico_infos_couche[u'nom'] = path.basename(shapepath)
    dico_infos_couche[u'titre'] = dico_infos_couche[u'nom'][:-4].replace('_', ' ').capitalize()
    dico_infos_couche[u'nbr_objets'] = couche.GetFeatureCount()
    dico_infos_couche[u'nbr_attributs'] = def_couche.GetFieldCount()
    dico_infos_couche[u'proj'] = unicode(srs.GetAttrValue("PROJCS")).replace('_', ' ')
    dico_infos_couche[u'EPSG'] = unicode(srs.GetAttrValue("AUTHORITY", 1))
    '''dico_infos_couche[u'EPSG'] = u"Projection : " + \
                                 unicode(srs.GetAttrValue("PROJCS")).replace('_', ' ') + \
                                 u" - Code EPSG : " + \
                                 unicode(srs.GetAttrValue("AUTHORITY", 1))'''
    # type géométrie
    if geom.GetGeometryName() == u'POINT':
        dico_infos_couche[u'type_geom'] = u'Point'
    elif u'LINESTRING' in geom.GetGeometryName():
        dico_infos_couche[u'type_geom'] = u'Ligne'
    elif u'POLYGON' in geom.GetGeometryName():
        dico_infos_couche[u'type_geom'] = u'Polygone'
    else:
        dico_infos_couche[u'type_geom'] = geom.GetGeometryName()
    # Spatial extent (bounding box)
    dico_infos_couche[u'Xmin'] = round(couche.GetExtent()[0],2)
    dico_infos_couche[u'Xmax'] = round(couche.GetExtent()[1],2)
    dico_infos_couche[u'Ymin'] = round(couche.GetExtent()[2],2)
    dico_infos_couche[u'Ymax'] = round(couche.GetExtent()[3],2)

    # Fields
    i = 0
    while i < def_couche.GetFieldCount():
        liste_chps.append(def_couche.GetFieldDefn(i).GetName())
        dico_champs[def_couche.GetFieldDefn(i).GetName()] = def_couche.GetFieldDefn(i).GetTypeName(),\
                                                            def_couche.GetFieldDefn(i).GetWidth(),\
                                                            def_couche.GetFieldDefn(i).GetPrecision()
        i = i+1

    dico_infos_couche[u'date_actu'] = unicode(localtime(path.getmtime(shapepath))[2]) +\
                                   u'/'+ unicode(localtime(path.getmtime(shapepath))[1]) +\
                                   u'/'+ unicode(localtime(path.getmtime(shapepath))[0])
    dico_infos_couche[u'date_creation'] = unicode(localtime(path.getctime(shapepath))[2]) +\
                                   u'/'+ unicode(localtime(path.getctime(shapepath))[1]) +\
                                   u'/'+ unicode(localtime(path.getctime(shapepath))[0])
    # end of function
    return dico_infos_couche, dico_champs, liste_chps


###################################
########### Variables #############
###################################

liste_shapes = []         # list for shapefiles path
dico_infos_couche = {}    # dictionary where will be stored informations
dico_champs = {}          # dictionary for fields information
dico_err = {}             # errors list

today = unicode(localtime()[0]) + u"-" +\
        unicode(localtime()[1]) + u"-" +\
        unicode(localtime()[2])    # date of the day
###################################
####### Output Excel file #########
###################################
# Basic configurationdu
book = Workbook(encoding = 'utf8')
feuy1 = book.add_sheet(u'Shapes', cell_overwrite_ok=True)

# Some customization: fonts and styles
# first line style
entete = XFStyle()
font1 = Font()
font1.name = 'Times New Roman'
font1.bold = True
entete.font = font1

# hyperlinks style
url = easyxf(u'font: underline single')
# errors style
erreur = easyxf(u'font: name Arial, bold 1, colour red')

# columns name
feuy1.write(0, 0, u'Nom fichier', entete)
feuy1.write(0, 1, u'Chemin', entete)
feuy1.write(0, 2, u'Thème', entete)
feuy1.write(0, 3, u'Type géométrie', entete)
feuy1.write(0, 4, u'Emprise', entete)
feuy1.write(0, 5, u'Projection', entete)
feuy1.write(0, 6, u'EPSG', entete)
feuy1.write(0, 7, u'Nombre de champs', entete)
feuy1.write(0, 8, u'Nombre d\'objets', entete)
feuy1.write(0, 9, u'Date de l\'information', entete)
feuy1.write(0, 10, u'Date dernière actualisation', entete)
feuy1.write(0, 11, u'Liste des champs', entete)

###################################################
################## Main program ###################
###################################################
# Folder "target"
root = Tk()
root.withdraw()
cible = doss_cible()

if cible == "":     # if any folder is choosen: stop the program
    root.destroy()
    exit()

# Listing of shapefiles into the folder
listing_shapes(cible)
if len(liste_shapes) == 0:  # if any shapefiles has been found: stop the program
    root.destroy()
    exit()

# Reading the shapefiles found
lig = 1
for couche in liste_shapes:
    # reset variables
    dico_infos_couche.clear()
    dico_champs.clear()
    liste_chps = []
    champs = ""
    theme = ""
    try:
        infos_ogr(couche)
    except:
        dico_err[couche] = u"Probleme dans la structure du shape." + \
                           "\n \n"
        continue
    # Add the shape informations to the Excel file
    # Name
    feuy1.write(lig, 0, dico_infos_couche.get('nom'))
    # Path of containing folder formatted to be a hyperlink
    lien = 'HYPERLINK("' + \
           couche.strip(dico_infos_couche.get('nom')) + \
           '"; "Atteindre le dossier")'    # chemin formaté pour être un lien
    feuy1.write(lig, 1, Formula(lien), url)
    # Name of containing folder
    if path.basename(path.dirname(couche)) != 'shp':
        feuy1.write(lig, 2, path.basename(path.dirname(couche)))
    else:
        feuy1.write(lig, 2, path.basename(path.dirname(path.dirname(couche))))

    # Geometry type
    feuy1.write(lig, 3, dico_infos_couche.get(u'type_geom'))
    # Spatial extent
    emprise = u"Xmin : " + unicode(dico_infos_couche.get(u'Xmin')) +\
              u", Xmax : " + unicode(dico_infos_couche.get(u'Xmax')) +\
              u", Ymin : " + unicode(dico_infos_couche.get(u'Ymin')) +\
              u", Ymax : " + unicode(dico_infos_couche.get(u'Ymax'))
    feuy1.write(lig, 4, emprise)
    # Name of srs
    feuy1.write(lig, 5, dico_infos_couche.get(u'proj'))
    # EPSG code
    feuy1.write(lig, 6, dico_infos_couche.get(u'EPSG'))
    # Number of fields
    feuy1.write(lig, 7, dico_infos_couche.get(u'nbr_attributs'))
    # Name of objects
    feuy1.write(lig, 8, dico_infos_couche.get(u'nbr_objets'))
    # Creation date
    feuy1.write(lig, 9, dico_infos_couche.get(u'date_creation'))
    # Last update date
    feuy1.write(lig, 10, dico_infos_couche.get(u'date_actu'))
    # Field informations
    for chp in liste_chps:
        # field type
        if dico_champs[chp][0] == 'Integer' or dico_champs[chp][0] == 'Real':
            tipo = u'Numérique'
        elif dico_champs[chp][0] == 'String':
            tipo = u'Texte'
        elif dico_champs[chp][0] == 'Date':
            tipo = u'Date'
        try:
            # concatenation of field informations
            champs = champs +\
                     chp +\
                     " (" + tipo +\
                     ", Lg. = " + unicode(dico_champs[chp][1]) +\
                     ", Pr. = " + unicode(dico_champs[chp][2]) + ") ; "
        except UnicodeDecodeError:
            # write a notification into the log file
            dico_err[couche] = u"Problème d'encodage sur le champ : " + \
                               chp.decode('latin1') + \
                               "\n\n"
            # décode le nom du champ litigieux
            champs = champs +\
                     chp.decode('utf8') +\
                     " (" + tipo +\
                     ", Lg. = " + unicode(dico_champs[chp][1]) +\
                     ", Pr. = " + unicode(dico_champs[chp][2]) + ") ; "

            continue

    # Once all fieds explored, wirte into the output file
    feuy1.write(lig, 11, champs)
    # And go to the next line
    lig = lig +1

## Save the Excel file
# Prompt of folder where save the file
saved = savefic(initialdir= cible,
                defaultextension = '.xls',
                initialfile = "DicoShapes_" + today + "_",
                filetypes = [("Classeurs Excel","*.xls")])
if path.splitext(saved)[1] != ".xls":
    saved = saved + ".xls"
book.save(saved)

## Log information to the user
if dico_err.keys() == []:    # s'il n'y a pas d'erreur
    info(title=u"Fin de programme", message=u"Programme terminé.\
                                              \nAucune erreur rencontrée.")
else:    # s'il y a des erreurs, création d'un fichier log
    fic = open(cible + "\\" + today + "_dico-shapes_log.txt", 'w')
    dump("Erreurs rencontrées sur les tables suivantes : \n\n", fic)
    fic.write('/n/n')
    dump(dico_err, fic)
    fic.close()
    info(title=u"Fin de programme", message=u"Programme terminé.\
        \nConsultez le fichier log créé pour les détails : \
        \n" + cible + u"\\" + unicode(today) + u"_dico-shapes_log.txt")

# End of program
startfile(fic.name)
startfile(cible)
del book