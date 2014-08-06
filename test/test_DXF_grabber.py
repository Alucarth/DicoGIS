# -*- coding: UTF-8 -*-
#!/usr/bin/env python
from __future__ import unicode_literals

#------------------------------------------------------------------------------
# Name:         Infos DXF
# Purpose:      Use GDAL/OGR to read into AutocAD exchanges file format.
#
# Author:       Julien Moura (https://github.com/Guts/)
#
# Python:       2.7.x
# Created:      24/07/2014
# Updated:      04/08/2014
# Licence:      GPL 3
#------------------------------------------------------------------------------

###############################################################################
########### Libraries #############
###################################
# Standard library
from os import path, walk   # files and folder managing
from time import localtime, strftime
import sys

# Python 3 backported
from collections import OrderedDict as OD

# 3rd party libraries
import dxfgrabber


###############################################################################
########### Classes #############
#################################

class Read_DXF():
    def __init__(self, dxfpath, dico_dxf, tipo, txt=''):
        u""" Uses OGR functions to extract basic informations about
        geographic vector file (handles shapefile or MapInfo tables)
        and store into dictionaries.

        dxfpath = path to the File Geodatabase Esri
        dico_dxf = dictionary for global informations
        dico_fields = dictionary for the fields' informations
        li_fieds = ordered list of fields
        tipo = format
        text = dictionary of text in the selected language

        """
        # opening
        dxf = dxfgrabber.readfile(dxfpath)

        # AutoCAD version
        dico_dxf['version_code'] = dxf.dxfversion
        # see: http://dxfgrabber.readthedocs.org/en/latest/#Drawing.dxfversion
        if dxf.dxfversion == 'AC1009':
            dico_dxf['version_name'] = 'AutoCAD R12'
        elif dxf.dxfversion == 'AC1015':
            dico_dxf['version_name'] = 'AutoCAD R2000'
        elif dxf.dxfversion == 'AC1018':
            dico_dxf['version_name'] = 'AutoCAD R2004'
        elif dxf.dxfversion == 'AC1021':
            dico_dxf['version_name'] = 'AutoCAD R2007'
        elif dxf.dxfversion == 'AC1024':
            dico_dxf['version_name'] = 'AutoCAD R2010'
        elif dxf.dxfversion == 'AC1027':
            dico_dxf['version_name'] = 'AutoCAD R2013'
        else:
            dico_dxf['version_name'] = 'NR'

        # headers
        dico_dxf['headers_var_count'] = len(dxf.header)

        # layers count
        dico_dxf['layers_count'] = len(dxf.layers)

        # entities count
        dico_dxf['entities_count'] = len(dxf.entities)

    def sizeof(self, os_size):
        u""" return size in different units depending on size
        see http://stackoverflow.com/a/1094933 """
        for size_cat in ['octets', 'Ko', 'Mo', 'Go']:
            if os_size < 1024.0:
                return "%3.1f %s" % (os_size, size_cat)
            os_size /= 1024.0
        return "%3.1f %s" % (os_size, " To")

###############################################################################
###### Stand alone program ########
###################################

if __name__ == '__main__':
    u""" standalone execution for tests. Paths are relative considering a test
    within the official repository (https://github.com/Guts/DicoGIS/)"""
    # searching for DX Files
    num_folders = 0
    li_dxf = [r'..\test\datatest\cao\dxf\paris_transports.dxf']
    
    # recipient datas
    dico_dxf = OD()
    
    # read DXF
    for dxfpath in li_dxf:
        dico_dxf.clear()
        if path.isfile(dxfpath):
            print("\n{0}: ".format(dxfpath))
            Read_DXF(dxfpath,
                     dico_dxf,
                     'AutoCAD DXF')
            # print results
            print(dico_dxf)
        else:
            pass
