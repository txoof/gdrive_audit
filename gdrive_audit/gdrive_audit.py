#!/usr/bin/env python3
# coding: utf-8






try:
    from . import contants
except ImportError:
    import constants

import re
import logging
import shutil
import tempfile
import unicodedata
import datetime
import csv
import sys

from pathlib import Path

from humanfriendly import prompts
import textwrap







from library import GDrive
from library.GDrive import GDriveError






logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)






def do_exit(exit_level=0, message='', testing=False):

    if testing:
        print(f'TESTING--EXIT MESSAGE: ({exit_level}){message}')
    elif exit_level > 0:
        logger.warning(f'exiting before completion with exit code {exit_level}: {message}')
        print('exiting due to errors:')
        print(message)
        sys.exit(exit_level)
    else:
        print(message)
        sys.exit(0)
        






def slugify(value, allow_unicode=False, lower=False):
    """
    Taken from https://github.com/django/django/blob/master/django/utils/text.py
    Convert to ASCII if 'allow_unicode' is False. Convert spaces or repeated
    dashes to single dashes. Remove characters that aren't alphanumerics,
    underscores, or hyphens. Convert to lowercase. Also strip leading and
    trailing whitespace, dashes, and underscores.
    """
    value = str(value)
    if allow_unicode:
        value = unicodedata.normalize('NFKC', value)
    else:
        value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
    if lower:
        value = re.sub(r'[^\w\s-]', '', value.lower())
    return re.sub(r'[-\s]+', '_', value).strip('-_')






def recurse_folders(drive, parents, 
                    fields=['parents', 'id', 'name', 'mimeType', 'owners', 'modifiedTime', 'webViewLink', 'parents'], 
                    file_list=[], skipped=[], depth=0):
    '''recursively find all files in a google drive folder'''
    if depth == 0:
        file_list = []
        skipped = []
    logger.info(f'recursion depth: {depth}')
    try:
        result = drive.search(parents=parents, fields=fields)
    except GDriveError as e:
        logger.error(f'error accessing google drive: {e}')
        skipped.append(parents)
        result = {}
                
    for f in result:
        if drive.MIMETYPES['folder'] == f.get('mimeType'):
            print(f'Searching folder {f.get("name", "no name")}')
            return_files, return_skipped = recurse_folders(drive=drive, parents=f['id'], 
                                         fields=fields, 
                                         file_list=file_list,
                                         skipped=skipped,
                                         depth=depth+1)
            file_list + return_files
            skipped + return_skipped
        else:
            file_list.append(f)
            print(f'found {len(file_list)} files so far...')
    return (file_list, skipped)
            






def get_folder_id():
    '''get folder id from URL provided by user
    
    Returns:
        str: unique google drive folder id'''
    valid_url = False
    retry = 4
    folderID = None
    print('\n')
    while not valid_url and retry > 0:
        retry -= 1
        url = prompts.prompt_for_input('Paste the URL of a Google Drive folder to audit:\n')
        
        match = re.match("https:\/\/drive\.google\.com\/(?:\S+\/)([a-zA-Z0-9-]+)(?:\S+)?$", url)
        if not match:
            print('That does not appear to be a valid google drive folder URL')
            continue
        else:
            folderID = match[1]
            valid_url = True
    
    return folderID






def get_secrets():
    if not constants.SECRETS_PATHS['saved'].exists():
        constants.SECRETS_PATHS['saved'].parent.mkdir(parents=True, exist_ok=True)
        
    if not constants.SECRETS_PATHS['saved'].exists():
        try:
            logger.debug(f'trying to move secrets from {constants.SECRETS_PATHS["downloaded"]}')
            shutil.move(constants.SECRETS_PATHS['downloaded'], constants.SECRETS_PATHS['saved'])
        except FileNotFoundError as e:
            do_exit(1, "client_secrets.json file is not avialable. Download the secrets file (see documentation) and try again.")
        except OSError as e:
            do_exit(1, f"failed to install secrets file: {e}")
    else:
        logger.debug(f'using {constants.SECRETS_PATHS["saved"]}')
        
    return constants.SECRETS_PATHS['saved']






