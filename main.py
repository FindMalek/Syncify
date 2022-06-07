""" 
    CHANGES:

        .Changing how Syncify creates playlists.
    Instead of downloading all the tracks from each playlist and then creating all the playlists.
    That changed to downloading the tracks of a playlist and then create the playlist file.
    After this change you don't have to wait to download all the tracks to get your playlist prepared.
"""


"""
    BUGS:
    
    1. Now Syncify deletes all of it's temporary files, to save storage.
"""

__title__ = "Syncify"
__author__ = "Malek Gara-Hellal"
__email__ = 'malekgarahellalbus@gmail.com'
__version__ = '1.0.6.4.1'


#importing systemFunctions
import logging, json, shutil, os, fnmatch
from SyncifyFunctions.systemFunctions import * 

#Importing spotifyHandeler
from spotifyHandler.requestsHandeling import *

#Setting up needed files
SettingUp()
setting_path = "Settings.json"
playlist_path = convertPath("Data/Playlists Informations.json")
logsSyncify("").Syncify("Function - SettingUp && Prepaths are set.").debug()

#importing Savify
from savify import Savify
from savify.types import Type, Format, Quality
from savify.utils import PathHolder
from savify.logger import Logger
logsSyncify("").Syncify("Savify imported.").debug()

#Importing playlistHandeling
from SyncifyFunctions.playlistHandeling import *

#Importing trackHandeling
from SyncifyFunctions.trackHandeling import *
logsSyncify("").Syncify("Imported all modules and packages.").debug()

#Downloader
def Downloads(syncifyToken, savifySession, playlistURLs):
    for url in playlistURLs:
        track = trackInformation(syncifyToken, url)
        if(isDownloaded(track) == False):
            logsSyncify("").Syncify(f"Downloading > {track[:-4]}...").info()
            savifySession.download(url)
            logsSyncify("").Syncify(f"Downloaded -> {track[:-4]}.").info()
    
#print Playlist / Album informations
def printObject(link, syncifyToken):
    logsSyncify("").message("\n\n_______________________________________")
    if(isLinkAlbum(link) == False):
        playlist_ID = link[link.find("playlist/") + len("playlist/"):]
        tries = 0
        while True:
            try:
                Result = playlist(syncifyToken, playlist_ID)
                break
            except Exception:
                logsSyncify("").Syncify(f"({nbTries}) Error -> Couldn't get result of {playlist_ID}. Sleeping for {getDataJSON(setting_path, 'Settings/Sleep')}").warning()
                
                tries = triesCounter(tries)
                if(tries == True):
                    logsSyncify("").Syncify(f"Number of tries exceeded 5. Quitting").critical()
                    quit()
                    
                time.sleep(getDataJSON("Settings.json", "Settings/Sleep"))
                
        logsSyncify("").message(f"\t-(Playlist)-\nName: {Result['name']}\n\n{Result['description']}\n{Result['owner']['display_name']} • {len(Result['tracks']['items'])} songs.")
        
    else:
        album_ID = link[link.find("album/") + len("album/"):]
        while True:
            try:
                Result = album(syncifyToken, album_ID)
                break
            except Exception:
                logsSyncify("").Syncify(f"({nbTries}) Error -> Couldn't get result of {album_ID}. Sleeping for {getDataJSON(setting_path, 'Settings/Sleep')}").warning()
                
                tries = triesCounter(tries)
                if(tries == True):
                    logsSyncify("").Syncify(f"Number of tries exceeded 5. Quitting").critical()
                    quit()
                    
                time.sleep(getDataJSON("Settings.json", "Settings/Sleep"))  
                    
        logsSyncify("").message(f"\t-(Album)-\nName: {Result['name']}\n{Result['artists'][0]['name']} • {len(Result['tracks']['items'])} songs.")
    logsSyncify("").message("_______________________________________")


#Add playlist link in the json file Playlists Informations.json
def AddLink(list):
    playlistLinks = ReadFILE(playlist_path)
    for link in list:
        if(link in playlistLinks["Playlists links"]) == False:
            playlistLinks["Playlists links"].append(link)

    WriteJSON(playlist_path, playlistLinks, 'w')
    logsSyncify("").Syncify(f"Added all links to {playlist_path}").debug()

#Add playlists to the settings.json "Playlists Informations"
def AddPlaylist(syncifyToken):
    listAP = []
    
    while True:
        link = input("\n-> Enter link (Album / Playlist) or <Enter> to skip: ")
        
        if(link == ''):
            logsSyncify("").message("=> No playlist have been entered!")
            break   
            
        #Print the name of the playlist and the description
        logsSyncify("").Syncify(f"Printing Album / Playlist -> {link}").debug()
        printObject(link, syncifyToken)
        
        if('?' in link):
            listAP.append(link[:link.find('?')])
        else:
            listAP.append(link)
            
    AddLink(listAP)

