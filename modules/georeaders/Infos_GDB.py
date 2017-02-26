# -*- coding: UTF-8 -*-
#!/usr/bin/env python
from __future__ import (absolute_import, print_function, unicode_literals)

# ----------------------------------------------------------------------------
# Name:         InfosGDB
# Purpose:      Uses OGR to read into Esri File GeoDataBase.
#
# Author:       Julien Moura (https://github.com/Guts/)
#
# Python:       2.7.x
# Created:      24/05/2014
# Updated:      11/11/2014
# Licence:      GPL 3
# ----------------------------------------------------------------------------

# ############################################################################
# ######### Libraries #############
# #################################
# Standard library
from collections import OrderedDict  # Python 3 backported
import logging
from os import path, walk   # files and folder managing
from time import localtime, strftime

# 3rd party libraries
from osgeo import ogr, osr
from osgeo import gdal
from gdalconst import *

# custom submodules
try:
    from .gdal_exceptions_handler import GdalErrorHandler
    from .geo_infos_generic import GeoInfosGenericReader
    from .geoutils import Utils
except ValueError:
    from gdal_exceptions_handler import GdalErrorHandler
    from geo_infos_generic import GeoInfosGenericReader
    from geoutils import Utils

# ############################################################################
# ######### Globals ############
# ##############################

gdal_err = GdalErrorHandler()
georeader = GeoInfosGenericReader()
youtils = Utils()

# ############################################################################
# ######### Classes ############
# ##############################


class ReadGDB():
    def __init__(self, source_path, dico_dataset, tipo, txt=''):
        u"""Use OGR functions to extract basic informations about
        geographic vector file (handles shapefile or MapInfo tables)
        and store into dictionaries.

        source_path = path to the File Geodatabase Esri
        dico_dataset = dictionary for global informations
        dico_fields = dictionary for the fields' informations
        li_fieds = ordered list of fields
        tipo = format
        text = dictionary of text in the selected language

        """
        # handling ogr specific exceptions
        errhandler = gdal_err.handler
        gdal.PushErrorHandler(errhandler)
        gdal.UseExceptions()
        self.alert = 0

        # opening GDB
        try:
            driver = ogr.GetDriverByName(str("OpenFileGDB"))
            src = driver.Open(source_path, 0)
        except Exception as e:
            logging.error(e)
            youtils.erratum(dico_dataset, source_path, u'err_corrupt')
            self.alert = self.alert + 1
            return None

        # GDB name and parent folder
        try:
            dico_dataset['name'] = path.basename(src.GetName())
            dico_dataset['folder'] = path.dirname(src.GetName())
        except AttributeError as e:
            dico_dataset['name'] = path.basename(source_path)
            dico_dataset['folder'] = path.dirname(source_path)
        # layers count and names
        dico_dataset['layers_count'] = src.GetLayerCount()
        li_layers_names = []
        li_layers_idx = []
        dico_dataset['layers_names'] = li_layers_names
        dico_dataset['layers_idx'] = li_layers_idx

        # cumulated size
        dico_dataset[u"total_size"] = youtils.sizeof(source_path)

        # global dates
        crea, up = path.getctime(source_path), path.getmtime(source_path)
        dico_dataset[u'date_crea'] = strftime('%Y/%m/%d',
                                              localtime(crea))
        dico_dataset[u'date_actu'] = strftime('%Y/%m/%d',
                                              localtime(up))
        # total fields count
        total_fields = 0
        dico_dataset['total_fields'] = total_fields
        # total objects count
        total_objs = 0
        dico_dataset['total_objs'] = total_objs
        # parsing layers
        for layer_idx in range(src.GetLayerCount()):
            # dictionary where will be stored informations
            dico_layer = OrderedDict()
            # parent GDB
            dico_layer['src_name'] = path.basename(src.GetName())
            # getting layer object
            layer = src.GetLayerByIndex(layer_idx)
            # layer globals
            li_layers_names.append(layer.GetName())
            dico_layer[u'title'] = georeader.get_title(layer)
            li_layers_idx.append(layer_idx)

            # features
            layer_feat_count = layer.GetFeatureCount()
            dico_layer[u'num_obj'] = layer_feat_count
            if layer_feat_count == 0:
                """ if layer doesn't have any object, return an error """
                dico_layer[u'error'] = u'err_nobjet'
                self.alert = self.alert + 1
            else:
                pass

            # fields
            layer_def = layer.GetLayerDefn()
            dico_layer['num_fields'] = layer_def.GetFieldCount()
            dico_layer['fields'] = georeader.get_fields_details(layer_def)

            # geometry type
            dico_layer[u'type_geom'] = georeader.get_geometry_type(layer)

            # SRS
            srs_details = georeader.get_srs_details(layer, txt)
            dico_layer[u'srs'] = srs_details[0]
            dico_layer[u'EPSG'] = srs_details[1]
            dico_layer[u'srs_type'] = srs_details[2]

            # spatial extent
            extent = georeader.get_extent_as_tuple(layer)
            dico_layer[u'Xmin'] = extent[0]
            dico_layer[u'Xmax'] = extent[1]
            dico_layer[u'Ymin'] = extent[2]
            dico_layer[u'Ymax'] = extent[3]

            # storing layer into the GDB dictionary
            dico_dataset['{0}_{1}'
                         .format(layer_idx,
                                 dico_layer.get('title'))] = dico_layer
            # summing fields number
            total_fields += dico_layer.get('num_fields', 0)
            # summing objects number
            total_objs += dico_layer.get('num_obj', 0)
            # deleting dictionary to ensure having cleared space
            del dico_layer
        # storing fileds and objects sum
        dico_dataset['total_fields'] = total_fields
        dico_dataset['total_objs'] = total_objs

        # warnings messages
        if self.alert:
            dico_dataset['err_gdal'] = gdal_err.err_type, gdal_err.err_msg
        else:
            pass
        # clean exit
        del src

