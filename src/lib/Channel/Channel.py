from lib.List.List import List

import json

class Channel(object):
    
    def __init__(self, name, code, description = ''):
        self.name = name
        self.code = code
        self.description = description
        self.characters = List()
        self.admins = List()
        self.persistent = True
        
    def change_name(self, name):
        self.name = name
        
    def change_desciption(self, description):
        self.description = description
        
    def json(self):
        data = {
                "name": self.name,
                "code": self.code,
                "description": self.description,
            }
        return data
    
    def toJSON(self):
        return  json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)
    
    def add_character(self, name):
        if name.lower() not in self.characters.get():
            self.characters.append(name.lower())
        else:
            print ("CHARACTER ALREADY IN CHANNEL")
    
    def add_admin(self, user:str):
        self.admins.append(user)
    
    def remove_character(self, name) -> bool:
        if name.lower() in self.characters.get():
            self.characters.drop(name.lower())
        
        if not self.persistent and len(self.characters) == 1:
            # just me left, it's time to leave
            return True            
        
        return False
    
    def is_online(self, name):
        return self.characters.contains(name.lower())  
    
    def is_admin(self, user:str) -> bool:
        return self.admins.contains(user)
    
    def __eq__(self, other):
        return other == self.code
    
    def __str__(self):
        return self.code      
    
    @staticmethod
    def save_file(channels:dict, file='channels.json'):
        json_object = {
                "channels": [channel.json() for channel in channels.values() if channel.persistent]      
            }
            
        with open(file, "w") as f:
            json.dump(json_object, f)
    
    @staticmethod
    def load_file(file='channels.json'):
        try:
            data = None
            
            with open(file) as f:
                data = json.load(f)
            
            out = {}
            
            if data:
                for d in data['channels']:
                    ch = Channel(d['name'],d['code'],d['description'])
                    out[d['code']] = ch
            
            return out
        
        except Exception as e:
            print("Exception load Channels")
            print(e)
        
    @staticmethod
    def find_channel_by_name(dict_of_channels = None, channel_name = None):        
        if type(dict_of_channels) == type ({}) and channel_name:
            #print (f"looking for {channel_name}")
            for key in dict_of_channels:
                #print (f"found: '{dict_of_channels[key].name}'")
                if dict_of_channels[key].name == channel_name:
                    #print ("found channel")
                    return dict_of_channels[key].code
            
            #print ("Channel: found nothing")
            return False
        else:
            #print ("Channel: wrong type")
            return False    
        
        
        
        
        
        