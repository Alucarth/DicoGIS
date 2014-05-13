#DicoGIS

Including 3 languages ([English](#en), [French](#fr) and [Spanish](#es)) but you can add your own translations (in [locale folder](https://github.com/Guts/DicoGIS/tree/master/data/locale)).

##EN
Automatize the creation of a dictionnary of geographic data in a folders structure. The output dictionary is an Excel file (.xls).

###How to use
####Windows
 1. Download the [last release](https://github.com/Guts/DicoGIS/releases),
 2. Uncompress it,
 3. Execute **DicoGIS.exe**.

If you've all dependencies installed, you can also clone this repository, edit it and create your customized executable, running:
```bash
python setup2exe_DicoGIS.py py2exe
```

####Ubuntu (or others Debian distributions)
You can [download this repository](https://github.com/Guts/DicoGIS/archive/master.zip) or run these commands:
```bash
sudo apt-get install -y git python-software-propertie
sudo add-apt-repository -y ppa:ubuntugis/ubuntugis-unstable
sudo apt-get update && sudo apt-get dist-upgrade
sudo apt-get install -y python-setuptools python-pip python-dev python-tk python-gdal
sudo pip install -r requirements.txt
git clone https://github.com/Guts/DicoGIS.git
```

##FR

Crée un dictionnaire des données géographiques (shapefiles et tables MapInfo) contenues dans une arborescence de répertoire. Le dictionnaire prend la forme d'un fichier Excel (.xls).

###Sous Windows
 1. Télécharger la [dernière version](https://github.com/Guts/DicoGIS/releases),
 2. Décompresser l'archive,
 3. Lancer **DicoGIS.exe**.

Si toutes les dépendances sont installées, vous pouvez créer votre version personnalisée en exécutant dans la console :
```bash
python setup2exe_DicoGIS.py py2exe
```

####Ubuntu (ou toute autre distribution Debian a priori)
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

Automatiza la creación de un diccionario de los datos geográficos (shapefiles y tablas MapInfo) contenidos en una estructura de carpetas. El archivo final es una tabla Excel (.xls).

###Windows
 1. Descargar la [ultima versión](https://github.com/Guts/DicoGIS/releases),
 2. Extraer el archivo,
 3. Ejecutar **DicoGIS.exe**.
