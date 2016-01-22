# -*- coding: UTF-8 -*-
#!/usr/bin/env python
# from __future__ import unicode_literals

#------------------------------------------------------------------------------
# Name:         Infos LYR
# Purpose:      Get some metadata abour LYR files (Esri symbology layer))
#
# Author:       Julien Moura (https://github.com/Guts/)
#
# Python:       2.7.x
# Created:      28/09/2015
# Updated:      12/10/2015
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
    from arcpy import env as enviro, Describe
    from arcpy import GetCount_management as obj_count, ListFields
    from arcpy.mapping import Layer, ListLayers
    from arcpy.da import SearchCursor
except ImportError:
    print("Mmmm, something's wrong with arcpy!")

###############################################################################
########### Classes #############
#################################

class Read_LYR():
    def __init__(self, lyr_path, dico_lyr, tipo, txt=''):
        u""" Uses OGR functions to extract basic informations about
        geographic vector file (handles shapefile or MapInfo tables)
        and store into dictionaries.

        lyrpath = path to the LYR file
        dico_lyr = dictionary for global informations
        tipo = format
        text = dictionary of text in the selected language

        see: http://resources.arcgis.com/fr/help/main/10.2/index.html#//00s300000008000000
        """
        # changing working directory to layer folder
        chdir(path.dirname(lyr_path))

        # raising arcpy specific exceptions
        self.alert = 0

        # opening LYR
        layer_obj = Layer(lyr_path)
        # layer_des = Describe(lyrpath)

        # basics
        dico_lyr[u'name'] = layer_obj.name
        dico_lyr[u'description'] = layer_obj.description
        dico_lyr[u'folder'] = path.dirname(lyr_path)
        # by default let's start considering there is only one layer
        dico_lyr[u'layers_count'] = 1

        # determining type of lyr
        if layer_obj.isFeatureLayer:
            dico_lyr[u'type'] = txt.get('lyr_featL')
            self.infos_geos(layer_obj, dico_lyr)
            self.infos_basics(layer_obj, dico_lyr)
            # features
            # dico_lyr[u'num_obj'] = int(obj_count(lyr_path).getOutput(0))
            # fields
            dico_fields = OD()
            self.infos_fields(lyr_path, dico_lyr, dico_fields)
            dico_lyr[u'fields'] = dico_fields

            # count features
            with SearchCursor(lyr_path, [dico_fields.keys()[0]]) as cursor:
                rows = {row[0] for row in cursor}
 
            count = 0
            for row in rows:
                count += 1
            dico_lyr[u'num_obj'] = count

        elif layer_obj.isRasterLayer:
            dico_lyr[u'type'] = txt.get('lyr_rastL')
            self.infos_geos(layer_obj, dico_lyr)
            self.infos_basics(layer_obj, dico_lyr)
        elif layer_obj.isRasterizingLayer:
            dico_lyr[u'type'] = txt.get('lyr_rastzL')
            self.infos_basics(layer_obj, dico_lyr)
        elif layer_obj.isServiceLayer:
            dico_lyr[u'type'] = txt.get('lyr_servL')
            self.infos_basics(layer_obj, dico_lyr)
            if layer_obj.supports("SERVICEPROPERTIES"):
                self.infos_service(layer_obj.serviceProperties, dico_lyr)
            else:
                self.erratum(dico_lyr, lyr_path, u'err_incomp')
                self.alert = self.alert + 1
                return None
        elif layer_obj.isNetworkAnalystLayer:
            dico_lyr['type'] = txt.get('lyr_netwaL')
            self.infos_basics(layer_obj, dico_lyr)
        elif layer_obj.isGroupLayer:
            dico_lyr['type'] = txt.get('lyr_groupL')
            self.infos_basics(layer_obj, dico_lyr)
            # layers inside
            sublayers = ListLayers(layer_obj)
            dico_lyr['layers_count'] = len(sublayers) -1
            dico_lyr['layers_names'] = [sublyr.name for sublyr in sublayers[1:]]
        else:
            self.erratum(dico_lyr, lyr_path, u'err_incomp')
            self.alert = self.alert + 1
            return None

        # scale
        dico_lyr['maxScale'] = layer_obj.maxScale
        dico_lyr['minScale'] = layer_obj.minScale

        # secondary
        dico_lyr['license'] = layer_obj.credits
        dico_lyr['broken'] = layer_obj.isBroken

        # dependencies
        dependencies = [f for f in listdir(path.dirname(lyr_path))
                        if path.splitext(path.abspath(f))[0] == path.splitext(lyr_path)[0]
                        and not path.splitext(path.abspath(f).lower())[1] == ".lyr"
                        or path.isfile('%s.xml' % f[:-4])]
        dico_lyr[u'dependencies'] = dependencies

        # cumulated size
        dependencies.append(lyr_path)
        total_size = sum([path.getsize(f) for f in dependencies])
        dico_lyr[u"total_size"] = self.sizeof(total_size)
        dependencies.pop(-1)

        # global dates
        dico_lyr[u'date_actu'] = strftime('%d/%m/%Y',
                                          localtime(path.getmtime(lyr_path)))
        dico_lyr[u'date_crea'] = strftime('%d/%m/%Y',
                                          localtime(path.getctime(lyr_path)))

        # # total fields count
        # total_fields = 0
        # dico_lyr['total_fields'] = total_fields

        # # total objects count
        # total_objs = 0
        # dico_lyr['total_objs'] = total_objs

        # # parsing layers

    def infos_basics(self, layer_obj, dico_lyr):
        u""" get the global informations about the layer """
        # dataset title
        if layer_obj.supports("WORKSPACEPATH"):
            dico_lyr[u'wkspace'] = layer_obj.workspacePath
        else:
            pass

        # dataset title
        if layer_obj.supports("DATASETNAME"):
            dico_lyr[u'title'] = layer_obj.datasetName
        else:
            pass

        # if a selection is active
        if layer_obj.supports("DEFINITIONQUERY"):
            dico_lyr[u'defquery'] = layer_obj.definitionQuery
        else:
            pass

        # if labels are displayed
        if layer_obj.supports("SHOWLABELS"):
            dico_lyr[u'labelsDisplay'] = layer_obj.showLabels
        else:
            pass

        # transparency level
        if layer_obj.supports("TRANSPARENCY"):
            dico_lyr[u'transpar'] = layer_obj.transparency
        else:
            pass

        # transparency level
        if layer_obj.supports("BRIGHTNESS"):
            dico_lyr[u'brightness'] = layer_obj.brightness
        else:
            pass

        # transparency level
        if layer_obj.supports("CONTRAST"):
            dico_lyr[u'contrast'] = layer_obj.contrast
        else:
            pass

        # end of function
        return

    def infos_geos(self, layer_obj, dico_lyr):
        u"""
        Gets informations about geography and geometry
        """
        # spatial extent
        extent = layer_obj.getExtent()
        dico_lyr[u'Xmin'] = round(extent.XMin, 2)
        dico_lyr[u'Xmax'] = round(extent.XMax, 2)
        dico_lyr[u'Ymin'] = round(extent.YMin, 2)
        dico_lyr[u'Ymax'] = round(extent.YMax, 2)

        # SRS
        srs = extent.spatialReference
        dico_lyr[u'srs'] = srs.name
        dico_lyr[u'srs_type'] = srs.type
        if srs.type == u'Projected':
            dico_lyr[u'EPSG'] = srs.PCSCode, srs.PCSName, srs.projectionCode, srs.projectionName
        elif srs.type == u'Geographic':
            dico_lyr[u'EPSG'] = srs.GCSCode, srs.GCSName, srs.datumCode, srs.datumName
        else:
            dico_lyr[u'EPSG'] = (srs.PCSCode, srs.PCSName, srs.projectionCode, srs.projectionName),\
                                (srs.GCSCode, srs.GCSName, srs.datumCode, srs.datumName)

        # end of function
        return


    def infos_service(self, lyr_serv_prop, dico_lyr):
        u"""
        specific informations for service layer
        """
        if lyr_serv_prop["ServiceType"] != "SDE":
            dico_lyr['servType'] = lyr_serv_prop.get('ServiceType', 'N/A')
            dico_lyr['servName'] = lyr_serv_prop.get('ServiceName', 'N/A')
            dico_lyr['WMSName'] = lyr_serv_prop.get('WMSName', 'N/A')
            dico_lyr['WMSTitle'] = lyr_serv_prop.get('WMSTitle', 'N/A')
            dico_lyr['URL'] = lyr_serv_prop.get('URL', 'N/A')
            dico_lyr['connection'] = lyr_serv_prop.get('Connection', 'N/A')
            dico_lyr['server'] = lyr_serv_prop.get('Server', 'N/A')
            dico_lyr['cache'] = str(lyr_serv_prop.get('Cache', 'N/A'))
            dico_lyr['user'] = lyr_serv_prop.get('UserName', 'N/A')
            dico_lyr['pwd'] = lyr_serv_prop.get('Password', 'N/A')
        else:
            dico_lyr['servType'] = lyr_serv_prop.get('ServiceType', 'N/A')
            dico_lyr['database'] = lyr_serv_prop.get('Database', 'N/A')
            dico_lyr['server'] = lyr_serv_prop.get('Server', 'N/A')
            dico_lyr['service'] = lyr_serv_prop.get('Service', 'N/A')
            dico_lyr['version'] = lyr_serv_prop.get('Version', 'N/A')
            dico_lyr['user'] = lyr_serv_prop.get('UserName', 'N/A')
            dico_lyr['authentication'] = lyr_serv_prop.get('AuthenticationMode', 'N/A')

        # end of function
        return

    def infos_fields(self, lyr_path, dico_lyr, dico_fields):
        u"""
        get the informations about fields definitions
        """
        fields = ListFields(lyr_path)
        dico_lyr[u'num_fields'] = len(fields)
        for field in fields:
            if field.name not in [u'FID', u'SHAPE', u'Shape', u'OBJECTID']:
                dico_fields[field.name] = field.type, field.length, field.precision,\
                                      field.aliasName, field.required
            else:
                pass
            
        # end of function
        return dico_fields

    def sizeof(self, os_size):
        u"""
        Returns size in different units depending on size
        see http://stackoverflow.com/a/1094933
        """
        for size_cat in ['octets', 'Ko', 'Mo', 'Go']:
            if os_size < 1024.0:
                return "%3.1f %s" % (os_size, size_cat)
            os_size /= 1024.0
        # end of function
        return "%3.1f %s" % (os_size, " To")


    def erratum(self, dico_lyr, lyrpath, mess):
        u""" errors handler """
        # storing minimal informations to give clues to solve later
        dico_lyr[u'name'] = path.basename(lyrpath)
        dico_lyr[u'folder'] = path.dirname(lyrpath)
        dico_lyr[u'error'] = mess
        # End of function
        return dico_lyr

