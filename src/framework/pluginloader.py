import os, sys
from types import ModuleType
import importlib


class PluginLoader():
    
    def __init__(self, plugins_dir:str='plugins', client=None):
        self.plugins_dir = plugins_dir
        self.plugins = {}
        self.client = client
    
    def set_client(self, client):
        self.client = client
        
    def load_plugins(self) -> None:
        for plugin_name in os.listdir(self.plugins_dir):
            if plugin_name.startswith("_") or not os.path.isdir(
                os.path.join(self.plugins_dir, plugin_name)
            ):
                continue

            try:
                module_path = f"plugins.{plugin_name}.{plugin_name}"
                module: ModuleType = importlib.import_module(module_path)

                plugin_class = getattr(module, plugin_name)
                plugin_instance = plugin_class()

                self.plugins[plugin_name] = plugin_instance
                plugin_instance.set_client(self.client)
                plugin_instance.setup()
                plugin_instance.register_actions()

                print(f"Loaded plugin: {plugin_name} [{module_path}]")

            except Exception as e:
                print(f"Failed to load plugin '{plugin_name}': {e}")
                
    def check_plugin(self, plugin) -> bool:
        return plugin in self.plugins
                
    def get_plugin(self, plugin):
        if plugin in self.plugins:
            return self.plugins[plugin]
