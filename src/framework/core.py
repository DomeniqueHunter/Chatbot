
from framework import opcode
from framework import PluginLoader

from framework.lib.config import Config
from framework.lib.manpage import Manpage
from framework.lib.filemanager import FileManager
from framework.lib.time import AdvTime

from framework.lib.channel import ChannelManager, ChannelCreationQueue

from time import sleep

import os
from framework.communicaton import Communication
from framework.lib.timeout.timeout import Timeout


class Core():
    """
        Connection
    """

    def __init__(self, config:Config, root_path:str="./") -> None:
        self.account = config.account
        self.password = config.password
        self.version = "0.9.8"

        self.channel_manager = ChannelManager(self.join)
        self.channels = self.channel_manager.joined_channels  # is this good?

        self.channel_creation_queue = ChannelCreationQueue()

        self.admins = []

        self.plugin_loader:PluginLoader = None
        self.restarts = 0
        self.start_time = AdvTime()

        self.manpage = Manpage(self)

        self.config = config
        self.root_path = root_path
        self.data_path = self.root_path + "/" + self.config.server + self.config.endpoint
        if not os.path.exists(self.data_path):
            os.makedirs(self.data_path, exist_ok=True)
        
        self.comm = Communication(self)
        self.timeouts = Timeout()

        self.file_manager = FileManager(self.data_path)
        self.file_manager.add('status', 'status.txt', 'plain')
        self.file_manager.add('admins', 'admins.json', 'json')
        self.file_manager.add('all_users', 'all_users.bin', 'binary')
        self.file_manager.add('channels', 'channels2.json', 'json')

    async def join(self, channel_code:str, channel_name:str="", force:bool=False) -> None:
        data = {'channel': channel_code}
        if channel_code not in self.channels and channel_code or (channel_code and force):
            await self.message(opcode.JOIN_CHANNEL, data)

    async def create_private_channel(self, channel_name:str) -> None:
        data = {"channel": channel_name}
        await self.message(opcode.CREATE_PRIVATE_CHANNEL, data)

    async def open_room(self, room:str) -> None:
        # channel_code = Channel.find_channel_by_name(self.channels, room)
        channel = self.channel_manager.find_channel(room)
        channel_code = channel.code
        
        data = {"channel": channel_code, "message": "/openroom"}
        await self.message(opcode.CHANNEL_MESSAGE, data)

    async def close_room(self, room:str) -> None:
        pass

    async def channel_operator(self, user:str, channel_code:str) -> None:
        data = {"character": user, "channel": channel_code}
        await self.message(opcode.PROMOTE_OP, data)

    async def set_channel_description(self, channel_name:str, description:str) -> None:
        channel = self.channel_manager.find_channel(channel_name)
        data = {"channel": channel.code, "description": description}
        await self.message(opcode.CHANNEL_DESCRIPTION, data)

    async def _join_by_name (self, channel_name=None) -> None:
        pass

    async def _leave(self, channel:str) -> None:
        data = {'channel': channel}
        await self.message(opcode.LEAVE_CHANNEL, data)
        self.channels.pop(channel)

    async def _order_list_of_official_channels(self) -> None:
        await self.message(opcode.LIST_OFFICAL_CHANNELS)

    async def _order_list_of_open_private_channels(self) -> None:
        await self.message(opcode.LIST_PRIVATE_CHANNELS)

    def remove_channel_from_list(self, code:str) -> None:
        self.channels.pop(code)

    def remove_channel_from_list_by_name(self, name:str) -> None:
        for channel in self.channels:
            if (name.lower() == self.channels[channel].name.lower()):
                self.remove_channel_from_list(self.channels[channel].code)
                break  # stop after finding the first one
            
    def remove_channel_from_list_by_code(self, code:str) -> None:
        for _, channel in self.channels.items():
            if (code.lower() == channel.code.lower()):
                self.remove_channel_from_list(channel.code)
                break  # stop after finding the first one

    def _rename_channel(self, channel:str, name:str) -> None:
        if channel in self.channels:
            self.channels[channel].change_name(name)
            print(str(self.channels))

    def _add_bot_admin(self, user:str) -> None:
        self.admins.append(user.lower())

    async def join_default_channels(self, channels:str) -> None:
        for channel in channels:
            await self.join(channel)

    async def message(self, opcode:str, data=None) -> None:
        await self.comm.message(opcode, data)

    def _set_save_path(self, path:str) -> None:
        self.save_path = path + "/"

    def _save_channels_to_file(self, file:str) -> None:
        self.file_manager.save('channels', self.channel_manager.get_channels_list())

    # deprecated!!!!
    async def _load_channels_from_file(self, file:str) -> None:
        channels = self.file_manager.load('channels')
        print(f'load Channels from file: {file}')
        for channel in channels:
            await self.channel_manager.join(channel['name'], channel['code'])
            
    async def _join_channels(self, channels:dict) -> None:
        print('load Channels:')
        for channel in channels.values():
            await self.channel_manager.join(channel['name'], channel['code'])

    async def _set_status(self, status:str) -> None:
        data = {"status":"online",
                "statusmsg":status}
        sleep(1)
        await self.message(opcode.STATUS, data)

    async def _invite_user_to_channel(self, user:str, channel_name:str) -> None:
        channel = self.channel_manager.find_channel(channel_name)
        channel_code = channel.code
        if channel_code:
            data = {"character": user, "channel": channel_code}
            await self.message(opcode.INVITE, data)

    async def _invite_user_to_channel_by_name(self, user:str, channel_name:str) -> None:
        await self._invite_user_to_channel(user, channel_name)

    async def _invite_user_to_channel_by_code(self, user:str, channel_code:str) -> None:
        data = {"character": user, "channel": channel_code}
        await self.message(opcode.INVITE, data)

    def is_admin(self, user:str) -> bool:
        return user.lower() in self.admins

    def is_owner(self, user:str) -> bool:
        return user.lower() == self.owner.lower()

    def has_owner_rights(self, user:str) -> bool:
        if self.is_owner(user):
            return True
        return False

    def has_admin_rights(self, user:str) -> bool:
        if self.has_owner_rights(user) or self.is_admin(user):
            return True
        return False

    def has_user_rights(self, user:str) -> bool:
        if user:
            return True
        return False

    def has_role(self, role:str, user:str) -> bool:
        if role == "owner":
            return self.has_owner_rights(user)

        elif role == "admin":
            return self.has_admin_rights(user)

        elif role == "user":
            return self.has_user_rights(user)

        else:
            return False
        
    def enable_plugin_loader(self, plugins_dir:str='plugins') -> None:
        """
            Enable the plugin loader
            Args:
                plugins_dir (str): Directory where plugins are located,
                relative to main.py
        """
        self.plugin_loader = PluginLoader(plugins_dir, self)

    def set_plugin_loader(self, loader:PluginLoader=None) -> None:
        # Deprecated function, can be removed later
        if loader:
            self.plugin_loader = loader
            self.plugin_loader.set_client(self)
        else:
            print ("no plugin loader!")
        print("Deprecated: use 'enable_plugin_loader' instead")

    def load_plugins(self) -> None:
        if self.plugin_loader:
            print ('Load Plugins:')
            self.plugin_loader.load_plugins()
        else:
            print ("no plugin loader")

    def trigger_plugins_load(self) -> None:
        for key in self.plugin_loader.plugins:
            print (f"autoload: {key}.load()")
            self.plugin_loader.plugins[key].load()

    def trigger_plugins_save(self) -> None:
        for key in self.plugin_loader.plugins:
            print (f"autosave: {key}.save()")
            self.plugin_loader.plugins[key].save()

    async def trigger_clock(self) -> None:
        for key in self.plugin_loader.plugins:
            try:
                await self.plugin_loader.plugins[key].clock()
            except:
                pass

    def _sysinfo(self) -> str:
        _now = AdvTime()
        sysinfo = "\n"
        sysinfo += f"Start Time {self.start_time.get_time_date()}\n"
        sysinfo += f"Local Time {_now.get_time_date()}\n"
        sysinfo += f"Version {self.version}\n"
        sysinfo += f"Restarts: {self.restarts}\n"
        sysinfo += f"Help calls: {self.manpage.counter()}\n"

        sysinfo += "Plugins:\n"
        for plugin in self.plugin_loader.plugins:
            sysinfo += f"-- {self.plugin_loader.plugins[plugin].module_name} ({self.plugin_loader.plugins[plugin].module_version})\n"

        return sysinfo

