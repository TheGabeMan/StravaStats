import requests
import time
import json
import os

def get_athlete_info( strava_token ):    
    ## Read Athlete info to find FTP
    athlete_url = "https://www.strava.com/api/v3/athlete" + "?access_token=" + str( strava_token )

    readAthlete = requests.get(athlete_url)
    Athlete = readAthlete.json()
    if "message" in Athlete:
        print( "Authorization error")
        exit()
    if len(Athlete) == 0:
        exit("No athlete found.")
    else:
        print("Athlete info found: " + Athlete["firstname"] + " " + Athlete["lastname"] + " FTP waarde: " + str(Athlete["ftp"]) )
        return Athlete

def epochHistory(daysHistory):
    return (round(time.time() - (daysHistory * 86400)))

def get_athlete_activities( daysHistory, strava_token ):
    ## Activities are read per page. To make sure we have all activities at once, we call for daysHistory x 2 
    ## because potentially we could have daysHistory days of 2 activities per day
    ## Bigger numbers could also be true, but we'll see about that later.

    url = "https://www.strava.com/api/v3/athlete/activities?after=" + str( epochHistory(daysHistory) ) + "&per_page=" + str(daysHistory*2) + "&access_token=" + str( strava_token )

    # Get last activities from Strava
    readStrava = requests.get(url)
    ListOfActivities = readStrava.json()
    if len(ListOfActivities) == 0:
        exit("Error reading activities. Stop")
    else:
        print('Number of activities read: ', len(ListOfActivities))
        return ListOfActivities
