# -*- coding: UTF-8 -*-
#!/usr/bin/env python
from __future__ import (absolute_import, print_function, unicode_literals)
# ------------------------------------------------------------------------------
# Name:         Isogeo to Microsoft Excel 2010
# Purpose:      Get metadatas from an Isogeo share and store it into
#               a Excel worksheet. It's one of the submodules of
#               isogeo2office (https://bitbucket.org/isogeo/isogeo-2-office).
#
# Author:       Julien Moura (@geojulien)
#
# Python:       2.7.x
# Created:      14/08/2014
# Updated:      15/04/2016
# ------------------------------------------------------------------------------

# ##############################################################################
# ########## Libraries #############
# ##################################

# Python 2 and 3 compatibility
from future.standard_library import install_aliases
install_aliases()

# Standard library
import logging

# 3rd party libraries
from osgeo import gdal
from gdalconst import *

# ##############################################################################
# ########## Classes ###############
# ##################################


class GdalErrorHandler(object):
    def __init__(self):
        """Callable error handler.

        see: http://trac.osgeo.org/gdal/wiki/PythonGotchas#Exceptionsraisedincustomerrorhandlersdonotgetcaught
        and http://pcjericks.github.io/py-gdalogr-cookbook/gdal_general.html#install-gdal-ogr-error-handler
        """
        self.err_level = gdal.CE_None
        self.err_type = 0
        self.err_msg = ''

    def handler(self, err_level, err_type, err_msg):
        """Make errors messages more readable."""
        # available types
        err_class = {gdal.CE_None: 'None',
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
