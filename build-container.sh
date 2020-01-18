#!/bin/bash

docker rmi -f dh/chatbot
docker build -t dh/chatbot .
