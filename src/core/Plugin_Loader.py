import os, sys

class Plugin_Loader():
    
    def __init__(self, plugins_dir = '', client  = None):
        self.plugins_dir = plugins_dir
        self.plugins = {}
        self.client = client
    
    def set_client(self, client):
        self.client = client
        
    def load_plugins(self):
        self._extend_path()
        self._load_plugins()
        try:
            pass
        except:
            e = sys.exc_info()[0]
            print ("critial error {}".format(e))
        
    def _load_plugins(self):
        for plugin in os.listdir(self.plugins_dir):
            if (not plugin.startswith("_") and not '.py' in plugin):
                plugin_path = self.plugins_dir+'/'+plugin+'/'
                exec ("from plugins.{}.{} import {}".format(plugin, plugin, plugin))
                exec ("self.plugins['{}'] = {}()".format(plugin, plugin))
                self.plugins[plugin].set_client(self.client)
                self.plugins[plugin].setup()
                self.plugins[plugin].register_actions()                
                print ("Plugin: {}.{}.{} import {}".format('plugins', plugin, plugin,plugin))
        
                
    def _extend_path(self):
        for module in os.listdir(self.plugins_dir):
            if (not module.startswith("_")):
                plugin = self.plugins_dir+'/'+module+'/'
                sys.path.append(plugin)
                
    def get_plugin(self, plugin):
        if plugin in self.plugins:
            return self.plugins[plugin]