import json
from discord.ext import commands
import discord
from discord_components import DiscordComponents
import os


class Bot:
    intents = discord.Intents().all()
    bot = commands.Bot(command_prefix='h.', case_insensitive=True, intents=intents)
    bot.remove_command('help')
    DiscordComponents(bot=bot)
    with open('settings.json', 'r') as set_file:
        settings = json.load(set_file)

    @classmethod
    def run(cls, mode='normal'):
        token = cls.settings['tokens'][mode]
        for module in os.listdir('extensions'):
            if module.endswith('.py') and module != '__init__.py':
                try:
                    cls.bot.load_extension(f'extensions.{module.replace(".py", "")}')
                except Exception as ex:
                    print(ex)
        cls.bot.run(token)

    @classmethod
    def get_bot(cls):
        return cls.bot
