import time

#importing Spotipy
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

#importing systemFunctions
from SyncifyFunctions.systemFunctions import *

#Importing spotifyHandeler
from spotifyHandenler.requestsHandeling import *


setting_path = "Settings.json"
playlist_path = convertPath("Data/Playlists Informations.json")


#get the needed informations to fill up the Playlist JSON file
def getPlaylistInformation(syncifyToken, objId=""):
    if(isLinkAlbum(objId)):
        spotipyResult = album(syncifyToken, objId)
    else:
        spotipyResult = playlist(syncifyToken, objId)
        
    return spotipyResult
    
#Updates and Add Playlists from the Playlist JSON file
def RefreshPlaylistFile(syncifyToken):
    SyncifySettings = getDataJSON(setting_path, "Settings")
    
    playlistFile = ReadFILE(playlist_path)
    playlist_list = []
    for link in playlistFile["Playlists links"]:
        if(isLinkAlbum(link)):
            spotifyObjId = link[link.find("album/") + len("album/"):]
        else:
            spotifyObjId = link[link.find("playlist/") + len("playlist/"):]

        spotipyResult = getPlaylistInformation(syncifyToken, spotifyObjId)
        
        #Structure of the playlist
        playlist_list.append(
            {
                spotipyResult["name"] : {
                    "Image": spotipyResult["images"][0]["url"],
                    "Links": {
                        "URL": spotipyResult["external_urls"]["spotify"],
                        "ID": spotifyObjId
                    }
                }
            }
        )
    
    Playlists = ReadFILE(playlist_path)
    Playlists["Playlists Informations"] = playlist_list
    WriteJSON(playlist_path, Playlists, 'w')

#Create the playlist // supports m3a format
def CreatePlaylist(order):
    SavifySettings = getDataJSON(setting_path, "Settings")
    playlistPath = getDataJSON(setting_path, "Settings/Paths/Playlist")
    musicPath = getDataJSON(setting_path, "Settings/Paths/Downloads")
    
    fileName = convertPath(playlistPath + '/' + order["Name"] + ".m3u")
    with open(fileName, "w") as playlistm3a:
        playlistm3a.write("#EXTM3U\n#EXTIMG: \n")
        for line in order["Order"]:
            playlistm3a.write(musicPath + line + "\n")

#Manage .m3u playlists
def PlaylistManager(syncifyToken, playlist_id):
    SavifySettings = getDataJSON(setting_path, "Settings")
    downloadLocation = getDataJSON(setting_path, "Settings/Paths/Downloads")
    playlistList = playlist(syncifyToken, playlist_id)
    
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

def popAlbums():
    playlistInfos = ReadFILE(playlist_path)
    for element in playlistInfos["Playlists links"]:
        if("album" in element):
            playlistInfos["Playlists links"].remove(element)
    WriteJSON(playlist_path, playlistInfos, 'w')