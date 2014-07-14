# -*- coding: UTF-8 -*-
#!/usr/bin/env python
##from __future__ import unicode_literals
#-------------------------------------------------------------------------------
# Name:         InfosKML
# Purpose:      Use GDAL/OGR library to extract informations about
#                   Keyhole Markup Language, Google Earth standard
#                   format. It permits a more friendly use as
#                   submodule.
#
# Author:       Julien Moura (https://github.com/Guts/)
#
# Python:       2.7.x
# Created:      18/06/2013
# Updated:      21/07/2014
# Licence:      GPL 3
#-------------------------------------------------------------------------------

################################################################################
########### Libraries #############
###################################
# Standard library
from os import walk, path       # files and folder managing
from time import localtime, strptime, strftime

# Python 3 backported
from collections import OrderedDict as OD

# 3rd party libraries
from osgeo import ogr    # handling vector spatial files
from osgeo import osr

################################################################################
########### Classes #############
#################################

class Read_KML():
    def __init__(self, layerpath, dico_layer, dico_fields, tipo, text=''):
        u""" Uses OGR functions to extract basic informations about
        geographic vector file (handles shapefile or MapInfo tables)
        and store into dictionaries.

        layerpath = path to the geographic file
        dico_layer = dictionary for global informations
        dico_fields = dictionary for the fields' informations
        li_fieds = ordered list of fields
        tipo = file format
        text = dictionary of text in the selected language

        """
        # Creating variables
        self.alert = 0
        source = ogr.Open(layerpath, 0)     # OGR driver
        if not source:
            u""" if layer doesn't have any object, return an error """
            print 'no compatible source'
            self.erratum(dico_layer, layerpath, u'err_nobjet')
            self.alert = self.alert +1
        self.layer = source.GetLayer()          # get the layer
        if self.layer.GetFeatureCount() == 0:
            u""" if layer doesn't have any object, return an error """
            self.erratum(dico_layer, layerpath, u'err_nobjet')
            self.alert = self.alert +1
            return None
        
        obj = self.layer.GetFeature(1)        # get the first object (shp)
        self.geom = obj.GetGeometryRef()       # get the geometry

        self.def_couche = self.layer.GetLayerDefn()  # get layer definitions
        self.srs = self.layer.GetSpatialRef()   # get spatial system reference
        self.srs.AutoIdentifyEPSG()     # try to determine the EPSG code

        # basic information
        dico_layer[u'type'] = tipo
        self.infos_basics(layerpath, dico_layer, text)
        # geometry information
        self.infos_geom(dico_layer, text)
        # fields information
        self.infos_fields(dico_fields)

    def infos_basics(self, layerpath, dico_layer, txt):
        u""" get the global informations about the layer """
        # srs type
        srsmetod = [
                    (self.srs.IsCompound(), txt.get('srs_comp')),
                    (self.srs.IsGeocentric(), txt.get('srs_geoc')),
                    (self.srs.IsGeographic(), txt.get('srs_geog')),
                    (self.srs.IsLocal(), txt.get('srs_loca')),
                    (self.srs.IsProjected(), txt.get('srs_proj')),
                    (self.srs.IsVertical(), txt.get('srs_vert'))
                    ]
        for srsmet in srsmetod:
            if srsmet[0] == 1:
                typsrs = srsmet[1]
        dico_layer[u'srs_type'] = unicode(typsrs)
        # Storing into the dictionary
        dico_layer[u'name'] = path.basename(layerpath)
        dico_layer[u'folder'] = path.dirname(layerpath)
        dico_layer[u'title'] = dico_layer[u'name'][:-4].replace('_', ' ').capitalize()
        dico_layer[u'num_obj'] = self.layer.GetFeatureCount()
        dico_layer[u'num_fields'] = self.def_couche.GetFieldCount()
        # Handling exception in srs names'encoding
        try:
            if self.srs.GetAttrValue('PROJCS') != 'unnamed':
                dico_layer[u'srs'] = unicode(self.srs.GetAttrValue('PROJCS')).replace('_', ' ')
            else:
                dico_layer[u'srs'] = unicode(self.srs.GetAttrValue('PROJECTION')).replace('_', ' ')
        except UnicodeDecodeError, e:
            if self.srs.GetAttrValue('PROJCS') != 'unnamed':
                dico_layer[u'srs'] = self.srs.GetAttrValue('PROJCS').decode('latin1').replace('_', ' ')
            else:
                dico_layer[u'srs'] = self.srs.GetAttrValue('PROJECTION').decode('latin1').replace('_', ' ')
        dico_layer[u'EPSG'] = unicode(self.srs.GetAttrValue("AUTHORITY", 1))
        # Getting basic dates
        dico_layer[u'date_actu'] = strftime('%Y-%m-%d',
                                            localtime(path.getmtime(layerpath)))
        dico_layer[u'date_crea'] = strftime('%Y-%m-%d',
                                            localtime(path.getctime(layerpath)))
        # SRS exception handling
        if dico_layer[u'EPSG'] == u'4326' and dico_layer[u'srs'] == u'None':
            print dico_layer[u'srs']
            dico_layer[u'srs'] = u'WGS 84'
            print dico_layer[u'srs']

        # end of function
        return dico_layer

    def infos_geom(self, dico_layer, txt):
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

    def erratum(self, dicolayer, layerpath, mess):
        u""" errors handling """
        # local variables
        dicolayer[u'name'] = path.basename(layerpath)
        dicolayer[u'folder'] = path.dirname(layerpath)
        try:
            def_couche = self.layer.GetLayerDefn()
            dicolayer[u'num_fields'] = def_couche.GetFieldCount()
        except AttributeError:
            mess = mess    
        finally:
            dicolayer[u'error'] = mess
        # End of function
        return dicolayer

################################################################################
###### Stand alone program ########
###################################

if __name__ == '__main__':
    u""" standalone execution for tests. Paths are relative considering a test
    within the official repository (https://github.com/Guts/DicoGIS)"""
    # libraries import
    from os import getcwd, chdir, path
    # test files
    li_kml = [path.join(getcwd(), r'..\test\datatest\vectors\kml\wc2014_MapTour.kml')]  # kml
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
    # execution
    for kml in li_kml:
        """ looping on kml list """
        # reset recipient data
        dico_layer.clear()
        dico_fields.clear()
        # getting the informations
        print kml
        info_kml = Read_KML(kml, dico_layer, dico_fields, 'kml', textos)
        print '\n', dico_layer, dico_fields