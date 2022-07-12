"""
    This module:
    Search and Download Audio from Youtube, using Youtube-DLL
"""

#Import Syncify System Functions
from SyncifyFunctions.systemFunctions import *
import re
  
#Importing the request module from url library
import urllib.request

#Import Youtube from pytube
from pytube import YouTube 

#Needed paths
setting_path = "Settings.json"

#Returns if video exists in Youtube or not from the output of the function searchTrack
def trackInYoutube(searchTrack):
    if(searchTrack == False):
        return searchTrack
    else:
        return True

#Search for video using the Spotify Data
#A good search algorithm, to get the exact track
def searchTrack(data):
    """ The algorithm is still weak, it must be improved in the next updates... """
    
    searchTitle = data['album']['artists'][0]['name'] + ' ' +  data['name'] + ' audio'
    html = urllib.request.urlopen("https://www.youtube.com/results?search_query=" + searchTitle.replace(" ", "_"))
    videoIds = re.findall(r"watch\?v=(\S{11})", html.read().decode())[:11]
    
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
    while(counter < len(videoIds)):
        youtubeElement = YouTube('https://www.youtube.com/watch?v=' + videoIds[counter])
        if(youtubeElement.length in range(int(data["duration_ms"] / 1000) - getDataJSON(setting_path, "Settings/Time Difference"), int(data["duration_ms"] / 1000) + getDataJSON(setting_path, "Settings/Time Difference"))):
            counter += 1
        else:
            videoIds.remove(videoIds[counter])

    """ Add other filters in the future """
    
    if(len(videoIds) == 0):
        """
            In the future send the 'data' to a server to download it using the module 'spotifyDownloader' 
        and upload it on Youtube to help the 'Syncify' community.
        """
        """ Use the 'spotifyDownloader' when it's finished. """
        return False
    
    else:
        #Filtering videos by most reliable using views count
        mostViewsId = videoIds[0]
        mostViewsElement =  YouTube('https://www.youtube.com/watch?v=' + mostViewsId)
        for videoId in videoIds:
            if(YouTube('https://www.youtube.com/watch?v=' + videoId).views > mostViewsElement.views):
                mostViewsId = videoId
                
        return mostViewsId

#Download track from youtube
def downloadTrack(videoId):
    pytubeElement = YouTube('https://www.youtube.com/watch?v=' + videoId)
    trackName = pytubeElement.title
    availableAudios = pytubeElement.streams.get_by_itag(140)
    availableAudios.download(convertPath('Data/'))
    
    return convertPath('Data/' + trackName + '.mp4')