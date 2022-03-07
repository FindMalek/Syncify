#importing Spotipy
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

#importing systemFunctions
from Functions.systemFunctions import *

setting_path = "Settings.json"
playlist_path = convertPath("Data/Playlists Informations.json")

#Log in Spotipy_Session
def SpotipySession():
    client_credentials_manager = SpotifyClientCredentials()#Spotify Client
    return spotipy.Spotify(client_credentials_manager = client_credentials_manager)

Spotipy_Session = SpotipySession()

#get the needed informations to fill up the Playlist JSON file
def getPlaylistInformation(Spotipy_Session, toGet, link, playlist_ID=""):
    if(toGet == "ID"):
        if(isLinkAlbum(link)):
            return "spotify:album:" + link[link.find("album/") + len("album/"):]
        else:
            return "spotify:playlist:" + link[link.find("playlist/") + len("playlist/"):]
    
    if(isLinkAlbum(link)):
        spotipyResult = Spotipy_Session.album(link[link.find("album/") + len("album/"):])
    else:
        spotipyResult = Spotipy_Session.playlist(playlist_ID)
    
    if(toGet == "Name"):
        return spotipyResult["name"]
    elif(toGet == "Image URL"):
        return spotipyResult["images"][0]["url"]
    elif(toGet == "Playlist URL"):
        return spotipyResult["external_urls"]["spotify"]
    
#Updates and Add Playlists from the Playlist JSON file
def RefreshPlaylistFile(Spotipy_Session):
    SyncifySettings = getDataJSON(setting_path, "Settings")
    
    playlistFile = ReadFILE(playlist_path)
    playlist_list = []
    for link in playlistFile["Playlists links"]:
        playlist_ID = getPlaylistInformation(Spotipy_Session, "ID", link)
        playlist_Name = getPlaylistInformation(Spotipy_Session, "Name", link, playlist_ID)
        playlist_Image = getPlaylistInformation(Spotipy_Session, "Image URL", link, playlist_ID)
        playlist_URL = getPlaylistInformation(Spotipy_Session, "Playlist URL", link, playlist_ID)

        #Structure of the 
        playlist_list.append(
            {
                playlist_Name : {
                    "Image": playlist_Image,
                    "Links": {
                        "URL": playlist_URL,
                        "ID": playlist_ID
                    }
                }
            }
        )
    
    Playlists = ReadFILE(playlist_path)
    Playlists["Playlists Informations"] = playlist_list
    WriteJSON(playlist_path, Playlists, 'w')

#Create the playlist // supports m3a and m3u8 formats
def CreatePlaylist(order):
    SavifySettings = getDataJSON(setting_path, "Settings")
    playlistPath = getDataJSON(setting_path, "Settings/Paths/Playlist")
    musicPath = getDataJSON(setting_path, "Settings/Paths/Downloads")
    
    fileName = convertPath(playlistPath + order["Name"] + ".m3u")
    with open(fileName, "w") as playlistm3a:
        playlistm3a.write("#EXTM3U\n#EXTIMG: \n")
        for line in order["Order"]:
            playlistm3a.write(musicPath + line + "\n")


#Manage .m3u playlists
def PlaylistManager(Spotipy_Session, playlist_id):
    SavifySettings = getDataJSON(setting_path, "Settings")
    downloadLocation = getDataJSON(setting_path, "Settings/Paths/Downloads")
    playlist = Spotipy_Session.playlist(playlist_id)
    
    pl_order = {"Name": playlist["name"], "Order": []}
    
    for track in playlist["tracks"]["items"]:
        songLocation = convertPath(
            track["track"]["artists"][0]["name"] + ' - ' +
            track["track"]["name"] + '.' +
            SavifySettings["Format"].lower()
        )
        pl_order["Order"].append(track["track"]["album"]["name"] + "*" + songLocation)
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