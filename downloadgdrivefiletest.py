# https://docs.google.com/document/d/1osirGQvfN9iQEuGPFBD9wu4btHFzVjiJ/edit?usp=share_link&ouid=111827661461814112034&rtpof=true&sd=true

# import io

# import google.auth
# from googleapiclient.discovery import build
# from googleapiclient.errors import HttpError
# from googleapiclient.http import MediaIoBaseDownload
# from google.auth.transport.requests import Request
# from google.oauth2.credentials import Credentials
# from google_auth_oauthlib.flow import InstalledAppFlow
# from googleapiclient.discovery import build
# from googleapiclient.errors import HttpError
# from googleapiclient.http import MediaFileUpload
# import os
# SCOPES = ['https://www.googleapis.com/auth/drive']

# def get_gdrive_service():
#     creds = None
#     # The file token.json stores the user's access and refresh tokens, and is
#     # created automatically when the authorization flow completes for the first
#     # time.
#     if os.path.exists('token.json'):
#         creds = Credentials.from_authorized_user_file('token.json', SCOPES)
#     # If there are no (valid) credentials available, let the user log in.
#     if not creds or not creds.valid:
#         if creds and creds.expired and creds.refresh_token:
#             creds.refresh(Request())
#         else:
#             flow = InstalledAppFlow.from_client_secrets_file(
#                 'credentials.json', SCOPES)
#             creds = flow.run_local_server(port=0)
#         # Save the credentials for the next run
#         with open('token.json', 'w') as token:
#             token.write(creds.to_json())

#     try:
#         return build('drive', 'v3', credentials=creds)

#         # # Call the Drive v3 API
#         # results = service.files().list(
#         #     pageSize=10, fields="nextPageToken, files(id, name)").execute()
#         # items = results.get('files', [])

#         # if not items:
#         #     print('No files found.')
#         #     return
#         # print('Files:')
#         # for item in items:
#         #     print(u'{0} ({1})'.format(item['name'], item['id']))
#     except HttpError as error:
#         # TODO(developer) - Handle errors from drive API.
#         print(f'An error occurred: {error}')

# def download_file(real_file_id):
#     """Downloads a file
#     Args:
#         real_file_id: ID of the file to download
#     Returns : IO object with location.

#     Load pre-authorized user credentials from the environment.
#     TODO(developer) - See https://developers.google.com/identity
#     for guides on implementing OAuth2 for the application.
#     """
#     creds=None
#     if os.path.exists('token.json'):
#         creds = Credentials.from_authorized_user_file('token.json', SCOPES)

#     try:
#         # create drive api client
#         service = build('drive', 'v3', credentials=creds)

#         file_id = real_file_id

#         # pylint: disable=maybe-no-member
#         request = service.files().get_media(fileId=file_id)
#         file = io.BytesIO()
#         downloader = MediaIoBaseDownload(file, request)
#         done = False
#         while done is False:
#             status, done = downloader.next_chunk()
#             print(F'Download {int(status.progress() * 100)}.')

#     except HttpError as error:
#         print(F'An error occurred: {error}')
#         file = None

#     return file.getvalue()


# if __name__ == '__main__':
#     res = download_file(real_file_id='1osirGQvfN9iQEuGPFBD9wu4btHFzVjiJ')
#     print(res)

from google_drive_downloader import GoogleDriveDownloader
a = GoogleDriveDownloader()
a.DOWNLOAD_URL("https://docs.google.com/document/d/1qomyI0Mm30zJbW1NlP5gl2bfwk3C2JlQ/edit?usp=share_link&ouid=111827661461814112034&rtpof=true&sd=true")