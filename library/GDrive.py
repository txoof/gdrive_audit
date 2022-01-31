#!/usr/bin/env python3
# coding: utf-8






try:
    from . import constants_GDrive
except ImportError:
    import constants_GDrive






from pathlib import Path
from json import JSONDecodeError
import logging
from os import path
from functools import wraps
from ssl import SSLError



from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError
from google.auth import exceptions as google_exceptions
from ratelimit import limits, sleep_and_retry






logger = logging.getLogger(__name__)






class GDriveError(Exception):
    pass






# wrap any call to the service in this decorator 
# see: https://stackoverflow.com/a/36944992/5530152
def credential_wrapper(method):
    '''decorator refreshes/creates credentials as needed
    
    updates self.credentials and writes token file as needed.
    
    Args:
        method(class function)
        
    Returns:
        method(class function)'''
    @wraps(method)
    def _impl(self, *method_args, **method_kwargs):
        if not self.credentials or not self.credentials.valid:
            if self.credentials and self.credentials.expired and self.credentials.refresh_token:
                self.credentials.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(self.secrets, self.scopes)
                self.credentials = flow.run_local_server(port=0)
                
                # save the credentials for the next run
                try:
                    with open(self.token, 'w') as token_file:
                        token_file.write(self.credentials.to_json())
                except OSError as e:
                    raise GDriveError(f'error writing token file: {self.token} - {e}')
            # finally build/update service using credentials
            self.build_service(self.credentials)
        method_output = method(self, *method_args, **method_kwargs)
        return method_output
    return _impl                    






def retryer(max_retries=10, timeout=2):
    '''
    Retry on specific network related errors with timeout
    https://pragmaticcoders.com/blog/retrying-exceptions-handling-internet-connection-problems/
    '''
    logger.debug(f'max_retries: {max_retries}, timeout: {timeout}')
    def decorator(func):
        @wraps(func)
        def retry(*args, **kwargs):
            
            network_exceptions = (HttpError, SSLError, BrokenPipeError)
            exceptions = []
            
            for i in range(max_retries):
                logger.debug(f'attempt: {i}')
                try:
                    result = func(*args, **kwargs)
                except network_exceptions as e:
                    logger.debug(f'attempt failed with error: {e}')
                    time.sleep(timeout)
                    exceptions.append(e)
                    continue
                else:
                    return result
            else:
                raise GDriveError(f'could not complete connection due to multiple errors: {exceptions}')
        return retry
    return decorator






class GDrive():
    def __repr__(self):
        return 'GDrive()'
    
    def __str__(self):
        return f'GDrive()'
    
    def __init__(self, secrets, scopes, cache='./', token='./token.json'):
        '''create a google drive interface for searching and returning file/folder information
        
        Args:
            secrets(Path): secrets json file obtained from https://console.cloud.google.com/cloud-resource-manager
            token(Path): file to cache auth information (typically within cache path)
        '''
        self.secrets = secrets
        self.scopes = scopes        
        self.token = token
        self.credentials = self.set_credentials(secrets=self.secrets, 
                                            scopes=self.scopes, 
                                            token=self.token)
        self.service = self.build_service(self.credentials)
        self.MIMETYPES = constants_GDrive.MIMETYPES
        self.CORPORA = constants_GDrive.CORPORA
        self.FILE_FIELDS = constants_GDrive.FILE_FIELDS
        self.FIELDS_DEFAULT = constants_GDrive.FIELDS_DEFAULT
        self.PAGESIZE = constants_GDrive.PAGESIZE
        
    
    @staticmethod
    # may be possible to replace this with the credential_wapper decorator 
    def set_credentials(secrets, token, scopes, force=False):
        token = Path(token).expanduser()
        secrets = Path(secrets).expanduser()
        creds = None

        if token.exists():
            creds = Credentials.from_authorized_user_file(token, scopes)


        if not creds or not creds.valid or force:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())    
            else:
                flow = InstalledAppFlow.from_client_secrets_file(secrets, scopes)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            try:
                with open('token.json', 'w') as token:
                    token.write(creds.to_json())
            except OSError as e:
                raise GDRiveError(f'error writing token file: {token} - {e}')

        return creds    
