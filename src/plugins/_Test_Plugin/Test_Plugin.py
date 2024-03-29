from plugins.Plugin_Prototype import Plugin_Prototype

class Test_Plugin(Plugin_Prototype):

    def __init__(self, client = None):
        self.module_name = "Test_Plugin"
        self.module_version = "1.0"
        self.client = client
        self.register_actions()
        self.store = {}

    def set_client (self, client):
        self.client = client

    def put(self, key = "key", item = ""):
        print(f"put: {key} -> {item}")
        self.store[key] = item

    def get(self, key):
        if key in self.store:
            return self.store[key]

    async def _hook_put_var(self, user, message):
        try:
            (key, value) = message.split(",", 1)
            self.put(key, value.strip())
        except:
            print ("ERROR!")

    async def _hook_get_var (self, user, key):
        value = self.get(key)
        await self.client.send_private_message(value, user)

    async def _hook_reply_message(self, user = None, message = ""):
        print(f"ACTION: {message}\n\n")
        print("AAAAAAA")
        print("AAAAAAA")
        print("AAAAAAA")
        print("AAAAAAA")
        if user:
            await self.client.send_private_message(message, user)    
    
    def register_actions(self):
        if self.client:
            self.client.private_msg_handler.add_action("!test_function <message>", self._hook_reply_message, "EXAMPLE reply", "admin", f"{self.module_name} (Admin)")
            self.client.private_msg_handler.add_action("!test_put <key,value>",      self._hook_put_var, "EXAMPLE put", "admin", f"{self.module_name} (Admin)")
            self.client.private_msg_handler.add_action("!test_get <key>",      self._hook_get_var, "EXAMPLE get", "admin", f"{self.module_name} (Admin)")
    
    
        