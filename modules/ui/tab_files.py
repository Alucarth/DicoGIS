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
from Tkinter import IntVar, StringVar, Tk
from Tkinter import DISABLED, END
from tkFileDialog import askdirectory
from tkMessageBox import showinfo, showerror
from ttk import Checkbutton, Button, Entry, Frame, Label, Labelframe

import logging
from os import path
import threading    # handling various subprocesses
from time import strftime

# ##############################################################################
# ############ Globals ############
# #################################

today = strftime("%Y-%m-%d")
logger = logging.getLogger("DicoGIS")   # LOG

# ##############################################################################
# ########## Classes ###############
# ##################################


class TabFiles(Frame):

    def __init__(self, parent, txt=dict(), path_browser=None, path_var=""):
        """Instanciating the output workbook."""
        self.p = parent
        self.txt = txt
        Frame.__init__(self)

        # -- VARIABLES -------------------------------------------------------
        self.target_path = StringVar()
        # formats / type: vectors
        self.li_vectors_formats = (".shp", ".tab", ".kml",
                                   ".gml", ".geojson")  # vectors handled
        self.li_shp = []        # list for shapefiles path
        self.li_tab = []        # list for MapInfo tables path
        self.li_kml = []        # list for KML path
        self.li_gml = []        # list for GML path
        self.li_geoj = []       # list for GeoJSON paths
        self.li_gxt = []       # list for GXT paths
        self.li_vectors = []    # list for all vectors
        # formats / type: rasters
        self.li_raster = []     # list for rasters paths
        self.li_raster_formats = (".ecw", ".tif", ".jp2")   # raster handled
        # formats / type: file databases
        self.li_fdb = []        # list for all files databases
        self.li_egdb = []       # list for Esri File Geodatabases
        self.li_spadb = []      # list for Spatialite Geodatabases
        # formats / type: CAO/DAO
        self.li_cdao = []     # list for all CAO/DAO files
        self.li_dxf = []      # list for AutoCAD DXF paths
        self.li_dwg = []      # list for AutoCAD DWG paths
        self.li_dgn = []      # list for MicroStation DGN paths
        # formats / type: maps documents
        self.li_mapdocs = []  # list for all map & documents
        self.li_pdf = []      # list for GeoPDF path
        self.li_lyr = []      # list for LYR path
        self.li_mxd = []      # list for MXD path
        self.li_qgs = []      # list for QGS path

        # -- Source path -----------------------------------------------------
        self.FrPath = Labelframe(self,
                                 name='files',
                                 text=txt.get('gui_fr1', "Path"))

        # target folder
        self.lb_target = Label(self.FrPath, text=txt.get('gui_path'))
        self.ent_target = Entry(master=self.FrPath, width=35,
                                textvariable=self.target_path)
        self.btn_browse = Button(self.FrPath,
                                 text=u"\U0001F3AF " + txt.get('gui_choix', "Browse"),
                                 command=lambda: self.get_target_path(r"."),
                                 takefocus=True)
        self.btn_browse.focus_force()

        # widgets placement
        self.lb_target.grid(row=1, column=1, columnspan=1,
                            sticky="NSWE", padx=2, pady=2)
        self.ent_target.grid(row=1, column=2, columnspan=1,
                             sticky="NSWE", padx=2, pady=2)
        self.btn_browse.grid(row=1, column=3,
                             sticky="NSE", padx=2, pady=2)

        # -- Format filters --------------------------------------------------
        self.FrFilters = Labelframe(self,
                                    name='filters',
                                    text=txt.get('gui_fr3', "Filters"))
        # formats options
        self.opt_shp = IntVar(self.FrFilters)    # able/disable shapefiles
        self.opt_tab = IntVar(self.FrFilters)    # able/disable MapInfo tables
        self.opt_kml = IntVar(self.FrFilters)    # able/disable KML
        self.opt_gml = IntVar(self.FrFilters)    # able/disable GML
        self.opt_geoj = IntVar(self.FrFilters)   # able/disable GeoJSON
        self.opt_gxt = IntVar(self.FrFilters)    # able/disable GXT
        self.opt_egdb = IntVar(self.FrFilters)   # able/disable Esri FileGDB
        self.opt_spadb = IntVar(self.FrFilters)  # able/disable Spatalite DB
        self.opt_rast = IntVar(self.FrFilters)   # able/disable rasters
        self.opt_cdao = IntVar(self.FrFilters)   # able/disable CAO/DAO files
        self.opt_pdf = IntVar(self.FrFilters)    # able/disable Geospatial PDF
        self.opt_lyr = IntVar(self.FrFilters)    # able/disable Geospatial Lyr
        self.opt_mxd = IntVar(self.FrFilters)    # able/disable Geospatial MXD
        self.opt_qgs = IntVar(self.FrFilters)    # able/disable Geospatial QGS

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
        self.caz_lyr = Checkbutton(self.FrFilters,
                                   text=u'.lyr',
                                   variable=self.opt_lyr)
        self.caz_mxd = Checkbutton(self.FrFilters,
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
        self.caz_lyr.grid(row=3,
                          column=0,
                          columnspan=2,
                          sticky="NSWE",
                          padx=2, pady=2)
        self.caz_mxd.grid(row=3,
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
        self.FrPath.grid(row=3, column=1,
                         padx=2, pady=2, sticky="NSWE")
        self.FrFilters.grid(row=4, column=1,
                            padx=2, pady=2, sticky="NSWE")

    def get_target_path(self, def_rep):
        """Browse and insert the path of target folder."""
        print(self.target_path.get())
        foldername = askdirectory(parent=self.p,
                                  initialdir=def_rep,
                                  mustexist=True,
                                  title="")
        # deactivate Go button
        # self.val.config(state=DISABLED)
        # check if a folder has been choosen
        if foldername:
            try:
                self.tab_files.ent_target.delete(0, END)
                self.tab_files.ent_target.insert(0, foldername)
            except Exception as e:
                logger.debug(e)
                showinfo(title=self.txt.get('nofolder'),
                         message=self.txt.get('nofolder'))
                return
        else:
            pass
        # set the default output file
        self.output.delete(0, END)
        self.output.insert(0, "DicoGIS_{0}_{1}.xlsx"
                              .format(path.split(self.target_path.get()),
                                                 today))
        # count geofiles in a separated thread
        proc = threading.Thread(target=self.ligeofiles,
                                args=(foldername, ))
        proc.daemon = True
        proc.start()
        # end of function
        return foldername

# #############################################################################
# ##### Stand alone program ########
# ##################################

if __name__ == '__main__':
    """To test"""
    #
    def browse():
        print("Launch files browser")
        logger.info("Launch files browser")

    #
    root = Tk()
    target_path = StringVar(root)
    frame = TabFiles(root, path_browser=browse, path_var=target_path)
    frame.pack()
    root.mainloop()