# 
    
    @staticmethod
    def build_service(credentials):
        try:
            service  = build('drive', 'v3', credentials=credentials)
        except google_exceptions.GoogleAuthError as e:
            raise GDriveError(f'error building credentials: {e}')
        return service
    
                
    @property
    def token(self):
        '''token file'''
        return self._token
        
    @token.setter
    def token(self, t_path):
        t_path = Path(t_path)        
        self._token = t_path
        
        
    def _interface(self, name=None, trashed=False, mimeType=None, fuzzy=True, 
               modifiedTime=None, parents=None, dopperator='>',
               fields = [], forcefields=False,
               corpora='user', orderBy='createdTime', driveId='',):
        '''priavate method to create dict for interfacing with files API
        
        Args:
            name(str): string to search for
            trashed(bool): false: do not search in trashed items
            mimeType(str): search for known mimeType (see self.MIMETYPES)
            fuzzy(bool): true: use `like` opperator when searching for names; 
                false: use `=` opperator when searching for names
            modifiedTime(str): YYYY-MM-DD formatted date for checking modified times
            parents(str): folder ID string used for searching within folders
            dopperator(str): >, <, =, >=, <= search for items with modified time
            fields(list of str): fields to return in search (see self.FIELDS)
            forcefields(bool): False: reject fields not found in self.FIELDS
            corpora(str): locations within drive to search (see self.CORPORA)
            orderBy(str): order results by
            driveId(str): drive identifier string; use for searching within a
                specific shared drive
        
        Returns:
            dict: {'q': 'constructed query string',
                'corpora': 'corpora identifier',
                'includeItemsFromAllDrives': 'True/False',
                'supportsAllDrives': 'True/False',
                'fields_string': 'nextPageToken, files(field1,field2,fieldN)',
                'driveId': 'drive identifier string',
                }
            '''
        
        query_build = {
            'name': (name, f'name {"contains" if fuzzy else "="} "{name}"'),
            'trashed': (trashed, f'trashed={trashed}'),
            'mimeType': (mimeType, f'mimeType="{self.MIMETYPES[mimeType] if mimeType in self.MIMETYPES else ""}"'),
            'parents': (parents, f'"{parents}" in parents'),
            'modifiedTime': (modifiedTime, f'modifiedTime{dopperator}"{modifiedTime}"')
        }
        
        query = [v[1] for k, v in query_build.items() if v[0]]
        
        if len(fields) < 1:
            fields = self.FIELDS_DEFAULT
        fields = set(fields)
        known_fields = []
        for f in fields:
            if f not in self.FILE_FIELDS:
                if forcefields:
                    logger.warning(f'unknown return field: {f}')
                    known_fields.append(f)
                else:
                    raise GDriveError(f'unknown return field: {f}')
            else:
                known_fields.append(f)
        fields_string = f'nextPageToken, files({",".join(known_fields)})'
        
        if driveId:
            corpora = 'drive'
        if corpora not in self.CORPORA:
            raise GDriveError(f'unknown `corpora` value: {corpora}')
        else:
            includeItemsFromAllDrives = self.CORPORA[corpora]['params']['includeItemsFromAllDrives']
            supportsAllDrives = self.CORPORA[corpora]['params']['supportsAllDrives']
            
        q = ' and '.join(query)
        logger.debug(f'QUERY STRING: {q}')
        
        return {'q': q,
                'corpora': corpora,
                'includeItemsFromAllDrives': includeItemsFromAllDrives,
                'supportsAllDrives': supportsAllDrives,
                'fields_string': fields_string,
                'driveId': driveId,
                }
    
    @credential_wrapper
    @sleep_and_retry
    @limits(calls=constants_GDrive.CALL_LIMIT, period=constants_GDrive.CALL_PERIOD)
    def _list(self, q='', corpora='', includeItemsFromAllDrives=False,
             supportsAllDrives='', fields_string='', driveId='', 
              pageToken='', pageSize=constants_GDrive.PAGESIZE):
        '''private function for listing within a drive'''
        logger.debug(f'fettching page of {pageSize} results with query {q}')
        try:
            results = self.service.files().list(q=q,
                                                corpora=corpora,
                                                includeItemsFromAllDrives=includeItemsFromAllDrives,
                                                supportsAllDrives=supportsAllDrives,
                                                fields=fields_string,
                                                driveId=driveId,
                                                pageSize=pageSize,
                                                pageToken=pageToken
                                                ).execute()
        except HttpError as e:
            raise GDriveError(f'error searching: {type(e)}: {e}')

        return results

    @retryer(max_retries=5)    
    def search(self, name=None, trashed=False, mimeType=None, fuzzy=True, 
               modifiedTime=None, parents=None, dopperator='>',
               fields = [], forcefields=False,
               corpora='user', orderBy='createdTime', driveId='',
               pageSize=constants_GDrive.PAGESIZE, complete=True,
               pageToken=''):
        '''search for objects in google drive by name

        Args:
            name(str): string to search for
            trashed(bool): search in trash when true
            mimeType(str): short mimeType (see MIMETYPES property)
            fuzzy(bool): true: `name contains "value"` false: `name = "value"`
            modifiedTime(str): yyyy-mm-dd string
            dopperator(str): >, < for use with modifiedTime
            parents(str): folder to search within
            fields(list of str): fields to return (see FILE_FIELDS property)
            forcefields(bool): true: use unknown fields, false: reject fields not in FILE_FIELDS
            corpora(str): locations to search (see CORPORA property)
            orderBy(str): order results by (see https://developers.google.com/drive/api/v3/reference/files/list)
            driveId(str): search this shared drive
            pageSize(int): number of results to return per page (default 300)
            complete(bool): true: exhaust all nextPageTokens

        Retruns dict of resutls'''

        interface = self._interface(name=name, trashed=trashed, mimeType=mimeType, fuzzy=fuzzy, 
               modifiedTime=modifiedTime, parents=parents, dopperator=dopperator,
               fields = fields, forcefields=forcefields,
               corpora=corpora, orderBy=orderBy, driveId=driveId)
        
        file_list = []
        search_result = self._list(pageToken=pageToken, **interface)
                    
        token = search_result.get('nextPageToken', False)
        file_list.extend(search_result.get('files', []))
        
        while token and complete:
            logger.debug(f'processing additional pages of results')
            search_result = self._list(pageToken=token, **interface) # need to pass pagetoken=token and **interface
            token = search_result.get('nextPageToken', False)
            file_list.extend(search_result.get('files', []))


        logger.debug(f'{len(file_list)} total matches returned')
        
        return file_list

    @retryer(max_retries=5)
    def ls(self, *args, **kwargs):
        '''print lis of files in a google drive using any of the search properties'''

        result = self.search(*args, **kwargs)
        for file in result.get('files', []):
            print(('name: {f[name]}, ID:{f[id]}, mimeType:{f[mimeType]}'.format(f=file)))

        return result
    
    @retryer(max_retries=5)
    @credential_wrapper
    def add_file(self, file, name=None, target_mimeType=None, parents=None, fields=['id', 'webViewLink', 'mimeType']):
        '''add a local file to google drive

        Args:
            file(str): path to local file to upload
            name(str): name of file
            target_mimeType(str): save as this mime type on google drive (see self.MIMETYPES and note below)
            parents(str): folder id
            fields(list of str): file properties to return see self.FILE_FIELDS

        mimeTypes -- https://developers.google.com/drive/api/v3/reference/files/create
        Google Drive will attempt to automatically detect an
        appropriate value from uploaded content if no value is
        provided. The value cannot be changed unless a new revision
        is uploaded.

        If a file is created with a Google Doc MIME type, the
        uploaded content will be imported if possible. The
        supported import formats are published in the About
        resource.

        Returns:
            dict of str containing requestesd fields
            '''


        file = Path(file).expanduser().resolve()
        if not name:
            name = file.name

        target_mimeType = self.MIMETYPES.get(target_mimeType, target_mimeType)

        if not target_mimeType:
            logger.warning('no mime type set: google will attempt to guess type based on content')

        file_metadata = {'name': name,
                         'mimeType': f'{target_mimeType if target_mimeType else ""}'}

        media = MediaFileUpload(filename=file)

        upload = self.service.files().create(body=file_metadata,
                                             media_body=media,
                                             fields=','.join(fields)).execute()

        return upload
    
    






# import constants

# sec = '../secrets/client_secret_910311278281-bh8qk3kmgk0veri3v8en260e76ipafpj.apps.googleusercontent.com.json'
# d = GDrive(secrets=sec, scopes=constants.SCOPES)

# f = d.add_file(file='./foo.txt', name='always take the weather with you...', target_mimeType='docs')

# r = d.search(parents='0B9WTleJ1MzaYT2pieWNXYkZtZm8', fields=['parents', 'id', 'name', 'mimeType'], pageSize=300)






# logging.basicConfig(level=logging.DEBUG)
# logger.debug('foo')






class DC():
    '''dummy class for developing class functions'''
    pass
self = DC()
# self.mimetypes = constants_GDrive.MIMETYPES
# self.service = d.service
# self.MIMETYPES = d.MIMETYPES




