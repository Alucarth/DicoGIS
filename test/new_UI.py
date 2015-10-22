# -*- coding: UTF-8 -*-
#!/usr/bin/env python
from __future__ import unicode_literals
# -----------------------------------------------------------------------------
# Name:         DicoGIS
# Purpose:      Automatize the creation of a dictionnary of geographic data
#                   contained in a folders structures.
#                   It produces an Excel output file (.xls)
#
# Author:       Julien Moura (https://twitter.com/geojulien)
#
# Python:       2.7.x
# Created:      14/02/2013
# Updated:      13/04/2015
#
# Licence:      GPL 3
# ------------------------------------------------------------------------------

DGversion = "2.5.0-beta1"

###############################################################################
########### Libraries #############
###################################

# Standard library
from Tkinter import Tk, StringVar, IntVar, Image    # GUI
from Tkinter import W, PhotoImage, ACTIVE, DISABLED, END
from tkFileDialog import askdirectory, asksaveasfilename    # dialogs
from tkMessageBox import showinfo as info, showerror as avert
from ttk import Combobox, Progressbar, Style, Labelframe, Frame
from ttk import Label, Button, Entry, Radiobutton, Checkbutton, Notebook  # widgets
import tkFont   # font library

from sys import exit, platform as opersys
from os import listdir, walk, path         # files and folder managing
from os import environ as env, access, R_OK
import platform  # about operating systems


# Imports depending on operating system
if opersys == 'win32':
    u""" windows """
    from os import startfile        # to open a folder/file
else:
    pass

###############################################################################
############# Classes #############
###################################


