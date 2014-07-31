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
from os import chdir, path       # files and folder managing
from time import localtime, strftime

# Python 3 backported
from collections import OrderedDict as OD

# 3rd party libraries
try:
    from osgeo import gdal
    from osgeo import osr
except ImportError:
    import gdal
    import osr

from gdalconst import *

###############################################################################
########### Classes #############
###################################


class Read_Rasters():
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
        # gdal specific
        gdal.AllRegister()
        gdal.UseExceptions()
        # changing working directory to layer folder
        chdir(path.dirname(rasterpath))
        # variables
        self.alert = 0
        # opening file
        self.rast = gdal.Open(rasterpath, GA_ReadOnly)
        
        # check if raster is GDAL friendly
        if self.rast is None:
            print("\n\tUnable to open " + rasterpath)
            print("Please check compatibility.")
            self.alert += 1
        else:
            pass
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

        # dependencies
        dependencies = [path.basename(filedepend) for filedepend in self.rast.GetFileList() if filedepend != rasterpath]
        dico_raster[u'dependencies'] = dependencies

        # total size
        dependencies.append(rasterpath)
        total_size = sum([path.getsize(f) for f in dependencies])
        dico_raster[u"total_size"] = self.sizeof(total_size)
        dependencies.pop(-1)

        # format
        dico_raster[u'compr_rate'] = self.rast.GetMetadata().get('COMPRESSION_RATE_TARGET')
        dico_raster[u'color_ref'] = self.rast.GetMetadata().get('COLORSPACE')
        if self.rast.GetMetadata().get('VERSION'):
            dico_raster[u'format_version'] = "(v{})".format(self.rast.GetMetadata().get('VERSION'))
        else:
            dico_raster[u'format_version'] = ""
        # image specifications
        dico_raster[u'num_cols'] = self.rast.RasterXSize
        dico_raster[u'num_rows'] = self.rast.RasterYSize
        dico_raster[u'num_bands'] = self.rast.RasterCount

        # data type
        dico_raster[u'data_type'] = gdal.GetDataTypeName(self.rast.GetRasterBand(1).DataType)

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
        geotransform = self.rast.GetGeoTransform()
        dico_raster[u'xOrigin'] = geotransform[0]
        dico_raster[u'yOrigin'] = geotransform[3]
        dico_raster[u'pixelWidth'] = round(geotransform[1], 3)
        dico_raster[u'pixelHeight'] = round(geotransform[5], 3)
        dico_raster[u'orientation'] = geotransform[2]

            ## SRS
        # using osr to get the srs
        srs = osr.SpatialReference()
        srs.ImportFromWkt(self.rast.GetProjectionRef())
        srs.AutoIdentifyEPSG()
        # srs types
        srsmetod = [
                    (srs.IsCompound(), txt.get('srs_comp')),
                    (srs.IsGeocentric(), txt.get('srs_geoc')),
                    (srs.IsGeographic(), txt.get('srs_geog')),
                    (srs.IsLocal(), txt.get('srs_loca')),
                    (srs.IsProjected(), txt.get('srs_proj')),
                    (srs.IsVertical(), txt.get('srs_vert'))
                    ]
        # searching for a match with one of srs types
        for srsmet in srsmetod:
            if srsmet[0] == 1:
                typsrs = srsmet[1]
            else:
                continue
        # in case of not match
        try:
            dico_raster[u'srs_type'] = unicode(typsrs)
        except UnboundLocalError:
            typsrs = txt.get('srs_nr')
            dico_raster[u'srs_type'] = unicode(typsrs)

        # Handling exception in srs names'encoding
        try:
            if srs.GetAttrValue('PROJCS') is not None:
                dico_raster[u'srs'] = unicode(srs.GetAttrValue('PROJCS')).replace('_', ' ')
            else:
                dico_raster[u'srs'] = unicode(srs.GetAttrValue('PROJECTION')).replace('_', ' ')
        except UnicodeDecodeError, e:
            if srs.GetAttrValue('PROJCS') != 'unnamed':
                dico_raster[u'srs'] = srs.GetAttrValue('PROJCS').decode('latin1').replace('_', ' ')
            else:
                dico_raster[u'srs'] = srs.GetAttrValue('PROJECTION').decode('latin1').replace('_', ' ')
        dico_raster[u'EPSG'] = unicode(srs.GetAttrValue("AUTHORITY", 1))

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

    def sizeof(self, os_size):
        u""" return size in different units depending on size
        see http://stackoverflow.com/a/1094933 """
        for size_cat in ['octets', 'Ko', 'Mo', 'Go']:
            if os_size < 1024.0:
                return "%3.1f %s" % (os_size, size_cat)
            os_size /= 1024.0
        return "%3.1f %s" % (os_size, " To")

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


###############################################################################
###### Stand alone program ########
###################################

if __name__ == '__main__':
    u""" standalone execution for tests. Paths are relative considering a test
    within the official repository (https://github.com/Guts/DicoShapes/)"""
    # listing test files by formats
    li_ecw = [r'C:\\Users\julien.moura\Documents\GIS Database\ECW\0468_6740.ecw']  # ECW
    li_gtif = [r'..\test\datatest\rasters\GeoTiff\BDP_07_0621_0049_020_LZ1.tif',
               r'..\test\datatest\rasters\GeoTiff\TrueMarble_16km_2700x1350.tif']  # GeoTIFF
    li_jpg2 = [r'..\test\datatest\rasters\JPEG2000\image_jpg2000.jp2']  # JPEG2000

    li_rasters = (path.abspath(li_ecw[0]),
                  path.abspath(li_gtif[0]),
                  path.abspath(li_gtif[1]),
                  path.abspath(li_jpg2[0]))

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
        else:
            pass
        print "\n======================\n\t", path.basename(raster)
        info_raster = Read_Rasters(path.abspath(raster),
                                   dico_raster,
                                   dico_bands,
                                   path.splitext(raster)[1],
                                   textos)
        print '\n', dico_raster, dico_bands
