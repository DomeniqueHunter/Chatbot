from plugins.Ranch.DB_Wrapper import DB_WRAPPER
from core.BBCode import BBCode
from core.Time import Time
import random
from datetime import datetime
from multiprocessing.pool import worker


class Logic():
    
    def __init__(self, ranch):
        self.ranch = ranch
        
    async def is_worker(self, name):
        worker = self.ranch.database.get_worker(name)
        
        if worker:
            return True
        else:
            return False
    
    async def is_cow(self, name):
        data = self.ranch.database.get_cow(name)
        
        if data:
            return True
        else:
            return False
    
    async def is_breeder(self, name):
        data = self.ranch.get_breeder(name)        
        if data:
            return True
        else:
            return False
    
    def add_cow(self, cow_name, milk_yield = 10):
        status = self.ranch.database.add_cow(cow_name, milk_yield)
        
        if not status:
            # is already a cow
            self.ranch.database.enable("cow", cow_name)
        
        return status
    
    def add_worker(self, name):
        status = self.ranch.database.add_worker(name)
        
        if not status:
            self.ranch.database.enable("worker", name)
        
        return status
    
    async def _get_milk_multiplier(self, worker_name):
        worker_is_cow = await self.is_cow(worker_name)
        worker_is_worker = await self.is_worker(worker_name)
        worker_is_breeder = False #self.ranch.database.get_breeder(worker_name) 
        
        if worker_is_worker or worker_is_breeder:              
            if worker_is_cow:
                multiplier = 0.5
            
            elif worker_is_worker and worker_is_cow:
                multiplier = 0.8
                
            elif worker_is_breeder:
                multiplier = 2
                
            else:
                multiplier = 1
        else:
            multiplier = 0  #error
             
        return multiplier
    
    def _milk_that_meat_sack(self, worker_name, cow_name, multiplier = 0, work_points = 1):
        """
        sends the milking request to the database, 
        returns if the milking was a success, the amount of max_milk, if there was a lvl up and the new milking yield of the cow
        @param worker_name: name of the worker, milking the cow
        @param cow_name: name of the cow
        @return: (success, amount, lvlup_cow, max_milk)
        """        
        name, max_milk, level, exp = self.ranch.database.get_cow(cow_name)[0]
                
        if not name.lower() == cow_name.lower():
            return None
        
        if worker_name.lower() == cow_name.lower():
            return None
        
        # grab some worker stats
        lvl_worker, exp_worker, max_work_points, used_work_points = self.ranch.database.get_worker_work_points(worker_name, cow_name)
        
        print (f"milk: n:{worker_name}, lvl_worker:{lvl_worker} e_w:{exp_worker} | c:{cow_name}, m:{max_milk}, lvl:{level}, exp:{exp} | m_wp:{max_work_points}, u_wp:{used_work_points}")    # debug!
        
        lvlup_cow = False
        lvlup_worker = False
        
        if (max_work_points - used_work_points) >= work_points and  multiplier > 0:
            date = datetime.now().strftime("%Y-%m-%d")
            max_milk = int(max_milk * multiplier / max_work_points)
            amount = int(random.uniform(0.2* max_milk, max_milk))          
            success = self.ranch.database.milk_cow(cow_name, worker_name, amount, date, work_points)
            
            if success:
                lvlup_cow = self._level_up_cow(cow_name, max_milk, level, exp)
                lvlup_worker = self._level_up_worker(worker_name, max_milk, lvl_worker, exp_worker)
                
        else:
            success = False
            amount = 0
            max_milk = 0
        
        return (success, amount, lvlup_cow, max_milk, lvlup_worker)
    
    async def milk_cow(self, worker_name, cow_name):
        """
        sends the milking request to the database, 
        returns if the milking was a success, the amount of milk, if there was a lvl up and the new milking yield of the cow
        @param worker_name: name of the worker, milking the cow
        @param cow_name: name of the cow
        @return: (success, amount, lvlup, milk)
        """
        work_points = 1
        multiplier = await self._get_milk_multiplier(worker_name)
        bonus = 0.4
        
        return self._milk_that_meat_sack(worker_name, cow_name, multiplier+bonus, work_points)

    async def milk_all(self, user, channel):
        '''
            An easier way to milk all the cows in the channel
        '''        
        message = ""
        multiplier = await self._get_milk_multiplier(user)
        not_milkable = 0
        work_points = 2
        
        if multiplier > 0:
            for character in self.ranch.client.channels[channel].characters.get():
                
                if await self.is_cow(character) and not user.lower() == character.lower():
                    success, amount, lvlup, milk, lvlup_worker = self._milk_that_meat_sack(user, character, multiplier, work_points)
                    
                    if success:
                        message += f"\n[user]{user}[/user] milked [user]{character}[/user] and got {amount} liters of Milk"
                        
                        if lvlup:
                            message += f"\n[user]{character}[/user] has leveled up!"
                    else:
                        not_milkable += 1
                        
                    if lvlup_worker:
                        message += f"\n[user]{user}[/user] has leveled up!"
                                                
                else:
                    #print (character, await self.is_cow(character))
                    pass
            
            if not_milkable > 0:
                if not_milkable == 1:
                    i = "is"
                    c = "cow"
                else:
                    i = "are"
                    c = "cows"
                    
                milkable_in = Time.time_until_tomorrow()
                message += f"\nThere {i} {not_milkable} {c} who {i} milkable in {milkable_in}."
                    
        else:
            message = None
        
        #print ("mssage: {}".format(message))
        return message

    def _level_up_cow(self, cow_name, milk, level, exp):
        exp += 1
        if exp >= self.next_level_ep_cow(level):
            level += 1
            milk += 1
            exp = 0
            lvlup = True
            
            self.ranch.database.update_cow_milk(cow_name, milk)
        else:
            lvlup = False
        self.ranch.database.update_experience(cow_name, level, exp, 'cow')
        
        return lvlup
    
    def _level_up_worker(self, worker_name, work_points, level, exp):
        exp += 1
        if exp >= self.next_level_ep_worker(level):
            level += 1
            work_points += 1
            exp = 0
            lvlup = True
            
            self.ranch.database.update_worker_points(worker_name, 1)
        else:
            lvlup = False
        self.ranch.database.update_experience(worker_name, level, exp, 'worker')
        return lvlup

    async def milkmachine(self):
        '''
        milk all cows for 1 l each day
        '''
        # get list of cows
        cows = self.get_all_cows()
        date = datetime.now().strftime("%Y-%m-%d")
        
        for cow in cows:
            cow_name = cow[0]
            
            milk_stats = self.ranch.database.get_cow(cow_name)
            name = milk_stats[0][0]
            milk = milk_stats[0][1]
            level= milk_stats[0][2]
            exp  = milk_stats[0][3]
            
            success = self.ranch.database.milk_cow(cow_name, self.ranch.client.config.character, 1, date)
            if success:
                self._level_up_cow(cow_name, milk, level, exp)
          
    def _max_level(self, current_level):
        if current_level >= 100:
            return True
        else:
            return False
       
    def next_level_ep_cow(self, current_level):
        if current_level >= 100:
            return 2**int(current_level/10)
        
        elif current_level >= 85:
            return current_level * 3
        
        elif current_level >= 50:
            return current_level * 2
        
        else:
            return 10
        
    def next_level_ep_worker(self, current_level):
        if current_level >= 100:
            return 2**int(current_level/10)
        
        elif current_level >= 85:
            return current_level * 30
        
        elif current_level >= 50:
            return current_level * 20
        
        else:
            return 100
        
                
    def get_worker(self, name):
        """
        Returns the milkings of worker
        
        @param name: name of theworker
        @return: list of Milkings
        """
        data = self.ranch.database.get_worker(name)
        return data

    def get_workers(self, page = 1):        
        try:
            page = int (page)
        except:
            page = 1
            
        workers = self.ranch.database.get_worker_stats_this_month(page)
        message = ""
        
        if page > 1:
            number = (page-1) * 10
        else:
            number = 0
        
        for worker, lvl, _, milk in workers:
            number += 1
            message += f"{number}. [user]{worker}[/user] ({lvl}) milked {milk} liters\n"     
        
        return message
    
    def get_worker_stats(self, name):
        return self.ranch.database.get_worker_jobs(name)    
    
    def get_cow(self, name):
        data = self.ranch.database.get_cow(name)
        return data[0][0], data[0][1], data[0][2], data[0][3]
    
    def get_cow_stats(self, name):
        data = self.ranch.database.get_cow_stats(name)
        return data
    
    def get_cow_milkings(self, name):
        return self.ranch.database.get_cow_milkings(name)
    
    def get_cows(self, page = 1):
        """
            @param page: number of page
            @return: list of milkings of cows (name, level, exp, milk)
        """
        data = self.ranch.database.get_cow_stats_this_month(page)
        return data
    
    def get_all_cows(self):
        """
        get all cows
        """
        data = self.ranch.database.get_all_cows()
        return data
    
    def get_all_workers(self):
        """
        get all worker names
        """
        return self.ranch.database.get_all_workers()
               
    def rename_person (self, old_name, new_name):
        return self.ranch.database.rename_person(old_name, new_name)
        
    async def disable_cow(self, name):
        if await self.is_cow(name):
            return self.ranch.database.disable("cow", name)
        else:
            return False
    
    async def disable_worker(self, name):
        if await self.is_worker(name):
            return self.ranch.database.disable("worker", name)
        else:
            return False
        
    async def update_cow_milk(self, name, milk):
        if await self.is_cow(name):
            return self.ranch.database.update_cow_milk(name, milk)
        else:
            return False
        
    async def debug_set_work_points(self, name, points):
        if await self.is_worker(name) and type(points) == type(1):
            return self.ranch.database.set_work_points(name, points)
        
        else:
            return False
    
        
        
        
        
        
        
        
        
        
        
        