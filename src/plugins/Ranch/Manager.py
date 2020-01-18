from Cow import Cow
from Worker import Worker
from core.Adv_Time import Adv_Time
import time, datetime


class Manager:
    def __init__(self):
        self.milkings = {}
        
    def milked (self, worker, cow, milk_amount):
        
        if worker.name not in self.milkings:
            self.milkings[worker.name] = {}
            
        if cow.name not in self.milkings[worker.name]:
            self.milkings[worker.name][cow.name] = {}
            self.milkings[worker.name][cow.name]["last_date"]    = None
            self.milkings[worker.name][cow.name]["total_amount"] = 0
              
        self._set_date(worker, cow)
        self._add_milk(worker, cow, milk_amount)
                
    def get_stats(self, worker):
        '''
            worker as an object
        '''
        stats  = "\n"
        amount = 0
        
        stats += "[b]{}[/b] milked {} liters\n".format(worker.name, worker.get_total_milk())
        
        for c in sorted(self.milkings[worker.name]):
            amount = int(self.milkings[worker.name][c]['total_amount'])
            stats += "-- {}: {} liters\n".format(c, amount)
        return stats
    
    def get_overview(self):
        stats = "\n"
        for w in self.milkings:
            amount = 0
            for c in self.milkings[w]:
                amount += int(self.milkings[w][c]['total_amount'])
            stats += "[b]{}[/b] milked [b]{}[/b] liters\n".format(w, amount)
            
            print (stats)
            
        return stats
    
    def get_total_of_worker(self, worker):
        '''
            worker as an object
        '''
        amount = 0        
        for c in self.milkings[worker.name]:
            amount += int(self.milkings[worker.name][c]['total_amount'])
            print ("{}: {} --> {}".format(c, int(self.milkings[worker.name][c]['total_amount']), amount))
            
        return amount
    
    def get_last_date(self, worker, cow):
        return self.milkings[worker.name][cow.name]['last_date']
    
    def _set_date(self, worker, cow):
        self.milkings[worker.name][cow.name]['last_date'] = int(time.time())
    
    def _add_milk(self, worker, cow, amount):
        self.milkings[worker.name][cow.name]['total_amount'] += int(amount)
        
    def get_total_milk_yield(self):
        workers = self.milkings.__dict__
        total_amount = 0
        
        for worker in workers:
            cows = self.milkings[worker].__dict__
            
            for cow in cows:
                total_amount += self.milkings[worker][cow]['total_amount']
        
        return total_amount
    
    def is_milkable(self, worker, cow):
        if worker.name not in self.milkings:
            return True, 0
        
        if cow.name not in self.milkings[worker.name]:
            return True, 0
        
        now = Adv_Time()
        last = self.get_last_date(worker, cow)
        last = Adv_Time(last)
                
        now_stamp      = int(now.get_time_formated("%Y%m%d")) 
        last_stamp     = int(last.get_time_formated("%Y%m%d")) 
        
        d = Adv_Time(now.get_time_until_tomorrow())
        # 86400 sec == 24 hr
        if ((self.get_last_date(worker, cow) == None) or (last_stamp < now_stamp)):
            return True, 0
        else:
            delta = Adv_Time(now.get_time_until_tomorrow())
            return False, delta.get_time_formated("%Hh %Mmin")