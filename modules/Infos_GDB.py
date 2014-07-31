# -*- coding: UTF-8 -*-
#!/usr/bin/env python
# from __future__ import unicode_literals

#-------------------------------------------------------------------------------
# Name:         InfosGDB
# Purpose:      Use arcpy, Python bundle dinto ArcGIS products (ESRI inc) to
#                   extract informations about geographic data.
#
# Author:       Julien Moura (https://github.com/Guts/)
#
# Python:       2.7.x
# Created:      24/05/2014
# Updated:      25/05/2014
# Licence:      GPL 3
#-------------------------------------------------------------------------------

################################################################################
########### Libraries #############
###################################
# Standard library
from os import walk, path       # files and folder managing
import sys
from time import localtime, strptime, strftime

# Python 3 backported
from collections import OrderedDict as OD

# 3rd party libraries
from osgeo import ogr
from osgeo import gdal
from gdalconst import *
gdal.AllRegister()
ogr.UseExceptions()
gdal.UseExceptions()

################################################################################
########### Classes #############
#################################

class Read_GDB():
    def __init__(self, gdb, dico_gdb, dico_layers, dico_fields, tipo, text=''):
        u""" Uses OGR functions to extract basic informations about
        geographic vector file (handles shapefile or MapInfo tables)
        and store into dictionaries.

        gdbpath = path to the FIle Geodatabase Esri
        dico_layer = dictionary for global informations
        dico_fields = dictionary for the fields' informations
        li_fieds = ordered list of fields
        tipo = shp or tab
        text = dictionary of text in the selected language

        """
        # raising OGR specific exceptions
        ogr.UseExceptions()

        # layer count
        dico_gdb['name'] = gdb.GetName()
        dico_gdb['layers_count'] = gdb.GetLayerCount()



################################################################################
###### Stand alone program ########
###################################

if __name__ == '__main__':
    u""" standalone execution for tests. Paths are relative considering a test
    within the official repository (https://github.com/Guts/DicoGIS/)"""
    # libraries import
    from os import getcwd, chdir, path, walk
    import sys
    # searching for File GeoDataBase
    num_folders = 0
    li_gdb = []
    for root, dirs, files in walk(r'..\test\datatest'):
            num_folders = num_folders + len(dirs)
            for d in dirs:
                try:
                    unicode(path.join(root, d))
                    full_path = path.join(root, d)
                except UnicodeDecodeError, e:
                    full_path = path.join(root, d.decode('latin1'))
                    print unicode(full_path), e
                if full_path[-4:].lower() == '.gdb':
                    # add complete path of shapefile
                    li_gdb.append(path.abspath(full_path))
    
    # recipient datas
    dico_gdb = OD()
    dico_layers = OD()  # dictionary where will be stored informations
    dico_fields = OD()  # dictionary for fields information
    
    # read GDB
    for gdb in li_gdb:
        print(gdb)
        dr_gdb_o = ogr.GetDriverByName("OpenFileGDB")
        try:
            gdb = dr_gdb_o.Open(gdb, 0)
            print("OGR driver OpenFileGDB: OK!")
        except Exception, e:
            print e
            sys.exit()
        else:
            Read_GDB(gdb, dico_gdb, dico_layers, dico_fields, 'gdb')
        # print results
        print(dico_gdb)
