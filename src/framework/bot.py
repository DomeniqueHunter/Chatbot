from .core import Core
from .chat_code_handler import ChatCodeHandler
from .op_code_handler import OpCodeHandler

from .plugin_loader import Plugin_Loader


class Bot():
    
    def __init__(self, config, root_path="./", plugins_path="./plugins"):
        self.config = config
        self.root_path = root_path
        
        self.core = Core(self)
        self.chat_code_handler = ChatCodeHandler(self)
        self.op_code_handler = OpCodeHandler(self)
        
        self.plugin_loader = Plugin_Loader(f"{plugins_path}")
        
    def load_plugins(self):
        pass
            
    def start(self):
        self.op_code_handler.start()
    
    
