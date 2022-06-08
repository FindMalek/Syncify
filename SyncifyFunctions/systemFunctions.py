import json, os, shutil, platform, sys, logging, re
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
    
#Logging class that prints and also logs
class logsSyncify: 
    def __init__(self, infos):
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
        
    #Print the message simply, without logging it
    def message(self, msg):
        print(msg) 
    
    #Remove '\n' and '\t' from the message
    def removeNewLines(self, msg):
        while('\n' in msg) or ('\t' in msg):
            msg = msg.strip()
            msg = re.sub('\s+', ' ', msg)
        return msg
               
    #Savify class
    class Savify:
        def __init__(self, msg):
            self.module = "Savify"
            self.orgMsg = msg
            self.msg = logsSyncify.removeNewLines(self, msg)
            
        def info(self):
            print(self.orgMsg)
            logging.info(f'({self.module}): {self.msg}')
        def debug(self):
            logging.debug(f'({self.module}): {self.msg}')
        def warning(self):
            logging.warning(f'({self.module}): {self.msg}')
        def critical(self):
            print(f'(CRITICAL) -> ({self.module}): {self.msg}')
            logging.critical(f'({self.module}): {self.msg}')

    class Syncify:
        def __init__(self, msg):
            self.module = "Syncify"
            self.orgMsg = msg
            self.msg = logsSyncify.removeNewLines(self, msg)
            
        def info(self):
            print(self.orgMsg)
            logging.info(f'({self.module}): {self.msg}')
        def debug(self):
            logging.debug(f'({self.module}): {self.msg}')
        def warning(self):
            logging.warning(f'({self.module}): {self.msg}')
        def critical(self):
            print(f'(CRITICAL) -> ({self.module}): {self.msg}')
            logging.critical(f'({self.module}): {self.msg}')
            
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
        "Playlists": [],
        "Albums" : [],
        "Tracks": []
    }
    onlyfiles = [f for f in listdir(convertPath(currentPath + "Data/")) if isfile(join(convertPath(currentPath + "Data/"), f))]
    if("userData.json" not in onlyfiles):
        WriteJSON(convertPath(currentPath + "Data/userData.json") , playlistInformations, 'w')
    
    #Setting up the logging configuration
    logsSyncify("").loggingSetup()
    
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
        logsSyncify.Syncify(f"Deleted {convertPath(path + '/tmp/')}").debug()

    except OSError:
        pass
    
    try:
        os.remove(convertPath(path + '/.cache'))
        logsSyncify.Syncify(f"Deleted {convertPath(path + '/.cache')}").debug()

    except OSError:
        pass  
    
    try:
        shutil.rmtree(convertPath(path + '/SyncifyFunctions/__pycache__'))
        logsSyncify.Syncify(f"Deleted {convertPath(path + '/SyncifyFunctions/__pycache__')}").debug()

    except:
        pass
    
    try:
        shutil.rmtree(convertPath(path + '/spotifyHandler/__pycache__'))
        logsSyncify.Syncify(f"Deleted {convertPath(path + '/spotifyHandler/__pycache__')}").debug()

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

#Download settings
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

    logsSyncify("").Syncify(f"Quality -> {qual}. Format -> {SavifySettings['Format'].lower()}").debug()
    return qual, SavifySettings["Format"].lower()

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
    if(tries > 5):
        return True
    return tries + 1