from core.List import List

import json

class Channel():
    
    def __init__(self, name, code, description = ''):
        self.name = name
        self.code = code
        self.description = description
        self.characters = List()
        
    def change_name(self, name):
        self.name = name
        
    def change_desciption(self, description):
        self.description = description
        
    def json(self):
        description_array = self.description.split()
        data = '{"name":"'+self.name+'",\n'
        data+= '"code":"'+self.code+'",\n'
        data+= '"description":"'+" ".join(description_array)+'"\n'
        data+= '}'
        return data
    
    def add_character(self, name):
        if name.lower() not in self.characters.get():
            self.characters.append(name.lower())
        else:
            print ("CHARACTER ALREADY IN CHANNEL")

    def remove_character(self, name):
        if name.lower() not in self.characters.get():
            self.characters.drop(name.lower())
    
    def is_online(self, name):
        return self.characters.contains(name.lower())        
    
    @staticmethod
    def save_file(list, file='channels.json'):
        
        print("LIST:", str(list))
        print("FILE:", file)
        
        json = '{"channels":[\n'
        length = len(list)
        counter = 0
        for i in list:
            if counter < length -1:
                json += str(list[i].json()) + ",\n"
            else:
                json += str(list[i].json()) + "]\n"
            counter += 1
        json += "}"
        
        fp = open(file, 'w')
        fp.write(json)
        fp.close()
        return json
    
    @staticmethod
    def load_file(file='channels.json'):
        try:
            json_data = open(file).read()
            data = json.loads(json_data)        
            out = {}
            print (json_data)            
            
            for d in data['channels']:
                ch = Channel(d['name'],d['code'],d['description'])
                out[d['code']] = ch
            
            return out
        
        except Exception:
            print ("ERROR")
        
    @staticmethod
    def find_channel_by_name(dict_of_channels = None, channel_name = None):        
        if type(dict_of_channels) == type ({}) and channel_name:
            #print (f"looking for {channel_name}")
            for key in dict_of_channels:
                #print (f"found: '{dict_of_channels[key].name}'")
                if dict_of_channels[key].name.lower() == channel_name.lower():
                    #print ("found channel")
                    return dict_of_channels[key].code
            
            #print ("Channel: found nothing")
            return False
        else:
            #print ("Channel: wrong type")
            return False    
        
        
        
        
        
        