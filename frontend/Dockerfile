FROM node:lts-alpine

RUN npm install -g http-server
RUN npm install -g amqplib


WORKDIR /app
# RUN npm install --save amqplib

COPY package*.json ./

RUN npm install

COPY . .

EXPOSE 3000
CMD ["npm", "start"]