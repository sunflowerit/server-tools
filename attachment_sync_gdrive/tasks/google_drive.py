# -*- coding: utf-8 -*-
# © 2018 Sunflower IT (http://sunflowerweb.nl)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import httplib2
from io import BytesIO
from googleapiclient import discovery
from oauth2client.client import AccessTokenCredentials
from googleapiclient.http import MediaFileUpload, MediaIoBaseUpload
from odoo.tools.mimetypes import guess_mimetype


class GoogleDriveTask:
    _key = 'google_drive'
    _name = 'GDRIVE'
    _synchronize_type = None
    _default_port = False
    _hide_login = True
    _hide_password = True
    _hide_port = True
    _hide_address = True

    def __init__(self, access_token):
        google_credentials = AccessTokenCredentials(access_token,
                                                    'my-user-agent/1.0')
        google_http = httplib2.Http()
        google_http = google_credentials.authorize(google_http)
        google_drive = discovery.build('drive', 'v3', http=google_http,
                                       cache_discovery=False)
        self.conn = google_drive.files()

    def setcontents(self, path, data=None):
        """Use the google drive MediaIoBaseUpload"""
        drive_client = self.conn
        mimetype = guess_mimetype(data)
        fh = BytesIO(data)
        media_body = MediaIoBaseUpload(fh, chunksize=-1, mimetype=mimetype,
                                       resumable=True)
        # construct upload kwargs
        file_name = path.split('/')[-1]
        create_kwargs = {
            'body': {
                'name': file_name  # Get the last bit, ignore dirs
            },
            'media_body': media_body,
            'fields': 'id'
        }
        # walk through parent directories
        parent_id = ''
        if path:
            walk_folders = True
            folder_kwargs = {
                'body': {
                    'name': '',
                    'mimeType': 'application/vnd.google-apps.folder'
                },
                'fields': 'id'
            }
            query_kwargs = {
                'spaces': 'drive',
                'fields': 'files(id, parents)'
            }
            folder_name = path.split('/')[0]

            folder_kwargs['body']['name'] = folder_name

            # search for folder id in existing hierarchy
            if walk_folders:
                walk_query = "name = '%s'" % folder_name
                if parent_id:
                    walk_query += "and '%s' in parents" % parent_id
                query_kwargs['q'] = walk_query
                response = drive_client.list(**query_kwargs).execute()
                file_list = response.get('files', [])
            else:
                file_list = []
            if file_list:
                folder_id = file_list[0].get('id')

            else:
                file_metadata = {
                    'name': folder_name,
                    'mimeType': 'application/vnd.google-apps.folder'
                }
                new_folder = drive_client.create(body=file_metadata, fields='id').execute()
                folder_id = new_folder.get('id')

        drive_space = folder_id
        create_kwargs['body']['parents'] = [drive_space]

        # send create request
        file = drive_client.create(**create_kwargs).execute()
        file_id = file.get('id')

        return file_id

    @staticmethod
    def connect(location):
        conn = GoogleDriveTask(location._get_access_token())
        return conn