#Print the load text, load the savify client
def Load(syncifyToken):
    printLoad(0, 18)
    
    settingFile = ReadFILE(setting_path)
    if(settingFile["Settings"]["Paths"]["Downloads"] == ""):
        downloadPath = input(".Enter a path where to store downloaded music: ")
        settingFile["Settings"]["Paths"]["Downloads"] = downloadPath
        logsSyncify("").Syncify(f"Changed the download path -> {downloadPath}").debug()

    if(settingFile["Settings"]["Paths"]["Playlist"] == ""):
        playlistPath = input(".Enter a path where to store playlist files <.m3a>: ")
        settingFile["Settings"]["Paths"]["Playlist"] = playlistPath
        logsSyncify("").Syncify(f"Changed the playlist path -> {playlistPath}").debug()

    WriteJSON(setting_path, settingFile, 'w')

    playlistFile = getDataJSON(playlist_path, "Playlists Informations")
    if(playlistFile == []):
        logsSyncify("").Syncify(f"Adding links to {playlist_path}.").debug()
        AddPlaylist(syncifyToken)

#Download settings
def DownloadSettings(Savify):
    SavifySettings = ReadFILE(setting_path)["Settings"]
    
    if(SavifySettings["Quality"] == "BEST"):    qual=Quality.BEST
    elif(SavifySettings["Quality"] == "Q320K"): qual=Quality.Q320K
    elif(SavifySettings["Quality"] == "Q256K"): qual=Quality.Q256K
    elif(SavifySettings["Quality"] == "Q192K"): qual=Quality.Q192K
    elif(SavifySettings["Quality"] == "Q128K"): qual=Quality.Q128K
    elif(SavifySettings["Quality"] == "Q96K"):  qual=Quality.Q96K
    elif(SavifySettings["Quality"] == "Q32K"):  qual=Quality.Q32K
    elif(SavifySettings["Quality"] == "WORST"): qual=Quality.WORST  

    logsSyncify("").Syncify(f"Quality -> {qual}. Format -> {SavifySettings['Format'].lower()}").debug()
    return qual, SavifySettings["Format"].lower()

#Add information in settings file
def addInformation(stroption, info, infoList, Settings):
    while True:
        infoEntered = input(f"{stroption} chosen (Press <Enter>, If you don't wish to change the {stroption}): ")
        if(infoEntered == ''):
            Settings["Settings"][stroption] = info
            break
        elif(infoEntered in infoList): 
            Settings["Settings"][stroption] = infoEntered
            break
        
    return Settings

