from plugins import PluginPrototype

from plugins.ranch import Hooks
from plugins.ranch import Logic

# from plugins.ranch.DB_Wrapper import RANCH_DB
from plugins.ranch import RANCH_DB
from plugins.ranch import SessionManager

from framework.lib.counter import Counter

import asyncio


class Ranch(PluginPrototype):

    def __init__(self, client=None):
        self.module_name = "Ranch"
        self.module_version = "2.10.1"
        
        self.set_client(client)
        self.word_counter = self.client.core_plugins.get_plugin("word_counter")
        
        self.logic = Logic(self)
        self.hooks = Hooks(self)

        '''
            ping every 30 seconds
            one day contains 1440 minutes
            one day contains 2880 pings

            12 h contain  720 minutes
            12 h contain 1440 pings
        '''
        count_to = 720
        # count_to_debug = 1
        self.counter = Counter(count_to)

        self.milking_channels = []  # id's of milking channels
        

    def is_milking_channel(self, channel):
        return channel in self.milking_channels

    def register_actions(self):
        if (self.client):
            # channel commands
            self.client.public_msg_handler.add_action("!cow <cowname>", self.hooks.get_cow, "list stats of a cow", "user", self.module_name)
            self.client.public_msg_handler.add_action("!cows <page>", self.hooks.get_cows, "list all cows", "user", self.module_name)
            self.client.public_msg_handler.add_action("!worker <workername>", self.hooks.get_worker, "stats of a worker", "user", self.module_name)
            self.client.public_msg_handler.add_action("!workers <page>", self.hooks.get_workers, "list all workers", "user", self.module_name)
            self.client.public_msg_handler.add_action("!milk <name>", self.hooks.milk, "you will milk a cow, if the cow is online and the cow is listed as cow", "user", self.module_name)
            self.client.public_msg_handler.add_action("!Milk", self.hooks.milk, no_help=True)
            self.client.public_msg_handler.add_action("!milkall", self.hooks.milkall, "user", "milk all online cows", "user", self.module_name)
            self.client.public_msg_handler.add_action("!Milkall", self.hooks.milkall, no_help=True)

            self.client.public_msg_handler.add_action('!businessyear <year>', self.hooks.get_buisines_year, "get stats of the business year", "user", self.module_name)

            self.client.public_msg_handler.add_action("!makemecow", self.hooks.makemecow, no_help=True)
            self.client.public_msg_handler.add_action("!becomeacow", self.hooks.makemecow, "you will beome a cow", "user", self.module_name)
            self.client.public_msg_handler.add_action("!becomeaworker", self.hooks.becomeaworker, "you will beome a worker", "user", self.module_name)
            
            moo_price_per_minute = self.hooks._ppm
            bot_coins = self.client.core_plugins.get_plugin("bot_coins")
            currency = bot_coins.currency or "coins"
                            
            self.client.public_msg_handler.add_action("!buymoo", self.hooks.buy_moo_session, f"buy a moo session for a given time (in minutes, default 5min) for {moo_price_per_minute} c", "user", self.module_name)

            self.client.private_msg_handler.add_action("!ranch_milkablecows <channel>", self.hooks.check_milkable, "Check if cows are milkable", "user", f"{self.module_name} (Direct)")

            # admin commands
            self.client.private_msg_handler.add_action("!power_milk <cowname>, <exp gain (int) : optional>", self.hooks.power_milk, "DEBUG power milk a cow", "admin", f"{self.module_name} (Admin)")
            self.client.private_msg_handler.add_action("!ranch_add_cow <name>", self.hooks.add_cow, "Add a cow to the Ranch", "admin", f"{self.module_name} (Admin)")
            self.client.private_msg_handler.add_action("!ranch_rename_person <old name>, <new name>", self.hooks.rename_person, "Rename a cow from old name ot new name", "admin", f"{self.module_name} (Admin)")
            self.client.private_msg_handler.add_action("!ranch_remove_cow <cow_name>", self.hooks.remove_cow, "Disables a cow", "admin", f"{self.module_name} (Admin)")
            self.client.private_msg_handler.add_action("!ranch_remove_worker <worker_name>", self.hooks.remove_worker, "Disables a worker", "admin", f"{self.module_name} (Admin)")
            # self.client.private_msg_handler.add_action("!ranch_set_cow_milk <cow_name>, <yield>", self.hooks.set_cow_milk, "DEBUG sets a new milk yield for a cow", "admin", f"{self.module_name} (Admin)")
            self.client.private_msg_handler.add_action("!ranch_cow_stats <cow_name>", self.hooks.get_cow_stats, "Shows stats of a cow", "admin", f"{self.module_name} (Admin)")
            self.client.private_msg_handler.add_action("!ranch_milking_channels", self.hooks.get_milking_channels, "Show milking channels", "admin", f"{self.module_name} (Admin)")
            self.client.private_msg_handler.add_action("!ranch_remove_milking_channel <index>", self.hooks.remove_milking_channel_by_index, "Disable milking in the Channel", "admin", f"{self.module_name} (Admin)")
            self.client.private_msg_handler.add_action("!ranch_person <name>", self.hooks.get_person, "Get Preson info", "admin", f"{self.module_name} (Admin)")

            self.client.public_msg_handler.add_action("!milkhere", self.hooks.set_milking_channel, "Enabled milking in the Channel", "admin", f"{self.module_name} (Admin)")
            self.client.public_msg_handler.add_action("!dontmilkhere", self.hooks.remove_milking_channel_by_id, "Disable milking in the Channel", "admin", f"{self.module_name} (Admin)")

            self.client.private_msg_handler.add_action("!new_moo <channel>, <duration in min (int): optional>, <exp (int): optional>", self.hooks.start_session, 'starts a moo sessions', 'admin', f"{self.module_name} (Admin)")
            self.client.private_msg_handler.add_action("!view_moo", self.hooks.moo_show_sessions, "shows moo sessions", "admin", f"{self.module_name} (Admin)")

            # self.client.private_msg_handler.add_action("!ranch_save",       self.hook_debug_save)
            # self.client.private_msg_handler.add_action("!ranch_fix_worker", self.hook_fix_workers)
        else:
            print ("no client")

    def setup(self):
        '''
            setup database
        '''
        print(self.info())
        host = self.client.config.plugins["ranch"]["sql_host"]
        user = self.client.config.plugins["ranch"]["sql_user"]
        password = self.client.config.plugins["ranch"]["sql_pass"]
        database = self.client.config.plugins["ranch"]["sql_database"]

        self.database = RANCH_DB(user, password, database, host)
        self.database.connect()
        self.database.setup()

        # session setup
        self.session_manager = SessionManager(bot=self.client)

        loop = asyncio.get_event_loop()
        # loop = asyncio.new_event_loop()
        loop.run_until_complete(self.logic.add_worker(self.client.config.character, setup=True))

        self.client.file_manager.add("ranch_milking_channels", "ranch_milking_channels.json", 'json')

        # load here to have all setting while setup time
        self.load()
        
        # register miliing channels as allwoed wordcounter channels
        if self.word_counter:
            for channel in self.milking_channels:
                self.word_counter.register_wordcount_channel(channel)

    def save (self):
        if len(self.milking_channels) > 0:
            self.client.file_manager.save('ranch_milking_channels', self.milking_channels)

    def load(self):
        try:
            self.milking_channels = self.client.file_manager.load('ranch_milking_channels') or []

        except:
            print (f"could not load data in '{self.module_name}'")

    async def clock(self):
        if self.counter.tick():
            await self.logic.milkmachine()

        # check if sessions were closed
        recently_closed_sessions = self.session_manager.check_sessions()
        for channel_id in recently_closed_sessions:
            await self.logic.moo_session_endpage(channel_id)


def setup(bot):
    return Ranch(bot)

