# -*- mode: python -*-

block_cipher = None

from os import path
from shutil import copyfile

# ------------ Initial settings ----------------------------------------------

copyfile("options_TPL.ini", "build\options.ini")

# ----------------------------------------------------------------------------

added_files = [('build\options.ini', '.'),
               ('LICENSE', '.'),
               ('README.md', '.'),
               ('DicoGIS.ico', '.'),
               ('data\\img\\DicoGIS_logo.gif', 'data\\img'),
               ('data\\img\\logo_isogeo.gif', 'data\\img'),
               ('data\\locale\\lang_EN.xml', 'data\\locale'),
               ('data\\locale\\lang_FR.xml', 'data\\locale'),
               ('data\\locale\\lang_ES.xml', 'data\\locale'),
              ]


a = Analysis(['DicoGIS.py'],
             pathex=['C:\\Users\\julien.moura\\Documents\\GitHub\\Perso\\DicoGIS'],
             binaries=None,
             datas=added_files,
             hiddenimports=[],
             hookspath=["hooks"],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)

pyz = PYZ(a.pure,
          a.zipped_data,
          cipher=block_cipher)

exe = EXE(pyz,
          a.scripts,
          exclude_binaries=True,
          name='DicoGIS',
          debug=False,
          strip=False,
          upx=False,
          console=False,
          icon='DicoGIS.ico',
          windowed=True,
          version='bundle_version.txt')

coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=False,
               name='DicoGIS',
               icon='data\\img\\DicoGIS_logo.gif'
               )
