# -*- coding: UTF-8 -*-
#!/usr/bin/env python
##from __future__ import unicode_literals

# source ref: http://pcjericks.github.io/py-gdalogr-cookbook/raster_layers.html#raster-layers
# developed during trainjourney: TGV 6951 ^^


# Standard library
from os import walk, path       # files and folder managing
from time import localtime, strptime, strftime

# Python 3 backported
from collections import OrderedDict as OD

# 3rd party libraries
from osgeo import gdal    # raster spatial files
from osgeo import osr   # handling spatial projections systems

# get GDAL exceptions handler
gdal.UseExceptions()

# test files
li_ecw = [r'C:\Users\julien.moura\Documents\GIS Database\ECW\0468_6740.ecw']    # ECW
li_gtif = [r'C:\Users\julien.moura\Documents\GIS Database\GeoTiff\BDP_07_0621_0049_020_LZ1.tif']    # GeoTIFF
li_jpg2 = [r'C:\Users\julien.moura\Documents\GIS Database\JPEG2000\image_jpg2000.jp2']  # JPEG2000

li_rasters = (li_ecw[0], li_gtif[0], li_jpg2[0])

# check if test files exist
print path.isfile(li_ecw[0])
print path.isfile(li_gtif[0])
print path.isfile(li_jpg2[0])


# read rasters data
for raster in li_rasters:
    rast = gdal.Open(raster)
    print "\n\n",dir(rast)

    # check if raster is GDAL friendly
    if rast is None:
        print "\n\tUnable to open " + raster
        continue

    # basic infos
    print "\nfilename: ", path.basename(raster)
    print "format: ", path.splitext(raster)[1]
    print "dependencies: ", [path.basename(filedepend) for filedepend in rast.GetFileList() if filedepend != raster]

    # tecnical specifications
    print "\nPixel size: columns=%.3f, rows=%.3f" % (rast.RasterXSize, rast.RasterYSize)
    print "Compression rate: " + str(rast.GetMetadata().get('COMPRESSION_RATE_TARGET'))
    print "Color system: " + str(rast.GetMetadata().get('COLORSPACE'))
    print "Version: ", rast.GetMetadata().get('VERSION')

    # raster bands specifications
    print "\nRaster bands count: ", rast.RasterCount
    for band in range(rast.RasterCount):
        band += 1
        print "\n\tBand: #",band
        inband = rast.GetRasterBand(band)
        #print dir(inband)
        if inband is not None:
            print "\tBand got!"
            stats = inband.GetStatistics( True, True )
            if stats is not None:
                print "\n\tStatistics got!"
                print "\t\t\tStatistics: Minimum=%.3f, Maximum=%.3f, Mean=%.3f, StdDev=%.3f" % ( stats[0], stats[1], stats[2], stats[3] )
                print "\t\t\tNoData=", inband.GetNoDataValue()
                print "\t\t\tMinimum=", inband.GetMinimum()
                print "\t\t\tMaximum=", inband.GetMaximum()
                print "\t\t\tScale=", inband.GetScale()
                print "\t\t\tUnit type=", inband.GetUnitType()
            else:
                print "\n\t\tNo statistics available."

            ctable = inband.GetColorTable()
            if ctable is not None:
                print "\n\tColor table found"
                print "\t\tColor table count: ", ctable.GetCount()
                for i in range( 0, ctable.GetCount() ):
                    entry = ctable.GetColorEntry( i )
                    if not entry:
                        continue
                    print "\t\tColor entry RGB = ", ctable.GetColorEntryAsRGB( i, entry )
            else:
                print "\n\tColor table not found."
        else:
            print "Band informations not available."


    # SRS
    srs= osr.SpatialReference()
    srs = srs.ImportFromWkt(rast.GetProjectionRef())
    print "\nProjection: ", type(srs)

    # file description
    #print rast.GetDescription()
    

    # closing dataset properly
    raster = None