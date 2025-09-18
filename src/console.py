#!/usr/bin/python3

import os
import aiohttp, asyncio
import requests
import aiohttp
import json

from core.lib.Config import Config as Config
from core.lib.HTTPClient import HTTPClient

import binascii

PROJECT_ROOT = os.path.dirname(__file__)+'/'
cfg = Config(PROJECT_ROOT+'/config.json', False)

server = "{}://{}:{}".format(cfg.webserver['protocol'], cfg.webserver['host'], cfg.webserver['port'])



# don't do thix, use new http module!
async def send_get_request(endpoint):
    headers = {"secret": str(cfg.webserver["secret"]), "content_type": "application/json"}
    resp = await HTTPClient.get(endpoint, headers)
    
    print (str(resp))
    
async def send_post_request(endpoint, data={}, headers = {'secret': cfg.webserver['secret']}):
    response = requests.post(endpoint, data=data, headers=headers)
    resp = response.content.decode('utf-8')
    print (str(resp))

async def main():
    pass



loop = asyncio.new_event_loop()
loop.run_until_complete(send_get_request(server + "/ranch/cows"))
#loop.run_until_complete(send_post_request(server  + "/save"))
