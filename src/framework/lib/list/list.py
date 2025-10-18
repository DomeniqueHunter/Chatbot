import random


class AdvList():
    """
    Advanced List
    Basicly a normal list with some extra functionality that is probably not very much used.
    TODO:
    - try to replace AdvList with normal List someday
    - used in channel.py
    """
    
    def __init__(self, base_list:list=None):
        if base_list and type(base_list) == type([]):
            self.items = base_list
        else:
            self.items = []
            
        self.deny_doubles()
    
    def append(self, item:any):
        if not item in self.items or self.doubles:
            self.items.append(item)
            
    def allow_doubles(self):
        self.doubles = True
        
    def contains(self, item:any):
        return item in self.items
        
    def deny_doubles (self):
        self.doubles = False
        
    def drop(self, item:any):
        if item in self.items:
            self.items.pop(self.items.index(item))
    
    def extend(self, in_list:list):
        if type(in_list) == type([]):
            self.items += in_list
    
        elif type(in_list) == type(AdvList()):
            self.items += in_list.get()
        
        if not self.doubles:
            self.items = list(set(self.items))
        
        return self.items
        
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
    
    
def test():
    # test data
    list1 = AdvList([1, 2, 3, 4, 5])
    list2 = AdvList([4, 5, 6, 7, 8])
    
    list3 = AdvList([1, 2, 3, 4, 5])
    list3.allow_doubles()
    normal_list_of_strings = ['apple', 'banana', 'orange', 'apple', 'kiwi']
    
    # extend advlist with advlist 
    print("Extend advlist with advlist:")
    print(list1.extend(list2))
    
    # extend advlist with normal list
    print("Extend advlist with normal list:")
    print(list1.extend(normal_list_of_strings))
    
    # extend advlist with normal list allowing doubles
    print("Extend advlist with normal list allowing doubles:")
    print(list3.extend(list1))


if __name__ == "__main__":
    test()
