from __future__ import print_function

import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/drive']


def get_gdrive_service():
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    try:
        return build('drive', 'v3', credentials=creds)

        # # Call the Drive v3 API
        # results = service.files().list(
        #     pageSize=10, fields="nextPageToken, files(id, name)").execute()
        # items = results.get('files', [])

        # if not items:
        #     print('No files found.')
        #     return
        # print('Files:')
        # for item in items:
        #     print(u'{0} ({1})'.format(item['name'], item['id']))
    except HttpError as error:
        # TODO(developer) - Handle errors from drive API.
        print(f'An error occurred: {error}')

def createFolder(service,uid):
    try:
        # create drive api client
        
        file_metadata = {
            'name': uid,
            'mimeType': 'application/vnd.google-apps.folder',
            "parents":["149uIJHmu2USVA0FaYkCEyTz2l3Le7AfM"]
        }

        # pylint: disable=maybe-no-member
        file = service.files().create(body=file_metadata, fields='id'
                                      ).execute()
        print(F'Folder ID: "{file.get("id")}".')
        return file.get('id')

    except HttpError as error:
        print(F'An error occurred: {error}')
        return None

def uploadFile(service,file=''):
    # 149uIJHmu2USVA0FaYkCEyTz2l3Le7AfM
    try:


        file_metadata = {'name': 'temp.pdf',"parents":["149uIJHmu2USVA0FaYkCEyTz2l3Le7AfM"]}
        media = MediaFileUpload('temp.pdf',
                                mimetype='application/pdf')
        # pylint: disable=maybe-no-member
        file = service.files().create(body=file_metadata, media_body=media,
                                      fields='id,webViewLink').execute()

        print(F'File ID: {file.get("webViewLink")}')

    except HttpError as error:
        print(F'An error occurred: {error}')
        file = None

    return file.get('id')
if __name__ == '__main__':
    service = get_gdrive_service()
    uploadFile(service)
    # createFolder(service,"he32g23y7cewdsb")