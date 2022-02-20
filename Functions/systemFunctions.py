import json, os, shutil
from datetime import datetime


#Write on JSON files
def WriteJSON(filePath, toWrite, mode):
    with open(filePath, mode) as outfile:
        json.dump(toWrite, outfile, indent=4)

#Create "Playlists Informations.json" and "Settings.json"
def SettingUp():
    currentPath = os.path.abspath(os.getcwd())
    Settings = {
        "System Os": "",
        "Settings": {
            "Quality": "BEST",
            "Format": "MP3",
            "Paths": {
                "Downloads": "",
                "Playlist": "",
                "Outdated Playlists": ""
            }
        }
    }
    WriteJSON(currentPath + "Settings.json", Settings, "w")
    
    playlistInformations = {
        "Playlists Informations" : [],
        "Playlists links": []
    }
    WriteJSON(currentPath + "Playlists Informations.json", playlistInformations, 'w')
    
setting_path = "Settings.json"

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

#Set outdated path
def SetOutdatedPath(settingFile):
    settingFile["Settings"]["Paths"]["Outdated Playlists"] = convertPath(settingFile["Settings"]["Paths"]["Playlist"] + 'Outdated Playlists/')
    return settingFile

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

#Store the old playlists in a folder with a date in it
def movePlaylists():
    playlist_path = getDataJSON(setting_path, "Settings/Paths/Playlist")
    odFolder_path = convertPath(getDataJSON(setting_path, "Settings/Paths/Outdated Playlists") + "/" + datetime.now().strftime("%Y-%m-%d (%Hh.%Mm)")) 
    
    sysos = getDataJSON(setting_path, "System Os")
    files = [f for f in os.listdir(playlist_path) if (os.path.isfile(f) and (isFilePlaylist(f) == True))]
    for file in files:
        try:
            os.makedirs(odFolder_path)    
        except FileExistsError:
            pass 
        #move the old playlist to the outdated folder
        pl_path = convertPath(playlist_path + "/" + file)
        odPl_path = convertPath(odFolder_path + "/" + file)
        shutil.move(pl_path, odPl_path)
        
#Deletes the log files
def CleanLogs(path):
    shutil.rmtree(path)
    
#Checks if a link is playlist or album
def isLinkAlbum(link):
    if("album" not in link):
        return False
    else:
        return True