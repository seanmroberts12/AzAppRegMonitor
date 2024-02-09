import msGraph_func
import creds

# for running locally, add a creds file to the same directory with the below details
# 

tenantId = creds.tenantId
appId = creds.appId
appSecret = creds.appSecret

msGraph_func.expiringAppRegSecret(thresholdDays=5)