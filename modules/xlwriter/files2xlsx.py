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
import logging
from os import path

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
        """ TO DOC

        Keyword arguments:

        """
        super(files2xlsx, self).__init__()
        # super(Isogeo2xlsx, self).__init__(write_only=True)
        self.texts = texts

        # deleting the default worksheet
        ws = self.active
        self.remove_sheet(ws)

    # ------------ Setting workbook ---------------------

    def set_worksheets(self, has_vector=0, has_raster=0, has_filegdb=0,
                       has_mapdocs=0, has_cad=0, has_sgbd=0):
        """ adds news sheets depending on present metadata types
        """
        # SHEETS & HEADERS
        if has_vector:
            self.ws_v = self.create_sheet(title=self.texts.get("sheet_vectors"))
            # headers
            self.ws_v.append([self.texts.get(i) for i in self.li_cols_vector])
            # initialize line counter
            self.idx_v = 1
        else:
            pass

        if has_raster:
            self.ws_r = self.create_sheet(title=self.texts.get("sheet_rasters"))
            # headers
            self.ws_r.append([self.texts.get(i) for i in self.li_cols_raster])
            # initialize line counter
            self.idx_r = 1
        else:
            pass

        if has_filegdb:
            self.ws_fgdb = self.create_sheet(title=self.texts.get("sheet_filedb"))
            # headers
            self.ws_fgdb.append([self.texts.get(i) for i in self.li_cols_filegdb])
            # initialize line counter
            self.idx_f = 1
        else:
            pass

        if has_mapdocs:
            self.ws_mdocs = self.create_sheet(title=self.texts.get("sheet_maplans"))
            # headers
            self.ws_mdocs.append([self.texts.get(i) for i in self.li_cols_mapdocs])
            # initialize line counter
            self.idx_m = 1
        else:
            pass

        if has_cad:
            self.ws_cad = self.create_sheet(title=self.texts.get("sheet_cdao"))
            # headers
            self.ws_cad.append([self.texts.get(i) for i in self.li_cols_caodao])
            # initialize line counter
            self.idx_c = 1
        else:
            pass

        if has_sgbd:
            self.ws_sgbd = self.create_sheet(title="PostGIS")
            # headers
            self.ws_sgbd.append([self.texts.get(i) for i in self.li_cols_sgbd])
            # initialize line counter
            self.idx_s = 1
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
            self.idx_v += 1
            self.store_md_vector(metadata)
            return
        elif metadata.get("type") == "rasterDataset":
            self.idx_r += 1
            self.store_md_raster(metadata)
            return
        elif metadata.get("type") == "service":
            self.idx_f += 1
            self.store_md_service(metadata)
            return
        elif metadata.get("type") == "resource":
            self.idx_m += 1
            self.store_md_resource(metadata)
            return
        else:
            print("Type of metadata is not recognized/handled: " + metadata.get("type"))
            pass
        # end of method
        return

    def store_md_vector(self, layer, fields, li_formats):
        """ TO DOCUMENT
        """
        # increment line
        self.idx_v += 1

        # local variables
        champs = ""

        # in case of a source error
        if layer.get('error'):
            # sheet.row(line).set_style(self.xls_erreur)
            err_mess = self.texts.get(layer.get('error'))
            logging.warning('\tproblem detected')
            self.ws_v["A{}".format(self.idx_v)] = layer.get('name')
            link = r'=HYPERLINK("{0}","{1}")'.format(layer.get(u'folder'),
                                                     self.texts.get('browse'))
            self.ws_v["B{}".format(self.idx_v)] = link
            self.ws_v["C{}".format(self.idx_v)] = err_mess
            # Interruption of function
            return False
        else:
            pass

        # Name
        self.ws_v["A{}".format(self.idx_v)] = layer.get('name')

        # Path of parent folder formatted to be a hyperlink
        link = r'=HYPERLINK("{0}","{1}")'.format(layer.get(u'folder'),
                                                 self.texts.get('browse'))
        self.ws_v["B{}".format(self.idx_v)] = link

        # Name of parent folder with an exception if this is the format name
        if not path.basename(layer.get(u'folder')).lower() in li_formats:
            self.ws_v["C{}".format(self.idx_v)] = path.basename(layer.get(u'folder'))
        else:
            self.ws_v["C{}".format(self.idx_v)] = path.basename(path.dirname(layer.get(u'folder')))

        # Fields count
        self.ws_v["D{}".format(self.idx_v)] = layer.get(u'num_fields')
        # Objects count
        self.ws_v["E{}".format(self.idx_v)] = layer.get(u'num_obj')
        # Geometry type
        self.ws_v["F{}".format(self.idx_v)] = layer.get(u'type_geom')
        # Name of srs
        self.ws_v["G{}".format(self.idx_v)] = layer.get(u'srs')
        # Type of SRS
        self.ws_v["H{}".format(self.idx_v)] = layer.get(u'srs_type')
        # EPSG code
        self.ws_v["I{}".format(self.idx_v)] = layer.get(u'EPSG')
        # Spatial extent
        emprise = u"Xmin : {0} - Xmax : {1} | \nYmin : {2} - Ymax : {3}"\
                  .format(unicode(layer.get(u'Xmin')),
                          unicode(layer.get(u'Xmax')),
                          unicode(layer.get(u'Ymin')),
                          unicode(layer.get(u'Ymax')))
        self.ws_v["J{}".format(self.idx_v)].style.alignment.wrap_text = True
        self.ws_v["J{}".format(self.idx_v)] = emprise
        # self.ws_v.cell("E{}".format(self.idx_v)).style.alignment.wrap_text = True

        # Creation date
        self.ws_v["K{}".format(self.idx_v)] = layer.get(u'date_crea')
        # Last update date
        self.ws_v["L{}".format(self.idx_v)] = layer.get(u'date_actu')
        # Format of data
        self.ws_v["M{}".format(self.idx_v)] = layer.get(u'type')
        # dependencies
        self.ws_v["N{}".format(self.idx_v)].style.alignment.wrap_text = True
        self.ws_v.cell("N{}".format(self.idx_v)).value = u' |\n '.join(layer.get(u'dependencies'))
        # total size
        self.ws_v["O{}".format(self.idx_v)] = layer.get(u'total_size')

        # Field informations
        for chp in fields.keys():
            # field type
            if 'Integer' in fields[chp][0]:
                tipo = self.texts.get(u'entier')
            elif fields[chp][0] == 'Real':
                tipo = self.texts.get(u'reel')
            elif fields[chp][0] == 'String':
                tipo = self.texts.get(u'string')
            elif fields[chp][0] == 'Date':
                tipo = self.texts.get(u'date')
            else:
                tipo = "unknown"
                print(chp, " unknown type")

            # concatenation of field informations
            try:
                champs = champs + chp +\
                          u" (" + tipo + self.texts.get(u'longueur') +\
                          unicode(fields[chp][1]) +\
                          self.texts.get(u'precision') +\
                          unicode(fields[chp][2]) + u") ; "
            except UnicodeDecodeError:
                # write a notification into the log file
                # self.dico_err[fields.get('name')] = self.texts.get(u'err_encod')\
                #                                     + chp.decode('latin1') \
                #                                     + u"\n\n"
                logging.warning('Field name with special letters: {}'.format(chp.decode('latin1')))
                # decode the fucking field name
                champs = champs + chp.decode('latin1') \
                + u" ({}, Lg. = {}, Pr. = {}) ;".format(tipo,
                                                        fields[chp][1],
                                                        fields[chp][2])
                # then continue
                continue

        # Once all fieds explored, write them
        self.ws_v["P{}".format(self.idx_v)] = champs

        # in case of a source error
        if layer.get('err_gdal')[0] != 0:
            logging.warning('\tproblem detected')
            self.ws_v["Q{}".format(self.idx_v)] = "{0} : {1}".format(layer.get('err_gdal')[0],
                                                                     layer.get('err_gdal')[1])
        else:
            pass

        # end of method
        return


    def store_md_raster(self, md_raster):
        """ TO DOCUMENT
        """
        self.ws_r["A{}".format(self.idx_raster)] = md_raster.get('title')
        self.ws_r["B{}".format(self.idx_raster)] = md_raster.get('abstract')


        # end of method
        return


    def store_md_service(self, md_service):
        """ TO DOCUMENT
        """
        self.ws_fgdb["A{}".format(self.idx_service)] = md_service.get('title')
        self.ws_fgdb["B{}".format(self.idx_service)] = md_service.get('abstract')


        # end of method
        return


    def store_md_resource(self, md_resource):
        """ TO DOCUMENT
        """
        self.ws_mdocs["A{}".format(self.idx_resource)] = md_resource.get('title')
        self.ws_mdocs["B{}".format(self.idx_resource)] = md_resource.get('abstract')



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
