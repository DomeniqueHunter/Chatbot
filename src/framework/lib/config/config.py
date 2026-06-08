import json

class Config():
    
    def __init__(self, file:str, verbose:bool=True) -> None:
        # json_data = open(file).read()
        # self.data = json.loads(json_data)#
        with open(file, "r") as f:
            self.data = json.load(f)      
        
        for key, value in self.data.items():
            if verbose:
                if key != 'password':
                    print(f"key: {key} -> {value}")
                else:
                    print(f"key: {key} -> ******")
                    
            self.add(key, value)
        
    def add(self,k:str,v:str) -> None:
        self.__dict__[k] = v
        
    def get(self,k:str, default_return:any=None) -> any:
        return self.data.get(k, default_return)