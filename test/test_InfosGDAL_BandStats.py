# -*- coding: UTF-8 -*-
#!/usr/bin/env python
##from __future__ import unicode_literals


# source ref: http://pcjericks.github.io/py-gdalogr-cookbook/raster_layers.html#get-raster-band-information

from osgeo import gdal
import sys

gdal.UseExceptions()

src_ds = gdal.Open(r'C:\Users\julien.moura\Documents\GIS Database\ECW\0468_6740.ecw')
if src_ds is None:
    print 'Unable to open', src_ds
    sys.exit(1)

print "[ RASTER BAND COUNT ]: ", src_ds.RasterCount
for band in range( src_ds.RasterCount ):
    band += 1
    print "[ GETTING BAND ]: ", band
    srcband = src_ds.GetRasterBand(band)
    if srcband is None:
        continue

    stats = srcband.GetStatistics( True, True )
    if stats is None:
        continue

    print "[ STATS ] =  Minimum=%.3f, Maximum=%.3f, Mean=%.3f, StdDev=%.3f" % ( \
                stats[0], stats[1], stats[2], stats[3] )

    print "[ NO DATA VALUE ] = ", srcband.GetNoDataValue()
    print "[ MIN ] = ", srcband.GetMinimum()
    print "[ MAX ] = ", srcband.GetMaximum()
    print "[ SCALE ] = ", srcband.GetScale()
    print "[ UNIT TYPE ] = ", srcband.GetUnitType()
    ctable = srcband.GetColorTable()

    if ctable is None:
        print 'No ColorTable found'
        sys.exit(1)

    print "[ COLOR TABLE COUNT ] = ", ctable.GetCount()
    for i in range( 0, ctable.GetCount() ):
        entry = ctable.GetColorEntry( i )
        if not entry:
            continue
        print "[ COLOR ENTRY RGB ] = ", ctable.GetColorEntryAsRGB( i, entry )