#Importing Os modules
import json, os, shutil, platform, sys, logging, re
from os import listdir
from os.path import isfile, join, exists

#Importing Moviepy for audio conversion
from moviepy.editor import *

 
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

#Remove '\n' and '\t' from the message
def removeNewLines(msg):
    while('\n' in msg) or ('\t' in msg):
        msg = msg.strip()
        msg = re.sub('\s+', ' ', msg)
    return msg

#Logging class that prints and also logs
class logsSyncify: 
    def __init__(self, infos=""):
        #Fix for the next update!!
        self.filename = ""          #infos.split('/')[0]
        self.funcName = ""          #infos.split('/')[1]
        self.line = ""              #infos.split('/')[2]
        
    #Setup logging configs
    def loggingSetup(self):
        #Deleting "logs.log"
        try:
            os.remove(convertPath("Data/logs.log"))
        except OSError:
            pass  
        
        logging.basicConfig(
            filename = convertPath("Data/logs.log"),
            level=logging.DEBUG,
            format="[%(asctime)s] - [" + self.filename + "/" + self.funcName + "/"  + self.line + "] - (%(levelname)s) - %(message)s"
        )
        
    def message(msg):
        print(msg)
         
    def info(msg):
        print(msg)
        logging.info(f'(Syncify): {removeNewLines(msg)}')
        
    def debug(msg):
        logging.debug(f'(Syncify): {removeNewLines(msg)}')
        
    def warning(msg):
        logging.warning(f'(Syncify): {removeNewLines(msg)}')
        
    def critical(msg):
        print(f'(CRITICAL) -> (Syncify): {removeNewLines(msg)}')
        logging.critical(f'(Syncify): {removeNewLines(msg)}')
            
#Write on JSON files
def WriteJSON(filePath, toWrite, mode):
    with open(filePath, mode) as outfile:
        json.dump(toWrite, outfile, indent=4)

#Create "UserData.json" and "Settings.json"
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
            "Sleep": 1.25,
            "Time Difference": 15,
            "Search Accuracy": 6,
            "Download Order": ["Playlists", "Albums", "Tracks"],
            "Paths": {
                "Downloads": "",
                "Playlist": "",
                "Temporary Downloads": currentPath + "Data"
            }
        }
    }
    onlyfiles = [f for f in listdir(currentPath) if isfile(join(currentPath, f))]
    if("Settings.json" not in onlyfiles):    
        WriteJSON(currentPath + "Settings.json", Settings, 'w')
        
    playlistInformations = {
        "Playlists": [],
        "Albums" : [],
        "Tracks": []
    }
    onlyfiles = [f for f in listdir(convertPath(currentPath + "Data/")) if isfile(join(convertPath(currentPath + "Data/"), f))]
    if("userData.json" not in onlyfiles):
        WriteJSON(convertPath(currentPath + "Data/userData.json") , playlistInformations, 'w')
    
    #Setting up the logging configuration
    logsSyncify().loggingSetup()
    
setting_path = "Settings.json"

#Print loadtext.txt
def printLoad(start, end): 
    loadText = ReadFILE(convertPath("Data/loadtext.txt"))[start:end]
    for line in loadText:
        print(line[:-1])
        
#Checks if the file is a song or not from these formats
def isFilePlaylist(file):
    if(file[-3:] == "m3a"):
        return True
    else:
        return False
        
