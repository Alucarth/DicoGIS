# -*- coding: UTF-8 -*-
#!/usr/bin/env python
from __future__ import (absolute_import, print_function, unicode_literals)

# ----------------------------------------------------------------------------
# Name:         Infos DXF
# Purpose:      Use GDAL/OGR and dxfgrabber to read AutoCAD exchanges file format.
#
# Author:       Julien Moura (https://github.com/Guts/)
#
# Python:       2.7.x
# Created:      24/07/2014
# Updated:      13/08/2014
# Licence:      GPL 3
# ----------------------------------------------------------------------------

# ############################################################################
# ######### Libraries #############
# #################################
# Standard library
from collections import OrderedDict  # Python 3 backported
import logging
from os import chdir, listdir, path  # files and folder managing
from time import localtime, strftime

# 3rd party libraries
try:
    from osgeo import gdal
    from osgeo import ogr
    from osgeo import osr
except ImportError:
    import gdal
    import ogr
    import osr

import dxfgrabber   # module dedicated to DXF

# custom submodules
try:
    from .gdal_exceptions_handler import GdalErrorHandler
    from .geo_infos_generic import GeoInfosGenericReader
    from .utils import Utils
except ValueError:
    from gdal_exceptions_handler import GdalErrorHandler
    from geo_infos_generic import GeoInfosGenericReader
    from utils import Utils

# ############################################################################
# ######### Globals ############
# ##############################

gdal_err = GdalErrorHandler()
georeader = GeoInfosGenericReader()
youtils = Utils()

# ##############################################################################
# ########## Classes #############
# ################################


class ReadDXF():
    def __init__(self, source_path, dico_dataset, tipo, txt=''):
        u""" Uses OGR functions to extract basic informations about
        geographic vector file (handles shapefile or MapInfo tables)
        and store into dictionaries.

        source_path = path to the DXF file
        dico_dataset = dictionary for global informations
        tipo = format
        text = dictionary of text in the selected language
        """
        # handling ogr specific exceptions
        errhandler = gdal_err.handler
        gdal.PushErrorHandler(errhandler)
        gdal.UseExceptions()
        self.alert = 0

        # changing working directory to layer folder
        chdir(path.dirname(source_path))

        # opening DXF
        try:
            # driver_dxf = ogr.GetDriverByName(str("DXF"))
            # dxf = driver_dxf.Open(source_path, 0)
            src = gdal.OpenEx(source_path, 0)
        except Exception as e:
            logging.error(e)
            youtils.erratum(dico_dataset, source_path, u'err_corrupt')
            self.alert = self.alert + 1
            return None

        # raising incompatible files
        if not src:
            u""" if file is not compatible """
            self.alert += 1
            dico_dataset['err_gdal'] = gdal_err.err_type, gdal_err.err_msg
            youtils.erratum(dico_dataset, source_path, u'err_nobjet')
            return None
        else:
            layer = src.GetLayer()   # get the layer
            pass

        # DXF name and parent folder
        try:
            dico_dataset['name'] = path.basename(src.GetName())
            dico_dataset['folder'] = path.dirname(src.GetName())
        except AttributeError as e:
            dico_dataset['name'] = path.basename(source_path)
            dico_dataset['folder'] = path.dirname(source_path)

        # specific AutoDesk informations
        douxef = dxfgrabber.readfile(source_path)
        dico_dataset['version_code'] = douxef.dxfversion
        # see: http://dxfgrabber.readthedocs.org/en/latest/#Drawing.dxfversion
        if douxef.dxfversion == 'AC1009':
            dico_dataset['version_name'] = 'AutoCAD R12'
        elif douxef.dxfversion == 'AC1015':
            dico_dataset['version_name'] = 'AutoCAD R2000'
        elif douxef.dxfversion == 'AC1018':
            dico_dataset['version_name'] = 'AutoCAD R2004'
        elif douxef.dxfversion == 'AC1021':
            dico_dataset['version_name'] = 'AutoCAD R2007'
        elif douxef.dxfversion == 'AC1024':
            dico_dataset['version_name'] = 'AutoCAD R2010'
        elif douxef.dxfversion == 'AC1027':
            dico_dataset['version_name'] = 'AutoCAD R2013'
        else:
            dico_dataset['version_name'] = 'douxef.dxfversion'

        # layers count and names
        dico_dataset['layers_count'] = src.GetLayerCount()
        li_layers_names = []
        li_layers_idx = []
        dico_dataset['layers_names'] = li_layers_names
        dico_dataset['layers_idx'] = li_layers_idx

        # dependencies and total size
        dependencies = youtils.list_dependencies(source_path, "auto")
        dico_dataset[u'dependencies'] = dependencies
        dico_dataset[u"total_size"] = youtils.sizeof(source_path,
                                                     dependencies)
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
            dico_layer['src_name'] = dico_dataset.get('name')
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
# ##### Stand alone program ######
# ################################

if __name__ == '__main__':
    u""" standalone execution for tests. Paths are relative considering a test
    within the official repository (https://github.com/Guts/DicoGIS/)"""
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

    # searching for DX Files
    num_folders = 0
    li_dxf = [r'..\..\test\datatest\cao\dxf\paris_transports_ed.dxf']

    # recipient datas
    dico_dataset = OrderedDict()

    # read DXF
    for source_path in li_dxf:
        dico_dataset.clear()
        source_path = path.abspath(source_path)
        if path.isfile(source_path):
            print("\n{0}: ".format(source_path))
            ReadDXF(source_path,
                    dico_dataset,
                    'AutoCAD DXF',
                    textos)
            # print results
            print(dico_dataset)
        else:
            pass
