from plugins import PluginPrototype


class ChannelCoins(PluginPrototype):

    def __init__(self, bot):
        self.bot = bot
        self.module_name = "Channel Coin"
        self.module_version = "0.1"
        print(f"initializing Channel Coin Plugin")


def setup(bot):
    return ChannelCoins(bot)
