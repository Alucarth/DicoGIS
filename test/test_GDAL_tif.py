# -*- coding: UTF-8 -*-
#!/usr/bin/env python
# from __future__ import unicode_literals

#------------------------------------------------------------------------------
# Name:         Infos Rasters
# Purpose:      Use GDAL library to extract informations about
#                   geographic rasters data. It permits a more friendly use as
#                   submodule.
#
# Author:       Julien Moura (https://github.com/Guts/)
#
# Python:       2.7.x
# Created:      18/02/2014
# Updated:      31/07/2014
# Licence:      GPL 3
#------------------------------------------------------------------------------

###############################################################################
########### Libraries #############
###################################
# Standard library
from __future__ import print_function
from os import chdir, path       # files and folder managing
from time import localtime, strftime

# Python 3 backported
from collections import OrderedDict as OD

# 3rd party libraries
try:
    from osgeo import gdal
    from osgeo import osr
    from osgeo.gdalconst import *
except ImportError:
    import gdal
    import osr
    from gdalconst import *



###############################################################################
###### Stand alone program ########
###################################

if __name__ == '__main__':
    u""" standalone execution for tests. Paths are relative considering a test
    within the official repository (https://github.com/Guts/DicoShapes/)"""
    # listing test files by formats
    li_ecw = [r'C:\\Users\julien.moura\Documents\GIS Database\ECW\0468_6740.ecw']  # ECW
    li_gtif = [r'..\test\datatest\rasters\GeoTiff\BDP_07_0621_0049_020_LZ1.tif',
               r'..\test\datatest\rasters\GeoTiff\TrueMarble_16km_2700x1350.tif',
               r'C:\Users\julien.moura\Documents\GIS Database\GeoTiff\ASTGTM_S17W069_dem.tif',
               r'C:\Users\julien.moura\Documents\GIS Database\GeoTiff\completo1-2.tif']  # GeoTIFF
    li_jpg2 = [r'..\test\datatest\rasters\JPEG2000\image_jpg2000.jp2']  # JPEG2000
    li_rasters = (path.abspath(li_ecw[0]),
                  path.abspath(li_gtif[0]),
                  path.abspath(li_gtif[1]),
                  path.abspath(li_gtif[2]),
                  path.abspath(li_gtif[3]),
                  path.abspath(li_jpg2[0])
                  ) 

    gdal.AllRegister()
    # execution
    for rasterpath in li_rasters:
        print('\n' + rasterpath)
        rast = gdal.Open(rasterpath, GA_ReadOnly)
        print('name: ' + path.basename(rasterpath))
        print('folder: ' + path.dirname(rasterpath))

        rastMD = rast.GetMetadata()
        print(rastMD.get('COMPRESSION_RATE_TARGET'))
        print(rastMD.get('COLORSPACE'))
        print(rastMD.get('VERSION'))

        print(rast.RasterXSize)
        print(rast.RasterYSize)
        print(rast.RasterCount)

        print(gdal.GetDataTypeName(rast.GetRasterBand(1).DataType))

        geotransform = rast.GetGeoTransform()
        print('xOrigin: {}'.format(geotransform[0]))
        print('yOrigin: {}'.format(geotransform[3]))
        print('pixelWidth: {}'.format(round(geotransform[1], 3)))
        print('pixelHeight: {}'.format(round(geotransform[5], 3)))
        print('orientation: {}'.format(geotransform[2]))


        srs = osr.SpatialReference(rast.GetProjection())
        srs.AutoIdentifyEPSG()
        print(srs.GetAttrValue('PROJCS'))
        print(srs.GetAttrValue('GEOGCS'))
        print(srs.GetAttrValue("AUTHORITY", 1))

        for band in range(rast.RasterCount):
            band += 1
            band_info = rast.GetRasterBand(band)
            stats = band_info.GetStatistics(True, True)
            band = None

        del rast