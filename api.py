import random
import string
import base64
import os

from flask import Flask
from flask.helpers import send_from_directory

import pika
import atexit
from threading import Thread
from flask import jsonify

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

            # 'amqp://rabbit_mq?connection_attempts=10&retry_delay=10'

rabbitMqUrl = 'amqp://ai21-ws21-swe-rabbitmq?connection_attempts=5&retry_delay=4'


# Producer
print('setting up producer connection to rabbitMq using URL', rabbitMqUrl)
connectionProducer = pika.BlockingConnection(pika.URLParameters(rabbitMqUrl))
print('established producer connection to rabbitMq')
# connection = pika.BlockingConnection(pika.ConnectionParameters('ai21-ws21-swe-rabbitmq.com'))
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