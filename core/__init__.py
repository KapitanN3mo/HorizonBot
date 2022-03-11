import json
from disnake.ext import commands
import disnake
import os


class Bot:
    intents = disnake.Intents().all()
    bot = commands.Bot(command_prefix=commands.when_mentioned_or('h.'), case_insensitive=True, intents=intents)
    bot.remove_command('help')
    with open('settings.json', 'r') as set_file:
        settings = json.load(set_file)

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
                try:
                    #print(module)
                    cls.bot.load_extension(f'extensions.{module.replace(".py", "")}')
                except Exception as ex:
                    print(ex)
        cls.bot.run(token)

    @classmethod
    def get_bot(cls):
        return cls.bot
