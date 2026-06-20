from plugins.plugin import PluginPrototype


class CasinoPlugin(PluginPrototype):

    def __init__(self, client=None):
        self.module_name = "Casino"
        self.module_version = "0.0.1"
        self.client = client
        self.register_actions()

    def set_client (self, client):
        self.client = client

    def register_actions(self):
        if self.client:
            pass
            # self.client.private_msg_handler.add_action("!test_function <message>", self._hook_reply_message, "EXAMPLE reply", "admin", f"{self.module_name} (Admin)")


def setup(client):
    return CasinoPlugin(client)
