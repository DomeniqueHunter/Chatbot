from core.ChatCodeHandler   import ChatCodeHandler   as ChatCodeHandler
from core.Reaction          import Reaction as Reaction
from core.Reactions         import Multi_Reaction as Reactions
from core                   import Opcodes  as opcode
from core.Counter           import Counter as Counter
from core.List              import List 
import json, asyncio, time

class OpCodeHandler(ChatCodeHandler):
    """
        Control
    """
    def __init__(self, config, root_path):
        ChatCodeHandler.__init__(self, config, root_path)
        self.loop = asyncio.get_event_loop()
        self.counter_load_channels = Counter(10)
        self.counter_save_all = Counter (60)
        
        # Register Opcode Actions
        self.opcodes_handler = Reactions()
        self.opcodes_handler.add_action("EXCEPTION"               , self._opcode_handler_except)
        self.opcodes_handler.add_action(opcode.PING               , self._opcode_handler_ping)
        self.opcodes_handler.add_action(opcode.PRIVATE_MESSAGE    , self._opcode_handler_private_message)
        self.opcodes_handler.add_action(opcode.CHANNEL_MESSAGE    , self._opcode_handler_channel_message)
        self.opcodes_handler.add_action(opcode.CHANNEL_DESCRIPTION, self._opcode_handler_channeldescription)
        self.opcodes_handler.add_action(opcode.INVITE             , self._opcode_handler_invite)
        self.opcodes_handler.add_action(opcode.KICK               , self._opcode_handler_kicked)
        self.opcodes_handler.add_action(opcode.GONE_OFFLINE       , self._opcoce_user_disconnected)
        self.opcodes_handler.add_action(opcode.STATUS             , self._opcode_user_changed_status)
        self.opcodes_handler.add_action(opcode.JOIN_CHANNEL       , self._opcode_handler_user_joined_channel)
        self.opcodes_handler.add_action(opcode.LEAVE_CHANNEL      , self._opcode_hander_user_left_channel)
        
        self.opcodes_handler.add_action(opcode.INITIAL_CHANNEL_DATA, self._opcode_handler_inital_channel_data)        
        self.opcodes_handler.add_action(opcode.LIST_PRIVATE_CHANNELS, self._opcode_handler_receive_list_of_open_public_channels)
        self.opcodes_handler.add_action(opcode.LIST_OFFICAL_CHANNELS, self._opcode_handler_receive_list_of_official_channels)
        
        self.public_msg_handler = Reaction()
        self.public_msg_handler.add_action("EXCEPTION", self._opcode_handler_except)
        self.public_msg_handler.add_action("!help", self._hook_help_page)
        
        self.all_users = {}
                
    async def dispatcher(self, op, json_object = None):
        if op:
            await self.opcodes_handler.react(op, json_object)
            
    async def _start(self):
        await self.connect(self.config.server, self.config.port)
        await self.identify()
        await self._join_default_channels(self.config.default_channels)
        
    def start(self):
        self.loop.run_until_complete(self._start())
        self.loop.run_until_complete(self._run())
                    
    async def _run (self):
        await self._load_all_settings(self.owner)
        await self._order_list_of_open_private_channels()
        await self._order_list_of_official_channels()
        
        while True:
            # https://websockets.readthedocs.io/en/stable/changelog.html
            if self.connection != None and str(self.connection.state.name) == "OPEN":
                message = await self._read()
                
                if message:
                    data = message.split(" ",1)
                    
                    #print(data)
                    await self.dispatcher(*data)
            else:
                print ("!!!!!!!! RECONNECT !!!!!!!!")
                await self._save_all_settings(self.owner)
                time.sleep(2*60)   
                self.restarts += 1           
                await self._start()
                await self._load_all_settings(self.owner)
                    
    async def _opcode_handler_private_message(self, json_object):
        data = json.loads(json_object)        
        user    = data['character']
        message = data['message'].strip()
        
        message = message.split(' ',1)
        handler = message.pop(0)
        
        print ("user: {}\nmessage: {}".format(user, message))
        
        await self.private_msg_handler.react(handler, user, *message)
    
    async def _opcode_handler_channel_message(self, json_object):
        '''
            Channel Message Dispatcher
        '''
        data = json.loads(json_object)
        channel = data ['channel']
        message = data ['message'].strip()
        user    = data ['character']
        
        message = message.split(' ',1)
        handler = message.pop(0)
        
        await self.public_msg_handler.react(handler, user, channel, *message)
    
    async def _opcode_handler_ping(self, nothing = None):
        #print ("PING ... .. .. ...")
        await self._ping()
        await self.trigger_clock()
        
        if self.counter_load_channels.tick():
            await self._order_list_of_open_private_channels()
            await self._order_list_of_official_channels()
            
        if self.counter_save_all.tick():
            await self._hook_save_all(self.owner)
    
    async def _opcode_handler_channeldescription(self, json_object):
        await self._get_channel_description(json.loads(json_object))    
    
    async def _opcode_handler_except(self, json_object):
        # silent
        pass
    
    async def _opcode_handler_invite(self, json_object):
        data = json.loads(json_object)
        user    = data['sender']
        title   = data['title']
        channel = data['name']
        
        if self.is_priviliged(user):            
            await self._hook_join_by_id(user, channel)
            await self._hook_channel_name(user, channel+" "+title)

    async def _opcode_handler_user_joined_channel(self, json_object):
        data = json.loads(json_object)
        code = data['channel']
        title= data['title']
        user = data['character']['identity']
        self.channels[code].characters.append(user.lower())

    async def _opcode_hander_user_left_channel(self, json_object):
        data = json.loads(json_object)
        code = data['channel']
        user = data['character']
        try:
            self.channels[code].characters.drop(user.lower())
        except:
            print ("channel {} not found".format(code))

    async def _opcode_handler_kicked(self, json_object):
        data      = json.loads(json_object)
        operator  = data['operator']
        channel   = data['channel']
        character = data['character']       
        
        #print ("Operator %s kicked %s from %s" % (operator, character, channel))
        if (character.lower() == self.charactername.lower()):
            self.channels.pop(channel)
            
    async def _opcoce_user_disconnected(self, json_object):
        data = json.loads(json_object)
        for ch_key in self.channels:
            self.channels[ch_key].characters.drop(data['character'].lower())
    
    async def _opcode_user_changed_status(self, json_object):
        pass
    
    async def _opcode_user_connected(self, json_object):
        data = json.loads(json_object)
        self.all_users[data['identity'].lower()] =  data
    
    async def _opcode_handler_inital_channel_data(self, json_object):
        data = json.loads(json_object)
        #print (data)
        channel = data['channel']
        for user in data['users']:
            self.channels[channel].characters.append(user['identity'].lower())
    
    async def _opcode_handler_receive_list_of_open_public_channels(self, json_object):
        data = json.loads(json_object)
        self.list_of_open_private_channels = List(data['channels'])        
        
    async def _opcode_handler_receive_list_of_official_channels(self, json_object):
        data = json.loads(json_object)
        self.official_channels = List(data['channels'])
    
    
        