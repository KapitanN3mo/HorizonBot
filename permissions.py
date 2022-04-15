from functools import wraps
import disnake
import database
from disnake.ext import commands
import json
from assets import emojis


def admin_permission_required(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            ctx: commands.Context = args[1]
        except IndexError:
            ctx: disnake.CommandInteraction = kwargs['inter']
        user: disnake.User = ctx.author
        guild: disnake.Guild = ctx.guild
        member: disnake.Member = disnake.utils.get(guild.members, id=user.id)
        if member.guild_permissions.administrator:
            return await func(*args, **kwargs)
        else:
            db_guild = database.Guild.get_or_none(database.Guild.guild_id == guild.id)
            if user.id in json.loads(db_guild.admins):
                return await func(*args, **kwargs)
            else:
                await ctx.send(f'{emojis.no_entry}`У вас недостаточно прав для использования этой команды!`')

    return wrapper


def check_admin_permission(member: disnake.Member, guild: disnake.Guild):
    if member.guild_permissions.administrator:
        return True
    else:
        db_guild = database.Guild.get_or_none(database.Guild.guild_id == guild.id)
        if member.id in json.loads(db_guild.admins):
            return True
        else:
            return False


def developer_permission_required(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            ctx: commands.Context = args[1]
        except IndexError:
            ctx: disnake.CommandInteraction = kwargs['inter']
        with open('settings.json', 'r') as s_file:
            settings = json.load(s_file)
            if ctx.author.id in map(int, settings['developers']):
                return await func(*args, **kwargs)
            else:
                await ctx.send(f'{emojis.no_entry}`У вас недостаточно прав для использования этой команды!`')

    return wrapper
