#232
#32
import numpy as np
import skimage as ski
import imageio.v3 as imageio
import matplotlib.pyplot as plt
import cv2
import os
from PIL import Image
from google_apis import GooglePhotosApi
from google_apis import list_albums
from google_apis import print_album_files

google_photos_api = GooglePhotosApi()
creds = google_photos_api.run_local_server()
service = google_photos_api.create_service()


available_albums = list_albums(service, show=True)
test = input("1 - Imprime todos os albuns\n2 - Imprime todos os arquivos do album\n3 - Imprime todos os favoritos\n4 - Imprime os favoritos do album\n5 - Baixa os favoritos\n")

match test:
    case "1":
        list_albums(service, print=True)
        
    case "2":
        # available_albums = list_albums(service)
        index = input("Insira o número do album que deseja ver os arquivos\n")
        filename_list = google_photos_api.list_album_files(service, available_albums[int(index)])
        print_album_files(filename_list)

    case "3":
        favorites = google_photos_api.download_favorites(available_albums[0])
        for media in favorites:
            print(media['filename'])

    case "4":
        albumFavs = google_photos_api.list_album_favorites(service, available_albums[0])
        print_album_files(albumFavs)

    case "5":
        index = input("Selecione o índice do album a ser baixado:")
        google_photos_api.download_favorites(available_albums[int(index)])









# def main():
#     new_size = (1024,1024)

#     image = cv2.imread("Scan34148.jpg")
#     img = cv2.resize(image, (960,560), interpolation=cv2.INTER_AREA)
#     new_img = np.full((new_size[0], new_size[1], 3), 255)
#     new_img[232:1024-232,32:1024-32] = img
#     cv2.imwrite("new_img.jpg", new_img)

    

# if __name__ == "__main__":
#     main()