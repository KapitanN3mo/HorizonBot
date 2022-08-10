import asyncio
import json
import core.log
import colorama
from disnake.ext import commands
import disnake
import os
import threading
from typing import List
import dt


head = r'''
 /$$   /$$                     /$$                              
| $$  | $$                    |__/                              
| $$  | $$  /$$$$$$   /$$$$$$  /$$ /$$$$$$$$  /$$$$$$  /$$$$$$$ 
| $$$$$$$$ /$$__  $$ /$$__  $$| $$|____ /$$/ /$$__  $$| $$__  $$
| $$__  $$| $$  \ $$| $$  \__/| $$   /$$$$/ | $$  \ $$| $$  \ $$
| $$  | $$| $$  | $$| $$      | $$  /$$__/  | $$  | $$| $$  | $$
| $$  | $$|  $$$$$$/| $$      | $$ /$$$$$$$$|  $$$$$$/| $$  | $$
|__/  |__/ \______/ |__/      |__/|________/ \______/ |__/  |__/                  
                   /$$                   /$$                    
                  | $$                  | $$                    
                  | $$$$$$$   /$$$$$$  /$$$$$$                  
                  | $$__  $$ /$$__  $$|_  $$_/                  
                  | $$  \ $$| $$  \ $$  | $$                    
                  | $$  | $$| $$  | $$  | $$ /$$                
                  | $$$$$$$/|  $$$$$$/  |  $$$$/                
                  |_______/  \______/    \___/                         
                                                    Powered by KapitanN3mo   
'''


class Bot:
    intents = disnake.Intents().all()
    run_mode = None
    bot = commands.Bot(command_prefix=commands.when_mentioned_or('h.'),
                       case_insensitive=True,
                       intents=intents,
                       test_guilds=[796776835367043092, 849628635639971871])
    bot.remove_command('help')
    with open('settings.json', 'r') as set_file:
        settings = json.load(set_file)
    _task_buffer: List[asyncio.Future] = []
    _garbage_cleaner_data = {
        "last_work": dt.get_msk_datetime(),
        "deleted_task_count": 0,
    }
    start_time = dt.get_msk_datetime()
    garbage_delay = 60
    logger = log.Logger('CORE')

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
            cls.logger.debug(f'Очищено {count} задач')
            await asyncio.sleep(cls.garbage_delay)

    @classmethod
    def run(cls, mode='normal'):
        import core.persistent_storage
        print(colorama.Fore.MAGENTA + head + colorama.Style.RESET_ALL)
        cls.run_mode = mode
        token = cls.settings['tokens'][mode]
        cls.bot.load_extension('core.events')
        cls.logger.info('Загружено расширение: events')
        cls.bot.load_extension('core.profile')
        cls.logger.info('Загружено расширение: profile')
        cls.bot.load_extension('core.indexing')
        cls.logger.info('Загружено расширение: indexing')
        extensions = os.listdir('extensions')
        for module in extensions:
            if module.endswith('.py') and module != '__init__.py':
                cls.bot.load_extension(f'extensions.{module.replace(".py", "")}')
                cls.logger.info(f'Загружено расширение: {module}')
        ft = cls.bot.loop.create_task(cls._cleaning_garbage())
        cls.logger.info('Создана задача очистки')
        cls.start_time = dt.get_msk_datetime()
        cls.logger.info('Запуск бота')
        cls.logger.info(f'Всего слэш-команд: {len(cls.bot.slash_commands)}')
        cls.bot.run(token)

    @classmethod
    def get_bot(cls):
        return cls.bot

    @classmethod
    def get_run_mode(cls):
        return cls.run_mode

    @classmethod
    def get_garbage_info(cls):
        return {**cls._garbage_cleaner_data, 'work_task_count': len(cls._task_buffer), 'delay': cls.garbage_delay}
