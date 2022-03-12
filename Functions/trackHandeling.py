from Functions.systemFunctions import *
from Functions.playlistHandeling import *


#Get {Artist} - {Trackname}.{format}
def trackInformation(Spotipy_Session, trackLink):
    trackFormat = getDataJSON(setting_path, "Settings/Format")
    trackResult = Spotipy_Session.track("spotify:track:" + trackLink[trackLink.find("track/") + len("track/"):])
    return trackResult["artists"][0]["name"] + ' - ' + trackResult["name"] + '.' + trackFormat.lower()

#Returns playlist songs in whatever order
def getTracks(pl_id):
    if(isLinkAlbum(pl_id)):
        resultTrackItems = Spotipy_Session.album(pl_id)["tracks"]["items"]
    else:
        resultTrackItems = Spotipy_Session.playlist(pl_id)["tracks"]["items"]

    track_links = []
    for item in resultTrackItems:
        try:
            if(isLinkAlbum(pl_id)):
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
    elif(track not in downloads):
        return False