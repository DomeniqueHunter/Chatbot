#!/usr/bin/env python3

import os

from framework import Client
from framework import Config

# from webserver.Webserver import Webserver

PROJECT_ROOT = os.path.dirname(__file__)
config = Config(PROJECT_ROOT + '/config.json')

client = Client(config, PROJECT_ROOT + '/data')

client.enable_plugin_loader(plugins_dir=f"{PROJECT_ROOT}/plugins/")
client.load_plugins()

# start webserver in thread
# Webserver(client)

# forever!
client.start()
