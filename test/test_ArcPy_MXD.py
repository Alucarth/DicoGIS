# -*- coding: UTF-8 -*-
#!/usr/bin/env python
# from __future__ import unicode_literals

#------------------------------------------------------------------------------
# Name:         Infos MXD
# Purpose:      Get some metadata abour MXD files (Esri map documents)
#
# Author:       Julien Moura (https://github.com/Guts/)
#
# Python:       2.7.x
# Created:      23/10/2015
# Updated:      12/2015
# Licence:      GPL 3
#------------------------------------------------------------------------------

###############################################################################
########### Libraries #############
###################################
# Standard library
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
from arcpy.mapping import MapDocument, ListLayers, ListBrokenDataSources, ListDataFrames

###############################################################################
########## Functions ############
#################################
def read_mxd(mxd_path):
    """

    """
    # open layer file
    mxd = MapDocument(mxd_path)

    # basic informations
    print(mxd.title)
    print(mxd.description)
    print(mxd.author)
    print(mxd.filePath)
    print(mxd.credits)
    print(mxd.tags)
    print(mxd.summary)
    print('relative paths ?', mxd.relativePaths)
    print(mxd.hyperlinkBase)
    print(mxd.dateExported)
    print(mxd.datePrinted)
    print(mxd.dateSaved)
    # print(mxd.activeDataFrame)
    # print(mxd.activeView)
    print(mxd.dataDrivenPages)

    # dataframes
    dfs = ListDataFrames(mxd)

    # broken datasources
    lost_ds = ListBrokenDataSources(mxd)
    for layer in lost_ds:
        print(layer.name)
    
    del mxd

    # End read MXD
    return

def main(workspace):
    """
    Create a pool class and run the jobs–the number of jobs is equal to the number of MXD
    """
    # setting the workspace
    
    enviro.workspace = workspace

    # listing mxd files
    mxds = ListFiles('*.mxd')
    mxd_list = [path.join(workspace, mxd) for mxd in mxds]
    print(mxd_list)

    # recipient dictionary
    dico_mxd = {}

    # creating the pool to process and the mapping between task and objects
    pool = multiprocessing.Pool()
    pool.apply_async(read_mxd, mxd_list)

    # Synchronize the main process with the job processes to ensure proper cleanup.
    pool.close()
    pool.join()

###############################################################################
###### Stand alone program ########
###################################
if __name__ == '__main__':
    main(workspace = path.realpath(r'datatest\maps_docs\mxd'))
