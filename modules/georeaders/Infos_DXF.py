# -*- coding: UTF-8 -*-
#!/usr/bin/env python
# from __future__ import unicode_literals

#------------------------------------------------------------------------------
# Name:         Infos DXF
# Purpose:      Use GDAL/OGR and dxfgrabber to read AutoCAD exchanges file format.
#
# Author:       Julien Moura (https://github.com/Guts/)
#
# Python:       2.7.x
# Created:      24/07/2014
# Updated:      13/08/2014
# Licence:      GPL 3
#------------------------------------------------------------------------------

###############################################################################
########### Libraries #############
###################################
# Standard library
from os import path, chdir, listdir   # files and folder managing
from time import localtime, strftime

# Python 3 backported
from collections import OrderedDict as OD

# 3rd party libraries
try:
    from osgeo import ogr
    from osgeo import osr
except ImportError:
    import ogr
    import osr

import dxfgrabber   # module dedicated to DXF

###############################################################################
########### Classes #############
#################################


class Read_DXF():
    def __init__(self, dxfpath, dico_dxf, tipo, txt=''):
        u""" Uses OGR functions to extract basic informations about
        geographic vector file (handles shapefile or MapInfo tables)
        and store into dictionaries.

        dxfpath = path to the DXF file
        dico_dxf = dictionary for global informations
        tipo = format
        text = dictionary of text in the selected language
        """
        # changing working directory to layer folder
        chdir(path.dirname(dxfpath))

        # raising GDAL/OGR specific exceptions
        ogr.UseExceptions()
        self.alert = 0

        # opening DXF
        dr_dxf = ogr.GetDriverByName("DXF")
        try:
            dxf = dr_dxf.Open(dxfpath, 0)
        except Exception, e:
            print e
            return

        # check if DXF is OGR friendly
        if dxf is None:
            self.alert += 1
            self.erratum(dico_dxf, dxfpath, u'err_incomp')
            return
        else:
            pass

        # DXF name and parent folder
        dico_dxf['name'] = path.basename(dxf.GetName())
        dico_dxf['folder'] = path.dirname(dxf.GetName())

        # opening
        douxef = dxfgrabber.readfile(dxfpath)

        # AutoCAD version
        dico_dxf['version_code'] = douxef.dxfversion
        # see: http://dxfgrabber.readthedocs.org/en/latest/#Drawing.dxfversion
        if douxef.dxfversion == 'AC1009':
            dico_dxf['version_name'] = 'AutoCAD R12'
        elif douxef.dxfversion == 'AC1015':
            dico_dxf['version_name'] = 'AutoCAD R2000'
        elif douxef.dxfversion == 'AC1018':
            dico_dxf['version_name'] = 'AutoCAD R2004'
        elif douxef.dxfversion == 'AC1021':
            dico_dxf['version_name'] = 'AutoCAD R2007'
        elif douxef.dxfversion == 'AC1024':
            dico_dxf['version_name'] = 'AutoCAD R2010'
        elif douxef.dxfversion == 'AC1027':
            dico_dxf['version_name'] = 'AutoCAD R2013'
        else:
            dico_dxf['version_name'] = 'NR'

        # layers count and names
        dico_dxf['layers_count'] = dxf.GetLayerCount()
        li_layers_names = []
        li_layers_idx = []
        dico_dxf['layers_names'] = li_layers_names
        dico_dxf['layers_idx'] = li_layers_idx

        # dependencies
        dependencies = [f for f in listdir(path.dirname(dxfpath))
                        if path.splitext(path.abspath(f))[0] == path.splitext(dxfpath)[0]
                        and not path.splitext(path.abspath(f).lower())[1] == ".dxf"]
        dico_dxf[u'dependencies'] = dependencies

        # cumulated size
        dependencies.append(dxfpath)
        total_size = sum([path.getsize(f) for f in dependencies])
        dico_dxf[u"total_size"] = self.sizeof(total_size)
        dependencies.pop(-1)

        # global dates
        dico_dxf[u'date_actu'] = strftime('%d/%m/%Y',
                                          localtime(path.getmtime(dxfpath)))
        dico_dxf[u'date_crea'] = strftime('%d/%m/%Y',
                                          localtime(path.getctime(dxfpath)))
        # total fields count
        total_fields = 0
        dico_dxf['total_fields'] = total_fields
        # total objects count
        total_objs = 0
        dico_dxf['total_objs'] = total_objs
        # parsing layers
        for layer_idx in range(dxf.GetLayerCount()):
            # dictionary where will be stored informations
            dico_layer = OD()
            # parent DXF
            dico_layer['dxf_name'] = path.basename(dxf.GetName())
            # getting layer object
            layer = dxf.GetLayerByIndex(layer_idx)
            # layer name
            li_layers_names.append(layer.GetName())
            # layer index
            li_layers_idx.append(layer_idx)
            # getting layer globlal informations
            self.infos_basics(layer, dico_layer, txt)
            # storing layer into the DXF dictionary
            dico_dxf['{0}_{1}'.format(layer_idx,
                                      layer.GetName())] = dico_layer
            # summing fields number
            total_fields += dico_layer.get(u'num_fields')
            # summing objects number
            total_objs += dico_layer.get(u'num_obj')
            # deleting dictionary to ensure having cleared space
            del dico_layer
        # storing fileds and objects sum
        dico_dxf['total_fields'] = total_fields
        dico_dxf['total_objs'] = total_objs

    def infos_basics(self, layer_obj, dico_layer, txt):
        u""" get the global informations about the layer """
        # title and features count
        dico_layer[u'title'] = layer_obj.GetName()
        dico_layer[u'num_obj'] = layer_obj.GetFeatureCount()

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
        if srs:
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
                if srs.GetAttrValue('PROJCS') != 'unnamed':
                    dico_layer[u'srs'] = unicode(srs.GetAttrValue('PROJCS')).replace('_', ' ')
                else:
                    dico_layer[u'srs'] = unicode(srs.GetAttrValue('PROJECTION')).replace('_', ' ')
            except UnicodeDecodeError:
                if srs.GetAttrValue('PROJCS') != 'unnamed':
                    dico_layer[u'srs'] = srs.GetAttrValue('PROJCS').decode('latin1').replace('_', ' ')
                else:
                    dico_layer[u'srs'] = srs.GetAttrValue('PROJECTION').decode('latin1').replace('_', ' ')
            finally:
                dico_layer[u'EPSG'] = unicode(srs.GetAttrValue("AUTHORITY", 1))

            # World SRS default
            if dico_layer[u'EPSG'] == u'4326' and dico_layer[u'srs'] == u'None':
                dico_layer[u'srs'] = u'WGS 84'
            else:
                pass
        else:
            typsrs = txt.get('srs_nr')
            dico_layer[u'srs_type'] = unicode(typsrs)

        # first feature and geometry type
        try:
            first_obj = layer_obj.GetFeature(1)
            geom = first_obj.GetGeometryRef()
        except AttributeError, e:
            print e, layer_obj.GetName()
            first_obj = layer_obj.GetNextFeature()
            geom = first_obj.GetGeometryRef()

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

    def sizeof(self, os_size):
        u""" return size in different units depending on size
        see http://stackoverflow.com/a/1094933 """
        for size_cat in ['octets', 'Ko', 'Mo', 'Go']:
            if os_size < 1024.0:
                return "%3.1f %s" % (os_size, size_cat)
            os_size /= 1024.0
        return "%3.1f %s" % (os_size, " To")


    def erratum(self, dico_dxf, dxfpath, mess):
        u""" errors handling """
        # storing minimal informations to give clues to solve later
        dico_dxf[u'name'] = path.basename(dxfpath)
        dico_dxf[u'folder'] = path.dirname(dxfpath)
        dico_dxf[u'error'] = mess
        # End of function
        return dico_dxf

###############################################################################
###### Stand alone program ########
###################################

if __name__ == '__main__':
    u""" standalone execution for tests. Paths are relative considering a test
    within the official repository (https://github.com/Guts/DicoGIS/)"""
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

    # searching for DX Files
    num_folders = 0
    li_dxf = [r'..\test\datatest\cao\dxf\paris_transports_ed.dxf']
    
    # recipient datas
    dico_dxf = OD()
    
    # read DXF
    for dxfpath in li_dxf:
        dico_dxf.clear()
        dxfpath = path.abspath(dxfpath)
        if path.isfile(dxfpath):
            print("\n{0}: ".format(dxfpath))
            Read_DXF(dxfpath,
                     dico_dxf,
                     'AutoCAD DXF',
                     textos)
            # print results
            print(dico_dxf)
        else:
            pass
