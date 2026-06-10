from plugins import PluginPrototype
from framework.core_modules.bot_coins.database import UserWalletDB
from framework.lib.counter import Counter
from framework.core_modules.bot_coins.hooks import BotCoinHooks


class BotCoins(PluginPrototype):

    def __init__(self, bot):
        self.bot = bot
        self.hooks = BotCoinHooks(self)

        self.config = self.bot.config.get("core_modules", dict()).get("bot_coins", dict())

        self.module_name = "BotCoin"
        self.module_version = "0.1.7"
        self.module_enabled = self.config.get("enabled") or True

        print(f"initializing Bot Coin Plugin")
        self.user_wallet_db = UserWalletDB(self.bot.file_manager)

        self.coins_per_interval = int(self.config.get("coins_per_tick", 0))
        interval = int(self.config.get("interval_min", 42))

        # count_to = interval * 30
        self.counter = Counter(1)

    def __get_users_in_channels(self):
        current_users = []
        for _, channel in self.bot.channel_manager.joined_channels.items():
            channel_users = channel.characters.get()
            current_users.extend(channel_users)

        # remove doubles
        current_users = list(set(current_users))

        for user in current_users:
            self.add_coins(str(user), self.coins_per_interval)

        self.save()

    def give_coins_to(self, from_user:str, to_user:str, number:int):
        self.user_wallet_db.transfer_amount(from_user, to_user, number)

    def add_coins(self, user:str, number:int):
        print(f"add {user} {number}")
        self.user_wallet_db.add_amount(user, number)

    def remove_coins(self, user:str, number:int):
        self.user_wallet_db.remove_amount(user, number)

    def setup(self):
        self.user_wallet_db.load_all()

    def load(self):
        if self.module_enabled:
            self.user_wallet_db.load_all()

    def save(self):
        if self.module_enabled:
            self.user_wallet_db.save_all()

    def register_actions(self):
        if self.bot:
            self.bot.private_msg_handler.add_action("!admin_add_coins <user:str> <amount:int>", self.hooks.admin_add_coins, "DEBUG add coins to user wallet", "admin", f"{self.module_name} (Admin)")
        else:
            print("no client")

    async def clock(self):
        if self.counter.tick():
            # TODO: give coins
            print("give coins!")
            self.__get_users_in_channels()


def setup(bot):
    return BotCoins(bot)
