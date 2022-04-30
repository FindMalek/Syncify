__title__ = "Syncify"
__author__ = "Malek Gara-Hellal"
__email__ = 'malekgarahellalbus@gmail.com'
__version__ = '1.0.6.1'



#importing Savify
from savify import Savify
from savify.types import Type, Format, Quality
from savify.utils import PathHolder
from savify.logger import Logger

#Importing spotifyHandeler
from spotifyHandenler.requestsHandeling import *

#importing systemFunctions
import logging, json, shutil, os, fnmatch
from SyncifyFunctions.systemFunctions import * 
from spotifyHandenler.systemHandeling import *

#Setting up needed files
SettingUp()
setting_path = "Settings.json"
playlist_path = convertPath("Data/Playlists Informations.json")

#Importing playlistHandeling
from SyncifyFunctions.playlistHandeling import *

#Importing trackHandeling
from SyncifyFunctions.trackHandeling import *


#Downloader
def Downloads(syncifyToken):
    #Get time before downloading the music and then compare every
    #music that its created time is later than that time and move it to
    #newly downloaded music  <Coming Soon>
    
    Playlists = getDataJSON(playlist_path, "Playlists Informations")
    downloadPath = getDataJSON(setting_path, "Settings/Paths/Downloads")
    
    counterPlaylist = 0
    for element in Playlists:
        playlist_Name = str(list(element.keys())[0])
        print("\n\n\tDownloading from :", playlist_Name)
        
        quality_type = DownloadSettings(Savify)[0]
        download_format = DownloadSettings(Savify)[1]
        
        #Logging stuff
        logger = Logger(log_location=convertPath("/tmp/"), log_level=None) # Silent output
        
        #Session
        Session = Savify(logger=logger,
                         quality=quality_type,
                         download_format=download_format,
                         path_holder=PathHolder(downloads_path=downloadPath))
        
        #Download each song individually
        tracksPath = getDataJSON(setting_path, "Settings/Paths/Downloads")
        for link in getTracks(syncifyToken, Playlists[counterPlaylist][playlist_Name]["Links"]["ID"]):
            track = trackInformation(syncifyToken, link)
            if(isDownloaded(track) == False):
                print(f"Downloading > {track[:-4]}")
                Session.download(link)
                print(f"Downloaded -> {track[:-4]}")
        
        print(f"\tDownloaded Playlist -> {playlist_Name}\n")
        counterPlaylist += 1
    print("\n>Download is finished! All songs are downloaded.")

#print the name of the playlist and the description
def printPlaylist(link, syncifyToken):
    if(isLinkAlbum(link) == False):
        playlist_ID = link[link.find("playlist/") + len("playlist/"):]
        Result = playlist(syncifyToken, playlist_ID)
        print(f"\n\t{Result['name']}\n{Result['description']}\n{Result['owner']['display_name']} • {len(Result['tracks']['items'])} songs.")
    else:
        album_ID = link[link.find("album/") + len("album/"):link.find("?")]
        
        while True:
            try:
                Result = album(syncifyToken, album_ID)
            except Exception:
                time.sleep(1.25)        
                        
        print(f"\n\t{Result['name']}\n{Result['artists'][0]['name']} • {len(Result['tracks']['items'])} songs.")

#Add playlist link in the json file Playlists Informations.json
def AddLink(list):
    playlistLinks = ReadFILE(playlist_path)
    for link in list:
        if(link in playlistLinks["Playlists links"]) == False:
            playlistLinks["Playlists links"].append(link)

    WriteJSON(playlist_path, playlistLinks, 'w')

#Add playlists to the settings.json "Playlists Informations"
def AddPlaylist(syncifyToken):
    link, listPL = ".", []
    while(link != ""):
        link = input("\n.Enter playlist link: ")
        if(link != ""):
            #Print the name of the playlist and the description
            printPlaylist(link, syncifyToken)
            if("?" in link):
                listPL.append(link[:link.find("?")])
            else:
                listPL.append(link)
        else:
            print(">No playlist have been entered!")
    AddLink(listPL)

