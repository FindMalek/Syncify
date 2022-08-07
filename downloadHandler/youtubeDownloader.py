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
    """ Create a point system for the Youtube Video title (Views/Title) """
    """ Remove in Spotify Track Name the parenthese """
    """ Implimant some sort of AI """

    searchTitle = data['album']['artists'][0]['name'].replace(" ", "+") + '+-+' +  data['name'].replace(" ", "+") + '+-+audio'
    searchLink = "https://www.youtube.com/results?search_query=" + searchTitle
    tries = 0
    while True:
        try:
            html = urllib.request.urlopen(searchLink)
            logsSyncify.debug(f"Requesting {searchLink}.")
            break
        except Exception:
            searchTitle = urllib.parse.quote(data['album']['artists'][0]['name'].replace(" ", "+") + '+-+' +  data['name'].replace(" ", "+") + '+-+audio')
            searchLink = "https://www.youtube.com/results?search_query=" + searchTitle
            
            logsSyncify.warning(f"({tries}) Error -> Couldn't Request {searchLink}. Sleeping for {getDataJSON(setting_path, 'Settings/Sleep')}")
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

        searchElement = {
            "Youtube Title": str(youtubeElement.title).lower(),
            "Spotify Artist": data['album']['artists'][0]['name'].lower(),
            "Youtube Uploader": str(youtubeElement.author).lower(),
            "Spotify Track Name": data['name'].lower()
        }
        
        """ Check for the Artist -> Channel Author | Youtube Title """
        if((searchElement["Spotify Artist"] in searchElement["Youtube Title"]) or (searchElement["Spotify Artist"] in searchElement["Youtube Uploader"])):
            logsSyncify.debug(f"(Youtube/Filtering): Filter by Title: Artist - Video link {'https://www.youtube.com/watch?v=' + videoIds[counter]} approved.")
            
            """ Check for the Track name -> With inside the parenthese | Without the parenthese """
            if((searchElement["Spotify Track Name"] in searchElement["Youtube Title"]) or (removeExtras(searchElement["Spotify Track Name"]) in searchElement["Youtube Title"]) or (removeExtras(searchElement["Spotify Track Name"]) in searchElement["Youtube Title"]) or (removeExtras(searchElement["Spotify Track Name"]) in removeExtras(searchElement["Youtube Title"]))) :
                logsSyncify.debug(f"(Youtube/Filtering): Filter by Title: Track name - Video link {'https://www.youtube.com/watch?v=' + videoIds[counter]} approved.")
                
                """ Check for the Duration -> +- getDataJSON(setting_path, "Settings/Time Difference") """
                if(youtubeElement.length in range(int(data["duration_ms"] / 1000) - getDataJSON(setting_path, "Settings/Time Difference"), int(data["duration_ms"] / 1000) + getDataJSON(setting_path, "Settings/Time Difference"))):
                    logsSyncify.debug(f"(Youtube/Filtering): Filter by Duration - Video link {'https://www.youtube.com/watch?v=' + videoIds[counter]} approved.")

                    """ Check for the Most Viewed -> Does it surpass the Most Viewed Video? """
                    if(youtubeElement.views > mostViews):
                        logsSyncify.debug(f"(Youtube/Filtering): Filter by Most Views - Video link {'https://www.youtube.com/watch?v=' + videoIds[counter]} approved.")
                        mostViewedDict, mostViews = {"Video ID": videoIds[counter], "Age Restriction": youtubeElement.age_restricted}, youtubeElement.views
                    counter += 1
                    
                else:
                    videoIds.remove(videoIds[counter])
            
            else:
                videoIds.remove(videoIds[counter])

        else:
            videoIds.remove(videoIds[counter])
            
    logsSyncify.debug(f"(Youtube/Filtering): Result with {len(videoIds)} Video Id.")
    if(len(videoIds) == 0):
        logsSyncify.warning("(Youtube/Filtering): Couldn't find any Video with the specific filter.")

        logsSyncify.debug(f"(Not-Found-Track): Spotify ID {data['uri']} is not found in Youtube, added to 'notFoundTracks.json' for the Syncify Community.")
        notFoundTracks("https://www.youtube.com/results?search_query=" + searchTitle.replace(' ', '+'), data, 'Spotify')
        
        return False, 'Spotify'
    
    else:   
        if(mostViewedDict["Age Restriction"] == True):
            logsSyncify.warning(f"(Youtube/Filtering): Video link: {'https://www.youtube.com/watch?v=' + mostViewedDict['Video ID']}, is Age-Restricted.")
            
            logsSyncify.debug(f"(Not-Found-Track): Spotify ID {data['uri']} is not found in Youtube, added to 'notFoundTracks.json' for the Syncify Community.")
            notFoundTracks("https://www.youtube.com/results?search_query=" + searchTitle.replace(' ', '+'), data, 'Yewtube', 'https://www.youtube.com/watch?v=' + mostViewedDict['Video ID'])
            
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