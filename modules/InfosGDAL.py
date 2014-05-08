# -*- coding: UTF-8 -*-
#!/usr/bin/env python
##from __future__ import unicode_literals
#-------------------------------------------------------------------------------
# Name:         InfosGDAL
# Purpose:      Use GDAL/OGR library to extract informations about
#                   geographic data. It permits a more friendly use as
#                   submodule.
#
# Author:       Julien Moura (https://github.com/Guts/)
#
# Python:       2.7.x
# Created:      18/02/2014
# Updated:      07/05/2014
# Licence:      GPL 3
#-------------------------------------------------------------------------------

################################################################################
########### Libraries #############
###################################
# Standard library
from os import walk, path       # files and folder managing
from time import localtime, strptime, strftime

# Python 3 backported
from collections import OrderedDict as OD

# 3rd party libraries
from osgeo import gdal    # handler for raster spatial files

################################################################################
########### Classes #############
###################################

class InfosRasters(self):
	""" """
	return



################################################################################
###### Stand alone program ########
###################################

if __name__ == '__main__':
    u""" standalone execution for tests. Paths are relative considering a test
    within the official repository (https://github.com/Guts/DicoShapes/)"""
    # libraries import
    from os import getcwd, chdir, path
    # test files
    li_ecw = [r'C:\Users\julien.moura\Documents\GIS Database\ECW\0468_6740.ecw']	# ECW
    li_gtif = [r'C:\Users\julien.moura\Documents\GIS Database\GeoTiff\BDP_07_0621_0049_020_LZ1.tif']	# GeoTIFF
    li_jpg2 = [r'C:\Users\julien.moura\Documents\GIS Database\JPEG2000\image_jpg2000.jp2']	# JPEG2000
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
    # recipient datas
    dicouche = OD()     # dictionary where will be stored informations
    dico_fields = OD()     # dictionary for fields information
    # execution
    for shp in li_shp:
        """ looping on shapefiles list """
        # reset recipient data
        dicouche.clear()
        dico_fields.clear()
        # getting the informations
        print shp
        info_shp = InfosOGR(shp, dicouche, dico_fields, 'shape', textos)
        print '\n', dicouche, dico_fields
    for tab in li_tab:
        """ looping on MapInfo tables list """
        # reset recipient data
        dicouche.clear()
        dico_fields.clear()
        # getting the informations
        info_tab = InfosOGR(tab, dicouche, dico_fields, 'table', textos)
        print '\n', dicouche, dico_fields
