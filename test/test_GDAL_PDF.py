# -*- coding: UTF-8 -*-
#!/usr/bin/env python
# from __future__ import unicode_literals

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
# Updated:      12/05/2014
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
from osgeo import ogr
from gdalconst import *
gdal.AllRegister()

################################################################################
########### Classes #############
#################################

in_geopdf = r'\\nas.hq.isogeo.fr\SIG\SIG_DATA_SERVICE\TEST\07_PDF\NC_Windsor_North_20110909_TM_geo.pdf'

geopdf = gdal.Open(in_geopdf)

print(dir(geopdf))