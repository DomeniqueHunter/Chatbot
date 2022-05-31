from plugins.Plugin_Prototype import Plugin_Prototype

from plugins.Ranch.Hooks import Hooks
from plugins.Ranch.Logic import Logic
from plugins.Ranch.DB_Wrapper import RANCH_DB

from lib.Channel.Channel import Channel
from lib.Counter.Counter import Counter

class Ranch(Plugin_Prototype):
    def __init__(self):
        self.module_name = "Ranch"
        self.module_version = "2.3.0"
        
        self.logic = Logic(self)
        self.hooks = Hooks(self)        
        
        '''
            ping every 30 seconds
            one day contains 1440 minutes
            one day contains 2880 pings
            
            12 h contain  720 minutes
            12 h contain 1440 pings
        '''
        count_to       = 720
        count_to_debug = 1
        self.counter = Counter (count_to)
             
    def is_milking_channel(self, channel):
        allowed_channels = self.client.config.plugins['ranch']['channels']
        #print(f"channel: {channel}")
        for allowed_channel in allowed_channels:
            try:
                probe = Channel.find_channel_by_name(self.client.channels, allowed_channel)
                
                if probe == channel:
                    return True
            except Exception as e:
                print (f"Exception {e}")
        
        return channel in allowed_channels
    
    def is_in_miling_channel(self, user):
        allowed_channels = self.client.config.plugins['ranch']['channels']
        
        for channel in self.ranch.bot.channels:
            if channel.name in allowed_channels:
                channel.is_online(user)
        
        return False
                      
    def register_actions(self):
        if (self.client):
            # channel commands
            self.client.public_msg_handler.add_action("!cow <cowname>",self.hooks.get_cow, "list stats of a cow", "user", self.module_name)
            self.client.public_msg_handler.add_action("!cows <page>",self.hooks.get_cows, "list all cows", "user", self.module_name)            
            self.client.public_msg_handler.add_action("!worker <workername>", self.hooks.get_worker,"stats of a worker", "user", self.module_name)
            self.client.public_msg_handler.add_action("!workers <page>", self.hooks.get_workers,"list all workers", "user", self.module_name)
            self.client.public_msg_handler.add_action("!milk <name>",self.hooks.milk, "you will milk a cow, if the cow is online and the cow is listed as cow", "user", self.module_name)
            self.client.public_msg_handler.add_action("!Milk",self.hooks.milk, no_help=True)
            self.client.public_msg_handler.add_action("!milkall",self.hooks.milkall, "user","milk all online cows", "user", self.module_name)
            self.client.public_msg_handler.add_action("!Milkall",self.hooks.milkall,no_help=True)
            
            self.client.public_msg_handler.add_action("!makemecow",     self.hooks.makemecow, no_help=True)
            self.client.public_msg_handler.add_action("!becomeacow",    self.hooks.makemecow, "you will beome a cow", "user", self.module_name)
            self.client.public_msg_handler.add_action("!becomeaworker", self.hooks.becomeaworker, "you will beome a worker", "user", self.module_name)
            
            # admin commands
            self.client.private_msg_handler.add_action("!power_milk <cowname>", self.hooks.power_milk, "DEBUG power milk a cow", "admin", f"{self.module_name} (Admin)")
            self.client.private_msg_handler.add_action("!ranch_add_cow <name>, <milkoutput:optional>", self.hooks.add_cow, "Add a cow to the Ranch", "admin", f"{self.module_name} (Admin)")
            self.client.private_msg_handler.add_action("!ranch_rename_person <old name>, <new name>", self.hooks.rename_person, "Rename a cow from old name ot new name", "admin", f"{self.module_name} (Admin)")            
            self.client.private_msg_handler.add_action("!ranch_remove_cow <cow_name>", self.hooks.remove_cow, "Disables a cow", "admin", f"{self.module_name} (Admin)")
            self.client.private_msg_handler.add_action("!ranch_remove_worker <worker_name>", self.hooks.remove_worker, "Disables a worker", "admin", f"{self.module_name} (Admin)")
            self.client.private_msg_handler.add_action("!ranch_set_cow_milk <cow_name>, <yield>", self.hooks.set_cow_milk, "DEBUG sets a new milk yield for a cow", "admin", f"{self.module_name} (Admin)")
            self.client.private_msg_handler.add_action("!ranch_cow_stats <cow_name>", self.hooks.get_cow_stats, "Shows stats of a cow", "admin", f"{self.module_name} (Admin)")
            
            #self.client.private_msg_handler.add_action("!ranch_save",       self.hook_debug_save)
            #self.client.private_msg_handler.add_action("!ranch_fix_worker", self.hook_fix_workers)
        else:
            print ("no client") 
    
    def setup(self):
        '''
            setup database
        '''
        
        self.database = RANCH_DB(f'{self.client.data_path}/ranch.db')
        self.database.connect()
        self.database.setup()
        
        self.logic.add_worker(self.client.config.character)
           
    def save (self):
        pass

            
    def load(self):
        pass
        
    async def clock(self):
        if self.counter.tick():
            await self.logic.milkmachine()
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        