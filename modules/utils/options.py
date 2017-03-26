# -*- coding: UTF-8 -*-
#!/usr/bin/env python
from __future__ import unicode_literals
# ------------------------------------------------------------------------------
# Name:         Options Manager
# Purpose:      Load & save settings of a parent module
#
# Author:       Julien Moura (@geojulien)
#
# Python:       2.7.x
# Created:      21/09/2014
# Updated:      21/09/2014
#
# Licence:      GPL 3
# -----------------------------------------------------------------------------

# #############################################################################
# ########## Libraries #############
# ##################################

# Standard library
import ConfigParser  # to manipulate options.ini file
import logging
from os import path
import platform

# #############################################################################
# ############ Classes #############
# ##################################


class OptionsManager(object):
    def __init__(self, confile=r"..\..\options.ini"):
        u"""
        Main window constructor
        Creates 1 frame and 2 labelled subframes
        """
        super(OptionsManager, self).__init__()
        self.confile = path.realpath(confile)
        # first use or not
        if not path.isfile(self.confile):
            logging.info("No options.ini file found. First use: welcome!")
            self.first_use = 1
        else:
            logging.info("Options.ini file found. ")
            self.first_use = 0
            pass

        # using safe parser
        self.config = ConfigParser.SafeConfigParser()
        self.config.read(confile)

    def load_settings(self, parent):
        u""" load settings from last execution """
        # basics
        parent.def_lang = self.config.get('basics', 'def_codelang')
        parent.def_rep = self.config.get('basics', 'def_rep')
        parent.nb.select(self.config.get('basics', 'def_tab'))
        # filters
        parent.tab_files.opt_shp.set(self.config.get('filters', 'opt_shp'))
        parent.tab_files.opt_tab.set(self.config.get('filters', 'opt_tab'))
        parent.tab_files.opt_kml.set(self.config.get('filters', 'opt_kml'))
        parent.tab_files.opt_gml.set(self.config.get('filters', 'opt_gml'))
        parent.tab_files.opt_geoj.set(self.config.get('filters', 'opt_geoj'))
        parent.tab_files.opt_gxt.set(self.config.get('filters', 'opt_gxt'))
        parent.tab_files.opt_rast.set(self.config.get('filters', 'opt_rast'))
        parent.tab_files.opt_egdb.set(self.config.get('filters', 'opt_egdb'))
        parent.tab_files.opt_spadb.set(self.config.get('filters', 'opt_spadb'))
        parent.tab_files.opt_cdao.set(self.config.get('filters', 'opt_cdao'))
        parent.tab_files.opt_pdf.set(self.config.get('filters', 'opt_pdf'))
        parent.tab_files.opt_lyr.set(self.config.get('filters', 'opt_lyr'))
        parent.tab_files.opt_qgs.set(self.config.get('filters', 'opt_qgs'))
        parent.tab_files.opt_mxd.set(self.config.get('filters', 'opt_mxd'))
        # database settings
        parent.tab_sgbd.host.set(self.config.get('database', 'host'))
        parent.tab_sgbd.port.set(self.config.get('database', 'port'))
        parent.tab_sgbd.dbnb.set(self.config.get('database', 'db_name'))
        parent.tab_sgbd.user.set(self.config.get('database', 'user'))
        parent.tab_sgbd.opt_pgvw.set(self.config.get('database', 'opt_views'))
        # proxy settings
        parent.tab_options.opt_proxy.set(self.config.get('proxy', 'proxy_needed'))
        parent.tab_options.opt_ntlm.set(self.config.get('proxy', 'proxy_type'))
        parent.tab_options.prox_server.set(self.config.get('proxy', 'proxy_server'))
        parent.tab_options.prox_port.set(self.config.get('proxy', 'proxy_port'))
        parent.tab_options.prox_user.set(self.config.get('proxy', 'proxy_user'))
        # Isogeo settings
        parent.tab_options.opt_isogeo.set(self.config.get('isogeo', 'opt_isogeo'))
        parent.tab_options.isog_app_id.set(self.config.get('isogeo', 'app_id'))
        parent.tab_options.set(self.config.get('isogeo', 'app_secret'))

        # log
        logging.info('Last options loaded')

        # End of function
        return

    def save_settings(self, parent):
        u""" save last options in order to make the next excution more easy """

        # add sections
        if self.first_use:
            self.config.add_section('config')
            self.config.add_section('basics')
            self.config.add_section('filters')
            self.config.add_section('database')
            self.config.add_section('proxy')
            self.config.add_section('isogeo')
        else:
            pass

        # config
        self.config.set('config', 'DicoGIS_version', parent.DGversion)
        self.config.set('config', 'OS', platform.platform())
        # basics
        self.config.set('basics', 'def_codelang', parent.ddl_lang.get())
        if parent.tab_files.target.get():
            self.config.set('basics', 'def_rep', parent.tab_files.target.get())
        else:
            self.config.set('basics', 'def_rep', parent.def_rep)
        self.config.set('basics', 'def_tab', str(parent.nb.index(
                                                 parent.nb.select())))
        # filters
        self.config.set('filters', 'opt_shp', unicode(parent.tab_files.opt_shp.get()))
        self.config.set('filters', 'opt_tab', unicode(parent.tab_files.opt_tab.get()))
        self.config.set('filters', 'opt_kml', unicode(parent.tab_files.opt_kml.get()))
        self.config.set('filters', 'opt_gml', unicode(parent.tab_files.opt_gml.get()))
        self.config.set('filters', 'opt_geoj', unicode(parent.tab_files.opt_geoj.get()))
        self.config.set('filters', 'opt_gxt', unicode(parent.tab_files.opt_gxt.get()))
        self.config.set('filters', 'opt_rast', unicode(parent.tab_files.opt_rast.get()))
        self.config.set('filters', 'opt_egdb', unicode(parent.tab_files.opt_egdb.get()))
        self.config.set('filters', 'opt_spadb', unicode(parent.tab_files.opt_spadb.get()))
        self.config.set('filters', 'opt_cdao', unicode(parent.tab_files.opt_cdao.get()))
        self.config.set('filters', 'opt_pdf', unicode(parent.tab_files.opt_pdf.get()))
        self.config.set('filters', 'opt_lyr', unicode(parent.tab_files.opt_lyr.get()))
        self.config.set('filters', 'opt_qgs', unicode(parent.tab_files.opt_qgs.get()))
        self.config.set('filters', 'opt_mxd', unicode(parent.tab_files.opt_mxd.get()))
        # database settings
        self.config.set('database', 'host', parent.tab_sgbd.host.get())
        self.config.set('database', 'port', unicode(parent.tab_sgbd.port.get()))
        self.config.set('database', 'db_name', parent.tab_sgbd.dbnb.get())
        self.config.set('database', 'user', parent.tab_sgbd.user.get())
        self.config.set('database', 'opt_views', unicode(parent.tab_sgbd.opt_pgvw.get()))
        # proxy settings
        self.config.set('proxy', 'proxy_needed', unicode(parent.tab_options.opt_proxy.get()))
        self.config.set('proxy', 'proxy_type', unicode(parent.tab_options.opt_ntlm.get()))
        self.config.set('proxy', 'proxy_server', parent.tab_options.prox_server.get())
        self.config.set('proxy', 'proxy_port', unicode(parent.tab_options.prox_port.get()))
        self.config.set('proxy', 'proxy_user', parent.tab_options.prox_user.get())
        # Isogeo settings
        self.config.set('isogeo', 'opt_isogeo', unicode(parent.tab_options.opt_isogeo.get()))
        self.config.set('isogeo', 'app_id', parent.tab_options.isog_app_id.get())
        self.config.set('isogeo', 'app_secret', parent.tab_options.isog_app_tk.get())

        # Writing the configuration file
        with open(self.confile, 'wb') as configfile:
            try:
                self.config.write(configfile)
                logging.info('Options saved.')
                return True
            except (UnicodeEncodeError, UnicodeDecodeError) as e:
                logging.error("Options couldn't be saved because of: {0}".format(e))
                return False

        # End of function
        return

# ##############################################################################
# ##### Stand alone program ########
# ##################################

if __name__ == '__main__':
    """ standalone execution """
    from os import path, chdir
    confile = r'options.ini'

    confile = path.abspath(confile)
    app = OptionsManager(confile)
