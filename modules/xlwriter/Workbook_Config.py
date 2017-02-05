# -*- coding: UTF-8 -*-
#!/usr/bin/env python
from __future__ import unicode_literals
from __future__ import print_function
#------------------------------------------------------------------------------
# Name:         Workbook configuration wizard
# Purpose:      set an Excel (2003 ie .xls) sheets and headers according
#               to options selected
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
import logging      # log files
from logging.handlers import RotatingFileHandler

# Python 3 backported
from collections import OrderedDict as OD   # ordered dictionary

# 3rd party libraries
from xlwt import Workbook, easyxf   # excel writer

###############################################################################
############# Classes #############
###################################


class ConfigExcel():
    def __init__(self, workbook, opt_vec=0, opt_rast=0, opt_gdb=0, opt_maps=0,
                 opt_cdao=0, opt_pgis=0, opt_isogeo=0, text=OD()):
        u"""
        Set the global configuration of Excel workbook (styles, headers, etc.)

        opt_vec = option to add and set sheet for vectors
        opt_rast = option to add and set sheet for rasters
        opt_gdb = option to add and set sheet for file geodatabases
        opt_cdao = option to add and set sheet for CAD files
        opt_maps = option to add and set sheet for maps documents
        opt_pgis = option to add and set sheet for PostGIS tables & views
        opt_isogeo = option to add and set sheet for Isogeo Open Catalog
        """
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

        #
        self.text = text

        # vectors files
        if opt_vec:
            self.add_vectors_sheet()
        else:
            pass

        # rasters files
        if opt_rast:
            self.add_rasters_sheet()
        else:
            pass

        # file geodatabases
        if opt_gdb:
            self.add_gdb_sheet()
        else:
            pass

        # maps & documents
        if opt_maps:
            self.add_maps_sheet()
        else:
            pass

        # CAD files
        if opt_cdao:
            self.add_cdao_sheet()
        else:
            pass

        # PostGIS database
        if opt_pgis:
            self.add_postgis_sheet()
        else:
            pass

        # Isogeo OpenCatalog
        if opt_isogeo:
            self.add_isogeo_sheet(workbook)
        else:
            pass

        # freezing headers line and first column
        # for sheet in self.sheets():
        #     sheet.set_panes_frozen(True)
        #     sheet.set_horz_split_pos(1)
        #     sheet.set_vert_split_pos(1)

    def add_vectors_sheet(self, xls_workbook, text, style_headers):
        """
        sets sheet dedicated to vectors information
        """
        # sheet
        feuyVC = workbook.add_sheet(text.get('sheet_vectors'),
                                    cell_overwrite_ok=True)
        # headers
        feuyVC.write(0, 0, text.get('nomfic'), entete)
        feuyVC.write(0, 1, text.get('path'), entete)
        feuyVC.write(0, 2, text.get('theme'), entete)
        feuyVC.write(0, 3, text.get('num_attrib'), entete)
        feuyVC.write(0, 4, text.get('num_objets'), entete)
        feuyVC.write(0, 5, text.get('geometrie'), entete)
        feuyVC.write(0, 6, text.get('srs'), entete)
        feuyVC.write(0, 7, text.get('srs_type'), entete)
        feuyVC.write(0, 8, text.get('codepsg'), entete)
        feuyVC.write(0, 9, text.get('emprise'), entete)
        feuyVC.write(0, 10, text.get('date_crea'), entete)
        feuyVC.write(0, 11, text.get('date_actu'), entete)
        feuyVC.write(0, 12, text.get('format'), entete)
        feuyVC.write(0, 13, text.get('li_depends'), entete)
        feuyVC.write(0, 14, text.get('tot_size'), entete)
        feuyVC.write(0, 15, text.get('li_chps'), entete)
        self.logger.info('Sheet vectors adedd')
        # tunning headers
        lg_shp_names = [len(lg) for lg in self.li_shp]
        lg_tab_names = [len(lg) for lg in self.li_tab]
        self.feuyVC.col(0).width = max(lg_shp_names + lg_tab_names) * 100
        self.feuyVC.col(1).width = len(self.text.get('browse')) * 256
        self.feuyVC.col(9).width = 35 * 256
        # freezing headers line and first column
        self.feuyVC.set_panes_frozen(True)
        self.feuyVC.set_horz_split_pos(1)
        self.feuyVC.set_vert_split_pos(1)

        # end of function
        return

    def add_rasters_sheet(self):
        """
        sets sheet dedicated to rasters information
        """
        self.feuyRS = self.book.add_sheet(self.text.get('sheet_rasters'),
                                          cell_overwrite_ok=True)
        # headers
        self.feuyRS.write(0, 0, self.text.get('nomfic'), self.entete)
        self.feuyRS.write(0, 1, self.text.get('path'), self.entete)
        self.feuyRS.write(0, 2, self.text.get('theme'), self.entete)
        self.feuyRS.write(0, 3, self.text.get('size_Y'), self.entete)
        self.feuyRS.write(0, 4, self.text.get('size_X'), self.entete)
        self.feuyRS.write(0, 5, self.text.get('pixel_w'), self.entete)
        self.feuyRS.write(0, 6, self.text.get('pixel_h'), self.entete)
        self.feuyRS.write(0, 7, self.text.get('origin_x'), self.entete)
        self.feuyRS.write(0, 8, self.text.get('origin_y'), self.entete)
        self.feuyRS.write(0, 9, self.text.get('srs_type'), self.entete)
        self.feuyRS.write(0, 10, self.text.get('codepsg'), self.entete)
        self.feuyRS.write(0, 11, self.text.get('emprise'), self.entete)
        self.feuyRS.write(0, 12, self.text.get('date_crea'), self.entete)
        self.feuyRS.write(0, 13, self.text.get('date_actu'), self.entete)
        self.feuyRS.write(0, 14, self.text.get('num_bands'), self.entete)
        self.feuyRS.write(0, 15, self.text.get('format'), self.entete)
        self.feuyRS.write(0, 16, self.text.get('compression'), self.entete)
        self.feuyRS.write(0, 17, self.text.get('coloref'), self.entete)
        self.feuyRS.write(0, 18, self.text.get('li_depends'), self.entete)
        self.feuyRS.write(0, 19, self.text.get('tot_size'), self.entete)
        self.feuyRS.write(0, 20, self.text.get('gdal_warn'), self.entete)
        self.logger.info('Sheet rasters created')
        # tunning headers
        lg_rast_names = [len(lg) for lg in self.li_raster]
        self.feuyRS.col(0).width = max(lg_rast_names) * 100
        self.feuyRS.col(1).width = len(self.text.get('browse')) * 256

        # end of function
        return

    def add_gdb_sheet(self):
        """
        sets sheet dedicated to file geodatabase information
        """
        # sheet
        self.feuyFGDB = self.book.add_sheet(self.text.get('sheet_filedb'),
                                         cell_overwrite_ok=True)
        # headers
        self.feuyFGDB.write(0, 0, self.text.get('nomfic'), self.entete)
        self.feuyFGDB.write(0, 1, self.text.get('path'), self.entete)
        self.feuyFGDB.write(0, 2, self.text.get('theme'), self.entete)
        self.feuyFGDB.write(0, 3, self.text.get('tot_size'), self.entete)
        self.feuyFGDB.write(0, 4, self.text.get('date_crea'), self.entete)
        self.feuyFGDB.write(0, 5, self.text.get('date_actu'), self.entete)
        self.feuyFGDB.write(0, 6, self.text.get('feats_class'), self.entete)
        self.feuyFGDB.write(0, 7, self.text.get('num_attrib'), self.entete)
        self.feuyFGDB.write(0, 8, self.text.get('num_objets'), self.entete)
        self.feuyFGDB.write(0, 9, self.text.get('geometrie'), self.entete)
        self.feuyFGDB.write(0, 10, self.text.get('srs'), self.entete)
        self.feuyFGDB.write(0, 11, self.text.get('srs_type'), self.entete)
        self.feuyFGDB.write(0, 12, self.text.get('codepsg'), self.entete)
        self.feuyFGDB.write(0, 13, self.text.get('emprise'), self.entete)
        self.feuyFGDB.write(0, 14, self.text.get('li_chps'), self.entete)
        self.logger.info('Sheet Esri FileGDB created')
        # tunning headers
        lg_gdb_names = [len(lg) for lg in self.li_gdb]
        self.feuyFGDB.col(0).width = max(lg_gdb_names) * 100
        self.feuyFGDB.col(1).width = len(self.text.get('browse')) * 256
        self.feuyFGDB.col(4).width = len(self.text.get('date_crea')) * 256
        self.feuyFGDB.col(5).width = len(self.text.get('date_actu')) * 256
        self.feuyFGDB.col(6).width = len(self.text.get('feats_class')) * 256
        self.feuyFGDB.col(13).width = 35 * 256
        # freezing headers line and first column
        self.feuyFGDB.set_panes_frozen(True)
        self.feuyFGDB.set_horz_split_pos(1)
        self.feuyFGDB.set_vert_split_pos(1)

        # end of function
        return

    def add_maps_sheet(self):
        """
        sets sheet dedicated to map documents information
        """

        # end of function
        return

    def add_cdao_sheet(self):
        """
        sets sheet dedicated to CAD information
        """
        # sheet
        self.feuyCDAO = self.book.add_sheet(self.text.get('sheet_cdao'), cell_overwrite_ok=True)
        # headers
        self.feuyCDAO.write(0, 0, self.text.get('nomfic'), self.entete)
        self.feuyCDAO.write(0, 1, self.text.get('path'), self.entete)
        self.feuyCDAO.write(0, 2, self.text.get('theme'), self.entete)
        self.feuyCDAO.write(0, 3, self.text.get('tot_size'), self.entete)
        self.feuyCDAO.write(0, 4, self.text.get('date_crea'), self.entete)
        self.feuyCDAO.write(0, 5, self.text.get('date_actu'), self.entete)
        self.feuyCDAO.write(0, 6, self.text.get('feats_class'), self.entete)
        self.feuyCDAO.write(0, 7, self.text.get('num_attrib'), self.entete)
        self.feuyCDAO.write(0, 8, self.text.get('num_objets'), self.entete)
        self.feuyCDAO.write(0, 9, self.text.get('geometrie'), self.entete)
        self.feuyCDAO.write(0, 10, self.text.get('srs'), self.entete)
        self.feuyCDAO.write(0, 11, self.text.get('srs_type'), self.entete)
        self.feuyCDAO.write(0, 12, self.text.get('codepsg'), self.entete)
        self.feuyCDAO.write(0, 13, self.text.get('emprise'), self.entete)
        self.feuyCDAO.write(0, 14, self.text.get('li_chps'), self.entete)
        self.logger.info('Sheet CAO - DAO created')
        # tunning headers
        lg_gdb_names = [len(lg) for lg in self.li_cdao]
        self.feuyCDAO.col(0).width = max(lg_gdb_names) * 100
        self.feuyCDAO.col(1).width = len(self.text.get('browse')) * 256
        self.feuyCDAO.col(4).width = len(self.text.get('date_crea')) * 256
        self.feuyCDAO.col(5).width = len(self.text.get('date_actu')) * 256
        self.feuyCDAO.col(6).width = len(self.text.get('feats_class')) * 256
        self.feuyCDAO.col(13).width = 35 * 256
        # freezing headers line and first column
        self.feuyCDAO.set_panes_frozen(True)
        self.feuyCDAO.set_horz_split_pos(1)
        self.feuyCDAO.set_vert_split_pos(1)
        # end of function
        return

    def add_postgis_sheet(self):
        """
        sets sheet dedicated to PostGIS tables & views information
        """
        # sheet
        self.feuyPG = self.book.add_sheet(u'PostGIS',
                                         cell_overwrite_ok=True)
        # headers
        self.feuyPG.write(0, 0, self.text.get('nomfic'), self.entete)
        self.feuyPG.write(0, 1, self.text.get('conn_chain'), self.entete)
        self.feuyPG.write(0, 2, self.text.get('schema'), self.entete)
        self.feuyPG.write(0, 3, self.text.get('num_attrib'), self.entete)
        self.feuyPG.write(0, 4, self.text.get('num_objets'), self.entete)
        self.feuyPG.write(0, 5, self.text.get('geometrie'), self.entete)
        self.feuyPG.write(0, 6, self.text.get('srs'), self.entete)
        self.feuyPG.write(0, 7, self.text.get('srs_type'), self.entete)
        self.feuyPG.write(0, 8, self.text.get('codepsg'), self.entete)
        self.feuyPG.write(0, 9, self.text.get('emprise'), self.entete)
        self.feuyPG.write(0, 10, self.text.get('date_crea'), self.entete)
        self.feuyPG.write(0, 11, self.text.get('date_actu'), self.entete)
        self.feuyPG.write(0, 12, self.text.get('format'), self.entete)
        self.feuyPG.write(0, 13, self.text.get('li_chps'), self.entete)
        self.logger.info('Sheet PostGIS created')
        # tunning headers
        self.feuyPG.col(1).width = len(self.text.get('browse')) * 256
        # freezing headers line and first column
        self.feuyPG.set_panes_frozen(True)
        self.feuyPG.set_horz_split_pos(1)
        self.feuyPG.set_vert_split_pos(1)

        # end of function
        return

    def add_isogeo_sheet(self, xls_wb):
        """
        sets sheet dedicated to Isogeo OpenCatalog metadata
        """
        # sheet
        self.feuyIsogeo = xls_wb.add_sheet(u'Isogeo',
                                           cell_overwrite_ok=True)
        # headers
        self.feuyIsogeo.write(0, 0, "Titre", self.entete)
        self.feuyIsogeo.write(0, 1, "Nom de la ressource", self.entete)
        self.feuyIsogeo.write(0, 2, "Emplacement", self.entete)
        self.feuyIsogeo.write(0, 3, "Mots-clés", self.entete)
        self.feuyIsogeo.write(0, 4, "Résumé", self.entete)
        self.feuyIsogeo.write(0, 5, "Thématiques INPIRES", self.entete)
        self.feuyIsogeo.write(0, 6, "Type", self.entete)
        self.feuyIsogeo.write(0, 7, "Format", self.entete)
        self.feuyIsogeo.write(0, 8, "SRS", self.entete)
        self.feuyIsogeo.write(0, 9, "Nombre d'objets", self.entete)
        self.feuyIsogeo.write(0, 10, "Visualiser sur l'OpenCatalog", self.entete)
        self.feuyIsogeo.write(0, 11, "Editer sur Isogeo", self.entete)

        # tunning headers
        self.feuyIsogeo.col(1).width = len(self.text.get('browse')) * 256
        # freezing headers line and first column
        self.feuyIsogeo.set_panes_frozen(True)
        self.feuyIsogeo.set_horz_split_pos(1)
        self.feuyIsogeo.set_vert_split_pos(1)

        # end of function
        return self.feuyIsogeo

###############################################################################
###### Stand alone program ########
###################################

if __name__ == '__main__':
    """ standalone execution """
    print("not ready to be launched standalone")
