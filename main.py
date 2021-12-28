#importing Savify
from savify import Savify
from savify.types import Type, Format, Quality
from savify.utils import PathHolder
from savify.logger import Logger

#importing Spotipy
import spotipy

#importing systemFunctions
import logging, json, shutil, os, fnmatch
from datetime import datetime
from Functions.systemFunctions import printLoad, getDataJSON, WriteJSON, ReadFILE
from Functions.systemFunctions import convertPath, SetOutdatedPath, isFilePlaylist, movePlaylists
from Functions.systemFunctions import DownloadSettings

#Importing playlistHandeling
from Functions.playlistHandeling import getPlaylistInformation, SpotipySession, RefreshPlaylistFile
from Functions.playlistHandeling import CreatePlaylist, PlaylistManager


setting_path = "Settings.json"
playlist_path = "Playlist links.json"

#Downloader
def Downloads():
    #Get time before downloading the music and then compare every
    #music that its created time is later than that time and move it to
    #newly downloaded music  <Coming Soon>
    
    Playlists = getDataJSON(setting_path, "Playlists")
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
def printPlaylist(link, Spotipy_Session):
    playlist_ID = "spotify:playlist:" + link[link.find("playlist/") + len("playlist/"):]
    Result = Spotipy_Session.playlist(playlist_ID)

    print("\n\t"+ Result["name"]
            + "\n.Description: " + Result["description"]
            + "\n.Number of tracks: " + str(len(Result["tracks"]["items"]))
            + "\n.Owner: " + Result["owner"]["display_name"]
            + "\n")

#Add playlist link in the json file playlist links.json
def AddLink(list):
    playlistLinks = ReadFILE(playlist_path)
    for link in list:
        if(link in playlistLinks["Playlists links"]) == False:
            playlistLinks["Playlists links"].append(link)

    WriteJSON(playlist_path, playlistLinks, 'w')

#Add playlists to the settings.json "Playlists"
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
    
    playlist_list = getDataJSON(setting_path, "Playlists")
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

    if(settingFile["Playlists"] == []):
        AddPlaylist(Spotipy_Session)
        
    settingFile = SetOutdatedPath(settingFile)
    WriteJSON(setting_path, settingFile, 'w')

#Select which action the user wants
def SelectCommand(Spotipy_Session): 
    printLoad(19, 42)
    
    answer = input("Choose the number of the command: ")

    if(answer == "1"):
        AddPlaylist(Spotipy_Session)

    elif(answer == "2"):
        RefreshPlaylistFile(Spotipy_Session)
        Downloads()  
        PlaylistUpdate()

    elif(answer == "3"):
        SavifyPlaylists = ReadFILE(setting_path)["Playlists"]
        for playlist in SavifyPlaylists:
            printPlaylist(playlist[list(playlist.keys())[0]]["Links"]["URL"], Spotipy_Session)
            pause = input("Next playlist (Press <Enter>)")

    elif(answer == "4"):
        printLoad(29, 37)

        ans4 = input("Choose the number of the command: ")
        Settings = ReadFILE(setting_path)
        sysOs = getDataJSON(setting_path, "System Os")
        
        if(ans4 == "1"):
            print("\nCurrently the download quality is: " + Settings["Settings"]["Quality"] + "\nAvailable qualities: BEST, 320K, 256K, 192K, 128K, 96K, 32K, WORST")
            
            quality, qualities = "", ["BEST", "320K", "256K", "192K", "128K", "96K", "32K", "WORST"]
            while(((quality in qualities) == False) or (quality == '')):
                quality = input("Quality chosen (Press <Enter>, If you don't wish to change the quality): ")
            if(quality != ""):
                Settings["Settings"]["Quality"] = quality
            
            WriteJSON(setting_path, Settings, 'w')

        elif(ans4 == "2"):
            print("\nCurrently the download format is: " + Settings["Settings"]["Format"] + "\nAvailable formats: WAV, VORBIS, OPUS, M4A, FLAC, AAC, MP3")
            formate, formats = "", ["WAV", "VORBIS", "OPUS", "M4A", "FLAC", "AAC", "MP3"]
            while((formate in formats) == False):
                formate = input("Format chosen (Press <Enter>, If you don't wish to change the format): ")
            if(formate != ""):
                Settings["Settings"]["Format"] = formate
            
            WriteJSON(setting_path, Settings, 'w')

        elif(ans4 == "3"):
            if(Settings["Paths"]["Downloads"] == ""):
                downloadPath = input("\nCurrently the download path is empty, please enter a path: ")
                
                if(sysOs != "Linux"):
                    Settings["Paths"]["Downloads"] = downloadPath.replace(r"\"", "\\")
                else:
                    Settings["Paths"]["Downloads"] = downloadPath
            else:
                downloadPath = input("\nCurrently the download path is: ", (Settings["Paths"]["Downloads"].replace("\\", r"\"")).replace('"', ''), "\nNew download path (Press <Enter>, If you don't wish to change the path): ")
                
                if(sysOs != "Linux"):
                    Settings["Paths"]["Downloads"] = downloadPath.replace(r"\"", "\\")
                else:
                    Settings["Paths"]["Downloads"] = downloadPath
                    
            WriteJSON(setting_path, Settings, 'w')

        elif(ans4 == "4"):
            if(Settings["Paths"]["Playlist"] == ""):
                PlaylistPath = input("\nCurrently the Playlist path is empty, please enter a path: ")
                
                if(sysOs != "Linux"):
                    Settings["Paths"]["Playlist"] = PlaylistPath.replace(r"\"", "\\")
                else:
                    Settings["Paths"]["Playlist"] = PlaylistPath
            else:
                PlaylistPath = input("\nCurrently the Playlist path is: ", (Settings["Paths"]["Playlist"].replace("\\", r"\"")).replace('"', ''), "\nNew Playlist path (Press <Enter>, If you don't wish to change the path): ")
                
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