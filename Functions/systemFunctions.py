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

#Store the old playlists in a folder with a date in it
def movePlaylists():
    playlist_path = getDataJSON(setting_path, "Settings/Paths/Playlist")
    odFolder_path = convertPath(getDataJSON(setting_path, "Settings/Paths/Outdated Playlists") + "à@à" + datetime.now().strftime("%Y-%m-%d (%Hh.%Mm)")) 
    
    sysos = getDataJSON(setting_path, "System Os")
    files = [f for f in os.listdir(playlist_path) if (os.path.isfile(f) and (isFilePlaylist(f) == True))]
    for file in files:
        try:
            os.makedirs(odFolder_path)    
        except FileExistsError:
            pass 
        #move the old playlist to the outdated folder
        pl_path = convertPath(playlist_path + "à@à" + file)
        odPl_path = convertPath(odFolder_path + "à@à" + file)
        shutil.move(pl_path, odPl_path)

#download ettings
def DownloadSettings(Savify):
    SavifySettings = ReadFILE(setting_path)["Settings"]
    
    if(SavifySettings["Quality"] == "BEST"):    qual=Quality.BEST
    elif(SavifySettings["Quality"] == "Q320K"): qual=Quality.Q320K
    elif(SavifySettings["Quality"] == "Q256K"): qual=Quality.Q256K
    elif(SavifySettings["Quality"] == "Q192K"): qual=Quality.Q192K
    elif(SavifySettings["Quality"] == "Q128K"): qual=Quality.Q128K
    elif(SavifySettings["Quality"] == "Q96K"):  qual=Quality.Q96K
    elif(SavifySettings["Quality"] == "Q32K"):  qual=Quality.Q32K
    elif(SavifySettings["Quality"] == "WORST"): qual=Quality.WORST  
    
    if(SavifySettings["Format"] == "WAV"):      download_format=Format.WAV
    elif(SavifySettings["Format"] == "VORBIS"): download_format=Format.VORBIS
    elif(SavifySettings["Format"] == "OPUS"):   download_format=Format.OPUS
    elif(SavifySettings["Format"] == "M4A"):    download_format=Format.M4A 
    elif(SavifySettings["Format"] == "FLAC"):   download_format=Format.FLAC 
    elif(SavifySettings["Format"] == "AAC"):    download_format=Format.AAC
    elif(SavifySettings["Format"] == "MP3"):    download_format=Format.MP3 
    
    return qual, download_format