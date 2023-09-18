# GDrive Audit
Audit ownership of all files in a Google Drive folder.

*GDrive Audit* produces a google sheet that shows all the files within a folder and their owners. This tool can aid in migrating folders into a Google _Shared Drive_. Run the audit tool to verify that all items contained within the _shared folder_ are owned by the team and are suitable for migrating into a Google _Shared Drive_.

Remember: When super-admins migrate a folder into a _Shared Drive_ all ownership of the files is transferred to the organization. This is strictly a ONE WAY process and cannot be undone. If items that are meant for organization-wide consumption are migrated, the rest of the organization will lose access. Each item must be individually restored to the original owner. There is **no undo**.

## Requirements
* M1 Mac for `.pkg` version
    * See [Building](#building) instructions below for building on other platforms
* Google Workspace Account -- This application will only run for accounts covered under a Google Workspace license
* Valid [`client_secrets.json` for ASH team members](https://drive.google.com/file/d/1HpkPtTeQ75oDP7iIHZzQmUAVJpvk5slA/view?usp=sharing) file
    * For users outside of ASH, see the [Back end API instructions](#backendapi) for obtaining a `secrets` file.

## Getting Started

Any Google Workspace user can audit a folder that is shared with them. The audit will be limited to folders that they can read in google drive. Ask the team to move all the folders that will be migrated into a shared folder and to give your user _Editor_ access to the shared folder. Follow the steps below to audit the folder.

You will need a valid `client_secrets.json` file to setup and use the software for the first time.

**To Get Started**

* Download the program from this [link](https://github.com/txoof/gdrive_audit/blob/master/gdrive_audit.zip) and unzip the executable.
* Right click and choose "open"
    * You will likely need an admin password to complete the installation process
* Obtain a `client_secrets.json` file and place it in your Downloads folder
    * ASH team members can download the [`client_secrets.json`](https://drive.google.com/file/d/1HpkPtTeQ75oDP7iIHZzQmUAVJpvk5slA/view?usp=sharing) file
    * Google Workspace users ouside of the ASH.nl organization, can create their own client_secrets.json file by following the [Back end API instructions](#backendapi) below
* Double click on the `/Applications/gdrive_audit` executable to run it
* Follow the prompts for authorizing the tool 
    - This tool needs to have read and write access to your Google Drive
    - Rationale for Read Access: Each file in a folder is checked for ownership, file type and modification time
    - Rationale for Write Access: A summary of the findings is uploaded to Google Sheets 
    - Rationale for Delete Access: This access is bundled together with the Write access
* Paste in the URL of the folder you wish to audit for migration
* Once the audit is complete, go on to [Auditing the Results](#Auditing)
* Repeat the steps above as needed to audit additional folders

<a name='Auditing'></a>
## Auditing the Results

After the audit is complete, a new file will be created in your _My Drive_. The link will be provided by the tool. The sheet can be used as-is or analyzed with a sheet that helps filter and organize the audited files. 

Use this [link](https://docs.google.com/spreadsheets/d/15U7uA7O9yAX61g_WPvdeGGuEninmJbnnyzA7wbHIaw0/copy) to make a copy of the filter. Follow the instructions embedded in the filter sheet.

**What to look for when auditing a folder**

* Review the owners of the documents
* Look for items that are owned by users **not** in the team
* Review any suspect items with the team and confirm that these items should be moved into the shared drive
    * If there is **any** doubt that the original owner can afford to lose access, **REMOVE** these items from the shared folder. The transfer to a _Shared Drive_ cannot be easily undone.
    * Suspect items can be excluded from the migration by simply moving out of the shared folder.
* Look for items that are owned by users **outside** of your organization 
    * These items will not be migrated and will be left in place. Some users find this distressing.
    * Items that are owned by external users can be copied by someone in the team; the copy will be migrated.

## Resources
* [Python Quick Start from Google](https://developers.google.com/drive/api/v3/quickstart/python)
* [Create an OAuth client ID](https://developers.google.com/workspace/guides/create-credentials#oauth-client-id)

<a name=building></a>
## Building

<a name=installsecrets></a>
### Installing Secrets
A `client_secrets.json` file is required. Obtain a copy by following the [Back End API](#backendapi) instructions, or if you are an ASH staff member, download a copy from google drive [here](https://drive.google.com/file/d/1HpkPtTeQ75oDP7iIHZzQmUAVJpvk5slA/view?usp=sharing).

Place the client_secrets.json file in you Downloads folder and then run `gdrive_audit`. The program will cache the secrets file in your home folder. 

For the curious, all cached information is stored in `~/.cache/gdrive_audit/`.

### Build Environment
**Requirements**

* Python 3.7+
* Python Modules**
    * google-api-python-client
    * google-auth-httplib2
    * google-auth-oauthlib
    * pyinstaller

**Setup Build Environment With Pipenv**

Pipenv will create a virutal environment and install the appropriate modules:
* `$ pip3 install pipenv`
* `$ cd ./gdrive_audit`
* `$ pipenv --python 3` 
* `$ pipenv install`

`gdrive_audit` can be run from the command line with the command below:

`pipenv run python3 gdrive_audit.py`

**Build Installable Package**

Pyinstaller will create a one-file application that can be run by double clicking on the icon. This application will only run on the device on which it was created unless it is be signed, notarized and stapled through Apple's codesigning procedure. 

PyInstaller works best from within the pipenv virtual environment:
`pipenv run pyinstaller -F --hiddenimport=google-api-python-client --hiddenimport=googleapiclient --add-data ./gdrive_audit/library:./library  -c --clean --noconfirm ./gdrive_audit/gdrive_audit.py`

**Package and Sign for MacOS Distribution**

To make an installable package that will pass MacOS' gatekeeper security checks, The package must be signed, notarized and stapled. [PyCodeSign](https://github.com/txoof/codesign) can provide this service, but requires an Apple Developer licenses and some configuration. See the [README](https://github.com/txoof/codesign#readme) for more information on configuring setting up a developer ID and configuring your keychain. 

A sample `pycodesign.ini` is provided as a template.

`pycodesign -s -p -n -t ./pycodesign.ini`

<a name=backendapi></a>
### Back End API
*Instructions as of Jan 2022*

**[Setup API Connection with Google](https://developers.google.com/drive/api/v3/enable-drive-api)**

This needs to be done by a Workspace user within the domain that has API permissions from the [Cloud Console](https://console.cloud.google.com/apis/dashboard)

1. Use the ≡ Menu to select *IAM & Admin* 
    - Select *Create a Project*
2. Provide the following information and click ***Create***
    - Project Name: something meaningful to you e.g. *Google Drive Folder Audit*
    - Organization: your tld e.g. ash.nl
    - Location: your org e.g. ash.nl
3. Make sure the project created in the previous step is active 
    - Use top left menu or 
    - [cloud resource manager console](https://console.cloud.google.com/cloud-resource-manager)
        - Select project and click ⋮ > ***Settings***
4. Use Menu ≡ > *APIs & Services > Library *
    - Locate and choose *Google Drive API*
    - Click ***ENABLE***
8. [Create OAuth client ID credentials](https://developers.google.com/workspace/guides/create-credentials#oauth-client-id)
    - Menu ≡ *APIs & Services > Credentials*
    - Click *+CREATE CREDENTIALS > Help me choose*
    - (1) Credential Type
        - Which API are you using? *Google Drive*
        - What data will you be accessing? ◍ *User data*
        - click ***NEXT***
    - (2) Scopes
        - *ADD OR REMOVE SCOPES*
            - *Filter: Google Drive API*
            - [x] See, edit, create, and delete only the specific Google Drive files you use with this app
            - [x] View and manage metadata of files in your Google Drive
            - [x] See information about your Google Drive files
            - [x] View the activity record of files in your Google Drive
            - click ***UPDATE***
            - click ***SAVE AND CONTINUE***
    - (3) OAuth Client ID
        - Application type: *Dekstop app*
        - Name: *Google Drive Folder Audit* or something similar
        - click ***CREATE***
        - click ***⇓ DOWNLOAD***
            - Store the *client_secret_xxxx-yyyy.apps.googleuserconent.com.json* in the `./secrets/`
            - ***DO NOT ADD THIS FILE TO YOUR GIT REPO*** It is a SECRET.
            - the `.gitignore` file ignores files matching the pattern `client_secret*.json`
        
    
 


