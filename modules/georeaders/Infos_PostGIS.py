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
    from osgeo import ogr  # handler for vector spatial files
    from osgeo import osr
except ImportError:
    import gdal
    import ogr  # handler for vector spatial files
    import osr

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
# ######### Classes #############
# #################################


class ReadPostGIS():
    def __init__(self, host="localhost", port=5432, db_name="postgis",
                 user="postgres", password="postgres", views_included=1,
                 dico_dataset=OrderedDict()):
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
        self.alert = 0
        if views_included:
            gdal.SetConfigOption(str("PG_LIST_ALL_TABLES"), str("YES"))
        else:
            gdal.SetConfigOption(str("PG_LIST_ALL_TABLES"), str("NO"))

        # testing connection
        self.conn_settings = "PG: host={} port={} dbname={} user={} password={}"\
                             .format(host, port, db_name, user, password)
        self.conn = self.get_connection()
        if not self.conn:
            self.alert += 1
            youtils.erratum(dico_dataset, self.conn_settings, u'err_corrupt')
            dico_dataset['err_gdal'] = gdal_err.err_type, gdal_err.err_msg
            return None
        else:
            pass

        # store basic info
        dico_dataset["sgbd_host"] = host
        dico_dataset["sgbd_port"] = port
        dico_dataset["db_name"] = db_name
        dico_dataset["user"] = user
        dico_dataset["password"] = password
        dico_dataset["connection_string"] = self.conn_settings
        dico_dataset["sgbd_version"] = self.get_version()
        dico_dataset["sgbd_schemas"] = self.get_schemas()

        # print(self.conn.GetLayerCount())
        # test = self.get_version()
        # print(dir(test))

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

    def infos_dataset(self, layer, dico_dataset, tipo, txt=''):
        """TO DO."""
        dico_dataset['type'] = tipo
        # raising forbidden access
        try:
            obj = layer.GetNextFeature()  # get the first object
        except RuntimeError as e:
            if u'permission denied' in str(e):
                mess = str(e).split('\n')[0]
                self.alert = self.alert + 1
                self.erratum(dico_dataset, layer, mess)
                logging.error("GDAL: {} - {}".format(layer.GetName(), mess))
                return None
            else:
                pass
        except Exception as e:
            logging.error(e)

        try:
            self.geom = obj.GetGeometryRef()        # get the geometry
            if not self.geom:
                obj = layer.GetNextFeature()
                self.geom = obj.GetGeometryRef()
                logging.warning("GetGeometryRef failed on: {}".format(layer.GetName()))
            else:
                pass

            self.def_couche = layer.GetLayerDefn()  # get layer definitions
            self.srs = layer.GetSpatialRef()   # get spatial system reference
            self.srs.AutoIdentifyEPSG()  # try to determine the EPSG code
        except AttributeError:
            mess = "No geodata"
            self.alert = self.alert + 1
            self.erratum(dico_dataset, layer, mess)
            return None
        except UnboundLocalError:
            return None

        # basic information
        dico_dataset[u'type'] = tipo
        self.infos_basics(layer, dico_dataset, text)
        # geometry information
        self.infos_geom(layer, dico_dataset, text)
        # fields information
        self.infos_fields(dico_fields)

    def infos_basics(self, layer, dico_dataset, txt):
        u""" get the global informations about the layer """
        # Storing into the dictionary
        dico_dataset[u'name'] = layer.GetName()
        dico_dataset[u'title'] = layer.GetName().capitalize()
        dico_dataset[u'num_obj'] = layer.GetFeatureCount()
        dico_dataset[u'num_fields'] = self.def_couche.GetFieldCount()

        # schema name
        try:
            layer.GetName().split('.')[1]
            dico_dataset[u'folder'] = layer.GetName().split('.')[0]
        except IndexError:
            dico_dataset[u'folder'] = 'public'

        ## SRS
        # srs type
        srsmetod = [
                    (self.srs.IsCompound(), txt.get("srs_comp")),
                    (self.srs.IsGeocentric(), txt.get("srs_geoc")),
                    (self.srs.IsGeographic(), txt.get("srs_geog")),
                    (self.srs.IsLocal(), txt.get("srs_loca")),
                    (self.srs.IsProjected(), txt.get("srs_proj")),
                    (self.srs.IsVertical(), txt.get("srs_vert"))
                   ]
        # searching for a match with one of srs types
        for srsmet in srsmetod:
            if srsmet[0] == 1:
                typsrs = srsmet[1]
            else:
                continue
        # in case of not match
        try:
            dico_dataset[u'srs_type'] = unicode(typsrs)
        except UnboundLocalError:
            typsrs = txt.get('srs_nr')
            dico_dataset[u'srs_type'] = unicode(typsrs)


        # Handling exception in srs names'encoding
        try:
            if self.srs.GetAttrValue(str("PROJCS")) != str("unnamed"):
                dico_dataset[u'srs'] = unicode(self.srs.GetAttrValue(str("PROJCS"))).replace('_', ' ')
            else:
                dico_dataset[u'srs'] = unicode(self.srs.GetAttrValue(str("PROJECTION"))).replace('_', ' ')
        except UnicodeDecodeError:
            if self.srs.GetAttrValue(str("PROJCS")) != str("unnamed"):
                dico_dataset[u'srs'] = self.srs.GetAttrValue(str("PROJCS")).decode('latin1').replace('_', ' ')
            else:
                dico_dataset[u'srs'] = self.srs.GetAttrValue(str("PROJECTION")).decode('latin1').replace('_', ' ')
        dico_dataset[u'EPSG'] = unicode(self.srs.GetAttrValue(str("AUTHORITY"), 1))
        # EPSG code
        if dico_dataset[u'EPSG'] == u'4326' and dico_dataset[u'srs'] == u'None':
            dico_dataset[u'srs'] = u'WGS 84'
        else:
            pass

        # end of function
        return dico_dataset, layer, txt

    def infos_geom(self, layer, dico_dataset, txt):
        u"""Get the informations about geometry."""
        try:
            # geometry type
            if self.geom.GetGeometryName() == u'POINT':
                dico_dataset[u'type_geom'] = txt.get('geom_point')
            elif u'LINESTRING' in self.geom.GetGeometryName():
                dico_dataset[u'type_geom'] = txt.get('geom_ligne')
            elif u'POLYGON' in self.geom.GetGeometryName():
                dico_dataset[u'type_geom'] = txt.get('geom_polyg')
            else:
                dico_dataset[u'type_geom'] = self.geom.GetGeometryName()
        except AttributeError, e:
            mess = str(e).split('\n')[0]
            # self.alert = self.alert + 1
            # self.erratum(dico_dataset, layer, mess)
            logging.warning("GDAL: {} - {}".format(layer.GetName(), mess))
            dico_dataset[u'type_geom'] = "ERROR: not recognized"

        # Spatial extent (bounding box)
        dico_dataset[u'Xmin'] = round(layer.GetExtent()[0], 2)
        dico_dataset[u'Xmax'] = round(layer.GetExtent()[1], 2)
        dico_dataset[u'Ymin'] = round(layer.GetExtent()[2], 2)
        dico_dataset[u'Ymax'] = round(layer.GetExtent()[3], 2)
        # end of function
        return dico_dataset

    def infos_fields(self, dico_fields):
        u""" get the informations about fields definitions """
        for i in range(self.def_couche.GetFieldCount()):
            champomy = self.def_couche.GetFieldDefn(i)  # ordered list of fields
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

