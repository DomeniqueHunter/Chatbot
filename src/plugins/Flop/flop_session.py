
import random
from time import time


class FlopSession():
    
    def __init__(self, started_by:str, delta:int=300):
        self.started_by = started_by
        self.participants = [started_by]
        self.stated = time()
        self.delta = delta
        
    def join(self, name):
        if name not in self.participants:
            self.participants.append(name)
        
        self.shuffle()
            
    def shuffle(self):
        random.shuffle(self.participants)
        print(self.participants)        
            
    def expired(self):
        return time() - self.stated >= (self.delta)
            
    