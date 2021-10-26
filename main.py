from discord.ext import commands
import config
import discord
from discord_components import DiscordComponents
import os

intents = discord.Intents().all()
bot = commands.Bot(command_prefix='h.', intents=intents)
bot.remove_command('help')
DiscordComponents(bot=bot)


@bot.event
async def on_ready():
    print('ready')


for module in os.listdir('modules'):
    if module.endswith('.py'):
        print(f'Загружен модуль {module}')
        bot.load_extension(f'modules.{module.replace(".py", "")}')
bot.run(config.token)
