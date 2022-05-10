import asyncio
import json
from disnake.ext import commands
import disnake
import os
import threading
from api import app
from typing import List
import dt


class Bot:
    intents = disnake.Intents().all()
    bot = commands.Bot(command_prefix=commands.when_mentioned_or('h.'),
                       case_insensitive=True,
                       intents=intents,
                       test_guilds=[796776835367043092,849628635639971871])
    bot.remove_command('help')
    with open('settings.json', 'r') as set_file:
        settings = json.load(set_file)
    api_thread = threading.Thread(
        target=app.run, kwargs={'host': settings['api']['host'], 'port': settings['api']['port']})
    _task_buffer: List[asyncio.Future] = []
    _garbage_cleaner_data = {
        "last_work": dt.get_msk_datetime(),
        "deleted_task_count": 0,
    }
    start_time = dt.get_msk_datetime()
    garbage_delay = 60

    @classmethod
    def add_task(cls, task: asyncio.Future):
        cls._task_buffer.append(task)

    @classmethod
    async def _cleaning_garbage(cls):
        while True:
            count = 0
            for task in cls._task_buffer:
                if task.done():
                    cls._task_buffer.remove(task)
                    count += 1
            cls._garbage_cleaner_data['last_work'] = dt.get_msk_datetime()
            cls._garbage_cleaner_data['deleted_task_count'] = count
            await asyncio.sleep(cls.garbage_delay)

    @classmethod
    def run(cls, mode='normal'):
        token = cls.settings['tokens'][mode]
        cls.bot.load_extension('core.events')
        cls.bot.load_extension('core.profile')
        cls.bot.load_extension('core.indexing')
        cls.bot.load_extension('core.bot_messages')
        extensions = os.listdir('extensions')
        for module in extensions:
            if module.endswith('.py') and module != '__init__.py':
                print(module)
                cls.bot.load_extension(f'extensions.{module.replace(".py", "")}')
        ft = cls.bot.loop.create_task(cls._cleaning_garbage())
        cls.start_time = dt.get_msk_datetime()
        cls.bot.run(token)

    @classmethod
    def get_bot(cls):
        return cls.bot

    @classmethod
    def get_garbage_info(cls):
        return {**cls._garbage_cleaner_data, 'work_task_count': len(cls._task_buffer), 'delay': cls.garbage_delay}
