# -*- coding: UTF-8 -*-
#!/usr/bin/env python
from __future__ import absolute_import, print_function, unicode_literals

# -----------------------------------------------------------------------------
# Name:         InfosSHP
# Purpose:      Use GDAL/OGR library to extract informations about
#                   geographic data. It permits a more friendly use as
#                   submodule.
#
# Author:       Julien Moura (https://github.com/Guts/)
#
# Python:       2.7.x
# Created:      11/04/2015
# Updated:      11/04/2015
# Licence:      GPL 3
# -----------------------------------------------------------------------------

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
    from osgeo import ogr  # handler for vector spatial files
    from osgeo import osr
except ImportError:
    import gdal
    import ogr  # handler for vector spatial files
    import osr

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
# ###############################


class ReadGXT:
    def __init__(self, layerpath, dico_layer, tipo, txt=""):
        """ Uses OGR functions to extract basic informations about
        geographic vector file (handles shapefile or MapInfo tables)
        and store into dictionaries.

        layerpath = path to the geographic file
        dico_layer = dictionary for global informations
        dico_fields = dictionary for the fields' informations
        li_fieds = ordered list of fields
        tipo = format
        text = dictionary of text in the selected language

        """
        # handling ogr specific exceptions
        errhandler = gdal_err.handler
        gdal.PushErrorHandler(errhandler)
        # gdal.UseExceptions()
        ogr.UseExceptions()
        self.alert = 0

        # changing working directory to layer folder
        chdir(path.dirname(layerpath))

        # raising corrupt files
        try:
            source = ogr.Open(layerpath)  # OGR driver
        except Exception as e:
            logging.error(e)
            self.alert = self.alert + 1
            youtils.erratum(dico_layer, layerpath, "err_corrupt")
            dico_layer["err_gdal"] = gdal_err.err_type, gdal_err.err_msg
            return None

        # raising incompatible files
        if not source:
            """ if file is not compatible """
            self.alert += 1
            dico_layer["err_gdal"] = gdal_err.err_type, gdal_err.err_msg
            youtils.erratum(dico_layer, layerpath, "err_nobjet")
            return None
        else:
            layer = source.GetLayer()  # get the layer
            pass

        # dataset name, title and parent folder
        try:
            dico_layer["name"] = path.basename(layerpath)
            dico_layer["folder"] = path.dirname(layerpath)
        except AttributeError as e:
            dico_layer["name"] = path.basename(layer.GetName())
            dico_layer["folder"] = path.dirname(layer.GetName())
        dico_layer["title"] = dico_layer.get("name")[:-4].replace("_", " ").capitalize()

        # dependencies and total size
        dependencies = youtils.list_dependencies(layerpath, "auto")
        dico_layer["dependencies"] = dependencies
        dico_layer["total_size"] = youtils.sizeof(layerpath, dependencies)
        # Getting basic dates
        crea, up = path.getctime(source_path), path.getmtime(source_path)
        dico_dataset["date_crea"] = strftime("%Y/%m/%d", localtime(crea))
        dico_dataset["date_actu"] = strftime("%Y/%m/%d", localtime(up))

        # features
        layer_feat_count = layer.GetFeatureCount()
        dico_layer["num_obj"] = layer_feat_count
        if layer_feat_count == 0:
            """ if layer doesn't have any object, return an error """
            self.alert += 1
            youtils.erratum(dico_layer, layerpath, "err_nobjet")
            return None
        else:
            pass

        # fields
        layer_def = layer.GetLayerDefn()
        dico_layer["num_fields"] = layer_def.GetFieldCount()
        dico_layer["fields"] = georeader.get_fields_details(layer_def)

        # geometry type
        dico_layer["type_geom"] = georeader.get_geometry_type(layer)

        # SRS
        srs_details = georeader.get_srs_details(layer, txt)
        dico_layer["srs"] = srs_details[0]
        dico_layer["EPSG"] = srs_details[1]
        dico_layer["srs_type"] = srs_details[2]

        # spatial extent
        extent = georeader.get_extent_as_tuple(layer)
        dico_layer["Xmin"] = extent[0]
        dico_layer["Xmax"] = extent[1]
        dico_layer["Ymin"] = extent[2]
        dico_layer["Ymax"] = extent[3]

        # warnings messages
        if self.alert:
            dico_layer["err_gdal"] = gdal_err.err_type, gdal_err.err_msg
        else:
            pass

        # safe exit
        del source


# ############################################################################
# #### Stand alone program ########
# #################################

if __name__ == "__main__":
    """ standalone execution for tests. Paths are relative considering a test
    within the official repository (https://github.com/Guts/DicoGIS/)"""
    from os import chdir, walk

    # sample files
    chdir(r"..\..\test")
    li_gxt = []
    # test text dictionary
    textos = OrderedDict()
    textos["srs_comp"] = "Compound"
    textos["srs_geoc"] = "Geocentric"
    textos["srs_geog"] = "Geographic"
    textos["srs_loca"] = "Local"
    textos["srs_proj"] = "Projected"
    textos["srs_vert"] = "Vertical"
    textos["geom_point"] = "Point"
    textos["geom_ligne"] = "Line"
    textos["geom_polyg"] = "Polygon"

    # searching for GXT files
    for root, dirs, files in walk(r"datatest"):
        for f in files:
            try:
                unicode(path.join(root, f))
                full_path = path.join(root, f)
            except UnicodeDecodeError as e:
                full_path = path.join(root, f.decode("latin1"))
                # print(unicode(full_path), e)
            if full_path[-4:].lower() == ".gxt":
                # add complete path of shapefile
                li_gxt.append(path.abspath(full_path))
            else:
                pass

    # recipient datas
    dico_gxt = OrderedDict()
    dico_fields = OrderedDict()  # dictionary for fields information
    # read GXT
    for gxtpath in li_gxt:
        dico_gxt.clear()
        dico_fields.clear()
        if path.isfile(gxtpath):
            print("\n{0}: ".format(gxtpath))
            ReadGXT(gxtpath, dico_gxt, "Geoconcept eXport Text", textos)
            # print results
            print(dico_gxt)
        else:
            pass
