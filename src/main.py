#!/usr/bin/env python3

import os

# from framework.op_code_handler import OpCodeHandler as Client
from framework.plugin_loader import Plugin_Loader
from framework.lib.config import Config

from framework.bot import Bot

# from webserver.Webserver import Webserver

PROJECT_ROOT = os.path.dirname(__file__)
config = Config(PROJECT_ROOT + '/config.json')

client = Bot(config, root_path=f"{PROJECT_ROOT}/data/", plugins_path=f"{PROJECT_ROOT}/plugins/")

# client.set_plugin_loader(Plugin_Loader(PROJECT_ROOT + '/plugins/'))
# client.load_plugins()

# start webserver in thread
# Webserver(client)

# forever!
client.start()
