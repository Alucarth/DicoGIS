# -*- coding: UTF-8 -*-
#!/usr/bin/env python
from __future__ import unicode_literals

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
import multiprocessing
from os import walk, path       # files and folder managing
import sys
from time import localtime, strptime, strftime

# Python 3 backported
from collections import OrderedDict as OD

# 3rd party libraries
try:
    import arcpy
    print("Great! ArcGIS is well installed.")
except ImportError:
    print("ArcGIS isn't registered in the sys.path")
    sys.path.append(r'C:\Program Files (x86)\ArcGIS\Desktop10.2\arcpy')
    sys.path.append(r'C:\Program Files (x86)\ArcGIS\Desktop10.2\bin')
    sys.path.append(r'C:\Program Files (x86)\ArcGIS\Desktop10.2\ArcToolbox\Scripts')
    try:
        from arcpy import env as enviro
        from arcpy import ListDatasets, ListFeatureClasses, GetCount_management
        print("ArcGIS has been added to Python path and then imported.")
    except:
        print("ArcGIS isn't installed on this computer")
        sys.exit()



################################################################################
########### Classes #############
#################################

def read_featureClass(featureclass):
    """  """
    print featureclass

    # end of function
    return

# print(sys.path)

class InfosGDB():
    def __init__(self, gdbpath, dico_layer, dico_fields, tipo, text=''):
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
        ## global ArcGIS environment settings
        enviro.maintainSpatialIndex = True
        enviro.workspace = gdbpath

        # variables
        li_fcdatasets = []
        li_featuresclasses = []

        #
        feats = []
        for dataset in ListDatasets("","featuredataset"):
            feats += ListFeatureClasses("*", "", dataset)
        print "autre : " + str(feats)

        # list datasets
        print self.li_fc_datasets(gdbpath, li_fcdatasets)

        # list Features Classes
        print self.li_featuresclasses(li_fcdatasets, li_featuresclasses)


    def li_fc_datasets(self,gdb, li_fcdatasets):
        u""" list all Feature Datasets into a File Geodatabase  """
        # looking for datasets
        for dataset in ListDatasets("","featuredataset"):
            li_fcdatasets.append(path.join(gdb, dataset))

        #  checking if Feature Classes exist into gdb's root
        if len(ListFeatureClasses('*')) != 0:
            li_fcdatasets.append('')

        # end of function
        return li_fcdatasets

    def li_featuresclasses(self, li_datasets, li_featuresclasses):
        u"""  """
        for dataset in li_datasets:
            li_featuresclasses += ListFeatureClasses("*", "", dataset)
            
        # end of function
        return li_featuresclasses


    def li_raster(self, li_datasets):
        u"""  """
        for dataset in ListDatasets("","featuredataset"):
            print dataset
            li_datasets.append(path.join(gdb, dataset))

        # end of function
        return li_datasets


    def read_featureClass(self, featureclass):
        """  """
        print featureclass

        # end of function
        return


    # def process(self, list_targets):
    #     """  """
    #     # create a pool to multi-process the features classes found
    #     pool = multiprocessing.Pool()
    #     print('\n\tpool_creation')
    #     pool.map(lambda:self.read_featureClass, list_targets)
    #     print('pool mapped')

    #     # Synchronize the main process with the job processes to ensure proper cleanup.
    #     pool.close()      
    #     pool.join()

    #     # end of function
    #     return


################################################################################
###### Stand alone program ########
###################################

if __name__ == '__main__':
    u""" standalone execution for tests. Paths are relative considering a test
    within the official repository (https://github.com/Guts/DicoGIS/)"""
    # libraries import
    from os import getcwd, chdir, path, walk
    # searching for File Geodatabase
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

    print li_gdb
    
    # recipient datas
    dico_datasets = OD()
    dico_raster = OD()      # dictionary where will be stored informations
    dico_bands = OD()       # dictionary for fields information
    
    # launch   
    # def read_featureClass(featureclass):
    #     """  """
    #     print featureclass

    #     # end of function
    #     return

    # enviro.workspace = li_gdb[0]

    # # list Features Classes
    # li_fcs = ListFeatureClasses('*')
    # li_fcs = [path.join(enviro.workspace, feature) for feature in li_fcs]

    # print('list fcs')
    # jobs = []
    # # create a pool to multi-process the features classes found
    # pool = multiprocessing.Pool()
    # print('pool_creation')
    # jobs.append(pool.apply_async(read_featureClass, (li_fcs[0]))) # send jobs to be processed

    # pool.map(read_featureClass, li_fcs)
    # print('pool mapped')

    # # Synchronize the main process with the job processes to ensure proper cleanup.
    # pool.close()      
    # pool.join()

    for gdb in li_gdb:
        InfosGDB(gdb,dico_datasets, dico_raster, 'gdb')