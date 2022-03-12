import json, os, shutil, platform
from datetime import datetime
from os import listdir
from os.path import isfile, join


 
#read JSON and TXT files
def ReadFILE(path):
    if(path[-3:] == "txt"):
        with open(path, "r") as file:
            return file.readlines()
    else:
        with open(path, 'r') as file:
            return json.load(file)
  
#Outputs the stored data inside a json file, i.e:
#jsonPath = "dir1/dir2" it will output file[dir1][dir2]
def getDataJSON(filePath, jsonPath):
    file = ReadFILE(filePath)
    for element in jsonPath.split('/'):
        file = file[element] #each element enters a new path
    return file

#Handle the windows path and Linux path
def convertPath(path):
    sysos = getDataJSON(setting_path, "System Os")
    if(sysos.lower() == 'linux'):
        return path
    else:
        return path.replace('/', '\\')

#Write on JSON files
def WriteJSON(filePath, toWrite, mode):
    with open(filePath, mode) as outfile:
        json.dump(toWrite, outfile, indent=4)

#Create "Playlists Informations.json" and "Settings.json"
def SettingUp():
    currentPath = os.path.abspath(os.getcwd())
    if('/' in currentPath):
        currentPath += '/'
    else:
        currentPath += '\\'
        
    Settings = {
        "System Os": str(platform.system()),
        "Settings": {
            "Quality": "BEST",
            "Format": "MP3",
            "Paths": {
                "Downloads": "",
                "Playlist": ""
            }
        }
    }
    onlyfiles = [f for f in listdir(currentPath) if isfile(join(currentPath, f))]
    if("Settings.json" not in onlyfiles):    
        WriteJSON(currentPath + "Settings.json", Settings, 'w')
    
    playlistInformations = {
        "Playlists Informations" : [],
        "Playlists links": []
    }
    onlyfiles = [f for f in listdir(convertPath(currentPath + "Data/")) if isfile(join(convertPath(currentPath + "Data/"), f))]
    if("Playlists Informations.json" not in onlyfiles):
        WriteJSON(convertPath(currentPath + "Data/Playlists Informations.json") , playlistInformations, 'w')
    
setting_path = "Settings.json"

#Print loadtext.txt
def printLoad(start, end): 
    loadText = ReadFILE(convertPath("Data/loadtext.txt"))[start:end]
    for line in loadText:
        print(line[:-1])
        
#Checks if the file is a song or not from these formats
#["WAV", "VORBIS", "OPUS", "M4A", "FLAC", "AAC", "MP3"]
#<Coming soon>
def isFilePlaylist(file):
    if(file[-3:] == "m3a"):
        return True
    else:
        return False
        
#Deletes the temporary files
def deleteTemporaryFiles(path):
    try:
        shutil.rmtree(convertPath(path + '/tmp/'))
    except OSError:
        pass
    try:
        os.remove(convertPath(path + '/.cache'))
    except OSError:
        pass  
    
#Checks if a link is playlist or album
def isLinkAlbum(link):
    if("album" not in link):
        return False
    else:
        return True