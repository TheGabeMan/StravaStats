import webbrowser
import json
import requests
import time

def check_for_secret( secretfile ):
    try:
        importfile = open("secret_client_"+ secretfile + ".env", "r")
    except OSError:
        print( "Could not open/read file: secret_client_" + secretfile + "id.env" )
        secret = input("Enter your client " + secretfile + ": ")
        with open("secret_client_"+ secretfile + ".env", "w") as outfile:
            outfile.write( secret ) 
            outfile.close
        return secret
    with importfile:
        secret = importfile.read()
        importfile.close
        return secret        

def get_strava_token():
    ## Are secret_client_id.env and secret_client_secret.env present?
    ## Do they have values
    client_id = check_for_secret( "id" )
    client_secret = check_for_secret( "secret" )
    
    ## Is there a secret_strava_tokens_json.env file?
    try:
        importtoken = open("secret_strava_tokens_json.env", "r")
    except OSError:
        ## No strava json found. Next step is to authorize this app
        print("No token found, webbrowser will open, authorize the application and copy paste the code section")
        strava_url = "http://www.strava.com/oauth/authorize?client_id=" + client_id + "&response_type=code&redirect_uri=http://localhost/exchange_token&approval_prompt=force&scope=profile:read_all,activity:read_all"
        webbrowser.open(strava_url,new=2)

        ### http://www.strava.com/oauth/authorize?client_id=32496&response_type=code&redirect_uri=http://localhost/exchange_token&approval_prompt=force&scope=profile:read_all,activity:read_all
        ## code = 'c5667666890bc9b64c9ae154a4ce4e35ab264cc6'
        code = input("Copy the code from the URL: ")

        # Make Strava auth API call with your 
        # client_code, client_secret and code
        response = requests.post(
                            url = 'https://www.strava.com/oauth/token',
                            data = {
                                    'client_id': client_id,
                                    'client_secret': client_secret,
                                    'code': code,
                                    'grant_type': 'authorization_code'
                                    }
                        )
        #Save json response as a variable
        strava_token = response.json()

        # Save tokens to file
        with open('secret_strava_tokens_json.env', 'w') as exporttoken:
            json.dump(strava_token, exporttoken)
            exporttoken.close

        ## Now return the token
        return strava_token['access_token']
    with importtoken:
        strava_json = json.load(importtoken)
        importtoken.close
        ## If access tokne has expired then use the refresh token to get the new access token
        if strava_json['expires_at'] < time.time():
            ## Make stava auth API call with current fresh token
            print( 'Token expired, going to refresh the existing token')
            response = requests.post(
                                url = 'https://www.strava.com/oauth/token',
                                data = {
                                        'client_id': client_id,
                                        'client_secret': client_secret,
                                        'grant_type': 'refresh_token',
                                        'refresh_token': strava_json['refresh_token']
                                        }
                                    )
            strava_token = response.json()
            with open('secret_strava_tokens_json.env', 'w') as outfile:
                json.dump(strava_token, outfile)
                outfile.close
            return strava_token['access_token']
        return strava_json['access_token']