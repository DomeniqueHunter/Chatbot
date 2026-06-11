
from framework.lib.argument.parser import parse


class BotCoinHooks():

    def __init__(self, module):
        self.bot_coin:"BotCoins" = module

    async def admin_add_coins(self, user:str, input_str:str=" , "):
        for_user, amount = parse(input_str, str, int)

        if self.bot_coin.bot.is_owner(user) and for_user and amount != 0:
            if amount > 0:
                self.bot_coin.add_coins(for_user, amount)
            else:
                self.bot_coin.remove_coins(for_user, amount)
            response = f"You ceated in {amount} for user {for_user}"
            await self.bot_coin.bot.send_private_message(response, user)

    async def give_coins_to(self, user:str, input_str:str=" , "):
        to_user, amount = parse(input_str, str, int)
        if self.bot_coin.has_wallet(user) and self.bot_coin.has_wallet(to_user):
            self.bot_coin.give_coins_to(user, to_user, amount)
            print(f"{user} > {to_user} : {amount}")
            response = f"Send {amount} to {user}"
            await self.bot_coin.bot.send_private_message(response, user)

        elif not self.bot_coin.has_wallet(user):
            await self.bot_coin.bot.send_private_message("you have no wallet", user)

        elif not self.bot_coin.has_wallet(to_user):
            await self.bot_coin.bot.send_private_message(f"{to_user} has no wallet", user)

    async def show_wallet(self, user:str):
        wallet_id, wallet = self.bot_coin.get_wallet(user)
        if wallet_id and wallet:
            response = f"Your Wallet is {user} ({wallet_id}): {wallet}"
            await self.bot_coin.bot.send_private_message(response, user)
        else:
            await self.bot_coin.bot.send_private_message("you have no wallet", user)

    async def create_wallet(self, user:str):
        pass

