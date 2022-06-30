from core.Api       import Api as Api
from core           import Opcodes as opcode

from lib.Manpage.Manpage   import Manpage
from lib.KVS.KVS    import KVS as KVS
from lib.List.List  import List
from lib.Time.AdvTime  import AdvTime

from lib.Channel.Channel  import Channel
from lib.Channel.Channels import Channels
from lib.Channel.ChannelCreationQueue import ChannelCreationQueue

from time           import sleep

import os
import websockets
import json
import pickle


class Core():
    """
        Connection
    """    
    def __init__(self, config, root_path = "./"):
        self.account  = config.account
        self.password = config.password
        self.version  = "0.4.0"
        
        self.all_channels = Channels(self.join)
        self.channels = self.all_channels.joined_channels # is this good?
        
        self.channel_creation_queue = ChannelCreationQueue()
        
        self.admins   = {}
        
        self.plugin_loader = None
        self.restarts = 0
        self.start_time = AdvTime()
        
        self.manpage = Manpage(self)
        
        self.config = config
        self.root_path = root_path
        self.data_path = self.root_path+"/"+self.config.server+self.config.endpoint
        
        self.files = KVS()
        self.files.add("status",   "status.dat")
        self.files.add("channels", "channels.dat")
        self.files.add("admins",   "admins.dat")
        self.files.add("all_users", "all_users.bin")
    
    async def connect(self, server, port):
        self.server = server
        self.port   = port
        
        print("CONNECT:",self.config.protocol + self.server + self.config.endpoint)
        try:
            self.connection = await websockets.connect(self.config.protocol + self.server + self.config.endpoint)
            
        except:
            self.connection = None
        
    async def get_api_ticket(self):
        return await Api.get_ticket(self.account, self.password)
        
    async def identify(self):
        data = {
            'method': 'ticket',
            'ticket': await self.get_api_ticket(),
            'account': str(self.account),
            'character': str(self.charactername),
            'cname': "Python Client",
            'cversion': self.version,
        }
        await self._message(opcode.IDENTIFY, data)
        await self._read()
        
    async def join(self, channel_name, true_name = None):
        data = {'channel': channel_name}
        if channel_name not in self.channels and channel_name:
            if true_name:
                channel = Channel(true_name, channel_name)
            else:    
                channel = Channel(channel_name, channel_name)
                
            self.channels[channel_name] = channel
            
            await self._message(opcode.JOIN_CHANNEL, data)
        
    async def create_private_channel(self, channel_name:str):
        data = {"channel": channel_name}
        await self._message(opcode.CREATE_PRIVATE_CHANNEL, data)
        
    async def open_room(self, room):
        channel_code = Channel.find_channel_by_name(self.channels, room)
        data = {"channel": channel_code, "message": "/openroom"}
        await self._message(opcode.CHANNEL_MESSAGE, data)
    
    async def close_room(self, room):
        pass
    
    async def channel_operator(self, user, channel_code):
        data = {"character": user, "channel": channel_code}
        await self._message(opcode.PROMOTE_OP, data)
    
    async def set_channel_description(self, channel_name, description:str):
        channel = self.all_channels.find_channel(channel_name)
        data = {"channel": channel.code, "description": description}
        await self._message(opcode.CHANNEL_DESCRIPTION, data)
    
    async def _join_by_name (self, channel_name = None):
        pass
                
    async def _leave(self, channel):
        data = {'channel': channel}        
        await self._message(opcode.LEAVE_CHANNEL, data)
        self.channels.pop(channel)
    
    async def _order_list_of_official_channels(self):
        await self._message(opcode.LIST_OFFICAL_CHANNELS)
    
    async def _order_list_of_open_private_channels(self):
        await self._message(opcode.LIST_PRIVATE_CHANNELS)
        
    def remove_channel_from_list(self, code):
        self.channels.pop(code)
        
    def remove_channel_from_list_by_name(self, name):
        for channel in self.channels:
            if (name.lower() == self.channels[channel].name.lower()):
                self.remove_channel_from_list(self.channels[channel].code)
                break   #stop after finding the first one
        
    def _rename_channel(self,channel, name):
        if channel in self.channels:
            self.channels[channel].change_name(name)
            print(str(self.channels))
        
    def _add_bot_admin(self, user):
        self.admins[user.lower()] = user
                
    async def join_default_channels(self, channels):
        for channel in channels:
            await self.join(channel)
    
    # TODO: sleep decorator from ChatCodeHandler, here
    # TODO: rename to message
    async def _message(self, opcode, data=None):
        try:
            if data:
                #print("send: {} {}".format(opcode, json.dumps(data)))
                await self.connection.send("{} {}".format(opcode, json.dumps(data)))
            else:
                #print("send: {}".format(opcode))
                await self.connection.send(opcode)
        except Exception as e:
            print("could not send data to server")
            print(e)
            
    async def _read(self):
        try:
            msg = await self.connection.recv()
            
            return msg
        except:
            print ("could not read from stream ...")
        
    def _set_save_path(self, path):
        self.save_path = path+"/"
    
    def _save_channels_to_file(self, file):
        Channel.save_file(self.channels, self.data_path+"/"+file)
    
    async def _load_channels_from_file(self, file):    
        #print ('FILE:', self.data_path+"/"+file)
        channels = Channel.load_file(self.data_path+"/"+file)
        
        print("Load Channels:")      
        for channel in channels.values():
            print (" *", channel.name)
            await self.join(channel.code, channel.name)
            #self.channels[channels[i].code].change_name(channels[i].name)

    # http://stackoverflow.com/questions/12517451/python-automatically-creating-directories-with-file-output
    def save_to_file(self,string, file, mode = 'w'):
        path_to_file = self.data_path+"/"+file
        
        if not os.path.exists(path_to_file):
            try:
                os.makedirs(os.path.dirname(path_to_file))
            except:
                print ("ERROR on creating dir")
        
        if os.path.exists(os.path.dirname(path_to_file)):
            fp = open(path_to_file, mode)
            fp.write(string)
            fp.close()
        else:
            print ("Path/File does not exist: "+path_to_file)
    
    def load_from_file(self, file):
        path_to_file = self.data_path+"/"
        try:
            string = open(path_to_file+file).read()
            return string
        except:
            print ("EXCEPTION could not open/find the file!")
            os.makedirs(path_to_file)
    
    def save_to_binary_file(self, object, file):
        file = self.data_path+"/"+file
        try:
            with open(file, 'wb') as f:
                pickle.dump(object, f)
        except:
            print (f"Error: could not save binary file {file}")

    def load_from_binary_file(self, file):
        data = None
        file = self.data_path+"/"+file
        try:
            with open(file, 'rb') as f:
                data = pickle.load(f)
                return data
        except:
            print (f"Error: could not load binary file {file}")
            return False
        
        return data
    
    async def _set_status(self, status):
        data = {"status":"online",
                "statusmsg":status}  
        sleep(1)      
        await self._message(opcode.STATUS, data)
        
    async def _invite_user_to_channel(self, user, channel_name):
        channel_code = Channel.find_channel_by_name(self.channels, channel_name)
        if channel_code:
            data = {"character": user, "channel": channel_code}  
            await self._message(opcode.INVITE, data)
    
    async def _invite_user_to_channel_by_name(self, user, channel_name):
        await self._invite_user_to_channel(user, channel_name)       
            
    async def _invite_user_to_channel_by_code(self, user, channel_code):
        data = {"character": user, "channel": channel_code}
        await self._message(opcode.INVITE, data)
    
    def is_admin(self, user):
        return user.lower() in self.admins
    
    def is_owner(self, user):
        return user == self.owner
    
    # depricated
    def is_priviliged(self, user):
        print("the method 'is_priviliged' is depricated")
        return (self.is_admin(user)  or self.is_owner(user))
    
    def has_owner_rights(self, user):
        if self.is_owner(user):
            return True
        return False
    
    def has_admin_rights(self, user):
        if self.has_owner_rights(user) or self.is_admin(user):
            return True
        return False
    
    def has_user_rights(self, user):
        if user:
            return True
        return False
    
    def has_role(self, role, user):
        if role == "owner":
            return self.has_owner_rights(user)
        
        elif role == "admin":
            return self.has_admin_rights(user)
        
        elif role == "user":
            return self.has_user_rights(user)
        
        else:
            return False
        
    def set_plugin_loader(self, loader = None):
        if loader:
            self.plugin_loader = loader
            self.plugin_loader.set_client(self)
        else:
            print ("no plugin loader!")
        
    def load_plugins(self):
        if self.plugin_loader:
            print ('Load Plugins:')
            self.plugin_loader.load_plugins()
        else:
            print ("no plugin loader")
        
    def trigger_plugins_load(self):
        for key in self.plugin_loader.plugins:
            print (f"autoload: {key}.load()")
            self.plugin_loader.plugins[key].load()
            
    def trigger_plugins_save(self):
        for key in self.plugin_loader.plugins:
            print (f"autosave: {key}.save()")
            self.plugin_loader.plugins[key].save()
            
    async def trigger_clock(self):
        for key in self.plugin_loader.plugins:
            try:
                await self.plugin_loader.plugins[key].clock()
            except:
                pass
    
    def _sysinfo(self):
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
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        