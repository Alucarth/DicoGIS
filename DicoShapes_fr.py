#--------------------------------
# Nom:         dicoshapes.py
# Objectif:    dresse la liste des shapes présents dans une
#              arborescence, en extrait les informations de base et
#              construit un fichier excel avec les informations.
# Auteur:      Julien Moura
# Crée le :    06/10/2011
# Last update: 09/05/2012
# Python Version:  2.7.3
#--------------------------------
#!/usr/bin/env python

###################################
##### Import des librairies #######
###################################

from Tkinter import Tk

from os import walk, path

from time import localtime

from osgeo import ogr    # pour la géométrie
from xlwt import Workbook, Font, XFStyle, easyxf, Formula

from tkFileDialog import askdirectory as doss_cible
from tkFileDialog import asksaveasfilename as savefic
from tkMessageBox import showinfo as info

from pickle import dump
from sys import exit

###################################
###### Définition fonctions #######
###################################

def listing_shapes(chemin_dossier):
    u"""Liste les shapes contenus dans un répertoire et
    ses sous-répertoires"""
    global liste_shapes
    for root, dirs, files in walk(chemin_dossier):
        for i in files:
            if path.splitext(path.join(root, i))[1] == u'.shp' and \
            path.isfile(path.join(root, i)[:-4] + u'.dbf') and \
            path.isfile(path.join(root, i)[:-4] + u'.shx') and \
            path.isfile(path.join(root, i)[:-4] + u'.prj'):
                liste_shapes.append(path.join(root, i))
    return liste_shapes

def infos_ogr(chemin_couche):
    u"""Utilise les fonctions de la librairie OGR pour extraire les
    caractéristiques de la table donnée en paramètre et les stocker dans le
    dictionnaire correspondant."""
    global dico_infos_couche, dico_champs, liste_chps
    driver = ogr.GetDriverByName('ESRI Shapefile')    # driver OGR
    source = driver.Open(chemin_couche, 0)
    couche = source.GetLayer()
    objet = couche.GetFeature(0)
    geom = objet.GetGeometryRef()
    def_couche = couche.GetLayerDefn()
    srs = couche.GetSpatialRef()
    srs.AutoIdentifyEPSG()
    # remplissage du dictionnaire
    dico_infos_couche[u'nom'] = path.basename(chemin_couche)
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
    # extension
    dico_infos_couche[u'Xmin'] = round(couche.GetExtent()[0],2)
    dico_infos_couche[u'Xmax'] = round(couche.GetExtent()[1],2)
    dico_infos_couche[u'Ymin'] = round(couche.GetExtent()[2],2)
    dico_infos_couche[u'Ymax'] = round(couche.GetExtent()[3],2)

    # champs
    i = 0
    while i < def_couche.GetFieldCount():
        liste_chps.append(def_couche.GetFieldDefn(i).GetName())
        dico_champs[def_couche.GetFieldDefn(i).GetName()] = def_couche.GetFieldDefn(i).GetTypeName(),\
                                                            def_couche.GetFieldDefn(i).GetWidth(),\
                                                            def_couche.GetFieldDefn(i).GetPrecision()
        i = i+1

    dico_infos_couche[u'date_actu'] = unicode(localtime(path.getmtime(chemin_couche))[2]) +\
                                   u'/'+ unicode(localtime(path.getmtime(chemin_couche))[1]) +\
                                   u'/'+ unicode(localtime(path.getmtime(chemin_couche))[0])
    dico_infos_couche[u'date_creation'] = unicode(localtime(path.getctime(chemin_couche))[2]) +\
                                   u'/'+ unicode(localtime(path.getctime(chemin_couche))[1]) +\
                                   u'/'+ unicode(localtime(path.getctime(chemin_couche))[0])
    # fin de fonction
    return dico_infos_couche, dico_champs, liste_chps


###################################
########### Variables #############
###################################

liste_shapes = []         # liste des chemins des shapes
dico_infos_couche = {}    # dictionnaire destiné aux caractéristiques des
                          # couches analysées par le curseur OGR
dico_champs = {}          # dictionnaire destiné aux attributs
dico_err = {}             # liste des erreurs

today = unicode(localtime()[0]) + u"-" +\
        unicode(localtime()[1]) + u"-" +\
        unicode(localtime()[2])    # date du jour
###################################
######### Fichier Excel ###########
###################################
# configuration du fichier excel de sortie
book = Workbook(encoding = 'utf8')
feuy1 = book.add_sheet(u'Shapes', cell_overwrite_ok=True)

