
import json
import time

from framework.lib.channel import Channel
from framework.lib.counter import Counter


class ChannelManager(object):

    def __init__(self, join_method=None) -> None:
        self.open_private_channels = {}
        self.official_channels = {}

        self.joined_channels = {}

        self.join_method = join_method
        self.counter = Counter(2)

    def add_open_private_channels(self, json_object:str) -> None:
        start = time.time()
        data = json.loads(json_object)

        for channel_data in data["channels"]:
            code = channel_data["name"]
            name = channel_data["title"]

            if not code in self.open_private_channels:
                self.open_private_channels[code] = Channel(name, code)

        elapsed = time.time() - start
        print(f"open private channels ({len(self.open_private_channels)}) in {elapsed}s")

    def add_official_channels(self, json_object:str) -> None:
        start = time.time()
        data = json.loads(json_object)

        for channel_data in data["channels"]:
            name = channel_data["name"]

            if not name in self.official_channels:
                self.official_channels[name] = Channel(name, name)

        elapsed = time.time() - start
        print(f"official channels ({len(self.official_channels)}) in {elapsed}s")

    def add_channel(self, channel:Channel) -> Channel:
        self.joined_channels[channel.code] = channel
        return self.joined_channels[channel.code]

    def reset_joined_channels(self) -> None:
        self.joined_channels = {}

    def reset_open_private(self) -> None:
        del self.open_private_channels
        self.open_private_channels = {}

    def find_channel(self, name:str) -> Channel:
        for channel in self.joined_channels.values():
            if channel.name.lower() == name.lower():
                return channel
        
        for channel in self.open_private_channels.values():
            if channel.name.lower() == name.lower():
                return channel

        if name in self.official_channels:
            return self.official_channels[name]

        else:
            return None

    def find_channel_by_id(self, code:str) -> Channel:
        for channel in self.joined_channels.values():
            if channel.code.lower() == code.lower():
                return channel
        
        if code in self.open_private_channels:
            return self.open_private_channels[code]

        elif code in self.official_channels:
            return  self.official_channels[code]

        else:
            return None
        
    def get_channels_list(self) -> list:
        channels = []
        
        for _, channel in self.joined_channels.items():
            channels.append(channel.json())
        
        return channels
    
    def json(self) -> dict:
        channels = dict()
        for k, v in self.joined_channels.items():
            channels[k] = v.json()
            
        return channels

    async def join(self, name:str, code:str=None) -> str:
        if name and code:
            channel = Channel(name, code)
            await self.join_method(channel.code, channel.name)
            self.add_channel(channel)
            return channel.name

        elif name and not code:
            return await self.join_by_name(name)

        elif not name and code:
            return await self.join_by_id(code)

        return None

    async def join_by_name(self, name:str):
        channel = self.find_channel(name)
        if self.join_method:
            if (channel and channel.code not in self.joined_channels):
                await self.join_method(channel.code, channel.name)
                self.add_channel(channel)
                return channel.name

        return None

    async def join_by_id(self, code:str) -> str:
        channel = self.find_channel_by_id(code)
        if self.join_method:
            await self.join_method(channel.code, channel.name)
            self.add_channel(channel)
            return channel.name
        else:
            return None

    # TODO: test rejoin
    async def rejoin(self, channel:Channel) -> str:
        if isinstance(channel, Channel) and channel.code in self.joined_channels:
            await self.join_method(channel.code, channel.name, force=True)
            return channel.code

        elif isinstance(channel, str):
            await self.join_method(channel, channel)
            print(f"WARNING rejoin: {channel} is not of type Channel but of string")
            return channel.code

        else:
            return None

    async def rejoin_channels(self) -> None:
        for channel in self.joined_channels.values():
            await self.rejoin(channel)

    def clock(self) -> None:
        if self.counter.tick():
            for channel in self.joined_channels.values():
                # trigger a clock method if channel is not persistant
                if not channel.persistent:
                    pass

