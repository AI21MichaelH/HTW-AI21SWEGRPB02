FROM python:slim

RUN apt-get update
RUN apt-get install ffmpeg libsm6 libxext6  -y

COPY requirements.txt .
RUN python -m pip install -r requirements.txt

WORKDIR /app
COPY video-worker.py ./
COPY config.py ./

CMD ["python", "./video-worker.py"]