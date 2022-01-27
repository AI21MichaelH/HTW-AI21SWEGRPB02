# HTW-AI21SWEGRPB02
+ Christina Obereigner
+ Maximilian Deutsch
+ Michael Hermann-Hubler

# Running the server
Have a docker environment file `.env`. Windows example:

    HOST_VOLUME_PATH=//c/my/path/to/the/volume/data


`docker-compose up --build`

`-d` means to run in background  
`--build` forces a build  
`--force-recreate` forces the docker image to rebuild

API available under `http://localhost:5000/` 
Frontend available under `http://localhost:3000`

# Using the service

## Uploading

To upload a file, the Base64 String of the file has to be supplied in the call.

The endpoint is /file with request method POST

An example call is `http://localhost:5000/file/VGVzdA==`

The answer will supply an unique token that can be used to access the file. This token is created randomly and cannot be recreated by uploading the same file again.

## Downloading

To download a file you have to supply the unique token in the call.

The endpoint is /file with request method GET

An example call is `http://localhost:5000/file/pbjjgoojjnkaahstajumojutzyakdcbtaiopwrlknlryqjtcna`

The file will returned and downloaded
