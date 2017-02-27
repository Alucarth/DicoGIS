# -*- coding: UTF-8 -*-
#!/usr/bin/env python
from __future__ import unicode_literals
from __future__ import print_function

# -----------------------------------------------------------------------------
# Name:         Infos MXD
# Purpose:      Get some metadata abour MXD files (Esri symbology layer))
#
# Author:       Julien Moura (https://github.com/Guts/)
#
# Python:       2.7.x
# Created:      28/09/2015
# Updated:      12/12/2015
# Licence:      GPL 3
# -----------------------------------------------------------------------------

# #############################################################################
# ########## Libraries #############
# ##################################
# Standard library
from collections import OrderedDict  # Python 3 backported
import logging
from os import chdir, listdir, path  # files and folder managing
from time import localtime, strftime

# 3rd party libraries
try:
    from arcpy import env as enviro
    from arcpy.mapping import ListDataFrames, ListLayers, MapDocument
except ImportError:
    logging.error("ArcPy is not installed.")
except RuntimeError:
    logging.error("ArcPy is installed, but not licensed.")

# #############################################################################
# ########## Classes #############
# ################################

class ReadMXD():
    def __init__(self, mxd_path, dico_mxd, tipo, txt=''):
        u""" Uses arcpy functions to extract basic informations about
        Esri map documents and store into dictionaries.

        mxdpath = path to the MXD file
        dico_mxd = dictionary for global informations
        tipo = format
        text = dictionary of text in the selected language

        see: http://help.arcgis.com/fr/arcgisdesktop/10.0/help/index.html#/na/00s30000000n000000/
        """
        # changing working directory to layer folder
        chdir(path.dirname(mxd_path))

        # raising arcpy specific exceptions
        self.alert = 0

        # opening MXD
        mxd = MapDocument(mxd_path)

        # basics
        dico_mxd['title'] = mxd.title
        dico_mxd['description'] = mxd.description
        dico_mxd['creator_prod'] = mxd.author
        dico_mxd['folder'] = mxd.filePath
        dico_mxd['credits'] = mxd.credits
        dico_mxd['keywords'] = mxd.tags
        dico_mxd['subject'] = mxd.summary
        dico_mxd['relpath'] = mxd.relativePaths
        dico_mxd['url'] = mxd.hyperlinkBase
        dico_mxd['date_export'] = mxd.dateExported
        dico_mxd['date_print'] = mxd.datePrinted
        dico_mxd['date_actu'] = mxd.dateSaved
        dico_mxd['active_df'] = mxd.activeDataFrame.name
        dico_mxd['active_view'] = mxd.activeView
        # dico_mxd['active_ddp'] = mxd.dataDrivenPages

        # by default let's start considering there is only one layer
        dframes = ListDataFrames(mxd)
        dico_mxd['subdatasets_count'] = len(dframes)

        li_dframes_names = []
        dico_mxd['dframes_names'] = li_dframes_names

        x = 0
        for dframe in dframes:
            x += 1
            # dictionary where will be stored informations
            dico_dframe = OrderedDict()
            # parent GDB
            dico_dframe[u'name'] = dframe.name

            # getting layer globlal informations
            self.infos_dataframe(dframe, dico_dframe)

            # storing layer into the GDB dictionary
            dico_mxd['{0}_{1}'.format(x,
                                      dico_dframe.get('name'))] = dico_dframe

            # reset
            del dico_dframe

        # dico_mxd[u'layers_count'] = total_layers

        # scale
        # dico_mxd['maxScale'] = layer_obj.maxScale
        # dico_mxd['minScale'] = layer_obj.minScale

        # # secondary
        # dico_mxd['license'] = layer_obj.credits
        # dico_mxd['broken'] = layer_obj.isBroken

        size = path.getsize(mxd_path)
        dico_mxd[u"total_size"] = self.sizeof(size)

        # global dates
        dico_mxd[u'date_crea'] = strftime('%d/%m/%Y',
                                          localtime(path.getctime(mxd_path)))

        # # total fields count
        # total_fields = 0
        # dico_mxd['total_fields'] = total_fields

        # # total objects count
        # total_objs = 0
        # dico_mxd['total_objs'] = total_objs

        # # parsing layers
        return

    def infos_dataframe(self, dataframe, dico_dframe):
        u"""
        Gets informations about geography and geometry
        """
        # spatial extent
        extent = dataframe.extent
        dico_dframe[u'Xmin'] = round(extent.XMin, 2)
        dico_dframe[u'Xmax'] = round(extent.XMax, 2)
        dico_dframe[u'Ymin'] = round(extent.YMin, 2)
        dico_dframe[u'Ymax'] = round(extent.YMax, 2)

        # map settings
        dico_dframe[u'mapUnits'] = dataframe.mapUnits

        # SRS
        srs = extent.spatialReference
        dico_dframe[u'srs'] = srs.name
        dico_dframe[u'srs_type'] = srs.type
        if srs.type == u'Projected':
            dico_dframe[u'EPSG'] = srs.PCSCode, srs.PCSName, srs.projectionCode, srs.projectionName
        elif srs.type == u'Geographic':
            dico_dframe[u'EPSG'] = srs.GCSCode, srs.GCSName, srs.datumCode, srs.datumName
        else:
            dico_dframe[u'EPSG'] = (srs.PCSCode, srs.PCSName, srs.projectionCode, srs.projectionName),\
                                   (srs.GCSCode, srs.GCSName, srs.datumCode, srs.datumName)

        # layers
        li_layers = ListLayers(dataframe)
        dico_dframe['layers_count'] = len(li_layers)
        dico_dframe['layers_names'] = [layer.name for layer in li_layers]

        # end of function
        return

    def sizeof(self, os_size):
        u"""
        Returns size in different units depending on size
        see http://stackoverflow.com/a/1094933
        """
        for size_cat in ['octets', 'Ko', 'Mo', 'Go']:
            if os_size < 1024.0:
                return "%3.1f %s" % (os_size, size_cat)
            os_size /= 1024.0
        # end of function
        return "%3.1f %s" % (os_size, " To")


    def erratum(self, dico_mxd, mxd_path, mess):
        u""" errors handler """
        # storing minimal informations to give clues to solve later
        dico_mxd[u'name'] = path.basename(mxdpath)
        dico_mxd[u'folder'] = path.dirname(mxdpath)
        dico_mxd[u'error'] = mess
        # End of function
        return dico_mxd

