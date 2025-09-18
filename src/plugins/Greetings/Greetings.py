from plugins.Plugin_Prototype import Plugin_Prototype
from framework import Opcodes as opcode

import json

class Greetings(Plugin_Prototype):

    def __init__(self):
        self.module_name    = "Greetings List"
        self.module_version = "2.0.1"
        self.greetings_list = {}

    def set_client(self, client):
        self.client = client
        
    def setup(self):
        self._info()
        self.client.file_manager.add("greetings", "greetings.json", 'json')

    def _register_greeting(self, user, title = None):
        if (title):
            greeting = f'{title} {user}'
        else:
            greeting = f'{user}'
        self.greetings_list[user] = title
        return greeting

    def _unsubscribe_greeting(self, user):
        if (user in self.greetings_list):
            self.greetings_list.pop(user)
            return True
        return False

    def save(self):
        if len(self.greetings_list) > 0:
            # self.client.save_json(self.greetings_list, self.client.files.greetings)
            self.client.file_manager.save('greetings', self.greetings_list)

    def load(self):
        try:
            self.greetings_list = self.client.file_manager.load('greetings') or {}
        except Exception as e:
            print(f"could not load data in '{self.module_name}'")
            print(e)
            
    def _get_pages(self, n=10):
        return (len(self.greetings_list) // n) +1

    async def _opcode_user_connected(self, json_object):
        data = json.loads(json_object)
        user = data['identity']
        if (user in self.greetings_list):
            if (self.greetings_list[user]):
                message = f"Hello {self.greetings_list[user]} {user}!"
            else:
                message = f"Hello {user}!"

            await self.client.send_private_message(message, user)

    async def get_greetings_list(self, user, page=1):
        if (self.client.is_priviliged(user)):
            if type(page) == str:
                try:
                    page = int(page)
                except ValueError:
                    page = 1
                    
            if page >= 1:
                page -= 1
            else:
                page = 0
                
            n = 10
            pages = self._get_pages(n)
            if page > pages:
                page = pages-1
                
            greetings = f"Greetings List: [{page+1}/{pages}]\n"
            
            
            keys = list(self.greetings_list.keys())
            values = list(self.greetings_list.values())
            
            start = page * n
            print(f"page: {page+1}")
            for k,v in zip(keys[start:start+n], values[start:start+n]):
                print(f"{k}: {v}")
                greetings += f"- {k} as {v}\n" if v else f" - {k}\n"

            await self.client.send_private_message(greetings, user)
        else:
            await self.client.send_private_message("fuck you", user)

    async def register_greeting(self, user, title = None):
        greeting = self._register_greeting(user, title)
        await self.client.send_private_message(f"I will greet you as {greeting}", user)

    async def unsubscribe_greeting(self, user):
        # pop from list
        if self._unsubscribe_greeting(user):
            await self.client.send_private_message("I will no longer greet you", user)
            
    async def rm_greeting(self, user, target):
        if self.client.is_priviliged(user):
            removed = self._unsubscribe_greeting(target)
            if removed:
                await self.client.send_private_message(f"removed [user]{target}[/user] from greetings list", user)
            else:
                await self.client.send_private_message(f"could not remove [user]{target}[/user] from greetings list", user)
                
            
    def register_actions(self):
        if self.client:
            print ("register actions")
            self.client.opcodes_handler.add_action('NLN', self._opcode_user_connected)
            self.client.private_msg_handler.add_action("!greetings",self.get_greetings_list, "Show Greetings List", "admin", f"{self.module_name} (Admin)")
            self.client.private_msg_handler.add_action("!rm_greeting <user>",self.rm_greeting, "remove user from Greetings List","admin", f"{self.module_name} (Admin)")
            self.client.private_msg_handler.add_action("!greetme <title:optional>",self.register_greeting, "bot will greet you, when you log in with the title","user",self.module_name)
            self.client.private_msg_handler.add_action("!dontgreetme",self.unsubscribe_greeting, "bot will no longer greet you","user", self.module_name)
            

