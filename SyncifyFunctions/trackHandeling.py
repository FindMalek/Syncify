import time

#Importing Syncify functions
from SyncifyFunctions.systemFunctions import *
from SyncifyFunctions.playlistHandeling import *

#Get {Artist} - {Trackname}.{format}
def trackInformation(syncifyToken, trackLink):
    trackFormat = getDataJSON(setting_path, "Settings/Format")
    spotifyTrackFormat = trackLink[trackLink.find("track/") + len("track/"):]

    tries = 0
    while True:
        try:
            trackResult = track(syncifyToken, spotifyTrackFormat)
            break
        except Exception:
            logsSyncify.warning(f"({tries}) Error -> Couldn't get result of {spotifyTrackFormat}. Sleeping for {getDataJSON(setting_path, 'Settings/Sleep')}")
            
            tries = triesCounter(tries)
            if(tries == True):
                logsSyncify.critical(f"Number of tries exceeded 5. Quitting")
                quit()
                
            time.sleep(getDataJSON("Settings.json", "Settings/Sleep"))    

    return trackResult["artists"][0]["name"] + ' - ' + trackResult["name"] + '.' + trackFormat.lower()

#Returns playlist songs in whatever order
def getTracks(syncifyToken, objId, objURL):
    track_links = []
    if(whatIsLink(objURL) == "Album"):
        while True:
            try:
                resultTrackItems = album(syncifyToken, objId)["tracks"]["items"]
                break
            except KeyError:
                logsSyncify.warning(f"({tries}) Error -> Couldn't get result of {objId}. Sleeping for {getDataJSON(setting_path, 'Settings/Sleep')}")
                
                tries = triesCounter(tries)
                if(tries == True):
                    logsSyncify.critical(f"Number of tries exceeded 5. Quitting")
                    quit()
                    
                time.sleep(getDataJSON("Settings.json", "Settings/Sleep"))
                
    elif(whatIsLink(objURL) == "Playlist"):
        while True:
            try:      
                resultTrackItems = playlist(syncifyToken, objId)["tracks"]["items"]
                break
            except KeyError:
                logsSyncify.warning(f"({tries}) Error -> Couldn't get result of {objId}. Sleeping for {getDataJSON(setting_path, 'Settings/Sleep')}")
                
                tries = triesCounter(tries)
                if(tries == True):
                    logsSyncify.critical(f"Number of tries exceeded 5. Quitting")
                    quit()
                    
                time.sleep(getDataJSON("Settings.json", "Settings/Sleep"))
                
    elif(whatIsLink(objURL) == "Track"):
        return list(objURL.split(" "))
    
    for item in resultTrackItems:
        try:
            if(whatIsLink(objURL) == "Album"):
                track_links.append(item["external_urls"]["spotify"])
            elif(whatIsLink(objURL) == "Playlist"):
                track_links.append(item["track"]["external_urls"]["spotify"])
        except KeyError:
            logsSyncify.critical(f"Error in getting track_links") 
            quit()
        
    return track_links

#Put every downloaded track in a list
def getDownloadedTracks():
    downloadedPath = getDataJSON(setting_path, "Settings/Paths/Downloads")
    trackFiles = [f for f in listdir(downloadedPath) if isfile(join(downloadedPath, f))]
    for file in trackFiles:
        if('.mp3' not in file):
            trackFiles.remove(file)
    
    return trackFiles

#Checks if a track is downloaded or not
def isDownloaded(track):
    downloads = sorted(getDownloadedTracks())
    if(track in downloads):
        return True
    else:
        return False
    
#Returns artists in this format "art1, art2, ... artn"
def getArtists(trackRes):
    nameArtists = []
    for artist in trackRes["artists"]:
        nameArtists.append(artist["name"])
    return ", ".join(nameArtists)
    
if __name__ == '__main__':
    #Setting up the logging configuration
    logsSyncify.loggingSetup()