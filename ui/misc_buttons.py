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
from Tkinter import Tk, StringVar, IntVar, Image    # GUI
from Tkinter import W, PhotoImage, ACTIVE, DISABLED, END
from tkFileDialog import askdirectory
from tkMessageBox import showinfo as info, showerror as avert
from ttk import Combobox, Progressbar, Style, Labelframe, Frame
from ttk import Label, Button, Entry, Checkbutton, Notebook  # widgets
import tkFont   # font library

import logging
from webbrowser import open_new_tab

# ##############################################################################
# ############ Globals ############
# #################################

# LOG
logger = logging.getLogger("DicoGIS")

# ##############################################################################
# ########## Classes ###############
# ##################################


class MiscButtons(Frame):

    def __init__(self, parent):
        """Instanciating the output workbook."""
        # print(type(self), dir(self))
        self.parent = parent
        Frame.__init__(self)

        # contact
        mailto = "mailto:Isogeo%20Projects%20"\
                 "<projects+isogeo2office@isogeo.com>?"\
                 "subject=[Isogeo2office]%20Question"
        btn_contact = Button(self,
                             text="\U00002709 " + "Contact",
                             command=lambda: open_new_tab(mailto))

        # source
        url_src = "https://github.com/Guts/DicoGIS/issues"
        btn_src = Button(self,
                         text="\U000026A0 " + "Report",
                         command=lambda: open_new_tab(url_src))

        # griding
        # btn_contact.pack()
        # btn_src.pack()
        btn_contact.grid(row=1, rowspan=1,
                         column=1, padx=2, pady=2,
                         sticky="WE")
        btn_src.grid(row=1, rowspan=1,
                     column=2, padx=2, pady=2,
                     sticky="NSWE")

# #############################################################################
# ##### Stand alone program ########
# ##################################

if __name__ == '__main__':
    """To test"""
    root = Tk()
    frame = MiscButtons(root)
    frame.pack()
    root.mainloop()
