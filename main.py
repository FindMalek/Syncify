#importing Savify
from savify import Savify
from savify.types import Type, Format, Quality
from savify.utils import PathHolder
from savify.logger import Logger

#importing Spotipy
import spotipy

#importing systemFunctions
import logging, json, shutil, os, fnmatch
from Functions.systemFunctions import printLoad, getDataJSON, WriteJSON, ReadFILE
from Functions.systemFunctions import convertPath, SetOutdatedPath, isFilePlaylist, movePlaylists

#Importing playlistHandeling
from Functions.playlistHandeling import getPlaylistInformation, SpotipySession, RefreshPlaylistFile
from Functions.playlistHandeling import CreatePlaylist, PlaylistManager


setting_path = "Settings.json"
playlist_path = convertPath("Data/Playlists Informations.json")

#Downloader
def Downloads():
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
        
        logger = Logger(log_location='logs/', log_level=None)
        Session = Savify(logger=logger,
                         quality=quality_type,
                         download_format=download_format,
                         path_holder=PathHolder(downloads_path=downloadPath))
        Session.download(Playlists[counterPlaylist][playlist_Name]["Links"]["URL"])
        counterPlaylist += 1
    print("\n>Download is finished! All songs are downloaded.")

#print the name of the playlist and the discription
def printPlaylist(counter, total, link, Spotipy_Session):
    playlist_ID = "spotify:playlist:" + link[link.find("playlist/") + len("playlist/"):]
    Result = Spotipy_Session.playlist(playlist_ID)
    print(f"\n\t{Result['name']}\n{Result['description']}\n{Result['owner']['display_name']} • {len(Result['tracks']['items'])} songs.\n\t({counter}/{total})\n")
    input()

#Add playlist link in the json file Playlists Informations.json
def AddLink(list):
    playlistLinks = ReadFILE(playlist_path)
    for link in list:
        if(link in playlistLinks["Playlists links"]) == False:
            playlistLinks["Playlists links"].append(link)

    WriteJSON(playlist_path, playlistLinks, 'w')

#Add playlists to the settings.json "Playlists Informations"
def AddPlaylist(Spotipy_Session):
    link, listPL = ".", []
    while(link != ""):
        link = input("\n.Enter playlist link: ")
        if(link != ""):
            #Print the name of the playlist and the description
            printPlaylist(link, Spotipy_Session)
            listPL.append(link[:link.find("?")])
        else:
            print(">No playlist have been entered!")
    AddLink(listPL)

#updating the playlists
def PlaylistUpdate():  
    #move the old playlists to the outdated folder
    movePlaylists()  
    
    playlist_list = getDataJSON(playlist_path, "Playlists Informations")
    playlistID_list = []
    for playlist in playlist_list:
        for key in playlist.keys():
            playlistID_list.append(playlist[key]["Links"]["ID"])
            
    for pl_id in playlistID_list:
        pl_order = PlaylistManager(Spotipy_Session, pl_id)
        CreatePlaylist(pl_order)
    print("\n>All playlist files are created.")

#Print the load text, load the savify client
def Load(Spotipy_Session):
    printLoad(0, 18)

    settingFile = ReadFILE(setting_path)
    if(settingFile["Settings"]["Paths"]["Downloads"] == ""):
        downloadPath = input(".Enter a path where to store downloaded music: ")
        settingFile["Settings"]["Paths"]["Downloads"] = downloadPath

    if(settingFile["Settings"]["Paths"]["Playlist"] == ""):
        playlistPath = input(".Enter a path where to store playlist files <.m3a>: ")
        settingFile["Settings"]["Paths"]["Playlist"] = playlistPath
        
    settingFile = SetOutdatedPath(settingFile)
    WriteJSON(setting_path, settingFile, 'w')

    playlistFile = getDataJSON(playlist_path, "Playlists Informations")
    if(playlistFile == []):
        AddPlaylist(Spotipy_Session)

#download ettings
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

def addInformation(stroption, info, infoList, Settings):
    infoEntered = '.'
    while(infoEntered not in infoList):
        infoEntered = input(f"{stroption} chosen (Press <Enter>, If you don't wish to change the {stroption}): ")
        if(infoEntered == ""):
            Settings["Settings"][stroption] = info
            break
    return Settings

#Select which action the user wants
def SelectCommand(Spotipy_Session): 
    printLoad(19, 42) #Printing for the user
    
    answer = input("Choose the number of the command: ")

    if(answer == "1"): #Enter Playlists Informations
        AddPlaylist(Spotipy_Session)

    elif(answer == "2"): 
        #Downloads newly added songs and Refresh playlists
        #And move Outdated Playlists to the Outdated folder
        #It keeps a version of each playlist
        RefreshPlaylistFile(Spotipy_Session)
        Downloads()  
        PlaylistUpdate()

    elif(answer == "3"):
        SavifyPlaylists = ReadFILE(playlist_path)["Playlists Informations"]
        for playlist, counter in zip(SavifyPlaylists, range(1, len(SavifyPlaylists) + 1)):
            playlistLink = playlist[list(playlist.keys())[0]]["Links"]["URL"]
            printPlaylist(counter, len(SavifyPlaylists), playlistLink,  Spotipy_Session)

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
            
            if(sysOs != "Linux") and (downloadPath != ''):
                Settings["Paths"]["Downloads"] = downloadPath.replace(r"\"", "\\")
            elif(downloadPath != ''):
                Settings["Paths"]["Downloads"] = downloadPath
            
            WriteJSON(setting_path, Settings, 'w')

        elif(answer == "4"):
            settingplaylist_path = Settings["Paths"]["Playlist"]
            PlaylistPath = input(f"\nCurrently the Playlist path is: {settingplaylist_path} \nNew Playlist path (Press <Enter>, If you don't wish to change the path): ")
            
            if(sysOs != "Linux"):
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
Spotipy_Session = SpotipySession()
Load(Spotipy_Session)
while(True):
    SelectCommand(Spotipy_Session)