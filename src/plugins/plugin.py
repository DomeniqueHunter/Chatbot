# kind of an interface
class PluginPrototype():

    def __init__(self):
        self.module_name = "PluginPrototype"
        self.module_version = "1.0"

    def set_client(self, client):
        """
            The Plugin needs the client which perfoms the actions
        """
        self.client = client

    def register_actions(self):
        """
            Register the actions, on which the client should react
        """
        pass
    
    def setup(self):
        """
            Setup the Things before running
        """
        print(self.info())
        
    def load(self):
        """
            If you stored data, here you can load them
        """
        pass

    def save (self):
        """
            If you want to store some data, do it here
        """
        pass
    
    async def clock(self):
        """
            To run clocked events.
            The Server Ping triggers this method
        """    
        pass
    
    def info(self) -> str:
        return f"\nModule Name: {self.module_name}\nModule Version: {self.module_version}"
