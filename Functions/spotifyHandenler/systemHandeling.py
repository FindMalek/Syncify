import os

def addEnv():
    clientId = input("-> Input 'SYNCIFY_CLIENT_ID': ")
    clientSecret = input("-> Input 'SYNCIFY_CLIENT_SECRET': ")
    
    os.environ['SYNCIFY_CLIENT_ID'] = clientId
    os.environ['SYNCIFY_CLIENT_SECRET'] = clientSecret

def checkExist():
    try:
        CLIENT_ID = os.getenv('SYNCIFY_CLIENT_ID')
        CLIENT_SECRET = os.environ.get('SYNCIFY_CLIENT_SECRET')
    except KeyError:
        print("Error Environment: 'SYNCIFY_CLIENT_ID' and 'SYNCIFY_CLIENT_SECRET' are not set as environment variables")
        rep = input("\nDo you want to enter environment variables? (y/n): ")
        if(rep.lower() == 'y'):
            addEnv()
        exit()
        
if __name__ == '__main__':
    checkExist()
    CLIENT_ID = os.getenv('SYNCIFY_CLIENT_ID')
    CLIENT_SECRET = os.environ.get('SYNCIFY_CLIENT_SECRET')