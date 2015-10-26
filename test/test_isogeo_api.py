import os
import zipfile
import requests
import shutil
os.environ["PATH"] = ""

directoryToZip = os.path.dirname(FME_LogFileName) + '\\' + FME_MacroValues['dest'] + '\\' + FME_MacroValues['schema'] + '\\' + FME_MacroValues['table']

# get a token
headers = {'Access-Control-Allow-Origin': '*'}
payload = {
    'client_id': 'isogeo-app',
    'client_secret': '',
    'grant_type': 'password',
    'username': FME_MacroValues['isogeo_user'],
    'password': FME_MacroValues['isogeo_password']}
token_request = requests.post(FME_MacroValues['isogeo_id'] + '/oauth/token', data=payload, headers=headers)
token = token_request.json()['access_token']

# getting and writing the resource XML file
xml_file_name = FME_MacroValues['resource_isogeo_id'] + '.xml'
xml_file_path = directoryToZip + '\\' + xml_file_name
headers = {'Access-Control-Allow-Origin': '*',
    'Authorization': 'Bearer ' + token}
xml_request = requests.get(FME_MacroValues['isogeo_api'] + '/resources/' + xml_file_name, headers=headers)
xml_file = open(xml_file_path, "w")
xml_file.write(xml_request.text.encode('utf-8'))
xml_file.close()

def list_folders_and_files(path):
    for dir in os.listdir(path):
        yield os.path.join(path, dir)

def zip_directory(data_path, zip_output):
    multifile = False
    # it's a multi files dataset like gml 
    if os.path.exists(zip_output.lower() + '.zip'):
        multifile = True
    zip = zipfile.ZipFile(zip_output.lower() + '.zip', 'a', compression=zipfile.ZIP_DEFLATED)
    if os.path.isdir(data_path):
        for root, dirs, files in os.walk(data_path):
            for f in files:
                file_path = os.path.join(data_path, f)
                zip.write(file_path, f.lower())
    else:
        file_name = os.path.basename(data_path)
        zip.write(data_path, file_name.lower())
    if not multifile:
        zip.write(xml_file_path, 'md_' + os.path.basename(zip_output.lower()) + '.xml')
    zip.close()
    return zip_output

for formatsFolder in list_folders_and_files(directoryToZip):
    if os.path.isdir(formatsFolder):
        for srsFolder in list_folders_and_files(formatsFolder):
            for areaFolder in list_folders_and_files(srsFolder):
                for data_path in list_folders_and_files(areaFolder):
                    if os.path.isdir(data_path):
                        zip_output = data_path
                    else:
                        zip_output = os.path.splitext(data_path)[0]
                    # make the archive
                    zip_directory(data_path, zip_output)
                    # remove the original data to keep only the archive
                    if os.path.isdir(data_path):
                        shutil.rmtree(data_path, ignore_errors=True)
                    else:
                        os.remove(data_path)
