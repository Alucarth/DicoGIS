# -*- coding: UTF-8 -*-
#!/usr/bin/env python
from __future__ import (absolute_import, print_function, unicode_literals)
# ------------------------------------------------------------------------------
# Name:         Isogeo to Microsoft Excel 2010
# Purpose:      Get metadatas from an Isogeo share and store it into
#               a Excel worksheet. It's one of the submodules of
#               isogeo2office (https://bitbucket.org/isogeo/isogeo-2-office).
#
# Author:       Julien Moura (@geojulien)
#
# Python:       2.7.x
# Created:      14/08/2014
# Updated:      30/01/2016
# ------------------------------------------------------------------------------

# ##############################################################################
# ########## Libraries #############
# ##################################

# Standard library

# Python 3 backported
from collections import OrderedDict     # ordered dictionary

# 3rd party library
from openpyxl import Workbook
from openpyxl.worksheet.properties import WorksheetProperties

# ##############################################################################
# ########## Classes ###############
# ##################################


class files2xlsx(Workbook):
    """ files2xlsx
    """
    li_cols_vector = [
                      "nomfic",
                      "path",
                      "theme",
                      "num_attrib",
                      "num_objets",
                      "geometrie",
                      "srs",
                      "srs_type",
                      "codepsg",
                      "emprise",
                      "date_crea",
                      "date_actu",
                      "format",
                      "li_depends",
                      "tot_size",
                      "li_chps",
                      "gdal_warn"
                       ]
    li_cols_raster = [
                     "nomfic",
                     "path",
                     "theme",
                     "size_Y",
                     "size_X",
                     "pixel_w",
                     "pixel_h",
                     "origin_x",
                     "origin_y",
                     "srs_type",
                     "codepsg",
                     "emprise",
                     "date_crea",
                     "date_actu",
                     "num_bands",
                     "format",
                     "compression",
                     "coloref",
                     "li_depends",
                     "tot_size",
                     "gdal_warn",
                     ]

    li_cols_filegdb = [
                      "nomfic",
                      "path",
                      "theme",
                      "tot_size",
                      "date_crea",
                      "date_actu",
                      "feats_class",
                      "num_attrib",
                      "num_objets",
                      "geometrie",
                      "srs",
                      "srs_type",
                      "codepsg",
                      "emprise",
                      "li_chps",
                      ]

    li_cols_mapdocs = [
                      "nomfic",
                      "path",
                      "theme",
                      "custom_title",
                      "creator_prod",
                      "keywords",
                      "subject",
                      "res_image",
                      "tot_size",
                      "date_crea",
                      "date_actu",
                      "origin_x",
                      "origin_y",
                      "srs",
                      "srs_type",
                      "codepsg",
                      "sub_layers",
                      "num_attrib",
                      "num_objets",
                      "li_chps",
                      ]

    li_cols_caodao = [
                      "nomfic",
                      "path",
                      "theme",
                      "tot_size",
                      "date_crea",
                      "date_actu",
                      "sub_layers",
                      "num_attrib",
                      "num_objets",
                      "geometrie",
                      "srs",
                      "srs_type",
                      "codepsg",
                      "emprise",
                      "li_chps",
                      ]

    li_cols_sgbd = [
                      "nomfic",
                      "conn_chain",
                      "schema",
                      "num_attrib",
                      "num_objets",
                      "geometrie",
                      "srs",
                      "srs_type",
                      "codepsg",
                      "emprise",
                      "date_crea",
                      "date_actu",
                      "format",
                      "li_chps",
                      ]

    def __init__(self, lang="EN", texts=OrderedDict()):
        """ 

        Keyword arguments:

        """
        super(files2xlsx, self).__init__()
        # super(Isogeo2xlsx, self).__init__(write_only=True)
        self.texts = texts

        # deleting the default worksheet
        ws = self.active
        self.remove_sheet(ws)


    # ------------ Setting workbook ---------------------

    def set_worksheets(self, has_vector=0, has_raster=0, has_filegdb=0, has_mapdocs=0, has_cad=0, has_sgbd=0):
        """ adds news sheets depending on present metadata types
        """
        # SHEETS & HEADERS
        if has_vector:
            self.ws_vectors = self.create_sheet(title=self.texts.get("sheet_vectors"))
            # headers
            self.ws_vectors.append([self.texts.get(i) for i in self.li_cols_vector])
            # initialize line counter
            self.idx_vector = 1
        else:
            pass

        if has_raster:
            self.ws_rasters = self.create_sheet(title=self.texts.get("sheet_rasters"))
            # headers
            self.ws_rasters.append([self.texts.get(i) for i in self.li_cols_raster])
            # initialize line counter
            self.idx_raster = 1
        else:
            pass

        if has_filegdb:
            self.ws_services = self.create_sheet(title=self.texts.get("sheet_filedb"))
            # headers
            self.ws_services.append([self.texts.get(i) for i in self.li_cols_filegdb])
            # initialize line counter
            self.idx_service = 1
        else:
            pass

        if has_mapdocs:
            self.ws_resources = self.create_sheet(title=self.texts.get("sheet_maplans"))
            # headers
            self.ws_resources.append([self.texts.get(i) for i in self.li_cols_mapdocs])
            # initialize line counter
            self.idx_resource = 1
        else:
            pass

        if has_cad:
            self.ws_resources = self.create_sheet(title=self.texts.get("sheet_cdao"))
            # headers
            self.ws_resources.append([self.texts.get(i) for i in self.li_cols_caodao])
            # initialize line counter
            self.idx_resource = 1
        else:
            pass

        if has_sgbd:
            self.ws_resources = self.create_sheet(title="PostGIS")
            # headers
            self.ws_resources.append([self.texts.get(i) for i in self.li_cols_sgbd])
            # initialize line counter
            self.idx_resource = 1
        else:
            pass

        # CLEAN UP & TUNNING
        for sheet in self.worksheets:
            # Freezing panes
            c = sheet['B2']
            sheet.freeze_panes = c

            # Print properties
            sheet.print_options.horizontalCentered = True
            sheet.print_options.verticalCentered = True
            sheet.page_setup.fitToWidth = 1
            sheet.page_setup.orientation = sheet.ORIENTATION_LANDSCAPE

            # Others properties
            wsprops = sheet.sheet_properties
            wsprops.filterMode = True

        # end of method
        return

    # ------------ Writing metadata ---------------------

    def store_metadatas(self, kind, metadata):
        """ TO DOCUMENT
        """
        if kind == "vectorDataset":
            self.idx_vector += 1
            self.store_md_vector(metadata)
            return
        elif metadata.get("type") == "rasterDataset":
            self.idx_raster += 1
            self.store_md_raster(metadata)
            return
        elif metadata.get("type") == "service":
            self.idx_service += 1
            self.store_md_service(metadata)
            return
        elif metadata.get("type") == "resource":
            self.idx_resource += 1
            self.store_md_resource(metadata)
            return     
        else:
            print("Type of metadata is not recognized/handled: " + metadata.get("type"))
            pass
        # end of method
        return

    def store_md_vector(self, layer_infos, fields_info):
        """ TO DOCUMENT
        """
        # increment line
        self.idx_vector += 1
        # writing
        self.ws_vectors["A{}".format(self.idx_vector)] = layer_infos.get('name')
        link = r'=HYPERLINK("http://www.example.com","XXX")'
        self.ws_vectors["B{}".format(self.idx_vector)] = link


        # end of method
        return


    def store_md_raster(self, md_raster):
        """ TO DOCUMENT
        """
        self.ws_rasters["A{}".format(self.idx_raster)] = md_raster.get('title')
        self.ws_rasters["B{}".format(self.idx_raster)] = md_raster.get('abstract')


        # end of method
        return


    def store_md_service(self, md_service):
        """ TO DOCUMENT
        """
        self.ws_services["A{}".format(self.idx_service)] = md_service.get('title')
        self.ws_services["B{}".format(self.idx_service)] = md_service.get('abstract')


        # end of method
        return


    def store_md_resource(self, md_resource):
        """ TO DOCUMENT
        """
        self.ws_resources["A{}".format(self.idx_resource)] = md_resource.get('title')
        self.ws_resources["B{}".format(self.idx_resource)] = md_resource.get('abstract')



        # end of method
        return

###############################################################################
###### Stand alone program ########
###################################

if __name__ == '__main__':
    """ Standalone execution and tests
    """
    # ------------ Specific imports ---------------------
    from os import path

    # ------------ REAL START ----------------------------
    wb = files2xlsx()
    # wb.set_worksheets(has_vector=1,
    #                   has_raster=1,
    #                   has_service=1,
    #                   has_resource=1)

    # # saving the test file
    # wb.save(r"files2xlsx.xlsx")
