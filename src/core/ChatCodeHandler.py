from core.Core      import Core
from core           import Opcodes as opcode
from core.Channel   import Channel
from core.Reaction  import Reaction 

from time          import sleep, time
import json

class ChatCodeHandler(Core):
    """
        Handler
    """
    
    def __init__(self,config, root_path):
        Core.__init__(self, config, root_path)
        self.charactername = config.character
        self.owner = config.owner
        self.status = ""
        self.greetings_list = {}
        
        # Register Message Actions
        self.private_msg_handler = Reaction()
        self.private_msg_handler.add_action("EXCEPTION"     , self._hook_exception_handler)
        self.private_msg_handler.add_action("!join"         , self._hook_join_by_name)
        self.private_msg_handler.add_action("!leave"        , self._hook_leave)
        self.private_msg_handler.add_action("!add_admin"    , self._hook_add_admin)
        self.private_msg_handler.add_action("!remove_admin" , self._hook_remove_admin)
        self.private_msg_handler.add_action("!admins"       , self._hook_admins)
        self.private_msg_handler.add_action("!channels"     , self._hook_channels)        
        
        self.private_msg_handler.add_action("!status"       , self._hook_set_status)
        
        self.private_msg_handler.add_action("!save"         , self._hook_save_all)       
        self.private_msg_handler.add_action("!load"         , self._hook_load_all)
        
        self.private_msg_handler.add_action("!invite"       , self._hook_invite_to_channel)
        self.private_msg_handler.add_action("!kick"         , self._hook_kick)
        self.private_msg_handler.add_action("!help"         , self._hook_help_page)
        
        self.private_msg_handler.add_action("!allusers"     , self._hook_list_all_users)
        
        self.private_msg_handler.add_action("!DIE"          , self._hook_die)
        
        self.private_msg_handler.add_action("!ch_info"      , self._hook_get_users_in_channel)
        self.private_msg_handler.add_action("!debug_ors"    , self._order_list_of_open_private_channels)
        self.private_msg_handler.add_action("!debug_cha"    , self._order_list_of_official_channels)
        self.private_msg_handler.add_action("!__"           , self._hook_sysinfo)
        
        self.owner_manpage.add_command("!add_admin <name>"   , "add a User to admins")
        self.owner_manpage.add_command("!remove_admin <name>", "remove User from admins")
        self.owner_manpage.add_command("!__" , "system information")
        
        self.admin_manpage.add_command("!ch_info <channel>", "returns info of channel")
        self.admin_manpage.add_command("!join <channel>"   , "Bot joins channel")
        self.admin_manpage.add_command("!leave <channel>"  , "Bot leaves channel")
        self.admin_manpage.add_command("!status <text>"    , "Set Bots Status to text")
        self.admin_manpage.add_command("!invite <channel>, <user>", "invite user to channel")
        
        self.everyone_manpage.add_command("!channels" , "returns a list of channels")
        self.everyone_manpage.add_command("!admins", "returns a list of admins")
        self.everyone_manpage.add_command("!greetme <title:optional>", "bot will greet you, when you log in with the title")
        self.everyone_manpage.add_command("!dontgreetme", "bot will no longer greet you")

    async def _ping(self):
        #print("ping back")
        self.ping_time = int(time())
        await self._message(opcode.PING)
    
    # TODO: sleep decorator, put sleep in _message
    async def send_private_message(self, message, user):
        data = {"character": self.charactername,
                "message"  : message,
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

    async def _save_all_settings(self, user = None):
        await self._hook_save_admins(user)
        await self._hook_save_channels(user)
        await self._hook_save_status(user)
        await self._hook_save_all_users(user)
        
        self.trigger_plugins_save()
        
    async def _load_all_settings(self, user = None):        
        await self._hook_load_admins(user)
        await self._hook_load_channels(user)            
        await self._hook_load_status(user)
        await self._hook_load_all_users(user)
        
        self.trigger_plugins_load()
    
    
    '''
        HOOKS
    '''  
    async def _hook_save_all(self, user = None):
        if (user == self.owner):
            print ("save settings")
            await self._save_all_settings(user)
            #await self.send_private_message("settings saved!", user)
    
    async def _hook_load_all(self, user = None):
        if (user == self.owner):
            await self._load_all_settings(user)
    
    async def _hook_exception_handler(self, handler, *args):
        print("HOOK EXCEPTION")
        print("handler:", handler, "\nargs:",*args)     
        #await self.send_private_message("don't understand: "+handler)
        
    async def _hook_permission_denied(self, user):
        await self.send_private_message("Permission denied!")

    async def _hook_join_old(self,  user = None, channel = None):        
        if (channel and self.is_priviliged(user)):
            await self._join(channel, channel)
            await self.send_private_message("joined: "+channel, user)
    
    async def _hook_join_by_name(self,  user = None, channel = None):
        (id, ch_name) = self._find_channel(channel)
        if (id and self.is_priviliged(user)):
            await self._join(id, ch_name)
            await self.send_private_message("joined: "+ch_name, user)
        else:            
            await self.send_private_message("didn't find the channel {}".format(channel), user)
    
    async def _hook_join_by_id(self, user = None, channel = None):
        if self.is_priviliged(user) and channel:
            if not channel in self.channels:
                await self._join(channel, channel)
                         
    async def _hook_leave(self, user = None, channel_to_leave = None):
        if (channel_to_leave and self.is_priviliged(user)):
            for channel in self.channels:
                if (channel_to_leave.lower() == self.channels[channel].name.lower()):
                    await self._leave(self.channels[channel].code)
                    await self.send_private_message("left: "+channel_to_leave, user)
                    self.remove_channel_from_list_by_name(channel_to_leave)
                    break   #stop after finding the first one
            
    #ADMIN HANDLING
    async def _hook_add_admin(self,  user = None, new_admin = None):
        if (self.is_priviliged(user)):
            self._add_bot_admin(new_admin)         
            await self.send_private_message(new_admin+" can now use this bot!", user)
            await self.send_private_message("you can use this bot now!", new_admin)

    async def _hook_remove_admin(self, user = None, admin = None):
        if (self.is_priviliged(user)):                      
            self.admins.pop(admin.lower())
            #self.admins.remove(user.lower())
            await self.send_private_message(admin+" is no longer admin", user)
            
    async def _hook_save_admins(self, user = None):
        if (self.is_owner(user)):
            if len(self.admins) > 0:
                self.save_to_file(str(self.admins), self.files.admins, 'w')
                #await self.send_private_message("saved admins", user)
    
    async def _hook_load_admins(self, user = None):
        if (self.is_owner(user)):
            try:
                data = self.load_from_file(self.files.admins)
                self.admins = eval(data)
                await self.send_private_message("loaded admins", user)
            except:
                pass                

    async def _hook_admins(self,  user = None, message = None):
        string = "\nOwner: [user]"+self.owner+"[/user]\n"
        string += "Admins:\n"
        for admin in self.admins:
            string += "[user]"+admin+"[/user]\n"
        await self.send_private_message(string, user)       
    
    # CHANNEL HANDLING

    async def _hook_channels(self,  user = None, message = None):
        message = "\nChannel: Code\n"
        for channel in self.channels:
            message += "[session="+self.channels[channel].name+"]" + self.channels[channel].code + "[/session]: "+self.channels[channel].code+"\n"
        await self.send_private_message(message, user)
    
    async def _hook_get_users_in_channel(self, user = None, channel = None):
        code = Channel.find_channel_by_name(self.channels, channel)
        if ((code in self.channels) and (self.is_priviliged(user))):
            message = 'Info for Channel [b]{}[/b] ({})\n'.format(self.channels[code].name, self.channels[code].characters.size())
            for char in self.channels[code].characters.get():
                message += "[user]{}[/user]\n".format(char)            
            await self.send_private_message(message, user)     
    
    async def _hook_channel_name(self,  user = None, message = None):
        data = message.split(" ",1)
        
        if len(data) >= 2 and user == self.owner or (user.lower() in self.admins):
            self._rename_channel(data[0], data[1])
            _message = "changed name of channel "+data[0]+" to "+data[1]
            await self.send_private_message(_message, user)
    
    async def _hook_save_channels(self,  user = None):
        if (self.is_owner(user)):
            if len(self.channels) > 0:
                self._save_channels_to_file(self.files.channels)
            else:
                await self.send_private_message("Error on saving Channels", user)
        else:
            await self.send_private_message("Permission denied!", user)
            
    async def _hook_load_channels(self,  user = None):
        if (self.is_owner(user)):
            try:
                await self._load_channels_from_file(self.files.channels)
            except:
                await self.send_private_message("can not open file", user)
    
    async def _hook_save_all_users(self, user = None):
        if (self.is_owner(user)):
            if self.all_users:
                self.save_to_binary_file(self.all_users, self.files.all_users)
            else:
                await self.send_private_message("Error on saving all Users", user)
        else:
            await self.send_private_message("Permission denied!", user)

    async def _hook_load_all_users(self, user = None):
        if (self.is_owner(user)):
            all_users = self.load_from_binary_file(self.files.all_users)
            if all_users:
                self.all_users = all_users
                await self.send_private_message("loaded all users", user)
                
    async def _hook_list_all_users(self, user_in = None, page = 1):
        if (self.is_owner(user_in)):
            
            try:
                page = int(page)
            except:
                # force it!
                page = 1
            
            entries_per_page = 10
            pages = int (len(self.all_users) / entries_per_page) + 1   # number of pages
            counter = 0
            page -= 1
            
            start_at = page * entries_per_page
            
            msg = "\n[ {} / {} ]:\n".format(page+1, pages)
            for user in self.all_users.sort():
                if (counter >= start_at and counter <= start_at+entries_per_page-1) or page == -1:
                    msg += "[user]{}[/user] : {}\n".format(self.all_users[user]['identity'], self.all_users[user]['gender'])
                
                counter += 1
                
            await self.send_private_message(msg, user_in)
    
    async def _hook_die(self,  user = None):
        if (self.is_owner(user)):
            await self._save_all_settings(user)
            await self.send_private_message("I'm out, Bye!", user)
            exit() 
            
    def _hook_start_loggin(self, user = None, channel = None):
        # log channel to file -> logs/channelname
        pass
    
    # STATUS HANDLING
    
    async def _hook_set_status(self, user = None, status = None):
        if (self.is_priviliged(user)):
            if status:
                self.status = status
                await self._set_status(status)
                self._hook_save_status(user)
            else:
                await self.send_private_message("No status given...", user)  
        else:
            self._hook_permission_denied(user)
    
    async def _hook_save_status(self, user = None):
        if (user == self.owner and self.status):
            self.save_to_file(self.status, self.files.status, 'w')
    
    async def _hook_load_status(self, user = None):
        if (user == self.owner):
            try:
                self.status = self.load_from_file(self.files.status)
                await self._set_status(self.status)
            except:
                pass
 
    async def _hook_invite_to_channel(self, user, data = None):
        # data example
        # CHANNELNAME USER NAME
        try:
            (channel, other_user) = data.split(',', 1)
            
            print ("invite USER {} to {}".format(other_user.strip(), channel.strip()))
            
            if (self.is_priviliged(user) and other_user):
                await self._invite_user_to_channel(other_user.strip(), channel.strip())
        except:
            print("ERROR: probably missing ,")        
    
    async def _hook_kick(self, user, message):        
        message    = message.split(" ",1)
        channel    = message[0] 
        other_user = message[1]
        if (self.is_priviliged(user) and other_user):
            print ('other user: ', other_user,' channel: ',channel)
            
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
        help_string  = "\nHELP PAGE:\n"
        help_string += "SYNOPSIS: DESCRIPTION\n"
        
        if (self.is_owner(user)):
            help_string += "\n"
            help_string += self.owner_manpage.get_manpage()
            
        if (self.is_priviliged(user)):
            help_string += "\n"
            help_string += self.admin_manpage.get_manpage()
                    
        help_string += "\n"
        help_string += self.everyone_manpage.get_manpage()
                        
        await self.send_private_message(help_string, user)
            
    async def _hook_sysinfo(self, user):
        if self.is_owner(user):
            await self.send_private_message(self._sysinfo(), user)
    