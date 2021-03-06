DicoGIS: el diccionario de datos SIG
====

O como crearse su propio DRAE de la información geográfica en 5 minutos y 3 clicks.
Les presento un pequeño herramienta sin ninguna pretensión sino de ser bien práctico para manejar sus datos.

![DicoGIS - Animated demonstration](https://raw.githubusercontent.com/Guts/DicoGIS/master/doc/DicoGIS_demo.gif "DicoGIS - Animated demonstration")

# Presentación

[DicoGIS](https://github.com/Guts/DicoGIS) es un pequeño utilitario que produce un diccionario de datos al formato Excel 2003 (.xls). Disponible en ejecutable Windows (.exe) sin instalación requerida y en script (consultar las dependencias), se puede usar directamente desde una USB.

![DicoGIS - Logo](https://raw.githubusercontent.com/Guts/DicoGIS/master/data/img/DicoGIS_logo.gif "DicoGIS - Logo")

Es muy útil para precisos casos:

- se le entrega una base de datos, tipo archivos o tipo PostGIS, dentro de la cual le gustaría saber lo que hay adentro;
- en el marco de su trabajo, le gustaría ofrecer fácilmente una lista de los datos entregados a sus colegas/partenarios/clientes.

Empecé a desarollarlo como complemento de [Metadator](http://www.datamadre.com/posts/17) y sigo usandolo de manera regular para realizar una rápida evaluación de los datos y tener una base de trabajo para constituir los tesauros de palabras claves en el marco de mis misiones a [Isogeo](http://www.isogeo.com/).

# Características técnicas

## Parte desarollo

- desarollado en [Python 2.7.8](https://www.python.org/) ;
- basado en el módulo [GDAL/OGR 1.11.0-2](http://www.gdal.org/) para leer geodatas;
- módulo [python-excel/xlwt](https://github.com/python-excel/xlwt) para escribir los archivos Excel 2003 (.xls);
- módulo [Tkinter / ttk](https://docs.python.org/2/library/tkinter.html)para la interfaz gráfica (viene por defecto con Python en Windows pero no con las distribuciones Debian);
- módulo [py2exe](http://www.py2exe.org/) para generar fácilmente el ejecutable Windows.

El código esta disponible en GitHub bajo la licencia GPL 3: significa que cada esta libre para reutilizar o modificar el código.

## Parte uso

En teoría, los formatos compatibles son todos que cuenta [GDAL](http://www.gdal.org/formats_list.html) e [OGR](http://www.gdal.org/ogr_formats.html) pero por el momento, aquí los implementados son:

- vectores: shapefile, tables MapInfo, GeoJSON, GML, KML
- rasters: ECW, GeoTIFF, JPEG
- bases de datos archivos ("flat"): Esri File GDB
- CAO: DXF (+ lista de los DWG)
- Documentos cartográficos: Geospatial PDF

El script Python es compatible con los mayores sistemas operativos:

- Ubuntu 12/14.04
- Windows 7/8.1
- Mac OS X (gracias a [GIS Blog Fr](https://twitter.com/gisblogfr/status/515068147901407232))

DicoGIS existe en [3 idiomas (Français, Anglais et Espagnol)](https://github.com/Guts/DicoGIS/tree/master/data/locale) pero es muy fácil de personalizar o añadir una traducción.

¿Qué tal los performancias? Eso si depende de la computadora que lo ejecute. Pero, para tener una idea, en la mía DicoGIS demora mas o menos 20 segundos para:

- una cuarentena de vectores,
- una decena de rasters (representando 90 Mo al total),
- 7 FileGDB conteniendo unos 60 vectores,
- y unos archivos DXF.

# Como usarlo

1/ Descargar la última versión:

* sea del [ejecutable Windows](https://github.com/Guts/DicoGIS/releases),
* sea del [código fuente](https://github.com/Guts/DicoGIS/archive/master.zip).

2/ Descomprimir y iniciar DicoGIS.exe / el script DicoGIS.py

![DicoGIS - Launch](https://raw.githubusercontent.com/Guts/DicoGIS/master/doc/00a_DicoGIS_Win32exe.PNG "DicoGIS - Launch")

3/ Cambiar el idioma

![DicoGIS - Switch language](https://github.com/Guts/DicoGIS/blob/master/doc/99_DicoGIS_SwitchLanguage.gif "DicoGIS - Switch language")

4/a Para datos organizados en archivos:

- Escoger la carpeta principal: la exploración empieza y la barra de progresión continua hasta el fin del listing;
- Elegir los formatos deseados;

![DicoGIS - Listing](https://raw.githubusercontent.com/Guts/DicoGIS/master/doc/02_DicoGIS_Listing.gif "DicoGIS - Listing")

4/b Para datos almacenados en una base de datos PostgreSQL / PostGIS, es lo mismo principio excepto que se debe entrar los parámetros de conexión:

![DicoGIS - Processing PostGIS](https://raw.githubusercontent.com/Guts/DicoGIS/master/doc/06_DicoGIS_PostGIS.gif "DicoGIS - Processing PostGIS")

5/ Iniciar y esperar hasta el fin del proceso: guardar el archivo Excel generado.

![DicoGIS - Processing files](https://raw.githubusercontent.com/Guts/DicoGIS/master/doc/05_DicoGIS_Processing.gif "DicoGIS - Processing files")

6/ Consultar el archivo y arreglar los estilos según sus preferencias. También un archivo DicoGIS.log es muy interesante.


# Y al final, ¿que tipo de informaciones para que tipo de datos?

El archivo Excel (2003 = .xls) contiene metadatos organizados en pestañas según el tipo de datos. Hice una [matrix resumiendo las informaciones para cada formato](https://github.com/Guts/DicoGIS/blob/master/doc/InfosByFormats_matrix.md).

# Lo que se puede esperar para el futuro

- tomar en cuenta más formatos: DGN, Spatialite, MXD, QGS, Geoconcept.
- agregar una pestaña con estadísticas sobre atributos, objetos, etc. 
- cambiar de python-xlwt para xlsxwriter.
- pasar a Python 3.x pero hay que esperar que py2exe sea listo.
- pasar al multiprocessing, pero creo que hay un conflicto con py2exe.
