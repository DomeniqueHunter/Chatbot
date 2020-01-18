class KVS:
    def __init__(self):
        pass
        
    def add(self,key,value):
        self.__dict__[key] = value
        
    def get(self, key):
        return self.__dict__[key]
        
    def get_keys(self):
        return self.__dict__