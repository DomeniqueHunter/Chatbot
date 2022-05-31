class Worker:
    def __init__(self, name):
        self.name = name
        self.milk_yield = 0
    
    def milked(self, amount):
        self.milk_yield += amount
        
    def get_total_milk(self):
        return int(self.milk_yield)