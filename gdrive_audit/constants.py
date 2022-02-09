import os
from pathlib import Path
dir_path = os.path.dirname(os.path.realpath(__file__))


VERSION = '0.1.0'
APP_NAME = 'gdrive_audit'
SCOPES = ['https://www.googleapis.com/auth/drive']
CACHE = Path(f'~/.cache/{APP_NAME}/').expanduser().resolve()
TOKEN_FILE = 'token.json'
TOKEN_PATH = CACHE/TOKEN_FILE
SECRETS_FILE = 'client_secrets.json'
SECRETS_PATHS = {'saved': CACHE/SECRETS_FILE,
                'downloaded': Path(f'~/Downloads/{SECRETS_FILE}').expanduser().resolve(),}

AUDIT_FILTER = "https://docs.google.com/spreadsheets/d/15U7uA7O9yAX61g_WPvdeGGuEninmJbnnyzA7wbHIaw0/copy"

README_GETTING_STARTED = "https://github.com/txoof/gdrive_audit#getting-started"