"""
    This module, searchs and downloads tracks from 'Youtube'
    using 'pytube' and 'Youtube-DLL'
"""

#Import Syncify System Functions
from SyncifyFunctions.systemFunctions import *
import re, time, codecs

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
    
#Searchs for the track, using Spotify Data
def youtubeSearchTrack(data):
    """ The algorithm is good now, but it always can get a little better. I'll always be improving the search algorithm... """

    searchTitle = data['album']['artists'][0]['name'].replace(" ", "+") + '+-+' +  data['name'].replace(" ", "+") + '+-+audio'
    tries = 0
    while True:
        try:
            html = urllib.request.urlopen("https://www.youtube.com/results?search_query=" + searchTitle.replace(' ', '+'))
            logsSyncify.debug(f"Requesting {'https://www.youtube.com/results?search_query=' + searchTitle.replace(' ', '+')}.")
            break
        except Exception:
            searchTitle = urllib.parse.quote(data['album']['artists'][0]['name'].replace(" ", "+") + '+-+' +  data['name'].replace(" ", "+") + '+-+audio')
            
            logsSyncify.warning(f"({tries}) Error -> Couldn't Request {'https://www.youtube.com/results?search_query=' + searchTitle.replace(' ', '+')}. Sleeping for {getDataJSON(setting_path, 'Settings/Sleep')}")
            tries = triesCounter(tries)
            if(tries == False):
                logsSyncify.critical(f"Number of tries exceeded 5. Quitting.")
                quit()
            time.sleep(getDataJSON("Settings.json", "Settings/Sleep"))

    logsSyncify.debug("(Youtube/Regex): Searching began for Video Ids...")
    videoIds = [*set(re.findall(r"watch\?v=(\S{11})", html.read().decode())[:getDataJSON(setting_path, "Settings/Search Accuracy")])]
    logsSyncify.debug(f"(Youtube/Regex): Found {len(videoIds)} Video Ids : {videoIds} .")

    #Filtering videos by title -> duration -> views
    """ Add other filters in the future """
    logsSyncify.debug(f"(Youtube/Filtering): Started with {len(videoIds)} Video Id...")
    counter, mostViews = 0, 0
    while(counter < len(videoIds)):
        youtubeElement = YouTube('https://www.youtube.com/watch?v=' + videoIds[counter])

        if((str(youtubeElement.title).lower().find(data['album']['artists'][0]['name'].lower()) >= 0) or (str(youtubeElement.author).lower().find(data['album']['artists'][0]['name'].lower()) >= 0)) and (str(youtubeElement.title).lower().find(data['name'].lower()) >= 0) and XNOR(str(youtubeElement.title).lower().find('acoustic'), data['name'].lower().find('acoustic')):
            logsSyncify.debug(f"(Youtube/Filtering): Filter by Title - Video link {'https://www.youtube.com/watch?v=' + videoIds[counter]} approved.")
            
            if(youtubeElement.length in range(int(data["duration_ms"] / 1000) - getDataJSON(setting_path, "Settings/Time Difference"), int(data["duration_ms"] / 1000) + getDataJSON(setting_path, "Settings/Time Difference"))):
                logsSyncify.debug(f"(Youtube/Filtering): Filter by Duration - Video link {'https://www.youtube.com/watch?v=' + videoIds[counter]} approved.")

                if(youtubeElement.views > mostViews):
                    logsSyncify.debug(f"(Youtube/Filtering): Filter by Most Views - Video link {'https://www.youtube.com/watch?v=' + videoIds[counter]} approved.")
                    mostViewedDict, mostViews = {"Video ID": videoIds[counter], "Age Restriction": youtubeElement.age_restricted}, youtubeElement.views
                counter += 1
                
            else:
                videoIds.remove(videoIds[counter])
            
        else:
            videoIds.remove(videoIds[counter])
            
    logsSyncify.debug(f"(Youtube/Filtering): Result with {len(videoIds)} Video Id.")
    if(len(videoIds) == 0):
        logsSyncify.warning("(Youtube/Filtering): Couldn't find any Video with the specific filter.")
        """ Use the 'yewtubeDownloader' when it's finished. """
        """
            In the future send the 'data' to a server to download it using the module 'spotifyDownloader' 
        and upload it on Youtube to help the 'Syncify' community.
        """
        return False, 'Spotify'
    
    else:   
        if(mostViewedDict["Age Restriction"] == True):
            logsSyncify.warning(f"(Youtube/Filtering): Video link: {'https://www.youtube.com/watch?v=' + mostViewedDict['Video ID']}, is Age-Restricted.")
            """ Use the 'yewtubeDownloader' when it's finished. """
            return False, 'Yewtube'
        
        else:
            logsSyncify.debug(f"(Youtube/Filtering): Filter by Most Reliable - Video link {'https://www.youtube.com/watch?v=' + mostViewedDict['Video ID']} approved.")
            return True, mostViewedDict["Video ID"]
        
#Download track from youtube
def youtubeDownloadTrack(videoId):
    pytubeElement = YouTube('https://www.youtube.com/watch?v=' + videoId)
    
    tries = 0
    while True:
        try:
            availableAudios = pytubeElement.streams.get_by_itag(140)
            break
        except KeyError:
            logsSyncify.warning(f"({tries}) Error -> Couldn't get streams of Youtube Id: {videoId}. Sleeping for {getDataJSON(setting_path, 'Settings/Sleep')}")
            tries = triesCounter(tries)
            if(tries == False):
                logsSyncify.critical(f"Number of tries exceeded 5. Quitting")
                quit()
            time.sleep(getDataJSON("Settings.json", "Settings/Sleep"))
    
    tries = 0
    while True:
        try:
            availableAudios.download(convertPath('Data/'))
            break
        except Exception:
            logsSyncify.warning(f"({tries}) Error -> Couldn't download {videoId}. Sleeping for {getDataJSON(setting_path, 'Settings/Sleep')}")
            tries = triesCounter(tries)
            if(tries == False):
                logsSyncify.critical(f"Number of tries exceeded 5. Quitting")
                quit()
            time.sleep(getDataJSON("Settings.json", "Settings/Sleep"))
    
    return convertPath('Data/' + pytubeElement.title + '.mp4')