# HTW-AI21SWEGRPB02

# Runnung the server
Have a docker environment file `.env`. Windows example:

    HOST_VOLUME_PATH=//c/my/path/to/the/volume/data


`docker-compose up -d --build`

`-d` means to run in background
`--build` forces a build
`--force-recreate` forces the docker image to rebuild

API available under `http://localhost:5000/` 