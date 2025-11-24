import random
from plugins.Ranch.response import MilkJobResponse
from datetime import datetime
from collections import deque, defaultdict
import calendar
import json
import re
import time
from plugins.Ranch.milkingstatus import MilkingStatus
from typing import Tuple


class Logic():

    def __init__(self, ranch):
        self.ranch = ranch

        # todo: Queues to remember cows and workers
        self.remember_cows = deque(maxlen=30)
        self.remember_workers = deque(maxlen=30)
        
        self.worker_interactions = defaultdict(dict)
        
        self.time_between_milkings = 10800  # 10 800 = 3 hr * 60 min * 60 sec
        
    def is_person(self, name:str) -> bool:
        person = self.ranch.database.get_person(name)
        if person:
            return True        
        return False        

    def is_worker(self, name:str) -> bool:
        if name in self.remember_workers:
            return True

        worker = self.ranch.database.get_worker(name)

        if worker:
            self.remember_workers.append(name)
            return True
        else:
            return False
    
    def is_cow(self, name:str, respect=True) -> bool:
        if name in self.remember_cows:
            return True

        data = self.get_cow(name, respect)

        if data:
            self.remember_cows.append(name)
            return True
        else:
            return False

    def is_breeder(self, name:str) -> bool:
        data = self.ranch.get_breeder(name)
        if data:
            return True
        else:
            return False

    async def add_cow(self, cow_name:str, milk_yield=10) -> bool:
        is_cow = self.is_cow(cow_name)

        if not is_cow:
            status = self.ranch.database.add_cow(cow_name, milk_yield)

            if not status:
                # is already a cow
                self.ranch.database.enable("cow", cow_name)

            return status
        return not is_cow

    async def add_worker(self, name:str) -> bool:
        is_worker = self.is_worker(name)

        if not is_worker:
            status = self.ranch.database.add_worker(name)

            if not status:
                self.ranch.database.enable("worker", name)

            return status
        return not is_worker

    async def _get_milk_multiplier(self, worker_name:str) -> float:
        worker_is_cow = self.is_cow(worker_name)
        worker_is_worker = self.is_worker(worker_name)
        worker_is_breeder = False  # self.ranch.database.get_breeder(worker_name)

        if worker_is_worker or worker_is_breeder: 

            if worker_is_cow:
                multiplier = 0.6

            elif worker_is_breeder:
                multiplier = 2.0

            else:
                multiplier = 1.0
        else:
            multiplier = 0.0  # error
        # print(f"multiplier: {multiplier}")
        return multiplier
    
    def worker_multiplier(self, lvl) -> float:
        if lvl < 200:
            m = lvl // 10
            return 1 + (m / 100)
        
        return 1.2
    
    def worker_milkings(self, worker_lvl:int, cow_lvl:int) -> int:
        if cow_lvl <= 10: return 1
        
        if worker_lvl >= 200: return 3
        if worker_lvl >= 100: return 2        
        return 1
    
    def check_milking_delay(self, worker:str, cow:str, delay_s:int=3600) -> bool:
        now = int(time.time())
        last = self.worker_interactions[worker].get(cow, 0)
        return (now - last) >= delay_s

    def _milk_that_meat_sack(self, worker_name:str, cow_name:str, multiplier:float=0, force_milking:bool=True) -> MilkJobResponse:
        """
        sends the milking request to the database,
        returns if the milking was a status, the amount of milk, if there was a lvl up and the new milking yield of the cow
        @param worker_name: name of the worker, milking the cow
        @param cow_name: name of the cow
        @param force_milking: debug flag
        @return: (status, amount, lvlup_cow, milk)
        """
        name, max_milk, level_cow, exp_cow, _ = self.ranch.database.get_cow(cow_name, force_milking)
        _, wname, wlvl, _, _ = self.get_worker(worker_name)

        if not name.lower() == cow_name.lower():
            return None

        if worker_name.lower() == cow_name.lower():
            return None

        date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        count_milking = self.ranch.database.check_milking(cow_name, worker_name, date)[0] # 0..1..N
        
        if (count_milking < self.worker_milkings(wlvl, level_cow) or not force_milking) and multiplier > 0:
            if self.check_milking_delay(worker_name, cow_name, delay_s=self.time_between_milkings) or not force_milking: 
                max_milk = int(max_milk * multiplier)
                
                repetions_factor = 1 / (count_milking + 1)
                
                amount = int(random.uniform(0.2 * max_milk, max_milk) * self.worker_multiplier(wlvl) * repetions_factor)
                cow_lvl_up = False
                
                if amount > 0:
                    success = self.ranch.database.milk_cow(cow_name, worker_name, amount, date)
                else:
                    return MilkJobResponse(worker_name, cow_name, MilkingStatus.COW_EMPTY)
                
                if success:
                    cow_lvl_up = self._level_up_cow(cow_name, max_milk, level_cow, exp_cow)
                    self.worker_interactions[worker_name][cow_name] = int(time.time())
                    status = MilkingStatus.SUCCESS
                else:
                    status = MilkingStatus.MILKING_DONE_TODAY
            
                return MilkJobResponse(worker_name, cow_name, status, max_milk, amount, cow_lvl_up)
            
            else:
                return MilkJobResponse(worker_name, cow_name, MilkingStatus.MILKING_ON_COOLDOWN)
        
        else:
            return MilkJobResponse(worker_name, cow_name, MilkingStatus.MILKING_DONE_TODAY)

    async def milk_cow(self, worker_name:str, cow_name:str) -> MilkJobResponse:
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
        
        response = self._milk_that_meat_sack(worker_name, cow_name, multiplier + bonus)
        
        if response.status == MilkingStatus.SUCCESS:
            response.worker_lvl_up = self._level_up_worker(worker_name, w_lvl, w_ep)
            
        return response

    async def power_milk_cow(self, worker_name:str, cow_name:str, debug_exp=1) -> MilkJobResponse:
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

        response = self._milk_that_meat_sack(worker_name, cow_name, multiplier + bonus, False)
        
        if response.status == MilkingStatus.SUCCESS:
            response.worker_lvl_up = self._level_up_worker(worker_name, w_lvl, w_ep, debug_exp)
        
        return response

    async def milk_all(self, user:str, channel:str) -> Tuple[list, int, bool]:
        '''
        An easier way to milk all the cows in the channel
        @param user: user that runns the command
        @param channel: channel where the command was started
        @return: milked_cows, not_milkable
        '''
        multiplier = await self._get_milk_multiplier(user)
        _, _, w_lvl, w_ep, _ = self.ranch.database.get_worker(user)[0]
        not_milkable: int = 0
        milked_cows: list = []
        
        # lvlup_worker = False
        new_worker_exp = 0

        if multiplier > 0:
            for character in self.ranch.client.channels[channel].characters.get():

                if self.is_cow(character) and not user.lower() == character.lower():
                    response = self._milk_that_meat_sack(user, character, multiplier)

                    if response.status == MilkingStatus.SUCCESS:
                        milked_cows.append((response.cow, response.amount, response.cow_lvl_up))
                        new_worker_exp += 1

                    else:
                        not_milkable += 1
        
        worker_lvl_up: bool = False
        if new_worker_exp:
            worker_lvl_up = self._level_up_worker(user, w_lvl, w_ep, new_worker_exp)

        milked_cows.sort(key=lambda x: x[1], reverse=True)

        return milked_cows, not_milkable, worker_lvl_up

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

    async def milkmachine(self) -> None:
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

    def _max_level(self, current_level) -> bool:
        if current_level >= 100:
            return True
        else:
            return False

    def next_level_ep(self, current_level) -> int:
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

    def get_worker(self, name:str) -> tuple:
        """
        Returns the milkings of worker

        @param name: name of theworker
        @return: list of Milkings: worker.id, person.name, level.level, level.experience, worker.active
        """
        return self.ranch.database.get_worker(name)[0]

    def get_workers(self, page:int=1) -> str:
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

    def get_worker_stats(self, name:str):
        return self.ranch.database.get_worker_jobs(name)

    def get_cow(self, name:str, respect:bool=True):
        try:
            return self.ranch.database.get_cow(name, respect)
        except:
            return None

    def get_cow_stats(self, name:str):
        return self.ranch.database.get_cow_stats(name)

    def get_cow_milkings(self, name:str):
        return self.ranch.database.get_cow_milkings(name)

    def get_cows(self, page:int=1):
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

    def rename_person (self, old_name:str, new_name:str):
        return self.ranch.database.rename_person(old_name, new_name)

    def set_milking_channel(self, channel_id:str):
        if not channel_id in self.ranch.milking_channels:
            self.ranch.milking_channels.append(channel_id)

    def show_milking_channels(self):
        message = "\n"
        garbage = []

        for index, channel_id in enumerate(self.ranch.milking_channels):
            channel = self.ranch.client.channel_manager.find_channel_by_id(channel_id)
            if channel: 
                message += f"({index}) - [b]{channel.name}[/b] ({channel_id})\n"
            else:
                message += f"({index}) - {channel_id} not found, removed!\n"
                garbage.append(channel_id)
        
        if any(garbage):
            for channel_id in garbage:
                print(f"remove: {channel_id}")
                self.remove_milking_channel_by_id(channel_id)

        return message

    def remove_milking_channel_by_index(self, channel_index:str):
        channel_index = int(channel_index)
        if len(self.ranch.milking_channels) >= channel_index + 1:
            try:
                self.ranch.milking_channels.pop(channel_index)
            except Exception as e:
                print(e)
                return False

            return True

        return False

    def remove_milking_channel_by_id(self, channel_id:str):
        if channel_id in self.ranch.milking_channels:
            self.ranch.milking_channels.remove(channel_id)

            return True

        return False

    def remove_milking_channel(self, channel_id:str):
        if channel_id in self.ranch.milking_channels:
            self.ranch.milking_channels.remove(channel_id)

    async def disable_cow(self, name:str):
        if self.is_cow(name):
            try:
                self.remember_cows.remove(name)
            except:
                pass
            return self.ranch.database.disable("cow", name)
        else:
            return False

    async def disable_worker(self, name:str):
        if await self.is_worker(name):
            try:
                self.remember_workers.remove(name)
            except:
                pass
            return self.ranch.database.disable("worker", name)
        else:
            return False

    async def cow_update_milk(self, name:str, milk:int):
        if self.is_cow(name):
            return self.ranch.database.update_cow_milk(name, milk)
        else:
            return False
        
    def __get_days_until_end_of_month(self, year:int, month:int) -> int:
        today = datetime.today()
        
        # we are in the current month return days until today
        if year == today.year and month == today.month:
            return today.day
            
        # future months return 0
        elif year == today.year and month > today.month:
            return 0
        
        # past months return their length
        return calendar.monthrange(year, month)[1]

    async def get_buisines_year(self, year:int=None):
        year = year or datetime.today().year
        year = int(year)

        total = self.ranch.database.get_total_milk(year)
        month_stats = {}
        for month in range(1, 13):
            milk = self.ranch.database.get_total_milk(year, month) or 0
            days = self.__get_days_until_end_of_month(year, month)
            
            # 0 can happen for future months only
            milk_per_day = milk // days if days else 0                
            
            month_stats[month] = (milk, milk_per_day)

        return year, total, month_stats

    def __remove_bbcode(self, text:str) -> str:
        bbcode_pattern = re.compile(r"\[.*?\]")
        return bbcode_pattern.sub('', text)
    
    def is_moo(self, text:str):
        pattern = re.compile(r"(?:m[oO0]{2,})+[.!?~]*", re.IGNORECASE)
        return bool(pattern.search(self.__remove_bbcode(text)))
    
    async def moo_function(self, json_object:str):
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
            
    async def moo_session_endpage(self, channel_id:str):
        last_session = self.ranch.session_manager.last_session(channel_id)
        
        if last_session and last_session.storage:
            exp = last_session.reward
            text = f"Thank you for mooing, cows! Cows who participated:\n" 
            extra_exp = len(last_session.storage) // 4
            
            for cow_name in last_session.storage:
                _, milk, level_cow, exp_cow, _ = self.ranch.database.get_cow(cow_name, True)
                lvlup_cow = self._level_up_cow(cow_name, milk, level_cow, exp_cow, add_exp=exp + extra_exp)
                lvlup_text = f" even leveled up!" if lvlup_cow else ""                
                text += f" - {cow_name}{lvlup_text}\n"
            
            text += f"\n{len(last_session.storage)} cows mooed and gained +{extra_exp+exp} bonus xp each!\n"
                
        else:
            text = "Moo Session closed!"
            
        await self.ranch.client.send_public_message(text, last_session.channel_id)
        

def test_milkings(): 
    max_milk = 10
    worker_multiplier = .8
    
    for count_milking in range(0, 10):
        repetions_factor = 1 / (count_milking + 1)
        amount = int(random.uniform(0.2 * max_milk, max_milk) * worker_multiplier * repetions_factor)
        
        print(f"{count_milking}: rf: {repetions_factor} -> {amount}")
        

if __name__ == "__main__":
    test_milkings()

