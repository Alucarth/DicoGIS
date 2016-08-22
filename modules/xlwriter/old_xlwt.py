    def configexcel(self):
        u""" create and configure the Excel workbook """
        # Basic configuration
        self.book = Workbook(encoding='utf8')
        self.book.set_owner(str('DicoGIS_') + str(self.DGversion))
        logging.info('Workbook created')
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
        if self.typo == 0:
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
            logging.info('Sheet for global statistics adedd')
            # tunning headers
            # lg_shp_names = [len(lg) for lg in self.li_shp]
            # lg_tab_names = [len(lg) for lg in self.li_tab]
            # self.feuySTATS.col(0).width = max(lg_shp_names + lg_tab_names) * 100
            # self.feuySTATS.col(1).width = len(self.blabla.get('browse')) * 256
            # self.feuySTATS.col(9).width = 35 * 256
        else:
            pass

        if self.typo == 0 \
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
            logging.info('Sheet vectors adedd')
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

        if self.typo == 0\
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
            logging.info('Sheet rasters created')
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

        if self.typo == 0\
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
            logging.info('Sheet FileGDB created')
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

        if self.typo == 0\
            and (self.opt_pdf.get() + self.opt_lyr.get() + self.opt_qgs.get()
                 + self.opt_mxd.get()) > 0\
            and len(self.li_mapdocs) > 0:
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
            logging.info('Sheet Maps & Documents created')
            # tunning headers
            lg_maps_names = [len(lg) for lg in self.li_mapdocs]
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

        if self.typo == 0\
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
            logging.info('Sheet CAO - DAO created')
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

        if self.typo == 1:
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
            logging.info('Sheet PostGIS created')
            # tunning headers
            self.feuyPG.col(1).width = len(self.blabla.get('browse')) * 256
            # freezing headers line and first column
            self.feuyPG.set_panes_frozen(True)
            self.feuyPG.set_horz_split_pos(1)
            self.feuyPG.set_vert_split_pos(1)
        else:
            pass

        if self.typo == 3:
            ConfigExcel(workbook=self.book, opt_isogeo=1, text=self.blabla)
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
            logging.warning('\tproblem detected')
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
            logging.warning('Path name with special letters: {}'.format(layer_infos.get(u'folder').decode('utf8')))
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
        self.global_total_fields += layer_infos.get(u'num_fields')
        # Name of objects
        sheet.write(line, 4, layer_infos.get(u'num_obj'))
        self.global_total_features += layer_infos.get(u'num_obj')
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
            if 'Integer' in fields_info[chp][0]:
                tipo = self.blabla.get(u'entier')
            elif fields_info[chp][0] == 'Real':
                tipo = self.blabla.get(u'reel')
            elif fields_info[chp][0] == 'String':
                tipo = self.blabla.get(u'string')
            elif fields_info[chp][0] == 'Date':
                tipo = self.blabla.get(u'date')
            else:
                tipo = "unknown"
                print(chp, " unknown type")

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
                logging.warning('Field name with special letters: {}'.format(chp.decode('latin1')))
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
            logging.warning('\tproblem detected')
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
            logging.warning('\tproblem detected')
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
            logging.warning('Path name with special letters: {}'.format(dico_raster.get(u'folder').decode('utf8')))
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
            logging.warning('\tproblem detected')
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
            logging.warning('\tproblem detected')
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
            logging.warning('Path name with special letters: {}'.format(gdb_infos.get(u'folder').decode('utf8')))
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
            logging.warning('\tproblem detected')
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
                logging.warning('\tproblem detected: \
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
                if 'Integer' in fields_info[chp][0]:
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
                    logging.warning('Field name with special letters: {}'.format(chp.decode('latin1')))
                    # decode the fucking field name
                    champs = champs + chp.decode('latin1') \
                                    + u" ({0}) ;".format(tipo)
                    # then continue
                    continue

            # Once all fieds explored, write them
            sheet.write(line, 14, champs)

            # write layer's name into the log
            logging.info('\t -- {0} = OK'.format(gdb_layer.get(u'title')))

        # End of function
        return self.feuyFGDB, line

    def dictionarize_cdao(self, dico_cdao, sheet, line):
        u""" write the infos of the CAO/DAO files into the Excel workbook """
        # local variables
        champs = ""

        # in case of a source error
        if dico_cdao.get('error'):
            logging.warning('\tproblem detected')
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
            logging.warning('Path name with special letters: {}'.format(dico_cdao.get(u'folder').decode('utf8')))
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
                if 'Integer' in fields_info[chp]:
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
                    logging.warning('Field name with special letters: {}'.format(chp.decode('latin1')))
                    # decode the fucking field name
                    champs = champs + chp.decode('latin1') + u" ({}) ;".format(tipo)
                    # then continue
                    continue

            # Once all fieds explored, write them
            sheet.write(line, 14, champs)

            # write layer's name into the log
            logging.info('\t -- {0} = OK'.format(cdao_layer.get(u'title')))

        # End of function
        return self.feuyCDAO, line

    def dictionarize_mapdocs(self, mapdoc_infos, sheet, line):
        u""" write the infos of the map document into the Excel workbook """
        # in case of a source error
        if mapdoc_infos.get('error'):
            logging.warning('\tproblem detected')
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
            logging.warning('Path name with special letters: {}'.format(mapdoc_infos.get(u'folder').decode('utf8')))
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
        if mapdoc_infos.get(u'layers_count') == 1:
            return
        else:
            pass

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
                    logging.warning('Field name with special letters: {}'.format(chp.decode('latin1')))
                    # decode the fucking field name
                    champs = champs + chp.decode('latin1') \
                                    + u" ({0}) ;".format(tipo)
                    # then continue
                    continue

            # Once all fieds explored, write them
            sheet.write(line, 19, champs)

            # write layer's name into the log
            logging.info('\t -- {0} = OK'.format(mapdoc_layer.get(u'title')))

        # End of function
        return self.feuyMAPS, line

    def dictionarize_lyr(self, mapdoc_infos, sheet, line):
        u""" write the infos of the map document into the Excel workbook """
        # in case of a source error
        if mapdoc_infos.get('error'):
            logging.warning('\tproblem detected')
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
            logging.warning('Path name with special letters: {}'.format(mapdoc_infos.get(u'folder').decode('utf8')))
            # decode the fucking path name
            link = 'HYPERLINK("{0}"; "{1}")'.format(mapdoc_infos.get(u'folder').decode('utf8'),
                                                    self.blabla.get('browse'))

        sheet.write(line, 1, Formula(link), self.url)

        # Name of parent folder
        sheet.write(line, 2, path.basename(mapdoc_infos.get(u'folder')))

        # Document title
        sheet.write(line, 3, mapdoc_infos.get(u'title'))

        # Type of lyr
        sheet.write(line, 4, mapdoc_infos.get(u'type'))

        # Type of lyr
        sheet.write(line, 5, mapdoc_infos.get(u'license'))

        # subject
        sheet.write(line, 6, mapdoc_infos.get(u'description'))

        # total size
        sheet.write(line, 8, mapdoc_infos.get(u'total_size'))

        # Creation date
        sheet.write(line, 9, mapdoc_infos.get(u'date_crea'), self.xls_date)
        # Last update date
        sheet.write(line, 10, mapdoc_infos.get(u'date_actu'), self.xls_date)


        if mapdoc_infos.get(u'type') in ['Feature', 'Raster']:
            # Spatial extent
            emprise = u"Xmin : {0} - Xmax : {1} \
                       \nYmin : {2} - Ymax : {3}".format(unicode(mapdoc_infos.get(u'Xmin')),
                                                         unicode(mapdoc_infos.get(u'Xmax')),
                                                         unicode(mapdoc_infos.get(u'Ymin')),
                                                         unicode(mapdoc_infos.get(u'Ymax'))
                                                         )
            sheet.write(line, 11, emprise, self.xls_wrap)

            # SRS name
            sheet.write(line, 13, mapdoc_infos.get(u'srs'))
            # Type of SRS
            sheet.write(line, 14, mapdoc_infos.get(u'srs_type'))
            # EPSG code
            sheet.write(line, 15, mapdoc_infos.get(u'EPSG')[0])
        else:
            pass

        if mapdoc_infos.get(u'type') == u'Group':
            # Layers count
            sheet.write(line, 16, mapdoc_infos.get(u'layers_count'))
             # layer's name
            sheet.write(line+1, 16, ' ; '.join(mapdoc_infos.get(u'layers_names')))
        else:
            pass

        if mapdoc_infos.get(u'type') == u'Feature':
            # number of fields
            sheet.write(line, 17, mapdoc_infos.get(u'num_fields'))

            # number of objects
            sheet.write(line, 18, mapdoc_infos.get(u'num_obj'))

            # definition query
            sheet.write(line, 7, mapdoc_infos.get(u'defquery'))

            # fields domain
            fields_info = mapdoc_infos.get(u'fields')
            champs = ""
            for chp in fields_info.keys():
                tipo = fields_info.get(chp)[0]
                # concatenation of field informations
                try:
                    champs = champs + chp +\
                              u" (" + tipo + self.blabla.get(u'longueur') +\
                              unicode(fields_info.get(chp)[1]) +\
                              self.blabla.get(u'precision') +\
                              unicode(fields_info.get(chp)[2]) + u") ; "
                except UnicodeDecodeError:
                    # write a notification into the log file
                    self.dico_err[layer_infos.get('name')] = self.blabla.get(u'err_encod')\
                                                        + chp.decode('latin1') \
                                                        + u"\n\n"
                    logging.warning('Field name with special letters: {}'.format(chp.decode('latin1')))
                    # decode the fucking field name
                    champs = champs + chp.decode('latin1') \
                    + u" ({}, Lg. = {}, Pr. = {}) ;".format(tipo,
                                                            fields_info.get(chp)[1],
                                                            fields_info.get(chp)[2])
                    # then continue
                    continue

            # Once all fieds explored, write them
            sheet.write(line, 19, champs)

            # write layer's name into the log
            # logging.info('\t -- {0} = OK'.format(mapdoc_layer.get(u'title')))

        else:
            pass

        # End of function
        return self.feuyMAPS, line

    def dictionarize_pg(self, layer_infos, fields_info, sheet, line):
        u""" write the infos of the layer into the Excel workbook """
        # local variables
        champs = ""
        # in case of a source error
        if layer_infos.get('error'):
            logging.warning('\tproblem detected')
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
            if 'Integer' in fields_info[chp][0]:
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
                logging.warning('Field name with special letters: {}'.format(chp.decode('latin1')))
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
        self.feuySTATS.write(1, 1, self.global_total_layers)  # total of layers
        self.feuySTATS.write(2, 1, self.global_total_fields)  # total of fields
        self.feuySTATS.write(3, 1, self.global_total_features)
        self.feuySTATS.write(4, 1, self.global_total_errors)
        self.feuySTATS.write(6, 1, self.global_total_warnings)

        # end of function
        return

