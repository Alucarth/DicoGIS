# -*- coding: UTF-8 -*-
#!/usr/bin/env python
from __future__ import unicode_literals
from __future__ import print_function
# ----------------------------------------------------------------------------
# Name:         Geodata Explorer
# Purpose:      Explore directory structure and list files and folders
#               with geospatial data
#
# Author:       Julien Moura (@geojulien)
#
# Python:       2.7.x
# Created:      21/09/2014
# Updated:      21/09/2014
#
# Licence:      GPL 3
# ----------------------------------------------------------------------------

# ############################################################################
# ######## Libraries #############
# ################################

# Standard library
from os import path, access, R_OK, walk  # files and folder managing
from sys import platform as opersys
import subprocess

# Imports depending on operating system
if opersys == 'win32':
    u""" windows """
    from os import startfile        # to open a folder/file
else:
    pass

# ############################################################################
# ######### Classes #############
# ###############################


class Utilities(object):
    def __init__(self):
        u"""DicoGIS specific utilities"""
        super(Utilities, self).__init__()

    def open_dir_file(self, target):
        """Open a file or directory in the explorer of the operating system."""
        # check if the file or the directory exists
        if not path.exists(target):
            raise IOError('No such file: {0}'.format(target))

        # check the read permission
        if not access(target, R_OK):
            raise IOError('Cannot access file: {0}'.format(target))

        # open the directory or the file according to the os
        if opersys == 'win32':  # Windows
            proc = startfile(path.realpath(target))

        elif opersys.startswith('linux'):  # Linux:
            proc = subprocess.Popen(['xdg-open', target],
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE)

        elif opersys == 'darwin':  # Mac:
            proc = subprocess.Popen(['open', '--', target],
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE)

        else:
            raise NotImplementedError(
                "Your `%s` isn't a supported operating system`." % opersys)

        # end of function
        return proc

# ############################################################################
# #### Stand alone program ########
# #################################

if __name__ == '__main__':
    """ standalone execution """
    utils = Utilities()
