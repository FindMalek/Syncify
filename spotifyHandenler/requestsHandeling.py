import requests, base64, json

#Importing the Client_ID and Client_Secret
from spotifyHandenler.systemHandeling import *


#From Text to base64
def convertBase64(string):
    string_byte = string.encode('ascii')
    base64_byte = base64.b64encode(string_byte)
    base64_string = base64_byte.decode('ascii')
    return base64_string

#Get access token
def getAccessToken(CLIENT_ID, CLIENT_SECRET):
    authURL = "https://accounts.spotify.com/api/token"
    authHeader = {}
    authData = {}
    base64Client = convertBase64(f"{CLIENT_ID}:{CLIENT_SECRET}")
    
    authHeader["Authorization"] = "Basic " + base64Client
    authData["grant_type"] = "client_credentials"
    responseObj = requests.post(authURL, headers=authHeader, data=authData).json()
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

if __name__ == '__main__':
    token = getAccessToken(CLIENT_ID, CLIENT_SECRET)