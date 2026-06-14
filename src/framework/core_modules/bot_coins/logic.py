

class BotCoinLogic:

    def __init__(self, module):
        self.bot_coin:"BotCoins" = module
        self.database = self.bot_coin.user_wallet_db

    def admin_statistics(self) -> tuple:
        wallets = self.database.wallets
        users = self.database.users

        _len = len(wallets.values())
        _min = min(wallets.values())
        _max = max(wallets.values())
        _total = sum(wallets.values())
        _mean = _total / _len

        return _len, _min, _max, _mean, _total
