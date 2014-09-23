# -*- coding: UTF-8 -*-
#!/usr/bin/env python
from __future__ import unicode_literals
#------------------------------------------------------------------------------
# Name:         Texts Manager
# Purpose:      Load texts from localized files to display in a parent program
#
# Author:       Julien Moura (@geojulien)
#
# Python:       2.7.x
# Created:      21/09/2014
# Updated:      21/09/2014
#
# Licence:      GPL 3
#------------------------------------------------------------------------------

###############################################################################
########### Libraries #############
###################################

# Standard library
from os import path
from xml.etree import ElementTree as ET     # XML parsing and writer

# Python 3 backported
from collections import OrderedDict as OD   # ordered dictionary

# 3rd party libraries

# Custom modules

# Imports depending on operating system

###############################################################################
############# Classes #############
###################################


class TextsManager():
    def __init__(self, dico_texts, lang='EN', locale_folder=r'../../data/locale'):
        u"""
        Load texts from a file into a dictionary used to custom program display.

        dico_texts = ordered dictonary filled by methods
        lang = 2 letters prefix to pick the correct language
        locale_folder = directory where languages files are located
        """
        print path.isdir(locale_folder)

    def load_texts(self, lang='FR'):
        u""" Load texts according to the selected language """
        # clearing the text dictionary
        self.blabla.clear()
        # open xml cursor
        xml = ET.parse('data/locale/lang_{0}.xml'.format(lang))
        # Looping and gathering texts from the xml file
        for elem in xml.getroot().getiterator():
            self.blabla[elem.tag] = elem.text
        # updating the GUI
        self.update()
        # Fin de fonction
        return self.blabla

###############################################################################
###### Stand alone program ########
###################################

if __name__ == '__main__':
    """ standalone execution """
    blabla = OD()
    app = TextsManager(dico_texts=blabla,
                       lang='EN',
                       locale_folder=r'../../data/locale')

