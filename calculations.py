''' ## Inlezen client_id
def read_client():
    with open('secret_client_id.env') as importfile:
        global client_id
        client_id = importfile.read()
        importfile.close()

    ## Inlezen Secret
    with open('secret_client_secret.env') as importfile:
        global client_secret
        client_secret = importfile.read()
        importfile.close()
'''

def calc_trainingload( moving_time, weighted_average_watts, ftp):
    '''
    Trainingload / PSS is calculated by using Weighted Average Power, moving_time and athlete's FTP from strava
    (( moving time x Weighted Average Power x IF) / (FTP * 3600) ) * 100
    Intensity Factor (IF) is calculated by dividing Weighted Average Power / FTP  
    '''
    intensity_factor = weighted_average_watts / ftp
    pss = round((( moving_time * weighted_average_watts * intensity_factor) / ( ftp * 3600))* 100)
    # print("PSS calculated is: ", pss)
    # print("Intensity factor is: ", intensity_factor)
    return pss, round(intensity_factor*100)

