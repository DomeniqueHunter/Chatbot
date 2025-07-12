#!/usr/bin/env python3

import os

from core.OpCodeHandler import OpCodeHandler as Client
from core.Plugin_Loader import Plugin_Loader

from lib.Config.Config import Config

# from webserver.Webserver import Webserver

PROJECT_ROOT = os.path.dirname(__file__)
config = Config(PROJECT_ROOT + '/config.json')

client = Client(config, PROJECT_ROOT + '/data')
client.set_plugin_loader(Plugin_Loader(PROJECT_ROOT + '/plugins/'))
client.load_plugins()

# start webserver in thread
# Webserver(client)

# forever!
client.start()
