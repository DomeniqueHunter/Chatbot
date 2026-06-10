
from framework.lib.argument.parser import parse

class BotCoinHooks():
    
    def __init__(self, module):
        self.bot_coin = module
        
    async def admin_add_coins(self, user:str, input_str:str=" , "):
        for_user, amount = parse(input_str, str, int)
        
        if self.bot_coin.bot.is_owner(user) and for_user and amount != 0:
            print(for_user, amount)
            
            if amount > 0:
                self.bot_coin.add_coins(user, amount)
                
            else:
                self.bot_coin.remove_coins(user, amount)