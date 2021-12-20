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
#still in progress <Coming soon>
def convertPath(path):
    sysos = getDataJSON(setting_path, "System Os")
    if(sysos == 'Linux'):
        return path.replace('-', '/')
    else:
        return path.replace('-', '\\')

#Set outdated path
def SetOutdatedPath(SavifyFile):
    outdatedPL_path = SavifyFile["Settings"]["Locations"]["Playlist"] + "\\Outdated Playlists"
    SavifyFile["Settings"]["Locations"]["Outdated Playlists"] = outdatedPL_path
    with open(setting_path, 'w') as outfile:
        json.dump(SavifyFile, outfile, indent=4)

#Print loadtext.txt
def printLoad(start, end):
    loadText = ReadFILE("loadtext.txt")[start:end]
    for line in loadText:
        print(line[:-1])
        
#Write on JSON files
def WriteJSON(filePath, toWrite, mode):
    with open(filePath, mode) as outfile:
        json.dump(toWrite, outfile, ident=4)