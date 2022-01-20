import atexit
import base64
import io
import re
import os
import random
import shutil
import string
import magic
import pika

from flask import Flask, Response
from flask.helpers import send_file, send_from_directory
from threading import Thread

import config

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

DIRECTORY_LOCATION = 'data/'

@app.after_request
def after_request(response):
    response.headers.add('Accept-Ranges', 'bytes')
    return response

def get_random_string(length):
    # choose from all lowercase letter
    letters = string.ascii_lowercase
    result_str = ''.join(random.choice(letters) for i in range(length))
    return result_str
    
def read_file_chunks(path, byte1=None, byte2=None):
    file_size = os.stat(path).st_size
    start = 0
    
    if byte1 < file_size:
        start = byte1
    if byte2:
        length = byte2 + 1 - byte1
    else:
        length = file_size - start

    with open(path, 'rb') as f:
        f.seek(start)
        chunk = f.read(length)
    return chunk, start, length, file_size

@app.route("/file/<name>/<path:base64string>", methods=['POST'])
def upload(name, base64string):
    if not os.path.isdir(DIRECTORY_LOCATION):
        os.mkdir(DIRECTORY_LOCATION)

    tempdir = DIRECTORY_LOCATION + 'temp/'
    if not os.path.isdir(tempdir):
        os.mkdir(tempdir)

    path = DIRECTORY_LOCATION + name + '/'
    if not os.path.isdir(path):
        os.mkdir(path)

    with open(tempdir + 'tmp', "wb") as fh:
        fh.write(base64.b64decode(base64string))
        mimeType = magic.from_file(tempdir + 'tmp', mime=True)
        if mimeType.startswith('image') or base64string.startswith('data:image/jpeg;base64'):
            filenname = 'IMG'
            ending = '.jpg'
        elif mimeType.startswith('video'):
            filenname = 'VID'
            ending = '.mp4'
        else:            
            filenname = name
            ending = ''
            path = DIRECTORY_LOCATION
    os.remove(tempdir + 'tmp')
    
    if ending == '.jpg':
        onlyfiles = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
        i = 1
        while (filenname + str(i) + ending) in onlyfiles:
            i = i + 1
        
        base64string = base64string.replace('data:image/jpeg;base64,', '')
        with open(path + filenname + str(i) + ending, "wb") as fh:
            fh.write(base64.b64decode(base64string))
        print('wrote file to', path + filenname + str(i) + ending)
    else:
        with open(path + filenname + ending, "wb") as fh:
            fh.write(base64.b64decode(base64string))

    return 'Success'

@app.route("/file/<name>", methods=['GET'])
def download(name):
    path = DIRECTORY_LOCATION + name + '/'

    if os.path.isdir(path):
        tempdir = DIRECTORY_LOCATION + 'temp/'
        if not os.path.isdir(tempdir):
            os.mkdir(tempdir)

        return_data = io.BytesIO()
        shutil.make_archive(tempdir + 'tmp', 'zip', path)
        with open(tempdir + 'tmp.zip', 'rb') as fo:
            return_data.write(fo.read())
        os.remove(tempdir + 'tmp.zip')

        return_data.seek(0)

        return send_file(return_data, mimetype='application/zip')
    else:
        return send_from_directory(DIRECTORY_LOCATION, name)

@app.route("/file/video/<name>", methods=['GET'])
def downloadVideo(name):
    path = DIRECTORY_LOCATION + name + '/VID.mp4'

    resp = Response(open(path, 'rb'), direct_passthrough=True, mimetype='video/mp4', content_type='video/mp4')
    resp.headers['Content-Disposition'] = 'inline'
    return resp

if not config.TEST_MODE:
    rabbitMqUrl ='amqp://ai21-ws21-swe-rabbitmq?connection_attempts=5&retry_delay=4'

    # Producer
    print('setting up producer connection to rabbitMq using URL', rabbitMqUrl)
    connectionProducer = pika.BlockingConnection(pika.URLParameters(rabbitMqUrl))
    print('established producer connection to rabbitMq')
    channelProducer = connectionProducer.channel()
    channelProducer.queue_declare(queue='hello')
    print('declared producer rabbitmq queue \'hello\'')

    # Consumer
    print('setting up consumer connection to rabbitMq using URL', rabbitMqUrl)
    connectionConsumer = pika.BlockingConnection(pika.URLParameters(rabbitMqUrl))
    print('established consumer connection to rabbitMq')
    channelConsumer = connectionConsumer.channel()
    channelConsumer.queue_declare(queue='hello')
    print('declared consumer rabbitmq queue \'hello\'')

    @app.route("/test/rabbitmq", methods=['POST'])
    def testRabbitMqPublish():
        channelProducer.basic_publish(exchange='',
                        routing_key='hello',
                        body='Hello World!')
        print("published 'Hello World!'")    
        return {}


    def testRabbitMqCallback(ch, method, properties, body):
        print("testRabbitMqCallback: Received %r" % body)

    print('before basic_consume')
    channelConsumer.basic_consume(queue='hello',
                        auto_ack=True,
                        on_message_callback=testRabbitMqCallback)
    print('after basic_conume; before start_consuming')

    def startConsuming():    
        print('startConsuming: before start_consuming')
        channelConsumer.start_consuming()
        print('startConsuming: after start_consuming')

    thread = Thread(target = startConsuming)
    thread.start()
    print('after thread.start()')

    def close_rabbitmq_connection():
        connectionProducer.close()
        connectionConsumer.close()
        # thread.join() TODO necessary to call? when? before or after connection.close()?
        # TODO start_consuming is a blocking method. so thread should exit on its own probably
        print('Closed rabbitmq connections')

    atexit.register(close_rabbitmq_connection)
    # TODO shutdown signals: https://docs.python.org/2/library/signal.html

if __name__ == "__main__":
    app.run(threaded=True)