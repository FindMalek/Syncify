""" 
    CHANGES:

        1.(In progress)     Changing the format of 'Playlists Information.json'.
    It used to have duplicate information which is bad for the database.
    It will only have unique data and  Albums and Playlists will be sperated as well.
    {
        "Playlists": [
            {}
        ],
        
        "Albums": [
            {}
        ],
        
        "Tracks": [
            'link1'
        ]
    }
    
        2.(In progress)      Adding traks.
        This update is a preparation to download tracks individually.
        In the next updates this feature will be available.
    
    
        3.(In progress)      Changing how the Albums / Playlists get saved
        in 'Playlists Information.json', they used to be saved only after choosing the download command.
        It will be changed to; after enterning each Album / Playlist it will be automatically
        saved to the file.
        
        4.(Done)     Changing 'Playlist Informations' -> 'userData.json'
        Because it makes more sense, since the 'userData' stores; 'Albums, Playlists and Tracks' of the user,
        not only playlists.
        
        5.(No progress)     Change the order of downloading Albums / Tracks / Playlists.
        By default it will be Playlists -> Albums -> Tracks.
        But the user will be able to change it, using an order system.
"""

__title__ = "Syncify"
__author__ = "Malek Gara-Hellal"
__email__ = 'malekgarahellalbus@gmail.com'
__version__ = '1.0.6.4.2'


#importing systemFunctions
import logging, json, shutil, os, fnmatch
from SyncifyFunctions.systemFunctions import * 

#Importing spotifyHandeler
from spotifyHandler.requestsHandeling import *

#Setting up needed files
SettingUp()
setting_path = "Settings.json"
userdata = convertPath("Data/userData.json")
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
    
#print Playlist / Album / Track informations
def printObject(link, syncifyToken):
    logsSyncify("").message("\n\n_______________________________________")
    
    #If the link is a Playlist Link
    if(whatIsLink(link) == "Playlist"):
        playlistId = link[link.find("playlist/") + len("playlist/"):]
        tries = 0
        while True:
            try:
                Result = playlist(syncifyToken, playlistId)
                break
            except Exception:
                logsSyncify("").Syncify(f"({nbTries}) Error -> Couldn't get result of {playlistId}. Sleeping for {getDataJSON(setting_path, 'Settings/Sleep')}").warning()
                
                tries = triesCounter(tries)
                if(tries == True):
                    logsSyncify("").Syncify(f"Number of tries exceeded 5. Quitting").critical()
                    quit()
                    
                time.sleep(getDataJSON("Settings.json", "Settings/Sleep"))
                
        logsSyncify("").message(f"\t-(Playlist)-\nName: {Result['name']}\n\n{Result['description']}\n{Result['owner']['display_name']} • {len(Result['tracks']['items'])} songs.")
        
    #If the link is an Album Link
    elif(whatIsLink(link) == "Album"):
        albumID = link[link.find("album/") + len("album/"):]
        while True:
            try:
                Result = album(syncifyToken, albumID)
                break
            except Exception:
                logsSyncify("").Syncify(f"({nbTries}) Error -> Couldn't get result of {albumID}. Sleeping for {getDataJSON(setting_path, 'Settings/Sleep')}").warning()
                
                tries = triesCounter(tries)
                if(tries == True):
                    logsSyncify("").Syncify(f"Number of tries exceeded 5. Quitting").critical()
                    quit()
                    
                time.sleep(getDataJSON("Settings.json", "Settings/Sleep"))  
                    
        logsSyncify("").message(f"\t-(Album)-\nName: {Result['name']}\n{Result['artists'][0]['name']} • {len(Result['tracks']['items'])} songs.")
    
    #If the link is a Track Link
    elif(whatIsLink(link) == "Track"):
        trackID = link[link.find("track/") + len("track/"):]
        while True:
            try:
                Result = track(syncifyToken, trackID)
                WriteJSON('res.json', Result, 'w')
                break
            except Exception:
                logsSyncify("").Syncify(f"({nbTries}) Error -> Couldn't get result of {trackID}. Sleeping for {getDataJSON(setting_path, 'Settings/Sleep')}").warning()

                tries = triesCounter(tries)
                if(tries == True):
                    logsSyncify("").Syncify(f"Number of tries exceeded 5. Quitting").critical()
                    quit()
                    
                time.sleep(getDataJSON("Settings.json", "Settings/Sleep"))  
        logsSyncify("").message(f"\t-(Track)")

    logsSyncify("").message("_______________________________________")

