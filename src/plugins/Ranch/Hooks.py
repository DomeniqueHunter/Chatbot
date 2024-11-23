from plugins.Ranch.Logic import Logic
from lib.Time.Time import time_until_tomorrow

from lib.BBCode.BBCode import BBCode
import calendar
from datetime import datetime
import random


class Hooks():
    """
    Just take the command and give it to the right method or function
    """

    def __init__(self, ranch):
        self.ranch = ranch

    async def get_cow(self, user, channel, name=None):
        if self.ranch.is_milking_channel(channel):
            name = BBCode.get_name(name)
            is_cow = self.ranch.logic.is_cow(name)
            message = "ERROR"
            if is_cow:
                data = self.ranch.logic.get_cow_milkings(name)
                if any(data):
                    (name, level, exp, milk) = self.ranch.logic.get_cow_stats(name)[0]
                    next_lvl_exp = self.ranch.logic.next_level_ep(level)

                    message = f"\nStats of [user]{name}[/user]: Level {level} [Ep {exp}/{next_lvl_exp}] Total Milk: {milk}\n"
                    # message += "Top 10 milkers\nWorker, Total Milk\n"

                    for worker_name, milk_amount in data:
                        message += f"[user]{worker_name}[/user], {milk_amount} liters\n"

                else:
                    message = f"{name} was not milked yet"

            else:
                message = f"[user]{name}[/user] is not a cow"

            await self.ranch.client.send_public_message(message, channel)

    async def get_cow_stats(self, user, name):
        if self.ranch.client.is_priviliged(user):
            name = BBCode.get_name(name)
            is_cow = self.ranch.logic.is_cow(name, False)
            message = ""
            if is_cow:
                _, amount, lvl, exp, active = self.ranch.logic.get_cow(name, False)
                message = f"[user]{name}[/user] is lvl {lvl} and yields {amount}l and has {exp} ep - active: {active}"

            else:
                message = "[user]{}[/user] is not a cow!".format(name)

            await self.ranch.client.send_private_message(message, user)

    async def get_cows(self, user, channel, page=1):
        """
        user requires list of cows
        @param user: User who calls command
        @param channel: Channel where command is called
        @param page: int, page that is required
        """

        if self.ranch.is_milking_channel(channel):
            page = int (page)
            if page > 1:
                number = (page - 1) * 10
            else:
                number = 0

            pages = len (self.ranch.logic.get_all_cows())
            pages = int (pages / 10) + 1

            data = self.ranch.logic.get_cows(page)  # (name, level, exp, milk, page)
            message = f"\nNr. Name (lvl), Milk [Page: {page}/{pages}]\n"

            if data:
                for name, level, exp, milk in data:
                    number += 1
                    message += f"{number}. [user]{name}[/user] ({level}): {milk}\n"

                # print (message)
                await self.ranch.client.send_public_message(message, channel)
            else:
                await self.ranch.client.send_public_message("No cows found!", channel)
        else:
            print (f"wrong channel: {channel}")

    async def get_workers(self, user, channel, page=1):
        """
        user requires list of workers
        @param user: User who calls command
        @param channel: Channel where command is called
        @param page: int, page that is required
        """
        if self.ranch.is_milking_channel(channel):
            data = self.ranch.logic.get_workers(page)

            pages = len (self.ranch.logic.get_all_workers())
            pages = int (pages / 10) + 1

            message = f"\nName, Milked [Page: {page}/{pages}]\n"
            if data:
                message += data
                await self.ranch.client.send_public_message(message, channel)
            else:
                await self.ranch.client.send_public_message("No workers found!", channel)

    async def get_worker(self, user, channel, name=None):
        if self.ranch.is_milking_channel(channel):
            name = BBCode.get_name(name)

            is_worker = self.ranch.logic.is_worker(name)
            message = "ERROR"

            if is_worker:
                _, _, lvl, exp, _ = self.ranch.logic.get_worker(name)
                next_lvl_exp = self.ranch.logic.next_level_ep(lvl)
                data = self.ranch.logic.get_worker_stats(name)
                message = f"\nStats of [user]{name}[/user]: Level {lvl} [Ep {exp}/{next_lvl_exp}]\nCow, Total Milk\n"

                for worker_name, milk_amount in data:
                    message += f"[user]{worker_name}[/user], {milk_amount} liters\n"

            else:
                message = "[user]{}[/user] is not a worker".format(name)

            await self.ranch.client.send_public_message(message, channel)
            
    async def get_person(self, user:str, name:str):
        if self.ranch.client.has_admin_rights(user):
            response = await self.ranch.logic.get_person_info(name)
            await self.ranch.client.send_private_message(response, user)
        else:
            await self.ranch.client.send_private_message("not permitted", user)

    async def milk(self, worker, channel, cow_name):
        """
        Milk a cow
        @param worker: the worker who milks the cow
        @param channel: channel where request was sent
        @param cow_name: name of the cow

        """
        if self.ranch.is_milking_channel(channel):
            cow_name = BBCode.get_name(cow_name)
            is_worker = self.ranch.logic.is_worker(worker)
            is_cow = self.ranch.logic.is_cow(cow_name)
            is_online = self.ranch.client.channels[channel].is_online(cow_name)
            message = ""

            if worker.lower() != cow_name.lower() and is_cow and is_worker and is_online:
                (success, amount, lvlup, _, lvlup_worker) = await self.ranch.logic.milk_cow(worker, cow_name)  # (success, amount, lvlup, milk)

                # print ((success, amount, lvlup))
                message = ""

                if success:
                    message = f"[user]{worker}[/user] milked [user]{cow_name}[/user] and got {amount}l of milk!"

                    if lvlup:
                        message += f"\n[user]{cow_name}[/user] had a boobgasm through milking and is now more productive!"

                    if lvlup_worker:
                        message += f"\n[user]{worker}[/user] is more skilled now!"

                else:
                    message = f"You can milk [user]{cow_name}[/user] again on the next day, [user]{worker}[/user]"

            elif worker.lower() == cow_name.lower() and is_cow and is_worker:
                message = f"[user]{cow_name}[/user] gets spanked merciless until that ass is bright red, cows are not allowed to milk them self!"

            elif not is_worker:
                message = f"[user]{worker}[/user] is not working here."

            elif not is_cow:
                message = f"[user]{cow_name}[/user] is not a cow."

            elif not is_online:
                message = f"cow [user]{cow_name}[/user] is not online!"

            else:
                # ERROR
                print ("### ERROR ###")

            await self.ranch.client.send_public_message(message, channel)

    async def power_milk(self, user, input_str=" , "):
        if self.ranch.client.is_owner(user.strip()):
            input = input_str.split(', ')
            if len(input) == 1:
                cow = input[0]
                exp = 1
            else:
                cow = input[0]
                exp = int(input[1])
                
            cow_name = BBCode.get_name(cow)
            is_worker = await self.ranch.logic.is_worker(user)
            is_cow = self.ranch.logic.is_cow(cow_name, False)
            is_online = True  # todo: find a better way

            if is_worker:
                worker = user

            if not is_cow:
                message = "this is not a cow"

            if worker.lower() != cow_name.lower() and is_worker and is_cow and is_online:
                (success, amount, lvlup, _, lvlup_worker) = await self.ranch.logic.power_milk_cow(worker, cow_name, exp)

                if success:
                    message = f"You milked [user]{cow_name}[/user] against it's will and got {amount}l of milk!"

                    if lvlup:
                        message += f"\n[user]{cow_name}[/user] had a boobgasm through milking and is now more productive!"

                    if lvlup_worker:
                        message += f"\n[user]{worker}[/user] is more skilled now!"

                else:
                    message = f"You can milk [user]{cow_name}[/user] again on the next day, [user]{worker}[/user]"

        else:
            message = "you don't have the permission for this!"

        await self.ranch.client.send_private_message(message, worker)

    async def milkall(self, user, channel):
        """
        milk all cows currently in the channel
        @param user: worker who wants to milk all cows
        @param channel: channel where the cows supposed to be
        """
        if self.ranch.is_milking_channel(channel):
            message = ""
            milked_cows, not_milkable, lvlup_worker = await self.ranch.logic.milk_all(user, channel)

            for cow, amount, lvlup in milked_cows:
                message += f"\n[user]{user}[/user] milked [user]{cow}[/user] and got {amount} liters of Milk"

                if lvlup:
                    message += f"\n[user]{cow}[/user] has leveled up!"

            if not_milkable > 0:
                if not_milkable == 1:
                    i = "is"
                    c = "cow"
                else:
                    i = "are"
                    c = "cows"

                milkable_in = time_until_tomorrow()
                message += f"\nThere {i} {not_milkable} {c} who {i} milkable in {milkable_in}."
            
            if lvlup_worker:
                message += f"\n[user]{user}[/user] has leveled up!"

            await self.ranch.client.send_public_message(message, channel)

    async def makemecow(self, user, channel):
        """
        add user to cows
        @param user: user who becomes a cow
        @param channel: channel where request was sent
        """
        if self.ranch.is_milking_channel(channel):
            status = await self.ranch.logic.add_cow(user)
            if status:
                message = f"[user]{user}[/user] is now a Cow at H-Milk! Milk it dry using !milk [user]{user}[/user]!"

            else:
                message = f"[user]{user}[/user] is already a Cow H-Milk!"

            await self.ranch.client.send_public_message(message, channel)

    async def becomeaworker(self, user, channel):
        """
        adds user to worker list
        @param user: new worker
        @param channel: channel where request was sent
        """
        if self.ranch.is_milking_channel(channel):
            status = await self.ranch.logic.add_worker(user)
            if status:
                message = f"[user]{user}[/user] is now a Worker at H-Milk!"

            else:
                message = f"[user]{user}[/user] is already a Worker at H-Milk!"

            await self.ranch.client.send_public_message(message, channel)

    async def set_milking_channel(self, user, channel):
        if self.ranch.client.has_admin_rights(user.strip()):
            self.ranch.logic.set_milking_channel(channel)

            if channel in self.ranch.milking_channels:
                message = "now you can milk cows here."
                await self.ranch.client.send_public_message(message, channel)

    async def remove_milking_channel_by_id(self, user, channel):
        if self.ranch.client.has_admin_rights(user.strip()):
            if self.ranch.logic.remove_milking_channel_by_id(channel):
                message = "milking is disabled here now! :("

            else:
                message = "nope!"

            await self.ranch.client.send_public_message(message, channel)

    # direct
    async def get_milking_channels(self, user):
        if self.ranch.client.has_admin_rights(user.strip()):
            message = self.ranch.logic.show_milking_channels()
            await self.ranch.client.send_private_message(message, user)

    async def remove_milking_channel_by_index(self, user, channel_index):
        if self.ranch.client.has_admin_rights(user.strip()):
            channel_index = int(channel_index)
            if self.ranch.logic.remove_milking_channel_by_index(channel_index):
                message = f"removed channel {channel_index} from list"
            else:
                message = "error on removing channel by id's"

            await self.ranch.client.send_private_message(message, user)

    async def add_cow(self, user, input_string=" , "):
        """
        add a cow the the farm
        @param user: user who sends the request
        @param input_string: cow,milk
        """
        if "," in input_string:
            name, milk = input_string.strip().split(',')
        else:
            name = input_string.strip()
            milk = 10

        name = BBCode.get_name(name)

        if self.ranch.client.is_priviliged(user.strip()):

            status = await self.ranch.logic.add_cow(name, milk)
            if status == True:
                message = f"[user]{name}[/user] is now a Cow at H-Milk!"
                message_4_cow = "Now you are a cow at H-Milk, offer you udders to all the workers!"
                await self.ranch.client.send_private_message(message_4_cow, name)
            else:
                message = f"[user]{name}[/user] is already a Cow H-Milk!"

        else:
            message = "you don't have the permission for this."

        await self.ranch.client.send_private_message(message, user)

    async def rename_person(self, user, input_string=" , "):
        if self.ranch.client.is_priviliged(user.strip()):
            old_name, new_name = input_string.strip().split(',')
            old_name = BBCode.get_name(old_name)
            new_name = BBCode.get_name(new_name)

            if self.ranch.logic.rename_person(old_name, new_name):
                message = f"renamed {old_name} to [user]{new_name}[/user]"

            else:
                message = f"couldn't find/rename {old_name}"

        else:
            message = "you don't have the permission for this."

        await self.client.send_private_message(message, user)

    async def remove_cow(self, user, name):
        """
        Disable a cow
        @param user: user who requests the cow to be disabled (admin)
        @param cow_name: name of the cow
        """
        if name:
            name = BBCode.get_name(name)

            if self.ranch.client.is_priviliged(user.strip()):
                status = await self.ranch.logic.disable_cow(name)
                if status:
                    message = f"cow [user]{name}[/user] was disabled!"

                else:
                    message = f"could not disable cow [user]{name}[/user]!"

            else:
                message = "you don't have the permission for this."

        else:
            message = "no name was given"

        await self.ranch.client.send_private_message(message, user)

    async def remove_worker(self, user, name):
        """
        Disable a worker
        @param user: user who requests the cow to be disabled ( admin)
        @param name: name of the cow
        """
        if name:
            name = BBCode.get_name(name)

            if self.ranch.client.is_priviliged(user.strip()):
                status = await self.ranch.logic.disable_worker(name)

                if status:
                    message = f"worker [user]{name}[/user] was disabled!"

                else:
                    message = f"could not disable worker [user]{name}[/user]!"

            else:
                message = "you don't have the permission for this."
        else:
            message = "no name was given"

        await self.ranch.client.send_private_message(message, user)

    async def set_cow_milk(self, user, input_string=" , "):
        """
        set the milk output of a cow
        @param user: username
        @param input_string: cow name, milk (csv)
        """
        if self.ranch.client.is_priviliged(user):
            name, amount = input_string.strip().split(',')
            name = BBCode.get_name(name)

            message = ""

            if int(amount) > 0:
                check = await self.ranch.logic.cow_update_milk(name, amount)

                if check:
                    message = f"cow {name} can yield {amount}l milk now!"
                else:
                    message = f"{name} is not a cow!"
            else:
                message = f"no valid amount"

        else:
            message = "you don't have the permission for this."

        await self.ranch.client.send_private_message(message, user)

    async def get_buisines_year(self, user, channel, year=None):
        """
        get stats for the business year
        """
        year = year or datetime.today().year
        year = int(year)

        if year <= datetime.today().year:
            year, total, month_stats = await self.ranch.logic.get_buisines_year(year)
            message = f"In year {year} we produced {total} l of milk:\n"
            for month, amount in month_stats.items():

                message += f" - {calendar.month_name[month]}: {amount} l\n"

            await self.ranch.client.send_public_message(message, channel)
            
    async def start_session(self, user:str, input_string:str=None):
        if self.ranch.client.has_admin_rights(user) and input_string:
            parameters = input_string.split(",")
            if len(parameters) == 1:
                channel = parameters[0]
                session_duration = 2 * 30 * 10
                ep = 1
            
            elif len(parameters) == 2:
                channel = parameters[0]
                session_duration = int(parameters[1]) * 60
                ep = 1
                
            else:
                channel = parameters[0]
                session_duration, ep = int(parameters[1]), int(parameters[2])           
                
            await self.__start_session(channel, session_duration, ep)
    
    async def __start_session(self, channel_name:str, session_duration:int, ep:int):
        # get channel_id for channel
        channel = self.ranch.client.channel_manager.find_channel(channel_name)
        if channel:
            channel_id = channel.code
            
            if session_duration > 15 * 60:
                session_duration = 15 * 60
            
            if channel_id:
                # create session
                self.ranch.session_manager.start_session(session_duration, channel_id, self.ranch.logic.moo_function)
            
            if self.ranch.session_manager.has_session(channel_id):
                session = self.ranch.session_manager.get_session(channel_id)
                
                # add set as data storage
                session.storage = set()
                session.reward = ep
                
                # prompt to channel
                prompts = [
                    f"A Moo Session was started! Cows, show us your best Moo!",
                    f"Announcement: All cows, please show us your best Moo!"
                    ]
                info = f"\n[i]The Session will run for {session_duration//60} min.\nAll participating cows will be rewarded with {ep} exp.\nPlease [b]moo[/b] as clear as possible so the system can register your moo![/i]"
                
                await self.ranch.client.send_public_message(random.choice(prompts) + info, session.channel_id)

