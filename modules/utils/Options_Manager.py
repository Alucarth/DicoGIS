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
        else:
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
        parent.opt_shp.set(self.config.get('filters', 'opt_shp'))
        parent.opt_tab.set(self.config.get('filters', 'opt_tab'))
        parent.opt_kml.set(self.config.get('filters', 'opt_kml'))
        parent.opt_gml.set(self.config.get('filters', 'opt_gml'))
        parent.opt_geoj.set(self.config.get('filters', 'opt_geoj'))
        parent.opt_gxt.set(self.config.get('filters', 'opt_gxt'))
        parent.opt_rast.set(self.config.get('filters', 'opt_rast'))
        parent.opt_egdb.set(self.config.get('filters', 'opt_egdb'))
        parent.opt_spadb.set(self.config.get('filters', 'opt_spadb'))
        parent.opt_cdao.set(self.config.get('filters', 'opt_cdao'))
        parent.opt_pdf.set(self.config.get('filters', 'opt_pdf'))
        parent.opt_lyr.set(self.config.get('filters', 'opt_lyr'))
        parent.opt_qgs.set(self.config.get('filters', 'opt_qgs'))
        parent.opt_mxd.set(self.config.get('filters', 'opt_mxd'))
        # database settings
        parent.host.set(self.config.get('database', 'host'))
        parent.port.set(self.config.get('database', 'port'))
        parent.dbnb.set(self.config.get('database', 'db_name'))
        parent.user.set(self.config.get('database', 'user'))
        parent.opt_pgvw.set(self.config.get('database', 'opt_views'))
        # proxy settings
        parent.opt_proxy.set(self.config.get('proxy', 'proxy_needed'))
        parent.opt_ntlm.set(self.config.get('proxy', 'proxy_type'))
        parent.prox_server.set(self.config.get('proxy', 'proxy_server'))
        parent.prox_port.set(self.config.get('proxy', 'proxy_port'))
        parent.prox_user.set(self.config.get('proxy', 'proxy_user'))
        # Isogeo settings
        parent.opt_isogeo.set(self.config.get('isogeo', 'opt_isogeo'))
        parent.url_OpenCatalog.set(self.config.get('isogeo', 'def_OC'))
        parent.isog_app_id.set(self.config.get('isogeo', 'app_id'))
        parent.isog_app_tk.set(self.config.get('isogeo', 'app_secret'))

        # log
        logging.info('Last options loaded')

        # End of function
        return

    def save_settings(self, parent):
        u""" save last options in order to make the next excution more easy """

        # add sections
        self.config.add_section('config')
        self.config.add_section('basics')
        self.config.add_section('filters')
        self.config.add_section('database')
        self.config.add_section('proxy')
        self.config.add_section('isogeo')
        self.config.add_section('youpi')
        # config
        self.config.set('config', 'DicoGIS_version', parent.DGversion)
        self.config.set('config', 'OS', platform.platform())
        # basics
        self.config.set('basics', 'def_codelang', self.ddl_lang.get())
        if self.target.get():
            self.config.set('basics', 'def_rep', self.target.get())
        else:
            self.config.set('basics', 'def_rep', self.def_rep)
        print(self.nb.index(self.nb.select()))
        self.config.set('basics', 'def_tab', self.nb.index(self.nb.select()))
        # filters
        self.config.set('filters', 'opt_shp', parent.opt_shp.get())
        self.config.set('filters', 'opt_tab', parent.opt_tab.get())
        self.config.set('filters', 'opt_kml', parent.opt_kml.get())
        self.config.set('filters', 'opt_gml', parent.opt_gml.get())
        self.config.set('filters', 'opt_geoj', parent.opt_geoj.get())
        self.config.set('filters', 'opt_gxt', parent.opt_gxt.get())
        self.config.set('filters', 'opt_rast', parent.opt_rast.get())
        self.config.set('filters', 'opt_egdb', parent.opt_egdb.get())
        self.config.set('filters', 'opt_spadb', parent.opt_spadb.get())
        self.config.set('filters', 'opt_cdao', parent.opt_cdao.get())
        self.config.set('filters', 'opt_pdf', parent.opt_pdf.get())
        self.config.set('filters', 'opt_lyr', parent.opt_lyr.get())
        self.config.set('filters', 'opt_qgs', parent.opt_qgs.get())
        self.config.set('filters', 'opt_mxd', parent.opt_mxd.get())
        # database settings
        self.config.set('database', 'host', parent.host.get())
        self.config.set('database', 'port', parent.port.get())
        self.config.set('database', 'db_name', parent.dbnb.get())
        self.config.set('database', 'user', parent.user.get())
        self.config.set('database', 'opt_views', parent.opt_pgvw.get())
        # proxy settings
        self.config.set('proxy', 'proxy_needed', parent.opt_proxy.get())
        self.config.set('proxy', 'proxy_type', parent.opt_ntlm.get())
        self.config.set('proxy', 'proxy_server', parent.prox_server.get())
        self.config.set('proxy', 'proxy_port', parent.prox_port.get())
        self.config.set('proxy', 'proxy_user', parent.prox_user.get())
        # Isogeo settings
        self.config.set('isogeo', 'opt_isogeo', parent.opt_isogeo.get())
        self.config.set('isogeo', 'def_OC', parent.url_OpenCatalog.get())
        self.config.set('isogeo', 'app_id', parent.isog_app_id.get())
        self.config.set('isogeo', 'app_secret', parent.isog_app_tk.get())

        # Writing the configuration file
        with open(confile, 'wb') as configfile:
            try:
                self.config.write(configfile)
                logging.info('Options saved.')
                return True
            except (UnicodeEncodeError, UnicodeDecodeError), e:
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
