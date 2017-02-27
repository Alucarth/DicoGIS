# -*- coding: UTF-8 -*-
#!/usr/bin/env python
# from __future__ import unicode_literals

# -----------------------------------------------------------------------------
# Name:         InfosGDAL
# Purpose:      Use GDAL/OGR library to extract informations about
#                   geographic data. It permits a more friendly use as
#                   submodule.
#
# Author:       Julien Moura (https://github.com/Guts/)
#
# Python:       2.7.x
# Created:      18/02/2014
# Updated:      12/09/2014
# Licence:      GPL 3
# -----------------------------------------------------------------------------

# #############################################################################
# ########## Libraries #############
# ##################################
# Standard library
from __future__ import print_function
from os import chdir, listdir, walk, path       # files and folder managing
from time import localtime, strptime, strftime

# Python 3 backported
from collections import OrderedDict as OD

# 3rd party libraries
from osgeo import gdal    # handler for raster spatial files
from osgeo import ogr
from gdalconst import *
gdal.AllRegister()

# #############################################################################
# ########## Classes #############
# ################################

dico_geopdf = OD()

# sample files
dir_pdf = path.abspath(r'datatest\maps_docs\pdf')
chdir(path.abspath(dir_pdf))
li_pdf = listdir(path.abspath(dir_pdf))
li_pdf = [path.abspath(pdf) for pdf in li_pdf if path.splitext(pdf)[1].lower()=='.pdf']


for in_pdf in li_pdf:
    geopdf = gdal.Open(in_pdf)
    print(dir(geopdf))
    # basics
    dico_geopdf[u'name'] = path.basename(in_pdf)
    dico_geopdf[u'folder'] = path.dirname(in_pdf)

    # dependencies
    dependencies = [path.basename(filedepend) for filedepend in
                    geopdf.GetFileList() if filedepend != in_pdf]
    dico_geopdf[u'dependencies'] = dependencies

    # total size
    dependencies.append(in_pdf)
    # total_size = sum([path.getsize(f) for f in dependencies])
    # dico_geopdf[u"total_size"] = total_size
    dependencies.pop(-1)

    # metadata
    geopdf_MD = geopdf.GetMetadata()
    print(geopdf_MD.keys())
    dico_geopdf[u'title'] = geopdf_MD.get('TITLE')
    dico_geopdf[u'creator'] = geopdf_MD.get('CREATOR')
    dico_geopdf[u'producer'] = geopdf_MD.get('PRODUCER')
    dico_geopdf[u'neatline'] = geopdf_MD.get('NEATLINE')
    dico_geopdf[u'date_crea'] = geopdf_MD.get('CREATION_DATE')

    geopdf_MDdomainlist = geopdf.GetMetadataDomainList()
    

    #
    dico_geopdf[u'raster_count'] = geopdf.RasterCount
    dico_geopdf[u'subdatasets_count'] = len(geopdf.GetSubDatasets())

    # read = geopdf.ReadRaster()
    # readray = geopdf.ReadAsArray()

    # geopdf.GetLayers()

    # help(geopdf.BeginAsyncReader)

    # overviews
    ov = geopdf.BuildOverviews()

    # description
    description = geopdf.GetDescription()

    # GCPs
    gcp_count = geopdf.GetGCPCount()
    gcps = geopdf.GetGCPs()

    # end
    print(dico_geopdf)

geopdf_v = ogr.Open(in_pdf)
# print(dir(geopdf_v))
print(geopdf_v.GetLayerCount())
# print(geopdf_v.GetName())
for index in range(geopdf_v.GetLayerCount()):
    # global information about each layer
    layer = geopdf_v.GetLayerByIndex(index)
    # first feature and geometry type
    obj = layer.GetFeature(1)
    geom = obj.GetGeometryRef()
    print(geom.GetGeometryName())
    # SRS
    srs = layer.GetSpatialRef()
    srs.AutoIdentifyEPSG()
    # srs type
    srsmetod = [(srs.IsCompound(), 'srs_comp'),
                (srs.IsGeocentric(), 'srs_geoc'),
                (srs.IsGeographic(), 'srs_geog'),
                (srs.IsLocal(), 'srs_loca'),
                (srs.IsProjected(), 'srs_proj'),
                (srs.IsVertical(), 'srs_vert')
                ]
    # searching for a match with one of srs types
    for srsmet in srsmetod:
        if srsmet[0] == 1:
            typsrs = srsmet[1]
        else:
            continue

    print(typsrs)

    print("\n\n\t\tLayer available methods: {0}\n".format(dir(layer)))
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
    dico_fields = OD()
    layer_def = layer.GetLayerDefn()
    print("\n\n\t\tLayer DEFINITION available methods: {0}\n".format(dir(layer_def)))
    print("# fields: {0}".format(layer_def.GetFieldCount()))
    dico_fields[u"geometry_fields_count"] = layer_def.GetGeomFieldCount()
    # print(layer_def.GetGeomFieldDefn())
    print(layer_def.GetGeomType())
    # print(dir(layer_def.GetGeomType()))
    # print(layer.GetName())
    style_table = layer.GetStyleTable()
    print(style_table)



    for fdidx in range(0, layer_def.GetFieldCount()-1):
        field = layer_def.GetFieldDefn(fdidx)
        print("\n= Field: {0}".format(field.GetName()))
        print("== Rank: {0}".format(fdidx))
        print("== Type: {0}".format(field.GetTypeName()))
        # print("== Type Name: {0}".format(field.GetFieldTypeName(field.GetType())))
        print("== Name ref: {0}".format(field.GetNameRef()))
        print("== Justify: {0}".format(field.GetJustify()))
        print("== Precision: {0}".format(field.precision))
        print("== Length: {0}".format(field.width))
    
    # end of fields loop
    print("\nFields, available methods: {0}".format(dir(field)))

# end of function
print("\nLayer definition, available methods: {0}".format(dir(layer_def)))
