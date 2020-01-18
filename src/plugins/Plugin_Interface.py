from interface import implements, Interface

class Plugin_Interface(Interface):
    
    def set_client(self, client):
        pass
    
    def register_actions(self):
        pass
    
    def setup(self):
        pass
    
    def load(self):
        pass
    
    def save(self):
        pass
    
    async def clock(self):
        pass
    
    def _info(self):
        pass
    
    
    