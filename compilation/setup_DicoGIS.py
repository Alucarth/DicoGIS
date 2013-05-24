from distutils.core import setup
import py2exe
import os

# custom modules
from modules import *

mfcdir = r'C:\Python27\Lib\site-packages\pythonwin'
mfcfiles = [os.path.join(mfcdir, i) for i in ["mfc90.dll", "mfc90u.dll", "mfcm90.dll", "mfcm90u.dll", "Microsoft.VC90.MFC.manifest"]]

py2exe_options = dict(
                      dll_excludes = ['MSVCP90.dll'],
                      compressed=True,  # Compress library.zip
                      optimize = 2,
                      dist_dir = 'DicoGIS'
                      )

setup(name="DicoGIS",
      version="1.5",
      description=u"Dynamic dictionary of geographic datas",
      author="Julien Moura",
      author_mail = "julien.moura@gmail.com",
      url = "https://github.com/Guts/Solinette",
      license="license GPL v3.0",
      data_files = [("", ["setting.xml"]),("", ["DicoGIS.ico"]),("img", ["img/DicoGIS_logo.gif"]),("documentacion",["documentation/DicoGIS_Manual_ES.docx"])],
      data_files=[("Microsoft.VC90.MFC", mfcfiles)],
      options={'py2exe': py2exe_options},
      windows = [
            {
            "script": "DicoGIS.py",              # script
            "icon_resources": [(1, "DicoGIS.ico")]     # Icone
            }
                ]
    )
