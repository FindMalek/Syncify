import json, os, shutil

setting_path = "Settings.json"

#read any file
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
    if(sysos == 'Linux'):
        return path.replace('à@à', '/')
    else:
        return path.replace('à@à', '\\')

#Write on JSON files
def WriteJSON(filePath, toWrite, mode):
    with open(filePath, mode) as outfile:
        json.dump(toWrite, outfile, indent=4)

#Set outdated path
def SetOutdatedPath(settingFile):
    odPlaylist_path = convertPath(settingFile["Settings"]["Paths"]["Playlist"] + 'à@àOutdated Playlists')
    settingFile["Settings"]["Paths"]["Outdated Playlists"] = odPlaylist_path
    return settingFile

#Print loadtext.txt
def printLoad(start, end): 
    loadText = ReadFILE(convertPath("Resourcesà@àloadtext.txt"))[start:end]
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