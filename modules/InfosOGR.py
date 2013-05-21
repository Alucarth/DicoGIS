# -*- coding: UTF-8 -*-
#!/usr/bin/env python
#-------------------------------------------------------------------------------
# Name:         InfosOGR
# Purpose:
#
# Author:       Julien Moura (https://github.com/Guts/)
#
# Created:      18/02/2013
# Updated:      21/05/2013
# Licence:      GPL 3
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
    def __init__(self, layerpath, dico_layer, dico_fields, tipo):
        u""" Uses gdal/ogr functions to extract basic informations about
        geographic file (handles shapefile or MapInfo tables)
        and store into the dictionaries.

        layerpath = path to the geographic file
        dico_layer = dictionary for global informations
        dico_fields = dictionary for the fields' informations
        li_fieds = ordered list of fields

        """
        # Creating variables
        print layerpath
        source = ogr.Open(layerpath, 0)     # OGR driver
        self.layer = source.GetLayer()          # get the layer
        if self.layer.GetFeatureCount() == 0:
            u""" if shape doesn't have any object, return an error """
            self.erratum(dico_layer)
            return
        try:
            obj = self.layer.GetFeature(0)        # get the first object (shp)
            self.geom = obj.GetGeometryRef()       # get the geometry
        except AttributeError, e:
            print '\t', e
            obj = self.layer.GetFeature(1)        # get the first object (tab)
            self.geom = obj.GetGeometryRef()      # get the geometry
        self.def_couche = self.layer.GetLayerDefn()  # get layer definitions
        self.srs = self.layer.GetSpatialRef()   # get spatial system reference
        self.srs.AutoIdentifyEPSG()     # try to determine the EPSG code

        # basic information
        dico_layer[u'type'] = tipo
        self.infos_basics(layerpath, dico_layer)
        # geometry information
        self.infos_geom(dico_layer)
        # fields information
        self.infos_fields(dico_fields)

    def infos_basics(self, layerpath, dico_layer):
        u""" get the globat informations about the layer """
        # srs type
        srsmetod = [
                    (self.srs.IsCompound(), "compound"),
                    (self.srs.IsGeocentric(), "Geocentric"),
                    (self.srs.IsGeographic(), "Geographic"),
                    (self.srs.IsLocal(), "Local"),
                    (self.srs.IsProjected(), "Projected"),
                    (self.srs.IsVertical(), "Vertical")
                    ]
        for srsmet in srsmetod:
            if srsmet[0] == 1:
                typsrs = srsmet[1]
        dico_layer[u'srstyp'] = unicode(typsrs)
        # Storing into the dictionary
        dico_layer[u'name'] = path.basename(layerpath)
        dico_layer[u'title'] = dico_layer[u'name'][:-4].replace('_', ' ').capitalize()
        dico_layer[u'num_obj'] = self.layer.GetFeatureCount()
        dico_layer[u'num_fields'] = self.def_couche.GetFieldCount()
        dico_layer[u'srs'] = unicode(self.srs.GetAttrValue("PROJCS")).replace('_', ' ')
        dico_layer[u'EPSG'] = unicode(self.srs.GetAttrValue("AUTHORITY", 1))
        dico_layer[u'date_actu'] = unicode(localtime(path.getmtime(layerpath))[2]) +\
                          u'/'+ unicode(localtime(path.getmtime(layerpath))[1]) +\
                          u'/'+ unicode(localtime(path.getmtime(layerpath))[0])
        dico_layer[u'date_crea'] = unicode(localtime(path.getctime(layerpath))[2]) +\
                                       u'/'+ unicode(localtime(path.getctime(layerpath))[1]) +\
                                       u'/'+ unicode(localtime(path.getctime(layerpath))[0])
        # end of function
        return dico_layer

    def infos_geom(self, dico_layer):
        u""" get the informations about geometry """
        # type géométrie
        if self.geom.GetGeometryName() == u'POINT':
            dico_layer[u'type_geom'] = u'Point'
        elif u'LINESTRING' in self.geom.GetGeometryName():
            dico_layer[u'type_geom'] = u'Ligne'
        elif u'POLYGON' in self.geom.GetGeometryName():
            dico_layer[u'type_geom'] = u'Polygone'
        else:
            dico_layer[u'type_geom'] = self.geom.GetGeometryName()
        # Spatial extent (bounding box)
        dico_layer[u'Xmin'] = round(self.layer.GetExtent()[0],2)
        dico_layer[u'Xmax'] = round(self.layer.GetExtent()[1],2)
        dico_layer[u'Ymin'] = round(self.layer.GetExtent()[2],2)
        dico_layer[u'Ymax'] = round(self.layer.GetExtent()[3],2)
        # end of function
        return dico_layer

    def infos_fields(self, dico_fields):
        u""" get the informations about fields definitions """
        for i in range(self.def_couche.GetFieldCount()):
            champomy = self.def_couche.GetFieldDefn(i) # liste ordonnée des champs
            dico_fields[champomy.GetName()] = champomy.GetTypeName(),\
                                           champomy.GetWidth(),\
                                           champomy.GetPrecision()


        # end of function
        return dico_fields

    def erratum(self, dico_layer):
        u""" errors handling """
        # local variables
        self.dico_layer[u'nom'] = path.basename(shape)
        def_couche = couche.GetLayerDefn()
        dico_infos_couche[u'num_fields'] = def_couche.GetFieldCount()
        alert = 1
        # End of function
        return self.dico_layer

################################################################################
###### Stand alone program ########
###################################

if __name__ == '__main__':
    u""" standalone execution for tests. Paths are relative considering a test
    within the official repository (https://github.com/Guts/DicoShapes/)"""
    # libraries import
    from os import getcwd, chdir, path
    # test files
    li_shp = [path.join(getcwd(), r'..\test\datatest\airports.shp')]         # shapefile
    li_tab = [path.join(getcwd(), r'..\test\datatest\airports_MI\tab\airports_MI.tab')] # MapInfo table
    # recipient datas
    dicouche = OD()     # dictionary where will be stored informations
    dico_fields = OD()     # dictionary for fields information
    # execution
    for shp in li_shp:
        """ looping on shapefiles list """
        # reset recipient data
        dicouche.clear()
        dico_fields.clear()
        # getting the informations
        info_shp = InfosOGR(li_shp[0], dicouche, dico_fields, 'shape')
        print '\n', dicouche, dico_fields, li_chps
    for tab in li_tab:
        """ looping on MapInfo tables list """
        # reset recipient data
        dicouche.clear()
        dico_fields.clear()
        # getting the informations
        info_tab = InfosOGR(li_tab[0], dicouche, dico_fields, 'table')
        print '\n', dicouche, dico_fields, li_chps



################################################################################
######## Former codelines #########
###################################

