
import json
import time

from lib.Channel.Channel import Channel
from lib.Counter.Counter import Counter

class Channels(object):
    """
        Dataclass to store channels
    
    """    
    
    def __init__(self, join_method = None):
        self.open_private_channels = {}
        self.official_channels = {}
        
        self.joined_channels = {} # not in use atm, in for testing
        
        self.join_method = join_method
        self.counter = Counter(2)
        
    def add_open_private_channels(self, json_object):
        start = time.time()
        data = json.loads(json_object)
        
        for channel_data in data["channels"]:
            code = channel_data["name"]
            name = channel_data["title"]

            if not code in self.open_private_channels:
                self.open_private_channels[code] = Channel(name, code)
                
        elapsed = time.time() - start
        print(f"open private channels ({len(self.open_private_channels)}) in {elapsed}s")
             
    def add_official_channels(self, json_object):
        start = time.time()
        data = json.loads(json_object)
        
        for channel_data in data["channels"]:
            name = channel_data["name"]
            
            if not name in self.official_channels:
                self.official_channels[name] = Channel(name, name) 

        elapsed = time.time() - start
        print(f"official channels ({len(self.official_channels)}) in {elapsed}s")
    
    def reset_open_private(self):
        del self.open_private_channels
        self.open_private_channels = {}
        
    def find_channel(self, name:str) -> Channel:
        for key, channel in self.open_private_channels.items():
            if channel.name.lower() == name.lower():
                return channel
            
        
        if name in self.official_channels:
            return self.official_channels[name]
        
        else:
            return None
        
    def find_channel_by_id(self, code:str) -> Channel:
        if code in self.open_private_channels:
            return self.open_private_channels[code]
        
        elif code in self.official_channels:
            return  self.official_channels[code]
        
        else:
            return None
    
    async def join(self, name:str):
        channel = self.find_channel(name)
        if self.join_method:
            await self.join_method(channel.code, channel.name)
            self.joined_channels[channel.code] = channel
            return channel.name
        else:
            return None
        
    async def join_by_id(self, code:str):
        channel = self.find_channel_by_id(code)
        if self.join_method:
            await self.join_method(channel.code, channel.name)
            self.joined_channels[channel.code] = channel
            return channel.name
        else:
            return None
        
        
    def clock(self):
        if self.counter.tick():
            for channel in self.joined_channels.values():
                # trigger a clock method if channel is not persistant
                if not channel.persistent:
                    pass
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    