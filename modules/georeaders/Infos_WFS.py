# -*- coding: UTF-8 -*-
#!/usr/bin/env python
from __future__ import unicode_literals

#------------------------------------------------------------------------------
# Name:         InfosWFS
# Purpose:      Uses OGR to read OGC Web Features Service.
#
# Author:       Julien Moura (https://github.com/Guts/)
#
# Python:       2.7.x
# Created:      24/04/2015
# Updated:      11/05/2015
# Licence:      GPL 3
#------------------------------------------------------------------------------

###############################################################################
########### Libraries #############
###################################
# Standard library
from os import path, walk   # files and folder managing
from time import localtime, strftime
import sys

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

from owslib.wfs import WebFeatureService

###############################################################################
########### Classes #############
#################################


class OGRErrorHandler(object):
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

        # disabling OGR exceptions raising to avoid future troubles
        ogr.DontUseExceptions()

        # propagating
        self.err_level = err_level
        self.err_type = err_type
        self.err_msg = err_msg

        # end of function
        return self.err_level, self.err_type, self.err_msg


class ReadWFS_OGR():
    def __init__(self, wfsUrl, dico_wfs, tipo, txt=''):
        u""" Uses OGR functions to extract basic informations about
        geographic Web Features Services.

        wfsUrl = url of a WFS service
        dico_wfs = dictionary for global informations
        dico_fields = dictionary for the fields' informations
        li_fieds = ordered list of fields
        tipo = format
        text = dictionary of text in the selected language

        """
        # handling ogr specific exceptions
        ogrerr = OGRErrorHandler()
        errhandler = ogrerr.handler
        gdal.PushErrorHandler(errhandler)
        ogr.UseExceptions()

        # custom settings to enhance querying WFS capabilities for services with a lot of layers
        gdal.SetConfigOption(str('OGR_WFS_LOAD_MULTIPLE_LAYER_DEFN'), str('NO'))
        gdal.SetConfigOption(str('OGR_WFS_BASE_START_INDEX'), str(1))

        # Set config for paging. Works on WFS 2.0 services and WFS 1.0 and 1.1 with some other services.
        # gdal.SetConfigOption(str('OGR_WFS_PAGING_ALLOWED'), str('YES'))
        # gdal.SetConfigOption(str('OGR_WFS_PAGE_SIZE'), str('5'))

        # counting alerts
        self.alert = 0

        # opening GDB
        try:
            drv_wfs = ogr.GetDriverByName(str('WFS'))
            wfs = drv_wfs.Open(str('WFS:') + str(wfsUrl))
        except Exception:
            self.erratum(dico_wfs, wfsUrl, u'err_corrupt')
            self.alert = self.alert + 1
            return None

        # GDB name and parent folder
        dico_wfs['name'] = wfs.GetName()
        dico_wfs['folder'] = path.dirname(wfs.GetName())
        # layers count and names
        dico_wfs['layers_count'] = wfs.GetLayerCount()
        li_layers_names = []
        li_layers_idx = []
        dico_wfs['layers_names'] = li_layers_names
        dico_wfs['layers_idx'] = li_layers_idx

        # total fields count
        total_fields = 0
        dico_wfs['total_fields'] = total_fields
        # total objects count
        total_objs = 0
        dico_wfs['total_objs'] = total_objs
        # parsing layers
        for layer_idx in range(wfs.GetLayerCount()):
            # dictionary where will be stored informations
            dico_layer = OD()
            # parent GDB
            dico_layer['wfs_name'] = path.basename(wfs.GetName())
            # getting layer object
            layer = wfs.GetLayerByIndex(layer_idx)
            # layer name
            li_layers_names.append(layer.GetName())
            # layer index
            li_layers_idx.append(layer_idx)
            # getting layer globlal informations
            self.infos_basics(layer, dico_layer, txt)
            # storing layer into the GDB dictionary
            dico_wfs['{0}_{1}'.format(layer_idx,
                                      dico_layer.get('title'))] = dico_layer
            # summing fields number
            total_fields += dico_layer.get(u'num_fields')
            # summing objects number
            total_objs += dico_layer.get(u'num_obj')
            # deleting dictionary to ensure having cleared space
            del dico_layer
        # storing fileds and objects sum
        dico_wfs['total_fields'] = total_fields
        dico_wfs['total_objs'] = total_objs

        # warnings messages
        dico_wfs['err_gdal'] = ogrerr.err_type, ogrerr.err_msg

    def infos_basics(self, layer_obj, dico_layer, txt):
        u""" get the global informations about the layer """
        # title
        try:
            dico_layer[u'title'] = unicode(layer_obj.GetName())
        except UnicodeDecodeError:
            layerName = layer_obj.GetName().decode('latin1', errors='replace')
            dico_layer[u'title'] = layerName

        # features count
        dico_layer[u'num_obj'] = layer_obj.GetFeatureCount()

        print dico_layer

        if layer_obj.GetFeatureCount() == 0:
            u""" if layer doesn't have any object, return an error """
            dico_layer[u'error'] = u'err_nobjet'
            self.alert = self.alert + 1
        else:
            # getting geography and geometry informations
            srs = layer_obj.GetSpatialRef()
            self.infos_geos(layer_obj, srs, dico_layer, txt)

        # getting fields informations
        dico_fields = OD()
        layer_def = layer_obj.GetLayerDefn()
        dico_layer['num_fields'] = layer_def.GetFieldCount()
        self.infos_fields(layer_def, dico_fields)
        dico_layer['fields'] = dico_fields

        # end of function
        return dico_layer

    def infos_geos(self, layer_obj, srs, dico_layer, txt):
        u""" get the informations about geography and geometry """
        # SRS
        srs.AutoIdentifyEPSG()
        # srs type
        srsmetod = [(srs.IsCompound(), txt.get('srs_comp')),
                    (srs.IsGeocentric(), txt.get('srs_geoc')),
                    (srs.IsGeographic(), txt.get('srs_geog')),
                    (srs.IsLocal(), txt.get('srs_loca')),
                    (srs.IsProjected(), txt.get('srs_proj')),
                    (srs.IsVertical(), txt.get('srs_vert'))]
        # searching for a match with one of srs types
        for srsmet in srsmetod:
            if srsmet[0] == 1:
                typsrs = srsmet[1]
            else:
                continue
        # in case of not match
        try:
            dico_layer[u'srs_type'] = unicode(typsrs)
        except UnboundLocalError:
            typsrs = txt.get('srs_nr')
            dico_layer[u'srs_type'] = unicode(typsrs)

        # handling exceptions in srs names'encoding
        try:
            if srs.GetAttrValue(str('PROJCS')) != 'unnamed':
                dico_layer[u'srs'] = unicode(srs.GetAttrValue(str('PROJCS'))).replace('_', ' ')
            else:
                dico_layer[u'srs'] = unicode(srs.GetAttrValue(str('PROJECTION'))).replace('_', ' ')
        except UnicodeDecodeError:
            if srs.GetAttrValue(str('PROJCS')) != 'unnamed':
                dico_layer[u'srs'] = srs.GetAttrValue(str('PROJCS')).decode('latin1').replace('_', ' ')
            else:
                dico_layer[u'srs'] = srs.GetAttrValue(str('PROJECTION')).decode('latin1').replace('_', ' ')
        finally:
            dico_layer[u'EPSG'] = unicode(srs.GetAttrValue(str("AUTHORITY"), 1))

        # World SRS default
        if dico_layer[u'EPSG'] == u'4326' and dico_layer[u'srs'] == u'None':
            dico_layer[u'srs'] = u'WGS 84'
        else:
            pass

        # first feature and geometry type
        try:
            first_obj = layer_obj.GetNextFeature()
            geom = first_obj.GetGeometryRef()
        except AttributeError, e:
            print e, layer_obj.GetName(), layer_obj.GetFeatureCount(), layer_obj.GetGeomType()
            return
        else:
            pass

        # geometry type human readable
        if geom.GetGeometryName() == u'POINT':
            dico_layer[u'type_geom'] = txt.get('geom_point')
        elif u'LINESTRING' in geom.GetGeometryName():
            dico_layer[u'type_geom'] = txt.get('geom_ligne')
        elif u'POLYGON' in geom.GetGeometryName():
            dico_layer[u'type_geom'] = txt.get('geom_polyg')
        else:
            dico_layer[u'type_geom'] = geom.GetGeometryName()

        # spatial extent (bounding box)
        dico_layer[u'Xmin'] = round(layer_obj.GetExtent()[0], 2)
        dico_layer[u'Xmax'] = round(layer_obj.GetExtent()[1], 2)
        dico_layer[u'Ymin'] = round(layer_obj.GetExtent()[2], 2)
        dico_layer[u'Ymax'] = round(layer_obj.GetExtent()[3], 2)

        # end of function
        return dico_layer

    def infos_fields(self, layer_def, dico_fields):
        u""" get the informations about fields definitions """
        for i in range(layer_def.GetFieldCount()):
            champomy = layer_def.GetFieldDefn(i)  # fields ordered
            dico_fields[champomy.GetName()] = champomy.GetTypeName()
        # end of function
        return dico_fields

    def erratum(self, dico_wfs, wfsUrl, mess):
        u""" errors handling """
        # local variables
        dico_wfs[u'name'] = path.basename(wfsUrl)
        dico_wfs[u'folder'] = path.dirname(wfsUrl)
        try:
            def_couche = self.layer.GetLayerDefn()
            dico_wfs[u'num_fields'] = def_couche.GetFieldCount()
        except AttributeError:
            mess = mess
        finally:
            dico_wfs[u'error'] = mess
            dico_wfs[u'layers_count'] = 0
        # End of function
        return dico_wfs


