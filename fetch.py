import requests
import json
import time

tokenfile = "tokens.json"
credentialsFile = "credentials.json"
activitiesFile = "activities.json"

tokens = json.load(open(tokenfile))
credentials = json.load(open(credentialsFile))
localActivities:list = json.load(open(activitiesFile))

def refreshTokens():
    body = {
        "client_id": credentials.get("client_id"),
        "client_secret": credentials.get("client_secret"),
        "grant_type": "refresh_token",
        "refresh_token": tokens.get("refresh_token")
    }
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    resp = requests.post("https://www.strava.com/oauth/token", data=json.dumps(body), headers=headers)
    new_tokens = json.loads(resp.text)
    return new_tokens

def getAccessToken():
    global tokens
    if tokens.get("expires_at") < (time.time()):
        # REFRESH TOKENS
        print("Token Expired. Requesting new Token.")
        tokenResponse = refreshTokens()
        if("access_token" not in tokenResponse): 
            print("ERROR: Could not refresh tokens")
            return None
        print("New Token: " + tokenResponse["access_token"])
        json.dump(tokenResponse, open(tokenfile, mode="w"))
        tokens = tokenResponse
        return tokens["access_token"]
    else:
        print("Using Token: " + tokens["access_token"])
        return tokens["access_token"]
    
def fetchActivities(page, per_page=100):
    accessToken = getAccessToken()
    headers = {
        'accept': 'application/json',
        'authorization': "Bearer " + accessToken
    }
    resp = requests.get("https://www.strava.com/api/v3/athlete/activities?page="+str(page)+"&per_page="+str(per_page), headers=headers)
    fetched = json.loads(resp.text)
    return fetched

def updateLocalActivities():
    lastLocalID = localActivities[0]["id"]
    activitiesToAdd = []
    page = 1
    finished = False
    while not finished:
        batch = fetchActivities(page, 50)
        for b in batch:
            if b["id"] == lastLocalID:
                finished = True
                break
            else:
                activitiesToAdd.insert(0,b)
        page = page + 1 
    print("ADDING:")
    for i in activitiesToAdd:
        print(" -"+str(i["id"]))
        localActivities.insert(0, i)
    
    json.dump(localActivities, open(activitiesFile, "w"))
    print("DONE")

def removeLocalActivities(num):
    for i in range(num):
        rem = localActivities.pop(0)
        print(rem["id"])
    json.dump(localActivities, open(activitiesFile, "w"))

if __name__ == "__main__":
    updateLocalActivities()


