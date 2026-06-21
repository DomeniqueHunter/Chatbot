from plugins.plugin import PluginPrototype
from plugins.casino.logic import CasinoLogic
from plugins.casino.hooks import CasinoHooks


class CasinoPlugin(PluginPrototype):

    def __init__(self, client=None):
        self.module_name = "Casino"
        self.module_version = "0.0.1"
        self.client = client

        self.channels = []

        self.logic = CasinoLogic(self)
        self.hooks = CasinoHooks(self)

        self.casino_save_file_handle = "casino_channels"
        self.casino_save_file_type = "json"
        self.casino_save_file_name = f"{self.casino_save_file_handle}.{self.casino_save_file_type}"

    def set_client (self, client):
        self.client = client

    def register_actions(self):
        if self.client:
            self.client.public_msg_handler.add_action("!setcasinochannel", self.hooks.set_casino_channel, "Set Casino Channel", "admin", f"{self.module_name} (Admin)")

    def setup(self):
        self.client.file_manager.add(self.casino_save_file_handle, self.casino_save_file_name, self.casino_save_file_type)

    def save (self):
        if len(self.channels) > 0:
            self.client.file_manager.save(self.casino_save_file_handle, self.channels)

    def load(self):
        try:
            self.channels = self.client.file_manager.load(self.casino_save_file_handle) or []

        except:
            print (f"could not load data in '{self.module_name}'")
    
    async def clock(self):
        # TODO: check sessions
        pass


def setup(client):
    return CasinoPlugin(client)
