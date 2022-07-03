import os, sys, subprocess

#Add SYNCIFY_CLIENT_ID and SYNCIFY_CLIENT_SECRET env variables
def addEnv():
    clientId = input("-> Input 'SYNCIFY_CLIENT_ID': ")
    clientSecret = input("-> Input 'SYNCIFY_CLIENT_SECRET': ")
    
    os.environ['SYNCIFY_CLIENT_ID'] = clientId
    os.environ['SYNCIFY_CLIENT_SECRET'] = clientSecret
    
#Checks if the env variables exists
def checkExist():
    if((os.getenv('SYNCIFY_CLIENT_ID')) == None or (os.environ.get('SYNCIFY_CLIENT_SECRET') == None)):
        print("Error Environment: 'SYNCIFY_CLIENT_ID' and 'SYNCIFY_CLIENT_SECRET' are not set as environment variables")
        rep = input("\nDo you want to enter environment variables? (y/n): ")
        if(rep.lower() == 'y'):
            addEnv()
        exit()

checkExist()
CLIENT_ID = os.getenv('SYNCIFY_CLIENT_ID')
CLIENT_SECRET = os.environ.get('SYNCIFY_CLIENT_SECRET')