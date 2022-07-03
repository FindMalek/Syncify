"""
    This module:
    Search and Download Audio from Youtube, using Youtube-DLL
"""

#Importing youtube DLL to download from youtube
import youtube_dl

#Import Syncify System Functions
from SyncifyFunctions.systemFunctions import *
import re
  
#Importing the request module from url library
import urllib.request

#Import Youtube from pytube
from pytube import YouTube 

#Needed paths
setting_path = "Settings.json"

#Search for video using the Spotify Data
#A good search algorithm, to get the exact track
def searchTrack(data):
    searchTitle = data['album']['artists'][0]['name'] + ' ' +  data['name'] + ' audio'
    html = urllib.request.urlopen("https://www.youtube.com/results?search_query=" + searchTitle.replace(" ", "_"))
    videoIds = re.findall(r"watch\?v=(\S{11})", html.read().decode())
    
    #Filtering videos by title
    counter = 0
    while(counter < len(videoIds)):
        titleElement = str(YouTube('https://www.youtube.com/watch?v=' + videoIds[counter]).title).lower()
        if((titleElement.find(data['album']['artists'][0]['name'].lower()) >= 0) and (titleElement.find(data['name'].lower()) >= 0)):
            counter += 1
        else:
            videoIds.remove(videoIds[counter])

    #Filtering videos by duration
    counter = 0
    while (counter < len(videoIds)):
        youtubeElement = YouTube('https://www.youtube.com/watch?v=' + videoIds[counter])
        if(youtubeElement.length in range(int(data["duration_ms"] / 1000) - getDataJSON(setting_path, "Settings/Time Difference"), int(data["duration_ms"] / 1000) + getDataJSON(setting_path, "Settings/Time Difference"))):
            counter += 1
        else:
            videoIds.remove(videoIds[counter])
    
    """ Add other filters in the future """
    
    if(len(videoIds) == 0):
        return None, False
    
    else:
        return videoIds, True

#Download track from youtube
#Change this with Pytube
def downloadTrack(url, data):
    videoInfo = youtube_dl.YoutubeDL().extract_info(url, download=False)
    options = {
        'format': 'bestaudio/best', 
        'keepvideo': False,
        'outtmpl': 'tmpAudio.mp3'
    }
    
    with youtube_dl.YoutubeDL(options) as yDL:
        yDL.download([videoInfo['webpage_url']])
        #yDL.download(convertPath("Data/" + [videoInfo['webpage_url']]))
        
    return "" #The path of the downloaded video

if __name__ == '__main__':
    data = ReadFILE('resTrStar.json')
    searchTrack(data)