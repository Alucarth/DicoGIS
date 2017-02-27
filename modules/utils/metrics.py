# -*- coding: UTF-8 -*-
#!/usr/bin/env python
from __future__ import unicode_literals
from __future__ import print_function
#------------------------------------------------------------------------------
# Name:         Metrics
# Purpose:      Perform some statistical metrics from DicoGIS
#
# Author:       Julien Moura (@geojulien)
#
# Python:       2.7.x
# Created:      12/04/2015
# Updated:      12/04/2015
#
# Licence:      GPL 3
#------------------------------------------------------------------------------

###############################################################################
########### Libraries #############
###################################

# Standard library
# from os import listdir, walk, path  # files and folder managing

###############################################################################
############# Classes #############
###################################


class MetricsManager(dict):
    # def __init__(self):
    #     u"""
    #     TODO
    #     """
    #     pass

    def init_metrics(self):
        u"""
        TODO
        """
        self[u"total_fields"] = 0

    def store_metrics(self, dico_global, dico_annex, type_data):
        """
        TODO
        """
        print('youhou')
        print(dico_global.keys())
        self['total_fields'] += dico_global.get('num_fields')
        pass

    def send_metrics(self):
        """
        TODO
        """
        print('youpi')
        pass

###############################################################################
###### Stand alone program ########
###################################

if __name__ == '__main__':
    """ standalone execution """
    app = MetricsManager()
