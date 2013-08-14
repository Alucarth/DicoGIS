# -*- coding: UTF-8 -*-
#!/usr/bin/env python
#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      Julien Moura, Pierre Vernier
# Python :     2.7.4 +
# Encoding:    utf-8
# Created:     09/04/2013
# Copyright:   (c) Julien 2013
# Licence:     <your licence>
#-------------------------------------------------------------------------------

###################################
##### Libraries importation #######
###################################

# standard library
from Tkinter import *    # GUI modules
from tkFileDialog import askopenfilename
from tkMessageBox import showerror, showinfo
from ttk import Combobox

from collections import OrderedDict as OD
from os import environ as env, path
import csv
import platform
from time import strftime, localtime

# external library
import xlrd, xlwt
import psycopg2 as pg

###################################
####### Classes definition ########
###################################

class DB_Connection(Tk):
    def __init__(self):
        # basics settings
        Tk.__init__(self)               # constructor of parent graphic class
        self.title(u'Solinette: geolocalizar direcciones en Lima y Callo')
        if platform == 'win32':
#            self.logger.info('Operating system: Windows')
            uzer = env.get(u'USERNAME')
        elif platform == 'linux2':
#            self.logger.info('Operating system: Linux')
            uzer = env.get(u'USER')
        elif platform == 'darwin':
#            self.logger.info('Operating system: Mac')
            uzer = env.get(u'USER')
#        else:
#            self.logger.warning('Operating system unknown')
        self.resizable(width = False, height = False)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        # Frames
        self.FrPath = LabelFrame(self, name ='primero',
                            text = u'1: las direcciones para geolocalizar',
                            padx = 5, pady = 5)
        self.FrAttr = LabelFrame(self, name ='segundo',
                            text = u'2: columnas indispensables',
                            padx = 5, pady = 5)
        self.FrConn = LabelFrame(self, name ='tercero',
                            text = u'3: parámetros de conexión a la base de datos',
                            padx=5, pady=5)

        # Variables
        inutile = ['Esperando que se elige el archivo Excel']
        self.typcols = []
        self.host = StringVar()
        self.port = IntVar()
        self.dbnb = StringVar()
        self.usua = StringVar()
        self.mdpa = StringVar()
        self.ok = 0
        self.dico_cols = OD()
        self.dico_vals = OD()
        self.dico_param = {}

            ## Frame 1
        # target folder
        labtarg = Label(self.FrPath, text = u'Archivo Excel (.xls): ')
        self.target = Entry(self.FrPath, width = 35)
        self.browsetarg = Button(self.FrPath,
                                 text = 'Explorar',
                                 command = self.setpathtarg)

        # widgets placement
        labtarg.grid(row = 1, column = 1, columnspan = 1, sticky = N+S+W+E, padx = 2, pady = 2)
        self.target.grid(row = 1, column = 2, columnspan = 1, sticky = N+S+W+E, padx = 2, pady = 2)
        self.browsetarg.grid(row = 1, column = 3, columnspan = 1, sticky = N+S+W+E, padx = 2, pady = 2)

            ## Frame 2
        # Drop-down lists of columns
        labdir = Label(self.FrAttr, text = u'Columna dirección: ')
        self.ddl_dir = Combobox(self.FrAttr, values = inutile)
        labdis = Label(self.FrAttr, text = u'Columna distrito: ')
        self.ddl_dis = Combobox(self.FrAttr, values = inutile)

        # nombre de la tabla en PostgreSQL
        labtabl = Label(self.FrAttr, text = u'Nombre de la tabla: ')
        self.tabl = Entry(self.FrAttr, width = 35)

        # widgets placement
        labdir.grid(row = 1, column = 1, sticky = N+S+W, padx = 2, pady = 2)
        self.ddl_dir.grid(row = 1, column = 2, sticky = N+S+W+E, padx = 2, pady = 2)
        labdis.grid(row = 2, column = 1, sticky = N+S+W, padx = 2, pady = 2)
        self.ddl_dis.grid(row = 2, column = 2, sticky = N+S+W+E, padx = 2, pady = 2)
        labtabl.grid(row = 3, column = 1, sticky = N+S+W, padx = 2, pady = 2)
        self.tabl.grid(row = 3, column = 2, sticky = N+S+W+E, padx = 2, pady = 2)

            ## Frame 3

        # Etiquetas
        Label(self.FrConn, text = u'Host: ').grid(row = 1, column = 1,
                                                  padx = 2, pady = 2,
                                                  sticky = N+S+W)
        Label(self.FrConn, text = u'Puerto: ').grid(row = 2, column = 1,
                                             padx = 2, pady = 2,
                                             sticky = N+S+W)
        Label(self.FrConn, text = u'Base de datos: ').grid(row = 3,
                                                    column = 1,
                                                    padx = 2,
                                                    pady = 2,
                                                    sticky = N+S+W)
        Label(self.FrConn, text = u'Usuario: ').grid(row = 4,
                                              column = 1,
                                              padx = 2,
                                              pady = 2,
                                              sticky = N+S+W)
        Label(self.FrConn, text = u'Contraseña: ').grid(row = 5,
                                                 column = 1,
                                                 padx = 2,
                                                 pady = 2,
                                                 sticky = N+S+W)

        # Formulario
        self.H = Entry(self.FrConn, textvariable = self.host)
        self.P = Entry(self.FrConn, textvariable = self.port)
        self.D = Entry(self.FrConn, textvariable = self.dbnb)
        self.U = Entry(self.FrConn, textvariable = self.usua)
        self.M = Entry(self.FrConn, textvariable = self.mdpa, show='*')
        # pre relleno
        self.host.set('localhost')
        self.port.set('5432')
        self.usua.set('postgres')
        self.mdpa.set('')
        self.dbnb.set('solinette')

        # widgets placement
        self.H.grid(row = 1, column = 2, padx = 3, pady = 5, sticky = N+S+W+E)
        self.P.grid(row = 2, column = 2, padx = 3, pady = 5, sticky = N+S+W+E)
        self.D.grid(row = 3, column = 2, padx = 3, pady = 5, sticky = N+S+W+E)
        self.U.grid(row = 4, column = 2, padx = 3, pady = 5, sticky = N+S+W+E)
        self.M.grid(row = 5, column = 2, padx = 3, pady = 5, sticky = N+S+W+E)


            ## Global frame
        # Hola
        Label(self, text = '¡Hola! ' + uzer).grid(row = 0, column = 0,
                                                 columnspan = 2, sticky = W+E,
                                                 padx = 2, pady = 5)
        # Imagen
        #self.icone = PhotoImage(file = r'sources/logo_Solinette.GIF')
        #Label(self, borderwidth = 2, relief = 'ridge',
