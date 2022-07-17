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
    
    logsSyncify.debug("(Regex): Searching began for Video Ids...")
    videoIds = re.findall(r"watch\?v=(\S{11})", html.read().decode())[:getDataJSON(setting_path, "Settings/Search Accuracy")]
    logsSyncify.debug(f"(Regex): Found {len(videoIds)} Video Id.")

    """
        New : Search for the most viewed video Id, while searching with the title filter and duration filter.
        for maximum efficiency. 
    """

    #Filtering videos by title -> duration -> views
    """ Add other filters in the future """
    logsSyncify.debug(f"(Filtering): Started with {len(videoIds)} Video Id...")
    counter, mostViews = 0, 0
    while(counter < len(videoIds)):
        youtubeElement = YouTube('https://www.youtube.com/watch?v=' + videoIds[counter])
        if((str(youtubeElement.title).lower().find(data['album']['artists'][0]['name'].lower()) >= 0) and (str(youtubeElement.title).lower().find(data['name'].lower()) >= 0)):
            logsSyncify.debug(f"(Filtering): Filter by Title - Video ID {videoIds[counter]} approved.")
            
            if(youtubeElement.length in range(int(data["duration_ms"] / 1000) - getDataJSON(setting_path, "Settings/Time Difference"), int(data["duration_ms"] / 1000) + getDataJSON(setting_path, "Settings/Time Difference"))):
                logsSyncify.debug(f"(Filtering): Filter by Duration - Video ID {videoIds[counter]} approved.")

                if(youtubeElement.views > mostViews):
                    logsSyncify.debug(f"(Filtering): Filter by Most Views - Video ID {videoIds[counter]} approved.")
                    mostViewedId = videoIds[counter]
                counter += 1
                
            else:
                videoIds.remove(videoIds[counter])
            
        else:
            videoIds.remove(videoIds[counter])
            
    logsSyncify.debug(f"(Filtering): Result with {len(videoIds)} Video Id.")
    
    if(len(videoIds) == 0):
        logsSyncify.warning("(Filtering): Couldn't find any Video with the specific filter. 'spotifyDownloader' will resume...")
        """
            In the future send the 'data' to a server to download it using the module 'spotifyDownloader' 
        and upload it on Youtube to help the 'Syncify' community.
        """
        """ Use the 'spotifyDownloader' when it's finished. """
        return False
    
    else:   
        return mostViewedId

#Download track from youtube
def downloadTrack(videoId):
    pytubeElement = YouTube('https://www.youtube.com/watch?v=' + videoId)
    availableAudios = pytubeElement.streams.get_by_itag(140)
    availableAudios.download(convertPath('Data/'))
    
    return convertPath('Data/' + pytubeElement.title + '.mp4')