
# Azure app registration expiring secrets monitor

Python function that can be implemented into an Azure runbook or function app to check for secrets that may be exipring soon. Output is can be used to either take action on as part of proactive remedations or send notification to admins to take manual action on.


## Azure App Registration

An app registration will need to be created for this function to utilize. It only needs application level permisisons to the scope Application.ReadAll. 

Generate a secret for the app registration created and save it along with the appId and tenantId for later use.

## Usage/Examples

Included in the msGraph_func python file is the the function for generating the authentication token as well as the function for checking the app registrations. 

Provide the tenantId, appId, and appSecret, preferably grabbing from a keyvault or secret manager if running in Azure or AWS

```python
import msGraph_func

tenantId = "<your-tenant-id>"
appId = "<your-app-id>"
appSecret = "<your-app-secret>"

msGraph_func.expiringAppRegSecret(thresholdDays=5)

```
