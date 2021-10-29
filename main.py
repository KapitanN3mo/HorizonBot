from discord.ext import commands
import discord
from discord_components import DiscordComponents
import os
from componets import config
import logging

intents = discord.Intents().all()
intents.members = True
bot = commands.Bot(command_prefix='h.', case_insensitive=True, intents=intents)
bot.remove_command('help')
DiscordComponents(bot=bot)

logger = logging.getLogger('MODULE_LOADER')
for module in os.listdir('modules'):
    if module.endswith('.py'):
        logger.info(f'Загружен модуль {module}')
        bot.load_extension(f'modules.{module.replace(".py", "")}')
token = config.get('Global', 'token')
bot.run(token)