class DicoGIS(Tk):
    def __init__(self):
        u"""
        Main window constructor
        Creates 1 frame and 2 labelled subframes
        """

        # basics settings
        Tk.__init__(self)               # constructor of parent graphic class
        self.title(u'DicoGIS {0}'.format(DGversion))

        self.li_raster_formats = ['ecw', 'geotiff']

        # notebook
        self.nb = Notebook(self)
        self.FrProg = Labelframe(self,
                                 name='progression',
                                 text='gui_prog')
        self.FrOutp = Labelframe(self,
                                 name='output',
                                 text='gui_fr4')
        # tabs
        self.tab_files = Frame(self.nb)    # tab_id = 0
        self.tab_sgbd = Frame(self.nb)          # tab_id = 1
        self.tab_webservices = Frame(self.nb)   # tab_id = 2
        self.tab_isogeo = Frame(self.nb)        # tab_id = 3
        self.tab_about = Frame(self.nb)        # tab_id = 4


        ## TAB 1: FILES
        self.nb.add(self.tab_files,
                    text='gui_files', padding=3)
        # frame: path folder
        self.FrPath = Labelframe(self.tab_files,
                                 name='files',
                                 text='gui_fr1')
        self.labtarg = Label(self.FrPath, text='gui_path')
        self.target = Entry(master=self.FrPath, width=35)
        self.browsetarg = Button(self.FrPath,       # browse button
                                 text='gui_choix',
                                 command=lambda: self.setpathtarg(),
                                 takefocus=True)
        self.browsetarg.focus_force()               # force the focus on

        # widgets placement
        self.labtarg.grid(row=1, column=1, columnspan=1,
                          sticky="NSWE", padx=2, pady=2)
        self.target.grid(row=1, column=2, columnspan=1,
                         sticky="NSWE", padx=2, pady=2)
        self.browsetarg.grid(row=1, column=3,
                             sticky="NSWE", padx=2, pady=2)

        # frame: filters
        self.FrFilters = Labelframe(self.tab_files,
                                    name='filters',
                                    text='filters')
        # formats options
        self.opt_shp = IntVar(self.FrFilters)   # able/disable shapefiles
        self.opt_tab = IntVar(self.FrFilters)   # able/disable MapInfo tables
        self.opt_kml = IntVar(self.FrFilters)   # able/disable KML
        self.opt_gml = IntVar(self.FrFilters)   # able/disable GML
        self.opt_geoj = IntVar(self.FrFilters)  # able/disable GeoJSON
        self.opt_gxt = IntVar(self.FrFilters)  # able/disable GXT
        self.opt_egdb = IntVar(self.FrFilters)  # able/disable Esri FileGDB
        self.opt_spadb = IntVar(self.FrFilters)  # able/disable Spatalite DB
        self.opt_rast = IntVar(self.FrFilters)  # able/disable rasters
        self.opt_cdao = IntVar(self.FrFilters)  # able/disable CAO/DAO files
        self.opt_pdf = IntVar(self.FrFilters)   # able/disable Geospatial PDF
        self.opt_lyr = IntVar(self.FrFilters)   # able/disable Geospatial Lyr
        self.opt_mxd = IntVar(self.FrFilters)   # able/disable Geospatial MXD
        self.opt_qgs = IntVar(self.FrFilters)   # able/disable Geospatial QGS

        # format choosen: check buttons
        caz_shp = Checkbutton(self.FrFilters,
                              text=u'.shp',
                              variable=self.opt_shp)
        caz_tab = Checkbutton(self.FrFilters,
                              text=u'.tab',
                              variable=self.opt_tab)
        caz_kml = Checkbutton(self.FrFilters,
                              text=u'.kml',
                              variable=self.opt_kml)
        caz_gml = Checkbutton(self.FrFilters,
                              text=u'.gml',
                              variable=self.opt_gml)
        caz_geoj = Checkbutton(self.FrFilters,
                               text=u'.geojson',
                               variable=self.opt_geoj)
        caz_gxt = Checkbutton(self.FrFilters,
                              text=u'.gxt',
                              variable=self.opt_gxt)
        caz_egdb = Checkbutton(self.FrFilters,
                               text=u'Esri FileGDB',
                               variable=self.opt_egdb)
        caz_spadb = Checkbutton(self.FrFilters,
                                text=u'Spatialite',
                                variable=self.opt_spadb)
        caz_rast = Checkbutton(self.FrFilters,
                               text=u'rasters ({0})'.format(', '.join(self.li_raster_formats)),
                               variable=self.opt_rast)
        caz_cdao = Checkbutton(self.FrFilters,
                               text=u'CAO/DAO',
                               variable=self.opt_cdao)
        caz_pdf = Checkbutton(self.FrFilters,
                              text=u'Geospatial PDF',
                              variable=self.opt_pdf)
        caz_lyr = Checkbutton(self.FrFilters,
                              text=u'.lyr',
                              variable=self.opt_lyr)
        caz_mxd = Checkbutton(self.FrFilters,
                              text=u'.mxd',
                              variable=self.opt_mxd)
        caz_qgs = Checkbutton(self.FrFilters,
                              text=u'.qgs',
                              variable=self.opt_qgs)
        # widgets placement
        caz_shp.grid(row=1,
                     column=0,
                     sticky="NSWE",
                     padx=2, pady=2)
        caz_tab.grid(row=1,
                     column=1,
                     sticky="NSWE",
                     padx=2, pady=2)
        caz_kml.grid(row=1,
                     column=2,
                     sticky="NSWE",
                     padx=2, pady=2)
        caz_gml.grid(row=1,
                     column=3,
                     sticky="NSWE",
                     padx=2, pady=2)
        caz_geoj.grid(row=1,
                      column=4,
                      sticky="NSWE",
                      padx=2, pady=2)
        caz_gxt.grid(row=1,
                     column=7,
                     sticky="NSWE",
                     padx=2, pady=2)
        caz_pdf.grid(row=1,
                     column=5,
                     columnspan=2,
                     sticky="NSWE",
                     padx=2, pady=2)
        caz_rast.grid(row=2,
                      column=0,
                      columnspan=2,
                      sticky="NSWE",
                      padx=2, pady=2)
        caz_egdb.grid(row=2,
                      column=2,
                      columnspan=2,
                      sticky="NSWE",
                      padx=2, pady=2)
        caz_cdao.grid(row=2,
                      column=4,
                      columnspan=1,
                      sticky="NSWE",
                      padx=2, pady=2)
        caz_spadb.grid(row=2,
                       column=5,
                       columnspan=2,
                       sticky="NSWE",
                       padx=2, pady=2)
        caz_lyr.grid(row=3,
                     column=0,
                     columnspan=2,
                     sticky="NSWE",
                     padx=2, pady=2)
        caz_mxd.grid(row=3,
                     column=1,
                     columnspan=2,
                     sticky="NSWE",
                     padx=2, pady=2)
        caz_qgs.grid(row=3,
                     column=2,
                     columnspan=2,
                     sticky="NSWE",
                     padx=2, pady=2)


        # frames placement
        self.FrPath.grid(row=3, column=1, padx=2, pady=2,
                 sticky="NSWE")
        self.FrFilters.grid(row=4, column=1, padx=2, pady=2,
                    sticky="NSWE")

        # tab 2: database
        self.nb.add(self.tab_sgbd,
                    text='gui_database', padding=3)





        # tab 3: webservices
        self.nb.add(self.tab_webservices,
                    text='gui_webservices', padding=3)



        ## TAB 4: ISOGEO
        self.nb.add(self.tab_isogeo,
                    text='gui_Isogeo', padding=3)


        ## TAB 5: ABOUT
        self.nb.add(self.tab_about,
                    text='gui_about', padding=3)


        ## MAIN FRAME
        # Welcome message
        self.welcome = Label(self,
                             text='hola test',
                             foreground="red2")

        # Progression bar
        self.status = StringVar(self.FrProg, '')
        # widgets
        self.prog_layers = Progressbar(self.FrProg,
                                       orient="horizontal")
        Label(master=self.FrProg,
              textvariable=self.status,
              foreground='DodgerBlue').pack()
        # widgets placement
        self.prog_layers.pack(expand=1, fill='both')

        # Output configuration
        # widgets
        self.nameoutput = Label(self.FrOutp,
                                text='gui_fic')
        self.output = Entry(self.FrOutp, width=35)
        # widgets placement
        self.nameoutput.grid(row=0, column=1,
                             sticky="NSWE", padx=2, pady=2)
        self.output.grid(row=0, column=2, columnspan=2,
                         sticky="NSWE", padx=2, pady=2)

        # Image
        self.icone = PhotoImage(file=r'../data/img/DicoGIS_logo.gif')
        Label(self,
              borderwidth=2,
              image=self.icone).grid(row=1,
                                     rowspan=4,
                                     column=0,
                                     padx=2,
                                     pady=2,
                                     sticky=W)
        # credits
        s = Style(self)
        s.configure('Kim.TButton', foreground='DodgerBlue', borderwidth=0)
        Button(self,
               text='by @GeoJulien\nGPL3 - 2015',
               style='Kim.TButton',
               command=lambda: open_new('https://github.com/Guts/DicoGIS')).grid(row=4,
                                                                                 padx=2,
                                                                                 pady=2,
                                                                                 sticky="WE")
        # language switcher
        self.ddl_lang = Combobox(self,
                                 values=['fr', 'en'],
                                 width=5)

        # grid placement
        self.val = Button(self,
                          text='gui_go',
                          state=ACTIVE,
                          command=lambda: self.process())
        self.can = Button(self, text='gui_quit',
                          command=lambda: self.destroy())
        self.welcome.grid(row=1, column=1, columnspan=1, sticky="NS",
                          padx=2, pady=2)
        self.ddl_lang.grid(row=1, column=1, sticky="NSE", padx=2, pady=2)
        self.nb.grid(row=2, column=1)
        self.FrProg.grid(row=3, column=1, sticky="NSWE", padx=2, pady=2)
        self.FrOutp.grid(row=4, column=1, sticky="NSWE", padx=2, pady=2)
        self.val.grid(row=5, column=1, columnspan=2,
                      sticky="NSWE", padx=2, pady=2)
        self.can.grid(row=5, column=0, sticky="NSWE", padx=2, pady=2)


###################################################################################
if __name__ == '__main__':
    """ standalone execution """
    app = DicoGIS()
    app.mainloop()