# ############################################################################
# #### Stand alone program ########
# #################################

if __name__ == '__main__':
    u""" standalone execution for tests. Paths are relative considering a test
    within the official repository (https://github.com/Guts/DicoGIS/)"""
    # libraries import
    from sys import exit
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
    dico_dataset = OrderedDict()     # dictionary where will be stored informations
    dico_fields = OrderedDict()     # dictionary for fields information
    # PostGIS database settings
    test_host = 'postgresql-guts.alwaysdata.net'
    test_db = 'guts_gis'
    test_user = 'guts_player'
    test_pwd = 'letsplay'
    test_conn = "PG: host={} dbname={} user={} password={}".format(test_host,
                                                                   test_db,
                                                                   test_user,
                                                                   test_pwd)

    # # include views
    # gdal.SetConfigOption(str("PG_LIST_ALL_TABLES"), str("YES"))
    # try:
    #     conn = ogr.Open(str(test_conn))
    #     print("Access granted : connecting people!")
    #     print("Layer count: {0}".format(conn.GetLayerCount()))

    #     sql_version = str("SELECT PostGIS_full_version();")
    #     version = conn.ExecuteSQL(sql_version)

    #     # schemas list
    #     sql_schemas = str("select nspname from pg_catalog.pg_namespace;")
    #     schemas = conn.ExecuteSQL(sql_schemas)
    #     print("Driver name: {0}".format(conn.GetDriver().GetName()))
    # except Exception as e:
    #     print('Connection failed. Check settings: {0}'.format(str(e)))
    #     exit()

    # # parsing layers
    # for layer in conn:
    #     dico_dataset.clear()
    #     print("\n")
    #     print(layer.GetName())
    #     # if "_current"
    #     ReadPostGIS(layer, dico_dataset, 'pg', textos)
    #     print(dico_dataset)

    pgReader = ReadPostGIS(host=test_host, port=5432, db_name=test_db,
                           user=test_user, password=test_pwd,
                           views_included=1, dico_dataset=dico_dataset)
    # print(dico_dataset)

    version = dico_dataset.get("sgbd_version")
    print(dir(version))
    print(version.__str__)
