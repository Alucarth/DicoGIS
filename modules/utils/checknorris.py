# -*- coding: UTF-8 -*-
#!/usr/bin/env python
from __future__ import (absolute_import, print_function, unicode_literals)
# -----------------------------------------------------------------------------
# Name:         Check Norris
# Purpose:      A class dedicated to perform system test to ensure another
#               program works fine
#
# Author:       Julien Moura (@geojulien)
#
# Python:       2.7.x
# Created:      22/12/2015
# Updated:      10/01/2016
# -----------------------------------------------------------------------------

# #############################################################################
# ###### Standard Libraries ########
# ##################################

import sys

# #############################################################################
# ########## Classes ###############
# ##################################


class CheckNorris(object):
    """ Check Norris never fails, always tests.
    """
    # -- ATTRIBUTES -----------------------------------------------------------

    # -- BEFORE ALL -----------------------------------------------------------

    def __init__(self, proxy=None):
        """ Instanciation
        """
        super(CheckNorris, self).__init__()

        # handling proxy parameters
        # see: http://docs.python-requests.org/en/latest/user/advanced/#proxies
        if proxy and type(proxy) is dict and 'http' in proxy.keys():
            print("Proxy activated")
            self.proxies = proxy
        elif proxy and type(proxy) is not dict:
            print("Proxy syntax error. Must be a dict { 'protocol': 'http://username:password@proxy_url:port' }.\
                e.g.: {'http': 'http://martin:p4ssW0rde@10.1.68.1:5678',\
                       'https': 'http://martin:p4ssW0rde@10.1.68.1:5678'}")
            return
        else:
            self.proxies = {}
            print("No proxy set. Use default configuration.")
            pass

    # -- API CONNECTION ------------------------------------------------------

    def check_arcpy(self):
        """ Chcks if arcpy and which verison is installed
        """
        # 3rd party libraries
        try:
            import arcpy
            print("Great! ArcGIS is well installed.")
        except ImportError:
            print("ArcGIS isn't registered in the sys.path")
            sys.path.append(r'C:\Program Files (x86)\ArcGIS\Desktop10.2\arcpy')
            sys.path.append(r'C:\Program Files (x86)\ArcGIS\Desktop10.2\bin')
            sys.path.append(r'C:\Program Files (x86)\ArcGIS\Desktop10.2\ArcToolbox\Scripts')
            try:
                from arcpy import env as enviro
                from arcpy import ListDatasets, ListFeatureClasses, GetCount_management, ListFiles, ListFields, ListRasters, Describe
                print("ArcGIS has been added to Python path and then imported.")
            except:
                print("ArcGIS isn't installed on this computer")
                sys.exit()

# ##############################################################################
# ##### Stand alone program ########
# ##################################

if __name__ == '__main__':
    """ standalone execution """
    # ------------ Specific imports ----------------
    
    # ------------ Real start ----------------
    # instanciating the class
    checker = CheckNorris()
