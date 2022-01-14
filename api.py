import random
import string
import base64
import os

from flask import Flask
from flask.helpers import send_from_directory

app = Flask(__name__)
DIRECTORY_LOCATION = 'data/'

def get_random_string(length):
    # choose from all lowercase letter
    letters = string.ascii_lowercase
    result_str = ''.join(random.choice(letters) for i in range(length))
    return result_str
    
@app.route("/file/<name>/<path:base64string>", methods=['POST'])
def upload(name, base64string):
    if not os.path.isdir(DIRECTORY_LOCATION):
        os.mkdir(DIRECTORY_LOCATION)

    path = DIRECTORY_LOCATION + name + '/'
    if not os.path.isdir(path):
        os.mkdir(path)

    onlyfiles = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
    filenname = 'IMG'
    ending = '.jpg'
    
    if ending == '.jpg':
        i = 1
        while (filenname + str(i) + ending) in onlyfiles:
            i = i + 1
        
        with open(path + filenname + str(i) + ending, "wb") as fh:
            fh.write(base64.b64decode(base64string))
        print('wrote file to', path + filenname + str(i) + ending)
    else:
        with open(name + ending, "wb") as fh:
            fh.write(base64.b64decode(base64string))

    return 'Success'

@app.route("/file/<fileCode>", methods=['GET'])
def download(fileCode):
    print('try to download file', fileCode)
    return send_from_directory(DIRECTORY_LOCATION, fileCode)
