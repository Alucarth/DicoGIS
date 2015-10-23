# -*- coding: UTF-8 -*-
#!/usr/bin/env python
# from __future__ import unicode_literals

#------------------------------------------------------------------------------
# Name:         Infos LYR
# Purpose:      Get some metadata abour LYR files (Esri symbology layer))
#
# Author:       Julien Moura (https://github.com/Guts/)
#
# Python:       2.7.x
# Created:      28/09/2015
# Updated:      12/10/2015
# Licence:      GPL 3
#------------------------------------------------------------------------------

###############################################################################
########### Libraries #############
###################################
# Standard library
from os import path, chdir, listdir   # files and folder managing
from time import localtime, strftime

# Python 3 backported
from collections import OrderedDict as OD

# 3rd party libraries
try:
    from arcpy import env as enviro, Describe
    from arcpy.mapping import Layer, ListLayers
except ImportError:
    pass

###############################################################################
########### Classes #############
#################################

class Read_LYR():
    def __init__(self, lyrpath, dico_lyr, tipo, txt=''):
        u""" Uses OGR functions to extract basic informations about
        geographic vector file (handles shapefile or MapInfo tables)
        and store into dictionaries.

        lyrpath = path to the LYR file
        dico_lyr = dictionary for global informations
        tipo = format
        text = dictionary of text in the selected language

        see: http://resources.arcgis.com/fr/help/main/10.2/index.html#//00s300000008000000
        """
        # changing working directory to layer folder
        chdir(path.dirname(lyrpath))

        # raising arcpy specific exceptions
        self.alert = 0

        # opening LYR
        layer = Describe(lyrpath)
        print "Name String:        " + layer.nameString
        print "Where Clause:       " + layer.whereClause

        # Find out if the layer represents a feature class
        if layer.dataElement.dataType != "FeatureClass":
            self.alert += 1
            self.erratum(dico_lyr, lyrpath, u'err_incomp')
        else:
            print "Feature class:      " + layer.dataElement.catalogPath
            print "Feature class Type: " + layer.featureClass.featureType

        # LYR name and parent folder
        dico_lyr['name'] = layer.nameString
        dico_lyr['folder'] = path.dirname(lyrpath)

        # layers count and names
        dico_lyr['layers_count'] = layer.GetLayerCount()
        li_layers_names = []
        li_layers_idx = []
        dico_lyr['layers_names'] = li_layers_names
        dico_lyr['layers_idx'] = li_layers_idx

        # dependencies
        dependencies = [f for f in listdir(path.dirname(lyrpath))
                        if path.splitext(path.abspath(f))[0] == path.splitext(lyrpath)[0]
                        and not path.splitext(path.abspath(f).lower())[1] == ".lyr"]
        dico_lyr[u'dependencies'] = dependencies

        # cumulated size
        dependencies.append(lyrpath)
        total_size = sum([path.getsize(f) for f in dependencies])
        dico_lyr[u"total_size"] = self.sizeof(total_size)
        dependencies.pop(-1)

        # global dates
        dico_lyr[u'date_actu'] = strftime('%d/%m/%Y',
                                          localtime(path.getmtime(lyrpath)))
        dico_lyr[u'date_crea'] = strftime('%d/%m/%Y',
                                          localtime(path.getctime(lyrpath)))
        # total fields count
        total_fields = 0
        dico_lyr['total_fields'] = total_fields
        # total objects count
        total_objs = 0
        dico_lyr['total_objs'] = total_objs
        # parsing layers
    #     for layer_idx in range(lyr.GetLayerCount()):
    #         # dictionary where will be stored informations
    #         dico_layer = OD()
    #         # parent LYR
    #         dico_layer['lyr_name'] = path.basename(lyr.GetName())
    #         # getting layer object
    #         layer = lyr.GetLayerByIndex(layer_idx)
    #         # layer name
    #         li_layers_names.append(layer.GetName())
    #         # layer index
    #         li_layers_idx.append(layer_idx)
    #         # getting layer globlal informations
    #         self.infos_basics(layer, dico_layer, txt)
    #         # storing layer into the LYR dictionary
    #         dico_lyr['{0}_{1}'.format(layer_idx,
    #                                   layer.GetName())] = dico_layer
    #         # summing fields number
    #         total_fields += dico_layer.get(u'num_fields')
    #         # summing objects number
    #         total_objs += dico_layer.get(u'num_obj')
    #         # deleting dictionary to ensure having cleared space
    #         del dico_layer
    #     # storing fileds and objects sum
    #     dico_lyr['total_fields'] = total_fields
    #     dico_lyr['total_objs'] = total_objs

    # def infos_basics(self, layer_obj, dico_layer, txt):
    #     u""" get the global informations about the layer """
    #     # title and features count
    #     dico_layer[u'title'] = layer_obj.GetName()
    #     dico_layer[u'num_obj'] = layer_obj.GetFeatureCount()

    #     # getting geography and geometry informations
    #     srs = layer_obj.GetSpatialRef()
    #     self.infos_geos(layer_obj, srs, dico_layer, txt)

    #     # getting fields informations
    #     dico_fields = OD()
    #     layer_def = layer_obj.GetLayerDefn()
    #     dico_layer['num_fields'] = layer_def.GetFieldCount()
    #     self.infos_fields(layer_def, dico_fields)
    #     dico_layer['fields'] = dico_fields

    #     # end of function
    #     return dico_layer

    # def infos_geos(self, layer_obj, srs, dico_layer, txt):
    #     u""" get the informations about geography and geometry """
    #     if srs:
    #         # SRS
    #         srs.AutoIdentifyEPSG()
    #         # srs type
    #         srsmetod = [(srs.IsCompound(), txt.get('srs_comp')),
    #                     (srs.IsGeocentric(), txt.get('srs_geoc')),
    #                     (srs.IsGeographic(), txt.get('srs_geog')),
    #                     (srs.IsLocal(), txt.get('srs_loca')),
    #                     (srs.IsProjected(), txt.get('srs_proj')),
    #                     (srs.IsVertical(), txt.get('srs_vert'))]
    #         # searching for a match with one of srs types
    #         for srsmet in srsmetod:
    #             if srsmet[0] == 1:
    #                 typsrs = srsmet[1]
    #             else:
    #                 continue
    #         # in case of not match
    #         try:
    #             dico_layer[u'srs_type'] = unicode(typsrs)
    #         except UnboundLocalError:
    #             typsrs = txt.get('srs_nr')
    #             dico_layer[u'srs_type'] = unicode(typsrs)

    #         # handling exceptions in srs names'encoding
    #         try:
    #             if srs.GetAttrValue('PROJCS') != 'unnamed':
    #                 dico_layer[u'srs'] = unicode(srs.GetAttrValue('PROJCS')).replace('_', ' ')
    #             else:
    #                 dico_layer[u'srs'] = unicode(srs.GetAttrValue('PROJECTION')).replace('_', ' ')
    #         except UnicodeDecodeError:
    #             if srs.GetAttrValue('PROJCS') != 'unnamed':
    #                 dico_layer[u'srs'] = srs.GetAttrValue('PROJCS').decode('latin1').replace('_', ' ')
    #             else:
    #                 dico_layer[u'srs'] = srs.GetAttrValue('PROJECTION').decode('latin1').replace('_', ' ')
    #         finally:
    #             dico_layer[u'EPSG'] = unicode(srs.GetAttrValue("AUTHORITY", 1))

    #         # World SRS default
    #         if dico_layer[u'EPSG'] == u'4326' and dico_layer[u'srs'] == u'None':
    #             dico_layer[u'srs'] = u'WGS 84'
    #         else:
    #             pass
    #     else:
    #         typsrs = txt.get('srs_nr')
    #         dico_layer[u'srs_type'] = unicode(typsrs)

    #     # first feature and geometry type
    #     try:
    #         first_obj = layer_obj.GetNextFeature()
    #         geom = first_obj.GetGeometryRef()
    #     except AttributeError, e:
    #         print e, layer_obj.GetName()
    #         first_obj = layer_obj.GetNextFeature()
    #         geom = first_obj.GetGeometryRef()

    #     # geometry type human readable
    #     if geom.GetGeometryName() == u'POINT':
    #         dico_layer[u'type_geom'] = txt.get('geom_point')
    #     elif u'LINESTRING' in geom.GetGeometryName():
    #         dico_layer[u'type_geom'] = txt.get('geom_ligne')
    #     elif u'POLYGON' in geom.GetGeometryName():
    #         dico_layer[u'type_geom'] = txt.get('geom_polyg')
    #     else:
    #         dico_layer[u'type_geom'] = geom.GetGeometryName()

    #     # spatial extent (bounding box)
    #     dico_layer[u'Xmin'] = round(layer_obj.GetExtent()[0], 2)
    #     dico_layer[u'Xmax'] = round(layer_obj.GetExtent()[1], 2)
    #     dico_layer[u'Ymin'] = round(layer_obj.GetExtent()[2], 2)
    #     dico_layer[u'Ymax'] = round(layer_obj.GetExtent()[3], 2)

    #     # end of function
    #     return dico_layer

    # def infos_fields(self, layer_def, dico_fields):
    #     u""" get the informations about fields definitions """
    #     for i in range(layer_def.GetFieldCount()):
    #         champomy = layer_def.GetFieldDefn(i)  # fields ordered
    #         dico_fields[champomy.GetName()] = champomy.GetTypeName()
    #     # end of function
    #     return dico_fields

    def sizeof(self, os_size):
        u""" return size in different units depending on size
        see http://stackoverflow.com/a/1094933 """
        for size_cat in ['octets', 'Ko', 'Mo', 'Go']:
            if os_size < 1024.0:
                return "%3.1f %s" % (os_size, size_cat)
            os_size /= 1024.0
        return "%3.1f %s" % (os_size, " To")


    def erratum(self, dico_lyr, lyrpath, mess):
        u""" errors handling """
        # storing minimal informations to give clues to solve later
        dico_lyr[u'name'] = path.basename(lyrpath)
        dico_lyr[u'folder'] = path.dirname(lyrpath)
        dico_lyr[u'error'] = mess
        # End of function
        return dico_lyr

###############################################################################
###### Stand alone program ########
###################################

if __name__ == '__main__':
    u""" standalone execution for tests. Paths are relative considering a test
    within the official repository (https://github.com/Guts/DicoGIS/)"""
    # searching for DX Files
    num_folders = 0
    li_lyr = [r'..\..\test\datatest\maps_docs\lyr\PRIF 2014.lyr',
              r'..\..\test\datatest\maps_docs\lyr\PRIF 2013.lyr',
              r'..\..\test\datatest\maps_docs\lyr\PRIF 2012.lyr']

    # recipient datas
    dico_lyr = OD()

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

    # read LYR
    for lyrpath in li_lyr:
        dico_lyr.clear()
        lyrpath = path.abspath(lyrpath)
        if path.isfile(lyrpath):
            print("\n{0}: ".format(lyrpath))
            Read_LYR(lyrpath,
                     dico_lyr,
                     'Esri LYR')
            # print results
            print(dico_lyr)
        else:
            print("{0} is not a recognized file".format(lyrpath))
            pass
