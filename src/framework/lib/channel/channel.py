from framework.lib.list import AdvList

import json


class Character:
    
    def __init__(self, name:str):
        self.name = name
        
    def __str__(self):
        return self.name
    
    def __eq__(self, other):
        if isinstance(other, str): 
            return other.lower() == self.name.lower()
        elif isinstance(other, Character):
            return other.name == self.name
        else:
            return False
        
    def __repr__(self):
        return self.name.lower()
    
    def __hash__(self):
        return hash(self.name)


class Channel(object):

    def __init__(self, name:str, code:str, description='') -> None:
        self.name = name
        self.code = code
        self.description = description
        self.characters = AdvList()
        self.admins = AdvList()
        self.persistent = True

    def change_name(self, name:str) -> None:
        self.name = name

    def change_desciption(self, description:str) -> None:
        self.description = description

    def json(self):
        data = {
                "name": self.name,
                "code": self.code,
                "description": self.description,
            }
        return data

    def toJSON(self) -> str:
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)
    
    def bbcode(self) -> str:
        return f"[session={self.name}]{self.code}[/session]"

    def add_character(self, name:str) -> None:
        if name.lower() not in self.characters.get():
            self.characters.append(Character(name))
        else:
            print("CHARACTER ALREADY IN CHANNEL")

    def add_admin(self, user:str) -> None:
        self.admins.append(Character(user))

    def remove_character(self, name:str) -> bool:
        if name.lower() in self.characters.get():
            self.characters.drop(name.lower())
            print(f"{name} left channel {self.name}")

        if not self.persistent and len(self.characters) == 1:
            # just me left, it's time to leave
            return True

        return False

    def is_online(self, name:str):
        return self.characters.contains(name.lower())

    def is_admin(self, user:str) -> bool:
        return self.admins.contains(user)

    def __eq__(self, other) -> bool:
        return other.lower() == self.code.lower()

    def __str__(self) -> str:
        return self.code
    
    def __repr__(self) -> str:
        return self.name

    @staticmethod
    def find_channel_by_name(dict_of_channels=None, channel_name=None) -> str | bool:
        if type(dict_of_channels) == type ({}) and channel_name:
            for key in dict_of_channels:
                if dict_of_channels[key].name == channel_name:
                    return dict_of_channels[key].code

            return False

        else:
            return False
        

def test():
    user1 = Character("User 1")
    user2 = Character("User 2")
    
    test_list = [user1, user2]
    for user in test_list:
        print(user)
        
    print("user 1" in test_list)
    
    test_list.extend(test_list)
    print(test_list)
    print(set(test_list))
    print(list(set(test_list)))
    


if __name__ == "__main__":
    test()

