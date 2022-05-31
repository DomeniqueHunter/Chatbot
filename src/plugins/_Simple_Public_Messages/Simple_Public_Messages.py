from plugins.Plugin_Prototype import Plugin_Prototype
from core.Api import Api

class Simple_Public_Messages(Plugin_Prototype):
    def __init__(self):
        self.module_name = "SPM"
        self.module_version = "1.0"

    def register_actions(self):
        if self.client:
            self.client.public_msg_handler.add_action("!hello", self.answer_hello)
            self.client.public_msg_handler.add_action("!debug_charinfo", self.info)

    async def answer_hello (self, user, channel, message = ""):
        print (f"User '{user}' wrote in '{channel}' the message '{message}")
        await self.client.send_public_message("Hello {user}!",channel)

    #async def info (self):
    #    Api.get_gender_of_character(Api.get_ticket(self.client.account, self.client.password), self.client.account, 'katharina_')