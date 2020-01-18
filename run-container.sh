#!/bin/bash

THIS_DIR=$(dirname $(readlink -f $0))

if [ ! -d ./data ]; then
    mkdir ${THIS_DIR}/data
fi

docker rm -f chatbot
docker run -i -t \
    -v "${THIS_DIR}/data":/bot/data \
    --name chatbot \
    --restart always \
    -d dh/chatbot
