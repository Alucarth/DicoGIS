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

from osgeo import ogr    # spatial files
from os import walk, path       # files and folder managing
from time import localtime

class InfosOGR():
    def __init__(self, shapepath, dicoshp, dicochps, listechps):
        u""" Uses gdal/ogr functions to extract basic informations about shapefile
        given as parameter and store into the corresponding dictionary. """
        source = ogr.Open(shapepath, 0)     # OGR driver
        couche = source.GetLayer()          # get the layer
        objet = couche.GetFeature(0)        # get the first object (index 0)
        geom = objet.GetGeometryRef()       # get the geometry
        def_couche = couche.GetLayerDefn()  # get the layer definitions
        srs = couche.GetSpatialRef()        # get spatial system reference
        srs.AutoIdentifyEPSG()              # try to determine the EPSG code
        # Storing into the dictionary
        dicoshp[u'nom'] = path.basename(shapepath)
        dicoshp[u'titre'] = dicoshp[u'nom'][:-4].replace('_', ' ').capitalize()
        dicoshp[u'nbr_objets'] = couche.GetFeatureCount()
        dicoshp[u'nbr_attributs'] = def_couche.GetFieldCount()
        dicoshp[u'proj'] = unicode(srs.GetAttrValue("PROJCS")).replace('_', ' ')
        dicoshp[u'EPSG'] = unicode(srs.GetAttrValue("AUTHORITY", 1))
        '''dico_infos_couche[u'EPSG'] = u"Projection : " + \
                                     unicode(srs.GetAttrValue("PROJCS")).replace('_', ' ') + \
                                     u" - Code EPSG : " + \
                                     unicode(srs.GetAttrValue("AUTHORITY", 1))'''
        # type géométrie
        if geom.GetGeometryName() == u'POINT':
            dicoshp[u'type_geom'] = u'Point'
        elif u'LINESTRING' in geom.GetGeometryName():
            dicoshp[u'type_geom'] = u'Ligne'
        elif u'POLYGON' in geom.GetGeometryName():
            dicoshp[u'type_geom'] = u'Polygone'
        else:
            dicoshp[u'type_geom'] = geom.GetGeometryName()
        # Spatial extent (bounding box)
        dicoshp[u'Xmin'] = round(couche.GetExtent()[0],2)
        dicoshp[u'Xmax'] = round(couche.GetExtent()[1],2)
        dicoshp[u'Ymin'] = round(couche.GetExtent()[2],2)
        dicoshp[u'Ymax'] = round(couche.GetExtent()[3],2)

        # Fields
        i = 0
        while i < def_couche.GetFieldCount():
            listechps.append(def_couche.GetFieldDefn(i).GetName())
            dicochps[def_couche.GetFieldDefn(i).GetName()] = def_couche.GetFieldDefn(i).GetTypeName(),\
                                                                def_couche.GetFieldDefn(i).GetWidth(),\
                                                                def_couche.GetFieldDefn(i).GetPrecision()
            i = i+1

        dicoshp[u'date_actu'] = unicode(localtime(path.getmtime(shapepath))[2]) +\
                                       u'/'+ unicode(localtime(path.getmtime(shapepath))[1]) +\
                                       u'/'+ unicode(localtime(path.getmtime(shapepath))[0])
        dicoshp[u'date_creation'] = unicode(localtime(path.getctime(shapepath))[2]) +\
                                       u'/'+ unicode(localtime(path.getctime(shapepath))[1]) +\
                                       u'/'+ unicode(localtime(path.getctime(shapepath))[0])
        # end of function
        return dicoshp, dicochps, listechps


if __name__ == '__main__':
    main()
