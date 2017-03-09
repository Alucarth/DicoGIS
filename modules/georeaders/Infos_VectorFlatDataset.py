# -*- coding: UTF-8 -*-
#!/usr/bin/env python
from __future__ import (absolute_import, print_function, unicode_literals)
# ----------------------------------------------------------------------------
# Name:         InfosSHP
# Purpose:      Use GDAL/OGR library to extract informations about
#                   geographic data. It permits a more friendly use as
#                   submodule.
#
# Author:       Julien Moura (https://github.com/Guts/)
#
# Python:       2.7.x
# Created:      18/02/2013
# Updated:      28/09/2014
# Licence:      GPL 3
# -----------------------------------------------------------------------------

# ############################################################################
# ######### Libraries #############
# #################################
# Python 2 and 3 compatibility
from future.standard_library import install_aliases
install_aliases()

# Standard library
from collections import OrderedDict  # Python 3 backported
import logging
from os import chdir, listdir, path       # files and folder managing
from time import localtime, strftime

# 3rd party libraries
try:
    from osgeo import gdal
    from osgeo import ogr
except ImportError:
    import gdal
    import ogr

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
youtils = Utils("flat")
logger = logging.getLogger("DicoGIS")

# ############################################################################
# ######### Classes #############
# ###############################


class ReadVectorFlatDataset():
    def __init__(self):
        """Class constructor."""
        # handling ogr specific exceptions
        errhandler = gdal_err.handler
        gdal.PushErrorHandler(errhandler)
        gdal.UseExceptions()
        ogr.UseExceptions()
        self.alert = 0

    def infos_dataset(self, source_path, dico_dataset, txt=dict(), tipo=None):
        """Use OGR functions to extract basic informations about
        geographic vector file (handles shapefile or MapInfo tables)
        and store into dictionaries.

        source_path = path to the geographic file
        dico_dataset = dictionary for global informations
        tipo = format
        txt = dictionary of text in the selected language
        """
        # changing working directory to layer folder
        chdir(path.dirname(source_path))

        # raising corrupt files
        try:
            src = gdal.OpenEx(source_path, 0)  # GDAL driver
            if not tipo:
                dico_dataset["type"] = src.GetDriver().LongName
            else:
                dico_dataset["type"] = tipo
                pass
        except Exception as e:
            logger.error(e)
            self.alert = self.alert + 1
            dico_dataset["type"] = tipo
            youtils.erratum(dico_dataset, source_path, u'err_corrupt')
            dico_dataset["err_gdal"] = gdal_err.err_type, gdal_err.err_msg
            return 0

        # raising incompatible files
        if not src:
            u""" if file is not compatible """
            self.alert += 1
            dico_dataset['err_gdal'] = gdal_err.err_type, gdal_err.err_msg
            youtils.erratum(dico_dataset, source_path, u'err_nobjet')
            return 0
        else:
            layer = src.GetLayer()   # get the layer
            pass

        # dataset name, title and parent folder
        try:
            dico_dataset['name'] = path.basename(source_path)
            dico_dataset['folder'] = path.dirname(source_path)
        except AttributeError as e:
            dico_dataset['name'] = path.basename(layer.GetName())
            dico_dataset['folder'] = path.dirname(layer.GetName())
        dico_dataset['title'] = dico_dataset.get('name')[:-4]\
                                            .replace('_', ' ')\
                                            .capitalize()

        # dependencies and total size
        dependencies = youtils.list_dependencies(source_path, "auto")
        dico_dataset[u'dependencies'] = dependencies
        dico_dataset[u"total_size"] = youtils.sizeof(source_path,
                                                     dependencies)
        # Getting basic dates
        crea, up = path.getctime(source_path), path.getmtime(source_path)
        dico_dataset[u'date_crea'] = strftime('%Y/%m/%d',
                                              localtime(crea))
        dico_dataset[u'date_actu'] = strftime('%Y/%m/%d',
                                              localtime(up))

        # features
        layer_feat_count = layer.GetFeatureCount()
        dico_dataset['num_obj'] = layer_feat_count
        if layer_feat_count == 0:
            u""" if layer doesn't have any object, return an error """
            self.alert += 1
            youtils.erratum(dico_dataset, source_path, u'err_nobjet')
            return 0
        else:
            pass

        # fields
        layer_def = layer.GetLayerDefn()
        dico_dataset['num_fields'] = layer_def.GetFieldCount()
        dico_dataset['fields'] = georeader.get_fields_details(layer_def)

        # geometry type
        dico_dataset[u'type_geom'] = georeader.get_geometry_type(layer)

        # SRS
        srs_details = georeader.get_srs_details(layer, txt)
        dico_dataset[u'srs'] = srs_details[0]
        dico_dataset[u'EPSG'] = srs_details[1]
        dico_dataset[u'srs_type'] = srs_details[2]

        # spatial extent
        extent = georeader.get_extent_as_tuple(layer)
        dico_dataset[u'Xmin'] = extent[0]
        dico_dataset[u'Xmax'] = extent[1]
        dico_dataset[u'Ymin'] = extent[2]
        dico_dataset[u'Ymax'] = extent[3]

        # warnings messages
        if self.alert:
            dico_dataset['err_gdal'] = gdal_err.err_type, gdal_err.err_msg
        else:
            pass

        # clean & exit
        del src
        return 1, dico_dataset

# ############################################################################
# #### Stand alone program ########
# ################################

if __name__ == '__main__':
    u""" standalone execution for tests. Paths are relative considering a test
    within the official repository (https://github.com/Guts/DicoGIS)"""
    # libraries import
    # from os import getcwd
    vectorReader = ReadVectorFlatDataset()
    # test files
    li_vectors = [path.realpath(r'..\..\test\datatest\vectors\shp\itineraires_rando.shp'),
                  path.realpath(r'..\..\test\datatest\vectors\shp\airports.shp'),
                  path.realpath(r'..\..\test\datatest\vectors\tab\tab\airports_MI.tab'),
                  path.realpath(r'..\..\test\datatest\vectors\tab\tab\Hydrobiologie.TAB'),
                  path.realpath(r'..\..\test\datatest\vectors\geojson\airports.geojson'),
                  path.realpath(r'..\..\test\datatest\vectors\gml\airports.gml'),
                  path.realpath(r'..\..\test\datatest\vectors\kml\wc2014_MapTour.kml'),
                  path.realpath(r'..\..\test\datatest\vectors\kml\PPRI_Loire_sept2014.kmz'),
                  ]
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
    # recipient datas
    dico_dataset = OrderedDict()  # dictionary where will be stored info
    # execution
    for vector in li_vectors:
        """ looping on shapefiles list """
        # reset recipient data
        dico_dataset.clear()
        # getting the informations
        print('\n{0}'.format(vector))
        info_ds = vectorReader.infos_dataset(path.abspath(vector),
                                             dico_dataset,
                                             txt=textos)
        print(info_ds)
