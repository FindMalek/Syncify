"""
    This module replaces FFMPEG.
    It uses the 'youtubeDownloader', 'yewtubeDownloader' and 'spotifyDownloader' to
    download and changes the metadata of the downloaded track using 'mutagen'
    and then move it to it's destination
"""

#Importing the module mutagen to change the metadata of the audio tracks
import mutagen
from mutagen.id3 import ID3, APIC
from mutagen.easyid3 import EasyID3

#Importing the Syncify System Functions
import os, shutil
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
    logsSyncify.debug(f"Converting {path} to MP3 file...")
    path = convertAudio(path, data)
    logsSyncify.debug(f"Converted and renamed {path} to MP3 file.")
    
    #Change the meta-data
    logsSyncify.debug(f"Updating the metadata of {path}...")
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
    logsSyncify.debug(f"Updated he metadata of {path}.")
    
    logsSyncify.debug(f"Setting the artwork of {path}...")
    logsSyncify.debug(f"Downloaded the artwork of {path}...")
    artPath = downloadArt(data['album']['images'][0]['url'])
    logsSyncify.debug(f"Downloaded the artwork of {path}...")
    
    audioFile = ID3(path)
    artCover = open(artPath, 'rb').read()
    audioFile.add(APIC(3, 'image/jpeg', 3, 'Front cover', artCover))
          
    audioFile.save(v2_version=3)
    logsSyncify.debug(f"Art work is set of {path}.")
    
    #Delete the tmpArt
    os.remove(artPath)
    
    return path
    
#Move the track from /tmp/ to the destination
def moveTrack(trackData):
    onlyfiles = [f for f in listdir(convertPath("Data/")) if isfile(join(convertPath("Data/"), f))]
    for file in onlyfiles:
        if('.mp3' in file):
            currPath = convertPath("Data/" + file)
    destiPath = convertPath(download_path + '/' + trackData['album']['artists'][0]['name'] + ' - ' +  trackData['name'] + '.mp3')
    shutil.move(currPath, destiPath)