#Select which action the user wants
def SelectCommand(syncifyToken): 
    printLoad(19, 42) #Printing for the CLI
    
    answer = input("Choose the number of the command: ")

    if(answer == "1"): #Enter Playlists Informations
        AddPlaylist(syncifyToken)

    elif(answer == "2"): 
        #And move Outdated Playlists to the Outdated folder
        #It keeps a version of each playlist
        
        logsSyncify("").Syncify("Adding and updating Playlists / Albums...").debug()
        RefreshPlaylistFile(syncifyToken)
        logsSyncify("").Syncify("Added and updated Playlists / Albums.").debug()

        downloadableObjs = getDataJSON(playlist_path, "Playlists Informations")
        downloadPath = getDataJSON(setting_path, "Settings/Paths/Downloads")
        logsSyncify("").Syncify(f"downloadPath = {downloadPath}").debug()

        #Logging stuff
        logger = Logger(log_location=convertPath("/tmp/"), log_level=None) # Silent output
        logsSyncify("").Savify("Logger setup -> {None}.").debug()

        #Savify Session
        savifySession = Savify(logger=logger,
                         quality=DownloadSettings(Savify)[0],
                         download_format=DownloadSettings(Savify)[1],
                         path_holder=PathHolder(downloads_path=getDataJSON(setting_path, "Settings/Paths/Downloads")))
        logsSyncify("").Savify(f"Savify Session has been setup.").debug()

        logsSyncify("").Syncify(">Downloading began...").debug()
        for obj, objectCounter in zip(downloadableObjs, range(len(downloadableObjs))):
            objName = str(list(obj.keys())[0])
            trackURLs = getTracks(syncifyToken, downloadableObjs[objectCounter][objName]["Links"]["ID"], downloadableObjs[objectCounter][objName]["Links"]["URL"])
            
            logsSyncify("").Syncify(f"\n\n\tDownloading from : {objName}").info()
            Downloads(syncifyToken, savifySession, trackURLs)  
            logsSyncify("").Syncify(f"\tDownloaded -> {objName}\n").info()
            
            #Creating playlist
            playlistURL = obj[list(obj.keys())[0]]["Links"]["URL"]
            if(isLinkAlbum(playlistURL) == False):
                plOrdered = PlaylistManager(syncifyToken, playlistURL[playlistURL.find("playlist/") + len("playlist/"):], playlistURL)
                CreatePlaylist(plOrdered)

            logsSyncify("").Syncify(f"\tCreated playlist -> {objName}").debug()
            
        logsSyncify("").Syncify("\n>Downloading all tracks is finished! All playlists are saved.").info()

        #Deleting Albums from "Playlist Information.json" to optimize the speed of the execution
        popAlbums()
        logsSyncify("").Syncify(f"Deleted Albums links from '{playlist_path}' for optimization.").debug()

    elif(answer == "3"):
        SavifyPlaylists = ReadFILE(playlist_path)["Playlists Informations"]
        for playlist in SavifyPlaylists:
            playlistLink = playlist[list(playlist.keys())[0]]["Links"]["URL"]
            printObject(playlistLink, syncifyToken)
            input()

    elif(answer == "4"):
        printLoad(29, 37)

        answer = input("Choose the number of the command: ")
        Settings = ReadFILE(setting_path)
        sysOs = getDataJSON(setting_path, "System Os")
        
        if(answer == "1"):
            quality = Settings["Settings"]["Quality"]
            qualityList = ["BEST", "320K", "256K", "192K", "128K", "96K", "32K", "WORST"]
            logsSyncify("").Syncify(f"\nCurrently the download quality is: {quality}\nAvailable qualities: {qualityList}").info()
            
            Settings = addInformation("Quality", quality, qualityList, Settings)
            WriteJSON(setting_path, Settings, 'w')

        elif(answer == "2"):
            formatType = Settings["Settings"]["Format"]
            formatList = ["WAV", "VORBIS", "OPUS", "M4A", "FLAC", "AAC", "MP3"]
            logsSyncify("").Syncify(f"\nCurrently the download format is: {formatType}\nAvailable formats: {formatList}").info()
            
            Settings = addInformation("Format", formatType, formatList, Settings)
            WriteJSON(setting_path, Settings, 'w')

        elif(answer == "3"):
            settingsDownload_path = Settings["Paths"]["Downloads"]
            downloadPath = input(f"\nCurrently the download path is: {settingsDownload_path}\nNew download path (Press <Enter>, If you don't wish to change the path): ")
            
            if(sysOs.lower() != "linux") and (downloadPath != ''):
                Settings["Paths"]["Downloads"] = downloadPath.replace(r"\"", "\\")
            elif(downloadPath != ''):
                Settings["Paths"]["Downloads"] = downloadPath
            
            WriteJSON(setting_path, Settings, 'w')

        elif(answer == "4"):
            settingplaylist_path = Settings["Paths"]["Playlist"]
            PlaylistPath = input(f"\nCurrently the Playlist path is: {settingplaylist_path} \nNew Playlist path (Press <Enter>, If you don't wish to change the path): ")
            
            if(sysOs.lower() != "linux"):
                Settings["Paths"]["Playlist"] = PlaylistPath.replace(r"\"", "\\")
            else:
                Settings["Paths"]["Playlist"] = PlaylistPath
                
            WriteJSON(setting_path, Settings, 'w')

    elif(answer == "5"):
        logsSyncify("").message("<This command is coming in the next updates...>")
        pause = input("")

    elif(answer == "6"):
        logsSyncify("").Syncify("<Exit>").info()
        quit()


if __name__ == '__main__':
    logsSyncify("").Syncify("Getting (CLIENT_ID, CLIENT_SECRET)...").debug()
    syncifyToken = getAccessToken(CLIENT_ID, CLIENT_SECRET)
    logsSyncify("").Syncify(f"Got (CLIENT_ID, CLIENT_SECRET) = ({CLIENT_ID}, {CLIENT_SECRET}).").debug()

    Load(syncifyToken)
    while(True):
        SelectCommand(syncifyToken)
        logsSyncify("").Syncify("Deleting temporary files...").debug()
        deleteTemporaryFiles(os.getcwd())
        logsSyncify("").Syncify("Deleted temporary files.").debug()