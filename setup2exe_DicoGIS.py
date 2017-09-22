# -*- coding: UTF-8 -*-
#!/usr/bin/env python
#-------------------------------------------------------------------------------
# Name:         dicogis2exe
# Purpose:      Script to transform DicoGIS scripts into an Windows executable
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
import ConfigParser
import numpy
import os
import py2exe
import sys

# custom modules
from DicoGIS import DGversion
from modules import *

################################################################################
########## Functions ##############
###################################

# add any numpy directory containing a dll file to sys.path
def numpy_dll_paths_fix():
    paths = set()
    np_path = numpy.__path__[0]
    for dirpath, _, filenames in os.walk(np_path):
        for item in filenames:
            if item.endswith('.dll'):
                paths.add(dirpath)

    sys.path.append(*list(paths))

################################################################################
########## Main program ###########
###################################

# adding py2exe to the env path
sys.argv.append('py2exe')
numpy_dll_paths_fix()

# Specific data for gdal
gdal_dir = r'data/gdal'
gdal_files = [os.path.join(gdal_dir, i) for i in os.listdir(gdal_dir)]

# Specific dll for pywin module
mfcdir = r'C:\Python27\Lib\site-packages\pythonwin'
mfcfiles = [os.path.join(mfcdir, i) for i in ["mfc90.dll", "mfc90u.dll", "mfcm90.dll", "mfcm90u.dll", "Microsoft.VC90.MFC.manifest"]]

# initial settings
confile = 'options.ini'
config = ConfigParser.RawConfigParser()
# add sections
config.add_section('basics')
# basics
config.set('basics', 'def_codelang', 'EN')
config.set('basics', 'def_rep', './')
# Writing the configuration file
with open(confile, 'wb') as configfile:
    config.write(configfile)

# build settings
build_options = dict(
                    build_base='setup/temp_build',
                    )

# conversion settings
py2exe_options = dict(
                        excludes=['_ssl',  # Exclude _ssl
                                  'pyreadline', 'doctest', 'email',
                                  'optparse', 'pickle'],  # Exclude standard lib
                        dll_excludes=["MSVCP90.dll"
                                      "libzmq.pyd",
                                      "geos_c.dll",
                                      "api-ms-win-core-string-l1-1-0.dll",
                                      "api-ms-win-core-registry-l1-1-0.dll",
                                      "api-ms-win-core-errorhandling-l1-1-1.dll",
                                      "api-ms-win-core-string-l2-1-0.dll",
                                      "api-ms-win-core-profile-l1-1-0.dll",
                                      "api-ms-win*.dll",
                                      "api-ms-win-core-processthreads-l1-1-2.dll",
                                      "api-ms-win-core-libraryloader-l1-2-1.dll",
                                      "api-ms-win-core-file-l1-2-1.dll",
                                      "api-ms-win-security-base-l1-2-0.dll",
                                      "api-ms-win-eventing-provider-l1-1-0.dll",
                                      "api-ms-win-core-heap-l2-1-0.dll",
                                      "api-ms-win-core-libraryloader-l1-2-0.dll",
                                      "api-ms-win-core-localization-l1-2-1.dll",
                                      "api-ms-win-core-sysinfo-l1-2-1.dll",
                                      "api-ms-win-core-synch-l1-2-0.dll",
                                      "api-ms-win-core-heap-l1-2-0.dll",
                                      "api-ms-win-core-handle-l1-1-0.dll",
                                      "api-ms-win-core-io-l1-1-1.dll",
                                      "api-ms-win-core-com-l1-1-1.dll",
                                      "api-ms-win-core-memory-l1-1-2.dll",
                                      "api-ms-win-core-version-l1-1-1.dll",
                                      "api-ms-win-core-version-l1-1-0.dll"],
                        compressed=1,  # Compress library.zip
                        optimize=2,
                        # bundle_files = 1,
                        dist_dir='setup/DicoGIS_{}'.format(DGversion)
                      )


setup(name="DicoGIS",
      version=DGversion,
      description="Dictionary of geographic datas",
      author="Julien Moura",
      url="https://github.com/Guts/DicoGIS",
      license="license GPL v3.0",
      data_files=[
                    # # pywin and numpy
                    # ("Microsoft.VC90.MFC", mfcfiles, "C:\\Python27\\Lib\\site-packages\\numpy\\core\\libiomp5md.dll"),
                    # gdal
                    ("data/gdal", gdal_files),
                    # languages
                    ("data/locale", ["data/locale/lang_EN.xml",
                                     "data/locale/lang_ES.xml",
                                     "data/locale/lang_FR.xml"]),
                    # initial configuration
                    ("", ["options.ini"]),
                    # images
                    ("", ["DicoGIS.ico"]),
                    ("data/img", ["data/img/DicoGIS_logo.gif"]),
                    # documentation
                    ("doc", ["README.md",
                             "doc/DicoGIS_Presentacion_ES.html",
                             "doc/DicoGIS_Presentation_FR.html",
                             "doc/DicoGIS_ReadMe.html",
                             "doc/DicoGIS_GitHub.url"])
                    ],
      options={'py2exe': py2exe_options, 'build': build_options},
      windows=[
            {
            "script": "DicoGIS.py",                     # main script
            "icon_resources": [(1, "DicoGIS.ico")]      # Icone
            }
                ]
    )
