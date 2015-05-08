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

DGversion = "2.1.0-beta3"

###############################################################################
########### Libraries #############
###################################

# Standard library
from Tkinter import Tk, StringVar, IntVar, Image    # GUI
from Tkinter import W, PhotoImage, ACTIVE, DISABLED, END
from tkFileDialog import askdirectory, asksaveasfilename    # dialogs
from tkMessageBox import showinfo as info, showerror as avert
from ttk import Combobox, Progressbar, Style, Labelframe
from ttk import Label, Button, Entry, Radiobutton, Checkbutton  # widgets
import tkFont   # font library

from sys import exit, platform as opersys
from os import listdir, walk, path         # files and folder managing
from os import environ as env, access, R_OK
from time import strftime
from webbrowser import open_new
import threading    # handling various subprocesses

import ConfigParser  # to manipulate the options.ini file

import platform  # about operating systems

import logging      # log files
from logging.handlers import RotatingFileHandler

import subprocess

# Python 3 backported
from collections import OrderedDict as OD   # ordered dictionary

# 3rd party libraries
try:
    from osgeo import gdal
    from osgeo import ogr
    from osgeo import osr
    from osgeo.gdalconst import *
except ImportError:
    import gdal
    import ogr
    import osr
    from gdalconst import *

from xlwt import Workbook, easyxf, Formula  # excel writer

# Custom modules
from modules import Read_Rasters    # extractor for rasters files
from modules import Read_SHP        # extractor for shapefiles
from modules import Read_TAB        # extractor for MapInfo Tables
from modules import Read_KML        # extractor for KML
from modules import Read_GML        # extractor for GML
from modules import Read_GeoJSON    # extractor for GeoJSON
from modules import ReadGXT    # extractor for Geoconcept eXport Text
from modules import Read_PostGIS    # extractor for PostGIS databases
from modules import Read_GDB        # extractor for Esri FileGeoDataBase
from modules import Read_SpaDB      # extractor for Spatialite DB
from modules import Read_DXF        # extractor for AutoCAD DXF
from modules import Read_GeoPDF     # extractor for Geospatial PDF

