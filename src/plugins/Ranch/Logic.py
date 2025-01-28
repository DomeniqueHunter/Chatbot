import random
from datetime import datetime
from collections import deque
import json
import re


class Logic():

    def __init__(self, ranch):
        self.ranch = ranch

        # todo: Queues to remember cows and workers
        self.remember_cows = deque(maxlen=30)
        self.remember_workers = deque(maxlen=30)
        
    def is_person(self, name:str):
        person = self.ranch.database.get_person(name)
        if person:
            return True        
        return False        

    def is_worker(self, name:str):
        if name in self.remember_workers:
            return True

        worker = self.ranch.database.get_worker(name)

        if worker:
            self.remember_workers.append(name)
            return True
        else:
            return False
    
    def is_cow(self, name:str, respect=True):
        if name in self.remember_cows:
            return True

        data = self.get_cow(name, respect)

        if data:
            self.remember_cows.append(name)
            return True
        else:
            return False

    def is_breeder(self, name:str):
        data = self.ranch.get_breeder(name)
        if data:
            return True
        else:
            return False

    async def add_cow(self, cow_name:str, milk_yield=10):
        is_cow = self.is_cow(cow_name)

        if not is_cow:
            status = self.ranch.database.add_cow(cow_name, milk_yield)

            if not status:
                # is already a cow
                self.ranch.database.enable("cow", cow_name)

            return status
        return not is_cow

    async def add_worker(self, name:str):
        is_worker = self.is_worker(name)

        if not is_worker:
            status = self.ranch.database.add_worker(name)

            if not status:
                self.ranch.database.enable("worker", name)

            return status
        return not is_worker

    async def _get_milk_multiplier(self, worker_name:str):
        worker_is_cow = self.is_cow(worker_name)
        worker_is_worker = self.is_worker(worker_name)
        worker_is_breeder = False  # self.ranch.database.get_breeder(worker_name)

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
            multiplier = 0  # error

        return multiplier
    
    def worker_multiplier(self, lvl):
        if lvl < 200:
            m = lvl // 10
            return 1 + (m / 100)
        
        return 1.2
    
    def worker_milkings(self, lvl):
        if lvl >= 300: return 3
        if lvl >= 200: return 2        
        return 1

    def _milk_that_meat_sack(self, worker_name:str, cow_name:str, multiplier:float=0, respect:bool=True):
        """
        sends the milking request to the database,
        returns if the milking was a success, the amount of milk, if there was a lvl up and the new milking yield of the cow
        @param worker_name: name of the worker, milking the cow
        @param cow_name: name of the cow
        @param respect: debug flag
        @return: (success, amount, lvlup_cow, milk)
        """
        name, milk, level_cow, exp_cow, _ = self.ranch.database.get_cow(cow_name, respect)
        _, wname, wlvl, _, _ = self.get_worker(worker_name)

        if not name.lower() == cow_name.lower():
            return None

        if worker_name.lower() == cow_name.lower():
            return None

        date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        count_milking = self.ranch.database.check_milking(cow_name, worker_name, date)[0]

        if (count_milking < self.worker_milkings(wlvl) or not respect) and multiplier > 0:
            max_milk = int(milk * multiplier)
            amount = int(random.uniform(0.2 * max_milk, max_milk) * self.worker_multiplier(wlvl))
            lvlup_cow = False
            success = self.ranch.database.milk_cow(cow_name, worker_name, amount, date)
            if success:
                lvlup_cow = self._level_up_cow(cow_name, milk, level_cow, exp_cow)

        else:
            success = False
            amount = 0
            lvlup_cow = False
            milk = 0

        # todo: lvlup_cow worker needs to be done
        return (success, amount, lvlup_cow, milk)

    async def milk_cow(self, worker_name:str, cow_name:str):
        """
        sends the milking request to the database,
        returns if the milking was a success, the amount of milk, if there was a lvl up and the new milking yield of the cow_name
        @param worker_name: name of the worker, milking the cow_name
        @param cow_name: name of the cow_name
        @return: (success, amount, lvlup, milk)
        """
        if worker_name == cow_name:
            return None

        _, _, w_lvl, w_ep, _ = self.ranch.database.get_worker(worker_name)[0]
        multiplier = await self._get_milk_multiplier(worker_name)
        bonus = 0.4
        lvlup_worker = False
        success, amount, lvlup, milk = self._milk_that_meat_sack(worker_name, cow_name, multiplier + bonus)
        if success:
            lvlup_worker = self._level_up_worker(worker_name, w_lvl, w_ep)

        return (success, amount, lvlup, milk, lvlup_worker)

    async def power_milk_cow(self, worker_name:str, cow_name:str, debug_exp=1):
        """
        sends the milking request to the database,
        returns if the milking was a success, the amount of milk, if there was a lvl up and the new milking yield of the cow
        @param worker_name: name of the worker, milking the cow
        @param cow_name: name of the cow
        @return: (success, amount, lvlup, milk)
        """
        if worker_name == cow_name:
            return None

        multiplier = 2
        bonus = 1

        _, _, w_lvl, w_ep, _ = self.ranch.database.get_worker(worker_name)[0]

        success, amount, lvlup, milk = self._milk_that_meat_sack(worker_name, cow_name, multiplier + bonus, False)
        lvlup_worker = False
        if success:
            lvlup_worker = self._level_up_worker(worker_name, w_lvl, w_ep, debug_exp)

        return (success, amount, lvlup, milk, lvlup_worker)

    async def milk_all(self, user:str, channel:str) -> (list, int):
        '''
        An easier way to milk all the cows in the channel
        @param user: user that runns the command
        @param channel: channel where the command was started
        @return: milked_cows, not_milkable
        '''
        multiplier = await self._get_milk_multiplier(user)
        _, _, w_lvl, w_ep, _ = self.ranch.database.get_worker(user)[0]
        not_milkable = 0
        milked_cows = []
        
        lvlup_worker = False
        new_worker_exp = 0

        if multiplier > 0:
            for character in self.ranch.client.channels[channel].characters.get():

                if self.is_cow(character) and not user.lower() == character.lower():
                    success, amount, lvlup, _ = self._milk_that_meat_sack(user, character, multiplier)

                    if success:
                        milked_cows.append((character, amount, lvlup))
                        new_worker_exp += 1

                    else:
                        not_milkable += 1
                    
        if new_worker_exp:
            lvlup_worker = self._level_up_worker(user, w_lvl, w_ep, new_worker_exp)

        milked_cows.sort(key=lambda x: x[1], reverse=True)

        return milked_cows, not_milkable, lvlup_worker

    def _level_up_cow(self, cow_name:str, milk:int, level:int, exp:int, add_exp:int=1) -> bool:
        exp += add_exp
        lvlup = False
        
        while True:
            exp_needed = self.next_level_ep(level)
            
            if exp >= exp_needed:
                level += 1
                milk += 1
                exp -= exp_needed
                lvlup = True
            else:
                break
        
        if lvlup:
            self.ranch.database.update_cow_milk(cow_name, milk)
        
        self.ranch.database.update_experience(cow_name, level, exp, 'cow')

        return lvlup

    def _level_up_worker(self, worker_name:str, level:int, exp:int, add_exp:int=1) -> bool:
        exp = exp + add_exp
        lvlup = False
        
        while True:
            exp_needed = self.next_level_ep(level)
            
            if exp >= exp_needed:
                level += 1
                exp -= exp_needed
                lvlup = True
            else:
                break

        self.ranch.database.update_experience(worker_name, level, exp, 'worker')

        return lvlup

    async def milkmachine(self):
        '''
        milk all cows for 1 l each day
        '''
        # get list of cows
        cows = self.get_all_cows()
        date = datetime.now().strftime("%Y-%m-%d")
        
        worker_name = self.ranch.client.config.character 

        for cow in cows:
            cow_name = cow[0]
            _, milk, level, exp = self.ranch.database.get_cow(cow_name)
            count_milking = self.ranch.database.check_milking(cow_name, worker_name, date)[0]
            
            if count_milking == 0:
                success = self.ranch.database.milk_cow(cow_name, worker_name, 1, date)
                if success:
                    self._level_up_cow(cow_name, milk, level, exp)

    def _max_level(self, current_level):
        if current_level >= 100:
            return True
        else:
            return False

    def next_level_ep(self, current_level):
        if current_level >= 100:
            return 2 ** int(current_level / 10)

        elif current_level >= 85:
            return current_level

        else:
            return 10
        
    async def get_person_info(self, name:str) -> str:
        is_person = self.is_person(name)
        if is_person: 
            pid, pname = self.ranch.database.get_person(name)
            response = f"\n[person] {pname} ({pid})\n"
            
            if self.is_cow(name, True):
                # person.name, cow.yield, level.level, level.experience, cow.active
                pname, myield, clvl, cxp, cactive = self.get_cow(name)                
                response += f"[cow] {pname}, yield:{myield}, lvl:{clvl}, xp:{cxp}, active:{cactive}\n"
            
            if self.is_worker(name):
                # worker.id, person.name, level.level, level.experience, worker.active
                wid, pname, wlvl, wxp, wactive = self.get_worker(name)
                response += f"[worker] {pname} ({wid}), lvl:{wlvl}, xp:{wxp}, active:{wactive}\n"
            
            return response

    def get_worker(self, name):
        """
        Returns the milkings of worker

        @param name: name of theworker
        @return: list of Milkings
        """
        return self.ranch.database.get_worker(name)[0]

    def get_workers(self, page=1):
        try:
            page = int (page)
        except:
            page = 1

        workers = self.ranch.database.get_worker_stats_this_month(page)
        message = ""

        if page > 1:
            number = (page - 1) * 10
        else:
            number = 0

        for worker, lvl, _, milk in workers:
            number += 1
            # message += f"{number}. [user]{worker}[/user] ({lvl}) milked {milk} liters\n" # future
            message += f"{number}. [user]{worker}[/user] ({lvl}) milked {milk} liters\n"

        return message

    def get_worker_stats(self, name):
        return self.ranch.database.get_worker_jobs(name)

    def get_cow(self, name, respect=True):
        try:
            return self.ranch.database.get_cow(name, respect)
        except:
            return None

    def get_cow_stats(self, name):
        return self.ranch.database.get_cow_stats(name)

    def get_cow_milkings(self, name):
        return self.ranch.database.get_cow_milkings(name)

    def get_cows(self, page=1):
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

    def set_milking_channel(self, channel_id):
        if not channel_id in self.ranch.milking_channels:
                self.ranch.milking_channels.append(channel_id)

    def show_milking_channels(self):
        message = "\n"

        for index, channel_id in enumerate(self.ranch.milking_channels):
            channel = self.ranch.client.channel_manager.find_channel_by_id(channel_id)
            message += f"({index}) - [b]{channel.name}[/b] ({channel_id})\n"

        return message

    def remove_milking_channel_by_index(self, channel_index):
        channel_index = int(channel_index)
        if len(self.ranch.milking_channels) >= channel_index + 1:
            try:
                self.ranch.milking_channels.pop(channel_index)
            except Exception as e:
                print(e)
                return False

            return True

        return False

    def remove_milking_channel_by_id(self, channel_id):
        if channel_id in self.ranch.milking_channels:
            self.ranch.milking_channels.remove(channel_id)

            return True

        return False

    def remove_milking_channel(self, channel_id):
        if channel_id in self.ranch.milking_channels:
            self.ranch.milking_channels.remove(channel_id)

    async def disable_cow(self, name):
        if self.is_cow(name):
            try:
                self.remember_cows.remove(name)
            except:
                pass
            return self.ranch.database.disable("cow", name)
        else:
            return False

    async def disable_worker(self, name):
        if await self.is_worker(name):
            try:
                self.remember_workers.remove(name)
            except:
                pass
            return self.ranch.database.disable("worker", name)
        else:
            return False

    async def cow_update_milk(self, name, milk):
        if self.is_cow(name):
            return self.ranch.database.update_cow_milk(name, milk)
        else:
            return False

    async def get_buisines_year(self, year=None):
        year = year or datetime.today().year
        year = int(year)

        total = self.ranch.database.get_total_milk(year)
        month_stats = {}
        for month in range(1, 13):
            month_stats[month] = self.ranch.database.get_total_milk(year, month) or 0

        return year, total, month_stats

    def __remove_bbcode(self, text:str) -> str:
        bbcode_pattern = re.compile(f"\[.*?\]")
        return bbcode_pattern.sub('', text)
    
    def is_moo(self, text:str):
        pattern = re.compile(r"(?:m[oO0]{2,})+[.!?~]*", re.IGNORECASE)
        return bool(pattern.search(self.__remove_bbcode(text)))
    
    async def moo_function(self, json_object):
        data = json.loads(json_object)
        channel_id = data['channel']
        message = data['message'].strip()
        user = data['character']
        
        if self.ranch.session_manager.is_channel(channel_id) and self.is_cow(user, True):
            session = self.ranch.session_manager.get_session(channel_id)
            
            if self.is_moo(message):
                session.storage.add(user)
                # print("moo detected", message)
            
            # print(session, session.storage, session.reward)
            
    async def moo_session_endpage(self, channel_id):
        last_session = self.ranch.session_manager.last_session(channel_id)
        
        if last_session and last_session.storage:
            exp = last_session.reward
            text = f"Thank you for mooing, cows! Cows who participated:\n" 
            extra_exp = len(last_session.storage) // 10
            
            for cow_name in last_session.storage:
                _, milk, level_cow, exp_cow, _ = self.ranch.database.get_cow(cow_name, True)
                lvlup_cow = self._level_up_cow(cow_name, milk, level_cow, exp_cow, add_exp=exp + extra_exp)
                lvlup_text = f" even leveled up!" if lvlup_cow else ""                
                text += f" - {cow_name}{lvlup_text}\n"
                
            
            text += f"\n{len(last_session.storage)} cows mooed and gained +{extra_exp+exp} bonus xp each!\n"
                
        else:
            text = "Moo Session closed!"
            
        await self.ranch.client.send_public_message(text, last_session.channel_id)