#updating the playlists
def PlaylistUpdate(syncifyToken):  
    playlist_list = getDataJSON(playlist_path, "Playlists Informations")
    playlistID_list = []
    for playlist in playlist_list:
        for key in playlist.keys():
            playlistID_list.append(playlist[key]["Links"]["ID"])
            
    for pl_id in playlistID_list:
        if(isLinkAlbum(pl_id) == False):
            pl_order = PlaylistManager(syncifyToken, pl_id)
            CreatePlaylist(pl_order)
    print("\n>All playlist files are created.")
    
    #Deleting Albums from "Playlist Information.json" to optimize the speed of the execution
    popAlbums()

#Print the load text, load the savify client
def Load(syncifyToken):
    printLoad(0, 18)
    
    settingFile = ReadFILE(setting_path)
    if(settingFile["Settings"]["Paths"]["Downloads"] == ""):
        downloadPath = input(".Enter a path where to store downloaded music: ")
        settingFile["Settings"]["Paths"]["Downloads"] = downloadPath

    if(settingFile["Settings"]["Paths"]["Playlist"] == ""):
        playlistPath = input(".Enter a path where to store playlist files <.m3a>: ")
        settingFile["Settings"]["Paths"]["Playlist"] = playlistPath
    WriteJSON(setting_path, settingFile, 'w')

    playlistFile = getDataJSON(playlist_path, "Playlists Informations")
    if(playlistFile == []):
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
    
    if(SavifySettings["Format"] == "WAV"):      download_format=Format.WAV
    elif(SavifySettings["Format"] == "VORBIS"): download_format=Format.VORBIS
    elif(SavifySettings["Format"] == "OPUS"):   download_format=Format.OPUS
    elif(SavifySettings["Format"] == "M4A"):    download_format=Format.M4A 
    elif(SavifySettings["Format"] == "FLAC"):   download_format=Format.FLAC 
    elif(SavifySettings["Format"] == "AAC"):    download_format=Format.AAC
    elif(SavifySettings["Format"] == "MP3"):    download_format=Format.MP3 
    
    return qual, download_format

#Add information in settings file
def addInformation(stroption, info, infoList, Settings):
    infoEntered = '.'
    while(infoEntered not in infoList):
        infoEntered = input(f"{stroption} chosen (Press <Enter>, If you don't wish to change the {stroption}): ")
        if(infoEntered == ""):
            Settings["Settings"][stroption] = info
            break
    return Settings

#Select which action the user wants
def SelectCommand(syncifyToken): 
    printLoad(19, 42) #Printing for the user
    
    answer = input("Choose the number of the command: ")

    if(answer == "1"): #Enter Playlists Informations
        AddPlaylist(syncifyToken)

    elif(answer == "2"): 
        #Downloads newly added songs and Refresh playlists
        #And move Outdated Playlists to the Outdated folder
        #It keeps a version of each playlist
        RefreshPlaylistFile(syncifyToken)
        Downloads(syncifyToken)  
        PlaylistUpdate(syncifyToken)

    elif(answer == "3"):
        SavifyPlaylists = ReadFILE(playlist_path)["Playlists Informations"]
        for playlist in SavifyPlaylists:
            playlistLink = playlist[list(playlist.keys())[0]]["Links"]["URL"]
            printPlaylist(playlistLink,  syncifyToken)
            input()

    elif(answer == "4"):
        printLoad(29, 37)

        answer = input("Choose the number of the command: ")
        Settings = ReadFILE(setting_path)
        sysOs = getDataJSON(setting_path, "System Os")
        
        if(answer == "1"):
            quality = Settings["Settings"]["Quality"]
            qualityList = ["BEST", "320K", "256K", "192K", "128K", "96K", "32K", "WORST"]
            print(f"\nCurrently the download quality is: {quality}\nAvailable qualities: {qualityList}")
            
            Settings = addInformation("Quality", quality, qualityList, Settings)
            WriteJSON(setting_path, Settings, 'w')

        elif(answer == "2"):
            formatType = Settings["Settings"]["Format"]
            formatList = ["WAV", "VORBIS", "OPUS", "M4A", "FLAC", "AAC", "MP3"]
            print(f"\nCurrently the download format is: {formatType}\nAvailable formats: {formatList}")
            
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
        print("<This command is coming in the next updates...>")
        pause = input("")

    elif(answer == "6"):
        print("<Exit>")
        quit()


#Main
if __name__ == '__main__':
    syncifyToken = getAccessToken(CLIENT_ID, CLIENT_SECRET)
    
    Load(syncifyToken)
    while(True):
        SelectCommand(syncifyToken)
        deleteTemporaryFiles(os.getcwd())