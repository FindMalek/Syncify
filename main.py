""" 
    CHANGES:
        
        1.(No progress)     Change the object of 'userData.json' format.
        (Those elements inside the 'Playlists', 'Albums' and 'Tracks')
        This will automatically fix unique data as well.
        It will be:
        {
            "ID": {
                "Image": link,
                "Owner": name,
                "Creation date": date
            }
        }
        
        2. (No progress) Add genre.
        Add genre in the meta-data of each track, using an API.
        
        3. (No progress) Add the option to modify the 'Settings.json'
        There are a lot of settings, the user can't change, through Syncify CLI.
        "Sleep" : Sleeping between an error,
        "Time Difference" : The search interval of a track (+- Time Difference),
        "Search Accuracy" : Recommended to keep it at 5 or 6,
        "Download Order" : The order of downloading.
        
        4. (In progress) Add not-found tracks.
        They are some tracks are in 'Spotify' and not in 'Youtube' or they are in 'Youtube' but my algorithm did'nt
        catch them. So I'll make a file that will store every Spotify Id of these tracks and their Youtube search.
        
        5. (In progress) A search algorithm for 'Yewtu.be'.
        Creating a search for track module for 'Yewtu.be' to avoid the bug of Age-Restricted.
        
        6. (In progress) Improving the 'Youtube' search algorithm.
        If the Track name in Spotify matches by 80% (or more) the one in 'Youtube', it will approve it.
    
    BUGS:
    
        1. (In progress) In playlist creation.
        It calls non-existant tracks. When calling for a track, their path is wrong.
        
        2. (In progress) Bypass Age-Restricted Videos.
        Some Youtube videos are Age-Restricted and to get away with that you must Login.
        
        3. (Done) Deleting Albums and Tracks after downloading.
        Syncify is now able to delete them, because it's useless to keep them.
"""

__title__ = "Syncify"
__author__ = "Malek Gara-Hellal"
__email__ = 'malekgarahellalbus@gmail.com'
__version__ = '1.1.3.1'


#importing systemFunctions
import logging, json, shutil, os, fnmatch, datetime
from SyncifyFunctions.systemFunctions import * 

#Importing spotifyHandeler
from spotifyHandler.requestsHandeling import *

#Setting up needed files
SettingUp()
setting_path = "Settings.json"
userdata_path = convertPath("Data/userData.json")
logsSyncify.debug("Function - SettingUp & & Prepaths are set.")

#Importing Syncify downloadHandler
from downloadHandler.audioManager import *
from downloadHandler.audioDownloader import *
logsSyncify.debug("Syncify downloadHandler module is imported.")

#Importing playlistHandeling
from SyncifyFunctions.playlistHandeling import *

#Importing trackHandeling
from SyncifyFunctions.trackHandeling import *
logsSyncify.debug("Imported all modules and packages.")

#Downloader
def Downloads(syncifyToken, playlistURLs):
    for url in playlistURLs:
        trackFormat = trackInformation(syncifyToken, url)
        trackData = track(syncifyToken, url[url.find('track/') + len('track/'):])

        if(trackDownloaded(trackData) == False):
            searchTrachData = algorithmSearchTrack(trackData)
            if(searchTrachData["Result"][0] == True):
                logsSyncify.info(f"Downloading > {trackFormat[:-4]}...")
                downloadTrack(searchTrachData, trackData)
                logsSyncify.info(f"Downloaded -> {trackFormat[:-4]}.")

        else:
            logsSyncify.debug("Track already exists in your Music Library.")   
    
#print Playlist / Album / Track informations
def printObject(link, syncifyToken):
    logsSyncify.message("\n\n_______________________________________")
    
    #If the link is a Playlist Link
    if(whatIsLink(link) == "Playlist"):
        playlistId = link[link.find("playlist/") + len("playlist/"):]
        tries = 0
        while True:
            try:
                Result = playlist(syncifyToken, playlistId)
                break
            except Exception:
                logsSyncify.warning(f"({nbTries}) Error -> Couldn't get result of {playlistId}. Sleeping for {getDataJSON(setting_path, 'Settings/Sleep')}")
                
                tries = triesCounter(tries)
                if(tries == False):
                    logsSyncify.critical(f"Number of tries exceeded 5. Quitting")
                    quit()
                    
                time.sleep(getDataJSON("Settings.json", "Settings/Sleep"))
                
        logsSyncify.message(f"\t-(Playlist)-\nName: {Result['name']}\n\n{Result['description']}\n{Result['owner']['display_name']} • {len(Result['tracks']['items'])} songs.")
        
    #If the link is an Album Link
    elif(whatIsLink(link) == "Album"):
        albumID = link[link.find("album/") + len("album/"):]
        while True:
            try:
                Result = album(syncifyToken, albumID)
                break
            except Exception:
                logsSyncify.warning(f"({nbTries}) Error -> Couldn't get result of {albumID}. Sleeping for {getDataJSON(setting_path, 'Settings/Sleep')}")
                
                tries = triesCounter(tries)
                if(tries == False):
                    logsSyncify.critical(f"Number of tries exceeded 5. Quitting")
                    quit()
                    
                time.sleep(getDataJSON("Settings.json", "Settings/Sleep"))  
        logsSyncify.message(f"\t-(Album)-\nName: {Result['name']}\n{Result['artists'][0]['name']} • {len(Result['tracks']['items'])} songs.")
    
    #If the link is a Track Link
    elif(whatIsLink(link) == "Track"):
        trackID = link[link.find("track/") + len("track/"):]
        while True:
            try:
                Result = track(syncifyToken, trackID)
                break
            except Exception:
                logsSyncify.warning(f"({nbTries}) Error -> Couldn't get result of {trackID}. Sleeping for {getDataJSON(setting_path, 'Settings/Sleep')}")

                tries = triesCounter(tries)
                if(tries == False):
                    logsSyncify.critical(f"Number of tries exceeded 5. Quitting")
                    quit()
                    
                time.sleep(getDataJSON("Settings.json", "Settings/Sleep"))  
        logsSyncify.message(f"\t-(Track)-\nName: {Result['name']}\nArtist(s): {getArtists(Result)}\nTrack number: {Result['track_number']}\nDuration: {datetime.datetime.fromtimestamp(int(Result['duration_ms']) / 1000).strftime('%M:%S')}")
    logsSyncify.message("_______________________________________")

