from savify import Savify
from savify.types import Type, Format, Quality
from savify.utils import PathHolder
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import logging, json, shutil, os, fnmatch
from datetime import datetime


setting_path = "Resources\Settings.json"
playlist_path = "Resources\Playlist links.json"

#read any file
def ReadFILE(path, filetype):
    if(filetype.lower() == "txt"):
        with open(path, "r") as file:
            return file.readlines()
    elif(filetype.lower() == "json"):
        with open(path, 'r') as file:
            return json.load(file)

#Set outdated path
def SetPaths():
    Settings = ReadFILE(setting_path, "json")
    outdatedPL_path = Settings["Settings"]["Locations"]["Playlist"] + "\\Outdated Playlists"
    Settings["Settings"]["Locations"]["Outdated Playlists"] = outdatedPL_path
    with open(setting_path, 'w') as outfile:
        json.dump(Settings, outfile, indent=4)

#Opens Savify Client
def SavifyClient(option=""):
    SavifySession = ReadFILE(setting_path, "json")["Savify Session"]
    if (option == "Client ID"):
        return SavifySession["SPOTIPY_CLIENT_ID"]
    
    elif (option == "Client Secret"):
        return SavifySession["SPOTIPY_CLIENT_SECRET"]

#Log in Spotipy_Session
def SpotipySession():
    client_credentials_manager = SpotifyClientCredentials()#Spotify Client
    return spotipy.Spotify(client_credentials_manager = client_credentials_manager)

#Playlist adder/ refresh / update
def RefreshPlaylist(Spotipy_Session):
    SyncifySettings = ReadFILE(setting_path, "json")["Settings"]
    Pl = ReadFILE(playlist_path, "json")
    
    Playlists = ReadFILE(setting_path, "json")
    nPl = []
    for element in Pl["Playlists links"]:
        Pl_id = "spotify:playlist:" + element[element.find("playlist/") + len("playlist/"):]
        Result = Spotipy_Session.playlist(Pl_id)
        Pl_Name = Result["name"]
        Pl_image = Result["images"][0]["url"]
        Pl_url = Result["external_urls"]["spotify"]

        nPl.append(
            {Pl_Name : {"Image": Pl_image,
                                    "Links":
                                        {"URL": Pl_url,
                                                "ID": Pl_id
                                        }
                        }
                    }
                )
        
    Playlists["Playlists"] = nPl
    with open(setting_path, 'w') as outfile:
        json.dump(Playlists, outfile, indent=4)

#Move songs from Music to Newly added music <Coming soon>
def NewlyMusic():
    pass

#Downloader
def Downloads():
    #Get time before downloading the music and then compare every
    # music that its created time is later than that time and move it to
    #newly downloaded music
    Playlists = ReadFILE(setting_path, "json")["Playlists"]
    SyncifySettings = ReadFILE(setting_path, "json")["Settings"]
    counter = 0
    for element in Playlists:
        print("\n\nDownloading from :", str(list(element.keys())[0]))
        Quality = DownloadSettings(Savify)[0]
        download_format = DownloadSettings(Savify)[1]
        PlaylistName = SyncifySettings["Locations"]["Downloads"]
        Session = Savify(quality=Quality,
                         download_format=download_format,
                         path_holder=PathHolder(downloads_path=PlaylistName))
        Session.download(Playlists[counter][str(list(element.keys())[0])]["Links"]["URL"])
        counter += 1
    print("\n>Download is finished! All songs are downloaded.")

#Get the name of the playlist and the discription
def InfoPlaylist(link, Spotipy_Session):
    idPL = "spotify:playlist:" + link[link.find("playlist/") + len("playlist/"):]
    Result = Spotipy_Session.playlist(idPL)

    print("\n-"+ Result["name"]
            + "\n.Description: " + Result["description"]
            + "\n.Number of tracks: " + str(len(Result["tracks"]["items"]))
            + "\n.Owner: " + Result["owner"]["display_name"]
            + "\n")

#Add playlist link in the json file playlist links.json
def AddLink(list):
    playlistLinks = ReadFILE(playlist_path, "json")
    for link in list:
        if(link in playlistLinks["Playlists links"]) == False:
            playlistLinks["Playlists links"].append(link)

    with open(playlist_path, 'w') as f:
        json.dump(playlistLinks, f, indent=4)

#Add playlists to the settings.json "Playlists"
def AddPlaylist(Spotipy_Session):
    link, listPL = ".", []
    while(link != ""):
        link = input("\n.Enter playlist link: ")
        if(link != ""):
            #Print the name of the playlist and the description
            InfoPlaylist(link, Spotipy_Session)
            listPL.append(link[:link.find("?")])
        else:
            print(">No playlist have been entered!")
    AddLink(listPL)

#Create the playlist
def CreatePlaylist(order):
    SavifySettings = ReadFILE(setting_path, "json")["Settings"]
    playlistLocation = SavifySettings["Locations"]["Playlist"]
    
    pl_name = playlistLocation + "\\" + order["Name"] + ".m3u"
    with open(pl_name, "w") as playlistm3a:
        playlistm3a.write("#EXTM3U\n")
        for line in order["Order"]:
            playlistm3a.write(line + "\n")
    
        
