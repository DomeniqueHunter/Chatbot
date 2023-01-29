
import json
import time

from lib.Channel.Channel import Channel
from lib.Counter.Counter import Counter


class ChannelManager(object):
    """
        Dataclass to store channels
        TODO: rename into ChannelManager
    
    """

    def __init__(self, join_method=None):
        self.open_private_channels = {}
        self.official_channels = {}

        self.joined_channels = {}

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

    def add_channel(self, channel:Channel) -> Channel:
        self.joined_channels[channel.code] = channel
        return self.joined_channels[channel.code]

    def reset_joined_channels(self):
        self.joined_channels = {}

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

    async def join(self, name:str, code:str=None):
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

    async def join_by_id(self, code:str):
        channel = self.find_channel_by_id(code)
        if self.join_method:
            await self.join_method(channel.code, channel.name)
            self.add_channel(channel)
            return channel.name
        else:
            return None

    # TODO: test rejoin
    async def rejoin(self, channel:Channel):
        if isinstance(channel, Channel) and channel.code in self.joined_channels:
            await self.join_method(channel.code, channel.name, force=True)
            return channel.code

        elif isinstance(channel, str):
            await self.join_method(channel, channel)
            print(f"WARNING rejoin: {channel} is not of type Channel but of string")
            return channel.code

        else:
            return None

    async def rejoin_channels(self):
        for channel in self.joined_channels.values():
            await self.rejoin(channel)

    def clock(self):
        if self.counter.tick():
            for channel in self.joined_channels.values():
                # trigger a clock method if channel is not persistant
                if not channel.persistent:
                    pass

