# -*- coding: UTF-8 -*-
#!/usr/bin/env python
from __future__ import unicode_literals
#------------------------------------------------------------------------------
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
#------------------------------------------------------------------------------

###############################################################################
########### Libraries #############
###################################

# Standard library
import ConfigParser  # to manipulate options.ini file

###############################################################################
############# Classes #############
###################################


class OptionsManager():
    def __init__(self, confile):
        u"""
        Main window constructor
        Creates 1 frame and 2 labelled subframes
        """
        print confile
        config = ConfigParser.RawConfigParser()

        self.load_settings(confile)





    def load_settings(self, confile):
        u""" load settings from last execution """
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
            self.opt_gdb.set(config.get('filters', 'opt_gdb'))
            self.opt_cdao.set(config.get('filters', 'opt_cdao'))
            self.opt_pdf.set(config.get('filters', 'opt_pdf'))
            # database settings
            self.host.set(config.get('database', 'host'))
            self.port.set(config.get('database', 'port'))
            self.dbnb.set(config.get('database', 'db_name'))
            self.user.set(config.get('database', 'user'))
            self.opt_pgvw.set(config.get('database', 'opt_views'))
            # log
            # self.logger.info('Last options loaded')
        except:
            # log
            # self.logger.info('1st use.')
        # End of function
        return self.def_rep, self.def_lang

    def save_settings(self, confile):
        u""" save last options in order to make the next excution more easy """
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
        config.set('filters', 'opt_gdb', self.opt_gdb.get())
        config.set('filters', 'opt_cdao', self.opt_cdao.get())
        config.set('filters', 'opt_pdf', self.opt_pdf.get())
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

###############################################################################
###### Stand alone program ########
###################################

if __name__ == '__main__':
    """ standalone execution """
    from os import path, chdir
    confile = r'options.ini'

    confile = path.abspath(confile)
    app = OptionsManager(confile)
