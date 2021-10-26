import asyncio
import datetime
import math
import pathlib
import random
import discord
from discord.ext import commands
import config
import json
import os
import componets
import discord
from discord_components import DiscordComponents, Button, ButtonStyle
import subprocess

intents = discord.Intents().all()
bot = commands.Bot(command_prefix='h.', intents=intents)
bot.remove_command('help')
DiscordComponents(bot=bot)


@bot.event
async def on_ready():
    print('ready')


























@create_poll.error
async def create_embed_error(ctx, error):
    if isinstance(error, KeyError):
        await ctx.send(':exclamation:`Ошибка в структуре аргумента!`')
    elif isinstance(error, commands.errors.MissingPermissions):
        await ctx.send(':no_entry:`Требуются права администратора!`')
    elif isinstance(error, commands.errors.MissingRequiredArgument):
        await ctx.send(':exclamation:`Необходимо передать данные в JSON формате`')
    elif isinstance(error, json.decoder.JSONDecodeError):
        await ctx.send(':exclamation:`Ошибка в структуре аргумента!`')
    elif isinstance(error, commands.errors.CommandInvokeError):
        await ctx.send(f':exclamation:`Произошла внутренняя ошибка : {error}`')


bot.run(config.token)
