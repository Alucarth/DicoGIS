# -*- coding: UTF-8 -*-
#!/usr/bin/env python
from __future__ import absolute_import, print_function, unicode_literals

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
from Tkinter import Tk
from Tkinter import W, PhotoImage
from ttk import Style, Frame
from ttk import Label, Button

import logging
from os import path
from webbrowser import open_new_tab

# 3rd party modules
from isogeo_pysdk import Isogeo, __version__ as pysdk_version

# ##############################################################################
# ############ Globals ############
# #################################

# LOG
logger = logging.getLogger("DicoGIS")

# ##############################################################################
# ########## Classes ###############
# ##################################


class MiscButtons(Frame):
    def __init__(self, parent, dicogis_path="../../"):
        """Instanciating the output workbook."""
        self.parent = parent
        Frame.__init__(self)
        logging.info("Isogeo PySDK version: {0}".format(pysdk_version))

        # logo
        ico_path = path.join(path.abspath(dicogis_path), "data/img/DicoGIS_logo.gif")
        self.icone = PhotoImage(master=self, file=ico_path)
        Label(self, borderwidth=2, image=self.icone).grid(
            row=1, columnspan=2, column=0, padx=2, pady=2, sticky=W
        )
        # credits
        s = Style(self)
        s.configure("Kim.TButton", foreground="DodgerBlue", borderwidth=0)
        btn_credits = Button(
            self,
            text="by @GeoJulien\nGPL3 - 2017",
            style="Kim.TButton",
            command=lambda: open_new_tab("https://github.com/Guts/DicoGIS"),
        )
        btn_credits.grid(row=2, columnspan=2, padx=2, pady=2, sticky="WE")

        # contact
        mailto = (
            "mailto:DicoGIS%20Developer%20"
            "<julien.moura+dev@gmail.com>?"
            "subject=[DicoGIS]%20Question"
        )
        btn_contact = Button(
            self, text="\U00002709 " + "Contact", command=lambda: open_new_tab(mailto)
        )

        # source
        url_src = "https://github.com/Guts/DicoGIS/issues"
        btn_src = Button(
            self, text="\U000026A0 " + "Report", command=lambda: open_new_tab(url_src)
        )

        # griding
        btn_contact.grid(row=3, column=0, padx=2, pady=2, sticky="WE")
        btn_src.grid(row=3, column=1, padx=2, pady=2, sticky="EW")


# #############################################################################
# ##### Stand alone program ########
# ##################################

if __name__ == "__main__":
    """To test"""
    root = Tk()
    frame = MiscButtons(root)
    frame.pack()
    root.mainloop()
