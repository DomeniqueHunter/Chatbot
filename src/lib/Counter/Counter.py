
class Counter:
    
    def __init__(self, target = 20):
        self.counter = 0
        self.target = target
        
    def tick (self, *args):
        self.counter = (self.counter +1) % self.target
        
        if self.counter == 0:
            return True
        else:
            return False
    
    