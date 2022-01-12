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
    
@app.route("/file/<path:base64string>", methods=['POST'])
def upload(base64string):
    filename = get_random_string(50)
    if not os.path.isdir(DIRECTORY_LOCATION):
        os.mkdir(DIRECTORY_LOCATION)

    with open(DIRECTORY_LOCATION + filename, "wb") as fh:
        fh.write(base64.b64decode(base64string))
    print('wrote file to', DIRECTORY_LOCATION + filename)
    return filename

@app.route("/file/<fileCode>", methods=['GET'])
def download(fileCode):
    print('try to download file', fileCode)
    return send_from_directory(DIRECTORY_LOCATION, fileCode)