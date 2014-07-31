# -*- coding: UTF-8 -*-
#!/usr/bin/env python
from __future__ import unicode_literals
#------------------------------------------------------------------------------
# Name:         DicoGIS
# Purpose:      Automatize the creation of a dictionnary of geographic data
#                   contained in a folders structures.
#                   It produces an Excel output file (.xls)
#
# Author:       Julien Moura (https://twitter.com/geojulien)
#
# Python:       2.7.x
# Created:      14/02/2013
# Updated:      31/07/2014
#
# Licence:      GPL 3
#------------------------------------------------------------------------------

DGversion = "2.0-beta.3"

###############################################################################
########### Libraries #############
###################################
# Standard library
from Tkinter import Tk, StringVar, IntVar, Image    # GUI
from Tkinter import W, PhotoImage, ACTIVE, DISABLED, END
from tkFileDialog import askdirectory, asksaveasfilename    # dialogs
from tkMessageBox import showinfo as info, showerror as avert
from ttk import Combobox, Progressbar, Style, Labelframe
from ttk import Label, Button, Entry, Radiobutton, Checkbutton  # advanced widgets
import tkFont   # font library

from sys import exit, platform as opersys
from os import listdir, walk, path         # files and folder managing
from os import environ as env, access, R_OK
from time import strftime
from webbrowser import open_new
import threading    # handling various subprocess

import ConfigParser         # to manipulate the options.ini file

import platform

import logging      # log files
from logging.handlers import RotatingFileHandler

import subprocess

from xml.etree import ElementTree as ET     # XML parsing and writer

# Python 3 backported
from collections import OrderedDict as OD   # ordered dictionary

# 3rd party libraries
try:
    from osgeo import gdal
    from osgeo import ogr
except ImportError:
    import gdal
    import ogr

from gdalconst import *
gdal.AllRegister()
ogr.UseExceptions()
gdal.UseExceptions()

from xlwt import Workbook, easyxf, Formula  # excel writer

# Custom modules
from modules import Read_Rasters    # custom extractor for rasters files
from modules import Read_SHP        # custom extractor for shapefiles
from modules import Read_TAB        # custom extractor for MapInfo Tables
from modules import Read_KML        # custom extractor for KML
from modules import Read_GML        # custom extractor for GML
from modules import Read_GeoJSON        # custom extractor for GeoJSON
from modules import Read_PostGIS     # custom extractor for geographic data in PostGIS databases
from modules import Read_GDB        # custom extractor for Esri FileGeoDataBase

# Imports depending on operating system
if opersys == 'win32':
    u""" windows """
    from os import startfile                            # to open a folder/file
    # try:
    #     import arcpy
    #     print("Great! ArcGIS is well installed.")
    # except ImportError:
    #     print("ArcGIS isn't registered in the sys.path")
    #     sys.path.append(r'C:\Program Files (x86)\ArcGIS\Desktop10.2\arcpy')
    #     sys.path.append(r'C:\Program Files (x86)\ArcGIS\Desktop10.2\bin')
    #     sys.path.append(r'C:\Program Files (x86)\ArcGIS\Desktop10.2\ArcToolbox\Scripts')
    #     try:
    #         import arcpy
    #         print("ArcGIS has been added to Python path and then imported.")
    #     except:
    #         print("ArcGIS isn't installed on this computer")
else:
    pass

###############################################################################
########### Variables #############
###################################


