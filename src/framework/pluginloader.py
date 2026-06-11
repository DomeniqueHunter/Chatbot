import os
from types import ModuleType
import importlib


class PluginLoader():

    def __init__(self, plugins_dir:str='plugins', client=None, module_path:str="plugins"):
        self.plugins_dir = plugins_dir  # can be str opr Path
        self.plugins = {}
        self.client = client
        self.module_path = module_path

    def set_client(self, client):
        self.client = client

    def load_plugins(self) -> None:
        for plugin_name in os.listdir(self.plugins_dir):
            if plugin_name.startswith("_") or not os.path.isdir(
                os.path.join(self.plugins_dir, plugin_name)
            ):
                continue

            try:
                module_path = f"{self.module_path}.{plugin_name}.{plugin_name}"
                module: ModuleType = importlib.import_module(module_path)
                
                if hasattr(module, plugin_name):
                    plugin_class = getattr(module, plugin_name)
                    plugin_instance = plugin_class()
                    plugin_instance.set_client(self.client)

                elif hasattr(module, "setup"):
                    plugin_instance = module.setup(self.client)


                self.plugins[plugin_name] = plugin_instance
                plugin_instance.setup()
                plugin_instance.register_actions()

            except Exception as e:
                print(f"Failed to load plugin '{plugin_name}': {e}")

    def check_plugin(self, plugin) -> bool:
        return plugin in self.plugins

    def get_plugin(self, plugin):
        if plugin in self.plugins:
            return self.plugins[plugin]
