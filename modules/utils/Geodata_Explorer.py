# -*- coding: UTF-8 -*-
#!/usr/bin/env python
from __future__ import unicode_literals
from __future__ import print_function
#------------------------------------------------------------------------------
# Name:         Geodata Explorer
# Purpose:      Explore directory structure and list files and folders
#               with geospatial data
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
from os import listdir, walk, path  # files and folder managing


###############################################################################
############# Classes #############
###################################


class GeodataExplorer:
    def __init__(self, parent_folder, opt_vec=1, opt_rast=1,
                 opt_gdb=1, opt_cdao=1, opt_maps=1):
        u"""
        Explore a directory and its subdirectories to list geodata

        parent_folder = directory to look into
        opt_vec = option to look for vectors
        opt_rast = option to look for rasters
        opt_gdb = option to look for file geodatabases
        opt_cdao = option to look for CAD files
        opt_maps = option to look for maps documents
        """


    def ligeofiles(self, foldertarget):
        u""" List compatible geo-files stored into
        the folders structure """
        # reseting global variables
        self.li_shp = []
        self.li_tab = []
        self.li_kml = []
        self.li_gml = []
        self.li_geoj = []
        self.li_vectors = []
        self.li_dxf = []
        self.li_dwg = []
        self.li_dgn = []
        self.li_cdao = []
        self.li_raster = []
        self.li_gdb = []
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
                except UnicodeDecodeError as e:
                    full_path = path.join(root, d.decode('latin1'))
                if full_path[-4:].lower() == '.gdb':
                    # add complete path of Esri FileGeoDatabase
                    self.li_gdb.append(path.abspath(full_path))
                else:
                    pass
            for f in files:
                """ looking for files with geographic data """
                try:
                    unicode(path.join(root, f))
                    full_path = path.join(root, f)
                except UnicodeDecodeError as e:
                    full_path = path.join(root, f.decode('latin1'))
                    print(unicode(full_path), e)
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
                elif path.splitext(full_path.lower())[1] == '.kml':
                    """ listing KML """
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
                else:
                    continue

        # grouping CAO/DAO files
        self.li_cdao.extend(self.li_dxf)
        self.li_cdao.extend(self.li_dwg)
        self.li_cdao.extend(self.li_dgn)
        # end of listing
        self.prog_layers.stop()
        self.logger.info('End of folders parsing: {0} shapefiles - \
          {1} tables (MapInfo) - \
          {2} KML - \
          {3} GML - \
          {4} GeoJSON\
          {5} rasters - \
          {6} FileGDB - \
          {7} CAO/DAO - \
          {8} PDF - \
          in {9}{10}'.format(len(self.li_shp),
                            len(self.li_tab),
                            len(self.li_kml),
                            len(self.li_gml),
                            len(self.li_geoj),
                            len(self.li_raster),
                            len(self.li_gdb),
                            len(self.li_cdao),
                            len(self.li_pdf),
                            self.num_folders,
                            self.blabla.get('log_numfold')))
        # grouping vectors lists
        self.li_vectors.extend(self.li_shp)
        self.li_vectors.extend(self.li_tab)
        self.li_vectors.extend(self.li_kml)
        self.li_vectors.extend(self.li_gml)
        self.li_vectors.extend(self.li_geoj)

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
        self.li_gdb.sort()
        self.li_gdb = tuple(self.li_gdb)
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
{4} GeoJSON\
\n{5} rasters - \
{6} Esri FileGDB - \
{7} CAO/DAO - \
{8} PDF - \
in {9}{10}'.format(len(self.li_shp),
                  len(self.li_tab),
                  len(self.li_kml),
                  len(self.li_gml),
                  len(self.li_geoj),
                  len(self.li_raster),
                  len(self.li_gdb),
                  len(self.li_cdao),
                  len(self.li_pdf),
                  self.num_folders,
                  self.blabla.get('log_numfold')))

        # reactivating the buttons
        self.browsetarg.config(state=ACTIVE)
        self.val.config(state=ACTIVE)
        # End of function
        return foldertarget, self.li_shp, self.li_tab, self.li_kml,\
            self.li_gml, self.li_geoj, self.li_raster, self.li_gdb,\
            self.li_dxf, self.li_dwg, self.li_dgn, self.li_cdao

    def finder_vectors(self):
        """

        """

        # end of function
        return

    def finder_rasters(self):
        """

        """

        # end of function
        return

    def finder_filegdb(self):
        """

        """

        # end of function
        return

    def finder_mapsdoc(self):
        """

        """

        # end of function
        return

    def finder_cdao(self):
        """

        """

        # end of function
        return

###############################################################################
###### Stand alone program ########
###################################

if __name__ == '__main__':
    """ standalone execution """
    app = DicoGIS()
    app.mainloop()