class DicoGIS(Tk):
    def __init__(self):
        u""" Main window constructor
        Creates 1 frame and 2 labelled subframes"""
        # creation and configuration of log file
        # see: http://sametmax.com/ecrire-des-logs-en-python/
        self.logger = logging.getLogger()
        self.logger.setLevel(logging.DEBUG)  # all errors will be get
        log_form = logging.Formatter('%(asctime)s || %(levelname)s || %(message)s')
        logfile = RotatingFileHandler('DicoGIS.log', 'a', 5000000, 1)
        logfile.setLevel(logging.DEBUG)
        logfile.setFormatter(log_form)
        self.logger.addHandler(logfile)
        self.logger.info('\t\t ============== DicoGIS =============')  # first write

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

        # variables
        self.num_folders = 0
        self.def_rep = ""       # default folder to search for
        self.def_lang = 'EN'    # default language to start
        self.li_shp = []         # list for shapefiles path
        self.li_tab = []         # list for MapInfo tables path
        self.li_raster = []     # list for rasters paths
        self.li_gdb = []     # list for Esri File Geodatabases
        self.li_kml = []    # list for KML path
        self.li_gml = []    # list for GML tables path
        self.li_geoj = []   # list for GeoJSON tables path
        self.li_raster_formats = (".ecw", ".tif", ".jp2")   # raster handled
        self.li_vectors_formats = (".shp", ".tab", ".kml", ".gml", ".geojson")  # vectors handled
        self.today = strftime("%Y-%m-%d")   # date of the day
        self.dico_layer = OD()      # dict for vectors informations
        self.dico_fields = OD()     # dict for fields informations
        self.dico_raster = OD()     # dict for rasters global informations
        self.dico_bands = OD()      # dict for bands informations
        self.dico_err = OD()     # errors list
        li_lang = [lg[5:-4] for lg in listdir(r'data/locale')]  # languages
        self.blabla = OD()      # texts dictionary

        # GUI fonts
        ft_tit = tkFont.Font(family="Times", size=10, weight=tkFont.BOLD)

        # fillfulling
        self.load_texts(self.def_lang)

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
        self.opt_rast = IntVar(self.FrFilters)  # able/disable rasters

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
        caz_rast = Checkbutton(self.FrFilters,
                               text=u'rasters ({0})'.format(', '.join(self.li_raster_formats)),
                               variable=self.opt_rast)
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
        caz_rast.grid(row=1,
                      column=5,
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
        # variables
        self.opt_pgvw = IntVar(self.FrDb)  # able/disable PostGIS views
        self.host = StringVar(self.FrDb, 'localhost')
        self.port = IntVar(self.FrDb, 5432)
        self.dbnb = StringVar(self.FrDb)
        self.user = StringVar(self.FrDb, 'postgres')
        self.pswd = StringVar(self.FrDb)
        # Form widgets
        caz_pgvw = Checkbutton(self.FrDb,
                               text=u'See views?',
                               variable=self.opt_pgvw)
        self.ent_H = Entry(self.FrDb, textvariable=self.host)
        self.ent_P = Entry(self.FrDb, textvariable=self.port, width=5)
        self.ent_D = Entry(self.FrDb, textvariable=self.dbnb)
        self.ent_U = Entry(self.FrDb, textvariable=self.user)
        self.ent_M = Entry(self.FrDb, textvariable=self.pswd, show='*')
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
               text='by Julien M.\n      2014',
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
                              text='Fichiers',
                              variable=self.typo,
                              value=1,
                              command=lambda: self.change_type())
        rd_pg = Radiobutton(self,
                            text='PostGIS',
                            variable=self.typo,
                            value=2,
                            command=lambda: self.change_type())
        # Basic buttons
        #img_proc = PhotoImage(master = self, file = 'img/Processing_TNP_10789.gif')
        self.val = Button(self,
                          text=self.blabla.get('gui_go'),
                          state=ACTIVE,
                          command=lambda: self.process())
        #self.val.config(image = img_proc)
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

        # loading previous options
        self.load_settings()

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
            self.opt_rast.set(config.get('filters', 'opt_rast'))
            # database settings
            self.host.set(config.get('database', 'host'))
            self.port.set(config.get('database', 'port'))
            self.dbnb.set(config.get('database', 'db_name'))
            self.user.set(config.get('database', 'user'))
            self.opt_pgvw.set(config.get('database', 'opt_views'))
            # log
            self.logger.info('Last options loaded')
        except:
            # log
            self.logger.info('1st use.')
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
        config.set('filters', 'opt_rast', self.opt_rast.get())
        # databse settings
        config.set('database', 'host', self.host.get())
        config.set('database', 'port', self.port.get())
        config.set('database', 'db_name', self.dbnb.get())
        config.set('database', 'user', self.user.get())
        config.set('database', 'opt_views', self.opt_pgvw.get())
        # Writing the configuration file
        with open(confile, 'wb') as configfile:
            config.write(configfile)
        # log
        self.logger.info('Options saved')
        # End of function
        return config

    def change_lang(self, event):
        u""" update the texts dictionary with the language selected """
        new_lang = event.widget.get()
        self.logger.info('\tLanguage switched to: {0}'.format(event.widget.get()))
        # change to the new language selected
        self.load_texts(new_lang)
        # update widgets text
        self.welcome.config(text=self.blabla.get('hi') + self.uzer)
        self.can.config(text=self.blabla.get('gui_quit'))
        self.FrPath.config(text=self.blabla.get('gui_fr1'))
        self.FrDb.config(text=self.blabla.get('gui_fr2'))
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
        self.output.insert(0, "DicoGIS_{0}_{1}.xls".format(
                                            path.split(self.target.get())[1],
                                            self.today ))
        # count geofiles in a separated thread
        proc = threading.Thread(target=self.ligeofiles,
                                args=(foldername, ))
        proc.daemon = True
        proc.start()
        # end of function
        return foldername

    def ligeofiles(self, foldertarget):
        u""" List shapefiles and MapInfo files (.tab, not .mid/mif) contained
        in the folders structure """
        # reseting global variables
        self.li_shp = []
        self.li_tab = []
        self.li_kml = []
        self.li_gml = []
        self.li_geoj = []
        self.li_raster = []
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
                except UnicodeDecodeError, e:
                    full_path = path.join(root, d.decode('latin1'))
                if full_path[-4:].lower() == '.gdb':
                    # add complete path of shapefile
                    self.li_gdb.append(path.abspath(full_path))
                else:
                    pass
            for f in files:
                """ looking for files with geographic data """
                try:
                    unicode(path.join(root, f))
                    full_path = path.join(root, f)
                except UnicodeDecodeError, e:
                    full_path = path.join(root, f.decode('latin1'))
                    print unicode(full_path), e
                # Looping on files contained
                if path.splitext(full_path.lower())[1].lower() == '.shp' and \
        (path.isfile('%s.dbf' % full_path[:-4]) or path.isfile('%s.DBF' % full_path[:-4])) and \
        (path.isfile('%s.shx' % full_path[:-4]) or path.isfile('%s.SHX' % full_path[:-4])):
                    """ listing compatible shapefiles """
                    # add complete path of shapefile
                    self.li_shp.append(full_path)
                elif path.splitext(full_path.lower())[1] == '.tab' and \
        (path.isfile(full_path[:-4] + '.dat') or path.isfile(full_path[:-4] + '.DAT')) and \
        (path.isfile(full_path[:-4] + '.map') or path.isfile(full_path[:-4] + '.MAP')) and \
        (path.isfile(full_path[:-4] + '.id') or path.isfile(full_path[:-4] + '.ID')):
                    """ listing MapInfo tables """
                    # add complete path of MapInfo file
                    self.li_tab.append(full_path)
                elif path.splitext(full_path.lower())[1] == '.kml':
                    """ listing KML """
                    # add complete path of KML file
                    self.li_kml.append(full_path)
                elif path.splitext(full_path.lower())[1] == '.gml':
                    """ listing GML """
                    # add complete path of KML file
                    self.li_gml.append(full_path)
                elif path.splitext(full_path.lower())[1] == '.geojson':
                    """ listing GeoJSON """
                    # add complete path of KML file
                    self.li_geoj.append(full_path)
                elif path.splitext(full_path.lower())[1] in self.li_raster_formats:
                    """ listing compatible rasters """
                    # add complete path of MapInfo file
                    self.li_raster.append(full_path)
                else:
                    continue

        # end of listing
        self.prog_layers.stop()
        self.logger.info('End of folders parsing: {0} shapefiles - {1} tables (MapInfo) - {2} KML - {3} GML - {4} GeoJSON\n{5} rasters - in {6}{7}'.format(len(self.li_shp),
                                                                                                                                                          len(self.li_tab),
                                                                                                                                                          len(self.li_kml),
                                                                                                                                                          len(self.li_gml),
                                                                                                                                                          len(self.li_geoj),
                                                                                                                                                          len(self.li_raster),
                                                                                                                                                          self.num_folders,
                                                                                                                                                          self.blabla.get('log_numfold')))
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
        # setting the label text and activing the buttons
        self.status.set('{0} shapefiles - {1} tables (MapInfo) - {2} KML - {3} GML - {4} GeoJSON\n{5} rasters - in {6}{7}'.format(len(self.li_shp), 
                                                                                                                                  len(self.li_tab), 
                                                                                                                                  len(self.li_kml),
                                                                                                                                  len(self.li_gml),
                                                                                                                                  len(self.li_geoj),
                                                                                                                                  len(self.li_raster),
                                                                                                                                  self.num_folders,
                                                                                                                                  self.blabla.get('log_numfold')))

        self.browsetarg.config(state=ACTIVE)
        self.val.config(state=ACTIVE)
        # End of function
        return foldertarget, self.li_shp, self.li_tab, self.li_kml, self.li_raster

    def process(self):
        """ check needed info and launch different processes """
        # saving settings
        self.save_settings()
        # process files or PostGIS database
        if self.typo.get() == 1:
            self.logger.info('=> files process started')
            self.process_files()
        elif self.typo.get() == 2:
            self.logger.info('=> DB process started')
            self.check_fields()
        else:
            pass
        # end of function
        return self.typo.get()

    def process_files(self):
        u""" launch the different processes """
        # check if at least a format has been choosen
        if (self.opt_shp.get() + self.opt_tab.get() + self.opt_kml.get() + 
            self.opt_gml.get() + self.opt_geoj.get() + self.opt_rast.get()):
            pass
        else:
            avert('DicoGIS - User error', self.blabla.get('noformat'))
            return
        # check if there are some layers into the folder structure
        if (len(self.li_shp) + len(self.li_tab) + len(self.li_kml) + 
            len(self.li_gml) + len(self.li_geoj) + len(self.li_raster)):
            pass
        else:
            avert('DicoGIS - User error', self.blabla.get('nodata'))
            return
        # creating the Excel workbook
        self.configexcel()
        self.logger.info('Excel file created')
        # configuring the progress bar
        total_files = 0
        if self.opt_shp.get():
            total_files += len(self.li_shp)
        else:
            pass
        if self.opt_tab.get():
            total_files += len(self.li_tab)
        else:
            pass
        if self.opt_kml.get():
            total_files += len(self.li_kml)
        else:
            pass
        if self.opt_gml.get():
            total_files += len(self.li_gml)
        else:
            pass
        if self.opt_geoj.get():
            total_files += len(self.li_geoj)
        else:
            pass
        if self.opt_rast.get():
            total_files += len(self.li_raster)
        else:
            pass
        print total_files
        self.prog_layers["maximum"] = total_files
        self.prog_layers["value"]
        # getting the info from shapefiles and compile it in the excel
        # line_folders = 1    # line rank of directories dictionary
        line_vectors = 1    # line rank of vectors dictionary
        line_rasters = 1    # line rank of rasters dictionary

        if self.opt_shp.get():
            self.logger.info('\n\tProcessing shapefiles: start')
            for shp in self.li_shp:
                """ looping on shapefiles list """
                self.status.set(path.basename(shp))
                self.logger.info('\n' + shp)
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
                except AttributeError, e:
                    """ empty files """
                    self.logger.error(e)
                    continue
                except RuntimeError, e:
                    """ corrupt files """
                    self.logger.error(e)
                    continue
                except Exception, e:
                    self.logger.error(e)
                    continue
                # writing to the Excel dictionary
                self.dictionarize_vectors(self.dico_layer,
                                          self.dico_fields,
                                          self.feuy1,
                                          line_vectors)
                self.logger.info('\t Wrote into the dictionary')
                # increment the line number
                line_vectors = line_vectors + 1
                # increment the progress bar
                self.prog_layers["value"] = self.prog_layers["value"] + 1
                self.update()
        else:
            self.logger.info('\tIgnoring {0} shapefiles'.format(len(self.li_shp)))
            pass

        if self.opt_tab.get():
            self.logger.info('\n\tProcessing MapInfo tables: start')
            for tab in self.li_tab:
                """ looping on MapInfo tables list """
                self.status.set(path.basename(tab))
                self.logger.info('\n' + tab)
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
                except AttributeError, e:
                    self.logger.error(e)
                    continue
                except RuntimeError, e:
                    self.logger.error(e)
                    continue
                except Exception, e:
                    self.logger.error(e)
                    continue
                # writing to the Excel dictionary
                self.dictionarize_vectors(self.dico_layer,
                                          self.dico_fields,
                                          self.feuy1, line_vectors)
                self.logger.info('\t Wrote into the dictionary')
                # increment the line number
                line_vectors = line_vectors + 1
                # increment the progress bar
                self.prog_layers["value"] = self.prog_layers["value"] + 1
                self.update()
        else:
            self.logger.info('\tIgnoring {0} MapInfo tables'.format(len(self.li_tab)))
            pass

        if self.opt_kml.get():
            self.logger.info('\n\tProcessing KML: start')
            for kml in self.li_kml:
                """ looping on KML list """
                self.status.set(path.basename(kml))
                self.logger.info('\n' + kml)
                # reset recipient data
                self.dico_layer.clear()
                self.dico_fields.clear()
                # getting the informations
                try:
                    Read_KML(path.abspath(kml),
                             self.dico_layer,
                             self.dico_fields,
                             'KML',
                             self.blabla)
                    self.logger.info('\t Infos OK')
                except AttributeError, e:
                    self.logger.error(e)
                    continue
                except RuntimeError, e:
                    self.logger.error(e)
                    continue
                except Exception, e:
                    self.logger.error(e)
                    continue
                # writing to the Excel dictionary
                self.dictionarize_vectors(self.dico_layer,
                                          self.dico_fields,
                                          self.feuy1,
                                          line_vectors)
                self.logger.info('\t Wrote into the dictionary')
                # increment the line number
                line_vectors = line_vectors + 1
                # increment the progress bar
                self.prog_layers["value"] = self.prog_layers["value"] + 1
                self.update()
        else:
            self.logger.info('\tIgnoring {0} KML'.format(len(self.li_kml)))
            pass

        if self.opt_gml.get():
            self.logger.info('\n\tProcessing GML: start')
            for gml in self.li_gml:
                """ looping on GML list """
                self.status.set(path.basename(gml))
                self.logger.info('\n' + gml)
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
                except AttributeError, e:
                    self.logger.error(e)
                    continue
                except RuntimeError, e:
                    self.logger.error(e)
                    continue
                except Exception, e:
                    self.logger.error(e)
                    continue
                # writing to the Excel dictionary
                self.dictionarize_vectors(self.dico_layer,
                                          self.dico_fields,
                                          self.feuy1, line_vectors)
                self.logger.info('\t Wrote into the dictionary')
                # increment the line number
                line_vectors = line_vectors + 1
                # increment the progress bar
                self.prog_layers["value"] = self.prog_layers["value"] + 1
                self.update()
        else:
            self.logger.info('\tIgnoring {0} GML'.format(len(self.li_gml)))
            pass

        if self.opt_geoj.get():
            self.logger.info('\n\tProcessing GeoJSON: start')
            for geojson in self.li_geoj:
                """ looping on GeoJSON list """
                self.status.set(path.basename(geojson))
                self.logger.info('\n' + geojson)
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
                except AttributeError, e:
                    self.logger.error(e)
                    continue
                except RuntimeError, e:
                    self.logger.error(e)
                    continue
                except Exception, e:
                    self.logger.error(e)
                    continue
                # writing to the Excel dictionary
                self.dictionarize_vectors(self.dico_layer,
                                          self.dico_fields,
                                          self.feuy1,
                                          line_vectors)
                self.logger.info('\t Wrote into the dictionary')
                # increment the line number
                line_vectors = line_vectors + 1
                # increment the progress bar
                self.prog_layers["value"] = self.prog_layers["value"] + 1
                self.update()
        else:
            self.logger.info('\tIgnoring {0} GeoJSON'.format(len(self.li_geoj)))
            pass

        if self.opt_rast.get():
            self.logger.info('\n\tProcessing rasters: start')
            for raster in self.li_raster:
                """ looping on rasters list """
                self.status.set(path.basename(raster))
                self.logger.info('\n' + raster)
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
                #   print(self.path.abspath(dico_raster), self.dico_bands)
                except AttributeError, e:
                    self.logger.error(e)
                    continue
                except RuntimeError, e:
                    self.logger.error(e)
                    continue
                except Exception, e:
                    self.logger.error(e)
                    continue
                # writing to the Excel dictionary
                self.dictionarize_rasters(self.dico_raster,
                                          self.dico_bands,
                                          self.feuy2,
                                          line_rasters)
                self.logger.info('\t Wrote into the dictionary')
                # increment the line number
                line_rasters = line_rasters + 1
                # increment the progress bar
                self.prog_layers["value"] = self.prog_layers["value"] + 1
                self.update()
        else:
            self.logger.info('\tIgnoring {0} rasters'.format(len(self.li_raster)))
            pass

        # saving dictionary
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
                                 self.feuy3,
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
        # saving settings
        self.save_settingspath.abspath(())

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
        u""" testing database connection settings using OGR specific exceptions """
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
        except Exception, e:
            self.logger.warning("Connection failed: {0}.".format(e))
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

        # columns headers
        if self.typo.get() == 1 \
            and (len(self.li_tab) + len(self.li_shp) + len(self.li_gml)
            + len(self.li_geoj) + len(self.li_kml)) > 0:
            """ adding a new sheet for vectors informations """
            self.feuy1 = self.book.add_sheet(u'Vectors', cell_overwrite_ok=True)
            self.feuy1.write(0, 0, self.blabla.get('nomfic'), self.entete)
            self.feuy1.write(0, 1, self.blabla.get('path'), self.entete)
            self.feuy1.write(0, 2, self.blabla.get('theme'), self.entete)
            self.feuy1.write(0, 3, self.blabla.get('num_attrib'), self.entete)
            self.feuy1.write(0, 4, self.blabla.get('num_objets'), self.entete)
            self.feuy1.write(0, 5, self.blabla.get('geometrie'), self.entete)
            self.feuy1.write(0, 6, self.blabla.get('srs'), self.entete)
            self.feuy1.write(0, 7, self.blabla.get('srs_type'), self.entete)
            self.feuy1.write(0, 8, self.blabla.get('codepsg'), self.entete)
            self.feuy1.write(0, 9, self.blabla.get('emprise'), self.entete)
            self.feuy1.write(0, 10, self.blabla.get('date_crea'), self.entete)
            self.feuy1.write(0, 11, self.blabla.get('date_actu'), self.entete)
            self.feuy1.write(0, 12, self.blabla.get('format'), self.entete)
            self.feuy1.write(0, 13, self.blabla.get('li_depends'), self.entete)
            self.feuy1.write(0, 14, self.blabla.get('tot_size'), self.entete)
            self.feuy1.write(0, 15, self.blabla.get('li_chps'), self.entete)
            self.logger.info('Sheet vectors adedd')
            # tunning headers
            lg_shp_names = [len(lg) for lg in self.li_shp]
            lg_tab_names = [len(lg) for lg in self.li_tab]
            self.feuy1.col(0).width = max(lg_shp_names + lg_tab_names) * 100
            self.feuy1.col(1).width = len(self.blabla.get('browse')) * 256
        else:
            pass

        if self.typo.get() == 1 and len(self.li_raster) > 0:
            """ adding a new sheet for rasters informations """
            self.feuy2 = self.book.add_sheet(u'Rasters', cell_overwrite_ok=True)
            self.feuy2.write(0, 0, self.blabla.get('nomfic'), self.entete)
            self.feuy2.write(0, 1, self.blabla.get('path'), self.entete)
            self.feuy2.write(0, 2, self.blabla.get('theme'), self.entete)
            self.feuy2.write(0, 3, self.blabla.get('size_Y'), self.entete)
            self.feuy2.write(0, 4, self.blabla.get('size_X'), self.entete)
            self.feuy2.write(0, 5, self.blabla.get('pixel_w'), self.entete)
            self.feuy2.write(0, 6, self.blabla.get('pixel_h'), self.entete)
            self.feuy2.write(0, 7, self.blabla.get('origin_x'), self.entete)
            self.feuy2.write(0, 8, self.blabla.get('origin_y'), self.entete)
            self.feuy2.write(0, 9, self.blabla.get('srs_type'), self.entete)
            self.feuy2.write(0, 10, self.blabla.get('codepsg'), self.entete)
            self.feuy2.write(0, 11, self.blabla.get('emprise'), self.entete)
            self.feuy2.write(0, 12, self.blabla.get('date_crea'), self.entete)
            self.feuy2.write(0, 13, self.blabla.get('date_actu'), self.entete)
            self.feuy2.write(0, 14, self.blabla.get('num_bands'), self.entete)
            self.feuy2.write(0, 15, self.blabla.get('format'), self.entete)
            self.feuy2.write(0, 16, self.blabla.get('compression'), self.entete)
            self.feuy2.write(0, 17, self.blabla.get('coloref'), self.entete)
            self.feuy2.write(0, 18, self.blabla.get('li_depends'), self.entete)
            self.feuy2.write(0, 19, self.blabla.get('total_size'), self.entete)
            self.logger.info('Sheet rasters created')
            # tunning headers
            lg_rast_names = [len(lg) for lg in self.li_raster]
            self.feuy2.col(0).width = max(lg_rast_names) * 100
            self.feuy2.col(1).width = len(self.blabla.get('browse')) * 256
        else:
            pass

        if self.typo.get() == 2:
            """ adding a new sheet for rasters informations """
            self.feuy3 = self.book.add_sheet(u'PostGIS', cell_overwrite_ok=True)
            self.feuy3.write(0, 0, self.blabla.get('nomfic'), self.entete)
            self.feuy3.write(0, 1, self.blabla.get('conn_chain'), self.entete)
            self.feuy3.write(0, 2, self.blabla.get('schema'), self.entete)
            self.feuy3.write(0, 3, self.blabla.get('num_attrib'), self.entete)
            self.feuy3.write(0, 4, self.blabla.get('num_objets'), self.entete)
            self.feuy3.write(0, 5, self.blabla.get('geometrie'), self.entete)
            self.feuy3.write(0, 6, self.blabla.get('srs'), self.entete)
            self.feuy3.write(0, 7, self.blabla.get('srs_type'), self.entete)
            self.feuy3.write(0, 8, self.blabla.get('codepsg'), self.entete)
            self.feuy3.write(0, 9, self.blabla.get('emprise'), self.entete)
            self.feuy3.write(0, 10, self.blabla.get('date_crea'), self.entete)
            self.feuy3.write(0, 11, self.blabla.get('date_actu'), self.entete)
            self.feuy3.write(0, 12, self.blabla.get('format'), self.entete)
            self.feuy3.write(0, 13, self.blabla.get('li_chps'), self.entete)
            self.logger.info('Sheet PostGIS created')
            # tunning headers
            # lg_rast_names = [len(lg) for lg in self.li_raster]
            # self.feuy3.col(0).width=max(lg_rast_names)*100
            # self.feuy3.col(1).width=len(self.blabla.get('browse'))*256
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
            return self.book, self.feuy1
        else:
            pass

        # Name
        sheet.write(line, 0, layer_infos.get('name'))
        # Path of containing folder formatted to be a hyperlink
        link = 'HYPERLINK("{0}"; "{1}")'.format(layer_infos.get(u'folder'),
                                                self.blabla.get('browse'))
        sheet.write(line, 1, Formula(link), self.url)
        # Name of containing folder
        # with an exception if this is the format name
        if path.basename(layer_infos.get(u'folder')).lower() in self.li_vectors_formats:
            sheet.write(line, 2, path.basename(layer_infos.get(u'folder')))
        else:
            sheet.write(line, 2, path.basename(path.dirname(layer_infos.get(u'folder'))))

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
        # Creation date
        sheet.write(line, 10, layer_infos.get(u'date_crea'))
        # Last update date
        sheet.write(line, 11, layer_infos.get(u'date_actu'))
        # Format of data
        sheet.write(line, 12, layer_infos.get(u'type'))
        # dependencies
        self.feuy1.write(line, 13, ' | '.join(layer_infos.get(u'dependencies')))
        # total size
        self.feuy1.write(line, 14, layer_infos.get(u'total_size'))
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

        # End of function
        return self.book, self.feuy1

    def dictionarize_rasters(self, dico_raster, dico_bands, sheet, line):
        u""" write the infos of the layer into the Excel workbook """
        # in case of a source error
        if dico_raster.get('error'):
            self.logger.warning('\tproblem detected')
            sheet.write(line, 0, layer_infos.get('name'))
            link = 'HYPERLINK("' + layer_infos.get(u'folder') \
                             + '"; "' + self.blabla.get('browse') + '")'
            sheet.write(line, 1, Formula(link), self.url)
            sheet.write(line, 2, self.blabla.get((layer_infos.get('error')), self.xls_erreur))
            # Interruption of function
            return self.book, self.feuy2
        else:
            pass

        # Name
        sheet.write(line, 0, dico_raster.get('name'))
        # Path of containing folder formatted to be a hyperlink
        link = 'HYPERLINK("' + dico_raster.get(u'folder') \
                             + '"; "' + self.blabla.get('browse') + '")'
        sheet.write(line, 1, Formula(link), self.url)
        # Name of containing folder
        sheet.write(line, 2, path.basename(dico_raster.get(u'folder')))
        # Name of containing folder
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
        sheet.write(line, 12, dico_raster.get(u'date_crea'))
        # Last update date
        sheet.write(line, 12, dico_raster.get(u'date_actu'))
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
        sheet.write(line, 18, dico_raster.get(u'total_size'))

        # End of function
        return line, sheet

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
        # Name of containing folder
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
        # # Creation date
        # sheet.write(line, 10, layer_infos.get(u'date_crea'))
        # # Last update date
        # sheet.write(line, 11, layer_infos.get(u'date_actu'))
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
        return self.book, self.feuy3

    def savedico(self):
        u""" Save the Excel file """
        # Prompt of folder where save the file
        saved = asksaveasfilename(initialdir=self.target.get(),
                                  defaultextension='.xls',
                                  initialfile=self.output.get(),
                                  filetypes=[(self.blabla.get('gui_excel'),
                                              "*.xls")])

        # check if the extension is correctly indicated
        if path.splitext(saved)[1] != ".xls":
            saved = saved + ".xls"
        # save
        self.book.save(saved)
        self.output.delete(0, END)
        self.output.insert(0, saved)

        # # notification
        # total_files = unicode(len(self.li_shp) + len(self.li_tab))
        # info(title=self.blabla.get('info_end'),
        #      message=self.blabla.get('info_end2'))

        # End of function
        return self.book, saved

    def open_dir_file(self, target):
        """ open a file or a directory in the explorer of the operating system
        see: http://sametmax.com/ouvrir-un-fichier-avec-le-bon-programme-en-python """
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
