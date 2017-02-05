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
from __future__ import print_function
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
        print("\tLet's play with OGR FileGDB driver\n\n".upper())
        print(dir(gdb))
        print(gdb.GetName())
        print(gdb.LayerCount())

class Read_GDB_o():
    def __init__(self, gdb):
        """ """
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
        # playing with driver
        print("\nLet's play with OGR OpenGDB driver".upper())
        print("GDB available methods: {0}".format(dir(gdb)))



        print(gdb.__sizeof__())
        # print(gdb.GetStyleTable())
        print("{0} layers found into.".format(gdb.GetLayerCount()))
        for index in range(gdb.GetLayerCount()):
            # global information about each layer
            layer = gdb.GetLayerByIndex(index)
            # first feature and geometry type
            obj = layer.GetFeature(1)
            geom = obj.GetGeometryRef()
            print(geom.GetGeometryName())
            # SRS
            srs = layer.GetSpatialRef()
            srs.AutoIdentifyEPSG()
            # srs type
            srsmetod = [
                        (srs.IsCompound(), textos.get('srs_comp')),
                        (srs.IsGeocentric(), textos.get('srs_geoc')),
                        (srs.IsGeographic(), textos.get('srs_geog')),
                        (srs.IsLocal(), textos.get('srs_loca')),
                        (srs.IsProjected(), textos.get('srs_proj')),
                        (srs.IsVertical(), textos.get('srs_vert'))
                       ]
            # searching for a match with one of srs types
            for srsmet in srsmetod:
                if srsmet[0] == 1:
                    typsrs = srsmet[1]
                else:
                    continue

            print(typsrs)

            print("\n==============================================\n\t\tLayer available methods: {0}\n".format(dir(layer)))
            print("\nLayer: {0}".format(layer.GetName()))
            print("Xmin = {0} - Xmax = {1} \n\
Ymin = {2} - Ymax = {3}".format(layer.GetExtent()[0],
                                                   layer.GetExtent()[1],
                                                   layer.GetExtent()[2],
                                                   layer.GetExtent()[3]))
            print("Geometry column name: {0}".format(layer.GetFIDColumn()))
            print("# features: {0}".format(layer.GetFeatureCount()))
            print("Geometry type: {0}".format(layer.GetGeomType()))
            # print("Geometry name: {0}".format(layer.GetGeomName()))  # doesn't work
            print("Geometry column: {0}".format(layer.GetGeometryColumn()))
            print(dir(layer.GetGeomType()))
            
            # fields information about each layer
            layer_def = layer.GetLayerDefn()
            print("\n\n\t\tLayer DEFINITION available methods: {0}\n".format(dir(layer_def)))
            print("# fields: {0}".format(layer_def.GetFieldCount()))
            print("# geometry fields: {0}".format(layer_def.GetGeomFieldCount()))
            # print(layer_def.GetGeomFieldDefn())
            print(layer_def.GetGeomType())
            print(dir(layer_def.GetGeomType()))
            # print(layer.GetName())
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
            print("\nFields, available methods: {0}".format(dir(field)))

        # end of function
        print("\nLayer definition, available methods: {0}".format(dir(layer_def)))


################################################################################
###### Stand alone program ########
###################################

if __name__ == '__main__':
    u""" standalone execution for tests. Paths are relative considering a test
    within the official repository (https://github.com/Guts/DicoGIS)"""
    # libraries import
    from os import getcwd, chdir, path
    # test FileGDB
    gdb = r'datatest\FileGDB\Esri_FileGDB\GDB_Test.gdb'

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
    except Exception as e:
        print(e)
        print("FileGeodatabases can't be read by this driver: {0}.\nYou need GDAL/OGR >= 1.11".format("OpenFileGDB"))



### doc : http://gis.stackexchange.com/questions/32762/how-to-access-feature-classes-in-file-geodatabases-with-python-and-gdal
