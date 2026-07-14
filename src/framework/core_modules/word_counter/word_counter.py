from plugins import PluginPrototype
from framework.core_modules.word_counter.database import WordCounterDB
from framework import opcode
import json


class WordCounter(PluginPrototype):

    def __init__(self, bot):
        self.bot = bot

        self.module_name = "Word Counter"
        self.module_version = "0.1.10"

        self.db = WordCounterDB()
        self.load()

    def get_user_count(self, channel, user) -> int:
        return self.db.get_total(channel, user)

    async def on_channel_message(self, json_object:str) -> None:
        # Channel Message Dispatcher

        data = json.loads(json_object)
        channel = data.get('channel', "chn")
        message = data.get('message', "msg").strip()
        user = data.get('character', "usr")

        print(f">> {channel} {user} {message}")

        if message.startswith("/me"):
            words = len(message.split(" ")) - 1
            self.db.add(channel, user, words)
            self.save()

            # debug
            print(self.get_user_count(channel, user))

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
            pass


def setup(bot):
    return WordCounter(bot)