#Add Albums, Playlists and Tracks to userData.json
def addObject(syncifyToken, link):
    objectResult = getObjectInformation(syncifyToken, link)
    objects = ReadFILE(userdata_path)
    
    if(whatIsLink(link) == "Album"):
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
        obj = {
            str(objectResult[0]["album"]["artists"][0]["name"] + ' - ' + objectResult[0]["name"]) : {
                "Image" : objectResult[0]["album"]["images"][0]["url"],
                "Links" : {
                    "URL": link,
                    "ID": link[link.find("track/") + len("track/"):]
                }
            }
        }
        objects["Tracks"].append(obj)
        
    #Add the new objects
    WriteJSON(userdata_path, objects, 'w')

#Enter Playlist / Album / Track to the "UserData.json"
def enterObject(syncifyToken):
    while True:
        link = input("\n-> Enter link (Album / Playlist / Track) or <Enter> to skip: ")
        
        if(link == ''):
            logsSyncify.message("=> Nothing has been entered!")
            break   
            
        if('?' in link):
            link = link[:link.find('?')]
            
        #Print the name of the playlist / album / track and the description
        logsSyncify.debug(f"Printing Album / Playlist / Track -> {link}")
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
        logsSyncify.debug(f"Changed the download path -> {downloadPath}")

    if(settingFile["Settings"]["Paths"]["Playlist"] == ""):
        playlistPath = input(".Enter a path where to store playlist files <.m3a>: ")
        settingFile["Settings"]["Paths"]["Playlist"] = playlistPath
        logsSyncify.debug(f"Changed the playlist path -> {playlistPath}")

    WriteJSON(setting_path, settingFile, 'w')

    if((getDataJSON(userdata_path, "Playlists") == []) and (getDataJSON(userdata_path, "Albums") ==  []) and (getDataJSON(userdata_path, "Tracks") == [])):
        logsSyncify.debug(f"Adding links to {userdata_path}.")
        enterObject(syncifyToken)

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

    logsSyncify.debug(f"Quality -> {qual}. Format -> {SavifySettings['Format'].lower()}")
    return qual, SavifySettings["Format"].lower()

