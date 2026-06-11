import uuid
from typing import Union
from framework.lib.filemanager import FileManager


class UserWalletDB:

    def __init__(self, file_manager:FileManager):
        self.file_manager = file_manager
        self.users_file = self.file_manager.add("bc_users", "bc_users.json", "json")
        self.wallets_file = self.file_manager.add("bc_wallets", "bc_wallets.json", "json")

        self.users = {}
        self.wallets = {}

        self.users_changed = False
        self.wallets_changed = False

        self.load_all()

    def add_user(self, user:str) -> bool:
        if user not in self.users:
            wallet_id = str(uuid.uuid4())
            self.users[user] = wallet_id
            self.wallets[wallet_id] = 0
            self.users_changed = True
            self.wallets_changed = True
            return True
        
        return False

    def get_wallet_id(self, user:str, create_if_not_exists:bool=False):
        wallet_id = self.users.get(user, None)
        if wallet_id == None and create_if_not_exists:
            self.add_user(user)
            wallet_id = self.users[user]
        return wallet_id

    def get_wallet(self, user:str) -> Union[float, int]:
        wallet_id = self.get_wallet_id(user)
        if not wallet_id: return None
        return self.get_wallet_by_id(wallet_id)

    def get_wallet_by_id(self, wallet_id:str) -> Union[float, int]:
        return self.wallets.get(wallet_id, 0)

    def __is_positive(self, number:Union[float, int]):
        return number > 0

    def is_user(self, user:str) -> bool:
        return user in self.users

    def add_amount(self, user:str, number:Union[float, int], create_if_not_exists=True) -> bool:
        wallet_id = self.get_wallet_id(user, create_if_not_exists=create_if_not_exists)
        if wallet_id and self.__is_positive(number):
            self.wallets[wallet_id] += number
            self.wallets_changed = True
            return True
        return False

    def remove_amount(self, user:str, number:Union[float, int]) -> bool:
        wallet_id = self.get_wallet_id(user)
        if wallet_id and self.wallets[wallet_id] >= number and self.__is_positive(number):
            self.wallets[wallet_id] -= number
            self.wallets_changed = True
            return True
        return False

    def check_amount(self, user:str, number:Union[float, int]) -> bool:
        return self.get_wallet(user) >= number

    def transfer_amount(self, from_user:str, to_user:str, number:Union[float, int]) -> bool:
        if not self.is_user(from_user) and not self.is_user(to_user) and self.check_amount(from_user, number):
            return False

        print(f"move {number} from {from_user} to {to_user}")
        if self.remove_amount(from_user, number):
            self.add_amount(to_user, number)

        return False

    def debug_show_wallets(self):
        for user_name, wallet_id in self.users.items():
            wallet = self.wallets.get(wallet_id, -1)
            print(f"{user_name} {wallet_id} {wallet}")

    def debug_show_changes(self):
        print(self.users_changed, self.wallets_changed)

    def load_all(self):
        # only done on start - I hope :D
        self.users = self.file_manager.load(self.users_file.handle) or {}
        self.wallets = self.file_manager.load(self.wallets_file.handle) or {}

    def save_users(self):
        if self.users_changed:
            self.file_manager.save(self.users_file.handle, self.users)
            self.users_changed = False

    def save_wallets(self):
        if self.wallets_changed:
            self.file_manager.save(self.wallets_file.handle, self.wallets)
            self.wallets_changed = False

    def save_all(self):
        self.save_users()
        self.save_wallets()


def test():
    fmg = FileManager(".")
    uwdb = UserWalletDB(fmg)

    uwdb.add_amount("test1", 1000)
    uwdb.add_amount("test2", 500)

    uwdb.add_amount("test1", 1000)

    uwdb.transfer_amount("test1", "test2", 5000)
    uwdb.transfer_amount("test1", "test2", 100)
    uwdb.transfer_amount("test1", "test3", 100)

    uwdb.debug_show_wallets()
    uwdb.debug_show_changes()

    # basic tests
    print("\n###")
    print(uwdb.get_wallet("test1"))
    print(uwdb.check_amount("test1", 1000))
    print(uwdb.check_amount("test1", 10000))

    # uwdb.save_all()


if __name__ == "__main__":
    test()

