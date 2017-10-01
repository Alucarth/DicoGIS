# -*- coding: UTF-8 -*-
#!/usr/bin/env python
from __future__ import (absolute_import, print_function, unicode_literals)

# ----------------------------------------------------------------------------
# Name:         Infos qgs
# Purpose:      Get some metadata abour qgs files (Esri symbology layer))
#
# Author:       Julien Moura (https://github.com/Guts/)
#
# Python:       2.7.x
# Created:      28/09/2015
# Updated:      12/12/2015
# Licence:      GPL 3
# ----------------------------------------------------------------------------

# ############################################################################
########### Libraries #############
###################################
# Standard library
from collections import OrderedDict  # Python 3 backported
from os import path, chdir, listdir   # files and folder managing
from time import localtime, strftime
from xml.etree import ElementTree

# ############################################################################
# ######### Classes #############
# ###############################

class ReadQGS():
    def __init__(self, qgs_path, dico_qgs, tipo, txt=''):
        u""" Uses ElementTree to parse QGS files which are XML based files

        qgspath = path to the qgs file
        dico_qgs = dictionary for global informations
        tipo = format
        text = dictionary of text in the selected language
        """
        # changing working directory to layer folder
        chdir(path.dirname(qgs_path))

        # raising arcpy specific exceptions
        self.alert = 0

        # opening qgs
        qgs = ElementTree.parse(qgs_path).getroot()
        # print(qgs.getroot().attrib["version"])
        # print(qgs.find( 'title').text)

    #     # basics
        dico_qgs['title'] = qgs.find('title').text
    #     dico_qgs['description'] = qgs.description
    #     dico_qgs['creator_prod'] = qgs.author
        dico_qgs['folder'] = path.dirname(qgs_path)
        dico_qgs['version'] = qgs.attrib["version"]
    #     dico_qgs['credits'] = qgs.credits
    #     dico_qgs['keywords'] = qgs.tags
    #     dico_qgs['subject'] = qgs.summary
    #     dico_qgs['relpath'] = qgs.relativePaths
    #     dico_qgs['url'] = qgs.hyperlinkBase
    #     dico_qgs['date_export'] = qgs.dateExported
    #     dico_qgs['date_print'] = qgs.datePrinted
    #     dico_qgs['date_actu'] = qgs.dateSaved

    #     # by default let's start considering there is only one layer
    #     dframes = ListDataFrames(qgs)
    #     dico_qgs['subdatasets_count'] = len(dframes)

    #     li_dframes_names = []
    #     dico_qgs['dframes_names'] = li_dframes_names

    #     x = 0
    #     for dframe in dframes:
    #         x += 1
    #         # dictionary where will be stored informations
    #         dico_dframe = OrderedDict()
    #         # parent GDB
    #         dico_dframe[u'name'] = dframe.name

    #         # getting layer globlal informations
    #         self.infos_dataframe(dframe, dico_dframe)

    #         # storing layer into the GDB dictionary
    #         dico_qgs['{0}_{1}'.format(x,
    #                                   dico_dframe.get('name'))] = dico_dframe

    #         # reset
    #         del dico_dframe
        # LAYERS
        qgs_layers = qgs.find('projectlayers')
        dico_qgs[u'layers_count'] = len(qgs_layers.getchildren())

        # MAP CANVAS
        qgs_canvas = qgs.find('mapcanvas')
        # units
        dico_qgs[u'units'] = qgs_canvas.find('units').text

        # SRS
        qgs_dest_srs = qgs_canvas.find("destinationsrs").getchildren()
        print(dir(qgs_dest_srs), qgs_dest_srs[0][1].tag)

        
        dico_qgs['srs'] = qgs_dest_srs.find("srsid").text

        # extent
        qgs_extent = qgs_canvas.find('extent').getchildren()
        dico_qgs[u'Xmin'] = round(float(qgs_extent[0].text), 2)
        dico_qgs[u'Xmax'] = round(float(qgs_extent[2].text), 2)
        dico_qgs[u'Ymin'] = round(float(qgs_extent[1].text), 2)
        dico_qgs[u'Ymax'] = round(float(qgs_extent[3].text), 2)

        # scale
        # dico_qgs['maxScale'] = layer_obj.maxScale
        # dico_qgs['minScale'] = layer_obj.minScale

    #     # # secondary
    #     # dico_qgs['license'] = layer_obj.credits
    #     # dico_qgs['broken'] = layer_obj.isBroken

    #     size = path.getsize(qgs_path)
    #     dico_qgs[u"total_size"] = self.sizeof(size)

    #     # global dates
    #     dico_qgs[u'date_crea'] = strftime('%d/%m/%Y',
    #                                       localtime(path.getctime(qgs_path)))

    #     # # total fields count
    #     # total_fields = 0
    #     # dico_qgs['total_fields'] = total_fields

    #     # # total objects count
    #     # total_objs = 0
    #     # dico_qgs['total_objs'] = total_objs

    #     # # parsing layers
    #     return

    # def infos_dataframe(self, dataframe, dico_dframe):
    #     u"""
    #     Gets informations about geography and geometry
    #     """
    #     # spatial extent
    #     extent = dataframe.extent
    #     dico_dframe[u'Xmin'] = round(extent.XMin, 2)
    #     dico_dframe[u'Xmax'] = round(extent.XMax, 2)
    #     dico_dframe[u'Ymin'] = round(extent.YMin, 2)
    #     dico_dframe[u'Ymax'] = round(extent.YMax, 2)

    #     # map settings
    #     dico_dframe[u'mapUnits'] = dataframe.mapUnits

    #     # SRS
    #     srs = extent.spatialReference
    #     dico_dframe[u'srs'] = srs.name
    #     dico_dframe[u'srs_type'] = srs.type
    #     if srs.type == u'Projected':
    #         dico_dframe[u'EPSG'] = srs.PCSCode, srs.PCSName, srs.projectionCode, srs.projectionName
    #     elif srs.type == u'Geographic':
    #         dico_dframe[u'EPSG'] = srs.GCSCode, srs.GCSName, srs.datumCode, srs.datumName
    #     else:
    #         dico_dframe[u'EPSG'] = (srs.PCSCode, srs.PCSName, srs.projectionCode, srs.projectionName),\
    #                                (srs.GCSCode, srs.GCSName, srs.datumCode, srs.datumName)

    #     # layers
    #     li_layers = ListLayers(dataframe)
    #     dico_dframe['layers_count'] = len(li_layers)
    #     dico_dframe['layers_names'] = [layer.name for layer in li_layers]

    #     # end of function
    #     return

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


    def erratum(self, dico_qgs, qgs_path, mess):
        u""" errors handler """
        # storing minimal informations to give clues to solve later
        dico_qgs[u'name'] = path.basename(qgspath)
        dico_qgs[u'folder'] = path.dirname(qgspath)
        dico_qgs[u'error'] = mess
        # End of function
        return dico_qgs

# ############################################################################
# #### Stand alone program ########
# #################################

if __name__ == '__main__':
    u"""
    Standalone execution for development and tests. Paths are relative considering
    a test within the official repository (https://github.com/Guts/DicoGIS/)
    """
    # searching for qgs Files
    dir_qgs = path.abspath(r'..\..\test\datatest\maps_docs\qgs')
    # dir_qgs = path.abspath(r'\\Copernic\SIG_RESSOURCES\1_qgs\ADMINISTRATIF')
    chdir(path.abspath(dir_qgs))
    li_qgs = listdir(path.abspath(dir_qgs))
    li_qgs = [path.abspath(qgs) for qgs in li_qgs if path.splitext(qgs)[1].lower()=='.qgs']

    # recipient datas
    dico_qgs = OrderedDict()

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

    # read qgs
    for qgspath in li_qgs:
        dico_qgs.clear()
        if path.isfile(qgspath):
            # print("\n{0}: ".format(qgspath))
            ReadQGS(qgspath,
                     dico_qgs,
                     'QGIS Document',
                     txt=textos)
            # print results
            print(dico_qgs)
        else:
            print("{0} is not a recognized file".format(qgspath))
            continue
