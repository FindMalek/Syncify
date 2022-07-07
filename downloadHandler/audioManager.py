"""
    This module replaces FFMPEG.
    It uses the 'youtubeDownloader' to download and changes the metadata of
    the downloaded track using 'music_tag' and then move it to it's destination
"""

#Importing the module mutagen to change the metadata of the audio tracks
import mutagen
from mutagen.id3 import ID3, APIC
from mutagen.easyid3 import EasyID3

#Importing the Syncify Youtube Downloader
from downloadHandler.youtubeDownloader import *

#Importing the Syncify System Functions
import os
from SyncifyFunctions.systemFunctions import *

#Import getArtist and isDownloaded function from trackHandeling
from SyncifyFunctions.trackHandeling import getArtists, isDownloaded

#Importing requestHandeling to download the art of the track
from spotifyHandler.requestsHandeling import downloadArt


#Pre-defined path
setting_path = "Settings.json"
download_path = getDataJSON(setting_path, "Settings/Paths/Downloads")
tmpTracks = convertPath("Data/" + os.path.abspath(os.getcwd()))


#Changes all of the metadata of the track
def changeMetaData(path, data):
    #Convert the extension and change the name
    logsSyncify("").Syncify(f"Converting {path} to MP3 file...").debug()
    path = convertAudio(path, data)
    logsSyncify("").Syncify(f"Converted and renamed {path} to MP3 file.").debug()
    
    #Change the meta-data
    logsSyncify("").Syncify(f"Updating the metadata of {path}...").debug()
    """ Fix : Its not updating the values """
    try:
        audioFile = EasyID3(path)
    except mutagen.id3.ID3NoHeaderError:
        audioFile = mutagen.File(path, easy=True)
        audioFile.add_tags()
        
    audioFile['title'] = data['name']
    audioFile['artist'] = getArtists(data)
    audioFile['album'] = data['album']['name']
    audioFile['tracknumber'] = str(data['track_number'])
    audioFile['discnumber'] = str(data['disc_number'])
    audioFile['date'] = data['album']['release_date']
    """
    Coming soon : Genre
    audioFile['genre'] = ""
    """
    audioFile.save()
    logsSyncify("").Syncify(f"Updated he metadata of {path}.").debug()
    
    """ Fix : Set Artwork"""
    
    #Set artwork
    artPath = downloadArt(data['album']['images'][0]['url'])
    audioFile = ID3(path)
    with open(artPath, 'rb') as albumart:
        audioFile['APIC'] = APIC(
                        encoding=3,
                        mime='image/jpeg',
                        type=3, desc=u'Cover',
                        data=albumart.read()
                        )
    audioFile.save()
    
    #Delete the tmpArt
    os.remove(artPath)
    
    return path
    
#Move the track from /tmp/ to the destination
def moveTrack(currPath, des):
    pass

#Checks if a track is already downloaded or not using the track data
def trackDownloaded(data):
    if(isDownloaded(data['album']['artists'][0]['name'] + ' - ' + data['name'])):
        return True
    else:
        return False

#The main function that changes the metadata of the track and move the track to it's destination
def downloadSyncify(trackData):
    searchTrachData = searchTrack(trackData)
    
    if((trackInYoutube(searchTrachData) == True) and (trackDownloaded(trackData) == False)):
        trackPath = downloadTrack(searchTrachData)
        
        trackPath = changeMetaData(trackPath, trackData)
        #moveTrack(trackPath, destinationPath)
        
    elif((trackInYoutube(searchTrachData) == False) and (trackDownloaded(trackData) == False)):
        #use the spotifyDownloader or raise an error for now
        pass
    
    else:
        #Track is already downloaded
        pass