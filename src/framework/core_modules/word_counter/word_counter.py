from plugins import PluginPrototype
from framework.core_modules.word_counter.database import WordCounterDB
from framework import opcode
from framework.lib.counter import Counter

import json


class WordCounter(PluginPrototype):

    def __init__(self, bot):
        self.bot = bot

        self.module_name = "Word Counter"
        self.module_version = "0.1.10"

        self.db = WordCounterDB()

        count_to = 120  # 120 pings -> 60 min
        self.counter = Counter(count_to)

        self.wordcount_channels = []

        self.load()

    def register_wordcount_channel(self, channel:str):
        if channel and channel not in self.wordcount_channels:
            self.wordcount_channels.append(channel)

    def is_wordcount_channel(self, channel:str) -> bool:
        return channel in self.wordcount_channels

    def get_user_count(self, channel, user) -> int:
        return self.db.get_total(channel, user)

    async def on_channel_message(self, json_object:str) -> None:
        # Channel Message Handler
        data:dict = json.loads(json_object)
        channel:str = data.get('channel', "")
        message:str = data.get('message', "").strip()
        user:str = data.get('character', "")

        if not self.is_wordcount_channel(channel):
            return

        if message.startswith("!"): return

        db_changed:bool = False
        if message.startswith("/me"):
            # on emote
            words = len(message.split(" ")) - 1
            self.db.add(channel, user, words)
            db_changed = True

        else:
            # normal talk, most likely not rp
            words = len(message.split(" ")) // 10
            if words > 0:
                self.db.add(channel, user, words)
                db_changed = True

        if db_changed:
            self.save()

    async def show_statistics(self) -> None:
        # admin!
        output_str = "\nWord Count Statistics:\n"

        for user, count in self.db.statistics():
            output_str += f"{user} {count}\n"

        print(output_str)

    def setup(self):
        self.bot.file_manager.add("word_counter_db", "wordcount.json", 'json')

    def save(self):
        self.bot.file_manager.save("word_counter_db", self.db.data)

    def load(self):
        self.db.data = self.bot.file_manager.load("word_counter_db") or {}

    def register_actions(self):
        if self.bot:
            self.bot.opcodes_handler.add_action(opcode.CHANNEL_MESSAGE, self.on_channel_message)

    async def clock(self):
        if self.counter.tick():
            if self.db.ensure_day(date_key=None):
                self.save()


def setup(bot):
    return WordCounter(bot)
