# -*- coding: UTF-8 -*-
#!/usr/bin/env python
#-------------------------------------------------------------------------------
# Name:         metadator2exe
# Purpose:      Script to transform Metadator scripts into an Windows executable
#                   software. It uses py2exe.
#
# Author:       Julien Moura (https://github.com/Guts/)
#
# Python:       2.7.x
# Created:      19/12/2011
# Updated:      12/05/2014
#
# Licence:      GPL 3
#-------------------------------------------------------------------------------

################################################################################
########### Libraries #############
###################################
# Standard library
from distutils.core import setup
import py2exe
import os
import ConfigParser
import numpy

# custom modules
from modules import *

################################################################################
########## Main program ###########
###################################

# version
num_version = "v2.0-beta.3"

# Specific data for gdal
gdal_dir = r'data/gdal'
gdal_files = [os.path.join(gdal_dir, i) for i in os.listdir(gdal_dir)]

# build settings
build_options = dict(
                    build_base='setup/temp_build',
                    )

# conversion settings 
py2exe_options = dict(
                        excludes=['_ssl',  # Exclude _ssl
                                  'pyreadline', 'doctest', 'email',
                                  'optparse', 'pickle'],  # Exclude standard library
                        dll_excludes = ['MSVCP90.dll'],
                        compressed=True,  # Compress library.zip
                        optimize = 2,
                        dist_dir = 'setup/DicoGIS_{}'.format(num_version)
                      )


setup(name="DicoGIS",
      version=num_version,
      description="Dictionary of geographic datas",
      author="Julien Moura",
      url = "https://github.com/Guts/DicoGIS",
      license="license GPL v3.0",
      data_files = [
                    # gdal
                    ("data/gdal", gdal_files),
                    # languages
                    ("data/locale", ["data/locale/lang_EN.xml",
                                "data/locale/lang_ES.xml",
                                "data/locale/lang_FR.xml"]),
                    # initial configuration
                    ("", ["settings.xml"]),
                    # images
                    ("", ["DicoGIS.ico"]),
                    ("data/img", ["data/img/DicoGIS_logo.gif"]),
                    # documentation
                    ("doc",["doc/DicoGIS_Manual_ES.pdf",
                            "doc/README.html",
                            "doc/DicoGIS_TechnicalDetails.htm"])
                    ],
      options={'py2exe': py2exe_options, 'build': build_options},
      windows = [
            {
            "script": "DicoGIS.py",                     # main script
            "icon_resources": [(1, "DicoGIS.ico")]      # Icone
            }
                ]
    )