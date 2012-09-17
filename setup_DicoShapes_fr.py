from distutils.core import setup
import py2exe
import os

mfcdir = r'C:\Python27\Lib\site-packages\pythonwin'
mfcfiles = [os.path.join(mfcdir, i) for i in ["mfc90.dll", "mfc90u.dll", "mfcm90.dll", "mfcm90u.dll", "Microsoft.VC90.MFC.manifest"]]

includes = ["encodings",
            "encodings.latin_1", "encodings.utf_8"]

py2exe_options = dict(
                      excludes=['_ssl',  # Exclude _ssl
                                'pyreadline', 'doctest', 'email',
                                'optparse'],  # Exclude standard library
                      includes = includes,
                      dll_excludes = ['MSVCP90.dll'],
                      compressed=True,  # Compress library.zip
                      optimize = 2,
                      )

setup(name="Dico Shapes",
      version="1.3",
      description=u"Création d'un dictionnaire au format Excel (2003) des \
                    shapefiles d'une arborescence",
      author="Julien Moura",
      license="license GPL v3.0",
      data_files=[("Microsoft.VC90.MFC", mfcfiles)],
      options={'py2exe': py2exe_options},
      windows = [
            {
            "script": "DicoShapes_fr.py",              # script
            "icon_resources": [(1, "DicoGIS.ico")]     # Icone
            }
                ]
    )
