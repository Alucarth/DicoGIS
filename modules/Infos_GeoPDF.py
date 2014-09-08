# -*- coding: UTF-8 -*-
#!/usr/bin/env python
# from __future__ import unicode_literals

#------------------------------------------------------------------------------
# Name:         Infos Geospatial PDF
# Purpose:      Use GDAL/OGR library to extract informations about
#                   geographic data. It permits a more friendly use as
#                   submodule.
#
# Author:       Julien Moura (https://github.com/Guts/)
#
# Python:       2.7.x
# Created:      18/02/2014
# Updated:      08/09/2014
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
    from osgeo import ogr
    from osgeo import osr
    from osgeo.gdalconst import *
except ImportError:
    import gdal
    import ogr
    import osr
    from gdalconst import *

##############################################################
############ Classes ##############
###################################


class GdalErrorHandler(object):
    def __init__(self):
        """ Callable error handler
        see: http://trac.osgeo.org/gdal/wiki/PythonGotchas#Exceptionsraisedincustomerrorhandlersdonotgetcaught
        and http://pcjericks.github.io/py-gdalogr-cookbook/gdal_general.html#install-gdal-ogr-error-handler
        """
        self.err_level = gdal.CE_None
        self.err_type = 0
        self.err_msg = ''

    def handler(self, err_level, err_type, err_msg):
        """ Making errors messages more readable """
        # available types
        err_class = {
                    gdal.CE_None: 'None',
                    gdal.CE_Debug: 'Debug',
                    gdal.CE_Warning: 'Warning',
                    gdal.CE_Failure: 'Failure',
                    gdal.CE_Fatal: 'Fatal'
                    }
        # getting type
        err_type = err_class.get(err_type, 'None')
        
        # cleaning message
        err_msg = err_msg.replace('\n', ' ')

        # disabling GDAL exceptions raising to avoid future troubles
        gdal.DontUseExceptions()

        # propagating
        self.err_level = err_level
        self.err_type = err_type
        self.err_msg = err_msg

        # end of function
        return self.err_level, self.err_type, self.err_msg


