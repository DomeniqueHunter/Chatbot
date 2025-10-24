#!/usr/bin/env python3

from framework import Client
from framework.lib.config import Config

from pathlib import Path

PROJECT_ROOT = Path(__file__).parent

config_path = PROJECT_ROOT / 'config.json'
config = Config(str(config_path))

data_path = PROJECT_ROOT / 'data'
client = Client(config, str(data_path))

plugins_path = PROJECT_ROOT / 'plugins'
client.enable_plugin_loader(plugins_dir=plugins_path)
client.load_plugins()

# start webserver in thread
# from webserver.Webserver import Webserver
# Webserver(client)

# forever!
client.start()
