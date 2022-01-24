const http = require('http');
const fs = require('fs');
const path = require('path');

const amqp = require('amqplib/callback_api');
const { syncBuiltinESMExports } = require('module'); // TODO why is this needed? copy/paste mistake?
var amqpChannel;
const queue = 'hello';
var retry_delay_ms = 4000;
var connection_attempts = 5;
var connection_attempts_counter = 0;
var connection_error = false
var err;

function sleep(ms) {
    return new Promise(resolve => {
        setTimeout(resolve, ms)
    })
}

async function connectToAmqp() {
    amqp.connect('amqp://ai21-ws21-swe-rabbitmq?connection_attempts=5&retry_delay=4',async(error0, connection) => {
                if (error0) {
                    console.log('Error on amqp initialization: ', error0);    
                    connection_error = true                    
                    connection_attempts_counter++;
                    console.log('Attempt: ', connection_attempts_counter);
                    if(connection_attempts_counter < connection_attempts) {
                        await sleep(retry_delay_ms);
                        connectToAmqp();
                        return;
                    } else {
                        throw error0;
                    }                    
                }
                console.log('Connected frontend server to queue');
                connection.createChannel((error1, channel) => {
                    if (error1) {
                        throw error1;
                    }
                    console.log('Created channel for frontend server');
                    channel.assertQueue(queue, {
                        durable: false
                    });
                    amqpChannel = channel;
                    console.log('Asserted queue for frontend server')
                });
            });
}
connectToAmqp();
    
const hostname = '0.0.0.0';
const port = 3000;

const server = http.createServer((req, res) => {
    console.log('Request for ' + req.url + ' by method ' + req.method);

    if (req.method == 'GET') {
        var fileUrl;
        if (req.url == '/') fileUrl = '/index.html';
        else fileUrl = req.url;

        var filePath = path.resolve('./public' + fileUrl);
        const fileExt = path.extname(filePath);
        if (fileExt == '.html') {
            fs.exists(filePath, (exists) => {
                if (!exists) {
                    filePath = path.resolve('./public/404.html');
                    res.statusCode = 404;
                    res.setHeader('Content-Type', 'text/html');
                    fs.createReadStream(filePath).pipe(res);
                    return;
                }
                res.statusCode = 200;
                res.setHeader('Content-Type', 'text/html');
                fs.createReadStream(filePath).pipe(res);
            });
        } else if(fileExt == '.js'){
            res.statusCode = 200;
            res.setHeader('Content-Type', 'text/html');
            fs.createReadStream(filePath).pipe(res);
        } else if (fileExt == '.css') {
            res.statusCode = 200;
            res.setHeader('Content-Type', 'text/css');
            fs.createReadStream(filePath).pipe(res);
        }
        else {
            filePath = path.resolve('./public/404.html');
            res.statusCode = 404;
            res.setHeader('Content-Type', 'text/html');
            fs.createReadStream(filePath).pipe(res);
        }
    }
    else if(req.method == 'POST') {
        console.log('POST req.url:', req.url);
        if(req.url == '/messages') {
            
            var body = '';
            req.on('data', chunk => {
                body += chunk;
            });
            req.on('end', () => {
                console.log('body:', body);
                amqpChannel.sendToQueue(queue, Buffer.from(body));
                res.writeHead(200, {'Content-Type': 'text/plain'});
                res.write('Sent message: ' + body);
                res.end();
            })
        } else {
            filePath = path.resolve('./public/404.html');
            res.statusCode = 404;
            res.setHeader('Content-Type', 'text/html');
            fs.createReadStream(filePath).pipe(res);
        }
        
    } else {
        filePath = path.resolve('./public/404.html');
        res.statusCode = 404;
        res.setHeader('Content-Type', 'text/html');
        fs.createReadStream(filePath).pipe(res);
    }
});


server.listen(port, hostname, () => {
    console.log(`Server running at http://${hostname}:${port}/`);
});
