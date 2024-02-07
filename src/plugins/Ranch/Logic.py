from lib.Time.Time import Time
import random
from datetime import datetime
from collections import deque


class Logic():

    def __init__(self, ranch):
        self.ranch = ranch

        # todo: Queues to remember cows and workers
        self.remember_cows = deque(maxlen=30)
        self.remember_workers = deque(maxlen=30)

    async def is_worker(self, name):
        if name in self.remember_workers:
            return True

        worker = self.ranch.database.get_worker(name)

        if worker:
            self.remember_workers.append(name)
            return True
        else:
            return False

    async def is_cow(self, name, respect=True):
        if name in self.remember_cows:
            return True

        data = self.get_cow(name, respect)

        if data:
            self.remember_cows.append(name)
            return True
        else:
            return False

    async def is_breeder(self, name):
        data = self.ranch.get_breeder(name)
        if data:
            return True
        else:
            return False

    async def add_cow(self, cow_name, milk_yield=10):
        is_cow = await self.is_cow(cow_name)

        if not is_cow:
            status = self.ranch.database.add_cow(cow_name, milk_yield)

            if not status:
                # is already a cow
                self.ranch.database.enable("cow", cow_name)

            return status
        return not is_cow

    async def add_worker(self, name):
        is_worker = await self.is_worker(name)

        if not is_worker:
            status = self.ranch.database.add_worker(name)

            if not status:
                self.ranch.database.enable("worker", name)

            return status
        return not is_worker

    async def _get_milk_multiplier(self, worker_name):
        worker_is_cow = await self.is_cow(worker_name)
        worker_is_worker = await self.is_worker(worker_name)
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

    def _milk_that_meat_sack(self, worker_name, cow_name, multiplier=0, respect=True):
        """
        sends the milking request to the database,
        returns if the milking was a success, the amount of milk, if there was a lvl up and the new milking yield of the cow
        @param worker_name: name of the worker, milking the cow
        @param cow_name: name of the cow
        @return: (success, amount, lvlup, milk)
        """
        name, milk, level, exp, _ = self.ranch.database.get_cow(cow_name, respect)

        if not name.lower() == cow_name.lower():
            return None

        if worker_name.lower() == cow_name.lower():
            return None

        if respect:
            date = datetime.now().strftime("%Y-%m-%d")  #  %H:%M
        else:
            date = datetime.now().strftime("%Y-%m-%d %H:%M")

        count_milking = self.ranch.database.check_milking(cow_name, worker_name, date)[0]

        if (count_milking == 0 or not respect) and multiplier > 0:
            max_milk = int(milk * multiplier)
            amount = int(random.uniform(0.2 * max_milk, max_milk))
            lvlup = False
            success = self.ranch.database.milk_cow(cow_name, worker_name, amount, date)
            if success:
                lvlup = self._level_up_cow(cow_name, milk, level, exp)

        else:
            success = False
            amount = 0
            lvlup = False
            milk = 0

        # todo: lvlup worker needs to be done
        return (success, amount, lvlup, milk)

    async def milk_cow(self, worker_name, cow_name):
        """
        sends the milking request to the database,
        returns if the milking was a success, the amount of milk, if there was a lvl up and the new milking yield of the cow_name
        @param worker_name: name of the worker, milking the cow_name
        @param cow_name: name of the cow_name
        @return: (success, amount, lvlup, milk)
        """
        multiplier = await self._get_milk_multiplier(worker_name)
        bonus = 0.4
        return self._milk_that_meat_sack(worker_name, cow_name, multiplier + bonus)

    async def power_milk_cow(self, worker_name, cow_name):
        """
        sends the milking request to the database,
        returns if the milking was a success, the amount of milk, if there was a lvl up and the new milking yield of the cow
        @param worker_name: name of the worker, milking the cow
        @param cow_name: name of the cow
        @return: (success, amount, lvlup, milk)
        """
        multiplier = 2
        bonus = 1
        return self._milk_that_meat_sack(worker_name, cow_name, multiplier + bonus, False)

    async def milk_all(self, user, channel) -> (list, int):
        '''
        An easier way to milk all the cows in the channel
        @param user: user that runns the command
        @param channel: channel where the command was started
        @return: milked_cows, not_milkable
        '''
        multiplier = await self._get_milk_multiplier(user)
        not_milkable = 0
        milked_cows = []

        if multiplier > 0:
            for character in self.ranch.client.channels[channel].characters.get():

                if await self.is_cow(character) and not user.lower() == character.lower():
                    success, amount, lvlup, _ = self._milk_that_meat_sack(user, character, multiplier)

                    if success:
                        milked_cows.append((character, amount, lvlup))

                    else:
                        not_milkable += 1

                else:
                    print (character, await self.is_cow(character))

        milked_cows.sort(key=lambda x: x[1], reverse=True)

        return milked_cows, not_milkable

    def _get_last_milking(self, cow, worker):
        last_milking_date = self.ranch.database.get_last_milking(worker, cow)

        return True

    def _is_milkable(self, cow, worker):
        return self._get_last_milking(cow, worker)

    def _level_up_cow(self, cow_name, milk, level, exp):
        exp += 1
        if exp >= self.next_level_ep(level):
            level += 1
            milk += 1
            exp = 0
            lvlup = True
            self.ranch.database.update_cow_milk(cow_name, milk)
        else:
            lvlup = False
        self.ranch.database.update_experience(cow_name, level, exp, 'cow')

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

            name, milk, level, exp = self.ranch.database.get_cow(cow_name)

            success = self.ranch.database.milk_cow(cow_name, self.ranch.client.config.character, 1, date)
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

    def get_worker(self, name):
        """
        Returns the milkings of worker

        @param name: name of theworker
        @return: list of Milkings
        """
        data = self.ranch.database.get_worker(name)
        return data

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
            message += f"{number}. [user]{worker}[/user] milked {milk} liters\n"

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
            message += f"({index}) - {channel_id}\n"

        return message

    def remove_milking_channel_by_index(self, channel_index):
        channel_index = int(channel_index)
        if len(self.ranch.milking_channels) <= channel_index + 1:
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
        if await self.is_cow(name):
            return self.ranch.database.disable("cow", name)
        else:
            return False

    async def disable_worker(self, name):
        if await self.is_worker(name):
            return self.ranch.database.disable("worker", name)
        else:
            return False

    async def cow_update_milk(self, name, milk):
        if await self.is_cow(name):
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

