import time

#Importing Syncify functions
from SyncifyFunctions.systemFunctions import *
from SyncifyFunctions.playlistHandeling import *

#Get {Artist} - {Trackname}.{format}
def trackInformation(syncifyToken, trackLink):
    trackFormat = getDataJSON(setting_path, "Settings/Format")
    spotifyTrackFormat = trackLink[trackLink.find("track/") + len("track/"):]
    
    while True:
        try:
            trackResult = track(syncifyToken, spotifyTrackFormat)
            break
        except Exception:
            time.sleep(1.25)
    
    return trackResult["artists"][0]["name"] + ' - ' + trackResult["name"] + '.' + trackFormat.lower()

#Returns playlist songs in whatever order
def getTracks(syncifyToken, objId, objURL):
    if(isLinkAlbum(objURL)):
        while True:
            try:
                resultTrackItems = album(syncifyToken, objId)["tracks"]["items"]
                break
            except KeyError:
                time.sleep(1.25)
                
    else:
        while True:
            try:      
                resultTrackItems = playlist(syncifyToken, objId)["tracks"]["items"]
                break
            except KeyError:
                time.sleep(1.25)
        
    track_links = []
    for item in resultTrackItems:
        try:
            if(isLinkAlbum(objURL)):
                track_links.append(item["external_urls"]["spotify"])
            else:
                track_links.append(item["track"]["external_urls"]["spotify"])
        except KeyError:
            pass  
        
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