from plugins.Plugin_Prototype import Plugin_Prototype

from plugins.Ranch.Hooks import Hooks
from plugins.Ranch.Logic import Logic
from plugins.Ranch.DB_Wrapper import RANCH_DB

from core.Channel import Channel
from core.Counter import Counter

class Ranch(Plugin_Prototype):
    def __init__(self):
        self.module_name = "Ranch"
        self.module_version = "2.3.0"
        
        self.database = None
        
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
        for ac in allowed_channels:
            try:
                if Channel.find_channel_by_name(self.client.channels, ac) == channel:
                    return True
            except:
                print ("ERROR")
        
        print ("Channel wasnt in the list")
        return False
                      
    def register_actions(self):
        if (self.client):
            # channel commands
            self.client.public_msg_handler.add_action("!cow",     self.hooks.get_cow)
            self.client.public_msg_handler.add_action("!cows",    self.hooks.get_cows)
            
            self.client.public_msg_handler.add_action("!workers", self.hooks.get_workers)
            self.client.public_msg_handler.add_action("!worker",  self.hooks.get_worker)
            self.client.public_msg_handler.add_action("!milk",    self.hooks.milk)
            self.client.public_msg_handler.add_action("!milkall", self.hooks.milkall)
            
            self.client.public_msg_handler.add_action("!makemecow",     self.hooks.makemecow)
            self.client.public_msg_handler.add_action("!becomeacow",    self.hooks.makemecow)
            self.client.public_msg_handler.add_action("!becomeaworker", self.hooks.becomeaworker)
            
            # admin commands
            self.client.private_msg_handler.add_action("!ranch_add_cow",    self.hooks.add_cow)
            self.client.private_msg_handler.add_action("!ranch_rename_person", self.hooks.rename_person)
            
            self.client.private_msg_handler.add_action("!ranch_remove_cow", self.hooks.remove_cow)
            self.client.private_msg_handler.add_action("!ranch_remove_worker", self.hooks.remove_worker)
            
            self.client.private_msg_handler.add_action("!ranch_set_cow_milk", self.hooks.set_cow_milk)
            self.client.private_msg_handler.add_action("!ranch_cow_stats", self.hooks.get_cow_stats)
            
            self.client.private_msg_handler.add_action("!ranch_debug_set_wp", self.hooks.debug_set_work_points)
            #self.client.private_msg_handler.add_action("!ranch_save",       self.hook_debug_save)
            #self.client.private_msg_handler.add_action("!ranch_fix_worker", self.hook_fix_workers)
        else:
            print ("no client") 
    
    def setup(self):
        '''
            setup database
        '''
        self.database = RANCH_DB('{}/ranch.db'.format(self.client.data_path))
        self.database.connect()
        self.database.setup()
        
        self.logic.add_worker(self.client.config.character)
        
        '''
            setup save files
        '''
        #self.client.files.add("ranch_cows",    "ranch_cows.bin")
        #self.client.files.add("ranch_workers", "ranch_workers.bin")
        #self.client.files.add("ranch_manager", "ranch_manager.bin")
        
        
        '''
            setup manpage
        '''
        self.client.admin_manpage.add_command("!ranch_add_cow <name>, <milkoutput:optional>", "Add a cow to the Ranch")
        self.client.admin_manpage.add_command("!ranch_rename_person <old name>, <new name>", "Rename a cow from old name ot new name")
        self.client.admin_manpage.add_command("!ranch_remove_cow <name>", "Removes a cow from the Ranch")
        self.client.admin_manpage.add_command("!ranch_set_cow_milk <cow_name>, <yield>", "sets a new milk yield for cow")        
        self.client.admin_manpage.add_command("!ranch_remove_cow <cow_name>")
        self.client.admin_manpage.add_command("!ranch_remove_worker <worker_name>")
        self.client.admin_manpage.add_command("!ranch_cow_stats <cow_name>")
        
        self.client.admin_manpage.add_command("!ranch_debug_set_wp <worker_name>, <work_points>")
        
              
        #self.client.owner_manpage.add_command("!ranch_fix_worker", "Fix Worker Milk Yield")
        
        self.client.everyone_manpage.add_command("\nRanch", "These Commands only work in the Public Channel")
        self.client.everyone_manpage.add_command("!cows <page>", "list all cows")
        self.client.everyone_manpage.add_command("!cow <cowname>", "list stats of a cow")
        self.client.everyone_manpage.add_command("!workers <page>", "list all workers")
        self.client.everyone_manpage.add_command("!worker <workername>", "stats of a worker")
        self.client.everyone_manpage.add_command("!milk <name>", "you will milk a cow, if the cow is online and the cow is listed as cow")
        self.client.everyone_manpage.add_command("!becomeacow", "you will beome a cow")
        self.client.everyone_manpage.add_command("!becomeaworker", "you will beome a worker")
           
    def save (self):
        pass
        """if (len(self.cows) > 0):
            '''
                save the data
            '''
            self.client.save_to_binary_file(self.cows,    self.client.files.ranch_cows)
            self.client.save_to_binary_file(self.workers, self.client.files.ranch_workers)
            self.client.save_to_binary_file(self.manager, self.client.files.ranch_manager)
        else:
            print ("no things to save")"""
            
    def load(self):
        """cows    = self.client.load_from_binary_file(self.client.files.ranch_cows)
        workers = self.client.load_from_binary_file(self.client.files.ranch_workers)
        manager = self.client.load_from_binary_file(self.client.files.ranch_manager)
        
        if cows:  
            self.cows = cows
        if workers:
            self.workers = workers 
        if manager:
            self.manager = manager"""
        pass
        
    async def clock(self):
        if self.counter.tick():
            await self.logic.milkmachine()
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        