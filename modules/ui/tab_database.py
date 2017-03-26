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
from Tkinter import Tk, StringVar, IntVar
from ttk import Labelframe, Frame
from ttk import Label, Entry, Checkbutton

import logging

# ##############################################################################
# ############ Globals ############
# #################################

# LOG
logger = logging.getLogger("DicoGIS")

# ##############################################################################
# ########## Classes ###############
# ##################################


class TabSGBD(Frame):

    def __init__(self, parent, txt=dict()):
        """Instanciating the output workbook."""
        self.parent = parent
        Frame.__init__(self)

        # subframe
        self.FrDb = Labelframe(self,
                               name='database',
                               text=txt.get('gui_fr2', "SGBD"))

        # DB variables
        self.opt_pgvw = IntVar(self.FrDb)   # able/disable PostGIS views
        self.host = StringVar(self.FrDb, 'localhost')
        self.port = IntVar(self.FrDb, 5432)
        self.dbnb = StringVar(self.FrDb)
        self.user = StringVar(self.FrDb, 'postgres')
        self.pswd = StringVar(self.FrDb)

        # Form widgets
        self.ent_H = Entry(self.FrDb, textvariable=self.host)
        self.ent_P = Entry(self.FrDb, textvariable=self.port, width=5)
        self.ent_D = Entry(self.FrDb, textvariable=self.dbnb)
        self.ent_U = Entry(self.FrDb, textvariable=self.user)
        self.ent_M = Entry(self.FrDb, textvariable=self.pswd, show='*')

        caz_pgvw = Checkbutton(self.FrDb,
                               text=txt.get('gui_views', "Views enabled"),
                               variable=self.opt_pgvw)

        # Label widgets
        self.lb_H = Label(self.FrDb, text=txt.get('gui_host', "Host"))
        self.lb_P = Label(self.FrDb, text=txt.get('gui_port', "Port"))
        self.lb_D = Label(self.FrDb, text=txt.get('gui_db', "Database"))
        self.lb_U = Label(self.FrDb, text=txt.get('gui_user', "User"))
        self.lb_M = Label(self.FrDb, text=txt.get('gui_mdp', "Password"))
        # widgets placement
        self.ent_H.grid(row=1, column=1, columnspan=2,
                        sticky="NSEW", padx=2, pady=2)
        self.ent_P.grid(row=1, column=3, columnspan=1,
                        sticky="NSE", padx=2, pady=2)
        self.ent_D.grid(row=2, column=1, columnspan=1,
                        sticky="NSEW", padx=2, pady=2)
        self.ent_U.grid(row=2, column=3, columnspan=1,
                        sticky="NSEW", padx=2, pady=2)
        self.ent_M.grid(row=3, column=1, columnspan=3,
                        sticky="NSEW", padx=2, pady=2)
        self.lb_H.grid(row=1, column=0,
                       sticky="NSEW", padx=2, pady=2)
        self.lb_P.grid(row=1, column=3,
                       sticky="NSW", padx=2, pady=2)
        self.lb_D.grid(row=2, column=0,
                       sticky="NSW", padx=2, pady=2)
        self.lb_U.grid(row=2, column=2,
                       sticky="NSW", padx=2, pady=2)
        self.lb_M.grid(row=3, column=0,
                       sticky="NSWE", padx=2, pady=2)
        caz_pgvw.grid(row=4, column=0,
                      sticky="NSWE", padx=2, pady=2)

        # frame position
        self.FrDb.grid(row=3, column=1, sticky="NSWE", padx=2, pady=2)

# #############################################################################
# ##### Stand alone program ########
# ##################################

if __name__ == '__main__':
    """To test"""
    root = Tk()
    frame = TabSGBD(root)
    frame.pack()
    root.mainloop()
