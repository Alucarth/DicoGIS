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




################################################################################
########### Classes #############
#################################

def read_featureClass(featureclass):
    """  """
    print featureclass

    # end of function
    return

# print(sys.path)

class Read_GDB():
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
        li_featuresclasses = []
        li_rasters = []

        # # list datasets
        # print self.li_fc_datasets(gdbpath, li_fcdatasets)

        # list all features classes
        self.li_feature_classes(li_featuresclasses)

        # read info from features classes
        for fc in li_featuresclasses:
            self.read_featureClass(fc)

        # list all rasters
        self.li_raster_classes(li_rasters)


    def li_feature_classes(self, li_featuresclasses):
        u""" list all features classes contained in a GDB """
        for dataset in ListDatasets("","featuredataset"):
            fcs = [path.join(dataset, feature) for feature in ListFeatureClasses("*", "", dataset)]
            li_featuresclasses += fcs
        li_featuresclasses += ListFeatureClasses()
            
        # end of function
        return li_featuresclasses


    def li_raster_classes(self, li_rasters):
        u""" list all rasters contained in a GDB """
        for dataset in ListDatasets("","featuredataset"):
            rasters = [path.join(dataset, raster) for raster in ListRasters("*")]
            li_rasters += rasters
        li_rasters += ListRasters()

        # end of function
        return li_rasters


    def read_featureClass(self, featureclass):
        """ get information about a feature class """
        description = Describe(featureclass)

        print "\n" + featureclass + " (in: " + description.catalogPath + ")"
        print "geometry: " + description.shapeType + " (" + description.featureType + ")"
        print "# entities: " + str(GetCount_management(featureclass))

        print "# fields:"
        for nomchp in ListFields(featureclass):
            print nomchp.name + " (" + nomchp.type + ")"

        print "SRS " + description.spatialReference.name        

        # end of function
        return featureclass


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
        Read_GDB(gdb,dico_datasets, dico_raster, 'gdb')