# -*- coding: UTF-8 -*-
#!/usr/bin/env python
#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      Utilisateur
#
# Created:     18/02/2013
# Copyright:   (c) Utilisateur 2013
# Licence:     <your licence>
#-------------------------------------------------------------------------------

################################################################################
########### Libraries #############
###################################
# Standard library
from os import walk, path       # files and folder managing
from time import localtime

# Python 3 backported
from collections import OrderedDict as OD

# 3rd party libraries
from osgeo import ogr    # spatial files

################################################################################
########### Classes #############
###################################

class InfosOGR():
    def __init__(self, shapepath, dicoshp, dicochps, listechps):
        u""" Uses gdal/ogr functions to extract basic informations about
        shapefile given as parameter and store into the corresponding dictionary. """
        # Creating variables
        source = ogr.Open(shapepath, 0)     # OGR driver
        lay = self.source.GetLayer()          # get the layer
        if lay.GetFeatureCount() == 0:
            u""" if shape doesn't have any object, return an error """
            self.erratum(dicoshp)
            break
        self.obj = self.lay.GetFeature(0)        # get the first object (index 0)
        self.geom = self.obj.GetGeometryRef()       # get the geometry
        self.def_couche = self.lay.GetLayerDefn()  # get the layer definitions
        self.srs = self.lay.GetSpatialRef()        # get spatial system reference
        self.srs.AutoIdentifyEPSG()              # try to determine the EPSG code

        # basic information
        self.infos_basics(shapepath, dicoshp)
        # geometry information
        self.infos_geom(dicoshp)
        # fields information
        self.infos_fields(listechps, dicochps)

    def infos_basics(self, shapepath, dicoshp):
        # Storing into the dictionary
        dicoshp[u'nom'] = path.basename(shapepath)
        dicoshp[u'titre'] = dicoshp[u'nom'][:-4].replace('_', ' ').capitalize()
        dicoshp[u'nbr_objets'] = self.lay.GetFeatureCount()
        dicoshp[u'nbr_attributs'] = self.def_couche.GetFieldCount()
        dicoshp[u'proj'] = unicode(self.srs.GetAttrValue("PROJCS")).replace('_', ' ')
        dicoshp[u'EPSG'] = unicode(self.srs.GetAttrValue("AUTHORITY", 1))
        dicoshp[u'date_actu'] = unicode(localtime(path.getmtime(shapepath))[2]) +\
                          u'/'+ unicode(localtime(path.getmtime(shapepath))[1]) +\
                          u'/'+ unicode(localtime(path.getmtime(shapepath))[0])
        dicoshp[u'date_creation'] = unicode(localtime(path.getctime(shapepath))[2]) +\
                                       u'/'+ unicode(localtime(path.getctime(shapepath))[1]) +\
                                       u'/'+ unicode(localtime(path.getctime(shapepath))[0])
        # end of function
        return dicoshp

    def infos_geom(self, dicoshp):
        # type géométrie
        if self.geom.GetGeometryName() == u'POINT':
            dicoshp[u'type_geom'] = u'Point'
        elif u'LINESTRING' in self.geom.GetGeometryName():
            dicoshp[u'type_geom'] = u'Ligne'
        elif u'POLYGON' in self.geom.GetGeometryName():
            dicoshp[u'type_geom'] = u'Polygone'
        else:
            dicoshp[u'type_geom'] = self.geom.GetGeometryName()
        # Spatial extent (bounding box)
        dicoshp[u'Xmin'] = round(self.lay.GetExtent()[0],2)
        dicoshp[u'Xmax'] = round(self.lay.GetExtent()[1],2)
        dicoshp[u'Ymin'] = round(self.lay.GetExtent()[2],2)
        dicoshp[u'Ymax'] = round(self.lay.GetExtent()[3],2)
        # end of function
        return dicoshp

    def infos_fields(self, liste_chps, dicochps):
        for i in range(self.def_couche.GetFieldCount()):
            champomy = self.def_couche.GetFieldDefn(i)
            liste_chps.append(champomy.GetName())  # liste ordonnée des champs
            dicochps[champomy.GetName()] = champomy.GetTypeName(),\
                                           champomy.GetWidth(),\
                                           champomy.GetPrecision()


        # end of function
        return liste_chps, dicochps

    def erratum(self, dicoshp):
        u""" errors handling """
        # local variables
        self.dicoshp[u'nom'] = path.basename(shape)
        def_couche = couche.GetLayerDefn()
        dico_infos_couche[u'nbr_attributs'] = def_couche.GetFieldCount()
        alert = 1
        # End of function
        return self.dicoshp

################################################################################
###### Stand alone program ########
###################################

if __name__ == '__main__':
    lishps = []         # list for shapefiles path
    dicouche = {}    # dictionary where will be stored informations
    dicochps = {}          # dictionary for fields information

################################################################################
######## Former codelines #########
###################################

