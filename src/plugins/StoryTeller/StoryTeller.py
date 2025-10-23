from plugins.plugin import PluginPrototype
from plugins.StoryTeller.hooks import Hooks


class StoryTeller(PluginPrototype):

    def __init__(self, client=None):
        self.module_name = "StoryTeller"
        self.module_version = "1.0"
        self.client = client
        self.register_actions()
        
        self.hooks = Hooks(self)

    def set_client (self, client):
        self.client = client
    
    def register_actions(self):
        if self.client:
            pass
        
