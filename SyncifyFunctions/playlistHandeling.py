import time

#importing Spotipy
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

#importing systemFunctions
from SyncifyFunctions.systemFunctions import *

#Importing spotifyHandeler
from spotifyHandler.requestsHandeling import *


setting_path = "Settings.json"
playlist_path = convertPath("Data/Playlists Informations.json")


#get the needed informations to fill up the Playlist / Album JSON file
def getObjectInformation(syncifyToken, objLink):
    if(isLinkAlbum(objLink)):
        spotifyObjId = objLink[objLink.find("album/") + len("album/"):]
        
        tries = 0
        while True:
            try:
                spotipyResult = album(syncifyToken, spotifyObjId)
                break
            except Exception:
                logMessage.Syncify(f"({nbTries}) Error -> Couldn't get result of {spotifyObjId}. Sleeping for {getDataJSON(setting_path, 'Settings/Sleep')}").warning()
                
                tries = triesCounter(tries)
                if(tries == True):
                    logsSyncify.Syncify(f"Number of tries exceeded 5. Quitting").critical()
                    quit()
                    
                time.sleep(getDataJSON("Settings.json", "Settings/Sleep"))
        
    elif(isLinkAlbum(objLink) == False):
        spotifyObjId = objLink[objLink.find("playlist/") + len("playlist/"):]
        
        tries = 0
        while True:
            try:
                spotipyResult = playlist(syncifyToken, spotifyObjId)
                break
            except Exception:
                logMessage.Syncify(f"({nbTries}) Error -> Couldn't get result of {spotifyObjId}. Sleeping for {getDataJSON(setting_path, 'Settings/Sleep')}").warning()
                
                tries = triesCounter(tries)
                if(tries == True):
                    logsSyncify.Syncify(f"Number of tries exceeded 5. Quitting").critical()
                    quit()
                    
                time.sleep(getDataJSON("Settings.json", "Settings/Sleep"))
        
    return spotipyResult, spotifyObjId
    
#Updates and Add Playlists from the Playlist JSON file
def RefreshPlaylistFile(syncifyToken):
    SyncifySettings = getDataJSON(setting_path, "Settings")
    
    objectFile = ReadFILE(playlist_path)
    Objectlist = []
    for link in objectFile["Playlists links"]:
        objectResult = getObjectInformation(syncifyToken, link)
        
        #Structure of the playlist
        Objectlist.append(
            {
                objectResult[0]["name"] : {
                    "Image": objectResult[0]["images"][0]["url"],
                    "Links": {
                        "URL": objectResult[0]["external_urls"]["spotify"],
                        "ID": objectResult[1]
                    }
                }
            }
        )
        logsSyncify.Syncify(f"Added {link} to {playlist_path}").debug()
    
    Objects = ReadFILE(playlist_path)
    Objects["Playlists Informations"] = Objectlist
    WriteJSON(playlist_path, Objects, 'w')

#Create the playlist // supports m3a format
def CreatePlaylist(order):
    downloadPath = getDataJSON(setting_path, "Settings/Paths/Downloads")
    
    fileName = convertPath(getDataJSON(setting_path, "Settings/Paths/Playlist") + '/' + order["Name"] + ".m3u")
    with open(fileName, "w") as playlistm3a:
        playlistm3a.write("#EXTM3U\n#EXTIMG: \n")
        for line in order["Order"]:
            playlistm3a.write(downloadPath + line + "\n")
    
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

#Deleting Albums from "Playlist Information.json" to optimize the speed of the execution
def popAlbums():
    playlistInfos = ReadFILE(playlist_path)
    for element in playlistInfos["Playlists links"]:
        if("album" in element):
            playlistInfos["Playlists links"].remove(element)
    WriteJSON(playlist_path, playlistInfos, 'w')
    
if __name__ == '__main__':
    #Setting up the logging configuration
    logsSyncify("").loggingSetup()