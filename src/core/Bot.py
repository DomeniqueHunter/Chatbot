from core import *

class Bot():
    
    def __init__(self, config, root_path = "./"):
        self.core = Core(config, root_path)
        self.chat_code_handler = ChatCodeHandler(config, root_path)
        self.opcode_hander = OpCodeHandler(config, root_path)
    
    
    def create_message_handler(self):
        self._create_private_message_handler()
        self._create_public_message_handler()
        self._create_opcode_handler()
    
    def _create_private_message_handler(self):
        self.private_message_hadler = Reaction()
    
    def _create_public_message_handler(self):
        self.public_message_handler = Reaction()
        
    def _create_opcode_handler(self):
        self.opcode_handler = Reactions()
            
    def run(self):
        pass
    
    