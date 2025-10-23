from plugins import PluginPrototype
import json
from framework.lib.argument import parse
from framework.lib.paginate import paginate


class Stalker(PluginPrototype):

    def __init__(self, client=None) -> None:
        self.module_name = "Stalker"
        self.module_version = "0.2.0"
        self.client = client
        self.all_clients = {}

    def _add_client_to_list(self, channel=None, client=None):
        if channel and client:
            if not channel in self.all_clients:
                self.all_clients[channel] = []

            if not client in self.all_clients[channel]:
                self.all_clients[channel].append(client)

    async def _opcode_handler_user_joined_channel(self, json_object) -> None:
        data = json.loads(json_object)
        channel = data['channel']
        client = data['character']['identity']
        self._add_client_to_list(channel, client)

    async def _get_full_client_list(self, user, input_string:str) -> None:
        if self.client.is_owner(user): 
            channel_name, page = parse(input_string, str, int)
            
            channel = self.client.channel_manager.find_channel(channel_name)
            
            # get total pages
            pages = paginate.get_pages(channel.characters.get(), 10)

            # parse page parameter
            page_nr = paginate.page_parameter(pages, page)
            
            # get message for page
            message = paginate.get_page(channel.characters.get(), page_nr, f"All Clients in {channel.name} ({channel.code}) [{page_nr+1}/{pages}]\n", 10)
            
            await self.client.send_private_message(message, user)

    async def get_joined_channels(self, user) -> None:
        if self.client.is_owner(user):
            channels = self.client.channels
            message = "\nChannels:\n"
            for _, chn in channels.items():
                message += f' - {chn.name} ({chn.code})\n'

            await self.client.send_private_message(message, user)

    def register_actions(self) -> None:
        if self.client:
            # self.client.opcodes_handler.add_action(opcode.JOIN_CHANNEL , self._opcode_handler_user_joined_channel)

            self.client.private_msg_handler.add_action("!stalker_chn", self.get_joined_channels, "show list of joined channels", "owner", f"{self.module_name} (Admin)")
            self.client.private_msg_handler.add_action("!stalker_list <channel>", self._get_full_client_list, "returns a list of all clients which where in the channel", "owner", f"{self.module_name} (Admin)")
