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
ogr.UseExceptions()
gdal.UseExceptions()

################################################################################
########### Classes #############
#################################

class Read_GDB_f():
    def __init__(self, gdb):
        """ """
        print "\tLet's play with OGR FileGDB driver\n\n".upper()
        print(dir(gdb))
        print(gdb.GetName())
        print(gdb.LayerCount())

class Read_GDB_o():
    def __init__(self, gdb):
        """ """
        print "\nLet's play with OGR OpenGDB driver".upper()
        print(dir(gdb))
        # print(gdb.GetStyleTable())
        print("{0} layers found into.".format(gdb.GetLayerCount()))
        for index in range(gdb.GetLayerCount()):
            # global information about each layer
            layer = gdb.GetLayerByIndex(index)
            print("\nLayer: {0}".format(layer.GetName()))
            print("Xmin = {0} - Xmax = {1} \n\
Ymin = {2} - Ymax = {3}".format(layer.GetExtent()[0],
                                                   layer.GetExtent()[1],
                                                   layer.GetExtent()[2],
                                                   layer.GetExtent()[3]))
            print("Geometry column name: {0}".format(layer.GetFIDColumn()))
            print("# features: {0}".format(layer.GetFeatureCount()))
            print("Geometry type: {0}".format(layer.GetGeomType()))
            # print("{0}".format(layer.GetGeometryColumn()))
            
            # fields information about each layer
            layer_def = layer.GetLayerDefn()
            print("# fields: {0}".format(layer_def.GetFieldCount()))
            print(dir(layer_def))
            print("# geometry fields: {0}".format(layer_def.GetGeomFieldCount()))
            # print(layer_def.GetGeomFieldDefn())
            print(layer_def.GetGeomType())
            # print(layer.GetName())
            print(help(layer_def.GetFieldDefn))
            style_table = layer.GetStyleTable()
            print(style_table)

            for fdidx in range(0, layer_def.GetFieldCount()-1):
                field = layer_def.GetFieldDefn(fdidx)
                print("\n= Field: {0}".format(field.GetName()))
                print("== Type: {0}".format(field.GetTypeName()))
                # print("== Type Name: {0}".format(field.GetFieldTypeName()))
                print("== Name ref: {0}".format(field.GetNameRef()))
                print("== Justify: {0}".format(field.GetJustify()))
                print("== Precision: {0}".format(field.precision))
                print("== Length: {0}".format(field.width))
            
            # end of fields loop
            print(dir(field))

        # end of function
        print("\n")
        print(dir(layer_def))


################################################################################
###### Stand alone program ########
###################################

if __name__ == '__main__':
    u""" standalone execution for tests. Paths are relative considering a test
    within the official repository (https://github.com/Guts/DicoGIS)"""
    # libraries import
    from os import getcwd, chdir, path
    # test FileGDB
    gdb = r'..\test\datatest\GDB_Test.gdb'

    # OGR: FileGDB (see: http://www.gdal.org/drv_filegdb.html)
    # try:
    #     dr_gdb_f = ogr.GetDriverByName("FileGDB")
    # except AttributeError:
    #     print("FileGeodatabases can't be read by this driver: {0}.\
    #     See: http://www.esri.com/apps/products/download/#File_Geodatabase_API_1.3".format("FileGDB"))
    # else:
    #     print("OGR driver FileGDB: OK!")
    #     Read_GDB_f(gdb)

    # OGR: OpenFileGDB (see: http://www.gdal.org/drv_openfilegdb.html)
    try:
        dr_gdb_o = ogr.GetDriverByName("OpenFileGDB")
        gdb = dr_gdb_o.Open(gdb, 0)
        print("OGR driver OpenFileGDB: OK!")
        Read_GDB_o(gdb)
    except Exception, e:
        print e
        print("FileGeodatabases can't be read by this driver: {0}.\nYou need GDAL/OGR >= 1.11".format("OpenFileGDB"))



### doc : http://gis.stackexchange.com/questions/32762/how-to-access-feature-classes-in-file-geodatabases-with-python-and-gdal
