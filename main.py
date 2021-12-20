#importing Savify
from savify import Savify
from savify.types import Type, Format, Quality
from savify.utils import PathHolder

#importing Spotipy
import spotipy

#importing systemFunctions
import logging, json, shutil, os, fnmatch
from datetime import datetime
from systemFunctions import printLoad, getDataJSON, WriteJSON, ReadFILE
from systemFunctions import convertPath

#Importing playlistHandeling
from playlistHandeling import getPlaylistInformation, SpotipySession


setting_path = "Settings.json"
playlist_path = "Playlist links.json"

#Updates and Add Playlists from the Playlist JSON file
def RefreshPlaylistFile(Spotipy_Session):
    SyncifySettings = getDataJSON(setting_path, "Settings")
    
    playlistFile = ReadFILE(playlist_path)
    playlist_list = []
    for link in playlistFile["Playlists links"]:
        playlist_ID = getPlaylistInformation("ID", link)
        playlist_Name = getPlaylistInformation("Name", link)
        playlist_Image = getPlaylistInformation("Image URL", link)
        playlist_URL = getPlaylistInformation("Playlist URL", link)

        playlist_list.append(
            {
                playlist_Name : {
                    "Image": playlist_Image,
                    "Links": {
                        "URL": playlist_URL,
                        "ID": playlist_ID
                        }
                    }
            }
        )
    
    Playlists = ReadFILE(setting_path)
    Playlists["Playlists"] = playlist_list
    WriteJSON(setting_path, Playlists, 'w')

