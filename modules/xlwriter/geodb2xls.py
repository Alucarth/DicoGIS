# -*- coding: UTF-8 -*-
#!/usr/bin/env python
from __future__ import unicode_literals
#------------------------------------------------------------------------------
# Name:         GeoDataBase to Excel
# Purpose:      Automatize the creation of a dictionnary of geographic data
#                   contained in a folders structures.
#                   It produces an Excel output file (.xls)
#
# Author:       Julien Moura (https://twitter.com/geojulien)
#
# Python:       2.7.x
# Created:      14/02/2013
# Updated:      11/11/2014
#
# Licence:      GPL 3
#------------------------------------------------------------------------------


###############################################################################
########### Libraries #############
###################################

# Python 3 backported
from collections import OrderedDict as OD   # ordered dictionary

# 3rd party libraries
from xlwt import Workbook, easyxf, Formula  # excel writer

# Custom modules
# from ..modules import TextsManager

###############################################################################
############# Classes #############
###################################


class XLWriter_GeoDB(Workbook):
    def __init__(self):
        u"""
        Main window constructor
        Creates 1 frame and 2 labelled subframes
        """
        print help(self)

    def dictionarize_gdb(self, gdb_infos, sheet, line):
        u""" write the infos of the FileGDB into the Excel workbook """
        # local variables
        champs = ""

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


###############################################################################
###### Stand alone program ########
###################################

if __name__ == '__main__':
    """ standalone execution """
    XLWriter_GeoDB()
