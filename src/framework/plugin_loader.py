import os, sys
from types import ModuleType
import importlib


class Plugin_Loader():
    
    def __init__(self, plugins_dir:str='plugins', client=None):
        self.plugins_dir = plugins_dir
        self.plugins = {}
        self.client = client
    
    def set_client(self, client):
        self.client = client
        
    def load_plugins(self) -> None:
        """Load all plugins from the given directory."""
        self._extend_path()

        for plugin_name in os.listdir(self.plugins_dir):
            if plugin_name.startswith("_") or not os.path.isdir(
                os.path.join(self.plugins_dir, plugin_name)
            ):
                continue

            try:
                module_path = f"{self.plugins_dir}.{plugin_name}.{plugin_name}"
                module: ModuleType = importlib.import_module(module_path)

                plugin_class = getattr(module, plugin_name)
                plugin_instance = plugin_class()

                self.plugins[plugin_name] = plugin_instance
                plugin_instance.set_client(self.client)
                plugin_instance.setup()
                plugin_instance.register_actions()

                print(f"Loaded plugin: {module_path}")

            except Exception as e:
                print(f"Failed to load plugin '{plugin_name}': {e}")
                
    def _extend_path(self):
        for module in os.listdir(self.plugins_dir):
            if (not module.startswith("_")):
                plugin = self.plugins_dir + '/' + module + '/'
                sys.path.append(plugin)
                
    def get_plugin(self, plugin):
        if plugin in self.plugins:
            return self.plugins[plugin]