#Move songs from Music to Newly added music <Coming soon>
def NewlyMusic():
    pass

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
        print("\n\nDownloading from :", playlist_Name)
        
        quality_type = DownloadSettings(Savify)[0]
        download_format = DownloadSettings(Savify)[1]
        
        Session = Savify(quality=quality_type,
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

#Create the playlist
def CreatePlaylist(order):
    SavifySettings = getDataJSON(setting_path, "Settings")
    playlistPath = getDataJSON(setting_path, "Settings/Paths/Playlist")
    
    fileName = convertPath(playlistLocation + "-" + order["Name"] + ".m3u")
    with open(fileName, "w") as playlistm3a:
        playlistm3a.write("#EXTM3U\n")
        for line in order["Order"]:
            playlistm3a.write(line + "\n")
    
#Manage .m3u playlists
def PlaylistManager(Spotipy_Session, playlist_id):
    SavifySettings = getDataJSON(setting_path, "Settings")
    downloadLocation = getDataJSON(setting_path, "Settings/Paths/Downloads")
    playlist = Spotipy_Session.playlist(playlist_id)
    
    pl_order = {"Name": playlist["name"], "Order": []}
    for i in range(0, len(playlist["tracks"]["items"])):
        pl_order["Order"].append(str(downloadLocation)+ "\\" + playlist["tracks"]["items"][i]["track"]["artists"][0]["name"] + ' - ' + playlist["tracks"]["items"][i]["track"]["name"] + '.' + SavifySettings["Format"].lower())
    return pl_order     
          
#Store the old playlists in a folder with a date in it
def PlaylistMove():
    SavifySettings = ReadFILE(setting_path)["Settings"]
    plsLocation = SavifySettings["Paths"]["Playlist"]
    folderLocation = SavifySettings["Paths"]["Outdated Playlists"] + "\\" +datetime.now().strftime("%Y-%m-%d (%Hh.%Mm)")

    for file in os.listdir(plsLocation):
        if((file == "desktop.ini") or (file == "Outdated Playlists")) == False:
            try:
                os.makedirs(folderLocation)    
            except FileExistsError:
                pass 
            shutil.move(plsLocation + "\\" + file, folderLocation + "\\" + file)

#updating the playlists
def PlaylistUpdate():  
    PlaylistMove()  
    SavifyPlaylists = ReadFILE(setting_path)["Playlists"]
    pl_ids = []
    for playlist in SavifyPlaylists:
        for key in playlist.keys():
            pl_ids.append(playlist[key]["Links"]["ID"])
            
    for pl_id in pl_ids:
        pl_order = PlaylistManager(Spotipy_Session, pl_id)
        CreatePlaylist(pl_order)
    print("\n>All playlist files are created.")

#Print the load text, load the savify client
def Load(Spotipy_Session):
    loadText, lines = ReadFILE("loadtext.txt"), ""
    for line in loadText[:18]:
        lines += line
    print(lines)

    SavifyFile = ReadFILE(setting_path)

    if(SavifyFile["Settings"]["Paths"]["Downloads"] == ""):
        downloadPath = input(".Enter a path where to store downloaded music: ")
        SavifyFile["Settings"]["Paths"]["Downloads"] = downloadPath

    if(SavifyFile["Settings"]["Paths"]["Playlist"] == ""):
        playlistPath = input(".Enter a path where to store playlist files <.m3a>: ")
        SavifyFile["Settings"]["Paths"]["Playlist"] = playlistPath

    if(SavifyFile["Playlists"] == []):
        AddPlaylist(Spotipy_Session)
        
    SavifyFile = SetOutdatedPath(SavifyFile)
    
    with open(setting_path, 'w') as outfile:
        json.dump(SavifyFile, outfile, indent=4)
    

#Settings
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

#Select which action the user wants
def SelectCommand(Spotipy_Session): 
    printLoad(0, 19)
    
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
        printLoad(29, 38)

        ans4 = input("Choose the number of the command: ")
        Settings = ReadFILE(setting_path)
        if(ans4 == "1"):
            print("\nCurrently the download quality is: " + Settings["Settings"]["Quality"] + "\nAvailable qualities: BEST, 320K, 256K, 192K, 128K, 96K, 32K, WORST")
            quality, qualities = "", ["BEST", "320K", "256K", "192K", "128K", "96K", "32K", "WORST"]
            while((quality in qualities) == False):
                quality = input("Quality chosen (Press <Enter>, If you don't wish to change the quality): ")
            if(quality != ""):
                Settings["Settings"]["Quality"] = quality
            with open(setting_path, 'w') as file:
                json.dump(Settings, file, indent=4)

        elif(ans4 == "2"):
            print("\nCurrently the download format is: " + Settings["Settings"]["Format"] + "\nAvailable formats: WAV, VORBIS, OPUS, M4A, FLAC, AAC, MP3")
            formate, formats = "", ["WAV", "VORBIS", "OPUS", "M4A", "FLAC", "AAC", "MP3"]
            while((formate in formats) == False):
                formate = input("Format chosen (Press <Enter>, If you don't wish to change the format): ")
            if(formate != ""):
                Settings["Settings"]["Format"] = formate
            with open(setting_path, 'w') as file:
                json.dump(Settings, file, indent=4)

        elif(ans4 == "3"):
            if(Settings["Paths"]["Downloads"] == ""):
                downloadPath = input("\nCurrently the download path is empty, please enter a path: ")
                Settings["Paths"]["Downloads"] = downloadPath.replace(r"\"", "\\")
            else:
                downloadPath = input("\nCurrently the download path is: ", (Settings["Paths"]["Downloads"].replace("\\", r"\"")).replace('"', ''), "\nNew download path (Press <Enter>, If you don't wish to change the path): ")
                Settings["Paths"]["Downloads"] = downloadPath.replace(r"\"", "\\")
            with open(setting_path, 'w') as file:
                json.dump(Settings, file, indent=4)

        elif(ans4 == "4"):
            if(Settings["Paths"]["Playlist"] == ""):
                PlaylistPath = input("\nCurrently the Playlist path is empty, please enter a path: ")
                Settings["Paths"]["Playlist"] = PlaylistPath.replace(r"\"", "\\")
            else:
                PlaylistPath = input("\nCurrently the Playlist path is: ", (Settings["Paths"]["Playlist"].replace("\\", r"\"")).replace('"', ''), "\nNew Playlist path (Press <Enter>, If you don't wish to change the path): ")
                Settings["Paths"]["Playlist"] = PlaylistPath.replace(r"\"", "\\")
            with open(setting_path, 'w') as file:
                json.dump(Settings, file, indent=4)

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