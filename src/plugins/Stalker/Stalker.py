from plugins.Plugin_Prototype import Plugin_Prototype
from core import Opcodes as opcode

from core.lib.channel import Channel

import json


class Stalker(Plugin_Prototype):

    def __init__(self, client=None):
        self.module_name = "Stalker"
        self.module_version = "0.0.3"
        self.client = client
        self.all_clients = {}

    def _add_client_to_list(self, channel=None, client=None):
        if channel and client:
            if not channel in self.all_clients:
                self.all_clients[channel] = []

            if not client in self.all_clients[channel]:
                self.all_clients[channel].append(client)

    async def _opcode_handler_user_joined_channel(self, json_object):
        data = json.loads(json_object)
        channel = data['channel']
        client = data['character']['identity']
        self._add_client_to_list(channel, client)

    async def _get_full_client_list(self, user, channel=None):
        if self.client.is_owner(user) and channel:
            channel_code = Channel.find_channel_by_name(self.client.channels, channel)
            channel = self.client.channels[channel_code]

            message = "\nAll Clients\n"
            for char in channel.characters.get():
                message += f' - {char}\n'
            
            await self.client.send_private_message(message, user)

    async def get_joined_channels(self, user):
        if self.client.is_owner(user):
            channels = self.client.channels
            message = "\nChannels:\n"
            for _, chn in channels.items():
                message += f' - {chn.name} ({chn.code})\n'

            await self.client.send_private_message(message, user)

    def register_actions(self):
        if self.client:
            # self.client.opcodes_handler.add_action(opcode.JOIN_CHANNEL , self._opcode_handler_user_joined_channel)

            self.client.private_msg_handler.add_action("!stalker_chn", self.get_joined_channels, "show list of joined channels", "owner", f"{self.module_name} (Admin)")
            self.client.private_msg_handler.add_action("!stalker_list <channel>", self._get_full_client_list, "returns a list of all clients which where in the channel", "owner", f"{self.module_name} (Admin)")
