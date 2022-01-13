# GDrive Audit
Audit ownership in Google Drive folders

## Resources
* [Python Quick Start](https://developers.google.com/drive/api/v3/quickstart/python)

## Setup

### Back End API
*Instructions as of Jan 2022*

**[Setup API Connection with Google](https://developers.google.com/drive/api/v3/enable-drive-api)**

This needs to be done by a Workspace user within the domain that has API permissions from the [Cloud Console](https://console.cloud.google.com/apis/dashboard)

1. Use the *Project* drop down menu (top left corner) and choose *NEW PROJECT*
2. Provide the following information and click *Create*
    - Project Name: something meaningful to you e.g. *Google Drive Folder Audit*
    - Organization: your tld e.g. ash.nl
    - Location: your org e.g. ash.nl
3. Select project from *Project* drop down menu (top left corner)
4. Use ≡ Menu (top left corner) to choose *APIs & Services*
5. Use the *+ ENABLE APIS AND SERVICES* menu to add the Google Drive API
6. Locate and choose *Google Drive API*
7. Click *ENABLE*
8. Create credentials from the *Overview* screen (use left-hand menu) by clicking *CREATE CREDENTIALS*
    - (1) Credential Type: 
        - Which API are you using? *Google Drive API*
        - What data will you be accessing? *User data*
        - *NEXT*
    - (2) OAuth Consent Screen:
       - App Information:
          - App name: something meaningful to you e.g. *Google Drive Folder Audit*
          - User support email: API User (e.g. you)
          - App logo: upload if you have one
       - Developer contact information:
          - Email address: appropriate contact information
          - *SAVE AND CONTINUE*
    - (3) Scopes:
        - *ADD OR REMOVE SCOPES*
          - [x] See, edit, create, and delete only the specific Google Drive files you use with this app
          - [x] View and manage metadata of files in your Google Drive
          - [x] See information about your Google Drive files
          - [x] View the activity record of files in your Google Drive
          - *SAVE AND CONTINUE*
    - (4) OAuth Client ID
        - Application type: Desktop app
        - Name: logical name e.g. Google Drive Folder Audit
    - (5) Download your credentials
        - Download
        - Done
       


* [Create an OAuth client ID](https://developers.google.com/workspace/guides/create-credentials#oauth-client-id)
    
 
