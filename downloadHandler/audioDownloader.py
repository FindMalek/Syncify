"""
    This module:
    Search and Download Audio from Youtube, Yewtube and Spotify.
    It uses 'youtubeDownloader', 'yewtubeDownloader' and 'spotifyDownloader'.
    And soon enough, I will implement Soundcloud and Deezer.
"""

#Import Syncify System Functions
from SyncifyFunctions.systemFunctions import *
from SyncifyFunctions.trackHandeling import isDownloaded

#Importing Youtube Downloader
from downloadHandler.youtubeDownloader import *

#Importing Yewtube Downloader
from downloadHandler.yewtubeDownloader import *

#Importing Spotify Downloader
from downloadHandler.spotifyDownloader import *

#Importing Audio Manager
from downloadHandler.audioManager import *

#Needed paths
setting_path = "Settings.json"

#Search for video using the Spotify Data
#A good search algorithm, to get the exact track
def algorithmSearchTrack(data):    
    logsSyncify.debug(f"(Youtube/Request) - Searching for {data['uri']}...\n'youtubeDownloader' will search and download the track if found.")
    youtubeSearchResult = youtubeSearchTrack(data)
    logsSyncify.debug(f"(Youtube/Request) - Response recieved about the search request of {data['uri']}.")

    if(youtubeSearchResult[0] == True):
        return {"From": "Youtube", "Result": youtubeSearchResult}
    
    elif((youtubeSearchResult[0] == False) and (youtubeSearchResult[1] == "Yewtube")):
        logsSyncify.warning(f"(Yewtube/Request) - Skipping, module is not complete yet...")
        #logsSyncify.debug(f"(Yewtube/Request) - Searching for {data['uri']}...\n'yewtubeDownloader' will search and download the track if found.")
        """ Use the 'yewtubeDownloader' when it's finished. """
        return {"From": "Yewtube", "Result": [False, None]}
    
    elif((youtubeSearchResult[0] == False) and (youtubeSearchResult[1] == "Spotify")):
        logsSyncify.warning(f"(Spotify/Request) - Skipping, module is not complete yet...")
        #logsSyncify.debug(f"(Spotify/Request) - Searching for {data['uri']}...\n'spotifyDownloader' will search and download the track if found.")
        """ Use the 'spotifyDownloader' when it's finished. """
        return {"From": "Spotify", "Result": [False, None]}

#Checks if a track is already downloaded or not using the track data
def trackDownloaded(data):
    if(isDownloaded(data['album']['artists'][0]['name'] + ' - ' + data['name'] + '.mp3')):
        return True
    else:
        return False

#Download Tracks from the specified Platform, The main function that changes the metadata of the track and move the track to it's destination
def downloadTrack(searchResult, trackData):
    
    if(searchResult["From"] == "Youtube"):
        logsSyncify.debug(f"(Youtube/Download) - {trackData['uri']} exists in ID: {searchResult['Result'][1]} and downloading is about to start...")
        trackPath = youtubeDownloadTrack(searchResult["Result"][1])
        logsSyncify.debug(f"(Youtube/Download) - {trackData['uri']} is downloaded in {trackPath}.")
    
    elif(searchResult["From"] == "Yewtube"):
        pass
    
    elif(searchResult["From"] == "Spotify"):
        pass
    
    trackPath = changeMetaData(trackPath, trackData)
    
    logsSyncify.debug(f"Moving {trackPath} to {download_path}...")
    moveTrack(trackData)
    logsSyncify.debug(f"Moved {trackPath} to {download_path}.")