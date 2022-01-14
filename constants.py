import os
dir_path = os.path.dirname(os.path.realpath(__file__))

VERSION = '0.0.1'
APP_NAME = 'gdrive_audit'
SCOPES = ['https://www.googleapis.com/auth/drive']
CACHE = f'~/.cache/{APP_NAME}/'
TOKEN_FILE = 'token.json'