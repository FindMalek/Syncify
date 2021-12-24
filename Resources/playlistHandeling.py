#importing Spotipy
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

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