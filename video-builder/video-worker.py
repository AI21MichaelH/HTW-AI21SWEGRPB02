import base64
import os
import shutil

import atexit
import pika
from threading import Thread

import cv2
import requests

import config

# fileRepoUrl = 'http://localhost:5000'
fileRepoUrl = 'http://htwai21swegrpb02:5000' # if running with docker compose
downloadUrl = fileRepoUrl + '/file/{name}'
uploadUrl = fileRepoUrl + '/file/{name}/{base64String}'
tempdir = 'temp/'

def onCall(ch, method, properties, body):
    print('Video Builder got message: ', body)
    body = body.decode('UTF-8') # TODO catch exception if it is a string rather than a byte-like object?
    if body.split('|')[0].lower() == 'video request':        
        videoName = body.split('|')[1]
        print('is video request with videoName: ', videoName)
        url = downloadUrl.format(name = videoName)
        print('url for file download is: ', url)
        videoPath = tempdir + videoName + '/' + videoName + '.mp4'
        print('videoPath: ', videoPath)
        response = requests.get(url)
        print('response from url: ', response)
        if not os.path.isdir(tempdir):
            os.mkdir(tempdir)
        
        open(tempdir + videoName + '.zip', 'wb').write(response.content)
        shutil.unpack_archive(tempdir + videoName + '.zip', tempdir + videoName)
        os.remove(tempdir + videoName + '.zip')

        images = [img for img in os.listdir(tempdir + videoName) if img.endswith(".jpg")]
        print('images:', images)
        frame = cv2.imread(os.path.join(tempdir + videoName, images[0]))
        height, width, _ = frame.shape
        print('height:', height, ', width:', width)
        fourcc = 0x00000021 # Codec needed for Web Viewing
        video = cv2.VideoWriter(videoPath, fourcc, 1, (width,height))    
        for image in images:
            video.write(cv2.imread(os.path.join(tempdir + videoName, image)))
        print('after writing images to video')
        cv2.destroyAllWindows()
        video.release()
        print('video released')
        with open(videoPath, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read())
            encoded_string = encoded_string.decode('ascii')
        shutil.rmtree(tempdir + videoName)

        url = uploadUrl.format(name = videoName, base64String = encoded_string)
        print('url for upload is: ', url);
        response = requests.post(url)
        print('response from upload: ', response)
        if not config.TEST_MODE:
            channelProducer.basic_publish(exchange='',
                            routing_key='hello',
                            body='New Video available|{name}'.format(name='videoName'))
            print("published a new video")    

if config.TEST_MODE:
    onCall('', '', '', 'Video request|test')
else:
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

    print('before basic_consume')
    channelConsumer.basic_consume(queue='hello',
                        auto_ack=True,
                        on_message_callback=onCall)
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
        print('Closed rabbitmq connections')

    atexit.register(close_rabbitmq_connection)