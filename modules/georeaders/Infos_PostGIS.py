#!/usr/bin/env python
# -*- coding: utf-8 -*-
#from __future__ import unicode_literals
#------------------------------------------------------------------------------
# Name:         InfosOGR_PG
# Purpose:      Use GDAL/OGR library to extract informations about
#                   geographic data contained in a PostGIS database.
#                   It permits a more friendly use as submodule.
#
# Author:       Julien Moura (https://github.com/Guts/)
#
# Python:       2.7.x
# Created:      18/06/2013
# Updated:      13/08/2014
# Licence:      GPL 3
#------------------------------------------------------------------------------

###############################################################################
########### Libraries #############
###################################
# Standard library

# Python 3 backported
from collections import OrderedDict as OD

# 3rd party libraries
# 3rd party libraries
try:
    from osgeo import gdal
    from osgeo import ogr  # handler for vector spatial files
    from osgeo import osr
except ImportError:
    import gdal
    import ogr  # handler for vector spatial files
    import osr

from gdalconst import *

# gdal.SetConfigOption("PG_LIST_ALL_TABLES", "YES")

###############################################################################
########### Classes #############
###################################

class Read_PostGIS():
    def __init__(self, layer, dico_layer, dico_fields, tipo, text=''):
        u""" Uses gdal/ogr functions to extract basic informations about
        geographic file (handles shapefile or MapInfo tables)
        and store into the dictionaries.

        layer = path to the geographic file
        dico_layer = dictionary for global informations
        dico_fields = dictionary for the fields' informations
        tipo = feature type to read
        text = dictionary of texts to display
        """
        # handling GDAL/OGR specific exceptions
        gdal.AllRegister()
        ogr.UseExceptions()
        gdal.UseExceptions()

        # Creating variables
        self.alert = 0

        # raising incompatible files
        # if not source:
        #     u""" if file is not compatible """
        #     self.erratum(dico_layer, layerpath, u'err_nobjet')
        #     self.alert = self.alert + 1
        #     return None
        # else:
        #     pass

        # raising forbidden access
        try:
            obj = layer.GetFeature(1)          # get the first object (shp)
        except RuntimeError, e:
            if u'permission denied' in str(e):
                mess = str(e).split('\n')[0]
                self.alert = self.alert + 1
                self.erratum(dico_layer, layer, mess)
                return None
            else:
                pass

        self.geom = obj.GetGeometryRef()        # get the geometry
        self.def_couche = layer.GetLayerDefn() # get layer definitions
        self.srs = layer.GetSpatialRef()   # get spatial system reference
        self.srs.AutoIdentifyEPSG()             # try to determine the EPSG code

        # basic information
        dico_layer[u'type'] = tipo
        self.infos_basics(layer, dico_layer, text)
        # geometry information
        self.infos_geom(layer, dico_layer, text)
        # fields information
        self.infos_fields(layer, dico_fields)

    def infos_basics(self, layer, dico_layer, txt):
        u""" get the global informations about the layer """
        # Storing into the dictionary
        dico_layer[u'name'] = layer.GetName()
        dico_layer[u'title'] = layer.GetName().capitalize()
        dico_layer[u'num_obj'] = layer.GetFeatureCount()
        dico_layer[u'num_fields'] = self.def_couche.GetFieldCount()

        # schema name
        try:
            layer.GetName().split('.')[1]
            dico_layer[u'folder'] = layer.GetName().split('.')[0]
        except IndexError:
            dico_layer[u'folder'] = 'public'

        ## SRS
        # srs type
        srsmetod = [
                    (self.srs.IsCompound(), txt.get('srs_comp')),
                    (self.srs.IsGeocentric(), txt.get('srs_geoc')),
                    (self.srs.IsGeographic(), txt.get('srs_geog')),
                    (self.srs.IsLocal(), txt.get('srs_loca')),
                    (self.srs.IsProjected(), txt.get('srs_proj')),
                    (self.srs.IsVertical(), txt.get('srs_vert'))
                   ]
        # searching for a match with one of srs types
        for srsmet in srsmetod:
            if srsmet[0] == 1:
                typsrs = srsmet[1]
            else:
                continue
        # in case of not match
        try:
            dico_layer[u'srs_type'] = unicode(typsrs)
        except UnboundLocalError:
            typsrs = txt.get('srs_nr')
            dico_layer[u'srs_type'] = unicode(typsrs)


        # Handling exception in srs names'encoding
        try:
            if self.srs.GetAttrValue('PROJCS') != 'unnamed':
                dico_layer[u'srs'] = unicode(self.srs.GetAttrValue('PROJCS')).replace('_', ' ')
            else:
                dico_layer[u'srs'] = unicode(self.srs.GetAttrValue('PROJECTION')).replace('_', ' ')
        except UnicodeDecodeError:
            if self.srs.GetAttrValue('PROJCS') != 'unnamed':
                dico_layer[u'srs'] = self.srs.GetAttrValue('PROJCS').decode('latin1').replace('_', ' ')
            else:
                dico_layer[u'srs'] = self.srs.GetAttrValue('PROJECTION').decode('latin1').replace('_', ' ')
        dico_layer[u'EPSG'] = unicode(self.srs.GetAttrValue("AUTHORITY", 1))
        # EPSG code
        if dico_layer[u'EPSG'] == u'4326' and dico_layer[u'srs'] == u'None':
            print dico_layer[u'srs']
            dico_layer[u'srs'] = u'WGS 84'
            print dico_layer[u'srs']

        # end of function
        return dico_layer, layer, txt

    def infos_geom(self, layer, dico_layer, txt):
        u""" get the informations about geometry """
        # type géométrie
        if self.geom.GetGeometryName() == u'POINT':
            dico_layer[u'type_geom'] = txt.get('geom_point')
        elif u'LINESTRING' in self.geom.GetGeometryName():
            dico_layer[u'type_geom'] = txt.get('geom_ligne')
        elif u'POLYGON' in self.geom.GetGeometryName():
            dico_layer[u'type_geom'] = txt.get('geom_polyg')
        else:
            dico_layer[u'type_geom'] = self.geom.GetGeometryName()
        # Spatial extent (bounding box)
        dico_layer[u'Xmin'] = round(layer.GetExtent()[0],2)
        dico_layer[u'Xmax'] = round(layer.GetExtent()[1],2)
        dico_layer[u'Ymin'] = round(layer.GetExtent()[2],2)
        dico_layer[u'Ymax'] = round(layer.GetExtent()[3],2)
        # end of function
        return dico_layer

    def infos_fields(self, layer, dico_fields):
        u""" get the informations about fields definitions """
        for i in range(self.def_couche.GetFieldCount()):
            champomy = self.def_couche.GetFieldDefn(i) # ordered list of fields
            dico_fields[champomy.GetName()] = champomy.GetTypeName(),\
                                           champomy.GetWidth(),\
                                           champomy.GetPrecision()
        # End of function
        return dico_fields

    def erratum(self, dicolayer, layer, mess):
        u""" errors handling """
        # local variables
        dicolayer[u'name'] = layer.GetName()
        # schema name
        try:
            layer.GetName().split('.')[1]
            dicolayer[u'folder'] = layer.GetName().split('.')[0]
        except IndexError:
            dicolayer[u'folder'] = 'public'
        # layer definition
        def_couche = layer.GetLayerDefn()
        dicolayer[u'num_fields'] = def_couche.GetFieldCount()
        dicolayer[u'error'] = mess
        # End of function
        return dicolayer, layer