from modules import TextsManager
from modules import MetricsManager

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
        u""" Main window constructor
        Creates 1 frame and 2 labelled subframes"""
        # creation and configuration of log file
        # see: http://sametmax.com/ecrire-des-logs-en-python/
        self.logger = logging.getLogger()
        logging.captureWarnings(True)
        self.logger.setLevel(logging.DEBUG)  # all errors will be get
        log_form = logging.Formatter('%(asctime)s || %(levelname)s || %(message)s')
        logfile = RotatingFileHandler('DicoGIS.log', 'a', 5000000, 1)
        logfile.setLevel(logging.DEBUG)
        logfile.setFormatter(log_form)
        self.logger.addHandler(logfile)
        self.logger.info('\t\t ============== DicoGIS =============')  # start
        self.logger.info('Version: {0}'.format(DGversion))

        # basics settings
        Tk.__init__(self)               # constructor of parent graphic class
        self.title(u'DicoGIS {0}'.format(DGversion))
        if opersys == 'win32':
            self.logger.info('Operating system: {0}'.format(platform.platform()))
            self.iconbitmap('DicoGIS.ico')    # windows icon
            self.uzer = env.get(u'USERNAME')
        elif opersys == 'linux2':
            self.logger.info('Operating system: {0}'.format(platform.platform()))
            self.uzer = env.get(u'USER')
            icon = Image("photo", file=r'data/img/DicoGIS_logo.gif')
            self.call('wm', 'iconphoto', self._w, icon)
            self.style = Style().theme_use('clam')
        elif opersys == 'darwin':
            self.logger.info('Operating system: {0}'.format(platform.platform()))
            self.uzer = env.get(u'USER')
        else:
            self.logger.warning('Operating system unknown')
            self.logger.info('Operating system: {0}'.format(platform.platform()))
        self.resizable(width=False, height=False)
        self.focus_force()

        # getting the GDAL version
        self.logger.info('GDAL version: {}'.format(gdal.__version__))

        ## Variables
        # settings
        self.num_folders = 0
        self.def_rep = ""       # default folder to search for
        self.def_lang = 'EN'    # default language to start
        self.today = strftime("%Y-%m-%d")   # date of the day
        li_lang = [lg[5:-4] for lg in listdir(r'data/locale')]  # languages
        self.blabla = OD()      # texts dictionary

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
        self.li_pdf = []    # list for GeoPDF path

        # dictionaries to store informations
        self.dico_layer = OD()      # dict for vectors informations
        self.dico_fields = OD()     # dict for fields informations
        self.dico_raster = OD()     # dict for rasters global informations
        self.dico_bands = OD()      # dict for bands informations
        self.dico_fdb = OD()        # dict for Esri FileGDB
        self.dico_cdao = OD()       # dict for CAO/DAO
        self.dico_pdf = OD()        # dict for Geospatial PDF
        self.dico_err = OD()        # errors list

        # metrics
        self.dico_metrics = OD()
        self.global_total_layers = 0
        self.global_total_fields = 0
        self.global_total_features = 0
        self.global_total_errors = 0
        self.global_total_warnings = 0
        self.global_total_srs_proj = 0
        self.global_total_srs_geog = 0
        self.global_total_srs_none = 0
        self.global_ignored = 0    # files ignored by an user filter
        self.global_dico_fields = OD()

        # GUI fonts
        ft_tit = tkFont.Font(family="Times", size=10, weight=tkFont.BOLD)

        # loading previous options
        self.load_settings()

        # fillfulling text
        TextsManager().load_texts(dico_texts=self.blabla,
                                  lang=self.def_lang,
                                  locale_folder=r'data/locale')

        # Frames
        self.FrPath = Labelframe(self,
                                 name='files',
                                 text=self.blabla.get('gui_fr1'))
        self.FrFilters = Labelframe(self,
                                    name='filters',
                                    text=self.blabla.get('gui_fr3'))
        self.FrDb = Labelframe(self,
                               name='database',
                               text=self.blabla.get('gui_fr2'))
        self.FrProg = Labelframe(self,
                                 name='progression',
                                 text=self.blabla.get('gui_prog'))
        self.FrOutp = Labelframe(self,
                                 name='output',
                                 text=self.blabla.get('gui_fr4'))
            ## Frame 1: path of geofiles
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
        # target folder
        self.labtarg = Label(self.FrPath, text=self.blabla.get('gui_path'))
        self.target = Entry(master=self.FrPath, width=35)
        self.browsetarg = Button(self.FrPath,       # browse button
                                 text=self.blabla.get('gui_choix'),
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

            ## Frame 2: Database
        # subframe
        self.FrProx = Labelframe(self.FrDb,
                                 name='proxy',
                                 text=self.blabla.get('gui_fr2'))

        # DB variables
        self.opt_pgvw = IntVar(self.FrDb)   # able/disable PostGIS views
        self.opt_proxy = IntVar(self.FrDb)  # proxy option

        self.host = StringVar(self.FrDb, 'localhost')
        self.port = IntVar(self.FrDb, 5432)
        self.dbnb = StringVar(self.FrDb)
        self.user = StringVar(self.FrDb, 'postgres')
        self.pswd = StringVar(self.FrDb)

        # proxy specific variables
        self.opt_ntlm = IntVar(self.FrProx, 0)  # proxy NTLM protocol option
        self.prox_server = StringVar(self.FrProx, 'proxy.server.com')
        self.prox_port = IntVar(self.FrProx, 80)
        self.prox_user = StringVar(self.FrProx, 'proxy_user')
        self.prox_pswd = StringVar(self.FrProx, '****')

        # Form widgets
        self.ent_H = Entry(self.FrDb, textvariable=self.host)
        self.ent_P = Entry(self.FrDb, textvariable=self.port, width=5)
        self.ent_D = Entry(self.FrDb, textvariable=self.dbnb)
        self.ent_U = Entry(self.FrDb, textvariable=self.user)
        self.ent_M = Entry(self.FrDb, textvariable=self.pswd, show='*')

        caz_pgvw = Checkbutton(self.FrDb,
                               text=self.blabla.get('gui_views'),
                               variable=self.opt_pgvw)
        caz_prox = Checkbutton(self.FrDb,
                               text=u'Proxy',
                               variable=self.opt_proxy,
                               command=lambda: self.proxy_form())
        # Label widgets
        self.lb_H = Label(self.FrDb, text=self.blabla.get('gui_host'))
        self.lb_P = Label(self.FrDb, text=self.blabla.get('gui_port'))
        self.lb_D = Label(self.FrDb, text=self.blabla.get('gui_db'))
        self.lb_U = Label(self.FrDb, text=self.blabla.get('gui_user'))
        self.lb_M = Label(self.FrDb, text=self.blabla.get('gui_mdp'))
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
        caz_prox.grid(row=4, column=2,
                      sticky="NSWE", padx=2, pady=2)

        # Proxy form widgets
        self.prox_ent_H = Entry(self.FrProx, textvariable=self.prox_server)
        self.prox_ent_P = Entry(self.FrProx, textvariable=self.prox_port)
        self.prox_ent_M = Entry(self.FrProx, textvariable=self.prox_pswd, show='*')

        self.prox_lb_H = Label(self.FrProx, text=self.blabla.get('gui_prox_server'))
        self.prox_lb_P = Label(self.FrProx, text=self.blabla.get('gui_port'))
        caz_ntlm = Checkbutton(self.FrProx,
                               text=u'NTLM',
                               variable=self.opt_ntlm)
        self.prox_lb_M = Label(self.FrProx, text=self.blabla.get('gui_mdp'))

        # proxy widgets placement
        self.prox_lb_H.grid(row=1, column=0,
                            sticky="NSEW", padx=2, pady=2)
        self.prox_ent_H.grid(row=1, column=1, columnspan=2,
                             sticky="NSEW", padx=2, pady=2)
        self.prox_lb_P.grid(row=1, column=2,
                            sticky="NSEW", padx=2, pady=2)
        self.prox_ent_P.grid(row=1, column=3, columnspan=2,
                             sticky="NSEW", padx=2, pady=2)
        caz_ntlm.grid(row=2, column=0,
                             sticky="NSEW", padx=2, pady=2)
        self.prox_lb_M.grid(row=2, column=1,
                            sticky="NSEW", padx=2, pady=2)
        self.prox_ent_M.grid(row=2, column=2, columnspan=2,
                             sticky="NSEW", padx=2, pady=2)

            ## Frame 3: Progression bar
        # variables
        self.status = StringVar(self.FrProg, '')
        # widgets
        self.prog_layers = Progressbar(self.FrProg,
                                       orient="horizontal")
        Label(master=self.FrProg,
              textvariable=self.status,
              foreground='DodgerBlue').pack()
        # widgets placement
        self.prog_layers.pack(expand=1, fill='both')

            ## Frame 4: Output configuration
        # widgets
        self.nameoutput = Label(self.FrOutp,
                                text=self.blabla.get('gui_fic'))
        self.output = Entry(self.FrOutp, width=35)
        # widgets placement
        self.nameoutput.grid(row=0, column=1,
                             sticky="NSWE", padx=2, pady=2)
        self.output.grid(row=0, column=2, columnspan=2,
                         sticky="NSWE", padx=2, pady=2)

            ## Main frame
        self.typo = IntVar(self, 1)    # type value (files or database)
        # Hola
        self.welcome = Label(self,
                             text=self.blabla.get('hi') + self.uzer,
                             font=ft_tit,
                             foreground="red2")
        # Imagen
        self.icone = PhotoImage(file=r'data/img/DicoGIS_logo.gif')
        Label(self,
              borderwidth=2,
              image=self.icone).grid(row=1,
                                     rowspan=5,
                                     column=0,
                                     padx=2,
                                     pady=2,
                                     sticky=W)
        # credits
        s = Style(self)
        s.configure('Kim.TButton', foreground='DodgerBlue', borderwidth=0)
        Button(self,
               text='by Julien M.\n      2015',
               style='Kim.TButton',
               command=lambda: open_new('https://github.com/Guts')).grid(row=6,
                                                                         padx=2,
                                                                         pady=2,
                                                                         sticky="WE")
        # language switcher
        self.ddl_lang = Combobox(self,
                                 values=li_lang,
                                 width=5)
        self.ddl_lang.current(li_lang.index(self.def_lang))
        self.ddl_lang.bind("<<ComboboxSelected>>", self.change_lang)

        # type switcher
        rd_file = Radiobutton(self,
                              text=self.blabla.get('gui_tab1'),
                              variable=self.typo,
                              value=1,
                              command=lambda: self.change_type())
        rd_pg = Radiobutton(self,
                            text='PostGIS',
                            variable=self.typo,
                            value=2,
                            command=lambda: self.change_type())
        # Basic buttons
        self.val = Button(self,
                          text=self.blabla.get('gui_go'),
                          state=ACTIVE,
                          command=lambda: self.process())
        self.can = Button(self, text=self.blabla.get('gui_quit'),
                          command=lambda: self.destroy())

        # widgets placement
        self.welcome.grid(row=1, column=1, columnspan=1, sticky="NS",
                          padx=2, pady=2)
        self.ddl_lang.grid(row=1, column=1, sticky="NSE", padx=2, pady=2)
        rd_file.grid(row=2, column=1, sticky="NSW", padx=2, pady=2)
        rd_pg.grid(row=2, column=1, sticky="NSE", padx=2, pady=2)
        self.val.grid(row=7, column=1, columnspan=2,
                      sticky="NSWE", padx=2, pady=2)
        self.can.grid(row=7, column=0, sticky="NSWE", padx=2, pady=2)
        # Frames placement
        rd_file.invoke()    # to provoc the type (frame 2) placement
        self.FrProg.grid(row=5, column=1, sticky="NSWE", padx=2, pady=2)
        self.FrOutp.grid(row=6, column=1, sticky="NSWE", padx=2, pady=2)

        # load previous settings
        self.load_settings()
        self.proxy_form()


    def proxy_form(self):
        u"""
        Activate or deactivate the proxy configuration form.
        """
        if self.opt_proxy.get():
            self.FrProx.grid(row=5, column=0, columnspan=4,
                             sticky="NSWE", padx=2, pady=2)
        else:
            self.FrProx.grid_forget()
        # end of function
        return

    def load_settings(self):
        u""" load settings from last execution """
        confile = 'options.ini'
        config = ConfigParser.RawConfigParser()
        try:
            config.read(confile)
            # basics
            self.def_lang = config.get('basics', 'def_codelang')
            self.def_rep = config.get('basics', 'def_rep')
            # filters
            self.opt_shp.set(config.get('filters', 'opt_shp'))
            self.opt_tab.set(config.get('filters', 'opt_tab'))
            self.opt_kml.set(config.get('filters', 'opt_kml'))
            self.opt_gml.set(config.get('filters', 'opt_gml'))
            self.opt_geoj.set(config.get('filters', 'opt_geoj'))
            self.opt_gxt.set(config.get('filters', 'opt_gxt'))
            self.opt_rast.set(config.get('filters', 'opt_rast'))
            self.opt_egdb.set(config.get('filters', 'opt_egdb'))
            self.opt_spadb.set(config.get('filters', 'opt_spadb'))
            self.opt_cdao.set(config.get('filters', 'opt_cdao'))
            self.opt_pdf.set(config.get('filters', 'opt_pdf'))
            # database settings
            self.host.set(config.get('database', 'host'))
            self.port.set(config.get('database', 'port'))
            self.dbnb.set(config.get('database', 'db_name'))
            self.user.set(config.get('database', 'user'))
            self.opt_pgvw.set(config.get('database', 'opt_views'))
            # proxy settings
            self.opt_proxy.set(config.get('proxy', 'proxy_needed'))
            self.opt_ntlm.set(config.get('proxy', 'proxy_type'))
            self.prox_server.set(config.get('proxy', 'proxy_server'))
            self.prox_port.set(config.get('proxy', 'proxy_port'))
            self.prox_user.set(config.get('proxy', 'proxy_user'))
            # log
            self.logger.info('Last options loaded')
        except Exception as e:
            # log
            self.logger.info('1st use: {0}'.format(e))

        # End of function
        return self.def_rep, self.def_lang

    def save_settings(self):
        u""" save last options in order to make the next excution more easy """
        confile = 'options.ini'
        config = ConfigParser.RawConfigParser()
        # add sections
        config.add_section('config')
        config.add_section('basics')
        config.add_section('filters')
        config.add_section('database')
        config.add_section('proxy')
        # config
        config.set('config', 'DicoGIS_version', DGversion)
        config.set('config', 'OS', platform.platform())
        # basics
        config.set('basics', 'def_codelang', self.ddl_lang.get())
        if self.target.get():
            config.set('basics', 'def_rep', self.target.get())
        else:
            config.set('basics', 'def_rep', self.def_rep)
        # filters
        config.set('filters', 'opt_shp', self.opt_shp.get())
        config.set('filters', 'opt_tab', self.opt_tab.get())
        config.set('filters', 'opt_kml', self.opt_kml.get())
        config.set('filters', 'opt_gml', self.opt_gml.get())
        config.set('filters', 'opt_geoj', self.opt_geoj.get())
        config.set('filters', 'opt_gxt', self.opt_gxt.get())
        config.set('filters', 'opt_rast', self.opt_rast.get())
        config.set('filters', 'opt_egdb', self.opt_egdb.get())
        config.set('filters', 'opt_spadb', self.opt_spadb.get())
        config.set('filters', 'opt_cdao', self.opt_cdao.get())
        config.set('filters', 'opt_pdf', self.opt_pdf.get())
        # database settings
        config.set('database', 'host', self.host.get())
        config.set('database', 'port', self.port.get())
        config.set('database', 'db_name', self.dbnb.get())
        config.set('database', 'user', self.user.get())
        config.set('database', 'opt_views', self.opt_pgvw.get())
        # proxy settings
        config.set('proxy', 'proxy_needed', self.opt_proxy.get())
        config.set('proxy', 'proxy_type', self.opt_ntlm.get())
        config.set('proxy', 'proxy_server', self.prox_server.get())
        config.set('proxy', 'proxy_port', self.prox_port.get())
        config.set('proxy', 'proxy_user', self.prox_user.get())

        # Writing the configuration file
        with open(confile, 'wb') as configfile:
            try:
                config.write(configfile)
                self.logger.info('Options saved')
            except (UnicodeEncodeError, UnicodeDecodeError), e:
                self.logger.error("Options couldn't be saved because of: {0}".format(e))

        # End of function
        return config

    def change_lang(self, event):
        u""" update the texts dictionary with the language selected """
        new_lang = event.widget.get()
        self.logger.info('\tLanguage switched to: {0}'.format(event.widget.get()))
        # change to the new language selected
        TextsManager().load_texts(dico_texts=self.blabla,
                                  lang=new_lang,
                                  locale_folder=r'data/locale')
        # update widgets text
        self.welcome.config(text=self.blabla.get('hi') + self.uzer)
        self.can.config(text=self.blabla.get('gui_quit'))
        self.FrPath.config(text=self.blabla.get('gui_fr1'))
        self.FrDb.config(text=self.blabla.get('gui_fr2'))
        self.FrFilters.config(text=self.blabla.get('gui_fr3'))
        self.FrOutp.config(text=self.blabla.get('gui_fr4'))
        self.FrProg.config(text=self.blabla.get('gui_prog'))
        self.labtarg.config(text=self.blabla.get('gui_path'))
        self.browsetarg.config(text=self.blabla.get('gui_choix'))
        self.val.config(text=self.blabla.get('gui_go'))
        self.nameoutput.config(text=self.blabla.get('gui_fic'))
        self.lb_H.config(text=self.blabla.get('gui_host'))
        self.lb_P.config(text=self.blabla.get('gui_port'))
        self.lb_D.config(text=self.blabla.get('gui_db'))
        self.lb_U.config(text=self.blabla.get('gui_user'))
        self.lb_M.config(text=self.blabla.get('gui_mdp'))

        # End of function
        return self.blabla

    def change_type(self):
        u""" switch between the available types of data (files or database) """
        if self.typo.get() == 1:
            self.logger.info('Type switched to: files structure')
            self.FrDb.grid_forget()
            self.status.set('')
            self.FrPath.grid(row=3, column=1, padx=2, pady=2,
                             sticky="NSWE")
            self.FrFilters.grid(row=4, column=1, padx=2, pady=2,
                                sticky="NSWE")
        elif self.typo.get() == 2:
            self.logger.info('Type switched to: database')
            self.FrPath.grid_forget()
            self.FrFilters.grid_forget()
            self.status.set('')
            self.FrDb.grid(row=3, column=1, sticky="NSWE", padx=2, pady=2)
        # End of function
        return self.typo

    def setpathtarg(self):
        """ ...browse and insert the path of target folder """
        foldername = askdirectory(parent=self,
                                  initialdir=self.def_rep,
                                  mustexist=True,
                                  title=self.blabla.get('gui_cible'))
        # deactivate Go button
        self.val.config(state=DISABLED)
        # check if a folder has been choosen
        if foldername:
            try:
                self.target.delete(0, END)
                self.target.insert(0, foldername)
            except:
                info(title=self.blabla.get('nofolder'),
                     message=self.blabla.get('nofolder'))
                return
        else:
            pass
        # set the default output file
        self.output.delete(0, END)
        self.output.insert(0,
                           "DicoGIS_{0}_{1}.xls".format(path.split(self.target.get())[1],
                                                        self.today))
        # count geofiles in a separated thread
        proc = threading.Thread(target=self.ligeofiles,
                                args=(foldername, ))
        proc.daemon = True
        proc.start()
        # end of function
        return foldername

    def ligeofiles(self, foldertarget):
        u""" List compatible geo-files stored into
        the folders structure """
        # reseting global variables
        self.li_shp = []
        self.li_tab = []
        self.li_kml = []
        self.li_gml = []
        self.li_geoj = []
        self.li_gxt = []
        self.li_vectors = []
        self.li_dxf = []
        self.li_dwg = []
        self.li_dgn = []
        self.li_cdao = []
        self.li_raster = []
        self.li_fdb = []
        self.li_egdb = []
        self.li_spadb = []
        self.li_pdf = []
        self.browsetarg.config(state=DISABLED)

        # Looping in folders structure
        self.status.set(self.blabla.get('gui_prog1'))
        self.prog_layers.start()
        self.logger.info('Begin of folders parsing')
        for root, dirs, files in walk(foldertarget):
            self.num_folders = self.num_folders + len(dirs)
            for d in dirs:
                """ looking for File Geodatabase among directories """
                try:
                    unicode(path.join(root, d))
                    full_path = path.join(root, d)
                except UnicodeDecodeError:
                    full_path = path.join(root, d.decode('latin1'))
                if full_path[-4:].lower() == '.gdb':
                    # add complete path of Esri FileGeoDatabase
                    self.li_egdb.append(path.abspath(full_path))
                else:
                    pass
            for f in files:
                """ looking for files with geographic data """
                try:
                    unicode(path.join(root, f))
                    full_path = path.join(root, f)
                except UnicodeDecodeError:
                    full_path = path.join(root, f.decode('latin1'))
                # Looping on files contained
                if path.splitext(full_path.lower())[1].lower() == '.shp'\
                   and (path.isfile('{0}.dbf'.format(full_path[:-4]))
                        or path.isfile('{0}.DBF'.format(full_path[:-4])))\
                   and (path.isfile('{0}.shx'.format(full_path[:-4]))
                        or path.isfile('{0}.SHX'.format(full_path[:-4]))):
                    """ listing compatible shapefiles """
                    # add complete path of shapefile
                    self.li_shp.append(full_path)
                elif path.splitext(full_path.lower())[1] == '.tab'\
                    and (path.isfile(full_path[:-4] + '.dat')
                         or path.isfile(full_path[:-4] + '.DAT'))\
                    and (path.isfile(full_path[:-4] + '.map')
                         or path.isfile(full_path[:-4] + '.MAP'))\
                    and (path.isfile(full_path[:-4] + '.id')
                         or path.isfile(full_path[:-4] + '.ID')):
                    """ listing MapInfo tables """
                    # add complete path of MapInfo file
                    self.li_tab.append(full_path)
                elif path.splitext(full_path.lower())[1] == '.kml'\
                    or path.splitext(full_path.lower())[1] == '.kmz':
                    """ listing KML and KMZ """
                    # add complete path of KML file
                    self.li_kml.append(full_path)
                elif path.splitext(full_path.lower())[1] == '.gml':
                    """ listing GML """
                    # add complete path of GML file
                    self.li_gml.append(full_path)
                elif path.splitext(full_path.lower())[1] == '.geojson':
                    """ listing GeoJSON """
                    # add complete path of GeoJSON file
                    self.li_geoj.append(full_path)
                elif path.splitext(full_path.lower())[1] == '.pdf':
                    """ listing GeoPDF """
                    # add complete path of PDF file
                    self.li_pdf.append(full_path)
                elif path.splitext(full_path.lower())[1] == '.gxt':
                    """ listing Geoconcept eXport Text (GXT) """
                    # add complete path of GXT file
                    self.li_gxt.append(full_path)
                elif path.splitext(full_path.lower())[1] in self.li_raster_formats:
                    """ listing compatible rasters """
                    # add complete path of raster file
                    self.li_raster.append(full_path)
                elif path.splitext(full_path.lower())[1] == '.dxf':
                    """ listing DXF """
                    # add complete path of DXF file
                    self.li_dxf.append(full_path)
                elif path.splitext(full_path.lower())[1] == '.dwg':
                    """ listing DWG """
                    # add complete path of DWG file
                    self.li_dwg.append(full_path)
                elif path.splitext(full_path.lower())[1] == '.dgn':
                    """ listing MicroStation DGN """
                    # add complete path of DGN file
                    self.li_dgn.append(full_path)
                elif path.splitext(full_path.lower())[1] == '.sqlite':
                    """ listing Spatialite DB """
                    # add complete path of DGN file
                    self.li_spadb.append(full_path)
                else:
                    continue

        # grouping CAO/DAO files
        self.li_cdao.extend(self.li_dxf)
        self.li_cdao.extend(self.li_dwg)
        self.li_cdao.extend(self.li_dgn)
        # grouping File geodatabases
        self.li_fdb.extend(self.li_egdb)
        self.li_fdb.extend(self.li_spadb)
        # end of listing
        self.prog_layers.stop()
        self.logger.info('End of folders parsing: {0} shapefiles - \
          {1} tables (MapInfo) - \
          {2} KML - \
          {3} GML - \
          {4} GeoJSON\
          {5} rasters - \
          {6} Esri FileGDB - \
          {7} Spatialite - \
          {8} CAO/DAO - \
          {9} PDF - \
          {10} PDF - \
          in {11}{12}'.format(len(self.li_shp), len(self.li_tab),
                              len(self.li_kml), len(self.li_gml),
                              len(self.li_geoj), len(self.li_raster),
                              len(self.li_egdb), len(self.li_spadb),
                              len(self.li_cdao), len(self.li_pdf),
                              len(self.li_gxt),
                              self.num_folders,
                              self.blabla.get('log_numfold')))
        # grouping vectors lists
        self.li_vectors.extend(self.li_shp)
        self.li_vectors.extend(self.li_tab)
        self.li_vectors.extend(self.li_kml)
        self.li_vectors.extend(self.li_gml)
        self.li_vectors.extend(self.li_geoj)
        self.li_vectors.extend(self.li_gxt)

        # Lists ordering and tupling
        self.li_shp.sort()
        self.li_shp = tuple(self.li_shp)
        self.li_tab.sort()
        self.li_tab = tuple(self.li_tab)
        self.li_raster.sort()
        self.li_raster = tuple(self.li_raster)
        self.li_kml.sort()
        self.li_kml = tuple(self.li_kml)
        self.li_gml.sort()
        self.li_gml = tuple(self.li_gml)
        self.li_geoj.sort()
        self.li_geoj = tuple(self.li_geoj)
        self.li_gxt.sort()
        self.li_gxt = tuple(self.li_gxt)
        self.li_egdb.sort()
        self.li_egdb = tuple(self.li_egdb)
        self.li_spadb.sort()
        self.li_spadb = tuple(self.li_spadb)
        self.li_fdb.sort()
        self.li_fdb = tuple(self.li_fdb)
        self.li_dxf.sort()
        self.li_dxf = tuple(self.li_dxf)
        self.li_dwg.sort()
        self.li_dwg = tuple(self.li_dwg)
        self.li_dgn.sort()
        self.li_dgn = tuple(self.li_dgn)
        self.li_cdao.sort()
        self.li_cdao = tuple(self.li_cdao)
        self.li_pdf.sort()
        self.li_pdf = tuple(self.li_pdf)
        # status message
        self.status.set(u'{0} shapefiles - \
{1} tables (MapInfo) - \
{2} KML - \
{3} GML - \
{4} GeoJSON - \
{5} GXT\
\n{6} rasters - \
{7} file databases - \
{8} CAO/DAO - \
{9} PDF - \
in {10}{11}'.format(len(self.li_shp),
                  len(self.li_tab),
                  len(self.li_kml),
                  len(self.li_gml),
                  len(self.li_geoj),
                  len(self.li_gxt),
                  len(self.li_raster),
                  len(self.li_fdb),
                  len(self.li_cdao),
                  len(self.li_pdf),
                  self.num_folders,
                  self.blabla.get('log_numfold')))

        # reactivating the buttons
        self.browsetarg.config(state=ACTIVE)
        self.val.config(state=ACTIVE)
        # End of function
        return foldertarget, self.li_shp, self.li_tab, self.li_kml,\
            self.li_gml, self.li_geoj, self.li_gxt, self.li_raster,\
            self.li_egdb, self.li_dxf, self.li_dwg, self.li_dgn,\
            self.li_cdao, self.li_fdb, self.li_spadb

    def process(self):
        """ check needed info and launch different processes """
        # saving settings
        self.save_settings()
        self.val.config(state=DISABLED)
        # process files or PostGIS database
        if self.typo.get() == 1:
            self.logger.info('=> files process started')
            self.process_files()
        elif self.typo.get() == 2:
            self.logger.info('=> DB process started')
            self.check_fields()
        else:
            pass
        self.val.config(state=ACTIVE)
        # end of function
        return self.typo.get()

    def process_files(self):
        u""" launch the different processes """
        # check if at least a format has been choosen
        if (self.opt_shp.get() + self.opt_tab.get() + self.opt_kml.get() +
           self.opt_gml.get() + self.opt_geoj.get() + self.opt_rast.get() +
           self.opt_egdb.get() + self.opt_cdao.get() + self.opt_pdf.get()):
            pass
        else:
            avert('DicoGIS - User error', self.blabla.get('noformat'))
            return
        # check if there are some layers into the folder structure
        if (len(self.li_vectors)
          + len(self.li_raster)
          + len(self.li_fdb)
          + len(self.li_cdao)
          + len(self.li_pdf)):
            pass
        else:
            avert('DicoGIS - User error', self.blabla.get('nodata'))
            return
        # creating the Excel workbook
        self.configexcel()
        self.logger.info('Excel file created')
        # configuring the progress bar
        total_files = 0
        if self.opt_shp.get() and len(self.li_shp) > 0:
            total_files += len(self.li_shp)
        else:
            pass
        if self.opt_tab.get() and len(self.li_tab) > 0:
            total_files += len(self.li_tab)
        else:
            pass
        if self.opt_kml.get()and len(self.li_kml) > 0:
            total_files += len(self.li_kml)
        else:
            pass
        if self.opt_gml.get() and len(self.li_gml) > 0:
            total_files += len(self.li_gml)
        else:
            pass
        if self.opt_geoj.get() and len(self.li_geoj) > 0:
            total_files += len(self.li_geoj)
        else:
            pass
        if self.opt_gxt.get() and len(self.li_gxt) > 0:
            total_files += len(self.li_gxt)
        else:
            pass
        if self.opt_rast.get() and len(self.li_raster) > 0:
            total_files += len(self.li_raster)
        else:
            pass
        if self.opt_egdb.get() and len(self.li_egdb) > 0:
            total_files += len(self.li_egdb)
        else:
            pass
        if self.opt_spadb.get() and len(self.li_spadb) > 0:
            total_files += len(self.li_spadb)
        else:
            pass
        if self.opt_cdao.get() and len(self.li_cdao) > 0:
            total_files += len(self.li_cdao)
        else:
            pass
        if self.opt_pdf.get() and len(self.li_pdf) > 0:
            total_files += len(self.li_pdf)
        else:
            pass
        self.prog_layers["maximum"] = total_files
        self.prog_layers["value"]

        # initializing metrics
        statistiker = MetricsManager(self.dico_metrics).init_metrics()
        print statistiker

        # getting the infos from files selected
        # line_folders = 1    # line rank of directories dictionary
        line_vectors = 1    # line rank of vectors dictionary
        line_rasters = 1    # line rank of rasters dictionary
        line_fdb = 1        # line rank of File DB dictionary
        line_cdao = 1       # line rank of CAO/DAO dictionary
        line_maps = 1       # line rank of maps & plans dictionary

        if self.opt_shp.get() and len(self.li_shp) > 0:
            self.logger.info('\n\tProcessing shapefiles: start')
            for shp in self.li_shp:
                """ looping on shapefiles list """
                self.status.set(path.basename(shp))
                self.logger.info('\n' + shp)
                # increment the progress bar
                self.prog_layers["value"] = self.prog_layers["value"] + 1
                self.update()
                # reset recipient data
                self.dico_layer.clear()
                self.dico_fields.clear()
                # getting the informations
                try:
                    Read_SHP(path.abspath(shp),
                             self.dico_layer,
                             self.dico_fields,
                             'Esri shapefiles',
                             self.blabla)
                    self.logger.info('\t Infos OK')
                except (AttributeError, RuntimeError, Exception) as e:
                    """ empty files """
                    self.logger.error(e)
                    self.prog_layers["value"] = self.prog_layers["value"] + 1
                    continue
                # writing to the Excel dictionary
                self.dictionarize_vectors(self.dico_layer,
                                          self.dico_fields,
                                          self.feuyVC,
                                          line_vectors)
                self.logger.info('\t Wrote into the dictionary')
                # writing to the Excel dictionary
                statistiker.store_metrics(self.dico_layer, self.dico_fields, "vector")
                self.logger.info('\t Added to global metrics')
                # increment the line number
                line_vectors = line_vectors + 1
        else:
            self.logger.info('\tIgnoring {0} shapefiles'.format(len(self.li_shp)))
            pass

        if self.opt_tab.get() and len(self.li_tab) > 0:
            self.logger.info('\n\tProcessing MapInfo tables: start')
            for tab in self.li_tab:
                """ looping on MapInfo tables list """
                self.status.set(path.basename(tab))
                self.logger.info('\n' + tab)
                # increment the progress bar
                self.prog_layers["value"] = self.prog_layers["value"] + 1
                self.update()
                # reset recipient data
                self.dico_layer.clear()
                self.dico_fields.clear()
                # getting the informations
                try:
                    Read_TAB(path.abspath(tab),
                             self.dico_layer,
                             self.dico_fields,
                             'MapInfo tab',
                             self.blabla)
                    self.logger.info('\t Infos OK')
                except (AttributeError, RuntimeError, Exception) as e:
                    """ empty files """
                    self.logger.error(e)
                    self.prog_layers["value"] = self.prog_layers["value"] + 1
                    continue
                # writing to the Excel dictionary
                self.dictionarize_vectors(self.dico_layer,
                                          self.dico_fields,
                                          self.feuyVC, line_vectors)
                self.logger.info('\t Wrote into the dictionary')
                # increment the line number
                line_vectors = line_vectors + 1
        else:
            self.logger.info('\tIgnoring {0} MapInfo tables'.format(len(self.li_tab)))
            pass

        if self.opt_kml.get() and len(self.li_kml) > 0:
            self.logger.info('\n\tProcessing KML-KMZ: start')
            for kml in self.li_kml:
                """ looping on KML/KMZ list """
                self.status.set(path.basename(kml))
                self.logger.info('\n' + kml)
                # increment the progress bar
                self.prog_layers["value"] = self.prog_layers["value"] + 1
                self.update()
                # reset recipient data
                self.dico_layer.clear()
                self.dico_fields.clear()
                # getting the informations
                try:
                    Read_KML(path.abspath(kml),
                             self.dico_layer,
                             self.dico_fields,
                             'Google KML/KMZ',
                             self.blabla)
                    self.logger.info('\t Infos OK')
                except (AttributeError, RuntimeError, Exception) as e:
                    """ empty files """
                    self.logger.error(e)
                    self.prog_layers["value"] = self.prog_layers["value"] + 1
                    continue
                # writing to the Excel dictionary
                self.dictionarize_vectors(self.dico_layer,
                                          self.dico_fields,
                                          self.feuyVC,
                                          line_vectors)
                self.logger.info('\t Wrote into the dictionary')
                # increment the line number
                line_vectors = line_vectors + 1
        else:
            self.logger.info('\tIgnoring {0} KML'.format(len(self.li_kml)))
            pass

        if self.opt_gml.get() and len(self.li_gml) > 0:
            self.logger.info('\n\tProcessing GML: start')
            for gml in self.li_gml:
                """ looping on GML list """
                self.status.set(path.basename(gml))
                self.logger.info('\n' + gml)
                # increment the progress bar
                self.prog_layers["value"] = self.prog_layers["value"] + 1
                self.update()
                # reset recipient data
                self.dico_layer.clear()
                self.dico_fields.clear()
                # getting the informations
                try:
                    Read_GML(path.abspath(gml),
                             self.dico_layer,
                             self.dico_fields,
                             'GML',
                             self.blabla)
                    self.logger.info('\t Infos OK')
                except (AttributeError, RuntimeError, Exception) as e:
                    """ empty files """
                    self.logger.error(e)
                    self.prog_layers["value"] = self.prog_layers["value"] + 1
                    continue
                # writing to the Excel dictionary
                self.dictionarize_vectors(self.dico_layer,
                                          self.dico_fields,
                                          self.feuyVC, line_vectors)
                self.logger.info('\t Wrote into the dictionary')
                # increment the line number
                line_vectors = line_vectors + 1
        else:
            self.logger.info('\tIgnoring {0} GML'.format(len(self.li_gml)))
            pass

        if self.opt_geoj.get() and len(self.li_geoj) > 0:
            self.logger.info('\n\tProcessing GeoJSON: start')
            for geojson in self.li_geoj:
                """ looping on GeoJSON list """
                self.status.set(path.basename(geojson))
                self.logger.info('\n' + geojson)
                # increment the progress bar
                self.prog_layers["value"] = self.prog_layers["value"] + 1
                self.update()
                # reset recipient data
                self.dico_layer.clear()
                self.dico_fields.clear()
                # getting the informations
                try:
                    Read_GeoJSON(path.abspath(geojson),
                                 self.dico_layer,
                                 self.dico_fields,
                                 'GeoJSON',
                                 self.blabla)
                    self.logger.info('\t Infos OK')
                except (AttributeError, RuntimeError, Exception) as e:
                    """ empty files """
                    self.logger.error(e)
                    self.prog_layers["value"] = self.prog_layers["value"] + 1
                    continue
                # writing to the Excel dictionary
                self.dictionarize_vectors(self.dico_layer,
                                          self.dico_fields,
                                          self.feuyVC,
                                          line_vectors)
                self.logger.info('\t Wrote into the dictionary')
                # increment the line number
                line_vectors = line_vectors + 1
        else:
            self.logger.info('\tIgnoring {0} GeoJSON'.format(len(self.li_geoj)))
            pass

        if self.opt_gxt.get() and len(self.li_gxt) > 0:
            self.logger.info('\n\tProcessing GXT: start')
            for gxtpath in self.li_gxt:
                """ looping on gxt list """
                self.status.set(path.basename(gxtpath))
                self.logger.info('\n' + gxtpath)
                # increment the progress bar
                self.prog_layers["value"] = self.prog_layers["value"] + 1
                self.update()
                # reset recipient data
                self.dico_layer.clear()
                self.dico_fields.clear()
                # getting the informations
                try:
                    Read_SHP(path.abspath(gxtpath),
                             self.dico_layer,
                             self.dico_fields,
                             'Geoconcept eXport Text',
                             self.blabla)
                    self.logger.info('\t Infos OK')
                except (AttributeError, RuntimeError, Exception) as e:
                    """ empty files """
                    self.logger.error(e)
                    self.prog_layers["value"] = self.prog_layers["value"] + 1
                    continue
                # writing to the Excel dictionary
                self.dictionarize_vectors(self.dico_layer,
                                          self.dico_fields,
                                          self.feuyVC,
                                          line_vectors)
                self.logger.info('\t Wrote into the dictionary')
                # increment the line number
                line_vectors = line_vectors + 1
        else:
            self.logger.info('\tIgnoring {0} Geoconcept eXport Text'.format(len(self.li_gxt)))
            pass

        if self.opt_rast.get() and len(self.li_raster) > 0:
            self.logger.info('\n\tProcessing rasters: start')
            for raster in self.li_raster:
                """ looping on rasters list """
                self.status.set(path.basename(raster))
                self.logger.info('\n' + raster)
                # increment the progress bar
                self.prog_layers["value"] = self.prog_layers["value"] + 1
                self.update()
                # reset recipient data
                self.dico_raster.clear()
                self.dico_bands.clear()
                # getting the informations
                try:
                    Read_Rasters(path.abspath(raster),
                                 self.dico_raster,
                                 self.dico_bands,
                                 path.splitext(raster)[1],
                                 self.blabla)
                    self.logger.info('\t Infos OK')
                except (AttributeError, RuntimeError, Exception) as e:
                    """ empty files """
                    self.logger.error(e)
                    self.prog_layers["value"] = self.prog_layers["value"] + 1
                    continue
                # writing to the Excel dictionary
                self.dictionarize_rasters(self.dico_raster,
                                          self.dico_bands,
                                          self.feuyRS,
                                          line_rasters)
                self.logger.info('\t Wrote into the dictionary')
                # increment the line number
                line_rasters = line_rasters + 1
        else:
            self.logger.info('\tIgnoring {0} rasters'.format(len(self.li_raster)))
            pass

        if self.opt_egdb.get() and len(self.li_egdb) > 0:
            self.logger.info('\n\tProcessing Esri FileGDB: start')
            for gdb in self.li_egdb:
                """ looping on FileGDB list """
                self.status.set(path.basename(gdb))
                self.logger.info('\n' + gdb)
                # increment the progress bar
                self.prog_layers["value"] = self.prog_layers["value"] + 1
                self.update()
                # reset recipient data
                self.dico_fdb.clear()
                self.dico_fields.clear()
                # getting the informations
                try:
                    Read_GDB(path.abspath(gdb),
                             self.dico_fdb,
                             'Esri FileGeoDataBase',
                             self.blabla)
                    self.logger.info('\t Infos OK')
                except (AttributeError, RuntimeError, Exception) as e:
                    """ empty files """
                    self.logger.error(e)
                    self.prog_layers["value"] = self.prog_layers["value"] + 1
                    continue
                # writing to the Excel dictionary
                self.dictionarize_fdb(self.dico_fdb,
                                      self.feuyFGDB,
                                      line_fdb)
                self.logger.info('\t Wrote into the dictionary')
                # increment the line number
                line_fdb += self.dico_fdb.get('layers_count') + 1
        else:
            self.logger.info('\tIgnoring {0} Esri FileGDB'.format(len(self.li_egdb)))
            pass

        if self.opt_spadb.get() and len(self.li_spadb) > 0:
            self.logger.info('\n\tProcessing Spatialite DB: start')
            for spadb in self.li_spadb:
                """ looping on Spatialite DBs list """
                self.status.set(path.basename(spadb))
                self.logger.info('\n' + spadb)
                # increment the progress bar
                self.prog_layers["value"] = self.prog_layers["value"] + 1
                self.update()
                # reset recipient data
                self.dico_fdb.clear()
                self.dico_fields.clear()
                # getting the informations
                try:
                    Read_SpaDB(path.abspath(spadb),
                               self.dico_fdb,
                               'Spatialite',
                               self.blabla)
                    self.logger.info('\t Infos OK')
                except (AttributeError, RuntimeError, Exception) as e:
                    """ empty files """
                    self.logger.error(e)
                    self.prog_layers["value"] = self.prog_layers["value"] + 1
                    continue
                # writing to the Excel dictionary
                self.dictionarize_fdb(self.dico_fdb,
                                      self.feuyFGDB,
                                      line_fdb)
                self.logger.info('\t Wrote into the dictionary')
                # increment the line number
                line_fdb += self.dico_fdb.get('layers_count') + 1
        else:
            self.logger.info('\tIgnoring {0} Spatialite DB'.format(len(self.li_spadb)))
            pass

        if self.opt_cdao.get() and len(self.li_cdao) > 0:
            self.logger.info('\n\tProcessing CAO/DAO: start')
            for dxf in self.li_dxf:
                """ looping on DXF list """
                self.status.set(path.basename(dxf))
                self.logger.info('\n' + dxf)
                # increment the progress bar
                self.prog_layers["value"] = self.prog_layers["value"] + 1
                self.update()
                # reset recipient data
                self.dico_cdao.clear()
                # getting the informations
                try:
                    Read_DXF(path.abspath(dxf),
                             self.dico_cdao,
                             'AutoCAD DXF',
                             self.blabla)
                    self.logger.info('\t Infos OK')
                except (AttributeError, RuntimeError, Exception) as e:
                    """ empty files """
                    self.logger.error(e)
                    self.prog_layers["value"] = self.prog_layers["value"] + 1
                    continue
                # writing to the Excel dictionary
                self.dictionarize_cdao(self.dico_cdao,
                                       self.feuyCDAO,
                                       line_cdao)
                self.logger.info('\t Wrote into the dictionary')
                # increment the line number
                line_cdao += self.dico_cdao.get('layers_count') + 1

            for dwg in self.li_dwg:
                """ looping on DWG list """
                self.status.set(path.basename(dwg))
                self.logger.info('\n' + dwg)
                # increment the progress bar
                self.prog_layers["value"] = self.prog_layers["value"] + 1
                self.update()
                # just writing filename and link to parent folder
                self.feuyCDAO.write(line_cdao, 0, path.basename(dwg))

                # Path of parent folder formatted to be a hyperlink
                try:
                    link = 'HYPERLINK("{0}"; "{1}")'.format(path.dirname(dwg),
                                                            self.blabla.get('browse'))
                except UnicodeDecodeError:
                    # write a notification into the log file
                    self.logger.warning('Path name with special letters: {}'.format(path.dirname(dwg).decode('utf8')))
                    # decode the fucking path name
                    link = 'HYPERLINK("{0}"; "{1}")'.format(path.dirname(dwg).decode('utf8'),
                                                            self.blabla.get('browse'))

                self.feuyCDAO.write(line_cdao, 1, Formula(link), self.url)

                # Name of parent folder
                self.feuyCDAO.write(line_cdao, 2, path.basename(path.dirname(dwg)))

                # logging
                self.logger.info('\t Wrote into the dictionary')
                # increment the line number
                line_cdao += 1
        else:
            self.logger.info('\tIgnoring {0} CAO/DAO files'.format(len(self.li_cdao)))
            pass

        if self.opt_pdf.get() and len(self.li_pdf) > 0:
            self.logger.info('\n\tProcessing Geospatial PDF: start')
            for pdf in self.li_pdf:
                """ looping on PDF list """
                self.status.set(path.basename(pdf))
                self.logger.info('\n' + pdf)
                # increment the progress bar
                self.prog_layers["value"] = self.prog_layers["value"] + 1
                self.update()
                # reset recipient data
                self.dico_pdf.clear()
                # getting the informations
                try:
                    Read_GeoPDF(path.abspath(pdf),
                                self.dico_pdf,
                                'Geospatial PDF',
                                self.blabla)
                    self.logger.info('\t Infos OK')
                except (AttributeError, RuntimeError, Exception) as e:
                    """ empty files """
                    self.logger.error(e)
                    self.prog_layers["value"] = self.prog_layers["value"] + 1
                    continue
                # writing to the Excel dictionary
                self.dictionarize_mapdocs(self.dico_pdf,
                                          self.feuyMAPS,
                                          line_maps)
                self.logger.info('\t Wrote into the dictionary')
                # increment the line number
                line_maps += self.dico_pdf.get('layers_count') + 1
        else:
            self.logger.info('\tIgnoring {0} Geospatial PDF'.format(len(self.li_pdf)))
            pass

        # writing global metrics about the dictionary
        self.dictionarize_metrics()

        # saving dictionary
        self.val.config(state=ACTIVE)
        self.savedico()
        self.logger.info('\n\tWorkbook saved: %s', self.output.get())
        self.bell()

        # quit and exit
        self.open_dir_file(self.output.get())
        self.destroy()
        exit()

        # End path.abspath(of) function
        return

    def process_db(self, conn):
        u""" launch the different processes """
        # creating the Excel workbook
        self.configexcel()
        self.logger.info('Excel file created')
        # getting the info from shapefiles and compile it in the excel
        line = 1    # line of dictionary
        self.logger.info('\tPostGIS table processing...')
        # setting progress bar
        self.prog_layers["maximum"] = conn.GetLayerCount()
        # parsing the layers
        for layer in conn:
            # reset recipient data
            self.dico_layer.clear()
            self.dico_fields.clear()
            Read_PostGIS(layer,
                         self.dico_layer,
                         self.dico_fields,
                         'PostGIS table',
                         self.blabla)
            self.logger.info('Table examined: %s' % layer.GetName())
            # writing to the Excel dictionary
            self.dictionarize_pg(self.dico_layer,
                                 self.dico_fields,
                                 self.feuyPG,
                                 line)
            self.logger.info('\t Wrote into the dictionary')
            # increment the line number
            line = line + 1
            # increment the progress bar
            self.prog_layers["value"] = self.prog_layers["value"] + 1
            self.update()
        # saving dictionary
        self.savedico()
        self.logger.info('\n\tWorkbook saved: %s', self.output.get())

        # quit and exit
        self.open_dir_file(self.output.get())
        self.destroy()
        exit()

        # End of function
        return

    def check_fields(self):
        u""" Check if required fields are not empty """
        # error counter
        # checking empty fields
        if self.host.get() == u''\
           or self.host.get() == self.blabla.get("err_pg_empty_field"):
            self.ent_H.configure(foreground="red")
            self.ent_H.delete(0, END)
            self.ent_H.insert(0, self.blabla.get("err_pg_empty_field"))
            return
        else:
            pass
        if not self.ent_P.get():
            self.ent_P.configure(foreground='red')
            self.ent_P.delete(0, END)
            self.ent_P.insert(0, 0000)
            return
        else:
            pass
        if self.dbnb.get() == u''\
           or self.host.get() == self.blabla.get("err_pg_empty_field"):
            self.ent_D.configure(foreground='red')
            self.ent_D.delete(0, END)
            self.ent_D.insert(0, self.blabla.get("err_pg_empty_field"))
            return
        else:
            pass
        if self.user.get() == u''\
           or self.host.get() == self.blabla.get("err_pg_empty_field"):
            self.ent_U.configure(foreground='red')
            self.ent_U.delete(0, END)
            self.ent_U.insert(0, self.blabla.get("err_pg_empty_field"))
            return
        else:
            pass
        if self.pswd.get() == u''\
           or self.pswd.get() == self.blabla.get("err_pg_empty_field"):
            self.ent_M.configure(foreground="red")
            self.ent_M.delete(0, END)
            self.ent_M.insert(0, self.blabla.get("err_pg_empty_field"))
            return
        else:
            pass
        # no error detected: let's test connection
        self.logger.info("Required fields are OK.")
        self.test_connection()
        # End of function
        return

    def test_connection(self):
        u"""
        Testing database connection and handling specific
        settings : proxy, DB views, etc.
        """
        # check if a proxy is needed
        # more information about the GDAL HTTP proxy options here:
        # http://trac.osgeo.org/gdal/wiki/ConfigOptions#GDALOGRHTTPoptions
        if self.opt_proxy.get():
            self.logger.info("Proxy configured.")
            gdal.SetConfigOption('GDAL_HTTP_PROXY', '{0}:{1}'.format(self.prox_server.get(),
                                                                     self.prox_port.get()))
            if self.opt_ntlm.get():
                # if authentication needs ...\
                # username/password or not (NTLM)
                gdal.SetConfigOption('GDAL_PROXY_AUTH', 'NTLM')
                gdal.SetConfigOption('GDAL_HTTP_PROXYUSERPWD', ' : ')
            else:
                pass
        else:
            self.logger.info("No proxy configured.")

        # checking if user chose to list PostGIS views
        if self.opt_pgvw.get():
            gdal.SetConfigOption(str("PG_LIST_ALL_TABLES"), str("YES"))
            self.logger.info("PostgreSQL views enabled.")
        else:
            gdal.SetConfigOption(str("PG_LIST_ALL_TABLES"), str("NO"))
            self.logger.info("PostgreSQL views disabled.")

        # testing connection settings
        try:
            conn = ogr.Open("PG: host={0} port={1} dbname={2} user={3} password={4}".format(
                            self.host.get(), self.port.get(), self.dbnb.get(), self.user.get(),
                            self.pswd.get()))
            conn.GetLayerCount()
            # sql_version = "SELECT PostGIS_full_version();"
            # version = conn.ExecuteSQL(sql_version)
        except Exception, e:
            self.logger.warning("Connection failed: {0}.".format(e))
            self.status.set("Connection failed: {0}.".format(e))
            avert(title=self.blabla.get("err_pg_conn_fail"), message=unicode(e))
            return

        # if connection successed
        self.status.set("{} tables".format(conn.GetLayerCount()))
        self.logger.info('Connection to database {0} successed.\
                          {1} tables found.'.format(self.dbnb.get(),
                                                    conn.GetLayerCount()))
        # set the default output file
        self.output.delete(0, END)
        self.output.insert(0, "DicoGIS_{0}-{1}_{2}.xls".format(self.dbnb.get(),
                                                               self.host.get(),
                                                               self.today))
        # launching the process
        self.process_db(conn)
        # end of function
        return conn

    def configexcel(self):
        u""" create and configure the Excel workbook """
        # Basic configuration
        self.book = Workbook(encoding='utf8')
        self.book.set_owner(str('DicoGIS_') + str(DGversion))
        self.logger.info('Workbook created')
        # Some customization: fonts and styles
        # headers style
        self.entete = easyxf('pattern: pattern solid, fore_colour black;'
                             'font: colour white, bold True, height 220;'
                             'align: horiz center')
        # hyperlinks style
        self.url = easyxf(u'font: underline single')
        # errors style
        self.xls_erreur = easyxf('pattern: pattern solid, fore_colour red;'
                                 'font: colour white, bold True;')
        # cell style handling return in-cell
        self.xls_wrap = easyxf('align: wrap True')
        # date cell style
        self.xls_date = easyxf(num_format_str='DD/MM/YYYY')

        # columns headers
        if self.typo.get() == 1:
            """ adding a new sheet for metrics """
            # sheet
            self.feuySTATS = self.book.add_sheet('Metrics',
                                                 cell_overwrite_ok=True)
            # headers
            self.feuySTATS.write(0, 0, "Totals", self.entete)
            self.feuySTATS.write(0, 1, "=== Global Statistics ===", self.entete)
            self.feuySTATS.write(1, 0, self.blabla.get('feats_class'), self.entete)
            self.feuySTATS.write(2, 0, self.blabla.get('num_attrib'), self.entete)
            self.feuySTATS.write(3, 0, self.blabla.get('num_objets'), self.entete)
            self.feuySTATS.write(4, 0, self.blabla.get('gdal_warn'), self.entete)
            self.feuySTATS.write(6, 0, self.blabla.get('geometrie'), self.entete)
            self.logger.info('Sheet for global statistics adedd')
            # tunning headers
            # lg_shp_names = [len(lg) for lg in self.li_shp]
            # lg_tab_names = [len(lg) for lg in self.li_tab]
            # self.feuySTATS.col(0).width = max(lg_shp_names + lg_tab_names) * 100
            # self.feuySTATS.col(1).width = len(self.blabla.get('browse')) * 256
            # self.feuySTATS.col(9).width = 35 * 256
        else:
            pass

        if self.typo.get() == 1 \
            and (self.opt_shp.get() + self.opt_tab.get() + self.opt_kml.get()
                 + self.opt_gml.get() + self.opt_geoj.get()) > 0\
            and len(self.li_vectors) > 0:
            """ adding a new sheet for vectors informations """
            # sheet
            self.feuyVC = self.book.add_sheet(self.blabla.get('sheet_vectors'),
                                              cell_overwrite_ok=True)
            # headers
            self.feuyVC.write(0, 0, self.blabla.get('nomfic'), self.entete)
            self.feuyVC.write(0, 1, self.blabla.get('path'), self.entete)
            self.feuyVC.write(0, 2, self.blabla.get('theme'), self.entete)
            self.feuyVC.write(0, 3, self.blabla.get('num_attrib'), self.entete)
            self.feuyVC.write(0, 4, self.blabla.get('num_objets'), self.entete)
            self.feuyVC.write(0, 5, self.blabla.get('geometrie'), self.entete)
            self.feuyVC.write(0, 6, self.blabla.get('srs'), self.entete)
            self.feuyVC.write(0, 7, self.blabla.get('srs_type'), self.entete)
            self.feuyVC.write(0, 8, self.blabla.get('codepsg'), self.entete)
            self.feuyVC.write(0, 9, self.blabla.get('emprise'), self.entete)
            self.feuyVC.write(0, 10, self.blabla.get('date_crea'), self.entete)
            self.feuyVC.write(0, 11, self.blabla.get('date_actu'), self.entete)
            self.feuyVC.write(0, 12, self.blabla.get('format'), self.entete)
            self.feuyVC.write(0, 13, self.blabla.get('li_depends'), self.entete)
            self.feuyVC.write(0, 14, self.blabla.get('tot_size'), self.entete)
            self.feuyVC.write(0, 15, self.blabla.get('li_chps'), self.entete)
            self.feuyVC.write(0, 16, self.blabla.get('gdal_warn'), self.entete)
            self.logger.info('Sheet vectors adedd')
            # tunning headers
            lg_shp_names = [len(lg) for lg in self.li_shp]
            lg_tab_names = [len(lg) for lg in self.li_tab]
            self.feuyVC.col(0).width = max(lg_shp_names + lg_tab_names) * 100
            self.feuyVC.col(1).width = len(self.blabla.get('browse')) * 256
            self.feuyVC.col(9).width = 35 * 256
            # freezing headers line and first column
            self.feuyVC.set_panes_frozen(True)
            self.feuyVC.set_horz_split_pos(1)
            self.feuyVC.set_vert_split_pos(1)
        else:
            pass

        if self.typo.get() == 1\
           and self.opt_rast.get() == 1\
           and len(self.li_raster) > 0:
            """ adding a new sheet for rasters informations """
            # sheet
            self.feuyRS = self.book.add_sheet(self.blabla.get('sheet_rasters'),
                                              cell_overwrite_ok=True)
            # headers
            self.feuyRS.write(0, 0, self.blabla.get('nomfic'), self.entete)
            self.feuyRS.write(0, 1, self.blabla.get('path'), self.entete)
            self.feuyRS.write(0, 2, self.blabla.get('theme'), self.entete)
            self.feuyRS.write(0, 3, self.blabla.get('size_Y'), self.entete)
            self.feuyRS.write(0, 4, self.blabla.get('size_X'), self.entete)
            self.feuyRS.write(0, 5, self.blabla.get('pixel_w'), self.entete)
            self.feuyRS.write(0, 6, self.blabla.get('pixel_h'), self.entete)
            self.feuyRS.write(0, 7, self.blabla.get('origin_x'), self.entete)
            self.feuyRS.write(0, 8, self.blabla.get('origin_y'), self.entete)
            self.feuyRS.write(0, 9, self.blabla.get('srs_type'), self.entete)
            self.feuyRS.write(0, 10, self.blabla.get('codepsg'), self.entete)
            self.feuyRS.write(0, 11, self.blabla.get('emprise'), self.entete)
            self.feuyRS.write(0, 12, self.blabla.get('date_crea'), self.entete)
            self.feuyRS.write(0, 13, self.blabla.get('date_actu'), self.entete)
            self.feuyRS.write(0, 14, self.blabla.get('num_bands'), self.entete)
            self.feuyRS.write(0, 15, self.blabla.get('format'), self.entete)
            self.feuyRS.write(0, 16, self.blabla.get('compression'), self.entete)
            self.feuyRS.write(0, 17, self.blabla.get('coloref'), self.entete)
            self.feuyRS.write(0, 18, self.blabla.get('li_depends'), self.entete)
            self.feuyRS.write(0, 19, self.blabla.get('tot_size'), self.entete)
            self.feuyRS.write(0, 20, self.blabla.get('gdal_warn'), self.entete)
            self.logger.info('Sheet rasters created')
            # tunning headers
            lg_rast_names = [len(lg) for lg in self.li_raster]
            self.feuyRS.col(0).width = max(lg_rast_names) * 100
            self.feuyRS.col(1).width = len(self.blabla.get('browse')) * 256
            # freezing headers line and first column
            self.feuyRS.set_panes_frozen(True)
            self.feuyRS.set_horz_split_pos(1)
            self.feuyRS.set_vert_split_pos(1)
        else:
            pass

        if self.typo.get() == 1\
           and (self.opt_spadb.get() + self.opt_egdb.get())\
           and len(self.li_fdb) > 0:
            """ adding a new sheet for flat geodatabases informations """
            # sheet
            self.feuyFGDB = self.book.add_sheet(self.blabla.get('sheet_filedb'),
                                                cell_overwrite_ok=True)
            # headers
            self.feuyFGDB.write(0, 0, self.blabla.get('nomfic'), self.entete)
            self.feuyFGDB.write(0, 1, self.blabla.get('path'), self.entete)
            self.feuyFGDB.write(0, 2, self.blabla.get('theme'), self.entete)
            self.feuyFGDB.write(0, 3, self.blabla.get('tot_size'), self.entete)
            self.feuyFGDB.write(0, 4, self.blabla.get('date_crea'), self.entete)
            self.feuyFGDB.write(0, 5, self.blabla.get('date_actu'), self.entete)
            self.feuyFGDB.write(0, 6, self.blabla.get('feats_class'), self.entete)
            self.feuyFGDB.write(0, 7, self.blabla.get('num_attrib'), self.entete)
            self.feuyFGDB.write(0, 8, self.blabla.get('num_objets'), self.entete)
            self.feuyFGDB.write(0, 9, self.blabla.get('geometrie'), self.entete)
            self.feuyFGDB.write(0, 10, self.blabla.get('srs'), self.entete)
            self.feuyFGDB.write(0, 11, self.blabla.get('srs_type'), self.entete)
            self.feuyFGDB.write(0, 12, self.blabla.get('codepsg'), self.entete)
            self.feuyFGDB.write(0, 13, self.blabla.get('emprise'), self.entete)
            self.feuyFGDB.write(0, 14, self.blabla.get('li_chps'), self.entete)
            self.logger.info('Sheet Esri FileGDB created')
            # tunning headers
            lg_gdb_names = [len(lg) for lg in self.li_egdb]
            self.feuyFGDB.col(0).width = max(lg_gdb_names) * 100
            self.feuyFGDB.col(1).width = len(self.blabla.get('browse')) * 256
            self.feuyFGDB.col(4).width = len(self.blabla.get('date_crea')) * 256
            self.feuyFGDB.col(5).width = len(self.blabla.get('date_actu')) * 256
            self.feuyFGDB.col(6).width = len(self.blabla.get('feats_class')) * 256
            self.feuyFGDB.col(13).width = 35 * 256
            # freezing headers line and first column
            self.feuyFGDB.set_panes_frozen(True)
            self.feuyFGDB.set_horz_split_pos(1)
            self.feuyFGDB.set_vert_split_pos(1)
        else:
            pass

        if self.typo.get() == 1\
           and self.opt_pdf.get()\
           and len(self.li_pdf) > 0:
            """ adding a new sheet for maps documents informations """
            # sheet
            self.feuyMAPS = self.book.add_sheet(self.blabla.get('sheet_maplans'),
                                                cell_overwrite_ok=True)
            # headers
            self.feuyMAPS.write(0, 0, self.blabla.get('nomfic'), self.entete)
            self.feuyMAPS.write(0, 1, self.blabla.get('path'), self.entete)
            self.feuyMAPS.write(0, 2, self.blabla.get('theme'), self.entete)
            self.feuyMAPS.write(0, 3, self.blabla.get('custom_title'), self.entete)
            self.feuyMAPS.write(0, 4, self.blabla.get('creator_prod'), self.entete)
            self.feuyMAPS.write(0, 5, self.blabla.get('keywords'), self.entete)
            self.feuyMAPS.write(0, 6, self.blabla.get('subject'), self.entete)
            self.feuyMAPS.write(0, 7, self.blabla.get('res_image'), self.entete)
            self.feuyMAPS.write(0, 8, self.blabla.get('tot_size'), self.entete)
            self.feuyMAPS.write(0, 9, self.blabla.get('date_crea'), self.entete)
            self.feuyMAPS.write(0, 10, self.blabla.get('date_actu'), self.entete)
            self.feuyMAPS.write(0, 11, self.blabla.get('origin_x'), self.entete)
            self.feuyMAPS.write(0, 12, self.blabla.get('origin_y'), self.entete)
            self.feuyMAPS.write(0, 13, self.blabla.get('srs'), self.entete)
            self.feuyMAPS.write(0, 14, self.blabla.get('srs_type'), self.entete)
            self.feuyMAPS.write(0, 15, self.blabla.get('codepsg'), self.entete)
            self.feuyMAPS.write(0, 16, self.blabla.get('sub_layers'), self.entete)
            self.feuyMAPS.write(0, 17, self.blabla.get('num_attrib'), self.entete)
            self.feuyMAPS.write(0, 18, self.blabla.get('num_objets'), self.entete)
            self.feuyMAPS.write(0, 19, self.blabla.get('li_chps'), self.entete)
            self.logger.info('Sheet Maps & Documents created')
            # tunning headers
            lg_maps_names = [len(lg) for lg in self.li_pdf]
            self.feuyMAPS.col(0).width = max(lg_maps_names) * 100
            self.feuyMAPS.col(1).width = len(self.blabla.get('browse')) * 256
            self.feuyMAPS.col(4).width = len(self.blabla.get('date_crea')) * 256
            self.feuyMAPS.col(5).width = len(self.blabla.get('date_actu')) * 256
            self.feuyMAPS.col(6).width = len(self.blabla.get('sub_layers')) * 275
            self.feuyMAPS.col(13).width = 35 * 256
            # freezing headers line and first column
            self.feuyMAPS.set_panes_frozen(True)
            self.feuyMAPS.set_horz_split_pos(1)
            self.feuyMAPS.set_vert_split_pos(1)
        else:
            pass

        if self.typo.get() == 1\
           and self.opt_cdao.get() == 1\
           and len(self.li_cdao) > 0:
            """ adding a new sheet for CAO informations """
            # sheet
            self.feuyCDAO = self.book.add_sheet(self.blabla.get('sheet_cdao'), cell_overwrite_ok=True)
            # headers
            self.feuyCDAO.write(0, 0, self.blabla.get('nomfic'), self.entete)
            self.feuyCDAO.write(0, 1, self.blabla.get('path'), self.entete)
            self.feuyCDAO.write(0, 2, self.blabla.get('theme'), self.entete)
            self.feuyCDAO.write(0, 3, self.blabla.get('tot_size'), self.entete)
            self.feuyCDAO.write(0, 4, self.blabla.get('date_crea'), self.entete)
            self.feuyCDAO.write(0, 5, self.blabla.get('date_actu'), self.entete)
            self.feuyCDAO.write(0, 6, self.blabla.get('sub_layers'), self.entete)
            self.feuyCDAO.write(0, 7, self.blabla.get('num_attrib'), self.entete)
            self.feuyCDAO.write(0, 8, self.blabla.get('num_objets'), self.entete)
            self.feuyCDAO.write(0, 9, self.blabla.get('geometrie'), self.entete)
            self.feuyCDAO.write(0, 10, self.blabla.get('srs'), self.entete)
            self.feuyCDAO.write(0, 11, self.blabla.get('srs_type'), self.entete)
            self.feuyCDAO.write(0, 12, self.blabla.get('codepsg'), self.entete)
            self.feuyCDAO.write(0, 13, self.blabla.get('emprise'), self.entete)
            self.feuyCDAO.write(0, 14, self.blabla.get('li_chps'), self.entete)
            self.logger.info('Sheet CAO - DAO created')
            # tunning headers
            lg_gdb_names = [len(lg) for lg in self.li_cdao]
            self.feuyCDAO.col(0).width = max(lg_gdb_names) * 100
            self.feuyCDAO.col(1).width = len(self.blabla.get('browse')) * 256
            self.feuyCDAO.col(4).width = len(self.blabla.get('date_crea')) * 256
            self.feuyCDAO.col(5).width = len(self.blabla.get('date_actu')) * 256
            self.feuyCDAO.col(6).width = len(self.blabla.get('feats_class')) * 256
            self.feuyCDAO.col(13).width = 35 * 256
            # freezing headers line and first column
            self.feuyCDAO.set_panes_frozen(True)
            self.feuyCDAO.set_horz_split_pos(1)
            self.feuyCDAO.set_vert_split_pos(1)
        else:
            pass

        if self.typo.get() == 2:
            """ adding a new sheet for PostGIS informations """
            # sheet
            self.feuyPG = self.book.add_sheet(u'PostGIS',
                                             cell_overwrite_ok=True)
            # headers
            self.feuyPG.write(0, 0, self.blabla.get('nomfic'), self.entete)
            self.feuyPG.write(0, 1, self.blabla.get('conn_chain'), self.entete)
            self.feuyPG.write(0, 2, self.blabla.get('schema'), self.entete)
            self.feuyPG.write(0, 3, self.blabla.get('num_attrib'), self.entete)
            self.feuyPG.write(0, 4, self.blabla.get('num_objets'), self.entete)
            self.feuyPG.write(0, 5, self.blabla.get('geometrie'), self.entete)
            self.feuyPG.write(0, 6, self.blabla.get('srs'), self.entete)
            self.feuyPG.write(0, 7, self.blabla.get('srs_type'), self.entete)
            self.feuyPG.write(0, 8, self.blabla.get('codepsg'), self.entete)
            self.feuyPG.write(0, 9, self.blabla.get('emprise'), self.entete)
            self.feuyPG.write(0, 10, self.blabla.get('date_crea'), self.entete)
            self.feuyPG.write(0, 11, self.blabla.get('date_actu'), self.entete)
            self.feuyPG.write(0, 12, self.blabla.get('format'), self.entete)
            self.feuyPG.write(0, 13, self.blabla.get('li_chps'), self.entete)
            self.logger.info('Sheet PostGIS created')
            # tunning headers
            self.feuyPG.col(1).width = len(self.blabla.get('browse')) * 256
            # freezing headers line and first column
            self.feuyPG.set_panes_frozen(True)
            self.feuyPG.set_horz_split_pos(1)
            self.feuyPG.set_vert_split_pos(1)
        else:
            pass

        # end of function
        return self.book, self.entete, self.url, self.xls_erreur

    def dictionarize_vectors(self, layer_infos, fields_info, sheet, line):
        u""" write the infos of the layer into the Excel workbook """
        # local variables
        champs = ""
        # in case of a source error
        if layer_infos.get('error'):
            sheet.row(line).set_style(self.xls_erreur)
            err_mess = self.blabla.get(layer_infos.get('error'))
            self.logger.warning('\tproblem detected')
            sheet.write(line, 0, layer_infos.get('name'), self.xls_erreur)
            sheet.write(line, 2, err_mess, self.xls_erreur)
            link = 'HYPERLINK("{0}"; "{1}")'.format(layer_infos.get(u'folder'),
                                                    self.blabla.get('browse'))
            sheet.write(line, 1, Formula(link), self.url)

            # Interruption of function
            return self.book, self.feuyVC
        else:
            pass

        # Name
        sheet.write(line, 0, layer_infos.get('name'))

        # Path of parent folder formatted to be a hyperlink
        try:
            link = 'HYPERLINK("{0}"; "{1}")'.format(layer_infos.get(u'folder'),
                                                    self.blabla.get('browse'))
        except UnicodeDecodeError:
            # write a notification into the log file
            self.logger.warning('Path name with special letters: {}'.format(layer_infos.get(u'folder').decode('utf8')))
            # decode the fucking path name
            link = 'HYPERLINK("{0}"; "{1}")'.format(layer_infos.get(u'folder').decode('utf8'),
                                                    self.blabla.get('browse'))
        sheet.write(line, 1, Formula(link), self.url)

        # Name of parent folder
        # with an exception if this is the format name
        if not path.basename(layer_infos.get(u'folder')).lower() in self.li_vectors_formats:
            sheet.write(line, 2, path.basename(layer_infos.get(u'folder')))
        else:
            sheet.write(line, 2, path.basename(path.dirname(layer_infos.get(u'folder'))))

        # Geometry type
        sheet.write(line, 5, layer_infos.get(u'type_geom'))
        # Spatial extent
        emprise = u"Xmin : {0} - Xmax : {1} \
                   \nYmin : {2} - Ymax : {3}".format(unicode(layer_infos.get(u'Xmin')),
                                                     unicode(layer_infos.get(u'Xmax')),
                                                     unicode(layer_infos.get(u'Ymin')),
                                                     unicode(layer_infos.get(u'Ymax'))
                                                     )
        sheet.write(line, 9, emprise, self.xls_wrap)
        # Name of srs
        sheet.write(line, 6, layer_infos.get(u'srs'))
        # Type of SRS
        sheet.write(line, 7, layer_infos.get(u'srs_type'))
        # EPSG code
        sheet.write(line, 8, layer_infos.get(u'EPSG'))
        # Number of fields
        sheet.write(line, 3, layer_infos.get(u'num_fields'))
        # Name of objects
        sheet.write(line, 4, layer_infos.get(u'num_obj'))
        # Creation date
        sheet.write(line, 10, layer_infos.get(u'date_crea'))
        # Last update date
        sheet.write(line, 11, layer_infos.get(u'date_actu'))
        # Format of data
        sheet.write(line, 12, layer_infos.get(u'type'))
        # dependencies
        self.feuyVC.write(line, 13, ' | '.join(layer_infos.get(u'dependencies')))
        # total size
        self.feuyVC.write(line, 14, layer_infos.get(u'total_size'))
        # Field informations
        for chp in fields_info.keys():
            # field type
            if fields_info[chp][0] == 'Integer':
                tipo = self.blabla.get(u'entier')
            elif fields_info[chp][0] == 'Real':
                tipo = self.blabla.get(u'reel')
            elif fields_info[chp][0] == 'String':
                tipo = self.blabla.get(u'string')
            elif fields_info[chp][0] == 'Date':
                tipo = self.blabla.get(u'date')
            # concatenation of field informations
            try:
                champs = champs + chp +\
                          u" (" + tipo + self.blabla.get(u'longueur') +\
                          unicode(fields_info[chp][1]) +\
                          self.blabla.get(u'precision') +\
                          unicode(fields_info[chp][2]) + u") ; "
            except UnicodeDecodeError:
                # write a notification into the log file
                self.dico_err[layer_infos.get('name')] = self.blabla.get(u'err_encod')\
                                                    + chp.decode('latin1') \
                                                    + u"\n\n"
                self.logger.warning('Field name with special letters: {}'.format(chp.decode('latin1')))
                # decode the fucking field name
                champs = champs + chp.decode('latin1') \
                + u" ({}, Lg. = {}, Pr. = {}) ;".format(tipo,
                                                        fields_info[chp][1],
                                                        fields_info[chp][2])
                # then continue
                continue

        # Once all fieds explored, write them
        sheet.write(line, 15, champs)

        # in case of a source error
        if layer_infos.get('err_gdal')[0] != 0:
            self.logger.warning('\tproblem detected')
            sheet.write(line, 16, "{0} : {1}".format(layer_infos.get('err_gdal')[0],
                                                     layer_infos.get('err_gdal')[1]), self.xls_erreur)
        else:
            pass

        # End of function
        return self.book, self.feuyVC

    def dictionarize_rasters(self, dico_raster, dico_bands, sheet, line):
        u""" write the infos of the layer into the Excel workbook """
        # in case of a source error
        if dico_raster.get('error'):
            self.logger.warning('\tproblem detected')
            sheet.write(line, 0, dico_raster.get('name'))
            link = 'HYPERLINK("{0}"; "{1}")'.format(dico_raster.get(u'folder'),
                                                    self.blabla.get('browse'))
            sheet.write(line, 1, Formula(link), self.url)
            sheet.write(line, 2, self.blabla.get(dico_raster.get('error')),
                                 self.xls_erreur)
            # Interruption of function
            return self.book, self.feuyRS
        else:
            pass

        # Name
        sheet.write(line, 0, dico_raster.get('name'))

        # Path of parent folder formatted to be a hyperlink
        try:
            link = 'HYPERLINK("{0}"; "{1}")'.format(dico_raster.get(u'folder'),
                                                    self.blabla.get('browse'))
        except UnicodeDecodeError:
            # write a notification into the log file
            self.logger.warning('Path name with special letters: {}'.format(dico_raster.get(u'folder').decode('utf8')))
            # decode the fucking path name
            link = 'HYPERLINK("{0}"; "{1}")'.format(dico_raster.get(u'folder').decode('utf8'),
                                                    self.blabla.get('browse'))
        sheet.write(line, 1, Formula(link), self.url)

        # Name of parent folder
        sheet.write(line, 2, path.basename(dico_raster.get(u'folder')))
        # Name of parent folder
        # with an exception if this is the format name
        if path.basename(dico_raster.get(u'folder')) in self.li_raster_formats:
            sheet.write(line, 2, path.basename(dico_raster.get(u'folder')))
        else:
            sheet.write(line, 2, path.basename(path.dirname(dico_raster.get(u'folder'))))

        # Image dimensions
        sheet.write(line, 3, dico_raster.get(u'num_rows'))
        sheet.write(line, 4, dico_raster.get(u'num_cols'))

        # Pixel dimensions
        sheet.write(line, 5, dico_raster.get(u'pixelWidth'))
        sheet.write(line, 6, dico_raster.get(u'pixelHeight'))

        # Image dimensions
        sheet.write(line, 7, dico_raster.get(u'xOrigin'))
        sheet.write(line, 8, dico_raster.get(u'yOrigin'))

        # Type of SRS
        sheet.write(line, 9, dico_raster.get(u'srs_type'))
        # EPSG code
        sheet.write(line, 10, dico_raster.get(u'EPSG'))

        # # Spatial extent
        # emprise = u"Xmin : " + unicode(layer_infos.get(u'Xmin')) +\
        #           u", Xmax : " + unicode(layer_infos.get(u'Xmax')) +\
        #           u", Ymin : " + unicode(layer_infos.get(u'Ymin')) +\
        #           u", Ymax : " + unicode(layer_infos.get(u'Ymax'))
        # sheet.write(line, 9, emprise)
        # # Name of srs
        # sheet.write(line, 6, layer_infos.get(u'srs'))

        # Number of bands
        sheet.write(line, 14, dico_raster.get(u'num_bands'))
        # # Name of objects
        # sheet.write(line, 4, layer_infos.get(u'num_obj'))
        # Creation date
        sheet.write(line, 12, dico_raster.get(u'date_crea'), self.xls_date)
        # Last update date
        sheet.write(line, 13, dico_raster.get(u'date_actu'), self.xls_date)
        # Format of data
        sheet.write(line, 15, "{0} {1}".format(dico_raster.get(u'format'),
                                               dico_raster.get('format_version')))
        # Compression rate
        sheet.write(line, 16, dico_raster.get(u'compr_rate'))

        # Color referential
        sheet.write(line, 17, dico_raster.get(u'color_ref'))

        # Dependencies
        sheet.write(line, 18, ' | '.join(dico_raster.get(u'dependencies')))

        # total size of file and its dependencies
        sheet.write(line, 19, dico_raster.get(u'total_size'))

        # in case of a source error
        if dico_raster.get('err_gdal')[0] != 0:
            self.logger.warning('\tproblem detected')
            sheet.write(line, 20, "{0} : {1}".format(dico_raster.get('err_gdal')[0],
                                                     dico_raster.get('err_gdal')[1]), self.xls_erreur)
        else:
            pass

        # End of function
        return line, sheet

    def dictionarize_fdb(self, gdb_infos, sheet, line):
        u""" write the infos of the FileGDB into the Excel workbook """
        # in case of a source error
        if gdb_infos.get('error'):
            self.logger.warning('\tproblem detected')
            sheet.write(line, 0, gdb_infos.get('name'))
            link = 'HYPERLINK("{0}"; "{1}")'.format(gdb_infos.get(u'folder'),
                                                    self.blabla.get('browse'))
            sheet.write(line, 1, Formula(link), self.url)
            sheet.write(line, 2, self.blabla.get(gdb_infos.get('error')),
                                 self.xls_erreur)
            # incrementing line
            # gdb_infos['layers_count'] = 0
            # Interruption of function
            return self.feuyFGDB, line
        else:
            pass

        # GDB name
        sheet.write(line, 0, gdb_infos.get('name'))

        # Path of parent folder formatted to be a hyperlink
        try:
            link = 'HYPERLINK("{0}"; "{1}")'.format(gdb_infos.get(u'folder'),
                                                    self.blabla.get('browse'))
        except UnicodeDecodeError:
            # write a notification into the log file
            self.logger.warning('Path name with special letters: {}'.format(gdb_infos.get(u'folder').decode('utf8')))
            # decode the fucking path name
            link = 'HYPERLINK("{0}"; "{1}")'.format(gdb_infos.get(u'folder').decode('utf8'),
                                                    self.blabla.get('browse'))

        sheet.write(line, 1, Formula(link), self.url)

        # Name of parent folder
        sheet.write(line, 2, path.basename(gdb_infos.get(u'folder')))

        # total size
        sheet.write(line, 3, gdb_infos.get(u'total_size'))

        # Creation date
        sheet.write(line, 4, gdb_infos.get(u'date_crea'), self.xls_date)
        # Last update date
        sheet.write(line, 5, gdb_infos.get(u'date_actu'), self.xls_date)

        # Layers count
        sheet.write(line, 6, gdb_infos.get(u'layers_count'))

        # total number of fields
        sheet.write(line, 7, gdb_infos.get(u'total_fields'))

        # total number of objects
        sheet.write(line, 8, gdb_infos.get(u'total_objs'))

        # in case of a source error
        if gdb_infos.get('err_gdal')[0] != 0:
            self.logger.warning('\tproblem detected')
            sheet.write(line, 15, "{0} : {1}".format(gdb_infos.get('err_gdal')[0],
                                                     gdb_infos.get('err_gdal')[1]), self.xls_erreur)
        else:
            pass

        # parsing layers
        for (layer_idx, layer_name) in zip(gdb_infos.get(u'layers_idx'),
                                           gdb_infos.get(u'layers_names')):
            # increment line
            line += 1
            champs = ""
            # get the layer informations
            try:
                gdb_layer = gdb_infos.get('{0}_{1}'.format(layer_idx,
                                                           layer_name))
            except UnicodeDecodeError:
                gdb_layer = gdb_infos.get('{0}_{1}'.format(layer_idx,
                                                           unicode(layer_name.decode('latin1'))))
            # in case of a source error
            if gdb_layer.get('error'):
                err_mess = self.blabla.get(gdb_layer.get('error'))
                self.logger.warning('\tproblem detected: \
                                    {0} in {1}'.format(err_mess,
                                                       gdb_layer.get(u'title')))
                sheet.write(line, 6, gdb_layer.get(u'title'), self.xls_erreur)
                sheet.write(line, 7, err_mess, self.xls_erreur)
                # Interruption of function
                continue
            else:
                pass

            # layer's name
            sheet.write(line, 6, gdb_layer.get(u'title'))

            # number of fields
            sheet.write(line, 7, gdb_layer.get(u'num_fields'))

            # number of objects
            sheet.write(line, 8, gdb_layer.get(u'num_obj'))

            # Geometry type
            sheet.write(line, 9, gdb_layer.get(u'type_geom'))

            # SRS label
            sheet.write(line, 10, gdb_layer.get(u'srs'))
            # SRS type
            sheet.write(line, 11, gdb_layer.get(u'srs_type'))
            # SRS reference EPSG code
            sheet.write(line, 12, gdb_layer.get(u'EPSG'))

            # Spatial extent
            emprise = u"Xmin : {0} - Xmax : {1} \
                       \nYmin : {2} - Ymax : {3}".format(unicode(gdb_layer.get(u'Xmin')),
                                                         unicode(gdb_layer.get(u'Xmax')),
                                                         unicode(gdb_layer.get(u'Ymin')),
                                                         unicode(gdb_layer.get(u'Ymax'))
                                                         )
            sheet.write(line, 13, emprise, self.xls_wrap)

            # Field informations
            fields_info = gdb_layer.get(u'fields')
            for chp in fields_info.keys():
                # field type
                if fields_info[chp][0] == 'Integer':
                    tipo = self.blabla.get(u'entier')
                elif fields_info[chp][0] == 'Real':
                    tipo = self.blabla.get(u'reel')
                elif fields_info[chp][0] == 'String':
                    tipo = self.blabla.get(u'string')
                elif fields_info[chp][0] == 'Date':
                    tipo = self.blabla.get(u'date')
                # concatenation of field informations
                try:
                    champs = champs + chp + u" ({0}) ; ".format(tipo)
                except UnicodeDecodeError:
                    # write a notification into the log file
                    self.dico_err[gdb_layer.get('name')] = self.blabla.get(u'err_encod') + \
                                                              chp.decode('latin1') + \
                                                              u"\n\n"
                    self.logger.warning('Field name with special letters: {}'.format(chp.decode('latin1')))
                    # decode the fucking field name
                    champs = champs + chp.decode('latin1') \
                                    + u" ({0}) ;".format(tipo)
                    # then continue
                    continue

            # Once all fieds explored, write them
            sheet.write(line, 14, champs)

            # write layer's name into the log
            self.logger.info('\t -- {0} = OK'.format(gdb_layer.get(u'title')))

        # End of function
        return self.feuyFGDB, line

    def dictionarize_cdao(self, dico_cdao, sheet, line):
        u""" write the infos of the CAO/DAO files into the Excel workbook """
        # local variables
        champs = ""

        # in case of a source error
        if dico_cdao.get('error'):
            self.logger.warning('\tproblem detected')
            sheet.write(line, 0, dico_cdao.get('name'))
            link = 'HYPERLINK("{0}"; "{1}")'.format(dico_cdao.get(u'folder'),
                                                    self.blabla.get('browse'))
            sheet.write(line, 1, Formula(link), self.url)
            sheet.write(line, 2, self.blabla.get(dico_cdao.get('error')),
                                 self.xls_erreur)
            # incrementing line
            dico_cdao['layers_count'] = 0
            # Interruption of function
            return self.feuyCDAO, line
        else:
            pass

        # Filename
        sheet.write(line, 0, dico_cdao.get('name'))

        # Path of parent folder formatted to be a hyperlink
        try:
            link = 'HYPERLINK("{0}"; "{1}")'.format(dico_cdao.get(u'folder'),
                                                    self.blabla.get('browse'))
        except UnicodeDecodeError:
            # write a notification into the log file
            self.logger.warning('Path name with special letters: {}'.format(dico_cdao.get(u'folder').decode('utf8')))
            # decode the fucking path name
            link = 'HYPERLINK("{0}"; "{1}")'.format(dico_cdao.get(u'folder').decode('utf8'),
                                                    self.blabla.get('browse'))

        sheet.write(line, 1, Formula(link), self.url)

        # Name of parent folder
        sheet.write(line, 2, path.basename(dico_cdao.get(u'folder')))

        # total size
        sheet.write(line, 3, dico_cdao.get(u'total_size'))

        # Creation date
        sheet.write(line, 4, dico_cdao.get(u'date_crea'), self.xls_date)
        # Last update date
        sheet.write(line, 5, dico_cdao.get(u'date_actu'), self.xls_date)

        # Layers count
        sheet.write(line, 6, dico_cdao.get(u'layers_count'))

        # total number of fields
        sheet.write(line, 7, dico_cdao.get(u'total_fields'))

        # total number of objects
        sheet.write(line, 8, dico_cdao.get(u'total_objs'))

        # parsing layers
        for (layer_idx, layer_name) in zip(dico_cdao.get(u'layers_idx'),
                                           dico_cdao.get(u'layers_names')):
            # increment line
            line += 1
            champs = ""
            # get the layer informations
            cdao_layer = dico_cdao.get('{0}_{1}'.format(layer_idx, layer_name))

            # layer's name
            sheet.write(line, 6, cdao_layer.get(u'title'))

            # number of fields
            sheet.write(line, 7, cdao_layer.get(u'num_fields'))

            # number of objects
            sheet.write(line, 8, cdao_layer.get(u'num_obj'))

            # Geometry type
            sheet.write(line, 9, cdao_layer.get(u'type_geom'))

            # SRS label
            sheet.write(line, 10, cdao_layer.get(u'srs'))
            # SRS type
            sheet.write(line, 11, cdao_layer.get(u'srs_type'))
            # SRS reference EPSG code
            sheet.write(line, 12, cdao_layer.get(u'EPSG'))

            # Spatial extent
            emprise = u"Xmin : {0} - Xmax : {1} \
                       \nYmin : {2} - Ymax : {3}".format(unicode(cdao_layer.get(u'Xmin')),
                                                         unicode(cdao_layer.get(u'Xmax')),
                                                         unicode(cdao_layer.get(u'Ymin')),
                                                         unicode(cdao_layer.get(u'Ymax'))
                                                         )
            sheet.write(line, 13, emprise, self.xls_wrap)

            # Field informations
            fields_info = cdao_layer.get(u'fields')
            for chp in fields_info.keys():
                # field type
                if fields_info[chp] == 'Integer':
                    tipo = self.blabla.get(u'entier')
                elif fields_info[chp] == 'Real':
                    tipo = self.blabla.get(u'reel')
                elif fields_info[chp] == 'String':
                    tipo = self.blabla.get(u'string')
                elif fields_info[chp] == 'Date':
                    tipo = self.blabla.get(u'date')
                # concatenation of field informations
                try:
                    champs = champs + chp + u" (" + tipo + u") \n; "
                except UnicodeDecodeError:
                    # write a notification into the log file
                    self.dico_err[dico_cdao.get('name')] = self.blabla.get(u'err_encod') + \
                                                           chp.decode('latin1') + \
                                                           u"\n\n"
                    self.logger.warning('Field name with special letters: {}'.format(chp.decode('latin1')))
                    # decode the fucking field name
                    champs = champs + chp.decode('latin1') + u" ({}) ;".format(tipo)
                    # then continue
                    continue

            # Once all fieds explored, write them
            sheet.write(line, 14, champs)

            # write layer's name into the log
            self.logger.info('\t -- {0} = OK'.format(cdao_layer.get(u'title')))

        # End of function
        return self.feuyCDAO, line

    def dictionarize_mapdocs(self, mapdoc_infos, sheet, line):
        u""" write the infos of the map document into the Excel workbook """
        # in case of a source error
        if mapdoc_infos.get('error'):
            self.logger.warning('\tproblem detected')
            # source name
            sheet.write(line, 0, mapdoc_infos.get('name'))
            # link to parent folder
            link = 'HYPERLINK("{0}"; "{1}")'.format(mapdoc_infos.get(u'folder'),
                                                    self.blabla.get('browse'))
            sheet.write(line, 1, Formula(link), self.url)
            sheet.write(line, 2, self.blabla.get(mapdoc_infos.get('error')),
                                 self.xls_erreur)
            # incrementing line
            mapdoc_infos['layers_count'] = 0
            # exiting function
            return sheet, line
        else:
            pass

        # PDF source name
        sheet.write(line, 0, mapdoc_infos.get('name'))

        # Path of parent folder formatted to be a hyperlink
        try:
            link = 'HYPERLINK("{0}"; "{1}")'.format(mapdoc_infos.get(u'folder'),
                                                    self.blabla.get('browse'))
        except UnicodeDecodeError:
            # write a notification into the log file
            self.logger.warning('Path name with special letters: {}'.format(mapdoc_infos.get(u'folder').decode('utf8')))
            # decode the fucking path name
            link = 'HYPERLINK("{0}"; "{1}")'.format(mapdoc_infos.get(u'folder').decode('utf8'),
                                                    self.blabla.get('browse'))

        sheet.write(line, 1, Formula(link), self.url)

        # Name of parent folder
        sheet.write(line, 2, path.basename(mapdoc_infos.get(u'folder')))

        # Document title
        sheet.write(line, 3, mapdoc_infos.get(u'title'))

        # creator
        sheet.write(line, 4, mapdoc_infos.get(u'creator_prod'))

        # keywords
        sheet.write(line, 5, mapdoc_infos.get(u'keywords'))

        # subject
        sheet.write(line, 6, mapdoc_infos.get(u'subject'))

        # image resolution
        sheet.write(line, 7, mapdoc_infos.get(u'dpi'))

        # total size
        sheet.write(line, 8, mapdoc_infos.get(u'total_size'))

        # Creation date
        sheet.write(line, 9, mapdoc_infos.get(u'date_crea'), self.xls_date)
        # Last update date
        sheet.write(line, 10, mapdoc_infos.get(u'date_actu'), self.xls_date)

        # Image dimensions
        sheet.write(line, 11, mapdoc_infos.get(u'xOrigin'))
        sheet.write(line, 12, mapdoc_infos.get(u'yOrigin'))

        # SRS name
        sheet.write(line, 13, mapdoc_infos.get(u'srs'))
        # Type of SRS
        sheet.write(line, 14, mapdoc_infos.get(u'srs_type'))
        # EPSG code
        sheet.write(line, 15, mapdoc_infos.get(u'EPSG'))

        # Layers count
        sheet.write(line, 16, mapdoc_infos.get(u'layers_count'))

        # total number of fields
        sheet.write(line, 17, mapdoc_infos.get(u'total_fields'))

        # total number of objects
        sheet.write(line, 18, mapdoc_infos.get(u'total_objs'))

        # parsing layers
        for (layer_idx, layer_name) in zip(mapdoc_infos.get(u'layers_idx'),
                                           mapdoc_infos.get(u'layers_names')):
            # increment line
            line += 1
            champs = ""
            # get the layer informations
            try:
                mapdoc_layer = mapdoc_infos.get('{0}_{1}'.format(layer_idx,
                                                                 layer_name))
            except UnicodeDecodeError:
                mapdoc_layer = mapdoc_infos.get('{0}_{1}'.format(layer_idx,
                                                                 unicode(layer_name.decode('latin1'))))

            # layer's name
            sheet.write(line, 16, mapdoc_layer.get(u'title'))

            # number of fields
            sheet.write(line, 17, mapdoc_layer.get(u'num_fields'))

            # number of objects
            sheet.write(line, 18, mapdoc_layer.get(u'num_obj'))

            # Field informations
            fields_info = mapdoc_layer.get(u'fields')
            for chp in fields_info.keys():
                # field type
                if fields_info[chp] == u'Integer':
                    tipo = self.blabla.get(u'entier')
                elif fields_info[chp] == u'Real':
                    tipo = self.blabla.get(u'reel')
                elif fields_info[chp] == u'String':
                    tipo = self.blabla.get(u'string')
                elif fields_info[chp] == u'Date':
                    tipo = self.blabla.get(u'date')
                # concatenation of field informations
                try:
                    champs = champs + chp + u" ({0}) ; ".format(tipo)
                except UnicodeDecodeError:
                    # write a notification into the log file
                    self.dico_err[mapdoc_infos.get('name')] = self.blabla.get(u'err_encod') + \
                                                              chp.decode('latin1') + \
                                                              u"\n\n"
                    self.logger.warning('Field name with special letters: {}'.format(chp.decode('latin1')))
                    # decode the fucking field name
                    champs = champs + chp.decode('latin1') \
                                    + u" ({0}) ;".format(tipo)
                    # then continue
                    continue

            # Once all fieds explored, write them
            sheet.write(line, 19, champs)

            # write layer's name into the log
            self.logger.info('\t -- {0} = OK'.format(mapdoc_layer.get(u'title')))

        # End of function
        return self.feuyMAPS, line

    def dictionarize_pg(self, layer_infos, fields_info, sheet, line):
        u""" write the infos of the layer into the Excel workbook """
        # local variables
        champs = ""
        # in case of a source error
        if layer_infos.get('error'):
            self.logger.warning('\tproblem detected')
            sheet.write(line, 0, layer_infos.get('name'))
            sheet.write(line, 1, "{0}:{1}-{2}".format(self.host.get(),
                                                      self.port.get(),
                                                      self.dbnb.get()),
                                                      self.xls_erreur)
            sheet.write(line, 2, layer_infos.get('error'), self.xls_erreur)
            # Interruption of function
            return sheet
        else:
            pass

        # Name
        sheet.write(line, 0, layer_infos.get('name'))

        # Connection chain to reach database
        sheet.write(line, 1, "{0}:{1}-{2}".format(self.host.get(),
                                                  self.port.get(),
                                                  self.dbnb.get()))
        # Name of parent folder
        sheet.write(line, 2, path.basename(layer_infos.get(u'folder')))

        # Geometry type
        sheet.write(line, 5, layer_infos.get(u'type_geom'))
        # Spatial extent
        emprise = u"Xmin : " + unicode(layer_infos.get(u'Xmin')) +\
                  u", Xmax : " + unicode(layer_infos.get(u'Xmax')) +\
                  u", Ymin : " + unicode(layer_infos.get(u'Ymin')) +\
                  u", Ymax : " + unicode(layer_infos.get(u'Ymax'))
        sheet.write(line, 9, emprise)
        # Name of srs
        sheet.write(line, 6, layer_infos.get(u'srs'))
        # Type of SRS
        sheet.write(line, 7, layer_infos.get(u'srs_type'))
        # EPSG code
        sheet.write(line, 8, layer_infos.get(u'EPSG'))
        # Number of fields
        sheet.write(line, 3, layer_infos.get(u'num_fields'))
        # Name of objects
        sheet.write(line, 4, layer_infos.get(u'num_obj'))
        # Format of data
        sheet.write(line, 12, layer_infos.get(u'type'))
        # Field informations
        for chp in fields_info.keys():
            # field type
            if fields_info[chp][0] == 'Integer':
                tipo = self.blabla.get(u'entier')
            elif fields_info[chp][0] == 'Real':
                tipo = self.blabla.get(u'reel')
            elif fields_info[chp][0] == 'String':
                tipo = self.blabla.get(u'string')
            elif fields_info[chp][0] == 'Date':
                tipo = self.blabla.get(u'date')
            # concatenation of field informations
            try:
                champs = champs + chp +\
                         u" (" + tipo + self.blabla.get(u'longueur') +\
                         unicode(fields_info[chp][1]) +\
                         self.blabla.get(u'precision') +\
                         unicode(fields_info[chp][2]) + u") ; "
            except UnicodeDecodeError:
                # write a notification into the log file
                self.dico_err[layer_infos.get('name')] = self.blabla.get(u'err_encod') + \
                                                         chp.decode('latin1') + \
                                                         u"\n\n"
                self.logger.warning('Field name with special letters: {}'.format(chp.decode('latin1')))
                # decode the fucking field name
                champs = champs + chp.decode('latin1') \
                        + u" ({}, Lg. = {}, Pr. = {}) ;".format(tipo,
                                                                fields_info[chp][1],
                                                                fields_info[chp][2])
                # then continue
                continue

        # Once all fieds explored, write them
        sheet.write(line, 13, champs)

        # End of function
        return self.book, self.feuyPG

    def dictionarize_metrics(self):
        """ Write global statistices about datas examined """
        # total count of layers
        self.feuySTATS.write(1, 1, self.global_total_layers)

        # end of function
        return

    def savedico(self):
        u""" Save the Excel file """
        # Prompt of folder where save the file
        saved = asksaveasfilename(initialdir=self.target.get(),
                                  defaultextension='.xls',
                                  initialfile=self.output.get(),
                                  filetypes=[(self.blabla.get('gui_excel'),
                                              "*.xls")],
                                  # message='Select where to save the output file',
                                  title='Output location')

        # check if the extension is correctly indicated
        if path.splitext(saved)[1] != ".xls":
            saved = saved + ".xls"
        # save
        if saved != ".xls":
            try:
                self.book.save(saved)
                self.output.delete(0, END)
                self.output.insert(0, saved)
            except IOError:
                avert(title=u'Concurrent access',
                      message=u'Please close Microsoft Excel before saving.')
        else:
            avert(title=u'Not saved', message="You cancelled saving operation")
            exit()

        # End of function
        return self.book, saved

    def open_dir_file(self, target):
        """
        Open a file or a directory in the explorer of the operating system
        http://sametmax.com/ouvrir-un-fichier-avec-le-bon-programme-en-python
        """
        # check if the file or the directory exists
        if not path.exists(target):
            raise IOError('No such file: {0}'.format(target))

        # check the read permission
        if not access(target, R_OK):
            raise IOError('Cannot access file: {0}'.format(target))

        # open the directory or the file according to the os
        if opersys == 'win32':  # Windows
            proc = startfile(target)

        elif opersys.startswith('linux'):  # Linux:
            proc = subprocess.Popen(['xdg-open', target],
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE)

        elif opersys == 'darwin':  # Mac:
            proc = subprocess.Popen(['open', '--', target],
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE)

        else:
            raise NotImplementedError(
                "Your `%s` isn't a supported operating system`." % opersys)

        # end of function
        return proc

    def erreurStop(self, mess):
        u""" In case of error, close the GUI and stop the program """
        avert(title=u'Erreur', message=mess)
        self.logger.error(mess)
        self.root.destroy()
        exit()

###############################################################################
###### Stand alone program ########
###################################

if __name__ == '__main__':
    """ standalone execution """
    app = DicoGIS()
    app.mainloop()
