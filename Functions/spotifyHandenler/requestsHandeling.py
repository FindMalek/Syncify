import requests, base64

#Importing the Client_ID and Client_Secret
from systemHandeling import CLIENT_ID, CLIENT_SECRET

#From Text to base64
def convertBase64(string):
    string_byte = string.encode('ascii')
    base64_byte = base64.b64encode(string_byte)
    base64_string = base64_byte.decode('ascii')
    return base64_string

authURL = "https://accounts.spotify.com/api/token"
authHeader = {}
authData = {}

base64Client = convertBase64(f"{CLIENT_ID}:{CLIENT_SECRET}")
print(base64)