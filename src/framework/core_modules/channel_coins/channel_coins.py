from plugins import PluginPrototype
from framework.core_modules.channel_coins.database import UserWalletDB


# TODO: rename to BotCoin ?
class ChannelCoins(PluginPrototype):

    def __init__(self, bot):
        self.bot = bot
        self.config = self.bot.config.get("core_modules", dict()).get("channel_coin", dict())
        
        # TODO: 
        # read config to enable/disable coin module
        # check if config/core_modules/channel_coins exists
        # read config for modul setting
        
        self.module_name = "Channel Coin"
        self.module_version = "0.1"
        self.module_enabled = True
        
        print(f"initializing Channel Coin Plugin")
        self.user_wallet_db = UserWalletDB(self.bot.file_manager)
        
    def setup(self):
        self.user_wallet_db.load_all()
        
    def load(self):
        if self.module_enabled:
            self.user_wallet_db.load_all()
        
    def save(self):
        if self.module_enabled:
            self.user_wallet_db.save_all()


def setup(bot):
    return ChannelCoins(bot)
