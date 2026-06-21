

class CasinoHooks:
    
    def __init__(self, main_module):
        self.casino:"Casino" = main_module
        
    async def set_casino_channel(self, user:str, channel:str) -> bool:
        if self.casino.client.has_admin_rights(user.strip()):
            pass