#Deletes the temporary files
def deleteTemporaryFiles(path):
    try:
        shutil.rmtree(convertPath(path + '/tmp/'))
        logsSyncify().debug(f"Deleted {convertPath(path + '/tmp/')}")

    except OSError:
        pass
    
    try:
        os.remove(convertPath(path + '/.cache'))
        logsSyncify().debug(f"Deleted {convertPath(path + '/.cache')}")

    except OSError:
        pass  
    
    try:
        shutil.rmtree(convertPath(path + '/SyncifyFunctions/__pycache__'))
        logsSyncify().debug(f"Deleted {convertPath(path + '/SyncifyFunctions/__pycache__')}")

    except:
        pass
    
    try:
        shutil.rmtree(convertPath(path + '/spotifyHandler/__pycache__'))
        logsSyncify().debug(f"Deleted {convertPath(path + '/spotifyHandler/__pycache__')}")

    except:
        pass
    
    try:
        shutil.rmtree(convertPath(path + '/downloadHandler/__pycache__'))
        logsSyncify().debug(f"Deleted {convertPath(path + '/downloadHandler/__pycache__')}")

    except:
        pass
    
    try:
        onlyfiles = [f for f in listdir(convertPath(path + "/Data/")) if isfile(join(convertPath(path + "/Data/"), f))]
        for file in onlyfiles:
            if('.mp3' in file) or ('.mp4' in file):
                os.remove(convertPath(path + "/Data/" + file))
        logsSyncify.debug(f"Deleted '.mp4' and '.mp3' files.")
    
    except:
        pass

#Checks if a link is playlist or album
def whatIsLink(link):
    if("album" in link):
        return "Album"
    elif("playlist" in link):
        return "Playlist"
    elif("track" in link):
        return "Track"

#Add information in settings file
def addInformation(stroption, info, infoList, Settings):
    while True:
        infoEntered = input(f"{stroption} chosen (Press <Enter>, If you don't wish to change the {stroption}): ")
        if(infoEntered == ''):
            Settings["Settings"][stroption] = info
            break
        elif(infoEntered in infoList): 
            Settings["Settings"][stroption] = infoEntered
            break
        
    return Settings

#Tries detector
def triesCounter(tries):
    if(tries >= 5):
        return False
    return tries + 1

#Convert audio files from '.mp4' -> '.mp3'
def convertAudio(path, data):
    onlyfiles = [f for f in listdir(convertPath('Data/')) if isfile(join(convertPath('Data/'), f))]
    for file in onlyfiles:
        if('.mp4' in file):
            path = convertPath("Data/" + file)
            
    #Convert from '.mp4' -> '.mp3'
    videoClip = AudioFileClip(path[:-4].replace('.', '') + '.mp4')
    videoClip.write_audiofile(convertPath('Data/' + data['album']['artists'][0]['name'] + ' - ' + data['name'] + '.mp3'), verbose=False, logger=None)
    videoClip.close()
    
    #Deleting the old 'mp4' file
    os.remove(path[:-4].replace('.', '') + '.mp4')
    
    return convertPath('Data/' + data['album']['artists'][0]['name'] + ' - ' + data['name'] + '.mp3')

#XNOR logic gate
def XNOR(cond1, cond2):
    if((cond1 < 0) and (cond2 < 0)) or ((cond1 > 0) and (cond2 > 0)):
        return True
    else:
        return False
    
#Add not-found tracks to 'notFoundTracks.json' so later they can be recorded and uploaded to Youtube
def notFoundTracks(searchLink, data, platform, videoId=None):
    if(os.path.exists(convertPath('Data/notFoundTracks.json'))):
        notFoundFile = ReadFILE(convertPath('Data/notFoundTracks.json'))
        
    else:
        notFoundFile = {}
    
    if(data['id'] not in notFoundFile.keys()):
        notFoundFile[data["id"]] = {
            "Youtube Search Link": searchLink,
            "Spotify Track Link": data["external_urls"]["spotify"],
            "Video link": videoId,
            "Platform": platform
        }
    
        WriteJSON(convertPath('Data/notFoundTracks.json'), notFoundFile, 'w')

#Will convert a string with parenthese to a string without them
#Example "Invincible (feat. Joe Pringle)" -> "Invincible"
def removeExtras(string):
    if ('-' in string):
        string = string[:string.find('-')]
    return re.sub(r'\([\s\S]*\)', '', string).replace('"', "").replace("'", "").strip()