#Select which action the user wants
def SelectCommand(syncifyToken): 
    printLoad(19, 44) #Printing for the CLI
    
    answer = input("Choose the number of the command: ")

    if(answer == "1"):
        logsSyncify.debug("Adding and updating Playlists / Albums / Tracks...")
        enterObject(syncifyToken)
        logsSyncify.debug("Added and updated Playlists / Albums / Tracks.")

    elif(answer == "2"): 
        downloadPath = getDataJSON(setting_path, "Settings/Paths/Downloads")
        logsSyncify.debug(f"downloadPath = {downloadPath}")
        
        """
            4.(No progress)     Change the order of downloading Albums / Tracks / Playlists.
            By default it will be Playlists -> Albums -> Tracks.
            (Next updates...) But the user will be able to change it, using an order system.
            Add in the 'Settings.json' ->  "Download Order": ["Playlists", "Albums", "Tracks"] (Default)
        """
        downloadOrder = getDataJSON(setting_path, "Settings/Download Order")
        
        for elementOrder in downloadOrder:
            downloadableObjs = getDataJSON(userdata_path, elementOrder)
            
            logsSyncify.debug(f"> Downloading {elementOrder} began...")
            for obj in downloadableObjs:
                objName = str(list(obj.keys())[0])
                trackURLs = getTracks(syncifyToken, obj[objName]["Links"]["ID"], obj[objName]["Links"]["URL"])
                
                logsSyncify.info(f"\n\n\tDownloading from : {objName}")
                Downloads(syncifyToken, trackURLs)  
                logsSyncify.info(f"\tDownloaded -> {objName}\n")
            
                #Creating playlist
                if(whatIsLink(obj[objName]["Links"]["URL"]) == "Playlist"):
                    plOrdered = PlaylistManager(syncifyToken, obj[objName]["Links"]["ID"], obj[objName]["Links"]["URL"])
                    CreatePlaylist(plOrdered)
                    logsSyncify.debug(f"Created playlist -> {objName}")

                #Deleting Albums from "userData.json" to optimize the speed of the execution
                if(elementOrder in ['Tracks', 'Albums']):
                    popTmpObject(obj, elementOrder)
            
        logsSyncify.info("\n>Downloading all tracks is finished! All playlists are saved.")
        logsSyncify.debug(f"Deleted Albums / Tracks links from '{userdata_path}' for optimization.")

    elif(answer == "3"):
        answer = input("These are your options:\n\t1. Playlists\n\t2. Albums\n\t3. Tracks\nChoose the number of the command: ")
        syncifyObjs = ReadFILE(userdata_path)
        
        if(answer == "1"):
            if(syncifyObjs["Playlists"] == []):
                logsSyncify.message("-> There's 0 Playlists! Add Playlists first.")
            for obj in syncifyObjs["Playlists"]:
                printObject(obj[str(list(obj.keys())[0])]["Links"]["URL"], syncifyToken)
        
        elif(answer == "2"):
            if(syncifyObjs["Albums"] == []):
                logsSyncify.message("-> There's 0 Albums! Add Albums first.")
            for obj in syncifyObjs["Albums"]:
                printObject(obj[str(list(obj.keys())[0])]["Links"]["URL"], syncifyToken)
        
        elif(answer == "3"):
            if(syncifyObjs["Tracks"] == []):
                logsSyncify.message("-> There's 0 Tracks! Add Tracks first.")
            for obj in syncifyObjs["Tracks"]:
                printObject(obj[str(list(obj.keys())[0])]["Links"]["URL"], syncifyToken)
        input()

    elif(answer == "4"):
        printLoad(29, 39)

        answer = input("Choose the number of the command: ")
        Settings = ReadFILE(setting_path)
        sysOs = getDataJSON(setting_path, "System Os")
        
        if(answer == "1"):
            quality = Settings["Settings"]["Quality"]
            qualityList = ["BEST", "320K", "256K", "192K", "128K", "96K", "32K", "WORST"]
            logsSyncify.info(f"\nCurrently the download quality is: {quality}\nAvailable qualities: {qualityList}")
            
            Settings = addInformation("Quality", quality, qualityList, Settings)
            WriteJSON(setting_path, Settings, 'w')

        elif(answer == "2"):
            formatType = Settings["Settings"]["Format"]
            formatList = ["WAV", "VORBIS", "OPUS", "M4A", "FLAC", "AAC", "MP3"]
            logsSyncify.info(f"\nCurrently the download format is: {formatType}\nAvailable formats: {formatList}")
            
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
            """
            1. Playlists  |
            2. Albums     |
            3. Tracks     |
            """
            downloadOrder = input(f"\nCurrently the Download Order is: {Settings['Settings']['Download Order']}\nNew download order (Press <Enter>, If you don't wish to change the order): \n")
            logsSyncify.message("<This command is coming in the next updates...>")
        
        elif(answer == "5"):
            settinguserdata = Settings["Paths"]["Playlist"]
            PlaylistPath = input(f"\nCurrently the Playlist path is: {settinguserdata} \nNew Playlist path (Press <Enter>, If you don't wish to change the path): ")
            
            if(sysOs.lower() != "linux"):
                Settings["Paths"]["Playlist"] = PlaylistPath.replace(r"\"", "\\")
            else:
                Settings["Paths"]["Playlist"] = PlaylistPath
                
            WriteJSON(setting_path, Settings, 'w')

    elif(answer == "5"):
        logsSyncify.message("<This command is coming in the next updates...>")
        input("")

    elif(answer == "6"):
        logsSyncify.info("<Exit>")
        logsSyncify.debug("Deleting temporary files...")
        deleteTemporaryFiles(os.getcwd())
        logsSyncify.debug("Deleted temporary files.")
        quit()

if __name__ == '__main__':
    logsSyncify.debug("Getting (CLIENT_ID, CLIENT_SECRET)...")
    syncifyToken = getAccessToken(CLIENT_ID, CLIENT_SECRET)
    logsSyncify.debug("Got (CLIENT_ID, CLIENT_SECRET).")

    Load(syncifyToken)
    while(True):
        logsSyncify.debug("Deleting temporary files...")
        deleteTemporaryFiles(os.getcwd())
        logsSyncify.debug("Deleted temporary files.")
        
        logsSyncify.debug("Selecting command...")
        SelectCommand(syncifyToken)