# ############################################################################
# #### Stand alone program #######
# ################################

if __name__ == '__main__':
    u""" standalone execution for tests. Paths are relative considering a test
    within the official repository (https://github.com/Guts/DicoGIS/)"""
    from os import chdir
    # sample files
    chdir(r'..\..\test\datatest\FileGDB\Esri_FileGDB')
    # test text dictionary
    textos = OrderedDict()
    textos['srs_comp'] = u'Compound'
    textos['srs_geoc'] = u'Geocentric'
    textos['srs_geog'] = u'Geographic'
    textos['srs_loca'] = u'Local'
    textos['srs_proj'] = u'Projected'
    textos['srs_vert'] = u'Vertical'
    textos['geom_point'] = u'Point'
    textos['geom_ligne'] = u'Line'
    textos['geom_polyg'] = u'Polygon'

    # searching for File GeoDataBase
    num_folders = 0
    li_gdb = [
              r'Points.gdb',
              r'Polygons.gdb',
              r'GDB_Test.gdb',
              r'MulitNet_2015_12.gdb',
              ]
    for root, dirs, files in walk(r'..\test\datatest'):
            num_folders = num_folders + len(dirs)
            for d in dirs:
                try:
                    unicode(path.join(root, d))
                    full_path = path.join(root, d)
                except UnicodeDecodeError as e:
                    full_path = path.join(root, d.decode('latin1'))
                    logging.error(unicode(full_path), e)
                if full_path[-4:].lower() == '.gdb':
                    # add complete path of shapefile
                    li_gdb.append(path.abspath(full_path))
                else:
                    pass

    # recipient datas
    dico_dataset = OrderedDict()

    # read GDB
    for source_path in li_gdb:
        dico_dataset.clear()
        source_path = path.abspath(source_path)
        print(path.isdir(source_path), source_path)
        if path.isdir(source_path):
            print("\n{0}: ".format(path.realpath(source_path)))
            ReadGDB(source_path,
                    dico_dataset,
                    'Esri FileGDB',
                    textos)
            # print results
            print(dico_dataset)
        else:
            print(path.isfile(source_path), source_path)
            pass
