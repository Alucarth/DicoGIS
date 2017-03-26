# -*- coding: UTF-8 -*-
#!/usr/bin/env python
from __future__ import (absolute_import, print_function, unicode_literals)
# -----------------------------------------------------------------------------
# Name:         DicoGIS
# Purpose:      Automatize the creation of a dictionnary of geographic data
#               contained in a folders structures.
#               It produces an Excel output file (.xlsx)
#
# Author:       Julien Moura (@geojulien)
#
# Python:       2.7.x
# Created:      14/02/2013
# Updated:      19/03/2017
#
# Licence:      GPL 3
# ------------------------------------------------------------------------------

# ##############################################################################
# ########## Libraries #############
# ##################################

# Standard library
from Tkinter import StringVar, Tk
from ttk import Frame, Label, Entry

import logging

# ##############################################################################
# ############ Globals ############
# #################################

# LOG
logger = logging.getLogger("DicoGIS")

# ##############################################################################
# ########## Classes ###############
# ##################################


class TabServices(Frame):

    def __init__(self, parent, txt=dict()):
        """Instanciating the output workbook."""
        self.parent = parent
        Frame.__init__(self)

        # variables
        self.url_service = StringVar(self,
                                     'http://suite.opengeo.org/geoserver/wfs?request=GetCapabilities')

        # widgets
        self.lb_url_service = Label(self,
                                    text='OpenCatalog')
        self.ent_url_service = Entry(self,
                                     width=75,
                                     textvariable=self.url_service)

        # widgets placement
        self.ent_url_service.grid(row=0, column=1,
                                  sticky="NSWE", padx=2, pady=2)


# #############################################################################
# ##### Stand alone program ########
# ##################################

if __name__ == '__main__':
    """To test"""
    root = Tk()
    frame = TabServices(root)
    frame.pack()
    root.mainloop()
