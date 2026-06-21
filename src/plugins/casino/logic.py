

class CasinoLogic:
    
    def __init__(self, main_module):
        self.casino:"Casino" = main_module
        
    def set_casino_channel(self, channel:str):
        if not channel in self.casino.channels:
            self.casino.channels.append(channel)
            
    def is_casino_channel(self, channel:str) -> bool:
        return channel in self.casino.channels