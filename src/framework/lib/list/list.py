import random

class AdvList():
    
    def __init__(self, list = None):
        if list and type(list) == type([]):
            self.items = list
        else:
            self.items = []
            
        self.deny_doubles()
    
    def append(self, item):
        if not item in self.items or self.doubles:
            self.items.append(item)
            
    def allow_doubles(self):
        self.doubles = True
        
    def contains(self, item):
        return item in self.items
        
    def deny_doubles (self):
        self.doubles = False
        
    def drop(self, item):
        if item in self.items:
            self.items.pop(self.items.index(item))
    
    def extend(self, list):
        if type(list) == type([]):
            self.items = AdvList.merge(self.items, list, doubles = self.doubles)
            return self.items
        else:
            return False
        
    def get(self):
        return self.items
    
    def shuffle(self):
        random.shuffle(self.items)
        
    def size(self):
        return len(self.items)
    
    def __len__(self):
        return len(self.items)
        
    def sort (self):
        self.items.sort()
        
    @staticmethod
    def merge(*args, **kwargs):
        final_list = AdvList()
        if 'doubles' in kwargs:
            doubles = kwargs['doubles']
            if doubles == True:
                final_list.allow_doubles()
            else:
                final_list.deny_doubles()
        else:
            doubles = False
            final_list.deny_doubles()
        
        for list in args:
            for entry in list:
                final_list.append(entry)
        
        return final_list.get()