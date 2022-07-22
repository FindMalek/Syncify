import time

#importing systemFunctions
from SyncifyFunctions.systemFunctions import *

#Importing spotifyHandeler
from spotifyHandler.requestsHandeling import *


setting_path = "Settings.json"
userdata_path = convertPath("Data/userData.json")


#get the needed informations to fill up the Playlist / Album / Track JSON file
def getObjectInformation(syncifyToken, objLink):
    if(whatIsLink(objLink) == "Album"):
        spotifyObjId = objLink[objLink.find("album/") + len("album/"):]
        
        tries = 0
        while True:
            try:
                spotifyResult = album(syncifyToken, spotifyObjId)
                break
            except Exception:
                logsSyncify.warning(f"({tries}) Error -> Couldn't get result of {spotifyObjId}. Sleeping for {getDataJSON(setting_path, 'Settings/Sleep')}")
                
                tries = triesCounter(tries)
                if(tries == False):
                    logsSyncify.critical(f"Number of tries exceeded 5. Quitting")
                    quit()
                    
                time.sleep(getDataJSON("Settings.json", "Settings/Sleep"))
        
    elif(whatIsLink(objLink) == "Playlist"):
        spotifyObjId = objLink[objLink.find("playlist/") + len("playlist/"):]
        
        tries = 0
        while True:
            try:
                spotifyResult = playlist(syncifyToken, spotifyObjId)
                break
            except Exception:
                logsSyncify.warning(f"({tries}) Error -> Couldn't get result of {spotifyObjId}. Sleeping for {getDataJSON(setting_path, 'Settings/Sleep')}")
                
                tries = triesCounter(tries)
                if(tries == False):
                    logsSyncify.critical(f"Number of tries exceeded 5. Quitting")
                    quit()
                    
                time.sleep(getDataJSON("Settings.json", "Settings/Sleep"))
    
    elif(whatIsLink(objLink) == "Track"):
        spotifyObjId = objLink[objLink.find("track/") + len("track/"):]
        
        tries = 0
        while True:
            try:
                spotifyResult = track(syncifyToken, spotifyObjId)
                break
            except Exception:
                logsSyncify.warning(f"({tries}) Error -> Couldn't get result of {spotifyObjId}. Sleeping for {getDataJSON(setting_path, 'Settings/Sleep')}")
                
                tries = triesCounter(tries)
                if(tries == False):
                    logsSyncify.critical(f"Number of tries exceeded 5. Quitting")
                    quit()
                    
                time.sleep(getDataJSON("Settings.json", "Settings/Sleep"))
    
    return spotifyResult, spotifyObjId

#Create the playlist // supports m3a format
def CreatePlaylist(order):
    downloadPath = getDataJSON(setting_path, "Settings/Paths/Downloads")
    
    fileName = convertPath(getDataJSON(setting_path, "Settings/Paths/Playlist") + '/' + order["Name"] + ".m3u")
    with open(fileName, "w", encoding='utf-8') as playlistm3a:
        playlistm3a.write("#EXTM3U\n#EXTIMG: \n")
        for line in order["Order"]:
            playlistm3a.write(convertPath(downloadPath + '/' + line + "\n"))
    
#Manage .m3u playlists
def PlaylistManager(syncifyToken, playlistId, playlistURL):
    SavifySettings = getDataJSON(setting_path, "Settings")
    downloadLocation = getDataJSON(setting_path, "Settings/Paths/Downloads")
    playlistList = playlist(syncifyToken, playlistId)
    
    pl_order = {
                    "Name": playlistList["name"],
                    "Order": []
            }
    
    #ALBUM*TRACKLOCATION+TrackName
    for track in playlistList["tracks"]["items"]:
        trackName = (
                    track["track"]["artists"][0]["name"] + ' - ' +
                    track["track"]["name"] + '.' +
                    SavifySettings["Format"].lower()
                )
            
        pl_order["Order"].append(track["track"]["album"]["name"] + "*" + trackName)
    
    #TRACKLOCATION+TrackName
    pl_order["Order"] = sorted(pl_order["Order"])
    for i in range(0, len(pl_order["Order"])):
        pl_order["Order"][i] = pl_order["Order"][i][pl_order["Order"][i].find("*") + 1:]
        
    return pl_order   

#Deleting Albums / Tracks from "userdata.json" to optimize the speed of the execution
def popTmpObject():
    userdata = ReadFILE(userdata_path)
    for element in userdata["Albums"]:
        userdata["Albums"].remove(element)
    for element in userdata["Tracks"]:
        userdata["Tracks"].remove(element)
    WriteJSON(userdata_path, userdata, 'w')
    
if __name__ == '__main__':
    #Setting up the logging configuration
    logsSyncify.loggingSetup()