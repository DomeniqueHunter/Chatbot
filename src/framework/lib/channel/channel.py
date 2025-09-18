from framework.lib.list import AdvList

import json


class Channel(object):

    def __init__(self, name, code, description=''):
        self.name = name
        self.code = code
        self.description = description
        self.characters = AdvList()
        self.admins = AdvList()
        self.persistent = True

    def change_name(self, name):
        self.name = name

    def change_desciption(self, description):
        self.description = description

    def json(self):
        data = {
                "name": self.name,
                "code": self.code,
                "description": self.description,
            }
        return data

    def toJSON(self):
        return  json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)
    
    def bbcode(self):
        return f"[session={self.name}]{self.code}[/session]"

    def add_character(self, name):
        if name.lower() not in self.characters.get():
            self.characters.append(name.lower())
        else:
            print("CHARACTER ALREADY IN CHANNEL")

    def add_admin(self, user:str):
        self.admins.append(user)

    def remove_character(self, name) -> bool:
        if name.lower() in self.characters.get():
            self.characters.drop(name.lower())

        if not self.persistent and len(self.characters) == 1:
            # just me left, it's time to leave
            return True

        return False

    def is_online(self, name):
        return self.characters.contains(name.lower())

    def is_admin(self, user:str) -> bool:
        return self.admins.contains(user)

    def __eq__(self, other):
        return other.lower() == self.code.lower()

    def __str__(self):
        return self.code
    
    def __repr__(self):
        return self.name

    @staticmethod
    def find_channel_by_name(dict_of_channels=None, channel_name=None):
        if type(dict_of_channels) == type ({}) and channel_name:
            for key in dict_of_channels:
                if dict_of_channels[key].name == channel_name:
                    return dict_of_channels[key].code

            return False

        else:
            return False

