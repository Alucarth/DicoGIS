from distutils.core import setup
import py2exe
import os

# custom modules
from modules import *

py2exe_options = dict(
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
      data_files = [("locale", ["locale/lang_EN.xml", "locale/lang_ES.xml", "locale/lang_FR.xml"]),("", ["settings.xml"]),("", ["DicoGIS.ico"]),("img", ["img/DicoGIS_logo.gif"]),("documentation",["documentation/DicoGIS_Manual_ES.docx"])],
      options={'py2exe': py2exe_options},
      windows = [
            {
            "script": "DicoGIS.py",              # script
            "icon_resources": [(1, "DicoGIS.ico")]     # Icone
            }
                ]
    )



