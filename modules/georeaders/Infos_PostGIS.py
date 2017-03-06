#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import (absolute_import, print_function, unicode_literals)
# ----------------------------------------------------------------------------
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
# ----------------------------------------------------------------------------

# ############################################################################
# ######### Libraries #############
# #################################
# Python 2 and 3 compatibility
from future.standard_library import install_aliases
install_aliases()

# Standard library
from collections import OrderedDict  # Python 3 backported
import logging

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
youtils = Utils(ds_type="postgis")

# ############################################################################
# ######### Classes #############
# #################################


class ReadPostGIS():
    def __init__(self, host="localhost", port=5432, db_name="postgis",
                 user="postgres", password="postgres", views_included=1,
                 dico_dataset=OrderedDict(), txt=dict()):
        u"""Uses gdal/ogr functions to extract basic informations about
        geographic file (handles shapefile or MapInfo tables)
        and store into the dictionaries.

        layer = path to the geographic file
        dico_dataset = dictionary for global informations
        dico_fields = dictionary for the fields' informations
        tipo = feature type to read
        text = dictionary of texts to display
        """
        # handling GDAL/OGR specific exceptions
        gdal.AllRegister()
        ogr.UseExceptions()
        gdal.UseExceptions()

        # Creating variables
        self.dico_dataset = dico_dataset
        self.txt = txt
        self.alert = 0
        if views_included:
            gdal.SetConfigOption(str("PG_LIST_ALL_TABLES"), str("YES"))
        else:
            gdal.SetConfigOption(str("PG_LIST_ALL_TABLES"), str("NO"))

        # connection infos
        self.conn_settings = "PG: host={} port={} dbname={} user={} password={}"\
                             .format(host, port, db_name, user, password)
        dico_dataset["sgbd_host"] = host
        dico_dataset["sgbd_port"] = port
        dico_dataset["db_name"] = db_name
        dico_dataset["user"] = user
        dico_dataset["password"] = password
        dico_dataset["connection_string"] = self.conn_settings

        # testing connection
        self.conn = self.get_connection()
        if not self.conn:
            self.alert += 1
            youtils.erratum(ctner=dico_dataset, mess_type=1,
                            ds_lyr=self.conn_settings, mess=u'err_connection_failed')
            dico_dataset['err_gdal'] = gdal_err.err_type, gdal_err.err_msg
            return None
        else:
            pass

        # sgbd info
        dico_dataset["sgbd_version"] = self.get_version()
        dico_dataset["sgbd_schemas"] = self.get_schemas()

    def get_connection(self):
        """TO DOC."""
        try:
            conn = ogr.Open(str(self.conn_settings))
            logging.info("Access granted : connecting people!")
            return conn
        except Exception as e:
            logging.error("Connection failed. Check settings: {0}".format(str(e)))
            return 0

    def get_version(self):
        """TO DO."""
        sql_version = str("SELECT PostGIS_full_version();")
        return self.conn.ExecuteSQL(sql_version)

    def get_schemas(self):
        """TO DO."""
        sql_schemas = str("select nspname from pg_catalog.pg_namespace;")
        return self.conn.ExecuteSQL(sql_schemas)

    def infos_dataset(self, layer, dico_dataset=dict(), tipo="PostGIS"):
        """TO DO."""
        if not dico_dataset:
            dico_dataset = self.dico_dataset
        else:
            pass
        # check layer type
        if type(layer) is not ogr.Layer:
            self.alert = self.alert + 1
            youtils.erratum(dico_dataset, layer, "Not a PostGIS layer")
            logging.error("OGR: {} - {}".format(layer, "Not a PostGIS layer."))
            return None
        else:
            dico_dataset['type'] = tipo
            pass

        # raising forbidden access
        try:
            obj = layer.GetFeatureCount()  # get the first object
        except RuntimeError as e:
            if u'permission denied' in str(e):
                mess = str(e).split('\n')[0]
                self.alert = self.alert + 1
                youtils.erratum(ctner=dico_dataset, ds_lyr=layer, mess=mess)
                logging.error("GDAL: {} - {}".format(layer.GetName(), mess))
                return None
            else:
                pass
        except Exception as e:
            logging.error(e)
            return None

        dico_dataset['name'] = layer.GetName()
        dico_dataset['title'] = layer.GetName().capitalize()
        # schema name
        try:
            layer.GetName().split('.')[1]
            dico_dataset[u'folder'] = layer.GetName().split('.')[0]
        except IndexError:
            dico_dataset[u'folder'] = 'public'

        # basic information
        # features
        layer_feat_count = layer.GetFeatureCount()
        dico_dataset['num_obj'] = layer_feat_count
        if layer_feat_count == 0:
            u""" if layer doesn't have any object, return an error """
            self.alert += 1
            youtils.erratum(ctner=dico_dataset, ds_lyr=layer,
                            mess='err_nobjet')
            return None
        else:
            pass

        # fields
        layer_def = layer.GetLayerDefn()
        dico_dataset['num_fields'] = layer_def.GetFieldCount()
        dico_dataset['fields'] = georeader.get_fields_details(layer_def)

        # geometry type
        dico_dataset[u'type_geom'] = georeader.get_geometry_type(layer)

        # SRS
        srs_details = georeader.get_srs_details(layer, self.txt)
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

        # clean exit
        del obj

# ############################################################################
# #### Stand alone program ########
# #################################

if __name__ == '__main__':
    u""" standalone execution for tests. Paths are relative considering a test
    within the official repository (https://github.com/Guts/DicoGIS/)"""
    # libraries import

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

    # PostGIS database settings
    test_host = 'postgresql-guts.alwaysdata.net'
    test_db = 'guts_gis'
    test_user = 'guts_player'
    test_pwd = 'letsplay'
    test_conn = "PG: host={} dbname={} user={} password={}".format(test_host,
                                                                   test_db,
                                                                   test_user,
                                                                   test_pwd)
    # use reader
    dico_dataset = OrderedDict()
    pgReader = ReadPostGIS(host=test_host, port=5432, db_name=test_db,
                           user=test_user, password=test_pwd,
                           views_included=1, dico_dataset=dico_dataset,
                           txt=textos)
    for layer in pgReader.conn:
        dico_dataset.clear()
        print(layer.GetName())
        pgReader.infos_dataset(layer)
        print(dico_dataset)