class ReadWFS_OWS():
    def __init__(self, wfsUrl, dico_wfs, tipo, txt=''):
        u""" Uses OWSLib to extract basic informations about
        geographic Web Features Services.

        wfsUrl = url of a WFS service
        dico_wfs = dictionary for global informations
        dico_fields = dictionary for the fields' informations
        li_fieds = ordered list of fields
        tipo = format
        text = dictionary of text in the selected language

        """
        # counting alerts
        self.alert = 0

        # opening WFS
        try:
            wfs = WebFeatureService(WFS_URL, version="2.0.0")
        except AttributeError:
            wfs = WebFeatureService(WFS_URL, version="1.1.0")
        except Exception:
            self.erratum(dico_wfs, wfsUrl, u'err_corrupt')
            self.alert = self.alert + 1
            return None

        # WFS identification
        dico_wfs['name'] = wfs.identification.title
        dico_wfs['url'] = wfs.url
        dico_wfs['format'] = wfs.identification.type + wfs.version
        dico_wfs['description'] = wfs.abstract
        dico_wfs['keywords'] = wfs.keywords

        # layers count and names
        dico_wfs['layers_count'] = len(wfs.contents)
        li_layers_names = []
        li_layers_idx = []
        dico_wfs['layers_names'] = li_layers_names
        dico_wfs['layers_idx'] = li_layers_idx

        # total fields count
        total_fields = 0
        dico_wfs['total_fields'] = total_fields
        # total objects count
        total_objs = 0
        dico_wfs['total_objs'] = total_objs
        # parsing layers
        for layer_idx in range(wfs.GetLayerCount()):
            # dictionary where will be stored informations
            dico_layer = OD()
            # parent GDB
            dico_layer['wfs_name'] = path.basename(wfs.GetName())
            # getting layer object
            layer = wfs.GetLayerByIndex(layer_idx)
            # layer name
            li_layers_names.append(layer.GetName())
            # layer index
            li_layers_idx.append(layer_idx)
            # getting layer globlal informations
            self.infos_basics(layer, dico_layer, txt)
            # storing layer into the GDB dictionary
            dico_wfs['{0}_{1}'.format(layer_idx,
                                      dico_layer.get('title'))] = dico_layer
            # summing fields number
            total_fields += dico_layer.get(u'num_fields')
            # summing objects number
            total_objs += dico_layer.get(u'num_obj')
            # deleting dictionary to ensure having cleared space
            del dico_layer
        # storing fileds and objects sum
        dico_wfs['total_fields'] = total_fields
        dico_wfs['total_objs'] = total_objs

        # warnings messages
        dico_wfs['err_gdal'] = ogrerr.err_type, ogrerr.err_msg

    def infos_basics(self, layer_obj, dico_layer, txt):
        u""" get the global informations about the layer """
        # title
        try:
            dico_layer[u'title'] = unicode(layer_obj.GetName())
        except UnicodeDecodeError:
            layerName = layer_obj.GetName().decode('latin1', errors='replace')
            dico_layer[u'title'] = layerName

        # features count
        dico_layer[u'num_obj'] = layer_obj.GetFeatureCount()

        print dico_layer

        if layer_obj.GetFeatureCount() == 0:
            u""" if layer doesn't have any object, return an error """
            dico_layer[u'error'] = u'err_nobjet'
            self.alert = self.alert + 1
        else:
            # getting geography and geometry informations
            srs = layer_obj.GetSpatialRef()
            self.infos_geos(layer_obj, srs, dico_layer, txt)

        # getting fields informations
        dico_fields = OD()
        layer_def = layer_obj.GetLayerDefn()
        dico_layer['num_fields'] = layer_def.GetFieldCount()
        self.infos_fields(layer_def, dico_fields)
        dico_layer['fields'] = dico_fields

        # end of function
        return dico_layer

    def infos_geos(self, layer_obj, srs, dico_layer, txt):
        u""" get the informations about geography and geometry """
        # SRS
        srs.AutoIdentifyEPSG()
        # srs type
        srsmetod = [(srs.IsCompound(), txt.get('srs_comp')),
                    (srs.IsGeocentric(), txt.get('srs_geoc')),
                    (srs.IsGeographic(), txt.get('srs_geog')),
                    (srs.IsLocal(), txt.get('srs_loca')),
                    (srs.IsProjected(), txt.get('srs_proj')),
                    (srs.IsVertical(), txt.get('srs_vert'))]
        # searching for a match with one of srs types
        for srsmet in srsmetod:
            if srsmet[0] == 1:
                typsrs = srsmet[1]
            else:
                continue
        # in case of not match
        try:
            dico_layer[u'srs_type'] = unicode(typsrs)
        except UnboundLocalError:
            typsrs = txt.get('srs_nr')
            dico_layer[u'srs_type'] = unicode(typsrs)

        # handling exceptions in srs names'encoding
        try:
            if srs.GetAttrValue(str('PROJCS')) != 'unnamed':
                dico_layer[u'srs'] = unicode(srs.GetAttrValue(str('PROJCS'))).replace('_', ' ')
            else:
                dico_layer[u'srs'] = unicode(srs.GetAttrValue(str('PROJECTION'))).replace('_', ' ')
        except UnicodeDecodeError:
            if srs.GetAttrValue(str('PROJCS')) != 'unnamed':
                dico_layer[u'srs'] = srs.GetAttrValue(str('PROJCS')).decode('latin1').replace('_', ' ')
            else:
                dico_layer[u'srs'] = srs.GetAttrValue(str('PROJECTION')).decode('latin1').replace('_', ' ')
        finally:
            dico_layer[u'EPSG'] = unicode(srs.GetAttrValue(str("AUTHORITY"), 1))

        # World SRS default
        if dico_layer[u'EPSG'] == u'4326' and dico_layer[u'srs'] == u'None':
            dico_layer[u'srs'] = u'WGS 84'
        else:
            pass

        # first feature and geometry type
        try:
            first_obj = layer_obj.GetNextFeature()
            geom = first_obj.GetGeometryRef()
        except AttributeError, e:
            print e, layer_obj.GetName(), layer_obj.GetFeatureCount(), layer_obj.GetGeomType()
            return
        else:
            pass

        # geometry type human readable
        if geom.GetGeometryName() == u'POINT':
            dico_layer[u'type_geom'] = txt.get('geom_point')
        elif u'LINESTRING' in geom.GetGeometryName():
            dico_layer[u'type_geom'] = txt.get('geom_ligne')
        elif u'POLYGON' in geom.GetGeometryName():
            dico_layer[u'type_geom'] = txt.get('geom_polyg')
        else:
            dico_layer[u'type_geom'] = geom.GetGeometryName()

        # spatial extent (bounding box)
        dico_layer[u'Xmin'] = round(layer_obj.GetExtent()[0], 2)
        dico_layer[u'Xmax'] = round(layer_obj.GetExtent()[1], 2)
        dico_layer[u'Ymin'] = round(layer_obj.GetExtent()[2], 2)
        dico_layer[u'Ymax'] = round(layer_obj.GetExtent()[3], 2)

        # end of function
        return dico_layer

    def infos_fields(self, layer_def, dico_fields):
        u""" get the informations about fields definitions """
        for i in range(layer_def.GetFieldCount()):
            champomy = layer_def.GetFieldDefn(i)  # fields ordered
            dico_fields[champomy.GetName()] = champomy.GetTypeName()
        # end of function
        return dico_fields

    def erratum(self, dico_wfs, wfsUrl, mess):
        u""" errors handling """
        # local variables
        dico_wfs[u'name'] = path.basename(wfsUrl)
        dico_wfs[u'folder'] = path.dirname(wfsUrl)
        try:
            def_couche = self.layer.GetLayerDefn()
            dico_wfs[u'num_fields'] = def_couche.GetFieldCount()
        except AttributeError:
            mess = mess
        finally:
            dico_wfs[u'error'] = mess
            dico_wfs[u'layers_count'] = 0
        # End of function
        return dico_wfs
###############################################################################
###### Stand alone program ########
###################################

if __name__ == '__main__':
    u""" standalone execution for tests. Paths are relative considering a test
    within the official repository (https://github.com/Guts/DicoGIS/)"""
    from urllib2 import urlopen
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

    # listing WFS
    li_wfs = [
              r"http://noisy.hq.isogeo.fr:6090/geoserver/Isogeo/ows",
              r"http://ws.carmencarto.fr/WFS/119/fxx_inpn?service=wfs",
              r"http://demo.mapserver.org/cgi-bin/wfs?request=getCapabilities&service=WFS"
              ]
    
    # recipient datas
    dico_wfs = OD()

    # read WFS
    for wfsUrl in li_wfs:
        dico_wfs.clear()
        if urlopen(wfsUrl):
            print("\n{0}: ".format(wfsUrl))
            ReadWFS(wfsUrl,
                    dico_wfs,
                    'OGC WFS',
                    textos)
            # print results
            print(dico_wfs)
        else:
            print("Invalid URL: {0}".format(wfsUrl))
            pass
