# -*- coding: UTF-8 -*-
#!/usr/bin/env python
from __future__ import unicode_literals
from __future__ import print_function
#------------------------------------------------------------------------------
# Name:         Texts Manager
# Purpose:      Load texts from localized files to display in a parent program
#
# Author:       Julien Moura (@geojulien)
#
# Python:       2.7.x
# Created:      21/09/2014
# Updated:      28/09/2014
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

###############################################################################
############# Classes #############
###################################


class TextsManager():
    def __init__(self):
        u"""
        Manage texts from a file into a dictionary used to custom program display.
        """

    def load_texts(self, dico_texts, lang='EN', locale_folder=r'../../data/locale'):
        u"""
        Load texts according to the selected language.

        dico_texts = ordered dictonary filled by methods
        lang = 2 letters prefix to pick the correct language
        locale_folder = directory where languages files are located
        """
        # clearing the text dictionary
        dico_texts.clear()
        
        # open xml cursor
        locale_folder = path.abspath(locale_folder)
        xml = ET.parse('{0}/lang_{1}.xml'.format(locale_folder, lang))

        # Looping and gathering texts from the xml file
        for elem in xml.getroot().getiterator():
            dico_texts[elem.tag] = elem.text
        
        # end of fonction
        return dico_texts

###############################################################################
###### Stand alone program ########
###################################

if __name__ == '__main__':
    """ standalone execution """
    # ordered dictionay to store texts
    blabla = OD()

    # get the app aobject
    app = TextsManager()

    # get texts
    app.load_texts(dico_texts=blabla,
                   lang='EN',
                   locale_folder=r'../../data/locale')

    # return texts
    print(blabla)
