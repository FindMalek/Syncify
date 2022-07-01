"""
    This module:
    Download Audio from Youtube
"""

#Importing youtube DLL to download from youtube
import youtube_dl

#Import Syncify System Functions
from SyncifyFunctions.systemFunctions import *


#Check if the track exists in Youtube
def trackInYoutube(data):
    return True

#Search for video using the Spotify Data
def searchTrack(data):
    pass

#Download track from youtube
def downloadTrack(url, data):
    videoInfo = youtube_dl.YoutubeDL().extract_info(url, download=False)
    options = {
        'format': '',
        'keepvideo': False,
        'outtmpl': 'tmpAudio.mp3'
    }
    
    with youtube_dl.YoutubeDL(options) as yDL:
        yDL.download([videoInfo['webpage_url']])
        
    return ""