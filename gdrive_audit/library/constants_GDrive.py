# Class constants

# # credentials token max age (seconds) 6 hours
# TOKEN_MAX_AGE = 60*60*2

# rate limit - keep this reasonably small to avoid going over quota
PAGESIZE = 300
# number of calls per period
CALL_LIMIT = int(100)
# period size
CALL_PERIOD = 60



# https://developers.google.com/drive/api/v3/mime-types
MIMETYPES = {'audio': 'application/vnd.google-apps.audio',
              'docs': 'application/vnd.google-apps.document',
              'spreadsheet': 'application/vnd.google-apps.spreadsheet',
              'drawing': 'application/vnd.google-apps.drawing',
              'file': 'application/vnd.google-apps.file',
              'folder': 'application/vnd.google-apps.folder',
              'forms': 'application/vnd.google-apps.form',
              'mymaps': 'application/vnd.google-apps.map',
              'photos': 'application/vnd.google-apps.photo',
              'slides': 'application/vnd.google-apps.presentation',
              'scripts': 'application/vnd.google-apps.script',
              'sites': 'application/vnd.google-apps.sites',
              'sheets': 'application/vnd.google-apps.spreadsheet',
              'video': 'application/vnd.google-apps.video',
              'fusiontable': 'application/vnd.google-apps.fusiontable',
              'drive-sdk': 'application/vnd.google-apps.drive-sdk',
              'shortcut': 'application/vnd.google-apps.shortcut',
              'site': 'application/vnd.google-apps.site',
              'unknown': 'application/vnd.google-apps.unknown',
              'video': 'application/vnd.google-apps.video',
              }
FIELDS_DEFAULT = ['id', 'name', 'kind', 'mimeType', 'webViewLink']

# corpora: https://developers.google.com/drive/api/v3/reference/files/list
# spaces to search
CORPORA = {'user': {'params': {
                        'includeItemsFromAllDrives': '',
                        'supportsAllDrives': ''},
                    'description': "files created by, opened by, or shared directly with the user"},
           'drive': {'params': {
                        'includeItemsFromAllDrives': True,
                        'supportsAllDrives': True},
                    'description': "files in the specified shared drive as indicated by the 'driveId'"},
           'domain': {'params': {
                        'includeItemsFromAllDrives': True,
                        'supportsAllDrives': True},
                    'description': "files shared to the user's domain"},
           'allDrives': {'params': {
                            'includeItemsFromAllDrives': True,
                            'supportsAllDrives': True},
                    'description': "A combination of 'user' and 'drive' for all drives where the user is a member"}}




# https://developers.google.com/drive/api/v3/reference/files
FILE_FIELDS = {'Methods',
 'appProperties',
 'capabilities',
 'contentHints',
 'contentRestrictions',
 'copyCreates',
 'copyRequiresWriterPermission',
 'createdTime',
 'description',
 'driveId',
 'explicitlyTrashed',
 'exportLinks',
 'fileExtension',
 'folderColorRgb',
 'fullFileExtension',
 'hasAugmentedPermissions',
 'hasThumbnail',
 'headRevisionId',
 'iconLink',
 'id',
 'imageMediaMetadata',
 'isAppAuthorized',
 'kind',
 'lastModifyingUser',
 'linkShareMetadata',
 'md5Checksum',
 'mimeType',
 'modifiedByMe',
 'modifiedByMeTime',
 'modifiedTime',
 'name',
 'originalFilename',
 'ownedByMe',
 'owners',
 'parents',
 'permissionIds',
 'permissions',
 'properties',
 'quotaBytesUsed',
 'resourceKey',
 'shared',
 'sharedWithMeTime',
 'sharingUser',
 'shortcutDetails',
 'size',
 'spaces',
 'starred',
 'teamDriveId',
 'thumbnailLink',
 'thumbnailVersion',
 'trashed',
 'trashedTime',
 'trashingUser',
 'version',
 'videoMediaMetadata',
 'viewedByMe',
 'viewedByMeTime',
 'viewersCanCopyContent',
 'webContentLink',
 'webViewLink',
 'writersCanShare',
}
    