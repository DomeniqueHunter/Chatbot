from plugins import PluginPrototype
from framework.core_modules.bot_coins.database import UserWalletDB
from framework.lib.counter import Counter
from framework.core_modules.bot_coins.hooks import BotCoinHooks
from framework.core_modules.bot_coins.logic import BotCoinLogic


class BotCoins(PluginPrototype):

    def __init__(self, bot):
        self.bot = bot

        self.config = self.bot.config.get("core_modules", dict()).get("bot_coins", dict())
        if not self.config:
            print("could not find the core_modules config for bot_coins")

        self.module_name = "BotCoin"
        self.module_version = "0.1.10"

        print(f"initializing Bot Coin Plugin")
        self.user_wallet_db = UserWalletDB(self.bot.file_manager)

        # from config
        self.module_enabled = self.config.get("enabled", True)
        self.currency = self.config.get("currency", "coin")
        self.symbol = self.config.get("symbol", "c")
        self.coins_per_tick = int(self.config.get("coins_per_tick", 0))
        self.interval = int(self.config.get("interval_min", 42))

        count_to = self.interval * 2
        if self.module_enabled:
            self.counter = Counter(count_to)

        self.logic = BotCoinLogic(self)
        self.hooks = BotCoinHooks(self)

    def __get_users_in_channels(self):
        current_users = []
        for _, channel in self.bot.channel_manager.joined_channels.items():
            channel_users = channel.characters.get()
            current_users.extend(channel_users)

        # remove doubles
        current_users = list(set(current_users))

        for user in current_users:
            self.add_coins(str(user), self.coins_per_tick, create_if_not_exists=True)

        self.save()

    def has_wallet(self, user:str) -> bool:
        if not self.module_enabled: return False
        if self.user_wallet_db.get_wallet_id(user):
            return True
        return False

    def get_wallet(self, user:str) -> tuple:
        if not self.module_enabled: return None, None
        if wallet_id := self.user_wallet_db.get_wallet_id(user):
            return wallet_id, self.user_wallet_db.get_wallet_by_id(wallet_id)
        else:
            return None, None

    def give_coins_to(self, from_user:str, to_user:str, number:int):
        if not self.module_enabled: return
        self.user_wallet_db.transfer_amount(from_user, to_user, number)
        self.save()

    def add_coins(self, user:str, number:int, create_if_not_exists=False):
        if not self.module_enabled: return
        check = self.user_wallet_db.add_amount(user, number, create_if_not_exists)
        if not check:
            print(f"{user} does not exist")
        self.save()

    def remove_coins(self, user:str, number:int) -> bool:
        if not self.module_enabled: return
        check = self.user_wallet_db.remove_amount(user, number)
        self.save()
        return check

    def create_wallet(self, user:str) -> bool:
        if not self.module_enabled: return
        check = self.user_wallet_db.add_user(user)
        self.save()
        return check

    def check_balance(self, user:str, number:int | float) -> bool:
        return self.user_wallet_db.check_amount(user, number)

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
            self.bot.private_msg_handler.add_action("!mywallet", self.hooks.show_wallet, "shows your wallet", "user", f"{self.module_name} (Direct)")
            self.bot.private_msg_handler.add_action("!create_wallet", self.hooks.create_wallet, "creates your wallet", "user", f"{self.module_name} (Direct)")
            self.bot.private_msg_handler.add_action("!send_coins <person>, <amount>", self.hooks.give_coins_to, "send coins to ther person", "user", f"{self.module_name} (Direct)")

            self.bot.private_msg_handler.add_action("!admin_add_coins <user:str> <amount:int>", self.hooks.admin_add_coins, "DEBUG add coins to user wallet", "admin", f"{self.module_name} (Admin)")
            self.bot.private_msg_handler.add_action("!admin_coin_statistics", self.hooks.admin_coin_statistics, "show wallet db statistics", "admin", f"{self.module_name} (Admin)")
        else:
            print("no client")

    async def clock(self):
        if self.counter.tick():
            self.__get_users_in_channels()


def setup(bot):
    return BotCoins(bot)