#Manage .m3u playlists
def PlaylistManager(Spotipy_Session, pl_id):
    SavifySettings = ReadFILE(setting_path, "json")["Settings"]
    downloadLocation = SavifySettings["Locations"]["Downloads"]
    playlist = Spotipy_Session.playlist(pl_id)
    
    pl_order = {"Name": playlist["name"], "Order": []}
    for i in range(0, len(playlist["tracks"]["items"])):
        pl_order["Order"].append(str(downloadLocation)+ "\\" + playlist["tracks"]["items"][i]["track"]["artists"][0]["name"] + ' - ' + playlist["tracks"]["items"][i]["track"]["name"] + '.' + SavifySettings["Format"].lower())
    return pl_order     
          
#Store the old playlists in a folder with a date in it
def PlaylistMove():
    SavifySettings = ReadFILE(setting_path, "json")["Settings"]
    plsLocation = SavifySettings["Locations"]["Playlist"]
    folderLocation = SavifySettings["Locations"]["Outdated Playlists"] + "\\" +datetime.now().strftime("%Y-%m-%d (%Hh.%Mm)")

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
    SavifyPlaylists = ReadFILE(setting_path, "json")["Playlists"]
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
    loadText, lines = ReadFILE("Resources\loadtext.txt", "txt"), ""
    for line in loadText[:18]:
        lines += line
    print(lines)

    SavifyFile = ReadFILE(setting_path, "json")
    playlists = ReadFILE(playlist_path, "json")

    if(SavifyFile["Savify Session"]["SPOTIPY_CLIENT_ID"] == "") or (SavifyFile["Savify Session"]["SPOTIPY_CLIENT_SECRET"] == ""):
        clientID = input(".Enter your Spotify Client ID: ")
        clientSecret = input(".Enter your Spotify Client Secret: ")

        SavifyFile["Savify Session"]["SPOTIPY_CLIENT_ID"] = clientID
        SavifyFile["Savify Session"]["SPOTIPY_CLIENT_SECRET"] = clientSecret 

    if(SavifyFile["Settings"]["Locations"]["Downloads"] == ""):
        downloadPath = input(".Enter a path where to store downloaded music: ")
        SavifyFile["Settings"]["Locations"]["Downloads"] = downloadPath

    if(SavifyFile["Settings"]["Locations"]["Playlist"] == ""):
        playlistPath = input(".Enter a path where to store playlist files <.m3a>: ")
        SavifyFile["Settings"]["Locations"]["Playlist"] = playlistPath

    if(SavifyFile["Playlists"] == []):
        AddPlaylist(Spotipy_Session)
    
    with open(setting_path, 'w') as outfile:
        json.dump(SavifyFile, outfile, indent=4)
    
    SetPaths()

#Settings
def DownloadSettings(Savify):
    SavifySettings = ReadFILE(setting_path, "json")["Settings"]
    
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
    lines, loadText = "", ReadFILE("Resources\loadtext.txt", "txt")
    for line in loadText[19:]:
        lines += line
    print(lines)
    answer = input("Choose the number of the command: ")

    if(answer == "1"):
        AddPlaylist(Spotipy_Session)

    elif(answer == "2"):
        RefreshPlaylist(Spotipy_Session)
        Downloads()  
        PlaylistUpdate()

    elif(answer == "3"):
        SavifyPlaylists = ReadFILE(setting_path, "json")["Playlists"]
        for playlist in SavifyPlaylists:
            InfoPlaylist(playlist[list(playlist.keys())[0]]["Links"]["URL"], Spotipy_Session)
            pause = input("Next playlist (Press <Enter>)")

    elif(answer == "4"):
        lines = ""
        for line in loadText[29:38]:
            lines += line
        print(lines)

        ans4 = input("Choose the number of the command: ")
        Settings = ReadFILE(setting_path, "json")
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
            if(Settings["Locations"]["Downloads"] == ""):
                downloadPath = input("\nCurrently the download path is empty, please enter a path: ")
                Settings["Locations"]["Downloads"] = downloadPath.replace(r"\"", "\\")
            else:
                downloadPath = input("\nCurrently the download path is: ", (Settings["Locations"]["Downloads"].replace("\\", r"\"")).replace('"', ''), "\nNew download path (Press <Enter>, If you don't wish to change the path): ")
                Settings["Locations"]["Downloads"] = downloadPath.replace(r"\"", "\\")
            with open(setting_path, 'w') as file:
                json.dump(Settings, file, indent=4)

        elif(ans4 == "4"):
            if(Settings["Locations"]["Playlist"] == ""):
                PlaylistPath = input("\nCurrently the Playlist path is empty, please enter a path: ")
                Settings["Locations"]["Playlist"] = PlaylistPath.replace(r"\"", "\\")
            else:
                PlaylistPath = input("\nCurrently the Playlist path is: ", (Settings["Locations"]["Playlist"].replace("\\", r"\"")).replace('"', ''), "\nNew Playlist path (Press <Enter>, If you don't wish to change the path): ")
                Settings["Locations"]["Playlist"] = PlaylistPath.replace(r"\"", "\\")
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