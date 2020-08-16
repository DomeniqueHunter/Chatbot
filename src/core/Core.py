# pip install websockets
from core.Api       import Api as Api
from core           import Opcodes as opcode
from core.Channel   import Channel as Channel
from core.List      import List
from core.Manpage   import Manpage
from core.Adv_Time  import Adv_Time 
from core.KVS       import KVS as KVS
from time           import sleep

import os
import websockets
import json
import asyncio
import pickle
import ssl
import pathlib


class Core():
    """
        Connection
    """    
    def __init__(self, config, root_path = "./"):
        self.account  = config.account
        self.password = config.password
        self.version  = "0.3.5"
        
        self.channels = {}
        self.admins   = {}
        self.list_of_open_private_channels = List()
        self.official_channels = List()
        self.all_channels = List()
        self.plugin_loader = None
        self.restarts = 0
        self.start_time = Adv_Time()
        
        self.owner_manpage    = Manpage()
        self.admin_manpage    = Manpage()
        self.everyone_manpage = Manpage()
        
        self.config = config
        self.root_path = root_path
        self.data_path = self.root_path+"/"+self.config.server+"/"+self.config.endpoint
        
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
        
    async def _join(self, channel, true_name = None):
        data = {'channel': channel}
        if channel not in self.channels:
            if true_name:
                self.channels[channel] = Channel(true_name, channel)
            else:    
                self.channels[channel] = Channel(channel, channel)
                
        await self._message(opcode.JOIN_CHANNEL, data)
    
    async def _join_by_name (self, channel_name = None):
        pass
                
    async def _leave(self, channel):
        data = {'channel': channel}        
        await self._message(opcode.LEAVE_CHANNEL, data)
    
    async def _order_list_of_official_channels(self):
        await self._message(opcode.LIST_OFFICAL_CHANNELS)
    
    async def _order_list_of_open_private_channels(self):
        await self._message(opcode.LIST_PRIVATE_CHANNELS)
    
    def _find_channel(self, channel_name):
        try:
            self.merge_all_channels()
            list = self.all_channels.get()
            if any(list) and channel_name:
                for channel_object in list:
                    try:
                        # open private
                        if channel_object['title'].lower() == channel_name.lower():
                            return (channel_object['name'], channel_object['title'])
                    except:
                        # public hcat
                        if channel_object['name'].lower() == channel_name.lower():
                            return (channel_object['name'], channel_object['name'])
                return (None, None)
        except:
            print ("find channels failed")
        
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
                
    async def _join_default_channels(self, channels):
        for channel in channels:
            await self._join(channel)
    
    # TODO: sleep decorator from ChatCodeHandler, here
    # TODO: rename to message
    async def _message(self, opcode, data=None):
        try:
            if data:
                print("send: {} {}".format(opcode, json.dumps(data)))
                await self.connection.send("{} {}".format(opcode, json.dumps(data)))
            else:
                print("send: {}".format(opcode))
                await self.connection.send(opcode)
        except:
            print ("could not send data to server")
            
    async def _read(self):
        try:
            msg = await self.connection.recv()
            #print("received: %s" % msg)
            return msg
        except:
            print ("could not read from stream ...")
        
    def _set_save_path(self, path):
        self.save_path = path+"/"
    
    def _save_channels_to_file(self, file):
        Channel.save_file(self.channels, self.data_path+"/"+file)
    
    async def _load_channels_from_file(self, file):    
        print ('FILE:', self.data_path+"/"+file)
        channels = Channel.load_file(self.data_path+"/"+file)         
        for i in channels:
            print (channels[i].name)
            await self._join(channels[i].code, channels[i].name)
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
            print ("Error: could not save binary file {}".format(file))

    def load_from_binary_file(self, file):
        data = None
        file = self.data_path+"/"+file
        try:
            with open(file, 'rb') as f:
                data = pickle.load(f)
                return data
        except:
            print ("Error: could not load binary file {}".format(file))
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
            data_invite = {'channel': channel_code, 'character': user}        
            await self._message(opcode.INVITE, data_invite)        
        
    def merge_all_channels(self):
        '''
         merge all channel lists into one
        '''
        self.all_channels = List(List.merge(
                                    self.list_of_open_private_channels.get(),
                                    self.official_channels.get()
                                    )
                                )
    
    def is_admin(self, user):
        return user.lower() in self.admins
    
    def is_owner(self, user):
        return user == self.owner
    
    def is_priviliged(self, user):
        return (self.is_admin(user)  or self.is_owner(user))
        
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
            print ("autoload: {}.load()".format(key))
            self.plugin_loader.plugins[key].load()
            
    def trigger_plugins_save(self):
        for key in self.plugin_loader.plugins:
            print ("autosave: {}.save()".format(key))
            self.plugin_loader.plugins[key].save()
            
    async def trigger_clock(self):
        for key in self.plugin_loader.plugins:
            try:
                await self.plugin_loader.plugins[key].clock()
            except:
                pass
    
    def _sysinfo(self):
        _now = Adv_Time()
        sysinfo = "\n"
        sysinfo += "Start Time {}\n".format(self.start_time.get_time_date())
        sysinfo += "Local Time {}\n".format(_now.get_time_date())
        sysinfo += "Version {}\n".format(self.version)
        sysinfo += "Restarts: {}\n".format(self.restarts)
        
        sysinfo += "Plugins:\n"
        for plugin in self.plugin_loader.plugins:
            sysinfo += "-- {} ({})\n".format(self.plugin_loader.plugins[plugin].module_name,
                                             self.plugin_loader.plugins[plugin].module_version)
        
        return sysinfo    
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        