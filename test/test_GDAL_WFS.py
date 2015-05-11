# -*- coding: UTF-8 -*-
#!/usr/bin/env python
from __future__ import unicode_literals

#-------------------------------------------------------------------------------
# Name:         InfosWFS
# Purpose:      Use GDAL/OGR library to extract informations about
#                   geographic data. It permits a more friendly use as
#                   submodule.
#
# Author:       Julien Moura (https://github.com/Guts/)
#
# Python:       2.7.x
# Created:      18/04/2015
# Updated:      12/05/2015
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
try:
    from osgeo import gdal
    from osgeo import ogr  # handler for vector spatial files
    from osgeo import osr
except ImportError:
    import gdal
    import ogr  # handler for vector spatial files
    import osr

from gdalconst import *
gdal.AllRegister()
ogr.UseExceptions()
gdal.UseExceptions()


from owslib.wfs import WebFeatureService

################################################################################
########### Classes #############
#################################


class Read_WFS():
    def __init__(self, wfs):
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
        print "\nLet's play with OGR Openwfs driver".upper()
        print("WFS available methods: {0}".format(dir(wfs)))



        print wfs.__sizeof__()
        # print(wfs.GetStyleTable())
        print("{0} layers found into.".format(wfs.GetLayerCount()))
        for index in range(wfs.GetLayerCount()):
            # global information about each layer
            layer = wfs.GetLayerByIndex(index)
            # first feature and geometry type
            obj = layer.GetFeature(1)
            geom = obj.GetGeometryRef()
            print geom.GetGeometryName()
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

            print typsrs

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
            print dir(layer.GetGeomType())
            
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
    import time

    # # custom settings to enhance querying WFS capabilities for services with a lot of layers
    gdal.SetConfigOption(str('OGR_WFS_LOAD_MULTIPLE_LAYER_DEFN'), str(1))

    # # Set config for paging. Works on WFS 2.0 services and WFS 1.0 and 1.1 with some other services.
    # gdal.SetConfigOption(str('OGR_WFS_PAGING_ALLOWED'), str('YES'))
    # gdal.SetConfigOption(str('OGR_WFS_PAGE_SIZE'), str('1'))
    gdal.SetConfigOption(str('OGR_WFS_BASE_START_INDEX'), str(1))
    gdal.SetConfigOption(str('OGR_WFS_USE_STREAMING'), str(1))

    # test WFS
    WFS_URL = r"http://noisy.hq.isogeo.fr:6090/geoserver/Isogeo/ows"
    # WFS_URL = r"http://ws.carmencarto.fr/WFS/119/fxx_inpn?service=wfs"
    # WFS_URL = r"http://demo.mapserver.org/cgi-bin/wfs?service=WFS"

    # # OGR WFS (see: http://www.gdal.org/drv_wfs.html)
    # try:
    #     OGR_start = time.clock()
    #     drv_wfs = ogr.GetDriverByName(str('WFS'))
    #     wfs = drv_wfs.Open(str('WFS:') + WFS_URL)
    #     print(wfs.name)
    #     print("OGR driver WFS: OK!")
        
    # except Exception, e:
    #     print e
    #     print("WFS error: can not open WFS datasource")

    # #
    # # print(wfs.GetName())
    # # print(wfs.GetSummaryRefCount())

    # #
    # capabilities = wfs.GetLayerByName(str("WFSGetCapabilities"))
    # # print(dir(capabilities))
    # print(capabilities.GetName())
    # print(capabilities.GetExtent())

    # #
    # metadata = wfs.GetLayerByName(str("WFSLayerMetadata"))
    # # print dir(metadata)
    # print(metadata.GetName())


    # for i in range(wfs.GetLayerCount()):
    #     layer = wfs.GetLayerByIndex(i)
    #     # print layer.GetName(), layer.GetFeatureCount()
    #     srs = layer.GetSpatialRef()
    #     srs.AutoIdentifyEPSG()
    #     print 'Layer: %s, Features: %s, SR: %s' % (layer.GetName(), layer.GetFeatureCount(), srs.ExportToWkt()[0:50])
    #     print layer.GetExtent()
    #     feat = layer.GetNextFeature()
    #     geom = feat.GetGeometryRef()
    #     print(geom.GetGeometryName())
        
    #     layer_def = layer.GetLayerDefn()
    #     print(layer_def.GetFieldCount())
    #     layer = None

    # OGR_end = time.clock()
    # print(OGR_end - OGR_start)

    OWS_start = time.clock()
    try:
        wfs = WebFeatureService(WFS_URL, version="2.0.0")
    except AttributeError:
        wfs = WebFeatureService(WFS_URL, version="1.1.0")

    print("\n\tGlobal: ", dir(wfs))
    print(wfs.version)
    print(wfs.url)
    print(wfs.items()[0][1])
    help(wfs.getSRS)
    print(wfs.timeout)

    print("\n\tIdentification: ", dir(wfs.identification))
    print(wfs.identification.type)
    print(wfs.identification.title)
    print(wfs.identification.service)
    abstract = wfs.identification.abstract
    if abstract: print(abstract.encode('utf8'))
    print(wfs.identification.fees)
    print(wfs.identification.version)
    print(wfs.identification.keywords)
    print(wfs.identification.accessconstraints)
    print(wfs.identification.profiles)
    
    print("\n\tProvider: ", dir(wfs.provider))
    print(wfs.provider.name)
    print(wfs.provider.url)
    print(wfs.provider.contact.email)
    print(wfs.provider.contact.phone)
    print(wfs.provider.contact.name)
    print(wfs.provider.contact.organization)
    print(wfs.provider.contact.city)
    print(wfs.provider.contact.region)
    print(wfs.provider.contact.postcode)
    print(wfs.provider.contact.country)

    print("\n\tOperations: ", [op.name for op in wfs.operations])
    
    op_describe = wfs.getOperationByName('DescribeFeatureType')
    help(op_describe)

    get_cap = wfs.getOperationByName('GetCapabilities')
    # help(get_cap)
    
    print(wfs.getGETGetFeatureRequest())

    get_feat = wfs.getOperationByName('GetFeature')
    # help(get_feat)
    

    for layer in list(wfs.contents):
        try:
            print(u'Layer: %s, Features: %s, SR: %s...' % (wfs[layer].title, wfs[layer].abstract, wfs[layer].crsOptions))
            print(wfs[layer].boundingBox)
            print(wfs[layer].boundingBoxWGS84)
            print(wfs[layer].keywords)

            # response = wfs.describefeaturetype()
            # print dir(response)

            response = wfs.getfeature(typename=(layer,))
            print(type(response))
            numb = response.read().find('<wfs:FeatureCollection')
            print(numb)

        except UnicodeEncodeError:
            title = wfs[layer].title
            print title.encode("UTF-8")
            abstract = wfs[layer].abstract
            if abstract: print abstract.encode("UTF-8")
            print wfs[layer].id
            print wfs[layer].keywords
            print(wfs[layer].boundingBox)
            print(wfs[layer].boundingBoxWGS84)
            print(wfs[layer].keywords)
            print(wfs[layer].metadataUrls)
            print(wfs[layer].timepositions)
            print(wfs[layer].defaulttimeposition)
            print(wfs[layer].styles)
            print(wfs[layer].verbOptions)
            print(map(lambda x: x.getcode(), wfs[layer].crsOptions))

            response = wfs.getfeature(typename=(layer,))
            numb = response.read().find('<wfs:FeatureCollection')
            print(numb)
        except UnicodeDecodeError:
            continue

    OWS_end = time.clock()
    print(OWS_end - OWS_start)
