#DicoGIS

Available in 3 languages ([English](#en), [French](#fr) and [Spanish](#es)) but you can add your own translations (in [locale folder](https://github.com/Guts/DicoGIS/tree/master/data/locale)).

##EN
Automatize the creation of a dictionnary of geographic data in a folders structure. The output dictionary is an Excel file (.xls).

### Windows
 1. Download the [last release](https://github.com/Guts/DicoGIS/releases),
 2. Uncompress it,
 3. Execute **DicoGIS.exe**.

If you've all dependencies installed, you can also clone this repository, edit it and create your customized executable, running:
```bash
python setup2exe_DicoGIS.py py2exe
```

#### Advanced usage

1. Open an elevated powershell (as admin) ;
2. Ensure that you have Python to the environment path typing `[Environment]::SetEnvironmentVariable("Path", "$env:Path;C:\Python27\;C:\Python27\Scripts\", "User")` ;
3. Download [get_pip.py](https://raw.githubusercontent.com/pypa/pip/master/contrib/get-pip.py) and execute it: `python get_pip.py` ;
4. Download the repository and execute: `pip install virtualenv virtualenvwrapper-powershell` ;
5. Execute: `set-executionpolicy RemoteSigned` to allow powershell advanced scripts. ;
6. Create the environment: `virtualenv virtenv --no-site-packages` ;
7. Activate it: `.\virtenv\Scripts\activate.ps1`. Your prompt should have changed. ;
8. Get the dependencies, choosing between 32/64 bits versions: `pip install -r requirements_32bits.txt` or `pip install -r requirements_64bits.txt` ;
9. Assuming you have installed Python in C:\Python27\, copy the *tcl* folder from C:\Python27\ over to the root of the new virtenv (see: http://stackoverflow.com/a/30377257) to avoid this error: "This probably means that tk wasn't installed properly.". You can do that from your admin powershell prompt executing: `Copy-Item -Path c:\python27\tcl\* -Destination {absolute_path_to_the_folder}\DicoGIS\virtenv\tcl -recurse -Container: $true`
10. For a more friendly usage, create a Windows shortcut: Right clic > New > Shortcut and insert this command replacing with the absolute paths (removing brackets): `C:\Windows\System32\cmd.exe /k "{absolute_path_to_the_folder}\DicoGIS\virtenv\Scripts\python {absolute_path_to_the_folder}\DicoGIS\DicoGIS.py"`

### Ubuntu (or others Debian distributions)

You can [download this repository](https://github.com/Guts/DicoGIS/archive/master.zip) or run these commands:
```bash
sudo apt-get install -y git python-software-propertie
sudo add-apt-repository -y ppa:ubuntugis/ubuntugis-unstable
sudo apt-get update && sudo apt-get dist-upgrade
sudo apt-get install -y python-setuptools python-pip python-dev python-tk python-gdal
sudo pip install -r requirements.txt
git clone https://github.com/Guts/DicoGIS.git
```

## FR

Pour une présentation plus sympa, consulter [l'article sur GeoTribu](http://geotribu.net/dicogis).

Crée un dictionnaire des données géographiques (shapefiles et tables MapInfo) contenues dans une arborescence de répertoire. Le dictionnaire prend la forme d'un fichier Excel (.xls).

### Sous Windows
 1. Télécharger la [dernière version](https://github.com/Guts/DicoGIS/releases),
 2. Décompresser l'archive,
 3. Lancer **DicoGIS.exe**.

Si toutes les dépendances sont installées, vous pouvez créer votre version personnalisée en exécutant dans la console :
```bash
python setup2exe_DicoGIS.py py2exe
```



###Ubuntu (ou toute autre distribution Debian a priori)
Vous pouvez télécharger [l'ensemble du dépôt](https://github.com/Guts/DicoGIS/archive/master.zip) ou bien lancer ces commandes dans un terminal :
```bash
sudo apt-get install -y git python-software-propertie
sudo add-apt-repository -y ppa:ubuntugis/ubuntugis-unstable
sudo apt-get update && sudo apt-get dist-upgrade
sudo apt-get install -y python-setuptools python-pip python-dev python-tk python-gdal
sudo pip install -r requirements.txt
git clone https://github.com/Guts/DicoGIS.git
```

##ES

Para una presentación mas completa, ver [el articulo en Mapping GIS](http://mappinggis.com/2014/10/dicogis-el-diccionario-de-datos-gis/).

Automatiza la creación de un diccionario de los datos geográficos (shapefiles y tablas MapInfo) contenidos en una estructura de carpetas. El archivo final es una tabla Excel (.xls).

###Windows
 1. Descargar la [ultima versión](https://github.com/Guts/DicoGIS/releases),
 2. Extraer el archivo,
 3. Ejecutar **DicoGIS.exe**.
