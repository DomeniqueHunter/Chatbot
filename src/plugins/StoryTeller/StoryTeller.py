from plugins.Plugin_Prototype import Plugin_Prototype


class StoryTeller(Plugin_Prototype):

    def __init__(self, client=None):
        self.module_name = "StoryTeller"
        self.module_version = "1.0"
        self.client = client
        self.register_actions()

    def set_client (self, client):
        self.client = client
    
    def register_actions(self):
        if self.client:
            pass
    
        