#Add Albums, Playlists and Tracks to userData.json
def addObject(syncifyToken, link):
    objectResult = getObjectInformation(syncifyToken, link)
    objects = ReadFILE(userdata)
    
    if(whatIsLink(link) == "Album"):
        WriteJSON('resAlb', objectResult, 'w')
        obj = {
            objectResult[0]["name"] : {
                "Image" : objectResult[0]["images"][0]["url"],
                "Links" : {
                    "URL": objectResult[0]["external_urls"]["spotify"],
                    "ID": objectResult[1]      
                }
            }
        }
        objects["Albums"].append(obj)
        
    elif(whatIsLink(link) == "Playlist"):
        obj = {
            objectResult[0]["name"] : {
                "Image" : objectResult[0]["images"][0]["url"],
                "Links" : {
                    "URL": objectResult[0]["external_urls"]["spotify"],
                    "ID": objectResult[1]      
                }
            }
        }
        objects["Playlists"].append(obj)
    
    elif(whatIsLink(link) == "Track"):
        objects["Tracks"].append(link)

    #Add the new objects
    WriteJSON(userdata, objects, 'w')

#Enter Playlist / Album / Track to the "UserData.json"
def enterObject(syncifyToken):
    while True:
        link = input("\n-> Enter link (Album / Playlist / Track) or <Enter> to skip: ")
        
        if(link == ''):
            logsSyncify("").message("=> Nothing has been entered!")
            break   
            
        if('?' in link):
            link = link[:link.find('?')]
            
        #Print the name of the playlist / album / track and the description
        logsSyncify("").Syncify(f"Printing Album / Playlist / Track -> {link}").debug()
        printObject(link, syncifyToken)
        
        #Add the Object to "userData.json"
        addObject(syncifyToken, link)

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

    if((getDataJSON(userdata, "Playlists") == []) and (getDataJSON(userdata, "Albums") ==  []) and (getDataJSON(userdata, "Tracks") == [])):
        logsSyncify("").Syncify(f"Adding links to {userdata}.").debug()
        enterObject(syncifyToken)

#Select which action the user wants
def SelectCommand(syncifyToken): 
    printLoad(19, 42) #Printing for the CLI
    
    answer = input("Choose the number of the command: ")

    if(answer == "1"): #Enter Playlists Informations
        logsSyncify("").Syncify("Adding and updating Playlists / Albums / Tracks...").debug()
        enterObject(syncifyToken)
        logsSyncify("").Syncify("Added and updated Playlists / Albums / Tracks.").debug()

    elif(answer == "2"): 
        downloadableObjs = getDataJSON(userdata, "Playlists Informations")
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
            if(isLinkAlbum(obj[list(obj.keys())[0]]["Links"]["URL"]) == False):
                plOrdered = PlaylistManager(syncifyToken, obj[list(obj.keys())[0]]["Links"]["ID"], obj[list(obj.keys())[0]]["Links"]["URL"])
                CreatePlaylist(plOrdered)

            logsSyncify("").Syncify(f"Created playlist -> {objName}").debug()
            
        logsSyncify("").Syncify("\n>Downloading all tracks is finished! All playlists are saved.").info()

        #Deleting Albums from "Playlist Information.json" to optimize the speed of the execution
        popAlbums()
        logsSyncify("").Syncify(f"Deleted Albums links from '{userdata}' for optimization.").debug()

    elif(answer == "3"):
        SavifyPlaylists = ReadFILE(userdata)["Playlists Informations"]
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
            settinguserdata = Settings["Paths"]["Playlist"]
            PlaylistPath = input(f"\nCurrently the Playlist path is: {settinguserdata} \nNew Playlist path (Press <Enter>, If you don't wish to change the path): ")
            
            if(sysOs.lower() != "linux"):
                Settings["Paths"]["Playlist"] = PlaylistPath.replace(r"\"", "\\")
            else:
                Settings["Paths"]["Playlist"] = PlaylistPath
                
            WriteJSON(setting_path, Settings, 'w')

    elif(answer == "5"):
        logsSyncify("").message("<This command is coming in the next updates...>")
        input("")

    elif(answer == "6"):
        logsSyncify("").Syncify("<Exit>").info()
        quit()


if __name__ == '__main__':
    logsSyncify("").Syncify("Getting (CLIENT_ID, CLIENT_SECRET)...").debug()
    syncifyToken = getAccessToken(CLIENT_ID, CLIENT_SECRET)
    logsSyncify("").Syncify(f"Got (CLIENT_ID, CLIENT_SECRET) = ({CLIENT_ID}, {CLIENT_SECRET}).").debug()

    Load(syncifyToken)
    while(True):
        logsSyncify("").Syncify("Selecting command...").debug()
        SelectCommand(syncifyToken)
        
        logsSyncify("").Syncify("Deleting temporary files...").debug()
        deleteTemporaryFiles(os.getcwd())
        logsSyncify("").Syncify("Deleted temporary files.").debug()