################################################################################
###### Stand alone program ########
###################################

if __name__ == '__main__':
    u""" standalone execution for tests. Paths are relative considering a test
    within the official repository (https://github.com/Guts/DicoGIS/)"""
    # libraries import
    from sys import exit
    # test text dictionary
    textos = OD()
    textos['srs_comp'] = u'Compound'
    textos['srs_geoc'] = u'Geocentric'
    textos['srs_geog'] = u'Geographic'
    textos['srs_loca'] = u'Local'
    textos['srs_proj'] = u'Projected'
    textos['srs_vert'] = u'Vertical'
    textos['geom_point'] = u'Point'
    textos['geom_ligne'] = u'Line'
    textos['geom_polyg'] = u'Polygon'
    # recipient datas
    dico_layer = OD()     # dictionary where will be stored informations
    dico_fields = OD()     # dictionary for fields information
    # PostGIS database settings
    test_host = 'postgresql1.alwaysdata.com'
    test_db = 'guts_gis'
    test_user = 'guts_player'
    test_pwd = 'letsplay'
    try:
        conn = ogr.Open("PG: host=%s dbname=%s user=%s password=%s" %(test_host, 
                                                                      test_db, 
                                                                      test_user, 
                                                                      test_pwd))
        print("Access granted : connecting people!")
        print("Layer count: {0}".format(conn.GetLayerCount()))
        sql_version = "SELECT version();"
        version = conn.ExecuteSQL(sql_version)
        # schemas list
        sql_schemas =  "select nspname from pg_catalog.pg_namespace;"
        schemas = conn.ExecuteSQL(sql_schemas)
  
        print("Driver name: {0}".format(conn.GetDriver().GetName()))
        print(dir(conn))
    except Exception, e:
        print 'Connection to database failed. Check your connection settings: {0}'.format(str(e))
        exit()
    # parsing the layers
    for layer in conn:
        dico_layer.clear()
        dico_fields.clear()
        print("\n")
        print layer.GetName()
        # if "_current"
        Read_PostGIS(layer, dico_layer, dico_fields, 'pg', textos)
        print(dico_layer)