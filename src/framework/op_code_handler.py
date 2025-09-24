
from framework.lib.command_manager import CommandManager
from framework.lib.reaction import Multi_Reaction as Reactions
from framework import opcode

from framework.lib.counter import Counter

import json, asyncio, time
from framework.lib.channel import Channel


class OpCodeHandler():
    """
        Control
    """

    def __init__(self, bot):
        self.bot = bot

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

        self.public_msg_handler = CommandManager(self.bot.core.manpage)
        self.public_msg_handler.add_action("EXCEPTION", self._opcode_handler_except, no_help=True)
        self.public_msg_handler.add_action("!help", self.bot.chat_code_handler._hook_help_page, no_help=True)

        self.public_msg_handler.add_action("!debug_users", self.bot.chat_code_handler._debug_users, "DEBUG show all users in channel", "owner", "Bot (Admin)")

        self.all_users = {}

    async def dispatcher(self, op, json_object=None):
        if op:
            await self.opcodes_handler.react(op, json_object)

    async def _connect(self):
        await self.bot.core.connect(self.bot.config.server, self.bot.config.port)
        await self.bot.core.identify()

    async def _restart(self):
        print("MSG: restart chatbot")
        await self._connect()
        await self.bot.core.channel_manager.rejoin_channels()
        self.bot.core.restarts += 1

    async def _prepare(self):
        await self.bot.chat_code_handler._load_all_settings(self.bot.core.owner)

        await self.bot.core._order_list_of_open_private_channels()
        await self.bot.core._order_list_of_official_channels()

        await self.bot.core.join_default_channels(self.bot.config.default_channels)

    def start(self):
        self.loop.run_until_complete(self._connect())
        self.loop.run_until_complete(self._prepare())
        self.loop.run_until_complete(self._run())

        self.loop.run_forever()
        
    def get_user_gender(self, user:str) -> str:
        return self.all_users[user.lower()]['gender']

    async def _run (self):

        while True:
            if self.bot.core.connection != None and str(self.bot.core.connection.state.name) == "OPEN":
                message = await self.bot.core._read()
                if message:
                    print(message)
                    data = message.split(" ", 1)

                    await self.dispatcher(*data)

                if self.bot.chat_code_handler.stop_impulse:
                    exit()

            else:
                print("!!!!!!!! RECONNECT !!!!!!!!")
                await self.bot.chat_code_handler._save_all_settings(self.bot.core.owner)
                time.sleep(30)
                await self._restart()
                await self.bot.chat_code_handler._load_all_settings(self.bot.core.owner)

    async def _opcode_handler_private_message(self, json_object):
        data = json.loads(json_object)
        user = data['character']
        message = data['message'].strip()

        message = message.split(' ', 1)
        handler = message.pop(0)

        # print (f"user: {user}\nmessage: {message}")

        await self.bot.chat_code_handler.private_msg_handler.react(handler, user, *message)

    async def _opcode_handler_channel_message(self, json_object):
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

    async def _opcode_handler_ping(self, nothing=None):
        # print ("PING ... .. .. ...")
        await self._ping()
        await self.trigger_clock()

        if self.counter_load_channels.tick():
            await self.bot.core._order_list_of_open_private_channels()
            await self.bot.core._order_list_of_official_channels()

        if self.counter_save_all.tick():
            await self.bot.chat_code_handler._hook_save_all(self.owner)

    async def _opcode_handler_channeldescription(self, json_object):
        data = json.loads(json_object)
        channel = data['channel']
        channel = channel[:3].upper() + channel[3:]
        data['channel'] = channel
        
        await self.bot.chat_code_handler._get_channel_description(data)

    async def _opcode_handler_except(self, json_object):
        # silent
        pass

    async def _opcode_handler_invite(self, json_object):
        data = json.loads(json_object)
        user = data['sender']
        title = data['title']
        channel = data['name']

        if self.bot.core.has_admin_rights(user):
            await self.bot.chat_code_handler._hook_join_by_id(user, channel)
            await self.bot.chat_code_handler._hook_channel_name(user, channel + " " + title)

    async def _opcode_handler_user_joined_channel(self, json_object):
        data = json.loads(json_object)
        code = data['channel']
        title = data['title']
        user = data['character']['identity']

        if code not in self.channels:
            channel = Channel(title, code)
            self.channels[code] = channel

            if self.bot.core.channel_creation_queue.size() > 0:
                for index, channel_object in enumerate(self.bot.core.channel_creation_queue.queue):
                    if channel_object["name"] == channel.name:
                        channel_object = self.bot.core.channel_creation_queue.pop(index)

                        await self.bot.core._invite_user_to_channel_by_code(channel_object["user"], code)
                        await self.bot.core.channel_operator(channel_object["user"], code)

                        self.bot.core.channels[code].add_admin(channel_object["user"])
                        self.bot.core.channels[code].persistent = False

        self.bot.core.channels[code].add_character(user.lower())

    async def _opcode_hander_user_left_channel(self, json_object):
        data = json.loads(json_object)
        code = data['channel']
        user = data['character']

        try:
            leave = self.bot.core.channels[code].remove_character(user.lower())
            if leave:
                await self.bot.core._leave(code)
        except:
            print (f"channel {code} not found")

    async def _opcode_handler_kicked(self, json_object):
        data = json.loads(json_object)
        operator = data['operator']
        channel = data['channel']
        character = data['character']

        # print ("Operator %s kicked %s from %s" % (operator, character, channel))
        if (character.lower() == self.bot.chat_code_handler.charactername.lower()):
            self.bot.core.channels.pop(channel)

    async def _opcoce_user_disconnected(self, json_object):
        # removes User from channels, managed by bot, the user is in
        data = json.loads(json_object)
        for ch_key in self.bot.core.channels:
            self.bot.core.channels[ch_key].remove_character(data['character'].lower())

    async def _opcode_user_changed_status(self, json_object):
        pass

    async def _opcode_user_connected(self, json_object):
        data = json.loads(json_object)
        self.all_users[data['identity'].lower()] = data

    async def _opcode_handler_inital_channel_data(self, json_object):
        data = json.loads(json_object)
        # print (data)
        channel = data['channel']
        for user in data['users']:
            self.bot.core.channels[channel].add_character(user['identity'].lower())

    async def _opcode_handler_receive_list_of_open_public_channels(self, json_object):
        self.bot.core.channel_manager.add_open_private_channels(json_object)

    async def _opcode_handler_receive_list_of_official_channels(self, json_object):
        self.bot.core.channel_manager.add_official_channels(json_object)

