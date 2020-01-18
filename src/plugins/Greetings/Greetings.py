from plugins.Plugin_Prototype import Plugin_Prototype
from core import Opcodes as opcode

import json

class Greetings(Plugin_Prototype):

    def __init__(self):
        self.module_name    = "Greetings List"
        self.module_version = "2.0"
        self.greetings_list = {}

    def set_client(self, client):
        self.client = client
        
    def setup(self):
        self._info()
        self.client.files.add("greetings", "greetings.dat")

    def _register_greeting(self, user, title = None):
        if (title):
            greeting = '{} {}'.format(title,user).strip()
        else:
            greeting = '{}'.format(user).strip()
        self.greetings_list[user] = title
        return greeting

    def _unsubscribe_greeting(self, user):
        if (user in self.greetings_list):
            self.greetings_list.pop(user)
            return True
        return False

    def save(self):
        if len(self.greetings_list) > 0:
            self.client.save_to_file(str(self.greetings_list), self.client.files.greetings, 'w')

    def load(self):
        try:
            data = self.client.load_from_file(self.client.files.greetings)
            self.greetings_list = eval(data)
            print(self.greetings_list)
        except:
            print ("could not load data in '{}'".format(self.module_name))

    async def _opcode_user_connected(self, json_object):
        data = json.loads(json_object)
        user = data['identity']
        if (user in self.greetings_list):
            if (self.greetings_list[user]):
                message = "Hello {} {}!".format(self.greetings_list[user],user)
            else:
                message = "Hello {}!".format(user)

            await self.client.send_private_message(message, user)

    async def get_greetings_list(self, user):
        if (self.client.is_owner(user)):
            greetings = "Greetings List:\n"
            for g_user in self.greetings_list:
                if (self.greetings_list[g_user]):
                    greetings += "- {} as {}\n".format(g_user,self.greetings_list[g_user])
                else:
                    greetings += "- {}\n".format(g_user)

            await self.client.send_private_message(greetings, user)
        else:
            await self.client.send_private_message("fuck you", user)

    async def register_greeting(self, user, title = None):
        greeting = self._register_greeting(user, title)
        await self.client.send_private_message("I will greet you as {}".format(greeting), user)

    async def unsubscribe_greeting(self, user):
        # pop from list
        if self._unsubscribe_greeting(user):
            await self.client.send_private_message("I will no longer greet you", user)
            
    def register_actions(self):
        if self.client:
            print ("register actions")
            self.client.opcodes_handler.add_action('NLN', self._opcode_user_connected)
            self.client.private_msg_handler.add_action("!greetings",   self.get_greetings_list)
            self.client.private_msg_handler.add_action("!greetme",     self.register_greeting)
            self.client.private_msg_handler.add_action("!dontgreetme", self.unsubscribe_greeting)