def output_csv(name, file_list, output=None):    
    if output:
        output = Path(output)/name
        if not output.parent.exists():
            output.parent.mkdir(exist_ok=True, parents=True)
    else:
        temp_dir = tempfile.mkdtemp()
        output = Path(temp_dir)/name
    logger.debug(f'using output file: {output}')
    
    fieldnames = ['name', 'emailAddress', 'displayName', 'webViewLink', 'modifiedTime', 'mimeType']
    pull = ['name', 'webViewLink', 'modifiedTime', 'mimeType']
    
    try:
        with open(output, 'w') as csvfile:            
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for row in file_list:
                line = {}
                for n in pull:
                    line[n] = row.get(n, '?error?')
                line['displayName'] = row.get('owners', [{}])[0].get('displayName', 'Unknown')
                line['emailAddress'] = row.get('owners', [{}])[0].get('emailAddress', 'Unknown')
                writer.writerow(line)
    except OSError as e:
        do_exit(1, f"error writing {output}: {e}")

    return output






def main():
    
    added_file = None
    secrets = get_secrets()
    
    drive = GDrive(secrets=secrets, scopes=constants.SCOPES)
    
#     return drive
    
    wrapper = textwrap.TextWrapper(replace_whitespace=True, drop_whitespace=True, width=60)
    welcome = f'{constants.APP_NAME} provides a Google Sheet that shows all of the files and owners within a google drive folder.'
    print('\n'.join(wrapper.wrap(welcome)))
    
    
    while True:
        folder_id = get_folder_id()

        if not folder_id:
            do_exit(1, 'No valid folder URL was provided. Exiting')

        try:
            folder_props = drive.get_properties(fileId=folder_id, fields=['owners', 'name', 'webViewLink', 'kind', 'id', 'mimeType'])
        except GDriveError as e:
            msg = f'failed to get information on this folder: {e}'
            logger.warning(msg)
            print(f'Failed to get information for this folder.')
            cont = prompts.prompt_for_confirmation('Try a new folder?', default=False)
            if not cont:
                break
            else:
                continue


        folder_name = folder_props.get('name', 'UNKNOWN FOLDER')
        time_string = datetime.date.strftime(datetime.datetime.now(), '%Y%m%d_%H%M%S')
        owners = folder_props.get('owners', [{}])

        if len(owners) > 0:
            owner_name = owners[0].get('displayName', 'UNKNOWN OWNER')
        else:
            owner_name = "UNKNOWN OWNER"                           

        google_filename = f'FOLDER:{folder_name} OWNER:{owner_name}-ownership audit [{time_string}]'
        local_filename = f'{time_string}.csv'

        files, skipped = recurse_folders(drive, parents=folder_id)

        local_file = output_csv(local_filename, files)
        try:
            logger.debug(f'sending csv to google sheets: {google_filename}')
            added_file = drive.add_file(local_file, name=google_filename, target_mimeType='sheets')
        except GDriveError as e:
            do_exit(1, f'failed to send audit sheet to google: {e}\nLocal copy available here: {local_file}')


        print(f'Audit completed and stored in the sheet below.')
        print(f'Audit of folder: {added_file.get("webViewLink", "ERROR")}\n\n')
        print(f'Use the sheet linked below to assist in viewing and filtering the audit:')
        print(constants.AUDIT_FILTER)
        
        cont = prompts.prompt_for_confirmation('Audit another Folder?', default=False)
        if not cont:
            break

    print('Done.')
    return added_file
   






if __name__ == "__main__":
    try:
        idx = sys.argv.index('-l')
    except ValueError:
        idx = None

    if idx:
        try:
            logger.root.setLevel(sys.argv[idx+1])
        except ValueError:
            pass    
    f = main()




