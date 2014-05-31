# -*- coding: UTF-8 -*-
#!/usr/bin/env python
from __future__ import unicode_literals

#-------------------------------------------------------------------------------
# Name:         InfosGDAL
# Purpose:      Use GDAL/OGR library to extract informations about
#                   geographic data. It permits a more friendly use as
#                   submodule.
#
# Author:       Julien Moura (https://github.com/Guts/)
#
# Python:       2.7.x
# Created:      18/02/2014
# Updated:      28/05/2014
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
from osgeo import gdal    # handler for raster spatial files

################################################################################
########### Classes #############
###################################

class InfosRasters():
    def __init__(self, rasterpath, dico_raster, dico_bands, tipo, text=''):
        u""" Uses GDAL functions to extract basic informations about
        geographic raster file (handles ECW, GeoTIFF, JPEG2000)
        and store into dictionaries.

        layerpath = path to the geographic file
        dico_raster = dictionary for global informations
        dico_bands = dictionary for the bands informations
        li_fieds = ordered list of fields
        tipo = format
        text = dictionary of text in the selected language
        """
        # variables
        self.alert = 0

        print rasterpath
        # opening file
        self.rast = gdal.Open(rasterpath)
        
        # check if raster is GDAL friendly
        if self.rast is None:
            print("\n\tUnable to open " + rasterpath)
            print("Please check compatibility.")
            self.alert += 1

        # basic informations
        dico_raster[u'format'] = tipo
        self.infos_basics(rasterpath, dico_raster, text)
        # geometry information
        self.infos_geom(dico_raster, text)
        # bands information
        for band in range(1, dico_raster.get('num_bands')):
            self.infos_bands(band, dico_bands)

    def infos_basics(self, rasterpath, dico_raster, txt):
        u""" get the global informations about the raster """
        # files and folder
        dico_raster[u'name'] = path.basename(rasterpath)
        dico_raster[u'folder'] = path.dirname(rasterpath)
        dico_raster[u'title'] = dico_raster[u'name'][:-4].replace('_', ' ').capitalize()
        dico_raster[u'dependencies'] = [path.basename(filedepend) for filedepend in self.rast.GetFileList() if filedepend != rasterpath]
        # format
        dico_raster[u'compr_rate'] = self.rast.GetMetadata().get('COMPRESSION_RATE_TARGET')
        dico_raster[u'color_ref'] = self.rast.GetMetadata().get('COLORSPACE')
        if self.rast.GetMetadata().get('VERSION'):
            dico_raster[u'format_version'] = "(v{})".format(self.rast.GetMetadata().get('VERSION'))
        else:
            dico_raster[u'format_version'] = ""
        # image specifications
        dico_raster[u'pixel_size_X'] = self.rast.RasterXSize
        dico_raster[u'pixel_size_Y'] = self.rast.RasterYSize
        dico_raster[u'num_bands'] = self.rast.RasterCount

        # basic dates
        dico_raster[u'date_actu'] = strftime('%Y-%m-%d',
                                            localtime(path.getmtime(rasterpath)))
        dico_raster[u'date_crea'] = strftime('%Y-%m-%d',
                                            localtime(path.getctime(rasterpath)))

        # end of function
        return dico_raster


    def infos_geom(self, dico_raster, txt):
        u""" get the informations about geometry """
        # Spatial extent (bounding box)
        dico_raster[u'Xmin'] = round(self.rast.GetExtent()[0],2)
        dico_raster[u'Xmax'] = round(self.rast.GetExtent()[1],2)
        dico_raster[u'Ymin'] = round(self.rast.GetExtent()[2],2)
        dico_raster[u'Ymax'] = round(self.rast.GetExtent()[3],2)

        # end of function
        return dico_raster


    def infos_bands(self, band, dico_bands):
        u""" get the informations about fields definitions """
        band_info = self.rast.GetRasterBand(band)
        dico_bands["band{}_Min".format(band)] = band_info.GetMinimum()
        dico_bands["band{}_Max".format(band)] = band_info.GetMaximum()
        dico_bands["band{}_NoData".format(band)] = band_info.GetNoDataValue()

        # end of function
        return dico_bands


    def erratum(self, dicolayer, layerpath, mess):
        u""" errors handling """
        # local variables
        dicolayer[u'name'] = path.basename(layerpath)
        dicolayer[u'folder'] = path.dirname(layerpath)
        def_couche = self.layer.GetLayerDefn()
        dicolayer[u'num_fields'] = def_couche.GetFieldCount()
        dicolayer[u'error'] = mess
        # End of function
        return dicolayer


################################################################################
###### Stand alone program ########
###################################

if __name__ == '__main__':
    u""" standalone execution for tests. Paths are relative considering a test
    within the official repository (https://github.com/Guts/DicoShapes/)"""
    # libraries import
    from os import getcwd, chdir, path
	# test files
    li_ecw = [r'C:\\Users\julien.moura\Documents\GIS Database\ECW\0468_6740.ecw']    # ECW
    li_gtif = [r'C:\\Users\julien.moura\Documents\GIS Database\GeoTiff\BDP_07_0621_0049_020_LZ1.tif']    # GeoTIFF
    li_jpg2 = [r'C:\\Users\julien.moura\Documents\GIS Database\JPEG2000\image_jpg2000.jp2']  # JPEG2000

    li_rasters = (li_ecw[0], li_gtif[0], li_jpg2[0])

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
    # recipient datas
    dico_raster = OD()     # dictionary where will be stored informations
    dico_bands = OD()     # dictionary for fields information
    # execution
    for raster in li_rasters:
        """ looping on raster files """
        # reset recipient data
        dico_raster.clear()
        dico_bands.clear()
        # getting the informations
        if not path.isfile(raster):
        	print("\n\t==> File doesn't exist: " + raster)
        	continue
        print "\n======================\n\t", path.basename(raster)
        info_raster = InfosRasters(raster, dico_raster, dico_bands, path.splitext(raster)[1], textos)
        print '\n', dico_raster, dico_bands
