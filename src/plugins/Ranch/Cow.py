from Worker import Worker
import random

class Cow:
    def __init__(self, name, milk_yield = 10):
        self.name       = name
        self.milk_yield = milk_yield
        self.counter    = int(0)
        self.level      = 0
        self.milk_total = int(0)
        
    def milk (self):
        #print ("Cow: {}\nYield: {}\nLevel: {}\nTotal: {}".format(self.name, self.milk_yield, self.level, self.milk_total))       
        self.counter += 1
        amount = int( random.uniform(0.2* int(self.milk_yield), int(self.milk_yield)) )
        if ((self.counter % 10) == 0):
            print ("Cow level up!")
            self.level = int(self.level) + 1
            self.counter = 1
            self.milk_yield = int(self.milk_yield) +1
            
        self.milk_total = int(self.milk_total) + amount
        return int(amount)