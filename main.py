from discord.ext import commands
import discord
from discord_components import DiscordComponents
import os
from componets import config

# from api import api

intents = discord.Intents().all()
intents.members = True
bot = commands.Bot(command_prefix='h.', case_insensitive=True, intents=intents)
bot.remove_command('help')
DiscordComponents(bot=bot)

for module in os.listdir('modules'):
    if module.endswith('.py'):
        try:
            bot.load_extension(f'modules.{module.replace(".py", "")}')
        except Exception as ex:
            print(ex)
token = config.get('Global', 'token')

# api.launch_api_server(bot)
bot.run(token)