class Read_GeoPDF(object):
    def __init__(self, pdfpath, dico_geopdf, tipo='pdf', txt=''):
        u""" Uses GDAL & OGR functions to extract basic
        informations about geographic PDF file and store into dictionaries.

        layerpath = path to the geographic file
        dico_geopdf = dictionary for global informations
        dico_bands = dictionary for the bands informations
        txt = dictionary of txt in the selected language
        """
        # gdal specific
        gdal.AllRegister()
        # changing working directory to layer folder
        chdir(path.dirname(pdfpath))
        pdfpath = path.abspath(pdfpath)
        
        # handling specific exceptions
        gdalerr = GdalErrorHandler()
        errhandler = gdalerr.handler
        gdal.PushErrorHandler(errhandler)
        self.alert = 0
        # gdal.SetConfigOption(str("GTIFF_IGNORE_READ_ERRORS"), str("TRUE"))
        gdal.UseExceptions()

        # opening file
        try:
            self.geopdf = gdal.Open(pdfpath, GA_ReadOnly)
        except Exception, e:
            print e
            self.alert += 1
            self.erratum(dico_geopdf, pdfpath, u'err_incomp')
            return

        # check if PDF is GDAL friendly
        if self.geopdf is None:
            self.alert += 1
            self.erratum(dico_geopdf, pdfpath, u'err_incomp')
            return
        else:
            pass
        # basic informations
        dico_geopdf[u'format'] = tipo
        self.raster_basics(pdfpath, dico_geopdf, txt)
        # geometry information
        self.infos_geom(dico_geopdf, txt)
        # bands information
        for band_idx in range(1, self.geopdf.RasterCount):
            # new dict to store band informations
            dico_band = OD()
            # getting band infos
            self.infos_bands(band_idx, dico_band)
            # storing band into the PDF dictionary
            dico_geopdf['band_{0}'.format(band_idx)] = dico_band
            # deleting dict object
            del(dico_band)

        # safe close (see: http://pcjericks.github.io/py-gdalogr-cookbook/)
        del self.geopdf
        # warnings messages
        dico_geopdf['err_gdal'] = gdalerr.err_type, gdalerr.err_msg

        ###### READING INTO VECTORS LAYERS
        ogr.UseExceptions()
        try:
            geopdf_v = ogr.Open(pdfpath)
        except Exception:
            self.erratum(dico_geopdf, pdfpath, u'err_corrupt')
            self.alert = self.alert + 1
            return None

        # layers count and names
        dico_geopdf['layers_count'] = geopdf_v.GetLayerCount()
        li_layers_names = []
        li_layers_idx = []
        dico_geopdf['layers_names'] = li_layers_names
        dico_geopdf['layers_idx'] = li_layers_idx


        # total fields count
        total_fields = 0
        dico_geopdf['total_fields'] = total_fields
        # total objects count
        total_objs = 0
        dico_geopdf['total_objs'] = total_objs
        # parsing layers
        for layer_idx in range(geopdf_v.GetLayerCount()):
            # dictionary where will be stored informations
            dico_layer = OD()
            # parent GDB
            dico_layer['parent_name'] = path.basename(geopdf_v.GetName())
            # getting layer object
            layer = geopdf_v.GetLayerByIndex(layer_idx)
            # layer name
            li_layers_names.append(layer.GetName())
            # layer index
            li_layers_idx.append(layer_idx)
            # getting layer globlal informations
            self.vector_basics(layer, dico_layer, txt)
            # storing layer into the GDB dictionary
            dico_geopdf['{0}_{1}'.format(layer_idx,
                                         layer.GetName())] = dico_layer
            # summing fields number
            total_fields += dico_layer.get(u'num_fields')
            # summing objects number
            total_objs += dico_layer.get(u'num_obj')
            # deleting dictionary to ensure having cleared space
            del dico_layer
        # storing fileds and objects sum
        dico_geopdf['total_fields'] = total_fields
        dico_geopdf['total_objs'] = total_objs

    def raster_basics(self, pdfpath, dico_geopdf, txt):
        u""" get the global informations about the PDF """
        # files and folder
        dico_geopdf[u'name'] = path.basename(pdfpath)
        dico_geopdf[u'folder'] = path.dirname(pdfpath)
        dico_geopdf[u'title'] = dico_geopdf[u'name'][:-4].replace('_', ' ')\
                                                         .capitalize()

        # dependencies
        dependencies = [path.basename(filedepend) for filedepend in
                        self.geopdf.GetFileList() if filedepend != pdfpath]
        dico_geopdf[u'dependencies'] = dependencies

        # total size
        dependencies.append(pdfpath)
        total_size = sum([path.getsize(f) for f in dependencies])
        dico_geopdf[u"total_size"] = self.sizeof(total_size)
        dependencies.pop(-1)

        # metadata
        geopdf_MD = self.geopdf.GetMetadata()
        print(geopdf_MD.keys())
        dico_geopdf[u'title'] = geopdf_MD.get('TITLE')
        dico_geopdf[u'creator'] = geopdf_MD.get('CREATOR')
        dico_geopdf[u'producer'] = geopdf_MD.get('PRODUCER')
        dico_geopdf[u'date_crea'] = geopdf_MD.get('CREATION_DATE')
        dico_geopdf[u'keywords'] = geopdf_MD.get('KEYWORDS')
        dico_geopdf[u'dpi'] = geopdf_MD.get('DPI')
        dico_geopdf[u'subject'] = geopdf_MD.get('SUBJECT')
        dico_geopdf[u'neatline'] = geopdf_MD.get('NEATLINE')
        dico_geopdf['description'] = self.geopdf.GetDescription()

        # image specifications
        dico_geopdf[u'num_cols'] = self.geopdf.RasterXSize
        dico_geopdf[u'num_rows'] = self.geopdf.RasterYSize
        dico_geopdf[u'num_bands'] = self.geopdf.RasterCount

        # data type
        dico_geopdf[u'data_type'] = gdal.GetDataTypeName(self.geopdf.GetRasterBand(1).DataType)

        # subdatasets count
        dico_geopdf[u'subdatasets_count'] = len(self.geopdf.GetSubDatasets())

        # GCPs
        dico_geopdf[u'gcp_count'] = self.geopdf.GetGCPCount()

        # basic dates
        dico_geopdf[u'date_actu'] = strftime('%d/%m/%Y',
                                             localtime(path.getmtime(pdfpath)))

        # end of function
        return dico_geopdf

    def vector_basics(self, layer_obj, dico_layer, txt):
        u""" get the global informations about the layer """
        # title and features count
        dico_layer[u'title'] = layer_obj.GetName()
        dico_layer[u'num_obj'] = layer_obj.GetFeatureCount()

        # getting geography and geometry informations
        # srs = layer_obj.GetSpatialRef()
        # self.infos_geos(layer_obj, srs, dico_layer, txt)

        # getting fields informations
        dico_fields = OD()
        layer_def = layer_obj.GetLayerDefn()
        dico_layer['num_fields'] = layer_def.GetFieldCount()
        self.infos_fields(layer_def, dico_fields)
        dico_layer['fields'] = dico_fields

        # end of function
        return dico_layer

    def infos_geom(self, dico_geopdf, txt):
        u""" get the informations about geometry """
        # Spatial extent (bounding box)
        geotransform = self.geopdf.GetGeoTransform()
        dico_geopdf[u'xOrigin'] = geotransform[0]
        dico_geopdf[u'yOrigin'] = geotransform[3]
        dico_geopdf[u'pixelWidth'] = round(geotransform[1], 3)
        dico_geopdf[u'pixelHeight'] = round(geotransform[5], 3)
        dico_geopdf[u'orientation'] = geotransform[2]

            ## SRS
        # using osr to get the srs
        srs = osr.SpatialReference(self.geopdf.GetProjection())
        # srs.ImportFromWkt(self.geopdf.GetProjection())
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
            dico_geopdf[u'srs_type'] = unicode(typsrs)
        except UnboundLocalError:
            typsrs = txt.get('srs_nr')
            dico_geopdf[u'srs_type'] = unicode(typsrs)

        # Handling exception in srs names'encoding
        if srs.IsProjected():
            try:
                if srs.GetAttrValue('PROJCS') is not None:
                    dico_geopdf[u'srs'] = unicode(srs.GetAttrValue('PROJCS')).replace('_', ' ')
                else:
                    dico_geopdf[u'srs'] = unicode(srs.GetAttrValue('PROJECTION')).replace('_', ' ')
            except UnicodeDecodeError:
                if srs.GetAttrValue('PROJCS') != 'unnamed':
                    dico_geopdf[u'srs'] = srs.GetAttrValue('PROJCS').decode('latin1').replace('_', ' ')
                else:
                    dico_geopdf[u'srs'] = srs.GetAttrValue('PROJECTION').decode('latin1').replace('_', ' ')
        else:
            try:
                if srs.GetAttrValue('GEOGCS') is not None:
                    dico_geopdf[u'srs'] = unicode(srs.GetAttrValue('GEOGCS')).replace('_', ' ')
                else:
                    dico_geopdf[u'srs'] = unicode(srs.GetAttrValue('PROJECTION')).replace('_', ' ')
            except UnicodeDecodeError:
                if srs.GetAttrValue('GEOGCS') != 'unnamed':
                    dico_geopdf[u'srs'] = srs.GetAttrValue('GEOGCS').decode('latin1').replace('_', ' ')
                else:
                    dico_geopdf[u'srs'] = srs.GetAttrValue('PROJECTION').decode('latin1').replace('_', ' ')
        
        dico_geopdf[u'EPSG'] = unicode(srs.GetAttrValue("AUTHORITY", 1))

        # end of function
        return dico_geopdf

    def infos_bands(self, band, dico_bands):
        u""" get the informations about fields definitions """
        # getting band object
        band_info = self.geopdf.GetRasterBand(band)

        # band statistics
        try:
            stats = band_info.GetStatistics(True, True)
        except:
            return
        if stats:
            # band minimum value
            if band_info.GetMinimum() is None:
                dico_bands["band{}_Min".format(band)] = stats[0]
            else:
                dico_bands["band{}_Min".format(band)] = band_info.GetMinimum()
            
            # band maximum value
            if band_info.GetMinimum() is None:
                dico_bands["band{}_Max".format(band)] = stats[1]
            else:
                dico_bands["band{}_Max".format(band)] = band_info.GetMaximum()

            # band mean value
            dico_bands["band{}_Mean".format(band)] = round(stats[2], 2)

            # band standard deviation value
            dico_bands["band{}_Sdev".format(band)] = round(stats[3], 2)
        else:
            pass

        # band no data value
        dico_bands["band{}_NoData".format(band)] = band_info.GetNoDataValue()

        # band scale value
        dico_bands["band{}_Scale".format(band)] = band_info.GetScale()

        # band unit type value
        dico_bands["band{}_UnitType".format(band)] = band_info.GetUnitType()

        # color table
        coul_table = band_info.GetColorTable()
        if coul_table is None:
            dico_bands["band{}_CTabCount".format(band)] = 0
        else:
            dico_bands["band{}_CTabCount".format(band)] = coul_table.GetCount()
            #### COMENTED BECAUSE IT'S TOO MUCH INFORMATIONS
            # for ctab_idx in range(0, coul_table.GetCount()):
            #     entry = coul_table.GetColorEntry(ctab_idx)
            #     if not entry:
            #         continue
            #     else:
            #         pass
            #     dico_bands["band{0}_CTab{1}_RGB".format(band, ctab_idx)] = \
            #                   coul_table.GetColorEntryAsRGB(ctab_idx, entry)

        # safe close (quite useless but good practice to have)
        del stats
        del band_info

        # end of function
        return dico_bands

    def infos_fields(self, layer_def, dico_fields):
        u""" get the informations about fields definitions """
        for i in range(layer_def.GetFieldCount()):
            champomy = layer_def.GetFieldDefn(i)  # fields ordered
            dico_fields[champomy.GetName()] = champomy.GetTypeName()
                                              
        # end of function
        return dico_fields

    def sizeof(self, os_size):
        u""" return size in different units depending on size
        see http://stackoverflow.com/a/1094933 """
        for size_cat in ['octets', 'Ko', 'Mo', 'Go']:
            if os_size < 1024.0:
                return "%3.1f %s" % (os_size, size_cat)
            os_size /= 1024.0
        return "%3.1f %s" % (os_size, " To")

    def erratum(self, dico_geopdf, pdfpath, mess):
        u""" errors handling """
        # storing minimal informations to give clues to solve later
        dico_geopdf[u'name'] = path.basename(pdfpath)
        dico_geopdf[u'folder'] = path.dirname(pdfpath)
        dico_geopdf[u'error'] = mess
        # End of function
        return dico_geopdf

###############################################################################
###### Stand alone program ########
###################################

if __name__ == '__main__':
    u""" standalone execution for tests. Paths are relative considering a test
    within the official repository (https://github.com/Guts/GIS)"""
    # test files
    chdir(r'..\test\datatest\pdf')
    li_pdf = [r'US_Country_Populations.pdf',
              r'Advanced_geospatial_PDF_made_with_GDAL.pdf',
              r'Geospatial_OpenStreetMap_vector_and_raster_map.pdf',
              r'NC_Windsor_North_20110909_TM_geo.pdf']
    
    # test txt dictionary
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
    dico_pdf = OD()     # dictionary where will be stored informations
    # execution
    for pdf in li_pdf:
        """ looping on pdf files """
        # reset recipient data
        dico_pdf.clear()
        # get the absolute path
        pdf = path.abspath(pdf)
        # getting the informations
        if not path.isfile(pdf):
            print("\n\t==> File doesn't exist: " + pdf)
            continue
        print "\n======================\n\t", path.basename(pdf)
        info_pdf = Read_GeoPDF(pdf,
                               dico_pdf,
                               path.splitext(pdf)[1],
                               textos)
        print '\n', dico_pdf
