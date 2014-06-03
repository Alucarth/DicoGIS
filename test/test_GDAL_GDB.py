# -*- coding: UTF-8 -*-
#!/usr/bin/env python
# from __future__ import unicode_literals

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
# Updated:      12/05/2014
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
from osgeo import ogr
from gdalconst import *
gdal.AllRegister()

################################################################################
########### Classes #############
#################################




################################################################################
###### Stand alone program ########
###################################

if __name__ == '__main__':
    u""" standalone execution for tests. Paths are relative considering a test
    within the official repository (https://github.com/Guts/DicoShapes/)"""
    # libraries import
    from os import getcwd, chdir, path
    # test FileGDB
    gdb = r'..\test\datatest\GDB_Test.gdb'

    # OGR: FileGDB (see: http://www.gdal.org/drv_filegdb.html)
    try:
        dr_gdb_f = ogr.GetDriverByName("FileGDB")
        gdb_f = dr_gdb_f.Open(gdb, 0)
        print("OGR driver FileGDB: OK!")
    except AttributeError:
        print("FileGeodatabases can't be read by this driver because FileGDB API SDK is not installed (see: http://www.esri.com/apps/products/download/#File_Geodatabase_API_1.3)")

    # OGR: OpenFileGDB (see: http://www.gdal.org/drv_openfilegdb.html)
    try:
        dr_gdb_o = ogr.GetDriverByName("OpenFileGDB")
        gdb_o = dr_gdb_o.Open(gdb, 0)
        print("OGR driver OpenFileGDB: OK!")
    except:
        print("FileGeodatabases can't be read by this driver. You need GDAL/OGR >= 1.11")



### doc : http://gis.stackexchange.com/questions/32762/how-to-access-feature-classes-in-file-geodatabases-with-python-and-gdal
