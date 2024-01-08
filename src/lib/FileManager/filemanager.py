
import os
import json
import pickle

from types import FunctionType, MethodType
from typing import Union


class ManagedFile:
    
    def __init__(self, handle:str, file_location:str, type:str, 
                        get_function:Union[FunctionType, MethodType],
                        set_function:Union[FunctionType, MethodType]):
        self.handle = handle
        self.file_location = file_location
        self.get_function = get_function
        self.set_function = set_function
        self.type = type
        

class FileManager:
    
    def __init__(self, file_root:str):
        self.file_root = file_root
        
        # ensure dirs
        if not os.path.exists(self.file_root):
            os.makedirs(self.file_root, exist_ok=True)
        
        self.managed_files = {}
        
        # save/load functions
        self.save_functions = {
                        'plain': self.__save_plain,
                        'binary': self.__save_binary,
                        'json': self.__save_json
                        }
                        
        self.load_functions = {
                        'plain': self.__load_plain,
                        'binary': self.__load_binary,
                        'json': self.__load_json
                        }               
    
    def add(self, handle:str, file:str, type:str='json', 
                    get_func:Union[FunctionType, MethodType]=None,
                    set_func:Union[FunctionType, MethodType]=None):
        if handle not in self.managed_files:
            self.managed_files[handle] = ManagedFile(handle, os.path.join(self.file_root, file), type, get_func, set_func)
            
    def save(self, handle:str, content=None):
        try:
            m_file = self.managed_files[handle]
            content = content or m_file.get_function()
            self.save_functions[m_file.type](m_file.file_location, content)
            
        except Exception as e:
            print(e)
        
    def load(self, handle:str):  
        try:
            m_file = self.managed_files[handle]
            loaded_data = self.load_functions[m_file.type](m_file.file_location)
            if m_file.set_function:
                m_file.set_function(loaded_data)
            return loaded_data
            
        except Exception as e:
            print(e)
            
        return None
        
    def save_all(self):
        for handle in self.managed_files.keys():
            self.save(handle)
            
    def load_all(self):
        for handle in self.managed_files.keys():
            self.load(handle)
           
    def __save_plain(self, f_location, content):
        with open(f_location, 'w') as fp:
            fp.write(content)
    
    def __save_binary(self, f_location, content):
        with open(f_location, 'wb') as fp:
            pickle.dump(content, fp)
        
    def __save_json(self, f_location, content):
        with open(f_location, 'w') as fp:
            json.dump(content, fp)
        
    def __load_plain(self, f_location):
        with open(f_location, 'r') as fp:
            return fp.read()
    
    def __load_binary(self, f_location):
        with open(f_location, 'rb') as fp:
            return pickle.load(fp)
        
    def __load_json(self, f_location):
        with open(f_location, 'r') as fp:
            return json.load(fp)
            
            
def test():
    class TestData:
        def __init__(self, a):
            self.a = a
            
        def get_func(self):
            return self.a + "X"
        
        def set_func(self, a):
            self.a = a
    
    td = TestData('TEST')
    
    fm = FileManager('.')
    fm.add('test', 'test.txt', 'plain', td.get_func, td.set_func)
    
    fm.save('test')    
    check = fm.load('test')
    print('check:', check)
    print('read :', td.a)
    
    
if __name__ == "__main__":
    test()