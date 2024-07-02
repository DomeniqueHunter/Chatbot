from core.Core      import Core
from core           import Opcodes as opcode

from lib.Channel.Channel import Channel
from lib.Reaction.Reaction  import Reaction
from lib.CommandManager.CommandManager import CommandManager

from time          import sleep, time


class ChatCodeHandler(Core):
    """
        Handler
    """

    def __init__(self, config, root_path):
        Core.__init__(self, config, root_path)

        # 4 the future
        self.core = None
        self.op_code_handler = None

        self.charactername = config.character
        self.owner = config.owner
        self.status = ""

        self.stop_impulse = False

        # Register Message Actions
        self.private_msg_handler = CommandManager(self.manpage)
        #  add_action(self, handler, function, man_text="", role="owner", section="Bot (Admin)")
        self.private_msg_handler.add_action("EXCEPTION"     , self._hook_exception_handler, no_help=True)
        self.private_msg_handler.add_action("!join <channel>", self._hook_join_by_name, "Bot joins channel", "admin", "Bot (Admin)")
        self.private_msg_handler.add_action("!leave <channel>", self._hook_leave, "Bot leaves channel", "admin", "Bot (Admin)")
        self.private_msg_handler.add_action("!add_admin <name>" , self._hook_add_admin, "add a User to admins", "admin", "Bot (Admin)")
        self.private_msg_handler.add_action("!remove_admin <name>", self._hook_remove_admin, "remove User from admins", "admin", "Bot (Admin)")
        self.private_msg_handler.add_action("!admins"       , self._hook_admins, "returns a list of admins", "user", "Bot")
        self.private_msg_handler.add_action("!channels"     , self._hook_channels, "returns a list of channels", "user", "Bot")
        self.private_msg_handler.add_action("!create_channel <channelname>", self._hook_create_private_channel, "creates a channel", "admin", "Bot (Admin)")

        self.private_msg_handler.add_action("!status <text>", self._hook_set_status, "Set Bots Status to text", "admin", "Bot (Admin)")

        self.private_msg_handler.add_action("!save"         , self._hook_save_all, "Save Bot Status", "owner", "Bot (Admin)")
        self.private_msg_handler.add_action("!load"         , self._hook_load_all, "Load Bot Status", "owner", "Bot (Admin)")

        self.private_msg_handler.add_action("!invite <channel>, <user>", self._hook_invite_to_channel, "invite user to channel", "admin", "Bot (Admin)")
        self.private_msg_handler.add_action("!kick <channel>, <user>", self._hook_kick, "kicks", "admin", "Bot (Admin)")
        self.private_msg_handler.add_action("!help"         , self._hook_help_page, "Show help Page", "user", "Bot")

        self.private_msg_handler.add_action("!allusers"     , self._hook_list_all_users, "Lists all users", "owner", "Bot (Admin)")

        self.private_msg_handler.add_action("!DIE"          , self._hook_die, "Kills the bot", "owner", "Bot (Admin)")

        self.private_msg_handler.add_action("!ch_info <channel>", self._hook_get_users_in_channel, "returns info of channel", "admin", "Bot (Admin)")
        self.private_msg_handler.add_action("!debug_ors"    , self._order_list_of_open_private_channels, "DEBUG List of open Channels", "owner", "Bot (Admin)")
        self.private_msg_handler.add_action("!debug_cha"    , self._order_list_of_official_channels, "DEBUG List of official Channels", "owner", "Bot (Admin)")
        self.private_msg_handler.add_action("!debug_channels", self._debug_channels, "Debug Channels", "admin", "Bot (Admin)")
        self.private_msg_handler.add_action("!__"           , self._hook_sysinfo, "system information", "owner", "Bot (Admin)")

        # TODO:
        # openroom room
        # closeroom room
        # deop channel, user
        # set_description room, desc

    async def _ping(self):
        # print("ping back")
        self.ping_time = int(time())
        await self._message(opcode.PING)

    # TODO: sleep decorator, put sleep in _message
    async def send_private_message(self, message, user):
        data = {"character": self.charactername,
                "message": message,
                "recipient": user}
        sleep(1)
        await self._message(opcode.PRIVATE_MESSAGE, data)

    async def send_public_message(self, message, channel):
        data = {"channel": channel,
                "message": message}
        sleep(1)
        await self._message(opcode.CHANNEL_MESSAGE, data)

    async def _get_channel_description(self, data):
        channel = data['channel']
        description = data['description']

        if channel in self.channels:
            self.channels[channel].change_desciption(description)

    async def _save_all_settings(self, user=None):
        await self._hook_save_admins(user)
        await self._hook_save_channels(user)
        await self._hook_save_status(user)
        await self._hook_save_all_users(user)

        self.trigger_plugins_save()

    async def _load_all_settings(self, user=None):
        await self._hook_load_admins(user)
        await self._hook_load_channels(user)
        await self._hook_load_status(user)
        await self._hook_load_all_users(user)

        self.trigger_plugins_load()

    '''
        HOOKS
    '''

    async def _hook_save_all(self, user=None):
        if (user == self.owner):
            print ("save settings")
            await self._save_all_settings(user)
            # await self.send_private_message("settings saved!", user)

    async def _hook_load_all(self, user=None):
        if (user == self.owner):
            await self._load_all_settings(user)

    async def _hook_exception_handler(self, handler, *args):
        print("HOOK EXCEPTION")
        print("handler:", handler, "\nargs:", *args)
        # await self.send_private_message("don't understand: "+handler)

    async def _hook_permission_denied(self, user):
        await self.send_private_message("Permission denied!")

    async def _hook_join_old(self, user=None, channel=None):
        if (channel and self.has_admin_rights(user)):
            await self.join(channel, channel)
            await self.send_private_message("joined: " + channel, user)

    async def _hook_join_channel(self, user:str=None, channel:str=None):
        if self.has_admin_rights(user):
            if channel.find("c:") or channel.find("C:"):
                # join by channel code
                code = channel.split(":")[1]
                channel_name = await self.channel_manager.join_by_id(code)
            else:
                # join by channel name
                channel_name = await self.channel_manager.join(channel)

            await self.send_private_message(f"joined: {channel_name}", user)
        else:
            await self.send_private_message(f"didn't find the channel {channel}", user)

    async def _hook_join_by_name(self, user=None, channel=None):
        if self.has_admin_rights(user):
            channel_name = await self.channel_manager.join(channel)
            await self.send_private_message(f"joined: {channel_name}", user)
        else:
            await self.send_private_message(f"didn't find the channel {channel}", user)

    async def _hook_join_by_id(self, user=None, channel=None):
        if self.has_admin_rights(user) and channel:
            if not channel in self.channels:
                await self.join(channel, channel)

    async def _hook_leave(self, user=None, channel_to_leave=None):
        if (channel_to_leave and self.has_admin_rights(user)):
            for _, channel in self.channels.items():
                if channel_to_leave.lower() == channel.name.lower():
                    await self._leave(channel.code)
                    await self.send_private_message("left: " + channel_to_leave, user)
                    self.remove_channel_from_list_by_name(channel_to_leave)
                    break  # stop after finding the first one
            else:
                await self.send_private_message(f"channel {channel_to_leave} not found", user)

    # ADMIN HANDLING
    async def _hook_add_admin(self, user=None, new_admin=None):
        if (self.has_admin_rights(user)):
            self._add_bot_admin(new_admin.lower())
            await self.send_private_message(new_admin + " can now use this bot!", user)
            await self.send_private_message("you can use this bot now!", new_admin)

    async def _hook_remove_admin(self, user=None, admin=None):
        if (self.has_admin_rights(user)):
            self.admins.remove(admin.lower())
            await self.send_private_message(admin + " is no longer admin", user)

    async def _hook_save_admins(self, user=None):
        if (self.is_owner(user)):
            if len(self.admins) > 0:
                self.file_manager.save('admins', self.admins)

    async def _hook_load_admins(self, user=None):
        if (self.is_owner(user)):
            try:
                self.admins = self.file_manager.load('admins') or []
                await self.send_private_message("loaded admins", user)
            except:
                pass

    async def _hook_admins(self, user=None, message=None):
        string = "\nOwner: [user]" + self.owner + "[/user]\n"
        string += "Admins:\n"
        for admin in self.admins:
            string += "[user]" + admin + "[/user]\n"
        await self.send_private_message(string, user)

    # CHANNEL HANDLING

    async def _hook_create_private_channel(self, user=None, channel_name:str=""):
        if self.has_admin_rights(user):
            await self.create_private_channel(channel_name)
            self.channel_creation_queue.add(channel_name, user)
            await self.send_private_message(f"created channel: {channel_name}", user)

    async def _hook_channels(self, user=None, message=None):
        message = "\nChannel: Code\n"
        for channel in self.channels.values():
            message += f"[session={channel.name}]{channel.code}[/session]: {channel.code} - {channel.persistent}\n"

        await self.send_private_message(message, user)

    async def _debug_channels(self, user=None):
        message = "\nChannel: Code\n"
        for channel in self.channels:
            message += "[session=" + self.channels[channel].name + "]" + self.channels[channel].code + "[/session]: " + self.channels[channel].code + "\n"

        message += "\nNew Style:\n"
        for channel in self.channel_manager.joined_channels.values():
            message += f"[session={channel.name}]{channel.code}[/session]: {channel.code}\n"

        await self.send_private_message(message, user)

    async def _debug_users(self, user=None, channel_code=None):
        if self.is_owner(user):
            message = "\nUsers in Channel:\n"
            for name in self.channel_manager.joined_channels[channel_code].characters:
                message += f" - {name}"
                print(self.channel_manager.joined_channels[channel_code].characters)
                print(name)

            await self.send_public_message(message, channel_code)

    async def _hook_get_users_in_channel(self, user=None, channel=None):
        code = Channel.find_channel_by_name(self.channels, channel)
        if ((code in self.channels) and (self.has_admin_rights(user))):
            message = f'Info for Channel [b]{self.channels[code].name}[/b] ({self.channels[code].characters.size()})\n'
            for char in self.channels[code].characters.get():
                message += f"[user]{char}[/user]\n"

            await self.send_private_message(message, user)

    async def _hook_channel_name(self, user=None, message=None):
        data = message.split(" ", 1)

        if len(data) >= 2 and user == self.owner or (user.lower() in self.admins):
            self._rename_channel(data[0], data[1])
            _message = "changed name of channel " + data[0] + " to " + data[1]
            await self.send_private_message(_message, user)

    async def _hook_save_channels(self, user=None):
        if self.is_owner(user):
            if any(self.channels):
                self._save_channels_to_file('channels.json')
                # self.file_manager.save('channels', self.channel)
            else:
                await self.send_private_message("Error on saving Channels", user)
        else:
            await self.send_private_message("Permission denied!", user)

    async def _hook_load_channels(self, user=None):
        if self.is_owner(user):
            try:
                await self._load_channels_from_file('channels.json') or {}
            except:
                await self.send_private_message("can not open channels file", user)

    async def _hook_save_all_users(self, user=None):
        if self.is_owner(user):
            if self.all_users:
                self.file_manager.save('all_users', self.all_users)
            else:
                await self.send_private_message("Error on saving all Users", user)
        else:
            await self.send_private_message("Permission denied!", user)

    async def _hook_load_all_users(self, user=None):
        if self.is_owner(user):
            all_users = self.file_manager.load('all_users') or {}
            if all_users:
                self.all_users = all_users
                await self.send_private_message("loaded all users", user)

    async def _hook_list_all_users(self, user_in=None, page=1):
        if self.is_owner(user_in):

            try:
                page = int(page)
            except:
                # force it!
                page = 1

            entries_per_page = 10
            pages = int (len(self.all_users) / entries_per_page) + 1  # number of pages
            counter = 0
            page -= 1

            start_at = page * entries_per_page

            msg = f"\n[ {page+1} / {pages} ]:\n"
            for user in self.all_users:
                if (counter >= start_at and counter <= start_at + entries_per_page - 1) or page == -1:
                    msg += f"[user]{self.all_users[user]['identity']}[/user] : {self.all_users[user]['gender']}\n"

                counter += 1

            await self.send_private_message(msg, user_in)

    async def _hook_die(self, user=None):
        if self.is_owner(user):
            await self._save_all_settings(user)
            await self.send_private_message("I'm out, Bye!", user)
            self.stop_impulse = True
            exit()

    def _hook_start_loggin(self, user=None, channel=None):
        # log channel to file -> logs/channelname
        pass

    # STATUS HANDLING

    async def _hook_set_status(self, user=None, status=None):
        if self.has_admin_rights(user):
            if status:
                self.status = status
                await self._set_status(status)
                await self._hook_save_status(user)
            else:
                await self.send_private_message("No status given...", user)
        else:
            self._hook_permission_denied(user)

    async def _hook_save_status(self, user=None):
        if (user == self.owner and self.status):
            self.file_manager.save('status', self.status)

    async def _hook_load_status(self, user=None):
        if (user == self.owner):
            try:
                self.status = self.file_manager.load('status')
                await self._set_status(self.status)
            except:
                pass

    async def _hook_invite_to_channel(self, user, data=None):
        # data example
        # CHANNELNAME USER NAME
        try:
            (channel, other_user) = data.split(',', 1)

            print (f"invite USER {other_user.strip()} to {channel.strip()}")

            if (self.has_admin_rights(user) and other_user):
                await self._invite_user_to_channel(other_user.strip(), channel.strip())
        except:
            print("ERROR: probably missing ,")

    async def _hook_kick(self, user, message):
        message = message.split(" ", 1)
        channel = message[0]
        other_user = message[1]
        if (self.has_admin_rights(user) and other_user):
            print ('other user: ', other_user, ' channel: ', channel)

            data = {'channel':channel,
                    'character':other_user}

            await self._message(opcode.KICK, data)
        pass

    async def _hook_op_user(self, user, other_user):
        if (self.is_owner(user) and other_user):
            data = {}
            await self._message(opcode.PROMOTE_OP, data)
        pass

    async def _hook_help_page(self, user):
        help_string = "\nHELP PAGE:\n"
        help_string += "SYNOPSIS: DESCRIPTION\n"

        help_string += self.manpage.show(user)

        await self.send_private_message(help_string, user)

    async def _hook_sysinfo(self, user):
        if self.is_owner(user):
            await self.send_private_message(self._sysinfo(), user)
