# import os
# import datetime
# from google_auth_oauthlib.flow import InstalledAppFlow
# from googleapiclient.discovery import build
# from google.oauth2.credentials import Credentials
# from google.auth.transport.requests import Request

# def Create_Service(client_secret_file, api_name, api_version, *scopes, prefix=''):
#     CLIENTE_SECRET_FILE = client_secret_file
#     API_SERVICE_NAME = api_name
#     API_VERSION = api_version
#     SCOPES = [scope for scope in scopes[0]]

#     cred = None
#     working_dir = os.getcwd()
#     token_dir = 'token_files'
#     token_file = f'token_{API_SERVICE_NAME}_{API_VERSION}{prefix}.json'

#     if not os.path.exists(os.path.join(working_dir, token_dir)):
#         os.mkdir(os.path.join(working_dir, token_dir))

#     if os.path.exists(os.path.join(working_dir, token_dir, token_file)):
#         cred = Credentials.from_authorized_user_file(os.path.join(working_dir, token_dir, token_file))

#     if not cred or not cred.valid:
#         if cred and cred.expired and cred.refresh_token:
#             cred.refresh(Request())
#         else:
#             flow = InstalledAppFlow.from_client_secrets_file(CLIENTE_SECRET_FILE, SCOPES)
#             cred = flow.run_local_server(port=0)

#         with open(os.path.join(working_dir, token_dir, token_file), 'w') as token:
#             token.write(cred.to_json())

#     try:
#         service = build(API_SERVICE_NAME, API_VERSION, credentials=cred)
#         print(API_SERVICE_NAME, 'service created successfully')
#         return service
#     except Exception as e:
#         print(f'Failed to create service for {API_SERVICE_NAME}')
#         print(e)
#         os.remove(os.path.join(working_dir, token_dir, token_file))
#         return None
    
# def convert_to_rfc_datetime(year, month, day, hour=0, minute=0):
#     return datetime.datetime(year, month, day, hour, minute, 0).isoformat() + 'Z'
    
import pickle
import os
import json
from google_auth_oauthlib.flow import Flow, InstalledAppFlow
from googleapiclient.discovery import build
#from googleapiclient.http import MediaFileUpload
from google.auth.transport.requests import Request
import requests

class GooglePhotosApi:
    def __init__(self,
                 api_name = 'photoslibrary',
                 client_secret_file= 'client_acc.json',
                 api_version = 'v1',
                 scopes = ['https://www.googleapis.com/auth/photoslibrary',
                           'https://www.googleapis.com/auth/photoslibrary.sharing']):
        '''
        Args:
            client_secret_file: string, location where the requested credentials are saved
            api_version: string, the version of the service
            api_name: string, name of the api e.g."docs","photoslibrary",...
            api_version: version of the api

        Return:
            service:
        '''

        self.api_name = api_name
        self.client_secret_file = client_secret_file
        self.api_version = api_version
        self.scopes = scopes
        self.cred_pickle_file = f'./token_{self.api_name}_{self.api_version}.pickle'

        self.cred = None

    def run_local_server(self):
        # is checking if there is already a pickle file with relevant credentials
        if os.path.exists(self.cred_pickle_file):
            with open(self.cred_pickle_file, 'rb') as token:
                self.cred = pickle.load(token)

        # if there is no pickle file with stored credentials, create one using google_auth_oauthlib.flow
        if not self.cred or not self.cred.valid:
            if self.cred and self.cred.expired and self.cred.refresh_token:
                self.cred.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(self.client_secret_file, self.scopes)
                self.cred = flow.run_local_server()

            with open(self.cred_pickle_file, 'wb') as token:
                pickle.dump(self.cred, token)

  
        return self.cred
    
    def create_service(self):
        try:
            service = build(self.api_name, self.api_version, credentials=self.cred, static_discovery=False)
            print(self.api_name, 'service created successfully')
            return service
        
        except Exception as e:
            print(f'Failed to create service for {self.api_name}')
            print(e)
            return None
            
    def list_album_files(self, service, title):
        request = service.albums().list().execute()
        if not request:
            return {}
        
        while True:
            albums = request.get('albums')
            for album in albums:
                if album['title'] == title:
                    album_id = album['id']
                    mediaItems= service.mediaItems().search(body={"albumId": album_id }).execute()['mediaItems']
                    return mediaItems
                    
            request = service.albums().list_next(request, request)
            if not request:
                return {}      

    def list_mediaItems(self, service):
        request = service.mediaItems().list().execute()
        if not request:
            return {}
        while True:
            media_items = request.get('mediaItems')
            for media_item in media_items:
                print(media_item)
            request = service.mediaItems().list_next(request, request)
            if not request:
                break

    def download_favorites(self, album_title):
        payload = {
            "filters":{
                "featureFilter":{
                    "includedFeatures":[
                        "FAVORITES"
                    ]
                }
            }
        }
        headers = {
            'content-type': 'application/json',
            'Authorization': 'Bearer {}'.format(self.cred.token)
        }
        try:
            res = requests.request("POST", "https://photoslibrary.googleapis.com/v1/mediaItems:search", headers=headers, data=json.dumps(payload))
        
        except:
            print("Erro na requisição")
            return
        if os.path.exists(album_title):
            print("Já há uma pasta com o nome do álbum")
            pass
        else:
            os.mkdir(album_title)
            for media in res.json()['mediaItems']:
                download_image(media['baseUrl'], f'{album_title}/{media["filename"]}')

    def list_album_favorites(self, service, title):
        request = service.albums().list().execute()

        if not request:
            return {}
        while True:
            albums = request.get('albums')
            for album in albums:
                if album['title'] == title:
                    album_id = album['id']
                    payload = {
                        "filters":{
                            "featureFilter":{
                                "includedFeatures":[
                                    "FAVORITES"
                                ]
                            }
                        }
                    }
                    return service.mediaItems().search(body=payload).execute()['mediaItems']

            next_request = service.albums().list_next(next_request, request)
            if not request:
                return {}

def list_albums(service, show=False):
    request = service.albums().list().execute()
    titles = []
    if not request:
        return {}
    
    while True:
        albums = request.get('albums')
        for album in albums:
            titles.append(album['title'])
        request = service.albums().list_next(request, request)
        if not request:
            break

    if show:
        for i in range(len(titles)):
            print(f'{i} - {titles[i]}')

    return titles

def print_media(mediaItems):
    for media in mediaItems:
        print(media['filename'])

def print_album_files(mediaItems):
    filenames = list()
    for media in mediaItems:
        filenames.append(media['filename'])
        print(media['filename'])
    return filenames