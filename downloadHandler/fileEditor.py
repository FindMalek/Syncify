"""
    This module replaces FFMPEG.
    It uses the 'youtubeDownloader' to download and changes the metadata of
    the downloaded track using 'music_tag' and then move it to it's destination
"""

#Importing the module Music-Tag to change the metadata of the audio tracks
import music_tag

#Importing the Syncify Youtube Downloader
from downloadHandler.youtubeDownloader import *

#Importing the Syncify System Functions
import os
from SyncifyFunctions.systemFunctions import *

#Importy getArtist function from trackHandeling
from SyncifyFunctions.trackHandeling import getArtists

#Importing requestHandeling to download the art of the track
from spotifyHandler.requestHandeling import downloadArt


#Pre-defined path
setting_path = "Settings.json"
download_path = getDataJSON(setting_path, "Settings/Paths/Downloads")
tmpTracks = convertPath(os.path.abspath(os.getcwd()) + "Data/")


#Changes all of the metadata of the track
def changeMetaData(path, data):
    audioFile = music_tag.load_file(path)
    audioFile['tracktitle'] = data['name']
    audioFile['artist'] = getArtists(data)
    audioFile['album'] = data['album']['name']
    audioFile['tracknumber'] = data['track_number']
    audioFile['totaltracks'] = data['album']['total_tracks']
    audioFile['discnumber'] = data['disc_number']
    audioFile['year'] = data['album']['release_date'][:4]
    audioFile['isrc'] = data['external_ids']['isrc']
    
    artPath = downloadArt(data['album']['images'][0]['url'])
    with open(artPath, 'rb') as img:
        audioFile['artwork'] = img.read()
    
    #Set the artwork
    audioFile.save()
    
    #Delete the tmpArt
    os.remove(artPath)
    
#Move the track from /tmp/ to the destination
def moveTrack(des, currPath):
    pass

#The main function that changes the metadata of the track and move the track to it's destination
def downloaderViaYoutube(trackData):
    if((trackInYoutube(trackData) == True) and (trackDownloaded(trackData) == False)):
        trackPath = downloadTrack(trackData)
        
        changeMetaData(trackPath, trackData)
        moveTrack(destinationPath, trackPath)
        
    elif((trackInYoutube(trackData) == False) and (trackDownloaded(trackData) == False)):
        #use the spotifyDownloader or raise an error for now
        pass
    
    else:
        #Track is already downloaded
        pass