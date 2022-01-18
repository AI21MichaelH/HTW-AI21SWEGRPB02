import base64
import os
import shutil

import cv2
import requests

import config

fileRepoUrl = 'http://localhost:5000'
downloadUrl = fileRepoUrl + '/file/{name}'
uploadUrl = fileRepoUrl + '/file/{name}/{base64String}'
tempdir = 'temp/'

def onCall(videoName):
    url = downloadUrl.replace('{name}', videoName)
    videoPath = tempdir + videoName + '/' + videoName + '.avi'

    response = requests.get(url)
    if not os.path.isdir(tempdir):
        os.mkdir(tempdir)
    
    open(tempdir + videoName + '.zip', 'wb').write(response.content)
    shutil.unpack_archive(tempdir + videoName + '.zip', tempdir + videoName)
    os.remove(tempdir + videoName + '.zip')

    images = [img for img in os.listdir(tempdir + videoName) if img.endswith(".jpg")]
    frame = cv2.imread(os.path.join(tempdir + videoName, images[0]))
    height, width, _ = frame.shape

    video = cv2.VideoWriter(videoPath, 0, 1, (width,height))
    for image in images:
        video.write(cv2.imread(os.path.join(tempdir + videoName, image)))

    cv2.destroyAllWindows()
    video.release()

    with open(videoPath, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read())
        encoded_string = encoded_string.decode('ascii')
    shutil.rmtree(tempdir + videoName)

    url = uploadUrl.replace('{name}', videoName).replace('{base64String}', encoded_string)
    response = requests.post(url)

if config.TEST_MODE:
    onCall('test')