# -*- coding: UTF-8 -*-
#!/usr/bin/env python
from __future__ import unicode_literals

# ----------------------------------------------------------------------------
# Name:         InfosWFS
# Purpose:      Uses OGR to read GeoServer
#
# Author:       Julien Moura (https://github.com/Guts/)
#
# Python:       2.7.x
# Created:      04/04/2016
# Updated:      2016
# Licence:      GPL 3
# ----------------------------------------------------------------------------

# ############################################################################
# ########## Libraries #############
# ##################################
# Standard library
from os import path, walk   # files and folder managing
from time import localtime, strftime
import sys

# Python 3 backported
from collections import OrderedDict as OD

# 3rd party libraries
from geoserver.catalog import Catalog

# ############################################################################
# ########## Classes #############
# ################################

class ReadGeoServer():
    def __init__(self, gs_url, dico_gs, tipo, txt=''):
        u""" Uses OGR functions to extract basic informations about
        geographic Web Features Services.

        gs_url = url of a WFS service
        dico_wfs = dictionary for global informations
        dico_fields = dictionary for the fields' informations
        li_fieds = ordered list of fields
        tipo = format
        text = dictionary of text in the selected language

        """
        cat = Catalog(gs_url, "####", "####")
        layers = cat.get_layers()
        for layer in layers:
            print(layer.name)

# ############################################################################
# ##### Stand alone program ########
# ##################################

if __name__ == '__main__':
    u""" standalone execution for tests. Paths are relative considering a test
    within the official repository (https://github.com/Guts/DicoGIS/)"""
    from urllib2 import urlopen
    # test text dictionary
    textos = OD()

    # listing WFS
    li_geoservers = [
              r"http://noisy.hq.isogeo.fr:6090/geoserver/rest",
              ]

    # recipient datas
    dico_gs = OD()

    # read WFS
    for gs_url in li_geoservers:
        dico_gs.clear()
        print("\n{0}: ".format(gs_url))
        ReadGeoServer(gs_url,
                      dico_gs,
                      'GeoServer',
                       textos)
        # print results
        print(dico_gs)
