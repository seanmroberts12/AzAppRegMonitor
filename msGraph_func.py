# Helper functions for interacting with ms graph apis
# Can be modified for use with other API oauth requests

from datetime import datetime, timedelta
import time
import requests
import creds

# for running locally, add a creds file to the same directory with the below details
# Grab from keyvault if running in Azure or secret manager if running in AWS

tenantId = creds.tenantId
appId = creds.appId
appSecret = creds.appSecret

# Oauth token request to ms graph api

def get_msAuthToken(tenantId, appId, appSecret, scope='https://graph.microsoft.com/.default'):
    
    auth_url = f'https://login.microsoftonline.com/{tenantId}/oauth2/v2.0/token'
    auth_body = {
        "client_id": appId,
        "client_secret": appSecret,
        "scope": scope,
        "grant_type": 'client_credentials'
    }
    auth_header = {
        "Content-type": 'application/x-www-form-urlencoded'
    }

    token_req = requests.post(auth_url, data=auth_body, headers=auth_header)

    expiration_time = time.time() + token_req.json()['ext_expires_in']

    return_dict = {
        "auth_token": token_req.json()['access_token'],
        "expiration": expiration_time
    }
    #Set to global variable to make it easier to use
    global ms_authToken
    ms_authToken = return_dict
    # return dict with api key and expiration time in unix epoch time
    return return_dict

# List app registrations and secret expiration

def expiringAppRegSecret(thresholdDays):
    
    if not 'ms_authToken' in globals():
        # Get auth token if not found in the global vars
        get_msAuthToken(tenantId, appId, appSecret)
    elif (time.time() - 100) < ms_authToken['expiration']:
        # check if token in global vars is expired
        # included a 100 second buffer for long running operations 
        print("Expired token in global")
        get_msAuthToken(tenantId, appId, appSecret)
        
    authHeader = {
        "Authorization" : "Bearer " + ms_authToken['auth_token'],
        "ConsistencyLevel" : "eventual"
    }

    appRegList_url = "https://graph.microsoft.com/v1.0/applications?$select=id,appId,displayName,passwordCredentials"
    response = requests.get(appRegList_url, headers=authHeader)

    responseData = response.json()['value']
    if '@odata.nextLink' in response.json():
        next_link = response.json()['@odata.nextLink']
        while next_link:
            next_response = requests.get(next_link,headers=authHeader)
            for x in next_response.json()['value']:
                responseData.append(x)
            next_link = next_response.json().get('@odata.nextLink', None)
    expiring_list = []
    for appReg in responseData:
        # if clause to filter out app registrations that have no secrets
        if appReg['passwordCredentials']:
            for key in appReg['passwordCredentials']:
                dateFormat = r'%Y-%m-%dT%H:%M:%S.%fZ'
                expiration = datetime.strptime(key['endDateTime'], dateFormat)
                if (expiration - datetime.now()) < timedelta(days= thresholdDays):
                    # Can add alerting actions here potentially email/teams message/slack/ event grid/ticketing system/ect
                    # Alternatively, generate the alerting action off of the returned list
                    appendDict = {"displayName": appReg['displayName'], "keyId": key['keyId']}
                    expiring_list.append(appendDict)
    return expiring_list