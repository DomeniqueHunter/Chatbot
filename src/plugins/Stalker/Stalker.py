from plugins.Plugin_Prototype import Plugin_Prototype
from core                     import Opcodes as opcode

from lib.Channel.Channel import Channel

import json

class Stalker(Plugin_Prototype):

    def __init__(self, client = None):
        self.module_name = "Stalker"
        self.module_version = "0.0.1"
        self.client = client
        self.all_clients = {}
    
    def _add_client_to_list(self, channel = None, client = None):
        if channel and client:
            if not channel in self.all_clients:
                self.all_clients[channel] = []
            
            if not client in self.all_clients[channel]:
                self.all_clients[channel].append(client)    
    
    async def _opcode_handler_user_joined_channel(self, json_object):
        data = json.loads(json_object)
        channel = data['channel']
        client  = data['character']['identity']
        self._add_client_to_list(channel, client)
        
    async def _get_full_client_list(self, user, channel = None):
        if self.client.is_owner(user) and channel:
            channel = Channel.find_channel_by_name(self.client.channels, channel)
            message = "\nAll Clients\n"
            for char in self.all_clients[channel]:
                message+= f"[user]{char}[/user]\n"
    
            await self.client.send_private_message(message, user)
            
    def register_actions(self):
        if self.client:
            self.client.opcodes_handler.add_action(opcode.JOIN_CHANNEL , self._opcode_handler_user_joined_channel)
            self.client.private_msg_handler.add_action("!stalker_list <channel>", self._get_full_client_list, "returns a list of all clients which where in the channel", "owner", f"{self.module_name} (Admin)")
 