#                                     image = self.icone).grid(row = 1,
#                                                              rowspan = 4,
#                                                              column = 0,
#                                                              padx = 1,
#                                                              pady = 1,
#                                                              sticky = W)

        # Basic buttons
        self.val = Button(self, text = u'Probar la conexión',
                                relief= 'raised',
                                command = self.process,
                                state = DISABLED)
        can = Button(self, text = 'Cancel (quit)',
                                relief= 'groove',
                                command = self.quit)

        # widgets placement
        self.FrPath.grid(row = 2, column = 1, sticky = N+S+W+E, padx = 2, pady = 2)
        self.val.grid(row = 5, column = 1, columnspan = 2,
                            sticky = N+S+W+E, padx = 2, pady = 5)
        can.grid(row = 5, column = 0, sticky = N+S+W+E, padx = 2, pady = 5)

    def setpathtarg(self):
        """ ...browse and insert the path of target folder """
        self.xls = askopenfilename(parent = self,
                                   title = u'Seleccionar el archivo Excel',
                                   filetypes = (("Archivos Excel (2003)", "*.xls"),
                                                ("All files", "*.*")),
                                   initialdir = '../sources')

        if path.splitext(self.xls)[1] == '.xls':
            hoy = '_' + strftime('%y%m%d', localtime())
            self.target.insert(0, self.xls)
            self.licolumns()
            self.browsetarg.config(state=DISABLED)
            self.target.config(state=DISABLED)
            self.FrAttr.grid(row = 3, column = 1, sticky = N+S+W+E, padx = 2, pady = 2)
            self.FrConn.grid(row = 4, column = 1, sticky = N+S+W+E, padx = 2, pady = 2)
            self.tabl.insert(0, path.basename(self.xls).split('.')[0] + hoy)
            self.val.config(state = ACTIVE)
        # end of function
        return self.xls

    def licolumns(self):
        u""" litsing columns names and types from Excel file """
        book = xlrd.open_workbook(self.target.get())   # lectura del archivo
        if book.nsheets > 1:
            print book.sheets()
        ish = 0
        sheet = book.sheet_by_index(ish)    # ouverture de la feuille 1
        # names of columns (first row/line)
        cols = sheet.row_values(0)
        self.ddl_dir['values'] = cols
        self.ddl_dis['values'] = cols
        self.ddl_dir.current(1)
        self.ddl_dis.current(2)
        # types of columns
        self.typcols = list(sheet.row_types(1))
        # add universal ID to list of columns
        self.dico_cols['SOL_IDU'] = 9
        # loop on names and types of columns
        for i in range(len(cols)):
            self.dico_cols[cols[i]] = self.typcols[i]
        # End of function
        return book, self.typcols, self.dico_cols, self.ddl_dir, self.ddl_dis

    def check_campos(self):
        u""" Verifica que los campos del formulario son bien rellenos """
        # conteo y mensaje de los errores
        err = 0
        msj = u'Rellenar todos los campos'
        # checkeo de los campos vacios
        if self.host.get() == u'':
            self.H.configure(background = 'red')
            err = err +1
        if self.port.get() == 0:
            self.P.configure(background = 'red')
            err = err +1
        if self.dbnb.get() == u'':
            self.D.configure(background = 'red')
            err = err +1
        if self.usua.get() == u'':
            self.U.configure(background = 'red')
            err = err +1
        if self.mdpa.get() == u'':
            self.M.configure(background = 'red')
            err = err +1
        if self.tabl.get() == u'':
            self.tabl.configure(background = 'red')
            err = err +1
        if self.ddl_dir.get() == u'':
            self.ddl_dir.configure(background = 'red')
            err = err +1
        if self.ddl_dis.get() == u'':
            self.ddl_dis.configure(background = 'red')
            err = err +1
        # se colunas direcciones y distrito son diferentes
        if self.ddl_dir.get() == self.ddl_dis.get():
            msj = msj + u'\nLas dos columnas no deben ser iguales'
            err = err +1

        # Acción según si hay error(es) o no
        if err != 0:
            showerror(title = u'Error: campo(s) vacío(s)',
                      message = msj)
        # End of function
        return err

    def testconnexion(self):
        u""" testing connection settings """
        try:
            conn = pg.connect(host = self.host.get(), dbname = self.dbnb.get(),
                              port = self.port.get(), user = self.usua.get(),
                              password = self.mdpa.get())
            curs = conn.cursor()
            # check PostgreSQL and PostGIS versions
            try:
                curs.execute('SELECT version()')
                ver = curs.fetchone()
                print ver
            except DatabaseError, e:
                showerror(title = u'Prueba de conexión ',
                message = 'Prueba de conexión fracasó. Mensaje de error:\n' + str(e))
                return
            # check if destination table already exists
            query = "select table_name from information_schema.tables where 'sql_identifier' LIKE 'public'" #% (self.tabl.get())
            curs.execute(query)
            li_tablas = curs.fetchall()
            print 'elle existe déjà connard : ', li_tablas
            # información al usuario
            self.val.config(text='¡D A L E!')
            showinfo(title = u'Prueba de conexión ',
                     message = u'Prueba de conexión terminó con éxito')
            self.ok = 1
            # clausura de la conexión
            conn.close()

        except pg.OperationalError, e:
            showerror(title = u'Prueba de conexión ',
                      message = 'Prueba de conexión fracasó. Mensaje de error:\n' + str(e))
            return

        except ImportError , e:
            return None

    def iduxls(self, xlspath):
        u""" add an ID column to an Excel 2003 file (.xls) """
        outbook = xlwt.Workbook(encoding = 'utf8')
        outsheet = outbook.add_sheet(unicode('solinette'), cell_overwrite_ok = True)
        with xlrd.open_workbook(xlspath, encoding_override='utf8') as inbook:
            insh = inbook.sheet_by_index(0)
            for lig in range(0,insh.nrows):
                outsheet.write(lig, 0, unicode(lig))
                for col in range(insh.ncols):
                    outsheet.write(lig, col+1, insh.cell(lig, col).value)

        # name the ID column
        outsheet.write(0, 0, 'SOL_IDU')
        # save the output excel file
        outbook.save('temp\\ParaSolinette_' + path.basename(xlspath))
        # End of function
        return outbook, 'temp\\ParaSolinette_' + path.basename(xlspath)


    def quit(self):
        self.destroy()

    def xls2csv(self, xlspath):
        u""" export an Excel 2003 file (.xls) to a CSV file
        see: http://stackoverflow.com/a/10803229 """
        with xlrd.open_workbook(xlspath) as book:
            sheet = book.sheet_by_index(0)
            with open(path.join(env.get('TEMP'), path.splitext(path.basename(xlspath))[0] + '.csv'), 'wb') as f:
                out = csv.writer(f, delimiter='\t', dialect = 'excel-tab', quotechar='"')
                for row in range(sheet.nrows):
                    try:
                        out.writerow(sheet.row_values(row))
                    except:
                         out.writerow([unicode(s).encode("latin1") for s in sheet.row_values(row)])

        # End of function
        return book, f

    def xls2dict(self, xlspath):
        u""" export values from ab Excel 2003 file (.xls) into a dictionary """
        with xlrd.open_workbook(xlspath) as book:
            sh = book.sheet_by_index(0)
            for row in range(1, sh.nrows):
                self.dico_vals[row] = []
                for col in range(sh.ncols):
                    if sh.cell_type(row, col) is 1:
                        self.dico_vals[row].append(unicode(sh.cell_value(row, col)))
                    elif sh.cell_type(row, col) is 2:
                        self.dico_vals[row].append(unicode(sh.cell_value(row, col)))
                    elif sh.cell_type(row, col) is 3:
                        self.date = xlrd.xldate_as_tuple(sh.cell_value(row, col), book.datemode)
                        dico_vals[row].append(unicode('-'.join([unicode(i) for i in date[:3]])))
                    elif sh.cell_type(row, col) is 4:
                        self.dico_vals[row].append(unicode(int(sh.cell_value(row, col))))
                    elif sh.cell_type(row, col) is 0:
                        self.dico_vals[row].append(unicode('NULL'))
        # End of function
        return book, self.dico_vals

    def process(self):
        u""" makes ones tests before getting variables needed to process """
        # check of empty entries
        if self.check_campos() != 0:
            return

        if self.ok == 0:
            # test connection settings
            self.testconnexion()
            return

        # test versions of PostgreSQL and PostGIS

        # create a new xls with an universal ID
        self.iduxls(self.target.get())
        excel = self.iduxls(self.target.get())[1]

