import requests, base64, json

#Importing the Client_ID and Client_Secret
from spotifyHandler.systemHandeling import *

#Importing the systeme Handeling
from SyncifyFunctions.systemFunctions import *


#From Text to base64
def convertBase64(string):
    string_byte = string.encode('ascii')
    base64_byte = base64.b64encode(string_byte)
    base64_string = base64_byte.decode('ascii')
    return base64_string

#Get access token
def getAccessToken(CLIENT_ID, CLIENT_SECRET):
    logsSyncify.debug(f"Getting Token Access...")
    authURL = "https://accounts.spotify.com/api/token"
    authHeader = {}
    authData = {}
    base64Client = convertBase64(f"{CLIENT_ID}:{CLIENT_SECRET}")
    logsSyncify.debug(f"Converted the CLIENT_ID and CLIENT_SECRET to Base 64.")
    
    authHeader["Authorization"] = "Basic " + base64Client
    authData["grant_type"] = "client_credentials"
    logsSyncify.debug(f"Sending a POST REQUEST to {authURL} for Token Acess...")
    responseObj = requests.post(authURL, headers=authHeader, data=authData).json()
    logsSyncify.debug(f"Sent a POST REQUEST to {authURL} for Token Acess.")
    return responseObj['access_token']

#Gets the result of the API
def spotifyInformations(token, obj, id):
    getHeader = {
        "Authorization": "Bearer " + token
    }
    objEndPoint = f"https://api.spotify.com/v1/{obj}/{id}"
    objRes = requests.get(objEndPoint, headers=getHeader).json()

    return objRes

#Gets Album result 
def album(token, id):
    return spotifyInformations(token, "albums", id)

#Gets Playlists result 
def playlist(token, id):
    return spotifyInformations(token, "playlists", id)

#Gets Tracks result 
def track(token, id):
    return spotifyInformations(token, "tracks", id)    

#Gets Episodes result
def episode(token, id):
    return spotifyInformations(token, "episodes", id)

#Downloads the art of an Object
def downloadArt(link):
    response = requests.get(link, stream=True)
    with open(convertPath("Data/tmpArt.jpg"), 'wb') as tmpArt:
        shutil.copyfileobj(response.raw, tmpArt)
    del response
    return convertPath("Data/tmpArt.jpg")

if __name__ == '__main__':
    logsSyncify.loggingSetup()
    token = getAccessToken(CLIENT_ID, CLIENT_SECRET)