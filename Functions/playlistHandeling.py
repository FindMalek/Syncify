#importing Spotipy
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

#importing systemFunctions
from Functions.systemFunctions import getDataJSON, ReadFILE, WriteJSON, convertPath

setting_path = "Settings.json"
playlist_path = convertPath("Data/Playlist links.json")

#Log in Spotipy_Session
def SpotipySession():
    client_credentials_manager = SpotifyClientCredentials()#Spotify Client
    return spotipy.Spotify(client_credentials_manager = client_credentials_manager)

Spotipy_Session = SpotipySession()

#get the needed informations to fill up the Playlist JSON file
def getPlaylistInformation(Spotipy_Session, toGet, link, playlist_ID=""):
    if(toGet == "ID"):
        return "spotify:playlist:" + link[link.find("playlist/") + len("playlist/"):]
    
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

#Create the playlist
def CreatePlaylist(order):
    SavifySettings = getDataJSON(setting_path, "Settings")
    playlistPath = getDataJSON(setting_path, "Settings/Paths/Playlist")
    
    fileName = convertPath(playlistPath + "/" + order["Name"] + ".m3u")
    with open(fileName, "w") as playlistm3a:
        playlistm3a.write("#EXTM3U\n")
        for line in order["Order"]:
            playlistm3a.write(line + "\n")

    
#Manage .m3u playlists
def PlaylistManager(Spotipy_Session, playlist_id):
    SavifySettings = getDataJSON(setting_path, "Settings")
    downloadLocation = getDataJSON(setting_path, "Settings/Paths/Downloads")
    playlist = Spotipy_Session.playlist(playlist_id)
    
    pl_order = {"Name": playlist["name"], "Order": []}
    for i in range(0, len(playlist["tracks"]["items"])):
        songLocation = convertPath(str(downloadLocation)+ "/"
                                 + playlist["tracks"]["items"][i]["track"]["artists"][0]["name"]
                                 + ' - ' + playlist["tracks"]["items"][i]["track"]["name"] +
                                 '.' + SavifySettings["Format"].lower())
        pl_order["Order"].append(songLocation)
    return pl_order     