import uuid
from typing import Union
from framework.lib.filemanager.filemanager import FileManager


class UserWalletDB:

    def __init__(self, file_manager:FileManager):
        self.file_manager = file_manager
        self.file_manager.add("cc_users", "cc_users.json", "json")
        self.file_manager.add("cc_wallets", "cc_wallets.json", "json")
        
        self.users = {}
        self.wallets = {}
        
        self.load_all()

    def add_user(self, user:str):
        if user not in self.users:
            wallet_id = str(uuid.uuid4())
            self.users[user] = wallet_id
            self.wallets[wallet_id] = 0

    def get_wallet(self, user:str, create_if_not_exists:bool=False):
        wallet_id = self.users.get(user, None)
        
        if wallet_id == None and create_if_not_exists:
            self.add_user(user)
            wallet_id = self.users[user]

        return wallet_id

    def __is_positive(self, number:Union[float, int]):
        return number > 0

    def add_amount(self, user:str, number:Union[float, int]):
        wallet_id = self.get_wallet(user, create_if_not_exists=True)
        
        if wallet_id and self.__is_positive(number):
            self.wallets[wallet_id] += number

    def remove_amount(self, user:str, number:Union[float, int]):
        wallet_id = self.get_wallet(user)
        if wallet_id and self.wallets[wallet_id] >= number and self.__is_positive(number):
            self.wallets[wallet_id] -= number

    def debug_show_wallets(self):
        for user_name, wallet_id in self.users.items():
            wallet = self.wallets.get(wallet_id, -1)
            print(f"{user_name} {wallet_id} {wallet}")
            
    def load_all(self):
        self.users = self.file_manager.load("cc_users") or {}
        self.wallets = self.file_manager.load("cc_wallets") or {}
        
    def save_all(self):
        self.file_manager.save("cc_users", self.users)
        self.file_manager.save("cc_wallets", self.wallets)


def test():
    fmg = FileManager(".")
    uwdb = UserWalletDB(fmg)
    
    uwdb.add_amount("test1", 1000)
    uwdb.add_amount("test2",  500)
    
    uwdb.add_amount("test1", 1000)

    uwdb.debug_show_wallets()
    uwdb.save_all()


if __name__ == "__main__":
    test()

