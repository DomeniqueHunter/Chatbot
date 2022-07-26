from plugins.Plugin_Prototype import Plugin_Prototype

import json

class ChatUserManagement(Plugin_Prototype):

    def __init__(self, client = None):
        self.module_name = "ChatUserManagement"
        self.module_version = "0.0.1"
        self.client = client
        self.register_actions()
        self.store = {}
    
    def set_client (self, client):
        self.client = client
              
    async def choose_tool(self, user, input_string = "list all 1"):
        if (self.client.is_owner(user)):
            input_string = input_string.strip()
            parameter = input_string.split()
            tool = parameter[0]       
            parameter = " ".join(parameter [1:])
            if tool == 'list':
                await self.tool_list(user, parameter)
                
            elif tool == 'find':
                await self.tool_find(user, parameter.strip())
                
            else:
                await self.client.send_private_message(f"{tool} is no valid tool!", user)
           
    async def tool_list(self, user, parameter = 'all 1'):
        parameter = parameter.strip()
        parameter = parameter.split(" ")
        
        try:
            gender = parameter[0].strip()        
        except:
            gender = 'all'
        
        try:
            page = parameter[1].strip()
            page = int(page)
        except:
            # force it!
            page = 1
        
        if gender == 'all':
            items = self.client.all_users
        else:
            items = self.gender_based_dict(gender, self.client.all_users)
            
        entries_per_page = 10
        pages = int (len(items) / entries_per_page) + 1   # number of pages
        counter = 0
        page -= 1
        
        start_at = page * entries_per_page
        
        msg = f"\n[{gender}][ {page+1} / {pages} ][users: {len(items)}]:\n"
        
        for key, value in sorted(items.items()):
            if (counter >= start_at and counter <= start_at+entries_per_page-1) or page == -1:
                msg += f"[user]{value['identity']}[/user] : {value['gender']}\n"      
            counter += 1
            
            #if counter > start_at+entries_per_page:
            #   break
            
        await self.client.send_private_message(msg, user)
    
    async def tool_find(self, user, name):
        try:           
            character = self.client.all_users[name.lower()]
            await self.client.send_private_message(f"[user]{character['identity']}[/user] : {character['gender']}", user)
        except:
            await self.client.send_private_message(f"{name} does not exists", user)
        
    async def gender_stats(self, user):
        if (self.client.is_owner(user)):
            all = self.client.all_users
            msg = f"\nAll: 100% - {len(all)}\n"
            genders = ['female', 'male', 'shemale', 'transgender', 'herm', 'male-herm', 'cunt-boy', 'none']
            sall = len(all)
            for gender in genders:     
                amount = len(self.gender_based_dict(gender, all))
                msg += f"{gender}: {round(amount/sall*100,2)}% - {amount}\n"
                
            await self.client.send_private_message(msg, user)

    def gender_based_dict(self, gender, all_elements):
        return {k:v for (k,v) in all_elements.items() if v['gender'].lower() == gender.lower()}
        
    
    async def _opcode_user_connected(self, json_object):
        data = json.loads(json_object)
        self.client.all_users[data['identity'].lower()] =  data   
    
        
    def register_actions(self):
        if self.client:
            print ("CUM register actions")
            self.client.opcodes_handler.add_action('NLN', self._opcode_user_connected)
            
            self.client.private_msg_handler.add_action("!users <tool>", 
                                                       self.choose_tool, 
                                                       "list <gender:all> <page:1>| find <name>", 
                                                       "owner", 
                                                       "Bot (Admin)")
            self.client.private_msg_handler.add_action("!userstats", self.gender_stats, "show gender stats of known users", "owner", "Bot (Admin)")
            
            
            
            
            