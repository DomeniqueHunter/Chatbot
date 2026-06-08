from plugins import PluginPrototype
from framework.core_modules.channel_coins.database import UserWalletDB


class ChannelCoins(PluginPrototype):

    def __init__(self, bot):
        self.bot = bot
        self.module_name = "Channel Coin"
        self.module_version = "0.1"
        print(f"initializing Channel Coin Plugin")
        self.user_wallet_db = UserWalletDB()
        
    def setup(self):
        self.user_wallet_db.load_all()
        
    def load(self):
        self.user_wallet_db.load_all()
        
    def save(self):
        self.user_wallet_db.save_all()


def setup(bot):
    return ChannelCoins(bot)