###############################################################################
###### Stand alone program ########
###################################

if __name__ == '__main__':
    u"""
    Standalone execution for development and tests. Paths are relative considering
    a test within the official repository (https://github.com/Guts/DicoGIS/)
    """
    # searching for lyr Files
    dir_lyr = path.abspath(r'..\..\test\datatest\maps_docs\lyr')
    # dir_lyr = path.abspath(r'\\Copernic\SIG_RESSOURCES\1_lyr\ADMINISTRATIF')
    chdir(path.abspath(dir_lyr))
    li_lyr = listdir(path.abspath(dir_lyr))
    li_lyr = [path.abspath(lyr) for lyr in li_lyr if path.splitext(lyr)[1].lower()=='.lyr']

    # recipient datas
    dico_lyr = OD()

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

    textos['lyr_featL'] = u'Feature'
    textos['lyr_rastL'] = u'Raster'
    textos['lyr_rastzL'] = u'Rasterizing'
    textos['lyr_netwaL'] = u'Network Analyst'
    textos['lyr_servL'] = u'Web Service'
    textos['lyr_groupL'] = u'Group'

    # read LYR
    for lyrpath in li_lyr:
        dico_lyr.clear()
        if path.isfile(lyrpath):
            print("\n{0}: ".format(lyrpath))
            Read_LYR(lyrpath,
                     dico_lyr,
                     'Esri LYR',
                     txt=textos)
            # print results
            print(dico_lyr)
        else:
            print("{0} is not a recognized file".format(lyrpath))
            continue
