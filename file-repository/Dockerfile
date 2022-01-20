# For more information, please refer to https://aka.ms/vscode-docker-python
FROM python:slim

EXPOSE 5000

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

RUN apt-get update
RUN apt-get --yes install libmagic1

# Install pip requirements
COPY requirements.txt .
RUN python -m pip install -r requirements.txt

WORKDIR /api
COPY . /api

# Creates a non-root user with an explicit UID and adds permission to access the /api folder
# For more info, please refer to https://aka.ms/vscode-docker-python-configure-containers
RUN adduser -u 5678 --disabled-password --gecos "" appuser && chown -R appuser /api
USER appuser

# During debugging, this entry point will be overridden. For more information, please refer to https://aka.ms/vscode-docker-python-debug
# app in api:app seems to correspond to the variable app in api.py
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "api:app"]
