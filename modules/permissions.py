from functools import wraps
import discord
import database
from discord.ext import commands
from core import Bot
import json
from assets import emojis


def admin_permission_required(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        ctx: commands.Context = args[1]
        user: discord.User = ctx.author
        guild: discord.Guild = ctx.guild
        member: discord.Member = discord.utils.get(guild.members, id=user.id)
        if member.guild_permissions.administrator:
            return await func(*args, **kwargs)
        else:
            db_guild = database.Guild.get_or_none(database.Guild.guild_id == guild.id)
            if user.id in json.loads(db_guild.admins):
                return await func(*args, **kwargs)
            else:
                await ctx.send(f'{emojis.no_entry}`У вас недостаточно прав для использования этой команды!`')

    return wrapper


def developer_permission_required(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        ctx: commands.Context = args[1]
        with open('settings.json', 'r') as s_file:
            settings = json.load(s_file)
            if ctx.author.id in map(int, settings['developers']):
                return func(*args, **kwargs)
            else:
                await ctx.send(f'{emojis.no_entry}`У вас недостаточно прав для использования этой команды!`')

    return wrapper
