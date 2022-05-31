import json

class Config():
    
    def __init__(self, file, verbose = True):
        json_data = open(file).read()
        data = json.loads(json_data)        
        
        for key in data.keys():
            if verbose:
                if key != 'password':
                    print("key:",key,"->",data[key])
                else:
                    print("key:",key,"->","******")
            self.add(key, data[key])
        
    def add(self,k,v):
        self.__dict__[k] = v