# personnalisation du fichier excel
font1 = Font()             # création police 1
font1.name = 'Times New Roman'
font1.bold = True


entete = XFStyle()         # création style pour les en-têtes
entete.font = font1             # application de la police 1 au style entete
hyperlien = easyxf(u'font: underline single')
erreur = easyxf(u'font: name Arial, bold 1, colour red')

# titre des colonnes
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
############## Programme principal ################
###################################################
# dossier à explorer
root = Tk()
root.withdraw()
cible = doss_cible()

if cible == "":          # si aucun dossier n'est choisi, le programme s'arrête
    root.destroy()
    exit()

# appel de la fonction pour lister les shapes
listing_shapes(cible)
# lecture des shapes trouvés
lig = 1
for couche in liste_shapes:
    # remise à zéro des variables
    dico_infos_couche.clear()
    dico_champs.clear()
    liste_chps = []
    champs = ""
    theme = ""
    try:
        # remplissage des dictionnaires
        infos_ogr(couche)
    except:
        dico_err[couche] = u"Probleme dans la structure du shape." + \
                           "\n \n"
        continue
    # Ecriture des infos dans le fichier excel
    # Nom de la table
    feuy1.write(lig, 0, dico_infos_couche.get('nom'))
    # Chemin du dossier contenant formaté pour être un lien
    lien = 'HYPERLINK("' + \
           couche.strip(dico_infos_couche.get('nom')) + \
           '"; "Atteindre le dossier")'    # chemin formaté pour être un lien
    feuy1.write(lig, 1, Formula(lien), hyperlien)
    # Dossier
    if path.basename(path.dirname(couche)) != 'shp':
        feuy1.write(lig, 2, path.basename(path.dirname(couche)))
    else:
        feuy1.write(lig, 2, path.basename(path.dirname(path.dirname(couche))))

    # Type de la géométrie
    feuy1.write(lig, 3, dico_infos_couche.get(u'type_geom'))
    # Emprise
    emprise = u"Xmin : " + unicode(dico_infos_couche.get(u'Xmin')) +\
              u", Xmax : " + unicode(dico_infos_couche.get(u'Xmax')) +\
              u", Ymin : " + unicode(dico_infos_couche.get(u'Ymin')) +\
              u", Ymax : " + unicode(dico_infos_couche.get(u'Ymax'))
    feuy1.write(lig, 4, emprise)
    # Nom de la projection
    feuy1.write(lig, 5, dico_infos_couche.get(u'proj'))
    # EPSG
    feuy1.write(lig, 6, dico_infos_couche.get(u'EPSG'))
    # Nombre de champs
    feuy1.write(lig, 7, dico_infos_couche.get(u'nbr_attributs'))
    # Nombre d'objets
    feuy1.write(lig, 8, dico_infos_couche.get(u'nbr_objets'))
    # Date de l'information
    feuy1.write(lig, 9, dico_infos_couche.get(u'date_creation'))
    # Date dernière actualisation des données
    feuy1.write(lig, 10, dico_infos_couche.get(u'date_actu'))
    # Liste des champs
    for chp in liste_chps:
        try:
            # détermine le type du champ
            if dico_champs[chp][0] == 'Integer' or dico_champs[chp][0] == 'Real':
                tipo = u'Numérique'
            elif dico_champs[chp][0] == 'String':
                tipo = u'Texte'
            elif dico_champs[chp][0] == 'Date':
                tipo = u'Date'
            # concatène les infos sur les champs : type, longueur et précision
            champs = champs +\
                     chp +\
                     " (" + tipo +\
                     ", Lg. = " + unicode(dico_champs[chp][1]) +\
                     ", Pr. = " + unicode(dico_champs[chp][2]) + ") ; "
        except:
            dico_err[couche] = u"Probleme sur le champ : " + \
                               chp.decode('latin1') + \
                               "\n\n"
            continue

    # Une fois tous les champs parcourus, on écrit la liste dans le excel
    feuy1.write(lig, 11, champs)
    # incrémente le numéro de ligne
    lig = lig +1
## Sauvegarde du fichier excel
# Prompt du dossier d'enregistrement
saved = savefic(initialdir= cible,
                defaultextension = '.xls',
                initialfile = "DicoShapes_" + today + "_",
                filetypes = [("Classeurs Excel","*.xls")])
if path.splitext(saved)[1] != ".xls":
    saved = saved + ".xls"
book.save(saved)

## Bilan programme
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