##        # export xls to csv
##        self.xls2csv(excel)
##        archivo = self.xls2csv(excel)[1]

        # export xls into a dictionary
        self.xls2dict(excel)

        # End of function
##        self.dico_param['archivo'] = archivo.name
        self.dico_param['direccion'] = self.ddl_dir.get()
        self.dico_param['distrito'] = self.ddl_dis.get()
        self.dico_param['pg_host'] = self.host.get()
        self.dico_param['pg_port'] = self.port.get()
        self.dico_param['pg_usuario'] = self.usua.get()
        self.dico_param['pg_bd'] = self.dbnb.get()
        self.dico_param['pg_pwd'] = self.mdpa.get()
        self.dico_param['tabla_out'] = self.tabl.get()
        self.dico_param['tipo_cols'] = self.typcols
        self.dico_param['cols'] = self.dico_cols
        self.dico_param['values'] = self.dico_vals
        self.quit()

##        return self.dico_param, self.target.get(), self.ddl_dir.get(), self.ddl_dis.get(), \
##                self.host.get(), self.port.get(), self.usua.get(), \
##                self.mdpa.get(), self.dbnb.get(), self.tabl.get(), self.typcols

################################################################################
if __name__ == '__main__':
    app = SolinetteGUI()
    app.mainloop()
    result = app.dico_param
    values = result.get('values')

#### Memo
##1 'XL_CELL_TEXT',cell_contents(sheet,1)
##2 'XL_CELL_NUMBER',cell_contents(sheet,2)
##3 'XL_CELL_DATE',cell_contents(sheet,3)
##0 'XL_CELL_BLANK',cell_contents(sheet,6)
##4 'XL_CELL_BOOLEAN',cell_contents(sheet,4)
##5 'XL_CELL_ERROR',cell_contents(sheet,5)
