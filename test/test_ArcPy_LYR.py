# -*- coding: UTF-8 -*-
#!/usr/bin/env python
# from __future__ import unicode_literals

#------------------------------------------------------------------------------
# Name:         Infos LYR
# Purpose:      Get some metadata abour LYR files (Esri symbology layer))
#
# Author:       Julien Moura (https://github.com/Guts/)
#
# Python:       2.7.x
# Created:      23/10/2015
# Updated:      10/2015
# Licence:      GPL 3
#------------------------------------------------------------------------------

###############################################################################
########### Libraries #############
###################################
# Standard library
from __future__ import print_function
from os import path
import re
import multiprocessing
import sys

# 3rd party libraries
try:
    from arcpy import env as enviro
    print("Great! ArcGIS is well installed.")
except ImportError:
    print("ArcGIS isn't registered in the sys.path")
    sys.path.append(r'C:\Program Files (x86)\ArcGIS\Desktop10.2\arcpy')
    sys.path.append(r'C:\Program Files (x86)\ArcGIS\Desktop10.2\bin')
    sys.path.append(r'C:\Program Files (x86)\ArcGIS\Desktop10.2\ArcToolbox\Scripts')
    try:
        from arcpy import env as enviro
        print("ArcGIS has been added to Python path and then imported.")
    except:
        print("ArcGIS isn'installed on this computer")
        sys.exit()

# if arcppy is installed
from arcpy import ListFiles, Describe
from arcpy.mapping import Layer, ListLayers

###############################################################################
########## Functions ############
#################################
def read_lyr(lyr_path):
    """

    """
    # open layer file
    layer = Layer(lyr_path)

    # 
    print(layer.name)
    print(layer.description)
    

    # # Define the projection to wgs84 — factory code is 4326
    # print "Name String: " + layer.nameString
    # print "Where Clause: " + layer.whereClause

    # # Find out if the layer represents a feature class
    # if layer.dataElement.dataType != "FeatureClass":
    #     print("\nThis is not a featureclass")
    #     sys.exit()
    # else:
    #     print "Feature class:      " + layer.dataElement.catalogPath
    #     print "Feature class Type: " + layer.featureClass.featureType

    # #
    # layers_in = ListLayers(layer)

    # End update_shapefiles
    return

def main():
    """
    Create a pool class and run the jobs–the number of jobs is equal to the number of shapefiles
    """
    # setting the workspace
    workspace = path.abspath(r'datatest\maps_docs\lyr')
    enviro.workspace = workspace

    # listing lyr files
    # li_lyr = [r'datatest\maps_docs\lyr\PRIF 2014.lyr',
    #           r'datatest\maps_docs\lyr\PRIF 2013.lyr',
    #           r'datatest\maps_docs\lyr\PRIF 2012.lyr']
    fcs = ListFiles('*.lyr')
    fc_list = [path.join(workspace, fc) for fc in fcs]
    print(fc_list)

    # 
    dico_lyr = {}

    # creating the pool to process and the mapping between task and objects
    pool = multiprocessing.Pool()
    pool.apply_async(read_lyr, fc_list)

    # Synchronize the main process with the job processes to ensure proper cleanup.
    pool.close()
    pool.join()

###############################################################################
###### Stand alone program ########
###################################
if __name__ == '__main__':
    main()