# ##############################################################################
# ##### Stand alone program ########
# ##################################

if __name__ == '__main__' and __package__ is None:
    u"""
    Standalone execution for development and tests. Paths are relative considering
    a test within the official repository (https://github.com/Guts/DicoGIS/)
    """
    # ------------ Specific imports ----------------
    # standard
    from os import sys
    sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

    # custom
    from utils.checknorris import CheckNorris

    # ------------ checking arcpy installation ----------------
    # Invoke Check Norris
    checker = CheckNorris()

    if not checker.check_arcpy()[0]:
        from sys import exit
        exit('ArcPy not found. Check your installation.')
    else:
        print(("ArcPy: ", checker.check_arcpy()))
        pass

    # ------------ Real start ----------------
    # searching for mxd Files
    dir_mxd = path.abspath(r'..\..\test\datatest\maps_docs\mxd')
    # dir_mxd = path.abspath(r'\\Copernic\SIG_RESSOURCES\1_mxd\ADMINISTRATIF')
    chdir(path.abspath(dir_mxd))
    li_mxd = listdir(path.abspath(dir_mxd))
    li_mxd = [path.abspath(mxd) for mxd in li_mxd if path.splitext(mxd)[1].lower()=='.mxd']

    # recipient datas
    dico_mxd = OrderedDict()

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

    # read MXD
    for mxdpath in li_mxd:
        dico_mxd.clear()
        if path.isfile(mxdpath):
            print("\n{0}: ".format(mxdpath))
            ReadMXD(mxdpath,
                    dico_mxd,
                    'Esri MXD',
                    txt=textos)
            # print results
            print(dico_mxd)
        else:
            print("{0} is not a recognized file".format(mxdpath))
            continue
