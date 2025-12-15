from framework.chat_code_handler import ChatCodeHandler
from framework.lib.command_manager import CommandManager
from framework.lib.reaction import Multi_Reaction as Reactions
from framework import opcode

from framework.lib.counter import Counter

import json, asyncio, time
from framework.lib.channel import Channel
from framework.lib.config.config import Config


class OpCodeHandler(ChatCodeHandler):
    """
        Control
    """

    def __init__(self, config:Config, root_path:str) -> None:
        ChatCodeHandler.__init__(self, config, root_path)

        # for the future
        self.core = None
        self.chat_code_handle = None

        self.loop = asyncio.get_event_loop()
        self.counter_load_channels = Counter(10)
        self.counter_save_all = Counter (60)

        # Register Opcode Actions
        self.opcodes_handler = Reactions()
        self.opcodes_handler.add_action("EXCEPTION"               , self._opcode_handler_except)
        self.opcodes_handler.add_action(opcode.PING               , self._opcode_handler_ping)
        self.opcodes_handler.add_action(opcode.PRIVATE_MESSAGE    , self._opcode_handler_private_message)
        self.opcodes_handler.add_action(opcode.CHANNEL_MESSAGE    , self._opcode_handler_channel_message)
        self.opcodes_handler.add_action(opcode.CHANNEL_DESCRIPTION, self._opcode_handler_channeldescription)
        self.opcodes_handler.add_action(opcode.INVITE             , self._opcode_handler_invite)
        self.opcodes_handler.add_action(opcode.KICK               , self._opcode_handler_kicked)
        # self.opcodes_handler.add_action(opcode.USER_CONNECTED     , self._opcode_user_connected)
        self.opcodes_handler.add_action(opcode.GONE_OFFLINE       , self._opcoce_user_disconnected)
        self.opcodes_handler.add_action(opcode.STATUS             , self._opcode_user_changed_status)
        self.opcodes_handler.add_action(opcode.JOIN_CHANNEL       , self._opcode_handler_user_joined_channel)
        self.opcodes_handler.add_action(opcode.LEAVE_CHANNEL      , self._opcode_hander_user_left_channel)

        self.opcodes_handler.add_action(opcode.INITIAL_CHANNEL_DATA, self._opcode_handler_inital_channel_data)
        self.opcodes_handler.add_action(opcode.LIST_PRIVATE_CHANNELS, self._opcode_handler_receive_list_of_open_public_channels)
        self.opcodes_handler.add_action(opcode.LIST_OFFICAL_CHANNELS, self._opcode_handler_receive_list_of_official_channels)

        self.public_msg_handler = CommandManager(self.manpage)
        self.public_msg_handler.add_action("EXCEPTION", self._opcode_handler_except, no_help=True)
        self.public_msg_handler.add_action("!help", self._hook_help_page, no_help=True)

        self.public_msg_handler.add_action("!debug_users", self._debug_users, "DEBUG show all users in channel", "owner", "Bot (Admin)")

        self.all_users = {}

    async def dispatcher(self, op:str, json_object:str="") -> None:
        await self.opcodes_handler.react(op, json_object)

    async def connect(self) -> None:
        await self.comm.start_sender()
        await self.comm.connect() # comm
        await self.comm.identify() # comm
        await self.comm.start_receiver()

    async def _restart(self) -> None:
        print("MSG: restart chatbot")
        await self.connect()
        await self.channel_manager.rejoin_channels()
        self.restarts += 1

    async def _prepare(self) -> None:
        await self._load_all_settings(self.owner)

        await self._order_list_of_open_private_channels()
        await self._order_list_of_official_channels()

        await self.join_default_channels(self.config.default_channels)

    def start(self) -> None:
        self.loop.run_until_complete(self.connect()) # comm
        self.loop.run_until_complete(self._prepare())
        self.loop.run_until_complete(self._run())

        self.loop.run_forever()
        
    def get_user_gender(self, user:str) -> str:
        return self.all_users[user.lower()]['gender']

    async def _run (self) -> None:
        while True:
            if self.comm.connection != None and self.comm.status() == "OPEN":
                # message = await self.comm.read() # comm
                op, msg = await self.comm.receive()
                await self.dispatcher(op, msg)

                if self.stop_impulse:
                    exit()

            else:
                print("!!!!!!!! RECONNECT !!!!!!!!")
                await self._save_all_settings(self.owner)
                time.sleep(30)
                await self._restart()
                await self._load_all_settings(self.owner)

    async def _opcode_handler_private_message(self, json_object:str) -> None:
        data = json.loads(json_object)
        user = data['character']
        message = data['message'].strip()

        message = message.split(' ', 1)
        handler = message.pop(0)

        await self.private_msg_handler.react(handler, user, *message)

    async def _opcode_handler_channel_message(self, json_object:str) -> None:
        '''
            Channel Message Dispatcher
        '''
        data = json.loads(json_object)
        channel = data ['channel']
        message = data ['message'].strip()
        user = data ['character']

        message = message.split(' ', 1)
        handler = message.pop(0)

        await self.public_msg_handler.react(handler, user, channel, *message)

    async def _opcode_handler_ping(self, empty:None=None) -> None:
        # print ("PING ... .. .. ...")
        await self.ping()
        await self.trigger_clock()

        if self.counter_load_channels.tick():
            await self._order_list_of_open_private_channels()
            await self._order_list_of_official_channels()

        if self.counter_save_all.tick():
            await self._hook_save_all(self.owner)

    async def _opcode_handler_channeldescription(self, json_object:str) -> None:
        data = json.loads(json_object)
        channel = data['channel']
        channel = channel[:3].upper() + channel[3:]
        data['channel'] = channel
        
        await self._get_channel_description(data)

    async def _opcode_handler_except(self, json_object:str) -> None:
        # silent
        pass

    async def _opcode_handler_invite(self, json_object:str) -> None:
        data = json.loads(json_object)
        user = data['sender']
        title = data['title']
        channel = data['name']

        if self.has_admin_rights(user):
            await self._hook_join_by_id(user, channel)
            await self._hook_channel_name(user, channel + " " + title)

    async def _opcode_handler_user_joined_channel(self, json_object:str) -> None:
        data = json.loads(json_object)
        code = data['channel']
        title = data['title']
        user = data['character']['identity']

        if code not in self.channels:
            channel = Channel(title, code)
            self.channels[code] = channel

            if self.channel_creation_queue.size() > 0:
                for index, channel_object in enumerate(self.channel_creation_queue.queue):
                    if channel_object["name"] == channel.name:
                        channel_object = self.channel_creation_queue.pop(index)

                        await self._invite_user_to_channel_by_code(channel_object["user"], code)
                        await self.channel_operator(channel_object["user"], code)

                        self.channels[code].add_admin(channel_object["user"])
                        self.channels[code].persistent = channel_object["persistent"]
        else:
            self.channels[code].add_character(user.lower())

    async def _opcode_hander_user_left_channel(self, json_object:str) -> None:
        data = json.loads(json_object)
        code = data['channel']
        user = data['character']

        try:
            leave = self.channels[code].remove_character(user.lower())
            if leave:
                await self._leave(code)
        except:
            print (f"channel {code} not found")

    async def _opcode_handler_kicked(self, json_object:str) -> None:
        data = json.loads(json_object)
        operator = data['operator']
        channel = data['channel']
        character = data['character']

        # print ("Operator %s kicked %s from %s" % (operator, character, channel))
        if (character.lower() == self.charactername.lower()):
            self.channels.pop(channel)

    async def _opcoce_user_disconnected(self, json_object:str) -> None:
        # removes User from channels, managed by bot, the user is in
        data = json.loads(json_object)
        for ch_key in self.channels:
            self.channels[ch_key].remove_character(data['character'].lower())

    async def _opcode_user_changed_status(self, json_object) -> None:
        pass

    async def _opcode_user_connected(self, json_object) -> None:
        data = json.loads(json_object)
        self.all_users[data['identity'].lower()] = data

    async def _opcode_handler_inital_channel_data(self, json_object:str) -> None:
        data = json.loads(json_object)
        # print (data)
        channel = data['channel']
        for user in data['users']:
            self.channels[channel].add_character(user['identity'].lower())

    async def _opcode_handler_receive_list_of_open_public_channels(self, json_object):
        self.channel_manager.add_open_private_channels(json_object)

    async def _opcode_handler_receive_list_of_official_channels(self, json_object):
        self.channel_manager.add_official_channels(json_object)

