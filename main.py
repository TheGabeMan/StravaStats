## Global imports
import time
from datetime import datetime, timedelta, date
import math

## Project files
import secretsfiles
import strava_calls
import calculations

## Get Strava API token
strava_token = secretsfiles.get_strava_token()
## Read Athleteinfo for FTP value
AthleteInfo = strava_calls.get_athlete_info( strava_token )

## To get past 70 (10 weeks) days of activities calculate 'after' date in epochtime. 1 day = 86400 sec
daysHistory = 70
ListOfActivities = strava_calls.get_athlete_activities(daysHistory = daysHistory, strava_token = strava_token)

## Since we need to know of each day if it was a rest day, and therefore no strava activity, we'll cycle through all days between epochHistory (start date) and today
## Startdate is formatted from epoch to datetime.date
startDate = datetime.date( datetime.fromtimestamp( strava_calls.epochHistory(daysHistory) ))
print( "Reading activities starting from ", startDate)

## CTL – Chronic Training Load = Fitness
## ATL – Acute Training Load = Fatigue
## TSB – Training Stress Balance = Form
## DailyProgress will be a list of the training per day. If there were two activities on the same day, they will be combined into one
## DailyProgress = date, start_date_local, name, moving_time, weighted_average_watts, pss, intensityfactor, CTL, ATL, TSB 
DailyProgress = []
## Checking for every date between startDate and today
fitnessdate = startDate
while fitnessdate <= date.today():
    ## Check if fitnessday is found in ListOfActivities
    ## StravaDate = datetime.date( datetime.strptime(activity["start_date_local"], "%Y-%m-%dT%H:%M:%SZ") )
    foundActivities = [x for x in ListOfActivities if datetime.date( datetime.strptime(x["start_date_local"], "%Y-%m-%dT%H:%M:%SZ") ) == fitnessdate ]
    if len(foundActivities) == 0:
        ## Add empty day, calculate Fitness with 0 value
        ## DailyProgress = date, start_date_local, name, moving_time, weighted_average_watts, pss, intensityfactor, CTL, ATL, TSB
        DailyProgress.append( [fitnessdate, 0, "", 0, 0, 0, 0, 0, 0, 0  ] )
    else:
        TempActivity = []
        for foundActivity in foundActivities:
            ## Add the scores of all activities today to sum into one score (todo)
            if "weighted_average_watts" in foundActivity:
                ## DailyProgress = date, start_date_local, name, moving_time, weighted_average_watts, pss, intensityfactor, CTL, ATL, TSB
                calc = calculations.calc_trainingload( moving_time = foundActivity["moving_time"], weighted_average_watts = foundActivity["weighted_average_watts"], ftp = AthleteInfo["ftp"])

                TempActivity = [
                    fitnessdate,
                    foundActivity["start_date_local"],
                    foundActivity["name"],
                    foundActivity["moving_time"],
                    foundActivity["weighted_average_watts"],
                    calc[0],    ## PSS
                    calc[1],     ## Intensity Factor
                    0,          ## CTL
                    0,          ## ATL,
                    0           ## TSB
                ]
            elif "average_heartrate" in foundActivity:
                ## DailyProgress = date, start_date_local, name, moving_time, weighted_average_watts, pss, intensityfactor, CTL, ATL, TSB
                ## 'has_heartrate': True
                ## 'average_heartrate': 134.4
                TempActivity= [
                    fitnessdate,
                    foundActivity["start_date_local"],
                    foundActivity["name"],
                    foundActivity["moving_time"],
                    foundActivity["average_heartrate"],
                0,              ## PSS
                    0,          ## Intensity Factor
                    0,          ## CTL
                    0,          ## ATL,
                    0           ## TSB
                    ]
            else:
                ## If there is no weigthed_average_watts and no average_heartrate, we can't calculate fitness
                TempActivity = [
                    fitnessdate,
                    foundActivity["start_date_local"],
                    foundActivity["name"],
                    foundActivity["moving_time"],
                    0,
                    0,          ## PSS
                    0,          ## Intensity Factor
                    0,          ## CTL
                    0,          ## ATL,
                    0           ## TSB
                    ]
        
        ## DailyProgress = date, start_date_local, name, moving_time, weighted_average_watts, pss, intensityfactor, CTL, ATL, TSB
        DailyProgress.append( TempActivity )

    # End Loop of fitnessdate
    fitnessdate = fitnessdate + timedelta(days=1)

## Now calculated fitness (CTL), fatigue (ATL) en form (TSB)
yesterdayCTL = 0
yesterdayATL = 0

for daily in DailyProgress:
    ## DailyProgress = date, start_date_local, name, moving_time, weighted_average_watts, pss(5), intensityfactor(6), CTL(7), ATL(8), TSB(9)
    ## todayCTL = yesterdayCTL +(( PSS - yesterdayCTL )* (1-exp(-1/42))
    ## todayATL = =yesterdayATL+((PSS -yesterdayATL) * (1-exp(-1/7)))
    todayCTL = yesterdayCTL + (( daily[5] - yesterdayCTL ) * (1 - math.exp( -1/42 )) )
    todayATL = yesterdayATL + (( daily[5] - yesterdayATL ) * (1 - math.exp( -1/7  )) )
    todayTSB = todayCTL - todayATL

    ## Now write the new values into current daily
    daily[7] = math.trunc(todayCTL)
    daily[8] = math.trunc(todayATL)
    daily[9] = math.trunc(todayTSB)

    ## Now replace yesterday's values with today's values
    yesterdayCTL = todayCTL
    yesterdayATL = todayATL
    if( daily[2] == ""):
        print( daily[0],"##", "no activity","##" , daily[7],"##", daily[8],"##", daily[9])
    else:
        print( daily[0],"##", daily[2],"##", daily[7],"##", daily[8],"##", daily[9])
