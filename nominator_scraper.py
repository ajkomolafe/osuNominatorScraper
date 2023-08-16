import requests
import ossapi as osu
import time
from bs4 import BeautifulSoup
from collections import OrderedDict
from os import path

clientID = ""
clientSecret = ""

with open(path.join(path.dirname(__file__),"client_id.txt")) as cIDFile:
    clientID = cIDFile.readline()
with open(path.join(path.dirname(__file__),"client_secret.txt")) as cSecFile:
    clientSecret = cSecFile.readline()
    
api = osu.OssapiV2(clientID, clientSecret)

def scrapeNominator(setID):
    """
    Takes in a beatmapset's ID and returns the usernames of people that nominated the mapset.
    
    setID : Integer or String ID of the beatmapset.

    Returns nomIDs : List of a beatmapset's nominators IDs.
    """
    homeUrl = "https://osu.ppy.sh/beatmapsets/"
    setUrl = homeUrl + str(setID)
    setHTML = requests.get(setUrl)
    setCode = BeautifulSoup(setHTML.text,features="html.parser").prettify()#.split("\n")
    
    currentNoms = setCode[setCode.find("current_nominations"):]
    currentNoms = currentNoms[0:currentNoms.find("current_user_attributes")]
    
    nomIDs = []
    while (currentNoms.find("\"user_id\"") > 0):
        firstNomInfo = currentNoms[currentNoms.find("\"user_id\""):currentNoms.find("}")]
        currentNoms = currentNoms[currentNoms.find("\"user_id\"")+len(firstNomInfo)+1:]
        nomIDs += [firstNomInfo[firstNomInfo.find(":")+1:]]
        
    nomUsers = []
    for i in nomIDs:
        try:
            nomUsers += [api.user(int(i)).username]
        except:
            print("One of these users doesn't exist")
            nomUsers += [f"Deleted User_{str(i)}"]
            
    return nomUsers
        
#main
userID = api.user(input("Type in your username or ID")).id
    
mapCount = api.user(userID).ranked_beatmapset_count
counter = mapCount
page = 0
beatmaps = api.user_beatmaps(user_id=userID,type_="ranked",offset=str(page))
totalNomUserList = []

while counter > 0:
    for i in range(len(beatmaps)):
        setID = beatmaps[i].id
        nomUserList = scrapeNominator(setID)
        print(f"{mapCount-counter+1}: {beatmaps[i].title}'s nominators are: {nomUserList}")
        counter -= 1
        page += 1
        for i in nomUserList:
            totalNomUserList += [i]
    if (counter>1):
        print("Next page")
    beatmaps = api.user_beatmaps(user_id=userID,type_="ranked",offset=str(page))
    
usernameOcc = {} #occurences
for i in totalNomUserList:
    if i not in usernameOcc:
        usernameOcc.update({i:totalNomUserList.count(i)})

usernameOccSort = OrderedDict(sorted(usernameOcc.items(), key=lambda x: x[1],reverse=True))
for i in usernameOccSort:
    print(f"{i}: {usernameOccSort[i]}x")